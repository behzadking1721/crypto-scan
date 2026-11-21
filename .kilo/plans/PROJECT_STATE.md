# PROJECT STATE

## Current phase
Phase 1 — Core Infra (in progress)

## Status
- Phase 0 design docs: done
- Phase 1 scaffolding: in progress
  - .gitignore, README.md
  - apps/api: FastAPI skeleton (main.py, config.py, requirements.txt, rate_limit.py, audit.py, auth.py)
  - apps/web: Next.js skeleton + i18n middleware + locale messages (en/fa)
  - infrastructure/docker/docker-compose.dev.yml (Postgres + Redis)
  - .github/workflows/ci.yml
- Pending: CI/CD branch protection (GitHub settings), logging/monitoring, DB migrations, 2FA, health page (frontend), i18n wiring (next-intl provider)

## Blockers
- npm install times out (network/registry) — frontend deps not installed; verify later.
- No Python runtime installed locally — backend cannot run; install Python 3.11+.
- No Docker installed locally — compose cannot run; install Docker Desktop.
