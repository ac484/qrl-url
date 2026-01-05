from dataclasses import dataclass
from src.app.domain.value_objects.balance import Balance
from src.app.domain.value_objects.timestamp import Timestamp


@dataclass
class Account:
    """Spot account snapshot."""

    can_trade: bool
    update_time: Timestamp
    balances: list[Balance]
