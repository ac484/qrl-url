from decimal import Decimal

from src.app.application.ports.exchange_service import ExchangeServiceFactory, PlaceOrderRequest
from src.app.application.trading.use_cases.place_order import _serialize_order
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.qrl_quantity import QrlQuantity
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce


class PlaceQrlOrder:
    """Place QRL/USDT order with fixed symbol and validated VOs."""

    def __init__(self, exchange_factory: ExchangeServiceFactory):
        self._exchange_factory = exchange_factory

    async def execute(
        self,
        *,
        side: str,
        order_type: str,
        price: Decimal | str | float | QrlPrice | None,
        quantity: Decimal | str | int | float | QrlQuantity,
        time_in_force: str | None = "GTC",
        client_order_id: str | None = None,
    ) -> dict:
        price_vo = None
        if price is not None:
            normalized_price = price if isinstance(price, QrlPrice) else QrlPrice(price)
            price_vo = Price.from_single(normalized_price.value)

        normalized_qty = quantity if isinstance(quantity, QrlQuantity) else QrlQuantity(quantity)
        quantity_vo = Quantity(normalized_qty.value)
        request = PlaceOrderRequest(
            symbol=Symbol("QRLUSDT"),
            side=Side(side),
            order_type=OrderType(order_type),
            price=price_vo,
            quantity=quantity_vo,
            time_in_force=TimeInForce(time_in_force) if time_in_force else None,
            client_order_id=client_order_id,
        )
        async with self._exchange_factory() as exchange:
            order = await exchange.place_order(request)
        return _serialize_order(order)
