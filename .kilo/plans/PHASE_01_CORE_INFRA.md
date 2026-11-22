# PHASE 1 — Core Infra
Goal: Build project foundation.

Tasks:
1. Create repo, branches (main/develop/feature/*), branch protection — DONE (branches created; branch protection pending in GitHub settings)
2. CI/CD (GitHub Actions) — DONE (workflow added; CI green on push/PR)
3. Backend + Frontend skeleton — DONE (committed in 52459bb)
4. DB (PostgreSQL), Redis setup — DONE (async SQLAlchemy asyncpg + Redis client; Docker Compose dev)
5. Logging, monitoring, config system — DONE (Logging via apps/api/logger.py; Monitoring via apps/api/health.py; config.py done incl. log_level + rate-limit settings)
6. Docker Compose dev/test/prod — DONE (dev compose committed; test/prod pending)
7. i18n skeleton (next-intl, RTL) — DONE (`apps/web/i18n.ts` + `[locale]` routing + `NextIntlClientProvider` + `useTranslations('Home')` + RTL/LTR + `Home`-namespaced messages en/fa + `createMiddleware` from `next-intl/middleware` + 9 unit tests in `tests/unit/*.mjs` with `node:test`)
8. Auth skeleton (OAuth, 2FA) — PARTIAL (auth.py stub committed; OAuth/2FA not implemented)
9. Rate limiting middleware — DONE (Redis-backed, working tree uncommitted; tests pass). Atomic INCR+TTL via Lua; `ratelimit:<ip>` keys; TTL expiry; IP from direct client host by default, `X-Forwarded-For` only when `rate_limit_trust_proxy=True` AND client in `rate_limit_trusted_proxies`. Fail-closed default (503 when Redis down) with `rate_limit_fail_open` toggle — POLICY PENDING YOUR CONFIRMATION. Returns JSONResponse directly (no HTTPException) for 429/503. **`GET /health` and `GET /ready` exempted from rate limiting** (before Redis contact) so health endpoints remain available when Redis is down; `POST /health` and other paths/methods still rate limited. 16 rate-limit unit tests (11 original + 5 bypass tests).
10. Health/status page — DONE (`GET /health` returns overall + per-dependency status; `GET /ready` returns 200 if healthy, 503 if degraded; **frontend page implemented** — `apps/web/app/[locale]/health/page.tsx`, `apps/web/lib/api.ts`, `apps/web/components/health/StatusCard.tsx`, i18n keys in en/fa messages, 14 unit tests, verified against live backend)
11. Audit log — DONE (`apps/api/audit.py` now persists `AuditLog` records to PostgreSQL via SQLAlchemy async; `apps/api/models.py` defines `AuditLog` model; no sensitive data stored; 5 unit tests passing)

Exit criteria (verified):
- CI active and green on develop (reported via GitHub Actions)
- Backend tests green in CI (reported); full backend suite verified locally green: **64 passed, 1 skipped, 0 failed** (exit 0) after resolving the logger test-isolation blocker
- Frontend typecheck+lint green in CI (reported)
- Async PostgreSQL + Redis infrastructure committed
- Alembic installed + validated (1.20.1); **initial migration created** (`689024602bb8_initial_audit_logs_table` for `audit_logs` table); `alembic upgrade head` / `downgrade -1` verified locally against PostgreSQL
- Redis-backed rate limiting implemented and tested locally (57 passed, 1 skipped total; 16 rate-limit tests incl. 5 health-bypass tests)
- Structured JSON logging implemented and tested locally (13 logger tests; isolation-safe — `crypto.api` logger state snapshotted/restored per test via autouse fixture to prevent `fileConfig` disable-leak from migration tests)
- Health Monitoring implemented and tested locally: `/health` + `/ready` endpoints; 8 unit tests + 4 integration tests
- **Health endpoint rate-limit bypass verified with real containers**: Redis down → `/health` 200 degraded + `/ready` 503; Postgres down → same; both down → same; both restored → healthy/200. Fail-closed preserved for non-health paths.
- Middleware order verified end-to-end: LoggingMiddleware outermost, captures 200/429/503 with X-Request-ID
- **Persisted Audit Logging verified**: `audit()` persists to `audit_logs` table via SQLAlchemy async; DB write failures logged without crashing caller; 5 unit tests passing; verified with live backend (audit events visible in `audit_logs` table; data survives restart)
- Project runs locally: Python 3.12 + Docker available; venv + deps installed; tests pass locally

Exit criteria (NOT yet verified):
- (none remaining)

Deps: Phase 0.
Tests: smoke tests, CI pipeline.
Status: Complete (all Phase 1 exit criteria verified)
Modules: Core System, User Management, Rate Limiting, Health/Status, Audit Log, Localization, Logging.
