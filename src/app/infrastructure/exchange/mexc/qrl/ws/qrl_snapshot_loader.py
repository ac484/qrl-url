from src.app.infrastructure.exchange.mexc.qrl.qrl_rest_client import QrlRestClient
from src.app.infrastructure.exchange.mexc.qrl.ws.qrl_stream_state import QrlStreamState


class QrlSnapshotLoader:
    def __init__(self, rest_client: QrlRestClient):
        self._rest_client = rest_client

    async def load(self, state: QrlStreamState, limit: int = 50) -> dict:
        async with self._rest_client as client:
            snapshot = await client.depth(limit=limit)
        state.last_update_id = snapshot.get("lastUpdateId")
        return snapshot
