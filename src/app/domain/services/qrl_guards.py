"""Guard rules for QRL trading domain logic."""

from __future__ import annotations

from decimal import Decimal

from src.app.domain.value_objects.qrl_price import QrlPrice


def ensure_price_range(
    price: QrlPrice,
    min_allowed: QrlPrice | None = None,
    max_allowed: QrlPrice | None = None,
) -> None:
    """Validate that the price stays within the optional bounds."""

    if min_allowed and price.value < min_allowed.value:
        raise ValueError("Price below allowed threshold")
    if max_allowed and price.value > max_allowed.value:
        raise ValueError("Price above allowed threshold")


def ensure_sufficient_balance(available_usdt: Decimal, cost: Decimal) -> None:
    """Ensure there is enough USDT to cover the order cost."""

    if cost > available_usdt:
        raise ValueError("Insufficient USDT balance for QRL order")


def prevent_duplicate(
    client_order_id: str | None, existing_ids: set[str] | None = None
) -> None:
    """Guard against duplicate client order identifiers."""

    if client_order_id and existing_ids and client_order_id in existing_ids:
        raise ValueError("Duplicate clientOrderId for QRL order")


def enforce_rate_limit(remaining_requests: int) -> None:
    """Ensure QRL operations remain within the allowed rate limits."""

    if remaining_requests <= 0:
        raise ValueError("Rate limit reached for QRL operations")
