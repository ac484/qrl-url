---
post_title: "Allocation chain analysis and micro-order design"
author1: "copilot"
post_slug: "allocation-chain-optimization"
microsoft_alias: "copilot"
featured_image: ""
categories: ["architecture"]
tags: ["allocation", "order-sizing", "execution"]
ai_note: "yes"
summary: "Breakdown of /tasks/allocation today and a design to minimize atomic order value while keeping orders short-lived."
post_date: "2026-01-12"
---

## Current /tasks/allocation flow
- Entry: `/tasks/allocation` (HTTP/Scheduler) → `run_allocation` → `AllocationUseCase`.
- Timeout: default 20s from `TASK_TIMEOUT_SECONDS`.
- Inputs:
  - Account balances (free + locked).
  - Mid price = (bid + ask) / 2 from `get_price`.
- Decision:
  - Normalize balances into USDT terms via `ValuationService`.
  - `BalanceComparisonRule` with tolerance 0.01 USDT: skip if |qrl_usdt - usdt| ≤ tolerance; else pick side (SELL if QRL heavier, BUY otherwise).
- Market check:
  - Fetch depth (limit 20).
  - `DepthCalculator` computes executable size/weighted price for target quantity = 1.
  - `SlippageAnalyzer` rejects if fill < target or slippage > 5% (desired price = top-of-book for chosen side).
- Order build:
  - Maker-style limit price from best bid/ask with 0.1% buffer to avoid crossing.
  - `OrderCommand` always uses `Quantity(1)`, `TimeInForce("GTC")`, symbol QRLUSDT, price as above.
  - Place LIMIT order; response returned as `AllocationResult` (status/action/order_id/slippage/fill/reason).

## How quantity and pricing are derived
- Quantity: constant `TARGET_QUANTITY = Quantity(Decimal("1"))`, independent of imbalance size, min notional, or tick/lot size.
- Price: maker limit inside spread using best bid/ask ± 0.1% buffer; skips if spread inverted/zero.
- Time in force: always GTC, so an order can rest indefinitely until filled/cancelled.
- Depth guard: rejects when book cannot fill 1 unit within 5% slippage; otherwise submits a single order.

## Gaps for stealth and latency
- Single fixed size (1 unit) may exceed the true minimum tradable notional and is recognizable by other bots.
- GTC + maker buffer can leave the order resting; there is no TTL or auto-cancel loop.
- No randomization or slicing; repeat executions reuse the same visible shape.
- Does not consult symbol metadata (min notional/step size), so “smallest safe” sizing is not enforced.

## Optimization proposal — minimal, short-lived slices
### 1) Atomic size policy
- Source min_notional and lot/step size from exchange metadata (or config). If either is missing or best_price ≤ 0, skip placing an order. Otherwise derive a stepped quantity:
  - raw_qty = min_notional / best_price
  - stepped_qty = ceil(raw_qty / step) * step
  - min_qty = max(step, stepped_qty)
  - step defaults to the smallest allowed lot increment (e.g., 0.0001 QRL) when metadata is absent.
- Compute imbalance_notional = |qrl_value - usdt_value|; target slice = clamp(imbalance_notional * slice_pct, min_qty, max_slice_notional / best_price) after the same guard.
- Apply random jitter (e.g., 0.9–1.2) and quantize to lot step to avoid a repeatable footprint.

### 2) Execution to avoid resting
- Prefer `IOC` for micro taker sweeps when imbalance is small; set limit at best ask (BUY) / best bid (SELL) ± a defined epsilon. Use `max(one_tick, 0.01% of spread, absolute_minimum_epsilon)` where:
  - one_tick = symbol tick size from metadata (fallback 0.0001 if unknown)
  - absolute_minimum_epsilon = hard floor like 1e-6 to avoid zero when spreads collapse
- If maker placement is required, keep `GTC` but attach a short TTL (e.g., 5–15s) and auto-cancel/resubmit with fresh depth instead of letting it rest.
- Cap attempts per run (e.g., 2–3 slices) and stop if depth thins or slippage > threshold.

### 3) Scheduling and safeguards
- Recompute depth before every slice; skip when executable notional < min_notional to avoid advertising unusable orders.
- Track cumulative notional filled this run; exit when target imbalance is reduced or attempts are exhausted.
- Log emitted slices (size, tif, ttl, slippage) for monitoring and future tuning.

### Implementation sketch
- New config knobs: `MIN_NOTIONAL_USDT`, `LOT_STEP`, `MAX_SLICE_NOTIONAL`, `SIZE_JITTER_PCT`, `ORDER_TTL_SECONDS`, `EXECUTION_MODE` enum (e.g., `IMMEDIATE_OR_CANCEL` vs `SHORT_LIVED_MAKER`) for type safety.
- Add helper `compute_slice_quantity(mid_price, imbalance)` to replace the fixed `TARGET_QUANTITY`.
- Switch time in force to IOC for taker-style slices; for maker flow, schedule cancel after TTL (or use a post-only + cancel timer if supported).
- Keep existing slippage/depth checks but evaluate them per-slice; stop early on repeated rejection to avoid signaling.
