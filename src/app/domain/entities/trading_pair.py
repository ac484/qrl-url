from dataclasses import dataclass


@dataclass(frozen=True)
class TradingPair:
    """Represents a trading pair such as QRL/USDT."""

    base_currency: str
    quote_currency: str

    @property
    def symbol(self) -> str:
        return f"{self.base_currency}{self.quote_currency}".upper()
