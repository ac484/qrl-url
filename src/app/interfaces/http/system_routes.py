from fastapi import APIRouter

from src.app.application.system.get_server_time import GetServerTimeUseCase
from src.app.application.system.ping import PingUseCase

router = APIRouter()


@router.get("/ping")
async def ping():
    """Ping endpoint."""
    usecase = PingUseCase()
    return await usecase.execute()


@router.get("/time")
async def get_server_time():
    """Get server time."""
    usecase = GetServerTimeUseCase()
    return await usecase.execute()
