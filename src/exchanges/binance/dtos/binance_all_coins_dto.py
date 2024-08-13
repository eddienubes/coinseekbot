import dataclasses

from dataclasses_json import DataClassJsonMixin
from decimal import Decimal
from exchanges.binance.dtos.binance_base_dto import BinanceBaseDto


@dataclasses.dataclass
class BinanceAllCoinsStatus:
    timestamp: str
    elapsed: int
    credit_count: int

    error_code: str | None = None
    notice: str | None = None
    total_count: int | None = None
    error_message: str | None = None


@dataclasses.dataclass
class BinanceCoinQuoteEntry(DataClassJsonMixin):
    price: Decimal
    volume_24h: Decimal
    volume_change_24h: Decimal
    percent_change_1h: Decimal
    percent_change_24h: Decimal
    percent_change_7d: Decimal
    percent_change_30d: Decimal
    percent_change_60d: Decimal
    percent_change_90d: Decimal
    market_cap: Decimal
    fully_diluted_market_cap: Decimal
    last_updated: str

    market_cap_dominance: Decimal | None = None
    tvl: Decimal | None = None


@dataclasses.dataclass
class BinanceCoinQuote(DataClassJsonMixin):
    USD: BinanceCoinQuoteEntry | None = None


@dataclasses.dataclass
class BinanceAllCoinsEntry(DataClassJsonMixin):
    # cmc id
    id: int
    # Bitcoin
    name: str
    # BTC
    symbol: str
    slug: str
    num_market_pairs: int
    date_added: str
    tags: list[str]
    circulating_supply: int
    total_supply: int
    infinite_supply: bool
    cmc_rank: int
    last_updated: str
    quote: BinanceCoinQuote | None = None

    max_supply: int | None = None
    tvl_ratio: Decimal | None = None
    self_reported_market_cap: int | None = None
    self_reported_circulating_supply: int | None = None
    platform: dict | None = None


@dataclasses.dataclass
class BinanceAllCoinsBody(DataClassJsonMixin):
    status: BinanceAllCoinsStatus
    data: list[BinanceAllCoinsEntry]


@dataclasses.dataclass
class BinanceAllCoinsData(DataClassJsonMixin):
    success: bool
    body: BinanceAllCoinsBody


@dataclasses.dataclass
class BinanceAllCoinsDto(BinanceBaseDto):
    data: BinanceAllCoinsData
