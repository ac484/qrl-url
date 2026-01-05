Purpose: Interface layer (HTTP/WS/tasks controllers). Handles DTO/route definitions only; no business logic.

Allowed dependencies:
- Can import application use cases.

Forbidden:
- Cannot import infrastructure, domain entities/VOs directly, or external SDKs/clients.
