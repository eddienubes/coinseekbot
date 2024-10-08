import dataclasses
import math


@dataclasses.dataclass
class Pageable[T]:
    hits: list[T]
    total: int
    limit: int
    offset: int

    def meta(self):
        return {
            'total': self.total,
            'limit': self.limit,
            'offset': self.offset
        }

    def get_total_pages(self) -> int:
        return math.ceil(self.total / self.limit)

    def get_current_page(self) -> int:
        return self.offset // self.limit + 1

    def get_next_offset(self) -> int:
        return self.offset + self.limit

    def get_previous_offset(self) -> int:
        return self.offset - self.limit

    def has_previous_page(self) -> bool:
        return self.offset > 0

    def has_next_page(self) -> bool:
        return self.get_total_pages() > self.get_current_page()

    def is_pageable(self) -> bool:
        return self.has_previous_page() or self.has_next_page()
