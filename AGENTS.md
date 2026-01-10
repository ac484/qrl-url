# AGENTS.md

## Purpose

This document defines **strict architectural boundaries** for this project.
All human contributors and AI agents (including Copilot) **must follow these rules**.
Violations are considered architectural defects, not implementation details.

The architecture follows **strict Domain-Driven Design (DDD)** with a
**dependency direction from inner layers to outer layers only**.

---

## Layer Order (Inner → Outer)

1. domain
2. application
3. interfaces
4. infrastructure

Dependencies are **one-directional only**.
Outer layers may depend on inner layers.
Inner layers must never depend on outer layers.

---

## 1️⃣ Domain Layer (`src/app/domain`)

### Responsibility
- Define business language, rules, and invariants
- Answer: **“What is allowed?”**

### Contains
- Aggregates
- Entities
- Value Objects
- Domain Services (pure, cross-aggregate rules only)
- Domain Events
- Factories

### Must NOT
- Import application / interfaces / infrastructure
- Contain IO, persistence, HTTP, SDKs, schedulers, or external APIs
- Know about use cases, workflows, or controllers
- Reference ORM models or database concepts

### Notes
- Domain is pure and deterministic
- All state changes must go through Aggregate Roots

---

## 2️⃣ Application Layer (`src/app/application`)

### Responsibility
- Orchestrate domain objects to complete a use case
- Answer: **“What workflow happens?”**

### Contains
- Use Cases (Application Services)
- Commands (write intentions)
- Queries (read intentions)
- DTOs (data crossing layer boundaries)
- Ports (repository / gateway abstractions)

### Must NOT
- Implement business rules (those belong to domain)
- Depend on infrastructure
- Perform technical IO (DB, HTTP, SDK calls)

### Notes
- Application coordinates, domain decides
- Ports define *what is needed*, not *how it is implemented*

---

## 3️⃣ Interfaces Layer (`src/app/interfaces`)

### Responsibility
- Translate external input/output into application use cases
- Answer: **“How does the outside world talk to us?”**

### Contains
- HTTP controllers / routers
- WebSocket handlers
- CLI commands
- Schedulers / entry adapters
- Request → Command mapping
- Result → Response mapping

### Must NOT
- Contain business logic or rules
- Directly manipulate domain objects
- Access infrastructure implementations directly

### Notes
- Interfaces call application use cases only
- Thin layer, mapping-focused

---

## 4️⃣ Infrastructure Layer (`src/app/infrastructure`)

### Responsibility
- Implement technical details
- Answer: **“How is it actually done?”**

### Contains
- Repository implementations
- Database / cache access
- External service adapters
- SDK / ORM / Driver usage
- Message queues / schedulers

### Must NOT
- Define business rules
- Define use case flow
- Change domain behavior

### Notes
- Implements application ports
- Replaceable without affecting domain or use cases

---

## Global Rules (Strict)

- Domain must be fully testable without infrastructure
- No layer may “skip” another layer
- Controllers never contain business decisions
- Repositories never enforce business rules
- DTOs never leak into domain
- Domain objects are never ORM entities

---

## Enforcement

If a piece of code does not clearly belong to one layer,
**it is in the wrong place**.

When in doubt:
- Business rule → Domain
- Workflow / orchestration → Application
- Input/output mapping → Interfaces
- Technical detail → Infrastructure
