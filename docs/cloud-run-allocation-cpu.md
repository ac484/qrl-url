---
post_title: "Cloud Run allocation CPU investigation"
author1: "ac484"
post_slug: "cloud-run-allocation-cpu"
microsoft_alias: "ac484"
featured_image: ""
categories:
  - "runbook"
tags:
  - "cloud-run"
  - "cloud-scheduler"
  - "performance"
  - "mexc"
ai_note: "Generated with AI assistance"
summary: "Why CPU spiked during Cloud Scheduler triggers and how the new single-flight guard and logging reduce overlap."
post_date: 2026-01-08
---

## What caused the CPU spike
- Cloud Scheduler retries/manual runs were overlapping on the same Cloud Run instance.
- Each `/tasks/allocation` call spins up a fresh signed AsyncClient and executes three network calls (account, ticker, depth). Overlap multiplies TLS handshakes and HMAC signing, which shows as CPU spikes even when no orders are placed.
- There was no per-instance guard, so concurrent attempts queued instead of fast-failing.

## Mitigations shipped
- Added a single-flight lock in `interfaces/tasks/entrypoints.py`. When a run is already in progress, the handler returns `429 Allocation is already running` instead of stacking work.
- The lock is controllable via `ALLOW_PARALLEL_ALLOCATION` (default `0`). Enable only if intentional concurrency is required.
- Task logging now emits `allocation.request.complete` with `elapsed_ms`, `status`, `job_name`, `retry_count`, and `execution_time` to make overlap easy to spot.

## Operational tuning
- Keep Cloud Run concurrency at **1–2** for this service and prefer CPU throttling on idle to avoid background burn.
- Align Cloud Scheduler settings with `TASK_TIMEOUT_SECONDS` (default 20s): use `minBackoff ≥ 10s` and `maxRetryAttempts ≤ 3`.
- If 429s appear repeatedly in logs, lower the schedule frequency or revisit retry/backoff to avoid overlap.

## How to verify
1. Trigger the scheduler job once and confirm a single `allocation.request.complete` log with the expected job metadata.
2. Trigger overlapping runs (or increase retry count) and confirm the second call returns HTTP 429 quickly.
3. Watch Cloud Run CPU charts; after the guard, spikes should correlate only with genuine task work rather than stacked retries.
