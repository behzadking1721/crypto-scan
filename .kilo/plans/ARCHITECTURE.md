# ARCHITECTURE

## Style
Modular Monolith + Independent Data Workers (not microservices initially). Modules independent, low coupling, high cohesion. Extract hot paths to services later.

## Layers
External Sources (CEX/DEX/Blockchains) → Data Connectors → Normalizer → Data Quality → Event Processor (via Celery/Redis queue) → Intelligence Engines (Trader/Wallet/Signal) → API Layer → Realtime Gateway (WS) → Frontend → User.

## Rules
1. Frontend never calls exchange APIs directly.
2. Analysis modules use only normalized data.
3. Each connector owns its source.
4. No module mutates another's internals.
5. Inter-module via interface/contract/event.
6. Every data has traceable origin.
7. Every module independently testable.
8. No provider-specific logic in analysis core.

## Infra
Frontend: Next.js + TS. Backend API: FastAPI. Data/analysis: Python. DB: PostgreSQL + Redis + TimescaleDB (evaluate). WS realtime. Queue: Celery on Redis (DLQ + exponential backoff retry).

## v1
Hosting: local dev (Docker Compose) first, cloud later.
Networks: Ethereum, Solana, Arbitrum.
API budget: minimal/free tiers first.
Product name: TBD (working: Crypto Intelligence Platform).
Languages: English + Persian from Phase 1.

## Data quality levels
High/Medium/Low/Insufficient. No engine produces definitive result without quality awareness.

## Security
Public APIs first; personal keys read-only; no trading/withdrawal; no private keys. Encrypted secrets; RBAC; rate limiting; input validation; audit logs; CORS; CSP; ORM-only; suspicious login detection.
