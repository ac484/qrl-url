from typing import AsyncIterator, Protocol

from app.domain.events.market_depth_event import MarketDepthEvent
from app.domain.events.trade_event import TradeEvent
from app.domain.events.order_event import OrderEvent
from app.domain.events.balance_event import BalanceEvent
from app.domain.value_objects.symbol import Symbol


class ExchangeGateway(Protocol):
    """Application port for streaming market/account data."""

    async def subscribe_market_depth(
        self, symbol: Symbol
    ) -> AsyncIterator[MarketDepthEvent]:
        ...

    async def subscribe_trades(self, symbol: Symbol) -> AsyncIterator[TradeEvent]:
        ...

    async def subscribe_orders(self) -> AsyncIterator[OrderEvent]:
        ...

    async def subscribe_balances(self) -> AsyncIterator[BalanceEvent]:
        ...
