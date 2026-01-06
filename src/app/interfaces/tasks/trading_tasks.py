"""Trading-related scheduled tasks for Cloud Scheduler/Tasks."""

from dataclasses import dataclass

from src.app.application.trading.use_cases.rebalance_qrl import (
    RebalanceQrlUseCase,
    RebalanceRequest,
)


@dataclass
class RebalanceTaskPayload:
    profile: str = "default-qrl"
    dry_run: bool = True
    request_id: str | None = None


async def run_rebalance(payload: RebalanceTaskPayload) -> dict:
    """Execute the QRL/USDT rebalance use case."""
    use_case = RebalanceQrlUseCase()
    result = await use_case.execute(
        RebalanceRequest(
            profile=payload.profile,
            dry_run=payload.dry_run,
            request_id=payload.request_id,
        )
    )
    return result.model_dump()
