from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class QrlStreamState:
    last_update_id: int | None = None
    backlog: list[dict[str, Any]] = field(default_factory=list)

    def apply_update(self, update_id: int) -> None:
        if self.last_update_id is None or update_id > self.last_update_id:
            self.last_update_id = update_id
