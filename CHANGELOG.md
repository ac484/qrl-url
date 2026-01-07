# Changelog

## [Unreleased]

### Added
- POST `/tasks/allocation` endpoint for Cloud Scheduler triggers.
- `/api/tasks/allocation` alias for Cloud Scheduler triggers to match the API namespace.
- Allocation use case now checks QRL vs USDT balances and places a limit order using live top-of-book pricing sized to ~1 USDT notional.

### Changed
- Allocation uses live top-of-book pricing (best bid/ask rounded to tick size) and sizes orders to ~1 USDT notional with safe rounding and last-price fallback.

### Testing
- Added `tests/test_allocation_use_case.py` to cover allocation use case behavior.
