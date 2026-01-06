from typing import AsyncIterator

from app.application.ports.exchange_gateway import ExchangeGateway
from app.domain.events.balance_event import BalanceEvent
from app.domain.events.market_depth_event import MarketDepthEvent
from app.domain.events.order_event import OrderEvent
from app.domain.events.trade_event import TradeEvent
from app.domain.value_objects.symbol import Symbol
from app.infrastructure.exchange.mexc.generated import (
    PrivateAccountV3Api_pb2,
    PrivateOrdersV3Api_pb2,
    PublicAggreDepthsV3Api_pb2,
    PublicDealsV3Api_pb2,
)
from app.infrastructure.exchange.mexc.ws.mexc_ws_client import MexcWebSocketClient
from .balance_mapper import balance_proto_to_domain
from .order_mapper import order_proto_to_domain
from .trade_mapper import trade_proto_to_domain
from .depth_mapper import depth_proto_to_domain


class MexcExchangeGateway(ExchangeGateway):
    """Infrastructure adapter that translates MEXC WS protobuf into domain events."""

    def __init__(self, ws_client: MexcWebSocketClient):
        self._ws = ws_client

    async def subscribe_market_depth(
        self, symbol: Symbol
    ) -> AsyncIterator[MarketDepthEvent]:
        async for proto in self._ws.subscribe("depth", symbol.value):
            if isinstance(proto, PublicAggreDepthsV3Api_pb2.PublicAggreDepthsV3Api):
                yield depth_proto_to_domain(symbol, proto)

    async def subscribe_trades(self, symbol: Symbol) -> AsyncIterator[TradeEvent]:
        async for proto in self._ws.subscribe("deals", symbol.value):
            if isinstance(proto, PublicDealsV3Api_pb2.PublicDealsV3Api):
                for item in proto.deals:
                    yield trade_proto_to_domain(symbol, item)

    async def subscribe_orders(self) -> AsyncIterator[OrderEvent]:
        async for proto in self._ws.subscribe("orders"):
            if isinstance(proto, PrivateOrdersV3Api_pb2.PrivateOrdersV3Api):
                yield order_proto_to_domain(proto)

    async def subscribe_balances(self) -> AsyncIterator[BalanceEvent]:
        async for proto in self._ws.subscribe("balances"):
            if isinstance(proto, PrivateAccountV3Api_pb2.PrivateAccountV3Api):
                yield balance_proto_to_domain(proto)
