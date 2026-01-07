from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class DepthLevel:
    """Single price level within an order book side."""

    price: Decimal
    quantity: Decimal

    def __post_init__(self) -> None:
        if self.price <= Decimal("0") or self.quantity <= Decimal("0"):
            raise ValueError("DepthLevel price and quantity must be positive")


@dataclass(frozen=True)
class OrderBookSide:
    """Side indicator for order book traversal."""

    value: str

    def __post_init__(self) -> None:
        if self.value not in ("BID", "ASK"):
            raise ValueError("OrderBookSide must be BID or ASK")


@dataclass(frozen=True)
class OrderBook:
    """Aggregated order book snapshot with bids and asks."""

    bids: list[DepthLevel] = field(default_factory=list)
    asks: list[DepthLevel] = field(default_factory=list)
