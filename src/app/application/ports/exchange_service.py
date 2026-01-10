from dataclasses import dataclass
from typing import AsyncContextManager, Callable, Protocol

from src.app.domain.entities.account import Account
from src.app.domain.entities.order import Order
from src.app.domain.entities.trade import Trade
from src.app.domain.value_objects.kline import KLine
from src.app.domain.value_objects.order_book import OrderBook
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce
from src.app.domain.value_objects.timestamp import Timestamp


@dataclass(frozen=True)
class PlaceOrderRequest:
    symbol: Symbol
    side: Side
    order_type: OrderType
    quantity: Quantity
    price: Price | None = None
    time_in_force: TimeInForce | None = None
    client_order_id: str | None = None


@dataclass(frozen=True)
class CancelOrderRequest:
    symbol: Symbol
    order_id: str | None = None
    client_order_id: str | None = None


@dataclass(frozen=True)
class GetOrderRequest:
    symbol: Symbol
    order_id: str | None = None
    client_order_id: str | None = None


class ExchangeService(Protocol, AsyncContextManager["ExchangeService"]):
    """Application port exposing required exchange operations."""

    async def get_server_time(self) -> Timestamp: ...

    async def get_account(self) -> Account: ...

    async def place_order(self, request: PlaceOrderRequest) -> Order: ...

    async def cancel_order(self, request: CancelOrderRequest) -> Order: ...

    async def get_order(self, request: GetOrderRequest) -> Order: ...

    async def list_open_orders(self, symbol: Symbol | None = None) -> list[Order]: ...

    async def list_trades(self, symbol: Symbol) -> list[Trade]: ...

    async def get_price(self, symbol: Symbol) -> Price: ...

    async def get_kline(self, symbol: Symbol, interval: str, limit: int = 100) -> list[KLine]: ...

    async def get_depth(self, symbol: Symbol, limit: int = 50) -> OrderBook: ...

    async def get_ticker_24h(self, symbol: Symbol) -> dict: ...

    async def get_market_trades(self, symbol: Symbol, limit: int = 50) -> list[dict]: ...


ExchangeServiceFactory = Callable[[], ExchangeService]
