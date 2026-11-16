# MODULE: Audit Log
Purpose: Record sensitive operations.
Features: log auth, key management, settings changes, admin actions.
Inputs: operation events.
Outputs: audit trail.
Relations: user management, security.
DB: audit_logs.
Files: src/audit/{logger,repository}.*
Deps: DB.
Errors: log failure → alert.
Config: retention policy.
Security: immutable logs; no secrets logged.
Tests: unit (log write), integration.
Acceptance: all sensitive ops logged.
Future: export, compliance.
Phase: 1,9
Mentioned in doc but not as module; now a module.
