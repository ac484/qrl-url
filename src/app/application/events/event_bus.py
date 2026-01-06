from typing import Any, Awaitable, Callable, Protocol, Type

DomainEvent = Any
EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        ...
