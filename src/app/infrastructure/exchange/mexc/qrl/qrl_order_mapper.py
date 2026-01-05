from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.qrl_quantity import QrlQuantity


def map_rest_order(payload: dict) -> dict:
    """Return normalized order fields; caller can wrap to domain entity later."""
    return {
        "id": payload.get("orderId"),
        "client_order_id": payload.get("clientOrderId") or payload.get("origClientOrderId"),
        "price": QrlPrice(payload["price"]) if payload.get("price") else None,
        "quantity": QrlQuantity(payload["origQty"]) if payload.get("origQty") else None,
        "executed_quantity": QrlQuantity(payload["executedQty"]) if payload.get("executedQty") else None,
        "status": payload.get("status"),
        "side": payload.get("side"),
        "type": payload.get("type"),
    }
