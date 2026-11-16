# MODULE: Health/Status
Purpose: System and connector health monitoring.
Features: service status page, connector health, latency, uptime, error rates.
Inputs: service/connector metrics.
Outputs: status dashboard, alerts on degradation.
Relations: core system, connectors, monitoring.
DB: data_source_status, connector_logs.
Files: src/health/{service,status-page,metrics}.*
Deps: core, connectors.
Errors: degraded → alert.
Config: thresholds, check intervals.
Security: admin-only details.
Tests: unit (health checks), integration (status page).
Acceptance: status visible; degradation detected.
Future: public status page.
Phase: 1,2
New module not in original doc.
