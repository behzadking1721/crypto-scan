# Crypto Intelligence Platform

Smart Money & Trader Intelligence System. See `.kilo/plans/` for architecture and roadmap.

## Stack
- Frontend: Next.js + TypeScript
- Backend: FastAPI (Python)
- Data/analysis: Python
- DB: PostgreSQL + Redis (+ TimescaleDB TBD)
- Queue: Celery on Redis

## Dev
See `infrastructure/docker/docker-compose.dev.yml` (Docker required). Frontend: `cd apps/web && npm install && npm run dev`. Backend: `cd apps/api && pip install -r requirements.txt && uvicorn main:app --reload`.

## Status
Phase 1 — Core Infra in progress. See `.kilo/plans/PROJECT_STATE.md`.
