# MODULE: Core System
Purpose: Manage project core — config, service registry, interfaces, events, errors, status, version compat.
Responsibilities: general settings; module structure; service registration/discovery; interface management; event bus; common error handling; service status; version compat.
Inputs: config files, service registrations.
Outputs: service registry, event bus, error context, status.
Relations: all backend modules, config, logging, monitoring.
DB: none (config in files/env).
Files: src/core/{config,registry,events,errors,status,version}.*
Deps: none (base).
Errors: config validation, service not found, version mismatch.
Config: env-based, per-environment.
Security: no secrets in logs; config validation.
Tests: unit (registry, events, errors), integration (service wiring).
Acceptance: project boots; services register; events flow; errors handled.
Future: extract to shared package.
Phase: 1
