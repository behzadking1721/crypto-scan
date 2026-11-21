# DATA SOURCE AUDIT (initial)

## Exchanges (priority)
1. Hyperliquid (public account activity, positions)
2. Binance (price, volume, futures)
3. Bybit (market data)
4. OKX (market data)
Others: Bitget, Gate.io, KuCoin, Coinbase, Kraken, Deribit, Bitfinex, MEXC (market data).

## Blockchains (v1)
Ethereum, Solana, Arbitrum. Providers to evaluate: Alchemy, Helius, Moralis, Bitquery, GoldRush, Etherscan, Solscan, The Graph, Subsquid, Dune.

## Market data providers
CoinGecko, CoinMarketCap, CoinGlass, DeFiLlama, DexScreener, GeckoTerminal, CryptoCompare, Mempool.space.

## Provider selection criteria
Accuracy, coverage, reliability, API stability, rate limits, latency, historical data, pricing, docs, license/terms. Primary + secondary + fallback for critical data. Conflicts logged, not auto-resolved.

## Budget
Minimal/free tiers first; scale when validated.

## Important limitation
Public exchange APIs do not reveal trader identity. Distinguish: Public Market Activity vs Public Wallet Activity vs Public Trader Account Activity vs User Private Data.
