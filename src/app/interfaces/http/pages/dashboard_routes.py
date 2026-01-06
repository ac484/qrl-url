from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _dashboard_config() -> dict[str, Any]:
    return {
        "price_url": "/api/qrl/price",
        "kline_url": "/api/qrl/kline?interval=1m&limit=50",
        "order_url": "/api/qrl/orders",
        "balance_url": "/api/account/balance",
        "depth_url": "/api/market/depth?limit=20",
        "trades_url": "/api/market/trades?limit=50",
        "orders_url": "/api/trading/orders",
        "refresh_ms": 10_000,
    }


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """Serve the trading dashboard page."""
    return templates.TemplateResponse(
        "dashboard/index.html",
        {"request": request, "dashboard_config": _dashboard_config()},
    )
