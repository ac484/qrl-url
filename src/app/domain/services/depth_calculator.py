from decimal import Decimal

from src.app.domain.value_objects.order_book import OrderBook
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side


class DepthCalculator:
    """Compute executable depth and weighted price for a side and target quantity."""

    def compute(self, book: OrderBook, side: Side, target: Quantity) -> tuple[Decimal, Decimal]:
        levels = book.asks if side.value == "BUY" else book.bids
        sorted_levels = sorted(
            levels, key=lambda lvl: lvl.price, reverse=side.value == "SELL"
        )

        remaining = target.value
        total = Decimal("0")
        filled = Decimal("0")

        for level in sorted_levels:
            if remaining <= 0:
                break
            take = min(level.quantity, remaining)
            total += take * level.price
            filled += take
            remaining -= take

        weighted_price = total / filled if filled > 0 else Decimal("0")
        return filled, weighted_price
