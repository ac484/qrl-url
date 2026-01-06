"""Pydantic schemas for interface layer requests/responses."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class PlaceOrderRequest(BaseModel):
    symbol: str = Field(default="QRLUSDT", description="Trading symbol")
    side: Literal["BUY", "SELL"]
    order_type: Literal["LIMIT", "MARKET"] = Field(default="LIMIT", alias="type")
    quantity: Decimal
    price: Decimal | None = None
    time_in_force: Literal["GTC", "IOC", "FOK"] | None = Field(default="GTC", alias="timeInForce")
    client_order_id: str | None = Field(default=None, alias="clientOrderId")


class CancelOrderRequest(BaseModel):
    symbol: str = Field(default="QRLUSDT", description="Trading symbol")
    order_id: str | None = Field(default=None, alias="orderId")
    client_order_id: str | None = Field(default=None, alias="clientOrderId")


class GetOrderRequest(BaseModel):
    symbol: str = Field(default="QRLUSDT", description="Trading symbol")
    order_id: str | None = Field(default=None, alias="orderId")
    client_order_id: str | None = Field(default=None, alias="clientOrderId")


class ListTradesRequest(BaseModel):
    symbol: str = Field(default="QRLUSDT", description="Trading symbol")
