"""
Market use case: get kline data for QRL/USDT.
"""

from dataclasses import dataclass


@dataclass
class GetKlineInput:
    # TODO: interval, start/end
    pass


@dataclass
class GetKlineOutput:
    # TODO: list of candles using domain VOs
    pass


class GetKlineUseCase:
    def execute(self, data: GetKlineInput) -> GetKlineOutput:
        # TODO: retrieve klines via port and map
        return GetKlineOutput()
