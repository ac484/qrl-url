from dataclasses import dataclass


@dataclass(frozen=True)
class ApiSecret:
    """API secret used to sign requests."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("API secret cannot be empty")
