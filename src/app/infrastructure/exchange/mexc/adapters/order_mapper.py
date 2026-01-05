from app.domain.events.order_event import OrderEvent
from app.domain.value_objects.order_id import OrderId
from app.domain.value_objects.order_status import OrderStatus
from app.domain.value_objects.price import Price
from app.domain.value_objects.quantity import Quantity
from app.domain.value_objects.symbol import Symbol
from app.infrastructure.exchange.mexc.generated import PrivateOrdersV3Api_pb2


def order_proto_to_domain(proto: PrivateOrdersV3Api_pb2.PrivateOrdersV3Api) -> OrderEvent:
    # MEXC push includes status as int; default to NEW when unmapped
    status_value = "NEW"
    try:
        status_value = str(proto.status).upper()
    except Exception:
        status_value = "NEW"

    try:
        status = OrderStatus(status_value)
    except ValueError:
        status = OrderStatus("NEW")

    return OrderEvent(
        order_id=OrderId(proto.id),
        symbol=Symbol("QRLUSDT"),
        price=Price(float(proto.price)),
        quantity=Quantity(float(proto.quantity)),
        status=status,
        timestamp=proto.createTime,
    )
