"""FastAPI dependency providers for interface layer."""

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.infrastructure.exchange.mexc.service import build_mexc_exchange_service
from src.app.infrastructure.exchange.mexc.settings import MexcSettings


def build_exchange_factory(settings: MexcSettings | None = None) -> ExchangeServiceFactory:
    """Return a factory that builds a fresh exchange adapter per request."""

    def factory():
        return build_mexc_exchange_service(settings or MexcSettings())

    return factory


def get_exchange_factory() -> ExchangeServiceFactory:
    """Default dependency for constructing exchange adapters."""

    return build_exchange_factory()
