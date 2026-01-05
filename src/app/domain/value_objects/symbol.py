from dataclasses import dataclass


@dataclass(frozen=True)
class Symbol:
    """Trading symbol constrained to QRL/USDT scope."""

    value: str

    def __post_init__(self):
        normalized = self.value.replace("/", "").upper()
        if normalized != "QRLUSDT":
            raise ValueError("Symbol must be QRL/USDT")
