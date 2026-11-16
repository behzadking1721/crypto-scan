# MODULE: Wallet Intelligence
Purpose: Track and analyze wallets.
Features: Wallet Explorer, Tracker, Profile, History, Groups, Favorites, Performance, Classification, Behavior, Correlation.
Calculations: realized/unrealized PNL, ROI, win rate, profit factor, avg holding time, max drawdown, trade frequency.
Challenges: historical token price for PNL, DeFi positions (LP, lending), cross-chain identity detection.
Inputs: on-chain transfers, token holdings, prices.
Outputs: Wallet Profile (address, network, first/last activity, tx count, PNL, win rate, profit factor, drawdown, behavior, coverage, confidence).
Relations: connector (chain), normalizer, data quality, market data.
DB: wallets, wallet_labels, wallet_groups, wallet_group_members, transactions, transfers, wallet_balances.
Files: src/wallet-intel/{service,repository,pnl,classifier,correlation}.*
Deps: chain connectors, price service.
Errors: insufficient coverage → mark incomplete; no definitive PNL.
Config: chain providers, price sources.
Security: read-only public data.
Tests: unit (PNL calc with fixtures), integration (chain data).
Acceptance: wallet history visible; incomplete data flagged; PNL only with sufficient coverage.
Future: more chains, DeFi, cross-chain identity.
Phase: 5
PNL rules: include fees, internal transfers not counted as P&L, open vs closed separated, price at tx time.
