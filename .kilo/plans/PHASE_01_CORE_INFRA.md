# PHASE 1 — Core Infra
Goal: Build project foundation.
Tasks:
1. Create repo, branches (main/develop/feature/*), branch protection
2. CI/CD (GitHub Actions)
3. Backend + Frontend skeleton
4. DB (PostgreSQL), Redis setup
5. Logging, monitoring, config system
6. Docker Compose dev/test/prod
7. i18n skeleton (next-intl, RTL) — Localization module
8. Auth skeleton (OAuth, 2FA) — User Management
9. Rate limiting middleware — Rate Limiting module
10. Health/status page — Health/Status module
11. Audit log — Audit Log module
Exit: project runs; DB connects; tests green; CI active; i18n works.
Deps: Phase 0.
Tests: smoke tests, CI pipeline.
Status: Planned.
Modules: Core System, User Management, Rate Limiting, Health/Status, Audit Log, Localization.
