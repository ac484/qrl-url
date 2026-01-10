"""Account use case: get subaccount balance with valuation."""

from dataclasses import dataclass
from decimal import Decimal

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.domain.entities.account import Account
from src.app.domain.services.valuation_service import ValuationService
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.symbol import Symbol


def _mid(price: Price) -> Decimal:
    return (price.bid + price.ask) / Decimal("2")


def _aggregate_balances(account: Account) -> dict:
    usdt_free = usdt_locked = Decimal("0")
    qrl_free = qrl_locked = Decimal("0")
    for balance in account.balances:
        asset = balance.asset.upper()
        if asset == "USDT":
            usdt_free += balance.free
            usdt_locked += balance.locked
        elif asset == "QRL":
            qrl_free += balance.free
            qrl_locked += balance.locked
    return {
        "usdt_free": usdt_free,
        "usdt_locked": usdt_locked,
        "qrl_free": qrl_free,
        "qrl_locked": qrl_locked,
    }


def _valuation(agg: dict, mid_price: Decimal | None) -> dict:
    usdt_total = agg["usdt_free"] + agg["usdt_locked"]
    if mid_price is None:
        return {
            "price_available": False,
            "price_mid": None,
            "qrl_available_value": None,
            "qrl_locked_value": None,
            "qrl_value_usdt": None,
            "total_value_usdt": None,
            "qrl_pct": None,
            "usdt_pct": None,
        }

    qrl_available_value = ValuationService.value(agg["qrl_free"], mid_price)
    qrl_locked_value = ValuationService.value(agg["qrl_locked"], mid_price)
    qrl_value = qrl_available_value + qrl_locked_value
    total_value = qrl_value + usdt_total

    if total_value > 0:
        qrl_pct = (qrl_value / total_value) * Decimal("100")
        usdt_pct = (usdt_total / total_value) * Decimal("100")
    else:
        qrl_pct = None
        usdt_pct = None

    return {
        "price_available": True,
        "price_mid": str(mid_price),
        "qrl_available_value": str(qrl_available_value),
        "qrl_locked_value": str(qrl_locked_value),
        "qrl_value_usdt": str(qrl_value),
        "total_value_usdt": str(total_value),
        "qrl_pct": str(qrl_pct) if qrl_pct is not None else None,
        "usdt_pct": str(usdt_pct) if usdt_pct is not None else None,
    }


def _serialize_account(account: Account, valuation: dict) -> dict:
    return {
        "can_trade": account.can_trade,
        "update_time": account.update_time.value.isoformat(),
        "balances": [
            {
                "asset": balance.asset,
                "free": str(balance.free),
                "locked": str(balance.locked),
                "free_value_usdt": (
                    valuation["qrl_available_value"] if balance.asset.upper() == "QRL" else None
                ),
                "locked_value_usdt": (
                    valuation["qrl_locked_value"] if balance.asset.upper() == "QRL" else None
                ),
            }
            for balance in account.balances
        ],
        "valuation": valuation,
    }


@dataclass
class GetBalanceUseCase:
    exchange_factory: ExchangeServiceFactory

    async def execute(self) -> dict:
        async with self.exchange_factory() as exchange:
            account = await exchange.get_account()
            try:
                price = await exchange.get_price(Symbol("QRLUSDT"))
                mid = _mid(price)
            except Exception:
                price = None
                mid = None

        agg = _aggregate_balances(account)
        valuation = _valuation(agg, mid)
        return _serialize_account(account, valuation)
