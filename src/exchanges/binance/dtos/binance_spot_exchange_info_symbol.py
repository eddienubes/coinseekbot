import dataclasses

from dataclasses_json import DataClassJsonMixin


@dataclasses.dataclass
class BinanceSpotExchangeInfoSymbol(DataClassJsonMixin):
    symbol: str
    status: str
    baseAsset: str | None
    baseAssetPrecision: int
    quoteAsset: str | None
    quotePrecision: int
    quoteAssetPrecision: int
    baseCommissionPrecision: int
    quoteCommissionPrecision: int
    orderTypes: list[str]
    icebergAllowed: bool
    ocoAllowed: bool
    otoAllowed: bool
    quoteOrderQtyMarketAllowed: bool
    allowTrailingStop: bool
    cancelReplaceAllowed: bool
    isSpotTradingAllowed: bool
    isMarginTradingAllowed: bool
    filters: list
    permissions: list
    defaultSelfTradePreventionMode: str
    allowedSelfTradePreventionModes: list
    permissionsSets: list = None
