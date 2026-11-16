# MODULE: Search
Purpose: Search across wallets, traders, assets.
Features: wallet/trader/asset search, filters, saved filters integration.
Inputs: query string, filters.
Outputs: ranked results.
Relations: wallet, trader, market data.
DB: uses existing tables + search index.
Files: src/search/{service,index,query}.*
Deps: DB full-text or search engine.
Errors: empty results → empty state.
Config: index fields, ranking.
Security: input validation, rate limit.
Tests: unit (query parsing), integration (search flow).
Acceptance: search returns relevant results quickly.
Future: advanced search, AI queries.
Phase: 4+
New module not in original doc.
