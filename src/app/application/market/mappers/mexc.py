from decimal import Decimal
from datetime import datetime, timezone

from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.ticker import Ticker


def map_ws_ticker_event_to_domain(event: dict) -> Ticker:
    """Map MEXC WS ticker event to Ticker VO."""
    return Ticker(
        symbol=Symbol(str(event.get("symbol", "QRLUSDT"))),
        last_price=Decimal(str(event.get("last", "0"))),
        bid_price=Decimal(str(event.get("bidPrice", "0"))),
        ask_price=Decimal(str(event.get("askPrice", "0"))),
        ts=datetime.fromtimestamp(
            int(event.get("ts", 0)) / 1000, tz=timezone.utc
        ),
    )
