class MexcClient:
    """Placeholder MEXC client (no external calls)."""

    async def ping(self):
        # TODO: implement real ping
        return {"detail": "TODO: ping"}

    async def close(self):
        # TODO: close resources if any
        return None


mexc_client = MexcClient()
