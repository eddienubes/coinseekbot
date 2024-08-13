import dataclasses


@dataclasses.dataclass
class Pageable[T]:
    hits: list[T]
    total: int
    limit: int
    offset: int

    def get_total_pages(self) -> int:
        return self.total // self.limit

    def get_current_page(self) -> int:
        return self.offset // self.limit + 1
