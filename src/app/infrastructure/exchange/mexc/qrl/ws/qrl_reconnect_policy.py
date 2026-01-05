class QrlReconnectPolicy:
    """Simple reconnect/backoff helper for QRL WS."""

    def __init__(self, max_retries: int = 5, base_delay: float = 1.0):
        self._max_retries = max_retries
        self._base_delay = base_delay

    def should_retry(self, attempt: int) -> bool:
        return attempt < self._max_retries

    def delay_seconds(self, attempt: int) -> float:
        return self._base_delay * max(1, attempt)
