"""
Trading use case: list trades for QRL/USDT.
"""

from dataclasses import dataclass
from typing import Iterable
from src.app.domain.entities.trade import Trade


@dataclass
class ListTradesInput:
    # TODO: add filters such as time range or limit
    pass


@dataclass
class ListTradesOutput:
    trades: Iterable[Trade]


class ListTradesUseCase:
    def execute(self, data: ListTradesInput) -> ListTradesOutput:
        # TODO: retrieve trades via port
        return ListTradesOutput(trades=[])
