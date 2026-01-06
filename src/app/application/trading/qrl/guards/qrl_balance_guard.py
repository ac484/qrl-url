from decimal import Decimal


def ensure_sufficient_balance(available_usdt: Decimal, cost: Decimal) -> None:
    if cost > available_usdt:
        raise ValueError("Insufficient USDT balance for QRL order")
