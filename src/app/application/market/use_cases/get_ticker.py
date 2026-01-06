"""
Market use case: get ticker for QRL/USDT.
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, timezone

from src.app.domain.value_objects.ticker import Ticker
from src.app.domain.value_objects.symbol import Symbol
from src.app.infrastructure.exchange.mexc.rest_client import MexcRestClient


@dataclass
class GetTickerInput:
    # Reserved for future filters or parameters
    pass


@dataclass
class GetTickerOutput:
    ticker: Ticker | None = None
    error: str | None = None


class GetTickerUseCase:
    """Use case to get current ticker price for QRL/USDT."""
    
    def __init__(self, client: MexcRestClient | None = None):
        """Initialize use case.
        
        Args:
            client: MEXC REST client (created if not provided)
        """
        self.client = client or MexcRestClient()
    
    async def execute(self, data: GetTickerInput | None = None) -> GetTickerOutput:
        """Execute the use case to fetch ticker data.
        
        Args:
            data: Input parameters (currently unused)
            
        Returns:
            GetTickerOutput with ticker data or error
        """
        try:
            # Fetch ticker from MEXC API
            response = await self.client.get_ticker_price(symbol="QRLUSDT")
            
            # Parse response
            price = Decimal(response.get('price', '0'))
            
            if price <= 0:
                return GetTickerOutput(error="Invalid price received from API")
            
            # Create ticker object
            # Note: MEXC ticker/price endpoint only returns price, not bid/ask
            # Using price for all values as approximation
            ticker = Ticker(
                symbol=Symbol(value="QRLUSDT"),
                last_price=price,
                bid_price=price,  # Approximation
                ask_price=price,  # Approximation
                ts=datetime.now(timezone.utc)
            )
            
            return GetTickerOutput(ticker=ticker)
            
        except Exception as e:
            return GetTickerOutput(error=f"Failed to fetch ticker: {str(e)}")
