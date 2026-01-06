import asyncio
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query

from src.app.application.market.qrl.get_qrl_depth import GetQrlDepth
from src.app.application.market.qrl.get_qrl_kline import GetQrlKline
from src.app.application.market.qrl.get_qrl_price import GetQrlPrice
from src.app.application.market.use_cases.get_market_trades import GetMarketTradesUseCase
from src.app.application.trading.qrl.cancel_qrl_order import CancelQrlOrder
from src.app.application.trading.qrl.get_qrl_order import GetQrlOrder
from src.app.application.trading.qrl.place_qrl_order import PlaceQrlOrder
from src.app.application.trading.use_cases.rebalance_qrl import RebalanceQrlUseCase, RebalanceRequest
from src.app.application.account.use_cases.get_balance import GetBalanceUseCase
from src.app.application.trading.use_cases.list_orders import ListOrdersUseCase
from src.app.application.trading.use_cases.list_trades import ListTradesUseCase
from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.qrl_quantity import QrlQuantity
from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient
from src.app.infrastructure.exchange.mexc.qrl.qrl_settings import QrlSettings
from src.app.interfaces.http.schemas import PlaceOrderRequest

router = APIRouter()


def _client() -> QrlRestClient:
    return QrlRestClient(QrlSettings())


@router.get("/price")
async def qrl_price():
    usecase = GetQrlPrice(_client())
    try:
        snapshot = await usecase.execute()
        return snapshot.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch QRL price: {exc}") from exc


@router.get("/kline")
async def qrl_kline(interval: str = Query(default="1m"), limit: int = Query(default=50, ge=1, le=500)):
    usecase = GetQrlKline(_client(), interval=interval, limit=limit)
    try:
        raw = await usecase.execute()
        normalized = [
            {"timestamp": item[0], "open": item[1], "high": item[2], "low": item[3], "close": item[4], "volume": item[5]}
            for item in raw
        ]
        return normalized
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch QRL klines: {exc}") from exc


@router.get("/depth")
async def qrl_depth(limit: int = Query(default=50, ge=5, le=1000)):
    usecase = GetQrlDepth(_client(), limit=limit)
    try:
        return await usecase.execute()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch QRL depth: {exc}") from exc


@router.post("/orders")
async def qrl_place_order(request: PlaceOrderRequest):
    usecase = PlaceQrlOrder(_client())
    price_vo = QrlPrice(request.price) if request.price is not None else None
    qty_vo = QrlQuantity(request.quantity)
    return await usecase.execute(
        side=request.side,
        order_type=request.order_type,
        price=price_vo,
        quantity=qty_vo,
        time_in_force=request.time_in_force,
        client_order_id=request.client_order_id,
    )


@router.post("/orders/{order_id}/cancel")
async def qrl_cancel_order(order_id: str):
    usecase = CancelQrlOrder(_client())
    return await usecase.execute(order_id=order_id, client_order_id=None)


@router.get("/orders/{order_id}")
async def qrl_get_order(order_id: str):
    usecase = GetQrlOrder(_client())
    return await usecase.execute(order_id=order_id, client_order_id=None)


@router.get("/summary")
async def qrl_summary(
    interval: str = Query(default="1m"),
    kline_limit: int = Query(default=50, ge=1, le=500),
    depth_limit: int = Query(default=50, ge=5, le=1000),
    trades_limit: int = Query(default=50, ge=1, le=500),
):
    """Aggregate price, kline, depth, and balance for dashboard consumption."""
    price_uc = GetQrlPrice(_client())
    kline_uc = GetQrlKline(_client(), interval=interval, limit=kline_limit)
    depth_uc = GetQrlDepth(_client(), limit=depth_limit)
    balance_uc = GetBalanceUseCase()
    orders_uc = ListOrdersUseCase()
    trades_uc = ListTradesUseCase()
    market_trades_uc = GetMarketTradesUseCase()

    price_result, kline_result, depth_result, balance_result, orders, trades, market_trades = await asyncio.gather(
        price_uc.execute(),
        kline_uc.execute(),
        depth_uc.execute(),
        balance_uc.execute(),
        orders_uc.execute(symbol="QRLUSDT"),
        trades_uc.execute("QRLUSDT"),
        market_trades_uc.execute(),
    )

    normalized_klines = [
        {"timestamp": item[0], "open": item[1], "high": item[2], "low": item[3], "close": item[4], "volume": item[5]}
        for item in kline_result
    ]
    return {
        "price": price_result.to_dict(),
        "klines": normalized_klines,
        "depth": depth_result,
        "balance": balance_result,
        "orders": orders,
        "trades": trades,
        "market_trades": market_trades[:trades_limit],
    }


@router.post("/allocation")
async def qrl_allocation(dry_run: bool = Query(default=True), tolerance: float = Query(default=0.01)):
    """
    Smart allocation endpoint to keep QRL:USDT at ~50/50 with 1% band by default.
    """
    use_case = RebalanceQrlUseCase()
    response = await use_case.execute(
        RebalanceRequest(
            dry_run=dry_run,
            target_ratio_qrl=Decimal("0.5"),
            tolerance=Decimal(str(tolerance)),
            min_notional_usdt=Decimal("0.5"),
            max_notional_usdt=Decimal("2"),
        )
    )
    return response.model_dump()
