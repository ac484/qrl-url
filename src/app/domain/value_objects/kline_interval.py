from dataclasses import dataclass


@dataclass(frozen=True)
class KlineInterval:
    """Supported MEXC spot kline intervals for QRL/USDT."""

    value: str

    _allowed = {
        "1m",
        "5m",
        "15m",
        "30m",
        "1h",
        "4h",
        "1d",
    }

    def __post_init__(self):
        if self.value not in self._allowed:
            raise ValueError(f"KlineInterval must be one of {sorted(self._allowed)}")
