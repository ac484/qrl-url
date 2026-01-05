class CancelOrderUseCase:
    """Use case: cancel an existing order."""

    async def execute(self, order_id: str):
        # TODO: implement cancel order via infrastructure client
        return {"detail": "TODO: cancel_order", "order_id": order_id}
