class GetOrderUseCase:
    """Use case: get order status."""

    async def execute(self, order_id: str):
        # TODO: implement get order via infrastructure client
        return {"detail": "TODO: get_order", "order_id": order_id}
