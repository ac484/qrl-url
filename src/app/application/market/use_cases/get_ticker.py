"""
Market use case: get ticker for QRL/USDT.
"""

from dataclasses import dataclass
from src.app.domain.value_objects.ticker import Ticker


@dataclass
class GetTickerInput:
    # Reserved for future filters or parameters
    pass


@dataclass
class GetTickerOutput:
    ticker: Ticker | None = None


class GetTickerUseCase:
    def execute(self, data: GetTickerInput) -> GetTickerOutput:
        # TODO: load ticker via port and map to domain
        return GetTickerOutput()
