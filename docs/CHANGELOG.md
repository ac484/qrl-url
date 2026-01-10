# Changelog

## [Unreleased]

### Added
- POST `/tasks/allocation` endpoint for Cloud Scheduler triggers.
- `/api/tasks/allocation` alias for Cloud Scheduler triggers to match the API namespace.
- Allocation use case now checks QRL vs USDT balances and submits a 1-unit limit order at price 1 based on the higher side.

### Testing
- Added `tests/test_allocation_use_case.py` to cover allocation use case behavior.
