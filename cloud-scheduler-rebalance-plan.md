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

## Guardrails (strategy & bot separation)
- Strategy math and bot decisions live only under `domain/strategies/` and `application/trading/use_cases/`; interfaces/routes must not embed thresholds, sizing, or guard logic.
- Interfaces/task entrypoints (`interfaces/tasks` and `interfaces/http/api/tasks_routes.py`) only validate input, pass VOs/DTOs to use cases, and render responses.
- Infrastructure clients (`infrastructure/exchange/mexc`) stay thin mappers/adapters; no strategy state in HTTP pages, templates, or static assets.
- Keep any staging/dry-run toggles in config or DTOs, not in controllers, to avoid mixing bot logic with presentation code.

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
1) **Strategy domain + DTOs (strategy folder only)**  
   - Add `domain/strategies/rebalance.py` to hold target weights, bands, cool-down, dry-run, and replay window.  
   - Create DTOs for inputs/outputs (`RebalanceConfig`, `RebalancePlan`, `PlannedOrder`) that wrap existing VOs (Price, Quantity, QrlUsdtPair) and never leak raw dicts.  
   - Keep simulation helpers (what-if sizing) here to stay separated from interfaces.
2) **Application use case orchestration**  
   - Add `application/trading/use_cases/rebalance_qrl.py` that owns async context for `MexcService`/gateways, fetches snapshot (balances + ticker), runs guards (rate limit, duplicate exec UUID, balance sanity), computes deltas via domain strategy, and returns a structured report.  
   - Accept an explicit `StrategyProfile` identifier and `dry_run: bool`; no controller math.  
   - Ensure no infrastructure creation in controllers; inject services via constructor/Depends.
3) **Infrastructure wiring and caching**  
   - Reuse `MexcRestClient`/`QrlRestClient` through a `MexcService` factory and a lightweight cache (ticker/account TTL ≤ 5s) owned by the use case.  
   - Map REST payloads to VOs/entities at the boundary; log correlation IDs for each call.  
   - Keep adapters in `infrastructure/exchange/mexc`; do not place strategy state there.
4) **Scheduler HTTP entrypoint (interfaces/tasks only)**  
   - Implement `interfaces/http/api/tasks_routes.py` (or `entrypoints.py`) exposing `POST /tasks/rebalance` that only validates payload and OIDC audience, then calls the use case.  
   - Expected payload (JSON): `{ "profile": "default-qrl", "dry_run": true, "request_id": "<uuid>" }`.  
   - Response DTO: `{ "request_id": "<uuid>", "plan": [...orders], "executed": [...], "dry_run": true, "started_at": "...", "ended_at": "...", "errors": [] }`.
5) **Task façades (shared between HTTP/Scheduler/Batches)**  
   - `interfaces/tasks/market_tasks.py`: fetch price/depth snapshot as a pure function returning VOs/DTOs.  
   - `interfaces/tasks/trading_tasks.py`: call the rebalance use case and return structured results; no business logic.  
   - `interfaces/tasks/entrypoints.py`: thin adapter to wire HTTP route to task façades and future Cloud Tasks/Jobs triggers.
6) **Deployment & IAM (keep out of app code)**  
   - Cloud Scheduler job: HTTPS POST to Cloud Run URL with OIDC token audience set to the service; store service account email in IaC or cloudbuild variables.  
   - Validate `Authorization` OIDC token and `X-CloudScheduler` headers; reject mismatched audience or missing replay window.  
   - Config knobs (env): `SCHEDULER_AUDIENCE`, `SCHEDULER_REPLAY_TTL_SEC`, `REBALANCE_PROFILE`, `REBALANCE_DRY_RUN_DEFAULT`, `MEXC_*`, `PORT`. Keep these documented in `.env.example` not in controllers.
7) **Testing & observability (fast, strategy-focused)**  
   - Unit tests in strategy layer for sizing, thresholds, and guard rails; include fixtures for ticker/account snapshots.  
   - Add task-level structured logging (JSON) with fields: `request_id`, `profile`, `dry_run`, `orders_planned`, `orders_sent`, `latency_ms`, `status`.  
   - Provide a dry-run mode that skips order placement but returns the computed plan; expose a staging profile to validate in CI.

