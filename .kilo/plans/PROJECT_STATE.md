# PROJECT STATE

## Current phase
Phase 1 — Core Infra (in progress)

## Active branch
develop

## Latest commit
52459bb feat(backend): add async database and redis infrastructure with tests

## Status
- Phase 0 design docs: done
- Phase 1 scaffolding: done (committed)
  - .gitignore, README.md
  - apps/api: FastAPI skeleton (main.py, config.py, requirements.txt, rate_limit.py, audit.py, auth.py, logger.py, health.py)
  - apps/api: async database.py, redis_client.py, conftest.py, pytest.ini, requirements-dev.txt
  - apps/api/tests/: unit, integration, api — 52 tests passing locally (includes structured logging + Redis rate-limiting + Health Monitoring tests)
  - apps/web: Next.js skeleton + next-intl provider + [locale] routing + RTL/LTR support + locale messages (en/fa)
  - infrastructure/docker/docker-compose.dev.yml (Postgres + Redis)
  - .github/workflows/ci.yml
- GitHub Actions (reported success):
  - Backend job: Success
  - Frontend job: Success
  - PostgreSQL service: Success
  - Redis service: Success
  - Unit/API tests: Success
  - Integration tests: Success
- Verified infrastructure:
  - Async PostgreSQL connection (SQLAlchemy asyncpg)
  - Redis connection
  - FastAPI Lifespan startup/shutdown
  - Alembic 1.20.1 installed + validated (`alembic current`/`history` connect to PostgreSQL; no migrations created; DB unchanged)
  - CI active and green
  - Backend test suite: 57 passed, 1 skipped
  - Python 3.12 + Docker available locally; venv + deps installed; tests run locally

## Pending
- GitHub branch protection rules (main/develop)
- 2FA

## Completed (this session)
- Structured Logging implemented (`apps/api/logger.py`):
  - JSON output via `JsonFormatter` (stdlib `logging`, no extra dependencies)
  - UTC timestamps from `record.created`
  - Levels DEBUG/INFO/WARNING/ERROR/CRITICAL, configurable via `log_level` env var
  - HTTP request logging: method, path, status_code, process_time_ms
  - Request ID: UUID4 generation, incoming `X-Request-ID` validated (UUID format), regenerated if invalid
  - `X-Request-ID` echoed in response header
  - Unhandled exceptions logged safely: `exception_type` only (no traceback, no secret leakage)
  - Sensitive headers (authorization, api-key, etc.) never logged; no request body logging
  - `LoggingMiddleware` outermost middleware — captures 200, 429, and 503 responses
  - `setup_logging()` called in FastAPI lifespan startup/shutdown
  - Idempotent setup (no duplicate handlers)
  - New tests: `tests/unit/test_logger.py` — JSON output, UTC timestamp, all log levels, request ID generation/validation, response header, status+time, no sensitive leak, unhandled exception, no duplicate handler — all passing.
- Rate limiting upgraded from in-memory to Redis-backed (`apps/api/rate_limit.py`):
  - Atomic INCR + TTL via Lua script (`_LUA_INCR_WITH_TTL`): single Redis round-trip, no key without TTL under concurrency.
  - Uses existing `redis_client.get_redis()` singleton (no new client per request).
  - Structured `ratelimit:<ip>` keys; shared counter across workers; TTL-based expiry.
  - Configurable `rate_limit_max_requests`/`rate_limit_window_seconds`/`rate_limit_fail_open`.
  - Returns JSONResponse directly (no HTTPException raised) for 429 and 503, with `x-request-id` header.
  - Fail-closed default (503 when Redis down) with `rate_limit_fail_open` toggle.
  - IP extraction: direct `request.client.host` by default; `X-Forwarded-For` honored only when `rate_limit_trust_proxy=True` AND direct client is in `rate_limit_trusted_proxies` (no blind trust of spoofable headers).
  - New tests: `tests/unit/test_rate_limit.py` — counting, over-limit 429, TTL on first request, TTL not reset, atomic concurrent increment, no key without TTL, per-client keys, XFF not trusted by default, XFF trusted when configured, fail-open, fail-closed 503, 429 not converted to 500, **health endpoint bypass** — all passing (16 total).
