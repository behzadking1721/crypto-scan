# DATABASE DESIGN (initial)

DB: PostgreSQL (primary), Redis (cache/state), TimescaleDB (evaluate for time-series). All timestamps UTC. Migrations only for schema changes. Idempotent event IDs. Raw vs processed separated.

## Core tables
users, user_profiles, user_settings
data_sources, data_source_status, api_credentials, connector_logs
assets, networks, markets
wallets, wallet_labels, wallet_groups, wallet_group_members
traders, trader_profiles, trader_statistics
trades, positions, transactions, transfers, wallet_balances
market_prices, market_candles, market_metrics
raw_events, normalized_events, event_processing_logs
signals, signal_evidence, signal_performance
alerts, notifications
favorites, watchlists
backtest_runs, backtest_results
shadow_portfolios, shadow_portfolio_positions
audit_logs

## Rules
- UTC timestamps; display per user tz.
- Raw data separated from processed.
- Source traceability on every record.
- Unique event IDs; idempotency.
- No destructive deletes without policy.
- Indexes/constraints defined in migration phase.

## Open
- Exact relations, indexes, partitioning for time-series (Phase 0/1).
- TimescaleDB decision after perf test.
