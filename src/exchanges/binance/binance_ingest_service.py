import asyncio
import itertools
import logging

import aiohttp

from .dtos.binance_spot_exchange_info_symbol import BinanceSpotExchangeInfoSymbol
from postgres import pg_session
from .binance_assets_query_api import BinanceAssetsQueryApi
from .binance_crypto_asset_repo import BinanceCryptoAssetRepo
from .binance_crypto_trading_pairs_repo import BinanceCryptoTradingPairsRepo
from .binance_s3_service import BinanceS3Service
from .entities import BinanceCryptoAsset
from .entities import BinanceCryptoTradingPair


class BinanceIngestService:
    def __init__(self, binance_assets_query_api: BinanceAssetsQueryApi,
                 binance_crypto_assets_repo: BinanceCryptoAssetRepo,
                 binance_crypto_trading_pairs_repo: BinanceCryptoTradingPairsRepo,
                 binance_s3_service: BinanceS3Service,
                 ):
        self.__binance_assets_query_api = binance_assets_query_api
        self.__binance_crypto_assets_repo = binance_crypto_assets_repo
        self.__binance_crypto_trading_pairs_repo = binance_crypto_trading_pairs_repo
        self.__binance_s3_service = binance_s3_service
        self.__logger = logging.getLogger(self.__class__.__name__)

    @pg_session
    async def ingest_assets(self) -> None:
        """Create available on binance assets and their pairs"""
        # Truncate both tables. Perhaps, we could preserve the data in the future
        await self.__binance_crypto_trading_pairs_repo.delete_all()
        await self.__binance_crypto_assets_repo.delete_all()

        assets = await self.__binance_assets_query_api.get_all_assets()
        self.__logger.info(f'Found {len(assets.data)} assets on binance')

        pairs = await self.__binance_assets_query_api.get_all_pairs()
        self.__logger.info(f'Found {len(pairs.symbols)} trading pairs on binance')

        assets_hm = dict()
        assets_entities_hm = dict[str, BinanceCryptoAsset]()
        trading_pairs_hm = dict()
        assets_with_pairs = set()

        for pair in pairs.symbols:
            if not pair.baseAsset or not pair.quoteAsset or not pair.status:
                self.__logger.warning(
                    f'{self.ingest_assets.__name__}: skipping asset: {pair.symbol} due to missing data')
                continue

            trading_pairs_hm[pair.symbol.upper()] = pair

            assets_with_pairs.add(pair.baseAsset.upper())
            assets_with_pairs.add(pair.quoteAsset.upper())

        for asset in assets.data:
            # For now, we are skipping assets without logos, names, or codes
            # TODO: Figure out placeholder logo later
            if not asset.logoUrl:
                self.__logger.warning(f'No logo for asset: {asset.assetCode}')
                continue
            if not asset.assetName:
                self.__logger.warning(f'No name for asset: {asset.assetCode}')
                continue
            if not asset.assetCode:
                self.__logger.warning(f'No code for asset: {asset.assetName}')
                continue
            # if asset.assetCode not in latest_prices_hm:
            #     self.__logger.warning(f'No price for asset: {asset.assetCode}')
            #     continue
            # Let's skip assets without trading pairs
            if asset.assetCode not in assets_with_pairs:
                self.__logger.warning(f'No trading pairs for asset: {asset.assetCode}')
                continue

            assets_hm[asset.assetCode] = asset
            assets_entities_hm[asset.assetCode] = BinanceCryptoAsset(
                name=asset.assetName,
                ticker=asset.assetCode
            )

        async with aiohttp.ClientSession() as session:
            async with asyncio.TaskGroup() as tg:
                for asset in assets_entities_hm.values():
                    self.__logger.debug(f'Creating a record for ticker: {asset.ticker}')

                    logo_url = assets_hm[asset.ticker].logoUrl

                    # Skip empty URLs
                    if not logo_url:
                        continue

                    async def upload(ticker: str, logo_url: str):
                        self.__logger.debug(f'Uploading logo for ticker: {ticker} with logo url: {logo_url}')
                        try:
                            async with session.get(logo_url) as res:
                                s3_key = await self.__binance_s3_service.upload_asset_logo(res.content, ticker)

                            assets_entities_hm[ticker].logo_s3_key = s3_key
                        except Exception as e:
                            self.__logger.warning(
                                f'Failed to create a record for ticker: {ticker}, logo url: {logo_url}, error: {e}')

                    tg.create_task(upload(asset.ticker, logo_url))

        asset_entities = list()

        # Further filter entities without logos
        for ticker, entity in assets_entities_hm.items():
            if not entity.logo_s3_key:
                self.__logger.warning(f'No logo for asset: {ticker}')
                del assets_entities_hm[ticker]
                continue
            asset_entities.append(entity)

        if not len(asset_entities):
            raise ValueError('No assets to ingest')

        self.__logger.info(f'Ingesting {len(asset_entities)} assets')

        asset_entities = await self.__binance_crypto_assets_repo.insert_many(asset_entities)

        # update the dict with the actual entities
        for asset in asset_entities:
            assets_entities_hm[asset.ticker] = asset

        trading_pairs_entities = list[BinanceCryptoTradingPair]()

        for pair in trading_pairs_hm.values():
            base_asset = assets_entities_hm.get(pair.baseAsset.upper(), None)
            quote_asset = assets_entities_hm.get(pair.quoteAsset.upper(), None)

            # Filter out pairs without assets ingested assets
            if not base_asset or not quote_asset:
                self.__logger.warning(
                    f'Skipping trading pair: {pair.symbol} due to missing assets: {pair.baseAsset} or {pair.quoteAsset}')
                continue

            trading_pairs_entities.append(
                BinanceCryptoTradingPair(
                    base_asset_uuid=base_asset.uuid,
                    base_asset_ticker=base_asset.ticker,
                    quote_asset_uuid=quote_asset.uuid,
                    quote_asset_ticker=quote_asset.ticker,
                    symbol=pair.symbol.upper(),
                    status=pair.status,
                    iceberg_allowed=pair.icebergAllowed,
                    oco_allowed=pair.ocoAllowed,
                    oto_allowed=pair.otoAllowed,
                    quote_order_qty_market_allowed=pair.quoteOrderQtyMarketAllowed,
                    allow_trailing_stop=pair.allowTrailingStop,
                    cancel_replace_allowed=pair.cancelReplaceAllowed,
                    is_spot_trading_allowed=pair.isSpotTradingAllowed,
                    is_margin_trading_allowed=pair.isMarginTradingAllowed
                )
            )

        self.__logger.info(f'Ingesting {len(trading_pairs_entities)} trading pairs')

        # Inserting in chunks of 1000
        chunks = itertools.batched(trading_pairs_entities, 1000)

        for chunk in chunks:
            await self.__binance_crypto_trading_pairs_repo.insert_many(chunk)
