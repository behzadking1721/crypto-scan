# Crypto Intelligence Platform — Master Plan

Plan index. Per-module and per-phase plans live alongside this file.

## Decisions
- Architecture: Modular Monolith + Data Workers
- Frontend: Next.js + TS; Backend: FastAPI (Python data/analysis)
- DB: PostgreSQL + Redis + TimescaleDB; WS realtime
- Sources priority: Hyperliquid → Binance → Bybit → OKX
- Auth: read-only keys v1; no trading/withdrawal; no private keys
- AI features deferred; copy trading out of v1
- i18n: English + Persian from Phase 1 (RTL, Persian numerals, Shamsi dates)
- Queue: Celery (Redis) between connectors and event processor; DLQ + retry
- v1 networks: Ethereum, Solana, Arbitrum
- Default UI language: English (Persian supported)

## Modules (each MODULE_*.md)
Core System, Data Connector, Normalization, Data Quality, Event Processing, Market Data, Wallet Intelligence, Trader Intelligence, Smart Money, Signal, Analytics, Alert, Realtime Gateway, User Management, Search, Rate Limiting, Health/Status, Audit Log, Localization

## Phases (each PHASE_*.md)
0 Design & Audit → 1 Core Infra → 2 Data Infra → 3 Market Data → 4 Dashboard → 5 Wallet Intel → 6 Trader Intel → 7 Live & Signals → 8 Analytics → 9 Alerts → 10 Polish

## AI execution rules
1. Read AI_PROJECT_CONTEXT + PROJECT_STATE + relevant module/phase plan first
2. No architecture changes without approval
3. Small independent tasks
4. Tests before merge
5. Update docs with code
6. End-of-task report required
7. No false claims about tests/Git

## Open questions
- Hosting location, API budget, product name/domain
