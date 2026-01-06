# Changelog

## [Unreleased]

### Added
- POST `/tasks/allocation` endpoint for Cloud Scheduler triggers.
- Allocation use case now checks QRL vs USDT balances and submits a 1-unit limit order at price 1 based on the higher side.

### Changed
- Allocation use case now returns structured skipped/error statuses instead of raising when credentials are missing or service calls fail.

### Testing
- Added `tests/test_allocation_use_case.py` to cover allocation use case behavior.
