from datetime import timezone
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.app.application.system.use_cases.allocation import AllocationUseCase


@pytest.mark.asyncio
async def test_allocation_use_case_returns_structured_result():
    usecase = AllocationUseCase()

    result = await usecase.execute()

    assert result.status == "ok"
    assert result.request_id
    assert result.executed_at.tzinfo is not None
    assert result.executed_at.tzinfo.utcoffset(result.executed_at) == timezone.utc.utcoffset(result.executed_at)
