from src.app.domain.value_objects.qrl_price import QrlPrice


def ensure_price_range(price: QrlPrice, min_allowed: QrlPrice | None = None, max_allowed: QrlPrice | None = None) -> None:
    if min_allowed and price.value < min_allowed.value:
        raise ValueError("Price below allowed threshold")
    if max_allowed and price.value > max_allowed.value:
        raise ValueError("Price above allowed threshold")
