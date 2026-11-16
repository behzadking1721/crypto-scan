# MODULE: Signal Engine
Purpose: Generate algorithmic signals.
Types: Open Long, Open Short, Close Long, Close Short, Increase, Reduce, Spot Buy, Spot Sell.
Signal fields: ID, Asset, Type, Source Wallets, Source Traders, Entry Ref Price, Timestamp, Confidence, Evidence, Data Quality, Algorithm Version, Status.
Rules: raw vs composite signals distinct; dedup/merge duplicates; versioned algorithms; reproducible output; per-algorithm performance tracked.
Each signal must explain why (evidence).
Inputs: smart money, wallet, trader, market data.
Outputs: signals + evidence.
Relations: smart money, wallet, trader, market data, analytics, realtime.
DB: signals, signal_evidence, signal_performance.
Files: src/signal/{engine,types,evidence,versioning,dedup}.*
Deps: smart money, wallet, trader, market data.
Errors: conflicting signals (long+short) → resolve; expiry; version invalidation.
Config: signal thresholds, expiry windows.
Security: read-only.
Tests: unit (signal gen), integration (evidence check).
Acceptance: every signal has reason+source+version; dedup works; expiry defined.
Future: AI analyst.
Phase: 7
Signal expiry and conflict resolution required.
