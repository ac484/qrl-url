"""
Market use case: 24h stats for QRL/USDT.
"""

from dataclasses import dataclass


@dataclass
class GetStats24hInput:
    pass


@dataclass
class GetStats24hOutput:
    # TODO: add fields for high/low/volume etc.
    pass


class GetStats24hUseCase:
    def execute(self, data: GetStats24hInput) -> GetStats24hOutput:
        # TODO: retrieve stats via port and map
        return GetStats24hOutput()
