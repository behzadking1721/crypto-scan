# MODULE: Smart Money
Purpose: Detect smart money activity.
Features: tracking, consensus, net buy/sell flow, wallet clustering, early entry, accumulation/distribution, whale activity, unusual activity.
Logic: check wallet independence, prior performance, volume, shared source/contract, market confirmation, sustainability, wallet correlation.
Inputs: wallet activity, market data, wallet scores.
Outputs: Smart Money Radar, consensus signals, flow metrics.
Relations: wallet intelligence, market data, data quality, signal engine.
DB: wallets, wallet_labels, signals, signal_evidence.
Files: src/smart-money/{service,consensus,clustering,flow,detection}.*
Deps: wallet intel, market data.
Errors: correlated wallets counted as one; insufficient evidence → no signal.
Config: thresholds, time windows.
Security: read-only.
Tests: unit (consensus logic), integration (scenario fixtures).
Acceptance: detects accumulation; avoids false positives from wash/sybil.
Future: predictive analytics.
Phase: 7
Critical: wash trading/sybil detection must exist before this module.
