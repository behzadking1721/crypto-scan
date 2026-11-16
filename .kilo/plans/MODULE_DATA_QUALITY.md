# MODULE: Data Quality Engine
Purpose: Assess correctness, completeness, quality of data.
Checks: missing data, duplicates, invalid timestamp, outliers, price/volume consistency, sequence gaps, delayed data, source availability, historical coverage, wash trading, sybil detection, cross-source validation, staleness thresholds.
Outputs: Data Quality Report (status, latency, missing, duplicates, coverage, confidence).
Levels: High/Medium/Low/Insufficient.
Inputs: normalized events, source metadata.
Relations: normalizer, event processor, all engines.
DB: normalized_events (quality field), event_processing_logs.
Files: src/data-quality/{checks,report,thresholds}.*
Deps: stats libs.
Errors: insufficient data → mark Insufficient, never produce definitive result.
Config: thresholds per asset/market type.
Security: none special.
Tests: unit (each check), integration (quality report).
Acceptance: detects incomplete/suspect data; wash trading/sybil flagged; quality reported.
Future: ML anomaly detection.
Phase: 2
Confidence: no engine result without quality awareness.
