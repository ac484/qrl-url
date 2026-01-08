---
post_title: "Allocation task refactor plan"
author1: "copilot"
post_slug: "allocation-task-refactor-plan"
microsoft_alias: "copilot"
featured_image: ""
categories: ["architecture"]
tags: ["allocation", "mexc", "ddd"]
ai_note: "yes"
summary: "Plan to refactor /tasks/allocation with balance comparison VO pipeline and pre-order depth/slippage checks before sending orders."
post_date: "2026-01-07"
---

## Scope and goals
- Align `/tasks/allocation → 比例分析 → 下訂單` with single-responsibility stages and domain value objects.
- Add pre-order market-depth and slippage analysis before placing the fixed 1-unit, price-1, GTC order.
- Keep DDD layering intact: Interface → Application → Domain → Infrastructure.

## Current baseline
- Route: `interfaces/http/api/tasks_routes.py` → `interfaces/tasks/entrypoints.py` → `AllocationUseCase`.
- Use case: compares QRL vs USDT free balances and always submits a 1-unit limit order at price 1.
- Services: `MexcService` (account, order), infra REST client, domain VOs for balances, side, price, quantity, order.

## Refactor stages (sequential)
1) Acquire reference balances
   - Fetch account; map to a normalized balance snapshot VO (e.g., `NormalizedBalances` with asset metadata).
2) Apply comparison rule
   - Domain service `BalanceComparisonRule` returns `BalanceComparisonResult` VO (qrl_free, usdt_free, diff, preferred_side, threshold/notes).
   - Decision branch: skip (no-change) or proceed (BUY/SELL).
3) Fetch and normalize order book
   - New infra call for depth; mapper to `OrderBook` VO (bids/asks as `DepthLevel` lists).
4) Executable depth & slippage analysis
   - Domain service computes executable depth for target quantity (1) on the chosen side, weighted expected fill, slippage_pct vs desired limit=1.
   - Result VO `SlippageAssessment` (expected_fill, slippage_pct, pass/fail, reason).
5) Order strategy and command
   - If slippage acceptable, build `OrderCommand` (still qty=1, price=1, TIF=GTC, side from comparison).
   - If not acceptable, exit with status “rejected” and reason from `SlippageAssessment`.
6) Execute and post-order
   - Application builds `PlaceOrderRequest` → `MexcService.place_order`.
   - `AllocationResult` VO captures request_id, executed_at, comparison outcome, slippage summary, action (buy/sell/skip/reject), order_id or reason.

## Domain artifacts to add
- VOs: `NormalizedBalances`, `BalanceComparisonResult`, `OrderBook`, `OrderBookSide`, `DepthLevel`, `SlippageAssessment`, `OrderCommand`.
- Services: `BalanceComparisonRule`, `DepthCalculator`, `SlippageAnalyzer`.

## Application/infrastructure updates
- Application: refactor `AllocationUseCase` to orchestrate stages, short-circuit on skip/reject, and log each stage.
- MexcService: add depth wrapper; ensure symbol normalization reused.
- Infra REST client: depth endpoint (e.g., `/api/v3/depth`), mapper to `OrderBook` VO; no business rules inside infra.
- Interface: keep routes unchanged; response schema may need optional fields for slippage/decision notes in follow-up PR.

## Testing plan
- Unit tests: comparison rule (balanced, QRL-heavy, USDT-heavy, zeros), slippage analyzer (thick/thin books, high slippage).
- Use case tests: skip path, reject-on-slippage path, execute path; stub MexcService account/depth/order responses.
- Integration smoke: ensure depth mapper handles empty/partial books safely.

## Open considerations
- Define acceptable slippage threshold (configurable?) for pass/fail decision.
- Depth levels to consider (top N vs full book); default limit parameter for depth call.
- Timeouts for depth/account calls; reuse existing `TASK_TIMEOUT_SECONDS`.
