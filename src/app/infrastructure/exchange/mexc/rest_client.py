import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import httpx

from src.app.infrastructure.exchange.mexc.settings import MexcSettings


class MexcRestClient:
    """Async REST client for MEXC spot API v3."""

    def __init__(self, settings: MexcSettings):
        self._settings = settings
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "MexcRestClient":
        self._client = httpx.AsyncClient(
            base_url=self._settings.base_url,
            timeout=self._settings.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _assert_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("MexcRestClient context has not been entered")
        return self._client

    def _signed_params(self, params: dict[str, Any]) -> dict[str, Any]:
        payload = {k: v for k, v in params.items() if v is not None}
        payload.setdefault("timestamp", int(time.time() * 1000))
        payload.setdefault("recvWindow", self._settings.recv_window)
        query = urlencode(payload, doseq=True)
        signature = hmac.new(
            self._settings.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        payload["signature"] = signature
        return payload

    async def _request(
        self, method: str, path: str, params: dict[str, Any] | None = None, signed: bool = False
    ) -> dict[str, Any]:
        client = self._assert_client()
        request_params = self._signed_params(params or {}) if signed else params or {}
        headers = {"X-MEXC-APIKEY": self._settings.api_key} if signed else None
        response = await client.request(method, path, params=request_params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def ping(self) -> dict[str, Any]:
        return await self._request("GET", "/api/v3/ping")

    async def get_server_time(self) -> dict[str, Any]:
        return await self._request("GET", "/api/v3/time")

    async def get_account(self) -> dict[str, Any]:
        return await self._request("GET", "/api/v3/account", signed=True)

    async def create_order(
        self,
        *,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str | None = None,
        price: str | None = None,
        time_in_force: str | None = None,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "price": price,
            "timeInForce": time_in_force,
            "newClientOrderId": client_order_id,
        }
        return await self._request("POST", "/api/v3/order", params=params, signed=True)

    async def get_order(
        self, *, symbol: str, order_id: str | None = None, client_order_id: str | None = None
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": client_order_id,
        }
        return await self._request("GET", "/api/v3/order", params=params, signed=True)

    async def cancel_order(
        self, *, symbol: str, order_id: str | None = None, client_order_id: str | None = None
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": client_order_id,
        }
        return await self._request("DELETE", "/api/v3/order", params=params, signed=True)

    async def list_open_orders(self, *, symbol: str | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"symbol": symbol} if symbol else {}
        result = await self._request("GET", "/api/v3/openOrders", params=params, signed=True)
        if isinstance(result, list):
            return result
        return []

    async def list_trades(self, *, symbol: str, limit: int = 50) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"symbol": symbol, "limit": limit}
        result = await self._request("GET", "/api/v3/myTrades", params=params, signed=True)
        if isinstance(result, list):
            return result
        return []
