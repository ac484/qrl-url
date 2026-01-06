"""
MEXC REST API client with authentication support.
Implements MEXC v3 API endpoints with proper signing and error handling.
"""

import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx

from src.app.infrastructure.config import MexcSettings


class MexcRestClient:
    """MEXC REST API client with authentication."""
    
    def __init__(self, settings: Optional[MexcSettings] = None):
        """Initialize MEXC REST client.
        
        Args:
            settings: MEXC API settings. If None, loads from environment.
        """
        self.settings = settings or MexcSettings()
        self.base_url = self.settings.MEXC_BASE_URL
        self.api_key = self.settings.MEXC_API_KEY
        self.secret_key = self.settings.MEXC_SECRET_KEY
        self.timeout = self.settings.MEXC_TIMEOUT
        
    def _generate_signature(self, query_string: str) -> str:
        """Generate HMAC SHA256 signature for authenticated requests.
        
        Args:
            query_string: URL-encoded query parameters
            
        Returns:
            Hex-encoded signature
        """
        return hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False
    ) -> Dict[str, Any]:
        """Make HTTP request to MEXC API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            signed: Whether request requires authentication
            
        Returns:
            JSON response as dictionary
            
        Raises:
            httpx.HTTPError: On HTTP errors
        """
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if params is None:
            params = {}
        
        # Add timestamp and signature for authenticated requests
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            query_string = urlencode(params)
            params['signature'] = self._generate_signature(query_string)
            headers['X-MEXC-APIKEY'] = self.api_key
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_ticker_price(self, symbol: str = "QRLUSDT") -> Dict[str, Any]:
        """Get latest price for a symbol.
        
        Args:
            symbol: Trading pair symbol (default: QRLUSDT)
            
        Returns:
            Ticker price data
        """
        return await self._request(
            method="GET",
            endpoint="/api/v3/ticker/price",
            params={"symbol": symbol},
            signed=False
        )
    
    async def get_klines(
        self,
        symbol: str = "QRLUSDT",
        interval: str = "1m",
        limit: int = 50
    ) -> list:
        """Get kline/candlestick data.
        
        Args:
            symbol: Trading pair symbol (default: QRLUSDT)
            interval: Time interval (1m, 5m, 15m, 1h, etc.)
            limit: Number of candles to return
            
        Returns:
            List of kline data
        """
        return await self._request(
            method="GET",
            endpoint="/api/v3/klines",
            params={
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            },
            signed=False
        )
    
    async def get_account(self) -> Dict[str, Any]:
        """Get account information including balances.
        
        Returns:
            Account data with balances
        """
        return await self._request(
            method="GET",
            endpoint="/api/v3/account",
            params={},
            signed=True
        )
