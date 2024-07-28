import dataclasses

from dataclasses_json import DataClassJsonMixin

from exchanges.binance.dtos.binance_base_dto import BinanceBaseDto


@dataclasses.dataclass
class BinanceAllCoinsStatus:
    timestamp: str
    error_code: str | None
    elapsed: int
    credit_count: int
    notice: str | None

    total_count: int = None
    error_message: str = None


@dataclasses.dataclass
class BinanceCoinQuoteEntry(DataClassJsonMixin):
    price: float
    volume_24h: float
    volume_change_24h: float
    percent_change_1h: float
    percent_change_24h: float
    percent_change_7d: float
    percent_change_30d: float
    percent_change_60d: float
    percent_change_90d: float
    market_cap: float
    market_cap_dominance: float
    fully_diluted_market_cap: float
    last_updated: str

    tvl: float = None


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

    max_supply: int = None
    tvl_ratio: float = None
    self_reported_market_cap: int = None
    self_reported_circulating_supply: int = None
    platform: dict = None


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