- **Rate limiting health endpoint bypass fixed (`apps/api/rate_limit.py`) (this session):**
  - `GET /health` and `GET /ready` are exempt from rate limiting before any Redis interaction.
  - When Redis is down (fail-closed): `/health` → 200 degraded, `/ready` → 503; regular requests still → 503.
  - `POST /health` (and other methods) are NOT exempted — still rate limited.
  - LoggingMiddleware still logs all requests; `x-request-id` header present on all responses.
  - Middleware order unchanged: CORSMiddleware → LoggingMiddleware → RateLimitMiddleware → Route Handler.
  - Verified with real containers: Redis down / Postgres down / both down / both restored — all scenarios behave correctly.
  - 5 new unit tests added; full backend suite: 57 passed, 1 skipped.
- Middleware order corrected: `RateLimitMiddleware` added before `LoggingMiddleware`, so LoggingMiddleware is outermost and observes all responses including 429/503.
  - Stack: ServerErrorMiddleware → CORSMiddleware → LoggingMiddleware → RateLimitMiddleware → ExceptionMiddleware → Route Handler
- Health Monitoring implemented (`apps/api/health.py` + updated `apps/api/main.py`):
  - `GET /health` — async, returns overall status + per-dependency status (postgresql, redis)
  - `GET /ready` — readiness check; returns 200 if healthy, 503 if degraded
  - PostgreSQL check: `SELECT 1` via SQLAlchemy async engine
  - Redis check: `PING` via redis async client
  - Errors logged safely: `exception_type` only, no traceback or secret leakage
  - Uses existing `logger.py` (JsonFormatter, UTC timestamps)
  - Uses existing `database.py` and `redis_client.py` singletons (no new clients per request)
  - New unit tests: `tests/unit/test_health.py` — 8 tests (postgres healthy/unhealthy, redis healthy/unhealthy, all combinations)
  - New integration tests: `tests/integration/test_health_endpoint.py` — 4 tests (200, readiness, x-request-id on both endpoints; skipped when services unavailable)

## Completed (this session)
- **Frontend Internationalization Foundation (`apps/web/`) — next-intl provider wiring (VERIFIED):**
  - `apps/web/i18n.ts` — next-intl config: `locales = ['en', 'fa']`, `defaultLocale = 'en'`, `getRequestConfig` with server-side message loading, invalid locale → `notFound()`, `Home` namespace in messages matching `useTranslations('Home')`
  - `apps/web/messages/en.json` — `{"Home": {"title": "...", "subtitle": "..."}}`
  - `apps/web/messages/fa.json` — `{"Home": {"title": "...", "subtitle": "..."}}`
  - `apps/web/app/layout.tsx` — root layout (Server Component), exports `metadata`, renders `<html lang="en" dir="ltr"><body>{children}</body></html>` defaults
  - `apps/web/app/[locale]/layout.tsx` — client layout with `NextIntlClientProvider`, `useParams` for locale, `useEffect` sets `document.documentElement.lang`/`dir` (`rtl` for `fa`, `ltr` for `en`) after hydration
  - `apps/web/app/[locale]/page.tsx` — home page using `useTranslations('Home')`
  - `apps/web/app/page.tsx` — removed (moved under `[locale]/`)
  - `apps/web/middleware.ts` — `createMiddleware` from `next-intl/middleware`: valid locale passes, invalid locale → 404, root → redirect to `/en`
  - `apps/web/tests/unit/i18n.test.mjs` — 4 tests: locales, default, message loading, key structure
  - `apps/web/tests/unit/layout.test.mjs` — 4 tests: RTL/LTR direction, lang attribute
  - `apps/web/package.json` — added `"test": "node --test tests/unit/*.test.mjs"` script
  - `npx tsc --noEmit` — passes (0 errors)
  - `npm run lint` — passes (0 warnings/errors)
  - `npm run test` — passes (9 passed, 0 failed)
  - `npm run build` — PASSES (requires `__NEXT_PRIVATE_STANDALONE_CONFIG` env var unset; pre-existing environment issue unrelated to i18n)

