from decimal import Decimal


class ValuationService:
    """Compute position values given a quantity and a unit price."""

    @staticmethod
    def value(quantity: Decimal, unit_price: Decimal) -> Decimal:
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        if unit_price <= 0:
            raise ValueError("Unit price must be positive")
        return quantity * unit_price
