from dataclasses import dataclass


@dataclass(frozen=True)
class ApiKey:
    """API key used for authenticated MEXC requests."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("API key cannot be empty")
