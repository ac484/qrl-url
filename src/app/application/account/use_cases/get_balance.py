"""
Account use case: get subaccount balance.
"""

from dataclasses import dataclass


@dataclass
class GetBalanceOutput:
    # TODO: add balance fields per asset (QRL/USDT)
    pass


class GetBalanceUseCase:
    def execute(self) -> GetBalanceOutput:
        # TODO: retrieve balances via port and map to domain VOs
        return GetBalanceOutput()
