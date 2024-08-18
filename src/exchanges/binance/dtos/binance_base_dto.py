import dataclasses
from typing import Generic, TypeVar

from dataclasses_json import DataClassJsonMixin

T = TypeVar('T')


@dataclasses.dataclass
class BinanceBaseDto(Generic[T], DataClassJsonMixin):
    code: str
    message: str | None
    messageDetail: str | None
    success: bool
    data: T
