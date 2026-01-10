from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from src.app.domain.aggregates.account_state import AccountState
from src.app.domain.aggregates.market_snapshot import MarketSnapshot
from src.app.domain.aggregates.trading_session import TradingSession
from src.app.domain.entities.account import Account
from src.app.domain.entities.order import Order
from src.app.domain.entities.order_book_level import OrderBookLevel
from src.app.domain.entities.trade import Trade
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.ticker import Ticker
from src.app.domain.value_objects.timestamp import Timestamp


def _ts_now() -> Timestamp:
    return Timestamp(datetime.now(timezone.utc))


def build_account_state(
    *, symbol: Symbol, account: Account, open_orders: Iterable[Order] = ()
) -> AccountState:
    return AccountState(
        symbol=symbol,
        account=account,
        open_orders=list(open_orders),
        updated_at=_ts_now(),
    )


def build_trading_session(
    *, symbol: Symbol, orders: Iterable[Order] = (), trades: Iterable[Trade] = ()
) -> TradingSession:
    now = _ts_now()
    return TradingSession(
        symbol=symbol,
        open_orders=list(orders),
        trades=list(trades),
        started_at=now,
        last_activity_at=now,
    )


def build_market_snapshot(
    *,
    symbol: Symbol,
    bids: Iterable[OrderBookLevel] = (),
    asks: Iterable[OrderBookLevel] = (),
    trades: Iterable[Trade] = (),
    ticker: Ticker | None = None,
) -> MarketSnapshot:
    return MarketSnapshot(
        symbol=symbol,
        bids=list(bids),
        asks=list(asks),
        trades=list(trades),
        ticker=ticker,
        updated_at=_ts_now(),
    )
