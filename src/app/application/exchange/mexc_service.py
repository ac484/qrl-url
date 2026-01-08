from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from src.app.domain.entities.account import Account
from src.app.domain.entities.order import Order
from src.app.domain.entities.trade import Trade
from src.app.domain.value_objects.order_book import OrderBook
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce
from src.app.domain.value_objects.timestamp import Timestamp
from src.app.infrastructure.exchange.mexc.mappers import (
    account_from_api,
    order_book_from_api,
    order_from_api,
    server_time_to_timestamp,
    trade_from_api,
)
from src.app.infrastructure.exchange.mexc.rest_client import MexcRestClient
from src.app.infrastructure.exchange.mexc_api_client import MexcApiClient
from src.app.infrastructure.exchange.mexc.settings import MexcSettings


def _to_str(value: Decimal | None) -> str | None:
    return str(value) if value is not None else None


def _symbol_value(symbol: Symbol) -> str:
    return symbol.value.replace("/", "").upper()


@dataclass
class PlaceOrderRequest:
    symbol: Symbol
    side: Side
    order_type: OrderType
    quantity: Quantity
    price: Price | None = None
    time_in_force: TimeInForce | None = None
    client_order_id: str | None = None


@dataclass
class CancelOrderRequest:
    symbol: Symbol
    order_id: str | None = None
    client_order_id: str | None = None


@dataclass
class GetOrderRequest:
    symbol: Symbol
    order_id: str | None = None
    client_order_id: str | None = None


class MexcService:
    """Application-level service that wraps the MEXC REST client."""

    def __init__(self, rest_client: MexcRestClient):
        self._rest_client = rest_client
        self._api_client = MexcApiClient(rest_client)

    async def __aenter__(self) -> "MexcService":
        await self._api_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._api_client.__aexit__(exc_type, exc, tb)

    async def get_server_time(self) -> Timestamp:
        payload = await self._rest_client.get_server_time()
        return server_time_to_timestamp(payload)

    async def get_account(self) -> Account:
        payload = await self._rest_client.get_account()
        return account_from_api(payload)

    async def place_order(self, request: PlaceOrderRequest) -> Order:
        if request.order_type.value == "LIMIT" and request.price is None:
            raise ValueError("Limit orders require price")
        payload = {
            "symbol": _symbol_value(request.symbol),
            "side": request.side.value,
            "order_type": request.order_type.value,
            "quantity": _to_str(request.quantity.value),
            "price": _to_str(request.price.last) if request.price else None,
            "time_in_force": request.time_in_force.value if request.time_in_force else None,
            "client_order_id": request.client_order_id,
        }
        response = await self._rest_client.create_order(**payload)
        return order_from_api(response)

    async def cancel_order(self, request: CancelOrderRequest) -> Order:
        response = await self._rest_client.cancel_order(
            symbol=_symbol_value(request.symbol),
            order_id=request.order_id,
            client_order_id=request.client_order_id,
        )
        return order_from_api(response)

    async def get_order(self, request: GetOrderRequest) -> Order:
        response = await self._rest_client.get_order(
            symbol=_symbol_value(request.symbol),
            order_id=request.order_id,
            client_order_id=request.client_order_id,
        )
        return order_from_api(response)

    async def list_open_orders(self, symbol: Symbol | None = None) -> list[Order]:
        response = await self._rest_client.list_open_orders(
            symbol=_symbol_value(symbol) if symbol else None
        )
        return [order_from_api(item) for item in response]

    async def list_trades(self, symbol: Symbol) -> list[Trade]:
        response = await self._rest_client.list_trades(symbol=_symbol_value(symbol))
        return [trade_from_api(item) for item in response]

    async def get_price(self, symbol: Symbol) -> Price:
        from src.app.domain.entities.trading_pair import TradingPair

        base = symbol.value.replace("/", "").upper().removesuffix("USDT")
        tp = TradingPair(base_currency=base, quote_currency="USDT")
        return await self._api_client.get_price(tp)

    async def get_kline(self, symbol: Symbol, interval: str, limit: int = 100) -> list["KLine"]:
        from src.app.domain.entities.trading_pair import TradingPair
        from src.app.domain.value_objects.kline import KLine

        base = symbol.value.replace("/", "").upper().removesuffix("USDT")
        tp = TradingPair(base_currency=base, quote_currency="USDT")
        return await self._api_client.get_klines(tp, interval=interval, limit=limit)

    async def get_depth(self, symbol: Symbol, limit: int = 50) -> OrderBook:
        response = await self._rest_client.depth(symbol=_symbol_value(symbol), limit=limit)
        return order_book_from_api(response)


def build_mexc_service(settings: MexcSettings) -> MexcService:
    """Factory to build a service with shared settings."""
    return MexcService(MexcRestClient(settings))
