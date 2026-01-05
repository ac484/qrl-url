"""FastAPI application entrypoint for the QRL/USDT trading bot."""

from fastapi import FastAPI

from src.app.interfaces.http.api import (
    account_routes,
    market_routes,
    system_routes,
    trading_routes,
    ws_routes,
)
from src.app.interfaces.http.pages import dashboard_routes


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="QRL/USDT Trading Bot",
        version="0.1.0",
    )

    app.include_router(
        account_routes.router,
        prefix="/api/account",
        tags=["account"],
    )
    app.include_router(
        market_routes.router,
        prefix="/api/market",
        tags=["market"],
    )
    app.include_router(
        system_routes.router,
        prefix="/api/system",
        tags=["system"],
    )
    app.include_router(
        trading_routes.router,
        prefix="/api/trading",
        tags=["trading"],
    )
    app.include_router(
        ws_routes.router,
        prefix="/ws",
        tags=["ws"],
    )
    app.include_router(
        dashboard_routes.router,
        tags=["pages"],
    )

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        """Health check endpoint used by deployment probes."""
        return {"status": "ok"}

    return app


app = create_app()

