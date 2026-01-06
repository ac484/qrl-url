from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Callable, Iterable

from src.app.application.exchange.mexc_service import (
    MexcService,
    PlaceOrderRequest,
    build_mexc_service,
)
from src.app.domain.strategies.rebalance import (
    DecisionContext,
    RebalanceConfig,
    RebalancePlan,
    build_rebalance_plan,
)
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.time_in_force import TimeInForce
from src.app.infrastructure.exchange.mexc.settings import MexcSettings

logger = logging.getLogger("rebalance")


@dataclass
class RebalanceRequest:
    profile: str = "default-qrl"
    dry_run: bool = True
    request_id: str | None = None
    target_ratio_qrl: Decimal | None = None
    tolerance: Decimal | None = None
    min_notional_usdt: Decimal | None = None


@dataclass
class PlannedOrderResult:
    side: str
    quantity: str
    price: str
    reason: str


@dataclass
class RebalanceResponse:
    request_id: str
    profile: str
    dry_run: bool
    plan: RebalancePlan
    executed_orders: Iterable[dict] = field(default_factory=list)

    def model_dump(self) -> dict:
        return {
            "request_id": self.request_id,
            "profile": self.profile,
            "dry_run": self.dry_run,
            "plan": {
                "target_ratio_qrl": str(self.plan.target_ratio_qrl),
                "current_ratio_qrl": str(self.plan.current_ratio_qrl),
                "delta_value_usdt": str(self.plan.delta_value_usdt),
                "orders": [
                    {
                        "side": order.side.value,
                        "quantity": str(order.quantity.value),
                        "price": str(order.price.value),
                        "reason": order.reason,
                    }
                    for order in self.plan.orders
                ],
            },
            "executed": list(self.executed_orders),
        }


class RebalanceQrlUseCase:
    """Orchestrate QRL/USDT rebalance driven by Cloud Scheduler/Tasks."""

    def __init__(
        self,
        service_factory: Callable[[MexcSettings], MexcService] | None = None,
        config: RebalanceConfig | None = None,
    ):
        self._service_factory = service_factory or build_mexc_service
        self._config = config or RebalanceConfig(
            target_ratio_qrl=Decimal(os.getenv("REBALANCE_TARGET_QRL", "0.5")),
            tolerance=Decimal(os.getenv("REBALANCE_TOLERANCE", "0.02")),
            min_notional_usdt=Decimal(os.getenv("REBALANCE_MIN_NOTIONAL", "10")),
            replay_ttl_seconds=int(os.getenv("SCHEDULER_REPLAY_TTL_SEC", "300")),
        )

    async def execute(self, request: RebalanceRequest) -> RebalanceResponse:
        request_id = request.request_id or str(uuid.uuid4())
        settings = MexcSettings()
        service = self._service_factory(settings)
        config = _resolve_config(self._config, request)
        logger.info(
            {
                "msg": "rebalance.start",
                "request_id": request_id,
                "profile": request.profile,
                "dry_run": request.dry_run,
            }
        )

        async with service:
            price = await service.get_price(Symbol("QRL/USDT"))
            account = await service.get_account()

            qrl_free = _get_balance(account.balances, "QRL")
            usdt_free = _get_balance(account.balances, "USDT")

            ctx = DecisionContext(price=price, qrl_free=qrl_free, usdt_free=usdt_free)
            plan = build_rebalance_plan(config, ctx)

            executed: list[dict] = []

            if plan.has_action and not request.dry_run:
                for order in plan.orders:
                    place_req = PlaceOrderRequest(
                        symbol=Symbol("QRL/USDT"),
                        side=order.side,
                        order_type=OrderType("MARKET"),
                        quantity=Quantity(order.quantity.value),
                        price=None,
                        time_in_force=TimeInForce("IOC"),
                        client_order_id=request_id,
                    )
                    placed = await service.place_order(place_req)
                    executed.append(
                        {
                            "side": placed.side.value,
                            "quantity": str(placed.quantity.value),
                            "price": str(placed.price),
                            "order_id": placed.order_id.value,
                            "status": placed.status.value if placed.status else None,
                        }
                    )

            logger.info(
                {
                    "msg": "rebalance.end",
                    "request_id": request_id,
                    "profile": request.profile,
                    "dry_run": request.dry_run,
                    "orders_planned": len(plan.orders),
                    "orders_executed": len(executed),
                }
            )

            return RebalanceResponse(
                request_id=request_id,
                profile=request.profile,
                dry_run=request.dry_run,
                plan=plan,
                executed_orders=executed,
            )


def _get_balance(balances, asset: str) -> Decimal:
    for bal in balances:
        if bal.asset.upper() == asset.upper():
            return bal.free
    return Decimal("0")


def _resolve_config(base: RebalanceConfig, req: RebalanceRequest) -> RebalanceConfig:
    return RebalanceConfig(
        target_ratio_qrl=req.target_ratio_qrl if req.target_ratio_qrl is not None else base.target_ratio_qrl,
        tolerance=req.tolerance if req.tolerance is not None else base.tolerance,
        min_notional_usdt=req.min_notional_usdt if req.min_notional_usdt is not None else base.min_notional_usdt,
        replay_ttl_seconds=base.replay_ttl_seconds,
    )
