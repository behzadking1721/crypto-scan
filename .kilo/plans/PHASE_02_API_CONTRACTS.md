# Phase 2 — API Contract Design (F5.2)

## Endpoint Catalog

- `GET /api/v1/market/overview`
- `GET /api/v1/market/assets`
- `GET /api/v1/market/assets/{asset_id}`
- `GET /api/v1/market/assets/{asset_id}/history`
- `GET /api/v1/market/freshness`
- `GET /api/v1/watchlist`
- `POST /api/v1/watchlist`
- `DELETE /api/v1/watchlist/{asset_id}`
- `GET /api/v1/settings`
- `PATCH /api/v1/settings`

## Common Standards

### Response Envelope

Success:
```
{ "data": ..., "meta": { "request_id": "uuid" } }
```

Error:
```
{ "error": { "code": "NOT_FOUND", "message": "..." }, "meta": { "request_id": "uuid" } }
```

### Timestamp
- ISO 8601, UTC, timezone-aware.
- Missing timestamp: return null or omit; never fabricate.

### Numeric Precision
- Prices/volumes/market caps as numbers (JSON number). Backend should preserve precision; avoid rounding unless documented.

### Pagination
- Query params: `limit` (default 50, max 200), `offset` (default 0).
- Response meta: `total`, `limit`, `offset`.

### Sorting & Filtering
- `sort_by`: market_cap | price | change_24h | volume
- `sort_dir`: asc | desc (default desc)
- `search`: case-insensitive substring on name/symbol.

### Error Codes
- VALIDATION_ERROR, NOT_FOUND, UNAUTHORIZED, FORBIDDEN, RATE_LIMITED, DATA_UNAVAILABLE, INTERNAL_ERROR

### Versioning
- All endpoints under `/api/v1/`.

### Idempotency
- Watchlist POST should be idempotent by asset_id (no duplicate).

## Market Overview

`GET /api/v1/market/overview`

Response:
```
{
  "data": {
    "total_market_cap_usd": 2700000000000,
    "total_volume_24h_usd": 95000000000,
    "btc_dominance_percent": 52.3,
    "eth_dominance_percent": 17.1,
    "last_updated": "2026-01-01T00:00:00Z",
    "source": "mock",
    "freshness": "fresh"
  }
}
```

## Asset List

`GET /api/v1/market/assets?search=&sort_by=market_cap&sort_dir=desc&limit=50&offset=0`

Response:
```
{
  "data": [ { "id": "bitcoin", "symbol": "BTC", "name": "Bitcoin", "price_usd": 64000, ... } ],
  "meta": { "total": 3, "limit": 50, "offset": 0 }
}
```

## Asset Detail

`GET /api/v1/market/assets/{asset_id}`

Returns single asset object or 404.

## Historical OHLCV

`GET /api/v1/market/assets/{asset_id}/history?range=7D`

Query: `range` in {1D,7D,30D,90D,1Y}; optional `start`, `end`.

Response:
```
{
  "data": {
    "asset_id": "bitcoin",
    "range": "7D",
    "points": [ { "timestamp": "2026-01-01T00:00:00Z", "price_usd": 64000 } ],
    "is_mock": true
  }
}
```

Ordering: ascending by timestamp. Gaps allowed; client should handle missing points.

## Freshness

`GET /api/v1/market/freshness`

Response:
```
{ "data": { "source": "mock", "last_updated": "...", "is_stale": false } }
```

Freshness also included in overview and asset detail.

Fresh/Stale/Unknown determination: based on data source heartbeat and configured staleness threshold (threshold TBD).

## Watchlist

- `GET /api/v1/watchlist` -> list of asset ids (or asset objects)
- `POST /api/v1/watchlist` body `{ "asset_id": "bitcoin" }` -> 201 or 200 idempotent
- `DELETE /api/v1/watchlist/{asset_id}` -> 204

Requires authentication. User isolation enforced.

## Settings

- `GET /api/v1/settings`
- `PATCH /api/v1/settings` body `{ "language": "fa" }`

Only supported settings: language, theme (optional). Data source config is read-only/admin.

## Frontend Compatibility

Frontend types in `apps/web/types/market.ts` map directly. `ApiMarketProvider` will implement `MarketDataProvider` and call these endpoints. Mock provider remains for dev/test.

## Connector Compatibility

API consumes normalized data from services; no provider-specific fields exposed. Freshness derived from connector status/last_success_at.

## Open Questions

- Freshness staleness threshold values (TBD).
- Authentication mechanism details (JWT/session).
- Pagination default/max.
- Watchlist returns ids vs full assets.

## Decision Log

- API versioning: /api/v1.
- Timestamps: UTC ISO 8601.
- History ranges: 1D,7D,30D,90D,1Y.
- Idempotent watchlist add.

## Numeric Precision Policy (Proposed)

- Financial values (price, volume, market cap) should be transferred as JSON strings at the API boundary, e.g. `"price": "67432.12345678"`.
- Backend should use Decimal or equivalent precise numeric types.
- Avoid unintended conversion to binary floating point during calculation/serialization.
- Frontend contract should receive these as strings.
- Conversion to Number only where precision loss is acceptable.
- NaN/Infinity invalid.

Note: Current Frontend types use `number`. This conflicts with the proposed string policy and will require a future contract/type decision. TypeScript types are not changed in this stage.

## Authentication Status

- Authentication method not yet selected (JWT vs session).
- Watchlist/settings dependent on authenticated user; implementation deferred until decision.
- User data isolation mandatory.

## Freshness Thresholds

- Fresh/Stale/Unknown retained.
- Thresholds not yet defined; must be configurable.
- Mock/Simulated/Live distinguishable.

## Pagination Defaults

- Method retained.
- Default/max page size pending decision; must be configurable and validated.

## Decision Log

| Topic | Status |
|---|---|
| Numeric Precision | Proposed: Decimal internally, String at API boundary |
| Authentication | Pending user decision |
| Freshness Thresholds | Pending |
| Pagination Defaults | Pending |
| Maximum Page Size | Pending |
