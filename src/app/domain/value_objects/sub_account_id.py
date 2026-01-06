from dataclasses import dataclass


@dataclass(frozen=True)
class SubAccountId:
    """Numeric sub-account identifier used by MEXC spot API."""

    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("SubAccountId must be a positive integer")
