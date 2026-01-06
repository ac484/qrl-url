"""
Factories to translate MEXC REST/WebSocket DTOs into domain aggregates.

These implementations are intentionally lightweight placeholders. They ensure
that aggregate construction paths are present and wired, while allowing the
future work to enrich the mapping with full business rules.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable, Optional

from src.app.domain.aggregates.account_state import AccountState
from src.app.domain.aggregates.market_snapshot import MarketSnapshot
from src.app.domain.aggregates.trading_session import TradingSession
from src.app.domain.entities.account import Account
from src.app.domain.entities.kline import Kline
from src.app.domain.entities.order import Order
from src.app.domain.entities.order_book_level import OrderBookLevel
from src.app.domain.entities.trade import Trade
from src.app.domain.value_objects.balance import Balance
from src.app.domain.value_objects.kline_interval import KlineInterval
from src.app.domain.value_objects.order_id import OrderId
from src.app.domain.value_objects.order_side import OrderSide
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.order_status import OrderStatus
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.ticker import Ticker
from src.app.domain.value_objects.timestamp import Timestamp
from src.app.domain.value_objects.trade_id import TradeId
from src.app.infrastructure.exchange.mexc.generated import (
    PrivateAccountV3Api_pb2,
    PrivateOrdersV3Api_pb2,
    PublicAggreDepthsV3Api_pb2,
    PublicAggreDealsV3Api_pb2,
    PublicBookTickerV3Api_pb2,
    PublicSpotKlineV3Api_pb2,
)


def _default_timestamp() -> Timestamp:
    return Timestamp(datetime.now(timezone.utc))


def _levels_from_depth(
    depth: Optional[PublicAggreDepthsV3Api_pb2.PublicAggreDepthsV3Api],
) -> tuple[list[OrderBookLevel], list[OrderBookLevel]]:
    if depth is None:
        return [], []

    bids = [
        OrderBookLevel(
            price=Decimal(str(item.price)),
            quantity=Decimal(str(item.quantity)),
            side=OrderSide("BUY"),
        )
        for item in getattr(depth, "bids", [])  # type: ignore[attr-defined]
    ]
    asks = [
        OrderBookLevel(
            price=Decimal(str(item.price)),
            quantity=Decimal(str(item.quantity)),
            side=OrderSide("SELL"),
        )
        for item in getattr(depth, "asks", [])  # type: ignore[attr-defined]
    ]
    return bids, asks


def market_snapshot_from_sources(
    symbol: Symbol,
    depth_proto: Optional[PublicAggreDepthsV3Api_pb2.PublicAggreDepthsV3Api] = None,
    trades: Optional[Iterable[Trade]] = None,
    ticker_proto: Optional[PublicBookTickerV3Api_pb2.PublicBookTickerV3Api] = None,
) -> MarketSnapshot:
    """
    Build a MarketSnapshot aggregate from available feed DTOs.

    The function accepts partial data (depth only, depth + trades, etc.) so
    the callers can incrementally enrich the snapshot.
    """

    bids, asks = _levels_from_depth(depth_proto)
    ticker: Ticker | None = None
    if ticker_proto is not None:
        bid = Decimal(str(getattr(ticker_proto, "bidPrice", 0)))
        ask = Decimal(str(getattr(ticker_proto, "askPrice", 0)))
        last = Decimal(str(getattr(ticker_proto, "lastPrice", 0)))
        if bid > 0 and ask > 0 and last > 0:
            ticker = Ticker(
                symbol=symbol,
                last_price=last,
                bid_price=bid,
                ask_price=ask,
                ts=_default_timestamp().value,
            )

    return MarketSnapshot(
        symbol=symbol,
        bids=bids,
        asks=asks,
        trades=list(trades or []),
        ticker=ticker,
        updated_at=_default_timestamp(),
    )


def account_state_from_proto(
    symbol: Symbol, account_proto: PrivateAccountV3Api_pb2.PrivateAccountV3Api
) -> AccountState:
    """
    Translate private account snapshot DTO into AccountState aggregate.

    Balance parsing is intentionally minimal; further normalization can be
    implemented when business rules are ready.
    """

    balances: list[Balance] = []
    for item in getattr(account_proto, "balances", []):  # type: ignore[attr-defined]
        balances.append(
            Balance(
                asset=getattr(item, "asset", ""),
                free=Decimal(str(getattr(item, "free", 0))),
                locked=Decimal(str(getattr(item, "locked", 0))),
            )
        )

    account = Account(
        can_trade=bool(getattr(account_proto, "canTrade", True)),
        update_time=_default_timestamp(),
        balances=balances,
    )
    return AccountState(
        symbol=symbol,
        account=account,
        open_orders=[],
        updated_at=_default_timestamp(),
    )


def trading_session_from_orders(
    symbol: Symbol, orders: Optional[Iterable[Order]] = None, trades: Optional[Iterable[Trade]] = None
) -> TradingSession:
    """Create a TradingSession aggregate from existing order/trade records."""

    return TradingSession(
        symbol=symbol,
        open_orders=list(orders or []),
        trades=list(trades or []),
        started_at=_default_timestamp(),
        last_activity_at=_default_timestamp(),
    )


def trades_from_public_proto(
    symbol: Symbol, deals_proto: Optional[PublicAggreDealsV3Api_pb2.PublicAggreDealsV3Api] = None
) -> list[Trade]:
    """Convert public trades DTO to domain trades (skeleton mapping)."""

    if deals_proto is None:
        return []

    trades: list[Trade] = []
    for item in getattr(deals_proto, "deals", []):  # type: ignore[attr-defined]
        trade_id_str = str(getattr(item, "tradeId", "0"))
        order_id_str = str(getattr(item, "orderId", "0"))
        trades.append(
            Trade(
                trade_id=TradeId(trade_id_str),
                order_id=OrderId(order_id_str),
                symbol=symbol,
                side=OrderSide("BUY") if bool(getattr(item, "isBuyerMaker", False)) else OrderSide("SELL"),
                price=Decimal(str(getattr(item, "price", 0))),
                quantity=Decimal(str(getattr(item, "quantity", 0))),
                fee=None,
                fee_asset=None,
                timestamp=_default_timestamp(),
            )
        )
    return trades


def klines_from_proto(
    symbol: Symbol, kline_proto: Optional[PublicSpotKlineV3Api_pb2.PublicSpotKlineV3Api] = None
) -> list[Kline]:
    """Convert spot kline DTOs to domain klines (skeleton mapping)."""

    if kline_proto is None:
        return []

    klines: list[Kline] = []
    interval = KlineInterval(str(getattr(kline_proto, "interval", "1m")))
    for item in getattr(kline_proto, "klineList", []):  # type: ignore[attr-defined]
        open_time_ms = int(getattr(item, "openTime", 0))
        close_time_ms = int(getattr(item, "closeTime", 0))
        klines.append(
            Kline(
                symbol=symbol,
                interval=interval,
                open=Decimal(str(getattr(item, "open", 0))),
                high=Decimal(str(getattr(item, "high", 0))),
                low=Decimal(str(getattr(item, "low", 0))),
                close=Decimal(str(getattr(item, "close", 0))),
                volume=Decimal(str(getattr(item, "volume", 0))),
                open_time=Timestamp(datetime.fromtimestamp(open_time_ms / 1000, tz=timezone.utc)),
                close_time=Timestamp(datetime.fromtimestamp(close_time_ms / 1000, tz=timezone.utc)),
            )
        )
    return klines


def orders_from_private_proto(
    symbol: Symbol, orders_proto: Optional[PrivateOrdersV3Api_pb2.PrivateOrdersV3Api] = None
) -> list[Order]:
    """Convert private orders DTO to domain orders (skeleton mapping)."""

    if orders_proto is None:
        return []

    orders: list[Order] = []
    for item in getattr(orders_proto, "orders", []):  # type: ignore[attr-defined]
        orders.append(
            Order(
                order_id=OrderId(str(getattr(item, "orderId", ""))),
                symbol=symbol,
                side=OrderSide(str(getattr(item, "side", "BUY"))),
                order_type=OrderType(str(getattr(item, "type", "LIMIT"))),
                status=OrderStatus(str(getattr(item, "status", "NEW"))),
                price=Decimal(str(getattr(item, "price", 0))),
                quantity=Quantity(Decimal(str(getattr(item, "origQty", 0)))),
                created_at=_default_timestamp(),
                time_in_force=None,
                client_order_id=str(getattr(item, "clientOrderId", "")) if getattr(item, "clientOrderId", None) else None,
                executed_quantity=Decimal(str(getattr(item, "executedQty", 0))),
                cumulative_quote_quantity=Decimal(str(getattr(item, "cummulativeQuoteQty", 0))),
                updated_at=_default_timestamp(),
            )
        )
    return orders
