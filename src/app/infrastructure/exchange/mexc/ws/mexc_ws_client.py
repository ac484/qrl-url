from typing import AsyncIterator, Optional


class MexcWebSocketClient:
    """
    Thin wrapper over MEXC V3 WebSocket transport.

    This class is intentionally minimal; transport details (auth, ping/pong,
    reconnect) can be layered later without leaking into Domain/Application.
    """

    async def subscribe(
        self, channel: str, symbol: Optional[str] = None
    ) -> AsyncIterator[object]:
        """
        Yield raw protobuf messages for the given channel.

        Args:
            channel: MEXC stream channel (e.g., depth, deals, orders).
            symbol: Optional trading pair symbol when required by the stream.
        """
        raise NotImplementedError("WebSocket transport not wired yet.")
