"""Pydantic schemas for interface layer requests/responses."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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


class AllocationResponse(BaseModel):
    """Response returned when the allocation task is triggered."""

    model_config = ConfigDict(from_attributes=True)

    request_id: str = Field(description="Identifier for the allocation trigger")
    status: str = Field(description="Execution status for the allocation task")
    executed_at: datetime = Field(description="UTC timestamp when the task executed")
