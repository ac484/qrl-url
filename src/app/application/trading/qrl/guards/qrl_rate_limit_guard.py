def enforce_rate_limit(remaining_requests: int) -> None:
    if remaining_requests <= 0:
        raise ValueError("Rate limit reached for QRL operations")
