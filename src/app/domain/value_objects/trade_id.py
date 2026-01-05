from dataclasses import dataclass


@dataclass(frozen=True)
class TradeId:
    """Trade identifier returned by MEXC."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("TradeId cannot be empty")
