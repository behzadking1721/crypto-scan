# MODULE: Rate Limiting
Purpose: Protect APIs and external calls.
Features: per-user, per-IP, per-endpoint limits; external provider limit management.
Inputs: request metadata.
Outputs: allow/deny + retry-after.
Relations: API layer, connectors, user management.
DB: none (Redis).
Files: src/rate-limit/{middleware,limiter,provider-limits}.*
Deps: Redis.
Errors: 429 with retry-after.
Config: limits per tier/endpoint.
Security: abuse prevention.
Tests: unit (limit logic), integration (middleware).
Acceptance: limits enforced; provider limits respected.
Future: adaptive limits.
Phase: 1,2
Covers internal API + external provider limits.
