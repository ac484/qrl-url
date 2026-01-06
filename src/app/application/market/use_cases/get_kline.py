"""
Market use case: get kline data for QRL/USDT.
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, timezone

from src.app.domain.value_objects.kline import Kline
from src.app.infrastructure.exchange.mexc.rest_client import MexcRestClient


@dataclass
class GetKlineInput:
    interval: str = "1m"
    limit: int = 50


@dataclass
class GetKlineOutput:
    klines: list[Kline] = None
    error: str | None = None
    
    def __post_init__(self):
        if self.klines is None:
            object.__setattr__(self, 'klines', [])


class GetKlineUseCase:
    """Use case to get kline/candlestick data for QRL/USDT."""
    
    def __init__(self, client: MexcRestClient | None = None, interval: str = "1m", limit: int = 50):
        """Initialize use case.
        
        Args:
            client: MEXC REST client (created if not provided)
            interval: Kline interval (1m, 5m, 15m, 1h, etc.)
            limit: Number of klines to fetch
        """
        self.client = client or MexcRestClient()
        self.interval = interval
        self.limit = limit
    
    async def execute(self, data: GetKlineInput | None = None) -> GetKlineOutput:
        """Execute the use case to fetch kline data.
        
        Args:
            data: Input parameters with interval and limit
            
        Returns:
            GetKlineOutput with kline data or error
        """
        try:
            interval = data.interval if data else self.interval
            limit = data.limit if data else self.limit
            
            # Fetch klines from MEXC API
            response = await self.client.get_klines(
                symbol="QRLUSDT",
                interval=interval,
                limit=limit
            )
            
            # Parse response - MEXC returns array of arrays
            # Format: [openTime, open, high, low, close, volume, closeTime, quoteVolume, ...]
            klines = []
            for kline_data in response:
                if len(kline_data) < 8:
                    continue
                
                try:
                    kline = Kline(
                        open_time=datetime.fromtimestamp(int(kline_data[0]) / 1000, tz=timezone.utc),
                        open=Decimal(str(kline_data[1])),
                        high=Decimal(str(kline_data[2])),
                        low=Decimal(str(kline_data[3])),
                        close=Decimal(str(kline_data[4])),
                        volume=Decimal(str(kline_data[5])),
                        close_time=datetime.fromtimestamp(int(kline_data[6]) / 1000, tz=timezone.utc),
                        quote_volume=Decimal(str(kline_data[7]))
                    )
                    klines.append(kline)
                except (ValueError, IndexError) as e:
                    # Skip invalid kline data
                    continue
            
            return GetKlineOutput(klines=klines)
            
        except Exception as e:
            return GetKlineOutput(error=f"Failed to fetch klines: {str(e)}")
