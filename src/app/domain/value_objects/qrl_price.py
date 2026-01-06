from __future__ import annotations

from decimal import Decimal, ROUND_DOWN, getcontext
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.domain.value_objects.qrl_quantity import QrlQuantity

getcontext().prec = 28


class QrlPrice:
    """
    QRL/USDT 專用價格 Value Object
    - 不可變
    - 強制 tick size
    """

    TICK_SIZE = Decimal("0.0001")
    MIN_PRICE = TICK_SIZE

    def __init__(self, value: Decimal | str | float):
        self._value = self._normalize(Decimal(str(value)))

    @staticmethod
    def _normalize(value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("QRL price must be > 0")

        normalized = (value // QrlPrice.TICK_SIZE) * QrlPrice.TICK_SIZE

        if normalized < QrlPrice.MIN_PRICE:
            raise ValueError("QRL price below minimum tick size")

        return normalized.quantize(QrlPrice.TICK_SIZE, rounding=ROUND_DOWN)

    @property
    def value(self) -> Decimal:
        return self._value

    def __str__(self) -> str:
        return format(self._value, "f")

    def __repr__(self) -> str:
        return f"QrlPrice({self._value})"

    def multiply(self, quantity: "QrlQuantity") -> Decimal:
        return (self._value * quantity.value).quantize(
            Decimal("0.00000001"), rounding=ROUND_DOWN
        )
