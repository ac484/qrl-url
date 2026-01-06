from dataclasses import dataclass, field

from src.app.domain.entities.account import Account
from src.app.domain.entities.order import Order
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.timestamp import Timestamp


@dataclass
class AccountState:
    """Aggregate for account balances and outstanding orders."""

    symbol: Symbol
    account: Account
    open_orders: list[Order] = field(default_factory=list)
    updated_at: Timestamp | None = None
