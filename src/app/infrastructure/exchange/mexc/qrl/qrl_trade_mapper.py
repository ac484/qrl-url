from decimal import Decimal

from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.qrl_quantity import QrlQuantity


def map_trade(payload: dict) -> dict:
    return {
        "id": payload.get("id"),
        "price": QrlPrice(payload["price"]) if payload.get("price") else None,
        "quantity": QrlQuantity(payload["qty"]) if payload.get("qty") else None,
        "quote_qty": Decimal(str(payload["quoteQty"])) if payload.get("quoteQty") else None,
        "side": payload.get("isBuyer") and "BUY" or "SELL",
        "time": payload.get("time"),
    }
