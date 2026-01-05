"""Entrypoint module for the FastAPI application."""

import asyncio
import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - optional in production images
    def load_dotenv() -> None:  # type: ignore
        return None

from fastapi import FastAPI
import uvicorn

from src.app.interfaces.http.api import (
    account_routes,
    market_routes,
    system_routes,
    trading_routes,
    ws_routes,
)
from src.app.interfaces.http.pages import dashboard_routes
from src.app.application.exchange.mexc_service import MexcService
from src.app.infrastructure.exchange.mexc.rest_client import MexcRestClient
from src.app.infrastructure.exchange.mexc.settings import MexcSettings

load_dotenv()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="QRL/USDT Trading Bot",
        version="0.1.0",
    )

    app.include_router(account_routes.router, prefix="/api/account", tags=["account"])
    app.include_router(market_routes.router, prefix="/api/market", tags=["market"])
    app.include_router(system_routes.router, prefix="/api/system", tags=["system"])
    app.include_router(trading_routes.router, prefix="/api/trading", tags=["trading"])
    app.include_router(ws_routes.router, prefix="/ws", tags=["ws"])
    app.include_router(dashboard_routes.router, tags=["pages"])

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        """Health check endpoint used by deployment probes."""
        return {"status": "ok"}

    return app


app = create_app()


async def _demo_mexc_usage() -> None:
    """Demonstrate how to initialize the MexcService and call a simple API."""
    try:
        settings = MexcSettings()
    except Exception as exc:  # pragma: no cover - demonstration only
        print(f"[demo] Unable to load MEXC credentials: {exc}")
        return

    async with MexcService(MexcRestClient(settings)) as service:
        server_time = await service.get_server_time()
        print(f"[demo] MEXC server time: {server_time.value.isoformat()}")


def _should_run_demo() -> bool:
    """Gate demo execution behind an opt-in flag."""
    return os.getenv("RUN_MEXC_DEMO", "0") == "1"


def _run_server() -> None:
    """Start the uvicorn server using environment configuration."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host=host, port=port, reload=False)


if __name__ == "__main__":
    if _should_run_demo():
        asyncio.run(_demo_mexc_usage())
    _run_server()

__all__ = ["app"]
