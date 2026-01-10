"""Trading use case: list trades for QRL/USDT."""

from src.app.application.exchange.mexc_service import MexcService, build_mexc_service
from src.app.domain.entities.trade import Trade
from src.app.domain.value_objects.symbol import Symbol
from src.app.infrastructure.exchange.mexc.settings import MexcSettings


def _serialize_trade(trade: Trade) -> dict:
    return {
        "trade_id": trade.trade_id.value,
        "order_id": trade.order_id.value,
        "symbol": trade.symbol.value,
        "side": trade.side.value,
        "price": str(trade.price.value),
        "quantity": str(trade.quantity.value),
        "fee": str(trade.fee) if trade.fee is not None else None,
        "fee_asset": trade.fee_asset,
        "timestamp": trade.timestamp.value.isoformat(),
    }


class ListTradesUseCase:
    settings: MexcSettings | None = None

    def __init__(self, settings: MexcSettings | None = None):
        self.settings = settings

    async def execute(self, symbol: str) -> list[dict]:
        service = build_mexc_service(self.settings or MexcSettings())
        async with service as svc:
            trades = await svc.list_trades(Symbol(symbol))
        return [_serialize_trade(trade) for trade in trades]
