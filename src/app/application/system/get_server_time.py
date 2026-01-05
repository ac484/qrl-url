from datetime import datetime


class GetServerTimeUseCase:
    """Use case: get server time."""

    async def execute(self):
        # TODO: replace with MEXC server time once available
        return {"server_time": datetime.utcnow().isoformat(), "note": "TODO: use MEXC time"}
