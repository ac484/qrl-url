from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Timestamp:
    """UTC timestamp wrapper."""

    value: datetime

    def __post_init__(self):
        if self.value.tzinfo is None:
            object.__setattr__(self, "value", self.value.replace(tzinfo=timezone.utc))

    @classmethod
    def from_epoch_ms(cls, ms: int | float) -> "Timestamp":
        dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
        return cls(dt)
