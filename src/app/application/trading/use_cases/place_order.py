"""
Trading use case: place order for QRL/USDT.
Application layer orchestrates domain and ports; no infrastructure calls here.
"""

from dataclasses import dataclass
from src.app.domain.value_objects.order_id import OrderId


@dataclass
class PlaceOrderInput:
    # TODO: add required fields (side, quantity, price, type, client order id, etc.)
    pass


@dataclass
class PlaceOrderOutput:
    order_id: OrderId | None = None
    # TODO: extend with status or acceptance flags as needed


class PlaceOrderUseCase:
    def execute(self, data: PlaceOrderInput) -> PlaceOrderOutput:
        # TODO: orchestrate domain aggregate and call port
        return PlaceOrderOutput()
