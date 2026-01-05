from dataclasses import dataclass


@dataclass(frozen=True)
class OrderId:
    """Order identifier returned by MEXC."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("OrderId cannot be empty")
