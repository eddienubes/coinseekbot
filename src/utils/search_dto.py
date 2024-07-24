from dataclasses import dataclass
from typing import TypeVar, Generic

H = TypeVar('H')
M = TypeVar('M')


@dataclass
class SearchDto(Generic[H, M]):
    hits: list[H]
    misses: list[M]
