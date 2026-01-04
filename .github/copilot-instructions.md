name: MEXC Trading Bot
description: Mandatory instructions for Copilot
max_file_length: 4000
stack: Python 3.11+, FastAPI 0.109, Uvicorn 0.27, httpx 0.26 (async), websockets 12 (async), Redis Cloud 5.0.1 (async), MEXC V3 API (REST+WS), cryptography 41 (HMAC), orjson 3.9, Pydantic 2.5
deployment: Cloud Run + Scheduler + Jobs
testing: pytest 7.4 + pytest-asyncio 0.21
role: Senior Python backend engineer; trading + cloud systems. Work only within repo rules.

copilot_context:
- Repo-wide instructions live in this file; prefer it over ad-hoc guidance.
- Reuse task-specific flows via .github/prompts/*.prompt.md.
- Path-scoped rules belong in .github/instructions/*.instructions.md. Legacy .github/.copilot assets should stay removed.

---

⚠ All generated files must be ≤ 4000 characters. If exceeded, automatically split into multiple files or raise an error.

---

architecture:

- STRICT 4-LAYER DDD: Interface → Application → Domain → Infrastructure (see .github/Boundary.md)
- Repository pattern: all external I/O via repos
- No god objects; single responsibility
- DI via Depends()
- Result pattern for async ops that may fail
- Modules by business capability; communicate via public interfaces
- Breaking changes allowed; public interfaces must be stable

ddd_layer_enforcement:

CRITICAL: These rules are MANDATORY and violations must be caught IMMEDIATELY.

Interface Layer (interfaces/http/, interfaces/tasks/, interfaces/templates/):
  MUST:
    - Receive HTTP/WS/CLI requests and validate input with Pydantic DTOs
    - Convert Pydantic DTOs to domain VOs before calling Application layer
    - Call Application Use Cases (never call Infrastructure directly)
    - Convert Use Case results back to Pydantic DTOs for HTTP responses
    - Handle HTTP concerns ONLY (status codes, headers, errors)
  MUST NOT:
    - Calculate business values (prices, percentages, quantities, risk)
    - Make business decisions (buy/sell, when to trade, order parameters)
    - Call Infrastructure layer directly (MEXC client, Redis, Database)
    - Contain domain logic or business rules
    - Use async context managers for Infrastructure (Use Case responsibility)
  
Application Layer (application/trading/, application/account/, application/market/):
  MUST:
    - Create Use Case classes that orchestrate domain objects and infrastructure
    - Accept domain VOs as input (never primitives or Pydantic DTOs)
    - Enter async context managers INTERNALLY before ANY infrastructure calls
    - Convert infrastructure primitives to domain VOs/Entities at boundary
    - Return structured result types (dataclasses, not Dict[str, Any])
    - Handle infrastructure errors and convert to domain-appropriate responses
  MUST NOT:
    - Implement business rules (delegate to Domain layer)
    - Accept Pydantic DTOs directly (Interface converts to VOs first)
    - Return primitives or untyped dicts (use structured results)
    - Leave async context management to controllers

Domain Layer (domain/value_objects/, domain/entities/, domain/aggregates/):
  MUST:
    - Define all business concepts as VOs, Entities, or Aggregates
    - Implement ALL business rules and validations
    - Be pure Python with zero external dependencies
    - Use immutable VOs with validation in __post_init__
    - Provide factory methods (from_float, from_string) for construction
  MUST NOT:
    - Call Infrastructure or Application layers
    - Use primitives for business concepts (use VOs)
    - Depend on FastAPI, httpx, Redis, or any external library

Infrastructure Layer (infrastructure/external/, infrastructure/persistence/):
  MUST:
    - Implement repository interfaces defined by Domain
    - Return primitives at boundaries (Application converts to VOs)
    - Handle async context management when called by Application
    - Implement MEXC API client with proper authentication
    - Provide Redis caching with proper TTLs
  MUST NOT:
    - Contain business logic or rules
    - Call Domain or Application layers
    - Make decisions about business values

domain_rules:

- Business rules ONLY in domain services, VOs, Entities, Aggregates
- API routes: NO business decisions, calculations, or Infrastructure calls
- Application Use Cases: orchestrate domain + infrastructure, handle context
- Interface controllers: thin adapters (HTTP ↔ DTO ↔ VO ↔ Use Case)
- Domain correctness > API convenience > performance

python_fastapi:

- Type hints mandatory
- async def for I/O; Annotated + Depends()
- Pydantic for validation; no Any except untyped libs
- Pattern matching for complex logic
- PEP8 via black/ruff
- Use asyncio.TaskGroup, contextlib.asynccontextmanager
- Catch specific exceptions only
- APIRouter for routes; BackgroundTasks for fire-and-forget
- Lifespan events for startup/shutdown
- Proper HTTP codes; HTTPException with detail

async_context_management:

CRITICAL: Async context management is a common source of 500 errors. Follow these rules STRICTLY.

CORRECT Pattern - Use Case Manages Context:
  Use Case:
    - Use Case enters `async with self._mexc_client:` INTERNALLY before ANY API calls
    - Use Case is responsible for context lifecycle
    - Use Case handles all infrastructure errors within context
  Controller:
    - Controller creates mexc_client instance via _get_mexc_client()
    - Controller passes client to Use Case constructor
    - Controller calls use_case.execute() WITHOUT async with wrapper
    - Controller converts result to HTTP response

INCORRECT Patterns (Will cause 500 errors):
  ❌ Controller enters context, Use Case also enters context (double-entry)
  ❌ Controller enters context, Use Case doesn't enter (inconsistent)
  ❌ Application function uses `async with` internally, controller doesn't enter
  ❌ Use Case doesn't enter context, calls API methods directly

ENFORCEMENT:
  - When creating NEW Use Cases: ALWAYS include async with self._mexc_client
  - When creating NEW controllers: NEVER include async with when calling Use Cases
  - When REPLACING old code: DELETE old files immediately, don't leave both versions
  - When fixing context bugs: Check ALL similar code, ensure consistent pattern

mexc_redis:

- All API calls via infrastructure/mexc/
- REST: retry + exponential backoff; WS: auto reconnect
- Signatures via HMAC-SHA256 (signer.py)
- Keys from env via Pydantic-settings
- Rate limit: 20 req/sec REST
- Redis for: market cache (TTL 1–60s), order state, distributed locks, WS state
- Redis async; keys: mexc:{entity}:{id}
- Validate all API responses via Pydantic
- MEXC client REQUIRES async context manager for proper session management

cloud_deployment:

- Cloud Run: multi-stage Docker, port 8080, /health, resource limits
- Scheduler: POST to Cloud Run, service account auth, retry policies
- Jobs: batch ops, idempotent, log executions
- Env vars (Secret Manager): MEXC_API_KEY, MEXC_API_SECRET, REDIS_URL, REDIS_PASSWORD, ENV=production, LOG_LEVEL=INFO

code_modification_workflow:

CRITICAL: Follow this workflow EXACTLY when modifying code to prevent accumulation of broken files.

When CREATING new Use Cases or Application Services:
  1. Write new Use Case with proper DDD layering and async context management
  2. IMMEDIATELY identify and DELETE old files being replaced
  3. Update ALL controller imports to use new Use Case (use grep to find)
  4. Verify no old imports remain: `grep -r "old_function_name" src/`
  5. Test endpoint or get user confirmation before claiming "fixed"

When FIXING bugs in existing code:
  1. Identify which code is ACTUALLY running (check imports, trace execution)
  2. Read the ACTUAL code files, don't assume based on documentation
  3. Fix the code that's actually executing, not a different version
  4. Verify fix by checking imports and testing endpoint
  5. NEVER claim "fixed" without verification

When REFACTORING:
  1. Make changes incrementally with one clear pattern
  2. Apply pattern consistently across ALL similar code
  3. Delete old code after confirming new code works
  4. Use grep to ensure old patterns are eliminated: `grep -r "old_pattern" src/`

PREVENTION CHECKLIST:
  ❌ NEVER leave both old and new versions of same functionality
  ❌ NEVER claim "fixed" without checking imports and execution paths
  ❌ NEVER ignore user's error logs showing persistent issues
  ❌ NEVER assume new code is running just because it exists
  ✅ ALWAYS delete old files when creating replacements
  ✅ ALWAYS use grep to verify old imports are removed
  ✅ ALWAYS trace actual execution paths before claiming fixes
  ✅ ALWAYS test endpoints or wait for user confirmation

do_dont:
do: repo pattern, input validation, async I/O, circuit breakers, structured logging, Redis caching, graceful WS shutdown, DELETE old files when creating replacements, verify execution paths with grep
dont: direct Redis/MEXC in routes, encode business rules in routes/repos, sync I/O in async, time.sleep(), commit secrets, circular deps, mutable defaults, leave old+new versions of same code, claim "fixed" without verification

errors_logging:

- Result pattern for failures
- Custom exceptions in core/exceptions.py
- Log context: request_id, user_id, symbol, order_id
- Structured JSON logs; critical errors trigger alerts
- Example Result pattern with Ok/Err dataclasses

testing:

- Unit: domain (mock deps)
- Integration: API (TestClient)
- pytest-asyncio, mock Redis + MEXC
- Fixtures in tests/conftest.py
- ≥80% domain coverage
- httpx.MockTransport for HTTP mocking

performance_cost:

- Aggressive Redis caching
- Batch API calls
- WS for real-time data
- Proper TTL, connection pooling, request coalescing
- Monitor Cloud Run instances, set max

boundary_conversion:

MANDATORY: All infrastructure responses MUST be converted to domain types at Use Case boundary.

Pattern (from MIGRATION_GUIDE.md / Boundary.md):
  Infrastructure returns primitives → Application Use Case converts to VOs/Entities → Interface converts to Pydantic DTOs

Examples:
  - MEXC API order dict → Use Case converts to Order entity → Controller converts to OrderResponse DTO
  - MEXC API trade dict → Use Case converts to Trade entity → Controller converts to TradeResponse DTO
  - MEXC API kline array → Use Case converts to KlineCandle VO → Controller converts to KlineResponse DTO

Conversion Rules:
  - Use factory methods: KlineCandle.from_mexc_array(), Price.from_float()
  - Handle parsing errors gracefully with try/except
  - Log warnings for individual item failures, continue processing rest
  - NEVER return Dict[str, Any] from Use Cases (use structured types)
  - NEVER accept primitives in Use Case execute() (require VOs)

output_expectations:

- Prefer architectural explanation before code
- State assumptions/trade-offs
- Ask before non-trivial architectural changes
- No large code blocks unless requested
- Provide deployment commands
- If any generated file would exceed 4000 chars, automatically split or fail
- When replacing old code: explain what's being deleted and why
- When fixing bugs: trace execution path and show which code actually runs
- NEVER claim "fixed" without explaining verification approach

style_enforcement:
black:
line-length: 100
target-version: [py311]
ruff:
line-length: 100
select: ["E","F","I","N","W","UP","B","A","C4","DTZ","T10","ISC","ICN","PIE","PT","Q","SIM","ARG","ERA","PD","PL","NPY","RUF"]
pytest:
asyncio_mode: auto
testpaths: ["tests"]
