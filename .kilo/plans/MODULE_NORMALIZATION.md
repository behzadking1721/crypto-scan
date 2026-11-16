# MODULE: Normalization
Purpose: Convert heterogeneous source data into standard internal schema.
Responsibilities: asset/symbol unification, unit conversion, timestamp normalization, trade type conversion, spot/futures handling, duplicate detection, preserve raw reference.
Standard Event: Event ID, Source, Event Type, Asset, Network, Wallet, Trader, Price, Quantity, Notional, Timestamp, Received At, Raw Ref, Data Quality.
Inputs: raw connector output.
Outputs: Normalized Event.
Relations: connector, data quality, event processor.
DB: raw_events, normalized_events.
Files: src/normalization/{schema,mappers,dedup}.*
Deps: shared-types.
Errors: unknown symbol, bad timestamp, missing fields.
Config: symbol mapping tables, unit rules.
Security: validate inputs.
Tests: unit (mappers), integration (connector→normalizer).
Acceptance: data from >=1 source normalized; dupes detected; raw preserved.
Future: reprocessing on schema change.
Phase: 2
