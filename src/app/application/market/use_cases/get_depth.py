"""
Market use case: get order book depth for QRL/USDT.
"""

from dataclasses import dataclass


@dataclass
class GetDepthInput:
    # TODO: include depth size or level
    pass


@dataclass
class GetDepthOutput:
    # TODO: include bids/asks structures using domain VOs
    pass


class GetDepthUseCase:
    def execute(self, data: GetDepthInput) -> GetDepthOutput:
        # TODO: retrieve depth via port and map
        return GetDepthOutput()
