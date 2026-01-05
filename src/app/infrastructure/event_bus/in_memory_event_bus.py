from collections import defaultdict
from typing import Dict, List, Type

from app.application.events.event_bus import DomainEvent, EventBus, EventHandler


class InMemoryEventBus(EventBus):
    """
    Minimal in-memory event bus for wiring domain events to handlers.

    Infrastructure concern; replaceable with Redis/Kafka later.
    """

    def __init__(self):
        self._handlers: Dict[Type, List[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: Type, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            await handler(event)
