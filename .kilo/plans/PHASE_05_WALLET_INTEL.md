# PHASE 5 — Wallet Intelligence
Goal: Track and analyze wallets.
Tasks:
1. Chain connectors (Ethereum, Solana, Arbitrum)
2. Wallet Explorer, Tracker, Profile
3. Transaction history, token transfers
4. Wallet PNL (realized/unrealized, ROI, win rate, profit factor, drawdown, holding time)
5. Historical token price strategy
6. DeFi positions handling
7. Cross-chain identity detection (basic)
8. Wallet Groups, Favorites
Exit: wallet history visible; incomplete data flagged; PNL only with sufficient coverage.
Deps: Phase 2, 3.
Tests: PNL unit tests with fixtures; integration.
Modules: Wallet Intelligence, Data Connector.
Status: Planned.
PNL rules: fees, internal transfers not P&L, open vs closed separated.
