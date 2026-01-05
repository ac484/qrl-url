"""Mapping helpers between MEXC API payloads and domain objects."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from src.app.domain.entities.account import Account
from src.app.domain.entities.order import Order
from src.app.domain.entities.trade import Trade
from src.app.domain.value_objects.balance import Balance
from src.app.domain.value_objects.order_id import OrderId
from src.app.domain.value_objects.order_status import OrderStatus
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce
from src.app.domain.value_objects.timestamp import Timestamp
from src.app.domain.value_objects.trade_id import TradeId


def _to_decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def _to_timestamp_from_ms(value: int | float | str) -> Timestamp:
    ms_value = int(value)
    dt = datetime.fromtimestamp(ms_value / 1000, tz=timezone.utc)
    return Timestamp(dt)


def server_time_to_timestamp(payload: dict[str, Any]) -> Timestamp:
    return _to_timestamp_from_ms(payload.get("serverTime", 0))


def account_from_api(payload: dict[str, Any]) -> Account:
    balances = [
        Balance(asset=item["asset"], free=_to_decimal(item["free"]), locked=_to_decimal(item["locked"]))
        for item in payload.get("balances", [])
    ]
    return Account(
        can_trade=bool(payload.get("canTrade", True)),
        update_time=_to_timestamp_from_ms(payload.get("updateTime", 0)),
        balances=balances,
    )


def order_from_api(payload: dict[str, Any]) -> Order:
    order_id_value = payload.get("orderId")
    if order_id_value is None:
        raise ValueError("orderId is required in MEXC response")
    return Order(
        order_id=OrderId(str(order_id_value)),
        symbol=Symbol(payload.get("symbol", "QRLUSDT")),
        side=Side(payload.get("side", "BUY")),
        order_type=OrderType(payload.get("type", "LIMIT")),
        status=OrderStatus(payload.get("status", "NEW")),
        price=_to_decimal(payload.get("price", "0")),
        quantity=Quantity(_to_decimal(payload.get("origQty", payload.get("quantity", "0.00000001")))),
        time_in_force=TimeInForce(payload["timeInForce"]) if payload.get("timeInForce") else None,
        created_at=_to_timestamp_from_ms(payload.get("transactTime", payload.get("createTime", 0))),
        client_order_id=payload.get("clientOrderId") or payload.get("origClientOrderId"),
        executed_quantity=_to_decimal(payload.get("executedQty", "0"))
        if payload.get("executedQty") is not None
        else None,
        cumulative_quote_quantity=_to_decimal(payload.get("cummulativeQuoteQty", "0"))
        if payload.get("cummulativeQuoteQty") is not None
        else None,
        updated_at=_to_timestamp_from_ms(payload["updateTime"]) if payload.get("updateTime") else None,
    )


def trade_from_api(payload: dict[str, Any]) -> Trade:
    return Trade(
        trade_id=TradeId(str(payload.get("id"))),
        order_id=OrderId(str(payload.get("orderId"))),
        symbol=Symbol(payload.get("symbol", "QRLUSDT")),
        side=Side("BUY" if payload.get("isBuyer") else "SELL"),
        price=_to_decimal(payload.get("price", "0")),
        quantity=_to_decimal(payload.get("qty", payload.get("quantity", "0"))),
        fee=_to_decimal(payload["commission"]) if payload.get("commission") else None,
        fee_asset=payload.get("commissionAsset"),
        timestamp=_to_timestamp_from_ms(payload.get("time", 0)),
    )
