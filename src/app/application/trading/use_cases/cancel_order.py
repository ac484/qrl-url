"""
Trading use case: cancel existing order for QRL/USDT.
"""

from dataclasses import dataclass
from src.app.domain.value_objects.order_id import OrderId


@dataclass
class CancelOrderInput:
    order_id: OrderId


@dataclass
class CancelOrderOutput:
    # TODO: add cancellation status
    pass


class CancelOrderUseCase:
    def execute(self, data: CancelOrderInput) -> CancelOrderOutput:
        # TODO: orchestrate domain and call port
        return CancelOrderOutput()
