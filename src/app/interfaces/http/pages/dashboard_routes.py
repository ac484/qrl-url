from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


def _render_dashboard() -> HTMLResponse:
    base = Path(__file__).parent / "templates" / "dashboard" / "index.html"
    return HTMLResponse(base.read_text(encoding="utf-8"))


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard() -> HTMLResponse:
    """Serve the trading dashboard page."""
    return _render_dashboard()
