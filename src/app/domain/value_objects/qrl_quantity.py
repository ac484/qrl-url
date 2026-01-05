from __future__ import annotations

from decimal import Decimal, ROUND_DOWN, getcontext

getcontext().prec = 28


class QrlQuantity:
    """
    QRL 專用數量 Value Object
    - 不可變
    - 防 fat finger
    """

    STEP_SIZE = Decimal("1")
    MIN_QTY = Decimal("1")
    MAX_QTY = Decimal("1000000")

    def __init__(self, value: Decimal | str | int | float):
        self._value = self._normalize(Decimal(str(value)))

    @staticmethod
    def _normalize(value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("QRL quantity must be > 0")

        normalized = (value // QrlQuantity.STEP_SIZE) * QrlQuantity.STEP_SIZE

        if normalized < QrlQuantity.MIN_QTY:
            raise ValueError("QRL quantity below minimum")

        if normalized > QrlQuantity.MAX_QTY:
            raise ValueError("QRL quantity exceeds safety limit")

        return normalized.quantize(QrlQuantity.STEP_SIZE, rounding=ROUND_DOWN)

    @property
    def value(self) -> Decimal:
        return self._value

    def __str__(self) -> str:
        return format(self._value, "f")

    def __repr__(self) -> str:
        return f"QrlQuantity({self._value})"
