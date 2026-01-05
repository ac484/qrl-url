from fastapi import FastAPI

from src.app.interfaces.http.api import (
    account_routes,
    market_routes,
    system_routes,
    trading_routes,
    ws_routes,
)


def register_all_routers(app: FastAPI) -> None:
    """Register all interface routers. Routes contain no business logic."""
    app.include_router(account_routes.router, prefix="/api/account", tags=["account"])
    app.include_router(trading_routes.router, prefix="/api/trading", tags=["trading"])
    app.include_router(market_routes.router, prefix="/api/market", tags=["market"])
    app.include_router(system_routes.router, prefix="/api/system", tags=["system"])
    app.include_router(ws_routes.router, prefix="/ws", tags=["websocket"])
