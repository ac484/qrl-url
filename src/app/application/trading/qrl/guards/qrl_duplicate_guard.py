def prevent_duplicate(client_order_id: str | None, existing_ids: set[str] | None = None) -> None:
    if client_order_id and existing_ids and client_order_id in existing_ids:
        raise ValueError("Duplicate clientOrderId for QRL order")
