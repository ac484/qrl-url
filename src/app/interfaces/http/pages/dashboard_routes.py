from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard() -> HTMLResponse:
    """Serve the trading dashboard page."""
    base = Path(__file__).parent / "templates" / "dashboard" / "index.html"
    return HTMLResponse(base.read_text(encoding="utf-8"))
