from dataclasses import dataclass


@dataclass(frozen=True)
class TimeInForce:
    """Time in force constraints for limit orders."""

    value: str

    _allowed = {"GTC", "IOC", "FOK"}

    def __post_init__(self):
        if self.value not in self._allowed:
            raise ValueError(f"TimeInForce must be one of {sorted(self._allowed)}")