## Scheduler ↔ Cloud Run wiring notes
- Use HTTPS POST from Cloud Scheduler with OIDC token targeting the Cloud Run service audience; reject unauthenticated or replayed requests.
- Keep handler idempotent: include execution UUID in responses and ignore duplicates within a window; rely on strategy thresholds to avoid churning orders.
- Support dry-run execution to emit the planned orders without placing them, enabling staging validation before production.
- Log and export metrics (success/failure, latency, orders placed) to aid SRE and finance review.

## Acceptance & risks checklist (strategy/bot scope)
- Strategy logic is confined to `domain/strategies` and `application/trading/use_cases`; interfaces/tasks remain orchestration-only.  
- Scheduler contract is documented (payload, headers, audience) and validated in controllers without embedding strategy math.  
- Dry-run and replay protection are implemented and testable without touching presentation code.  
- Observability covers per-request logs/metrics; failure paths are surfaced without exposing secrets.  
- Risks: MEXC API rate limits, Cloud Scheduler retries causing duplicate attempts, and Cloud Run cold starts increasing latency; mitigated via guards, caching, and replay window.

## Execution plan (actionable, ready to land)
- **Create strategy primitives (Dev)**  
  - File: `src/app/domain/strategies/rebalance.py` with `RebalanceConfig`, `RebalancePlan`, `PlannedOrder`, `DecisionContext`, and what-if sizing helpers.  
  - Tests: add unit tests under `tests/domain/strategies/test_rebalance.py` covering target band hits, cool-down, dry-run, and replay window.
- **Add rebalance use case (Dev)**  
  - File: `src/app/application/trading/use_cases/rebalance_qrl.py` orchestrating snapshot fetch → guards → plan → (optional) order placement.  
  - Ensure async context enters `MexcService` internally; no controller context managers.  
  - Tests: `tests/application/trading/test_rebalance_qrl.py` with mocked MexcService, verifying dry-run returns plan only.
- **Wire task façades and route (Dev)**  
  - Files: `src/app/interfaces/tasks/market_tasks.py`, `trading_tasks.py`, `entrypoints.py`; new route `src/app/interfaces/http/api/tasks_routes.py` exposing `POST /tasks/rebalance`.  
  - Validate OIDC audience (`SCHEDULER_AUDIENCE`), `X-CloudScheduler` headers, and payload schema `{profile, dry_run, request_id}`; return DTO report.  
  - Tests: `tests/interfaces/tasks/test_trading_tasks.py` (payload → DTO), `tests/interfaces/http/test_tasks_routes.py` (401 on bad audience, 200 on valid payload).
- **Config and envs (DevOps)**  
  - Update `.env.example` with `SCHEDULER_AUDIENCE`, `SCHEDULER_REPLAY_TTL_SEC`, `REBALANCE_PROFILE`, `REBALANCE_DRY_RUN_DEFAULT`, `MEXC_*`.  
  - Add dry-run default and replay TTL into config loader; keep out of controllers.
- **Scheduler job (DevOps)**  
  - Cloud Scheduler job creation (example):  
    ```
    gcloud scheduler jobs create http rebalance-qrl \
      --schedule="*/5 * * * *" \
      --uri="https://<cloud-run-url>/tasks/rebalance" \
      --oidc-service-account-email=<scheduler-sa>@<proj>.iam.gserviceaccount.com \
      --oidc-token-audience="<cloud-run-audience>" \
      --http-method=POST \
      --headers="Content-Type=application/json" \
      --message-body='{"profile":"default-qrl","dry_run":true}'
    ```
  - Ensure Cloud Run IAM allows the scheduler SA `run.invoker`.
- **Observability (Dev)**  
  - Structured JSON logs with fields: `request_id`, `profile`, `dry_run`, `orders_planned`, `orders_sent`, `latency_ms`, `status`, `error`.  
  - Metrics hooks: count successes/failures and latency histogram around the use case entry.  
  - Add execution UUID to responses and logs for replay detection.
