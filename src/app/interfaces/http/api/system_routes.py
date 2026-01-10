from fastapi import APIRouter, Depends

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.application.system.use_cases.get_server_time import GetServerTimeUseCase
from src.app.application.system.use_cases.ping import PingUseCase
from src.app.interfaces.http.dependencies import get_exchange_factory

router = APIRouter()


@router.get("/ping")
async def ping():
    """Ping endpoint."""
    usecase = PingUseCase()
    return await usecase.execute()


@router.get("/time")
async def get_server_time(exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory)):
    """Get server time."""
    usecase = GetServerTimeUseCase(exchange_factory)
    return await usecase.execute()
