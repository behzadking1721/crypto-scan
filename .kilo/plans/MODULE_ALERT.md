# MODULE: Alert Engine
Purpose: Manage user alerts.
Types: Wallet Activity, Whale, Smart Money, Trader Position, Signal, Price, Funding, Unusual Volume.
Channels: in-app, browser notification, Telegram, Email, Webhook.
Rules: per-alert config; dedup window; priority levels (Critical/Info); no spam.
Inputs: events, user rules.
Outputs: notifications.
Relations: event processor, user management, realtime gateway.
DB: alerts, notifications.
Files: src/alert/{engine,rules,channels,dedup}.*
Deps: user management, event processor.
Errors: duplicate alerts suppressed; channel failure logged.
Config: channel credentials, dedup windows.
Security: encrypted channel secrets; rate limit per user.
Tests: unit (rule eval), integration (channel send).
Acceptance: alerts only on defined conditions; dedup works; user-manageable.
Future: more channels.
Phase: 9
Webhook channel required for trading tools.
