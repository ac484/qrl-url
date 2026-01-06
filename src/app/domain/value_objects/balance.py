"""Balance value object for account balances."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Balance:
    """Account balance for an asset."""
    
    asset: str
    free: Decimal
    locked: Decimal
    
    @property
    def total(self) -> Decimal:
        """Calculate total balance (free + locked)."""
        return self.free + self.locked
    
    def __post_init__(self):
        """Validate balance values."""
        if self.free < 0:
            raise ValueError("Free balance cannot be negative")
        if self.locked < 0:
            raise ValueError("Locked balance cannot be negative")
