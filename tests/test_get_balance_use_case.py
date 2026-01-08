from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.app.application.account.use_cases.get_balance import GetBalanceUseCase
from src.app.domain.entities.account import Account
from src.app.domain.value_objects.balance import Balance
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.timestamp import Timestamp
from src.app.infrastructure.exchange.mexc.settings import MexcSettings


class _FakeService:
    def __init__(self, account: Account, price: Price | None, raise_on_price: bool = False):
        self._account = account
        self._price = price
        self._raise_on_price = raise_on_price

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def get_account(self) -> Account:
        return self._account

    async def get_price(self, symbol):
        if self._raise_on_price:
            raise RuntimeError("price unavailable")
        return self._price


def _fake_account() -> Account:
    ts = Timestamp(datetime.now(timezone.utc))
    return Account(
        can_trade=True,
        update_time=ts,
        balances=[
            Balance(asset="USDT", free=Decimal("10"), locked=Decimal("5")),
            Balance(asset="QRL", free=Decimal("2"), locked=Decimal("1")),
        ],
    )


def _fake_price() -> Price:
    ts = Timestamp(datetime.now(timezone.utc))
    return Price(bid=Decimal("2"), ask=Decimal("4"), last=Decimal("3"), timestamp=ts)


@pytest.mark.asyncio
async def test_balance_valuation_with_price(monkeypatch):
    account = _fake_account()
    price = _fake_price()
    settings = MexcSettings(MEXC_API_KEY="x", MEXC_SECRET_KEY="y")

    monkeypatch.setattr(
        "src.app.application.account.use_cases.get_balance.build_mexc_service",
        lambda settings: _FakeService(account, price),
    )

    result = await GetBalanceUseCase(settings=settings).execute()

    assert result["valuation"]["price_available"] is True
    assert result["valuation"]["price_mid"] == "3"
    assert result["valuation"]["qrl_value_usdt"] == "9"
    assert result["valuation"]["total_value_usdt"] == "24"
    assert Decimal(result["valuation"]["qrl_pct"]) == Decimal("37.5")
    assert Decimal(result["valuation"]["usdt_pct"]) == Decimal("62.5")

    qrl_balance = next(b for b in result["balances"] if b["asset"] == "QRL")
    assert qrl_balance["free_value_usdt"] == "6"
    assert qrl_balance["locked_value_usdt"] == "3"


@pytest.mark.asyncio
async def test_balance_when_price_unavailable(monkeypatch):
    account = _fake_account()
    settings = MexcSettings(MEXC_API_KEY="x", MEXC_SECRET_KEY="y")

    monkeypatch.setattr(
        "src.app.application.account.use_cases.get_balance.build_mexc_service",
        lambda settings: _FakeService(account, None, raise_on_price=True),
    )

    result = await GetBalanceUseCase(settings=settings).execute()

    assert result["valuation"]["price_available"] is False
    assert result["valuation"]["price_mid"] is None
    assert result["valuation"]["qrl_value_usdt"] is None
    qrl_balance = next(b for b in result["balances"] if b["asset"] == "QRL")
    assert qrl_balance["free_value_usdt"] is None
    assert qrl_balance["locked_value_usdt"] is None
