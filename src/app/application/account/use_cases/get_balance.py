"""
Account use case: get subaccount balance.
"""

from dataclasses import dataclass
from decimal import Decimal

from src.app.domain.value_objects.balance import Balance
from src.app.infrastructure.exchange.mexc.rest_client import MexcRestClient


@dataclass
class GetBalanceOutput:
    balances: list[Balance] = None
    error: str | None = None
    
    def __post_init__(self):
        if self.balances is None:
            object.__setattr__(self, 'balances', [])


class GetBalanceUseCase:
    """Use case to get account balance."""
    
    def __init__(self, client: MexcRestClient | None = None):
        """Initialize use case.
        
        Args:
            client: MEXC REST client (created if not provided)
        """
        self.client = client or MexcRestClient()
    
    async def execute(self) -> GetBalanceOutput:
        """Execute the use case to fetch account balance.
        
        Returns:
            GetBalanceOutput with balance data or error
        """
        try:
            # Fetch account data from MEXC API
            response = await self.client.get_account()
            
            # Parse balances from response
            balances = []
            balance_data = response.get('balances', [])
            
            for item in balance_data:
                try:
                    asset = item.get('asset', '')
                    free = Decimal(item.get('free', '0'))
                    locked = Decimal(item.get('locked', '0'))
                    
                    # Only include non-zero balances
                    if free > 0 or locked > 0:
                        balance = Balance(
                            asset=asset,
                            free=free,
                            locked=locked
                        )
                        balances.append(balance)
                except (ValueError, KeyError) as e:
                    # Skip invalid balance data
                    continue
            
            return GetBalanceOutput(balances=balances)
            
        except Exception as e:
            return GetBalanceOutput(error=f"Failed to fetch balance: {str(e)}")