## Completed (this session)
- **Frontend Health Monitoring Dashboard** (`apps/web/`) — VERIFIED:
  - `apps/web/lib/api.ts` — API service layer: `NEXT_PUBLIC_API_URL` base URL, typed `HealthResponse`/`DependencyHealth` interfaces, `ApiError` class, `fetchHealth()`/`fetchReady()` with 5s timeout, network error handling, HTTP error handling, invalid JSON handling, no hardcoded healthy responses
  - `apps/web/app/[locale]/health/page.tsx` — client component health page at `/[locale]/health`, real backend data via `fetchHealth()`/`fetchReady()`, manual refresh, loading/error states, last check/attempt timestamps, system overview + dependency cards (Backend API, PostgreSQL, Redis)
  - `apps/web/components/health/StatusCard.tsx` — reusable status card with colored indicators per status (healthy/degraded/unhealthy/unknown/checking)
  - `apps/web/messages/en.json` + `apps/web/messages/fa.json` — added `Health` namespace with all UI text (English LTR / Persian RTL)
  - `apps/web/tests/unit/api.test.mjs` — 14 tests: status mapping (healthy/degraded/unhealthy/unknown), ApiError, network/timeout classification, healthy/degraded/503 response shapes, invalid status handling
  - `npx tsc --noEmit` — passes (0 errors)
  - `npm run lint` — passes (0 warnings/errors)
  - `npm run test` — passes (23 passed, 0 failed)
  - `npm run build` — passes
  - Integration verified with live backend: both dependencies healthy → 200; Redis down → /health 200 degraded + /ready 503; PostgreSQL down → /health 200 degraded + /ready 503; backend unavailable → connection refused (frontend shows Unknown/Unable to connect)

- **Persisted Audit Logging + Alembic Initial Migration** (`apps/api/`) — VERIFIED:
  - `apps/api/models.py` — SQLAlchemy `Base` (DeclarativeBase) + `AuditLog` model: `audit_logs` table with `id` (UUID PK), `event_type` (String 255, indexed), `actor` (String 255, nullable, indexed), `timestamp` (DateTime TZ, indexed), `detail` (String 1024, nullable). No sensitive fields (no password, token, api_key, request_body).
  - `apps/api/audit.py` — `audit()` is now async, persists `AuditLog` records via existing `database.get_session()` SQLAlchemy async infrastructure. DB write failures are logged (exception_type only, no traceback) without crashing the caller. No secrets stored.
  - `apps/api/main.py` — `await audit("health_check")` / `await audit("readiness_check")` in `/health` and `/ready` endpoints.
  - `apps/api/migrations/env.py` — `target_metadata = Base.metadata` registered; imports `from models import Base`.
  - `apps/api/migrations/versions/689024602bb8_initial_audit_logs_table.py` — initial migration creates `audit_logs` table + 3 indexes; downgrade drops them.
  - `apps/api/tests/unit/test_audit.py` — 5 tests: record creation, DB persistence, write failure resilience, sensitive-data exclusion, default None values.
  - `apps/api/tests/integration/test_migration.py` — 3 tests: upgrade creates table, downgrade removes table, upgrade idempotent.
  - `npx tsc --noEmit` — passes (0 errors)
  - `npm run lint` — passes (0 warnings/errors)
  - `npm run test` — passes (23 passed, 0 failed)
  - `npm run build` — passes
  - Backend: 65 tests collected (56 unit/API + 9 integration)
  - Integration verified with live backend: health/ready return 200, audit events persisted to `audit_logs`, data survives restart

### Logger test isolation (Phase 1 final blocker — resolved)
  - Root cause: `apps/api/migrations/env.py` calls `logging.config.fileConfig(...)`, which defaults to `disable_existing_loggers=True`. During in-process integration migration tests this globally sets the already-created `crypto.api` logger's `disabled = True`. The shared pytest process then leaks that flag into `tests/unit/test_logger.py`, so records never reach the capture handler (5 failures in full-suite runs; tests passed in isolation).
  - Fix: added an autouse `isolate_crypto_logger` fixture in `apps/api/tests/unit/test_logger.py` that re-enables the logger for each test and snapshots/restores handlers, level, `propagate`, and `disabled` afterwards. Test-only change; production logging (`logger.py`, `main.py`, `migrations/env.py`) unchanged — alembic runs in a separate process in production, so this is not a production defect.
  - No assertions removed, no tests skipped/xfail'd; all original assertions remain meaningful. No duplicate handlers/records introduced.
  - Final backend result (full suite): **64 passed, 1 skipped, 0 failed** (exit code 0). Logger tests: **13 passed** in isolation. The 1 skip is the intentional PostgreSQL/Redis availability guard (`test_health_endpoint.py`), which can transiently trigger under full-suite DB connection contention and passes when integration tests run on their own (9/9 passed).

## Blockers (local environment)
- `npm run build` fails if `__NEXT_PRIVATE_STANDALONE_CONFIG` env var is set (contains serialized config from another machine; `JSON.parse` loses function values like `generateBuildId`). Unset the env var before building. Unrelated to i18n changes.
- Next.js dev server fails with Tailwind CSS JIT error in edge runtime on Windows (pre-existing environment issue, unrelated to i18n changes). Production build works correctly.
- npm install times out locally — frontend dependencies not installed; works in CI.
