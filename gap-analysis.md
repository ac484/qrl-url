# Gap analysis – qrl-url (QRL/USDT bot)

## Snapshot of the current state
- Domain layer already includes QRL-specific VOs (`QrlPrice`, `QrlQuantity`, `QrlUsdtPair`) and base order/price/trade entities.
- Application layer exposes QRL use cases for price/depth/kline and basic trading flows (place/cancel/get), plus generic balance/orders/trades queries.
- Infrastructure layer has QRL-wrapped REST/WS clients and mappers; streaming utilities (`BoundedAsyncQueue`, `RingBuffer`) and an in-memory event bus exist but are not wired in.
- Interfaces expose `/api/qrl` routes and a static dashboard page, but the page is not yet connected to live data.

## Gaps that need convergence (ordered by impact)
1) **Interfaces / UX**
- Dashboard (`interfaces/http/pages/dashboard_routes.py`) serves static HTML and never calls the QRL use cases; no websocket endpoints are wired to the page, so price/depth/trades are invisible despite the API support.
- `/api/qrl/summary` fans out seven calls per request and returns heterogeneous shapes (raw dicts and lists) without DTO normalization, making front-end consumption fragile.

2) **Application correctness & purity**
- `GetQrlPrice` returns a dict instead of a domain VO/DTO and bypasses normalization for bid/ask; other use cases leak infrastructure shapes rather than returning typed results.
- Use cases repeatedly construct REST clients/settings per request instead of accepting ports/adapters, which blocks dependency injection and reuse (e.g., for WS vs REST fallback).
- Event bus and backpressure utilities are unused; WS clients are not publishing domain events, so realtime processing/replay described in `1.md` never happens.

3) **Infrastructure resilience**
- `QrlWsClient` is defined but never integrated with mappers/event bus; no reconnect policy, snapshot loader, or ring-buffer replay is in place for depth/trade/order streams.
- No caching for hot paths (price/depth/klines) or rate-limit handling; each summary call hits MEXC directly.

4) **Testing & observability**
- No automated tests exist (unit or integration); critical value objects and QRL guards lack coverage and fixtures, and there is no CI signal.
- Minimal structured logging/metrics around exchange calls, making production debugging difficult.

## Recommended convergence steps
- **Wire the dashboard to QRL data**: have the page call `/api/qrl/summary` (or a narrowed DTO) on load, and add WS endpoints for price/depth streams so the UI reflects live data without reloads.
- **Normalize application outputs**: adjust QRL use cases to return domain VOs/DTOs (e.g., `QrlPrice`-backed response models) and centralize serialization so interfaces stay thin.
- **Introduce realtime pipeline**: connect `QrlWsClient` → mapper → event bus with `BoundedAsyncQueue`/`RingBuffer`, then expose the processed stream to interfaces (align with `1.md` flow).
- **Stabilize infra calls**: reuse shared clients/settings, add lightweight caching for price/depth/kline, and define retry/rate-limit handling for MEXC endpoints.
- **Add fast tests first**: start with unit tests for `QrlPrice`, `QrlQuantity`, guards, and basic QRL use cases; stub REST/WS clients to keep tests offline and reproducible.

Assumptions: env vars/credentials are provided via `MexcSettings`; no behavioral changes were made in this report. Tests were not run (documentation-only change).
