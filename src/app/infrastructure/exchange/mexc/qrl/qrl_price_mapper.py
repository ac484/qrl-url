from decimal import Decimal

from src.app.domain.value_objects.qrl_price import QrlPrice


def map_ticker_to_price(payload: dict) -> QrlPrice:
    price = payload.get("lastPrice") or payload.get("last")
    if price is None:
        raise ValueError("Missing QRL price in payload")
    return QrlPrice(Decimal(str(price)))
