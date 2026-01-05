## Boundary Map (QRL/USDT skeleton)

- interfaces/ → can import application; no domain/infrastructure/SDK.
- application/ → can import domain; no interfaces/infrastructure/SDK.
- domain/ → pure Python only; no upward references.
- infrastructure/ → can import external libs and domain types; no interfaces/application.

See `.github/Boundary.md` for full rules.
