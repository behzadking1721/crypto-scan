# MODULE: Data Connector
Purpose: Fetch data from external sources via standard contract.
Responsibilities: API connect/disconnect, historical/latest fetch, subscribe/unsubscribe, health_check, status, rate limit, retry, timeout, reconnect, WS, completeness check.
Contract: connect, disconnect, health_check, fetch_historical, fetch_latest, subscribe, unsubscribe, get_status.
Inputs: source config, credentials.
Outputs: raw data + connection status.
Relations: normalizer, data quality, event processor.
DB: data_sources, data_source_status, connector_logs, api_credentials.
Files: connectors/{exchanges,blockchains,market-data,analytics-providers}/<name>/.
Deps: http client, ws client.
Errors: timeout, rate limit, auth, disconnect, partial data.
Config: per-connector endpoints, keys, limits.
Security: encrypted keys; no keys in logs/frontend.
Tests: unit (mock connector), integration (real source in staging), contract tests.
Acceptance: >=1 source connected; health reported; retry works; mock connector for tests.
Future: connector versioning, connection pooling, mock connector standard.
Phase: 2,3,5
