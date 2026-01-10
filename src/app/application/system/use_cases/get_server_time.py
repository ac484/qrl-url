"""
System use case: get server time.
"""

from dataclasses import dataclass

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.domain.value_objects.timestamp import Timestamp


@dataclass
class GetServerTimeOutput:
    server_time: Timestamp | None = None


class GetServerTimeUseCase:
    def __init__(self, exchange_factory: ExchangeServiceFactory):
        self._exchange_factory = exchange_factory

    async def execute(self) -> GetServerTimeOutput:
        async with self._exchange_factory() as exchange:
            server_time = await exchange.get_server_time()
        return GetServerTimeOutput(server_time=server_time)
