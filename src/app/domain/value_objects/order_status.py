from dataclasses import dataclass


@dataclass(frozen=True)
class OrderStatus:
    """Order status with a minimal allowed set."""

    value: str

    _allowed = {
        "NEW",
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELED",
        "REJECTED",
    }

    def __post_init__(self):
        if self.value not in self._allowed:
            raise ValueError(f"OrderStatus must be one of {sorted(self._allowed)}")
