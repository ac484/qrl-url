Purpose: Root guidance for src/app layering (Interface → Application → Domain; Infrastructure isolated).

Layer boundaries (allowed imports):
- interfaces/: may import application
- application/: may import domain (VO/mapping) only
- domain/: pure Python/stdlib only
- infrastructure/: may import external libs and domain types, but not interfaces/application

Reference: .github/Boundary.md for enforcement details.
