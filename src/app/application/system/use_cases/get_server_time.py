"""
System use case: get server time.
"""

from dataclasses import dataclass
from src.app.domain.value_objects.timestamp import Timestamp


@dataclass
class GetServerTimeOutput:
    server_time: Timestamp | None = None


class GetServerTimeUseCase:
    def execute(self) -> GetServerTimeOutput:
        # TODO: retrieve via port
        return GetServerTimeOutput()
