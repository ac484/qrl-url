from dataclasses import dataclass


@dataclass(frozen=True)
class Side:
    """Order side constrained to BUY/SELL."""

    value: str

    def __post_init__(self):
        if self.value not in ("BUY", "SELL"):
            raise ValueError("Side must be BUY or SELL")
