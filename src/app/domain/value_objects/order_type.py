from dataclasses import dataclass


@dataclass(frozen=True)
class OrderType:
    """Supported MEXC order types."""

    value: str

    _allowed = {"LIMIT", "MARKET"}

    def __post_init__(self):
        if self.value not in self._allowed:
            raise ValueError(f"OrderType must be one of {sorted(self._allowed)}")
