# PHASE 2 — Data Infrastructure
Goal: Build data ingestion and quality layer.
Tasks:
1. Connector framework (standard contract)
2. Mock connectors for tests
3. Data Normalizer (standard schema)
4. Data Quality Engine (incl. wash trading, sybil, cross-source, staleness)
5. Event Processor (dedup, idempotency, recovery, DLQ)
6. Raw storage, retry, rate limit, provider health monitor
7. Message queue (Celery on Redis)
Exit: >=1 source connected; data normalized; dupes detected; quality reported; recovery works.
Deps: Phase 1.
Tests: unit + integration per module.
Modules: Data Connector, Normalization, Data Quality, Event Processing.
Status: Planned.
Note: most critical phase for data accuracy.
