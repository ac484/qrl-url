from decimal import Decimal

import pytest

from src.app.domain.services.qrl_guards import (
    enforce_rate_limit,
    ensure_price_range,
    ensure_sufficient_balance,
    prevent_duplicate,
)
from src.app.domain.value_objects.qrl_price import QrlPrice


def test_ensure_price_range_within_bounds() -> None:
    price = QrlPrice("1.0001")
    min_price = QrlPrice("1.0000")
    max_price = QrlPrice("2.0000")

    ensure_price_range(price, min_allowed=min_price, max_allowed=max_price)


def test_ensure_price_range_out_of_bounds_raises() -> None:
    price = QrlPrice("0.9999")
    min_price = QrlPrice("1.0000")

    with pytest.raises(ValueError):
        ensure_price_range(price, min_allowed=min_price)


def test_ensure_price_range_above_max_raises() -> None:
    price = QrlPrice("2.0001")
    max_price = QrlPrice("2.0000")

    with pytest.raises(ValueError):
        ensure_price_range(price, max_allowed=max_price)


def test_ensure_sufficient_balance_passes_when_funded() -> None:
    ensure_sufficient_balance(Decimal("10.0"), Decimal("5.0"))


def test_ensure_sufficient_balance_raises_when_insufficient() -> None:
    with pytest.raises(ValueError):
        ensure_sufficient_balance(Decimal("1.0"), Decimal("2.0"))


def test_prevent_duplicate_raises_on_existing_id() -> None:
    with pytest.raises(ValueError):
        prevent_duplicate("abc", existing_ids={"abc", "other"})


def test_prevent_duplicate_allows_new_id() -> None:
    prevent_duplicate("abc", existing_ids={"def"})


def test_enforce_rate_limit_raises_on_limit_exceeded() -> None:
    with pytest.raises(ValueError):
        enforce_rate_limit(0)


def test_enforce_rate_limit_allows_positive_quota() -> None:
    enforce_rate_limit(1)
