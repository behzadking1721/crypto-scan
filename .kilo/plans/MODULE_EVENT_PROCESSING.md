# MODULE: Event Processing
Purpose: Process incoming events, prevent duplicates, recover missed.
Responsibilities: ingest normalized events, dedup (idempotency keys), sequence handling, recovery/backfill trigger, dispatch to engines via queue.
Inputs: normalized events.
Outputs: processed events dispatched to queues.
Relations: normalizer, data quality, queue, wallet/trader/signal engines, realtime gateway.
DB: normalized_events, event_processing_logs.
Files: src/event-processing/{processor,dedup,recovery,dispatcher}.*
Deps: Celery, Redis.
Errors: duplicate, out-of-order, processing failure → DLQ.
Config: retry policy, backoff.
Security: validate payloads.
Tests: unit (dedup), integration (end-to-end event).
Acceptance: no duplicate processing; missed events recoverable; DLQ works.
Future: priority queues, partitioning.
Phase: 2
Queue: Celery on Redis; DLQ; exponential backoff retry.
