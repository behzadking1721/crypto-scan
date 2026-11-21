# AI PROJECT CONTEXT

## Purpose
Reference for any AI agent working on this project. Read this + PROJECT_STATE + relevant module/phase plan before any change.

## Project
Crypto Intelligence Platform — Smart Money & Trader Intelligence System. Modular monolith + data workers.

## Stack
Next.js + TS (frontend), FastAPI (backend API), Python (data/analysis), PostgreSQL + Redis + TimescaleDB, Celery queue, WebSocket realtime.

## Structure
apps/web, apps/api, services/*, packages/*, connectors/*, database/*, tests/*, infrastructure/*, scripts/* (see master plan section 18).

## Rules for AI
1. Read AI_PROJECT_CONTEXT + PROJECT_STATE + relevant module/phase plan first.
2. No architecture changes without approval (interfaces, merges, DB without migration, deps, other modules).
3. Small independent tasks.
4. Tests before merge.
5. Update docs with code.
6. End-of-task report: files changed, features added, tests run+results, remaining issues, dep changes, docs updated, merge-ready?
7. No false claims about tests/Git.

## Naming conventions
- TS: camelCase vars/functions, PascalCase components/types, kebab-case files.
- Python: snake_case.
- DB columns: snake_case.
- API endpoints: /api/v1/<resource>.
- Files: kebab-case.

## Code style
- TS: ESLint + Prettier.
- Python: Black + Ruff.
- No comments unless asked.

## Module boundaries
Each module has its own plan in MODULE_*.md. Do not cross boundaries without contract.

## v1 scope
Public APIs first; read-only keys; no trading/withdrawal; no private keys; no copy trading; no AI (deferred to Phase 10); free tier only.

## i18n
English + Persian from Phase 1; RTL/LTR; Persian numerals; Shamsi dates.

## Current phase
Phase 0 — Design & Audit (in progress).
