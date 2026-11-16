# MODULE: Market Data Engine
Purpose: Manage general market data.
Data: price, OHLCV, volume, market cap, funding, OI, liquidations, order book snapshots, trades, depth.
Sources: Binance, Hyperliquid, Bybit, OKX, CoinGecko, CoinGlass.
Outputs: Market Overview, Heatmap, charts, funding/OI dashboards.
Inputs: connector events.
Relations: connector, normalizer, event processor, frontend API.
DB: market_prices, market_candles, market_metrics, assets, markets.
Files: src/market-data/{service,repository,api}.*
Deps: connector, normalizer.
Errors: stale data, source mismatch → flag.
Config: source priority, refresh intervals.
Security: read-only public data.
Tests: unit (aggregation), integration (source compare).
Acceptance: real market data shown; source+timestamp preserved; latency tracked.
Future: more sources, derivatives.
Phase: 3,4
Priority sources: Hyperliquid, Binance, Bybit, OKX.
