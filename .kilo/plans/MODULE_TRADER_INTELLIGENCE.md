# MODULE: Trader Intelligence
Purpose: Analyze trader performance and behavior.
Features: discovery, leaderboard, profile, history, PNL, win rate, profit factor, drawdown, consistency, trader score.
Calculations: entry/exit price, quantity, fees, funding, slippage; identity resolution across exchanges.
Trader Score weights (initial, to validate): ROI 15%, MaxDD 20%, ProfitFactor 15%, WinRate 10%, Consistency 15%, Risk/Reward 10%, SampleSize 5%, Risk-Adjusted 10%.
Inputs: trades, positions, account history where accessible.
Outputs: Trader Profile with score, ranking.
Relations: market data, connector (exchange), data quality.
DB: traders, trader_profiles, trader_statistics, trades, positions.
Files: src/trader-intel/{service,repository,score,pnl,identity}.*
Deps: connector, market data.
Errors: incomplete history → no misleading ranking; sample size too small → flag.
Config: score weights (configurable).
Security: read-only; no private keys.
Tests: unit (PNL, score), integration (real data validation).
Acceptance: calculations validated on test + real data; fees/funding included.
Future: more exchanges, identity resolution.
Phase: 6
Note: ranking by profit alone is insufficient; risk and sample size matter.
