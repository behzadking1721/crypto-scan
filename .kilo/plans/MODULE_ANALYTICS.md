# MODULE: Analytics Engine
Purpose: Statistical and comparative analysis.
Features: trader/wallet comparison, historical performance, signal backtesting, wallet correlation, strategy clustering, performance attribution, historical replay, shadow portfolio.
Rules: deterministic calculations; backtest must prevent lookahead bias, include transaction costs (fees, slippage, funding), out-of-sample testing, statistical significance.
Inputs: trades, signals, market data.
Outputs: comparison results, backtest reports, replay, shadow portfolio.
Relations: trader, wallet, signal, market data.
DB: backtest_runs, backtest_results, shadow_portfolios, shadow_portfolio_positions.
Files: src/analytics/{comparison,backtest,replay,clustering,attribution,shadow}.*
Deps: trader, wallet, signal, market data.
Errors: invalid assumptions → document; insufficient data → flag.
Config: backtest parameters, cost model.
Security: read-only.
Tests: unit (calculations), integration (reproducibility).
Acceptance: reproducible; assumptions documented; costs included.
Future: predictive analytics, regime detection.
Phase: 8
Backtest is weakest part — enforce anti-overfitting.
