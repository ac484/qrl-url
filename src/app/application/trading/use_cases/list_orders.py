"""
Trading use case: list open/closed orders.
"""

from dataclasses import dataclass
from typing import Iterable
from src.app.domain.entities.order import Order


@dataclass
class ListOrdersInput:
    # TODO: add filters (status, time range, limit)
    pass


@dataclass
class ListOrdersOutput:
    orders: Iterable[Order]


class ListOrdersUseCase:
    def execute(self, data: ListOrdersInput) -> ListOrdersOutput:
        # TODO: retrieve via port and map to domain
        return ListOrdersOutput(orders=[])
