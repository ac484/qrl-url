from app.domain.events.trade_event import TradeEvent
from app.domain.value_objects.price import Price
from app.domain.value_objects.quantity import Quantity
from app.domain.value_objects.symbol import Symbol
from app.domain.value_objects.trade_id import TradeId
from app.infrastructure.exchange.mexc.generated import PublicDealsV3Api_pb2


def trade_proto_to_domain(
    symbol: Symbol, proto: PublicDealsV3Api_pb2.PublicDealsV3ApiItem
) -> TradeEvent:
    # tradeType: 1=buy, 2=sell in MEXC WS push; treat 2 as maker sell
    is_buyer_maker = proto.tradeType == 2
    return TradeEvent(
        trade_id=TradeId(str(proto.time)),
        symbol=symbol,
        price=Price(float(proto.price)),
        quantity=Quantity(float(proto.quantity)),
        is_buyer_maker=is_buyer_maker,
        timestamp=proto.time,
    )
