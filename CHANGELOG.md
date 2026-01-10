# Changelog

## [Unreleased]

### Added
- POST `/tasks/allocation` endpoint for Cloud Scheduler triggers.
- `/api/tasks/allocation` alias for Cloud Scheduler triggers to match the API namespace.
- Allocation flow now compares free + locked balances using a 50/50 target ratio with tolerance, derives notional trade size dynamically, and applies slippage/depth checks before submitting maker limit orders (client-order-id = request id).
- Added optional notional guards, limit-price cap, and consideration of locked balances in allocation decisions.
- Added exchange safety filters: quantities are rounded to lot size step and prices to tick size to avoid order rejections.

### Testing
- Added unit coverage for ratio-based balance comparison, locked-balance handling, and updated allocation use case scenarios.
