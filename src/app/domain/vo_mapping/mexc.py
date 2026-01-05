from decimal import Decimal
from datetime import datetime, timezone

from src.app.domain.entities.order import Order
from src.app.domain.entities.trade import Trade
from src.app.domain.value_objects.order_id import OrderId
from src.app.domain.value_objects.order_status import OrderStatus
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.ticker import Ticker
from src.app.domain.value_objects.timestamp import Timestamp
from src.app.domain.value_objects.trade_id import TradeId


def map_rest_order_dto_to_domain(dto: dict) -> Order:
    """Map MEXC REST order DTO (primitives) to Order entity."""
    return Order(
        order_id=OrderId(str(dto.get("orderId", ""))),
        symbol=Symbol(str(dto.get("symbol", "QRLUSDT"))),
        side=Side(str(dto.get("side", "")).upper()),
        status=OrderStatus(str(dto.get("status", "")).upper()),
        price=Decimal(str(dto.get("price", "0"))),
        quantity=Quantity(Decimal(str(dto.get("origQty", "0")))),
        created_at=Timestamp(
            datetime.fromtimestamp(
                int(dto.get("time", 0)) / 1000, tz=timezone.utc
            )
        ),
        updated_at=Timestamp(
            datetime.fromtimestamp(
                int(dto.get("updateTime", dto.get("time", 0))) / 1000,
                tz=timezone.utc,
            )
        )
        if dto.get("updateTime")
        else None,
    )


def map_rest_trade_dto_to_domain(dto: dict) -> Trade:
    """Map MEXC REST trade DTO to Trade entity."""
    return Trade(
        trade_id=TradeId(str(dto.get("id", ""))),
        order_id=OrderId(str(dto.get("orderId", ""))),
        symbol=Symbol(str(dto.get("symbol", "QRLUSDT"))),
        side=Side(str(dto.get("side", "")).upper()),
        price=Decimal(str(dto.get("price", "0"))),
        quantity=Decimal(str(dto.get("qty", "0"))),
        fee=Decimal(str(dto["commission"])) if dto.get("commission") is not None else None,
        fee_asset=str(dto["commissionAsset"]) if dto.get("commissionAsset") else None,
        timestamp=Timestamp(
            datetime.fromtimestamp(int(dto.get("time", 0)) / 1000, tz=timezone.utc)
        ),
    )


def map_ws_ticker_event_to_domain(event: dict) -> Ticker:
    """Map MEXC WS ticker event to Ticker VO."""
    return Ticker(
        symbol=Symbol(str(event.get("symbol", "QRLUSDT"))),
        last_price=Decimal(str(event.get("last", "0"))),
        bid_price=Decimal(str(event.get("bidPrice", "0"))),
        ask_price=Decimal(str(event.get("askPrice", "0"))),
        ts=datetime.fromtimestamp(int(event.get("ts", 0)) / 1000, tz=timezone.utc),
    )
