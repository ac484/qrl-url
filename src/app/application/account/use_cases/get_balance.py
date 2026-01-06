"""Account use case: get subaccount balance."""

from dataclasses import dataclass

from src.app.application.exchange.mexc_service import MexcService, build_mexc_service
from src.app.domain.entities.account import Account
from src.app.infrastructure.exchange.mexc.settings import MexcSettings


def _serialize_account(account: Account) -> dict:
    return {
        "can_trade": account.can_trade,
        "update_time": account.update_time.value.isoformat(),
        "balances": [
            {"asset": balance.asset, "free": str(balance.free), "locked": str(balance.locked)}
            for balance in account.balances
        ],
    }


@dataclass
class GetBalanceUseCase:
    settings: MexcSettings | None = None

    async def execute(self) -> dict:
        service = build_mexc_service(self.settings or MexcSettings())
        async with service as svc:
            account = await svc.get_account()
        return _serialize_account(account)
