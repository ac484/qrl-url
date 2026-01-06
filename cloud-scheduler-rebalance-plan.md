---
post_title: "Cloud Scheduler Rebalance Integration Plan"
author1: "ac484"
post_slug: "cloud-scheduler-rebalance-plan"
microsoft_alias: "ac484"
featured_image: ""
categories:
  - "architecture"
tags:
  - "cloud-run"
  - "cloud-scheduler"
  - "mexc"
  - "rebalancing"
  - "ddd"
ai_note: "Generated with AI assistance"
summary: "Gap assessment and implementation steps to let Cloud Scheduler trigger QRL/USDT rebalancing on Cloud Run using MEXC Spot API v3."
post_date: 2026-01-06
---

## Purpose
Identify the missing pieces to let Cloud Scheduler call this Cloud Run service to execute a QRL/USDT rebalancing strategy, confirm MEXC Spot API v3 coverage via Context7, and propose a concrete implementation path that preserves single-responsibility/DDD boundaries.

## Current structure (focused tree)
```
src/app
├─ interfaces/
│  ├─ http/api (qrl_routes.py, trading_routes.py, market_routes.py, system_routes.py, ws_routes.py)
│  ├─ http/pages (dashboard_routes.py, static/ assets, templates/)
│  └─ tasks (entrypoints.py TODO, market_tasks.py, trading_tasks.py, system_tasks.py)
├─ application/
│  ├─ trading/use_cases (place_order.py, cancel_order.py, get_price.py, list_orders.py, list_trades.py)
│  ├─ trading/qrl (place_qrl_order.py, cancel_qrl_order.py, guards/)
│  ├─ market/use_cases (get_kline.py, get_price.py, get_ticker.py, etc.)
│  ├─ ports (exchange_gateway.py)
│  └─ system/use_cases (health checks)
├─ domain/
│  ├─ value_objects (qrl_price.py, qrl_quantity.py, qrl_usdt_pair.py, symbol.py, price.py, quantity.py, etc.)
│  ├─ entities (order.py, trade.py, account.py)
│  └─ events (market_depth_event.py, trade_event.py, order_event.py, balance_event.py)
└─ infrastructure/
   ├─ exchange/mexc (rest_client.py, ws_client.py, mappers.py, adapters/, generated/ proto, qrl/ wrappers)
   ├─ streaming (bounded_queue.py, ring_buffer.py)
   └─ event_bus (in_memory_event_bus.py)
```

## Context7 MEXC Spot API v3 readiness
- Library resolved via Context7: `/suenot/mexc-docs-markdown` (High reputation, 261 snippets). It documents Spot REST/WS endpoints required for rebalancing.
- Relevant REST: `GET /api/v3/account` (balances), `GET /api/v3/ticker/price` and `GET /api/v3/ticker/24hr` (prices), `POST /api/v3/order` (create), `DELETE /api/v3/order` (cancel), `GET /api/v3/openOrders` and `GET /api/v3/myTrades` (state/filled trades).
- Relevant WS: public depth/trade streams for live price/volume. These cover all data and trade actions needed for periodic rebalancing.

## Gaps blocking Cloud Scheduler–driven rebalancing
- No scheduler-facing HTTP entrypoint: `interfaces/tasks/entrypoints.py` is a TODO, and FastAPI routes do not expose a `/tasks/rebalance` (or similar) endpoint for Cloud Scheduler POST calls with OIDC auth.
- Task handlers are placeholders: `market_tasks.py`, `trading_tasks.py`, and `system_tasks.py` return `None` and are not wired to application use cases or domain strategies.
- Missing rebalance strategy orchestration: there is no domain service that computes target weights/position deltas, nor an application use case that sequences data fetch → sizing → order placement/cancel with guards/idempotency.
- Limited dependency wiring: use cases frequently create clients directly; there is no scheduler-safe composition (e.g., injecting `MexcService`, `ExchangeGateway`, event bus, caches) to keep single responsibility and enable testing.
- Scheduler/auth/config gaps: Cloud Run deployment (cloudbuild.yaml) omits scheduler auth bindings, expected headers (X-CloudScheduler-*) validation, and replay protection; .env example has strategy knobs but no scheduler payload schema or OIDC audience value.
- Observability and tests: no fast tests for guards/sizing, no task-level logging/metrics to trace scheduler executions, and no dry-run mode to avoid unintended live trades.

## Implementation steps (ordered, keep DDD boundaries)
1) **Define strategy domain + DTOs**: add a `domain/strategies/rebalance.py` (target weights, thresholds, cool-down) plus DTOs for computed orders; ensure VOs (Price, Quantity, QrlUsdtPair) are reused.
2) **Application use case**: create `application/trading/use_cases/rebalance_qrl.py` that accepts strategy config + market snapshot, runs guards (rate limit, duplicate, balance), and returns structured plan/results (no raw dicts).
3) **Infrastructure wiring**: reuse `MexcRestClient`/`QrlRestClient` inside a `MexcService` factory, add lightweight caching for ticker/account, and ensure async context is owned by the use case (per repo rules).
4) **Scheduler HTTP entrypoint**: add `interfaces/http/api/tasks_routes.py` (or extend `entrypoints.py`) with `POST /tasks/rebalance` protected by Cloud Scheduler OIDC audience, parsing a small payload (strategy profile ID or default); this route should call the use case and return a normalized report.
5) **Task façade**: implement `interfaces/tasks/market_tasks.py` (load price/depth), `trading_tasks.py` (invoke rebalance), and use `entrypoints.py` to share logic between HTTP route and any future Cloud Tasks/Jobs triggers.
6) **Deployment & IAM**: update `cloudbuild.yaml` notes/scripts to create a Cloud Scheduler job pointing to the Cloud Run URL with a service account; document required env vars (`PORT`, `MEXC_*`, scheduler audience) and recommend `X-CloudScheduler` replay checks.
7) **Testing & observability**: add unit tests for sizing/guards, and include structured logging around every scheduler invocation (start/end, symbol, orders placed, errors) plus optional dry-run flag.

## Scheduler ↔ Cloud Run wiring notes
- Use HTTPS POST from Cloud Scheduler with OIDC token targeting the Cloud Run service audience; reject unauthenticated or replayed requests.
- Keep handler idempotent: include execution UUID in responses and ignore duplicates within a window; rely on strategy thresholds to avoid churning orders.
- Support dry-run execution to emit the planned orders without placing them, enabling staging validation before production.
- Log and export metrics (success/failure, latency, orders placed) to aid SRE and finance review.
