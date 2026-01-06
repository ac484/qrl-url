"""System use case to expose an allocation trigger for schedulers."""

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class AllocationResult:
    """Outcome returned when an allocation task is triggered."""

    request_id: str
    status: str
    executed_at: datetime


class AllocationUseCase:
    """Provide a lightweight allocation trigger for Cloud Scheduler."""

    async def execute(self) -> AllocationResult:
        """Return a structured result confirming the allocation trigger."""
        return AllocationResult(
            request_id=str(uuid4()),
            status="ok",
            executed_at=datetime.now(timezone.utc),
        )
