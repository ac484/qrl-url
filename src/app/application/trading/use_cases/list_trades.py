"""Trading use case: list trades for QRL/USDT."""

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.application.trading.dtos import TradeDTO
from src.app.domain.entities.trade import Trade
from src.app.domain.value_objects.symbol import Symbol


def _serialize_trade(trade: Trade) -> dict:
    dto = TradeDTO(
        trade_id=trade.trade_id.value,
        order_id=trade.order_id.value,
        symbol=trade.symbol.value,
        side=trade.side.value,
        price=str(trade.price.value),
        quantity=str(trade.quantity.value),
        fee=str(trade.fee) if trade.fee is not None else None,
        fee_asset=trade.fee_asset,
        timestamp=trade.timestamp.value.isoformat(),
    )
    return dto.to_dict()


class ListTradesUseCase:
    def __init__(self, exchange_factory: ExchangeServiceFactory):
        self._exchange_factory = exchange_factory

    async def execute(self, symbol: str) -> list[dict]:
        async with self._exchange_factory() as exchange:
            trades = await exchange.list_trades(Symbol(symbol))
        return [_serialize_trade(trade) for trade in trades]
