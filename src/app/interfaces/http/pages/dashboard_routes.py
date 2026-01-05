import pathlib

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/dashboard")
async def dashboard():
    """Dashboard page controller placeholder."""
    return {"message": "dashboard placeholder"}


@router.get("/dashboard/trading", response_class=HTMLResponse)
async def trading_dashboard():
    """Serve the trading dashboard page."""
    base = pathlib.Path(__file__).parent / "templates" / "dashboard" / "trading_dashboard.html"
    return HTMLResponse(base.read_text(encoding="utf-8"))
