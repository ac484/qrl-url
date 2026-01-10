from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class OrderDTO:
    order_id: str
    symbol: str
    side: str
    type: str
    status: str
    price: str | None
    quantity: str
    executed_quantity: str | None
    cumulative_quote_quantity: str | None
    client_order_id: str | None
    created_at: str
    updated_at: str | None
    time_in_force: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class TradeDTO:
    trade_id: str
    order_id: str
    symbol: str
    side: str
    price: str
    quantity: str
    fee: str | None
    fee_asset: str | None
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)
