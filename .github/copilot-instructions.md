name: MEXC Trading Bot
stack: Python 3.11+, FastAPI, httpx, websockets, Redis, MEXC V3 API, orjson, Pydantic 2.5
deployment: Cloud Run + Scheduler + Jobs
testing: pytest + pytest-asyncio

role: Senior Python backend; trading + cloud; follow repo rules

copilot_context:
  - Repo instructions > ad-hoc
  - Task-specific: .github/prompts/*.prompt.md
  - Path-scoped: .github/instructions/*.instructions.md

max_file_length: 4000
split_large_files: true

architecture:
  - DDD 4-layer: Interface → Application → Domain → Infrastructure
  - Repository pattern; no god objects; DI via Depends()
  - Modules by business capability; stable public interfaces
  - Breaking changes allowed internally

layers:
  interface:
    must: validate input (Pydantic), convert to VO, call Use Cases, convert results to DTOs, handle HTTP only
    must_not: business logic, infra calls
  application:
    must: orchestrate domain + infra, context mgmt, structured results
    must_not: business logic, accept DTOs, return primitives
  domain:
    must: all business rules in VOs/Entities/Aggregates, immutable, pure Python
    must_not: call infra/app, use primitives, external deps
  infrastructure:
    must: implement repos, async context, API client, Redis caching
    must_not: business logic, call domain/app

async_context:
  pattern: Use Case manages async with client; controller never wraps
  enforcement: new code follows pattern; delete old files immediately

mexc_redis:
  - REST: retry/backoff; WS auto reconnect
  - HMAC-SHA256 signing; keys from env
  - Redis: cache (TTL 1–60s), order state, locks

cloud:
  - Cloud Run: multi-stage Docker, port 8080, /health, resource limits
  - Scheduler/Jobs: POST to Cloud Run, auth via service account

workflow:
  - Create Use Case → delete old files → update controllers → verify imports → test
  - Fix bugs → trace execution → fix actual code → verify
  - Refactor → incremental → consistent → delete old code

do_dont:
  do: repo pattern, async I/O, validation, Redis cache, structured logs, delete old files
  dont: infra in routes, business in routes/repos, sync I/O, sleep(), commit secrets, leave old+new

errors_logging:
  - Result pattern (Ok/Err), custom exceptions, structured JSON logs

testing:
  - Unit: domain (mock deps)
  - Integration: API (TestClient)
  - ≥80% coverage
  - Use httpx.MockTransport

boundary_conversion:
  - Infra primitives → Use Case converts to VO/Entity → Interface converts to DTO
  - Never return dicts or accept primitives in Use Cases

style:
  black: line-length 100, py311
  ruff: line-length 100, select E,F,I,N,W,UP,B,A,C4,DTZ,T10,ISC,ICN,PIE,PT,Q,SIM,ARG,ERA,PD,PL,NPY,RUF
  pytest: asyncio_mode auto, testpaths ["tests"]
