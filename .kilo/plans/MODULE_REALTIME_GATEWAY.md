# MODULE: Realtime Gateway
Purpose: Push live data to frontend.
Features: WebSocket, connection management, subscriptions, channel management, reconnection, message validation, rate limiting.
Rules: users receive only needed data (e.g., favorites only).
Flow: Data Events → Event Processor → Realtime Gateway → WebSocket → Frontend.
Inputs: processed events, user subscriptions.
Outputs: WS messages.
Relations: event processor, user management, frontend.
DB: none (state in Redis).
Files: src/realtime/{gateway,channels,subscriptions,validation}.*
Deps: WS server, Redis.
Errors: reconnect handling, invalid messages dropped.
Config: channel definitions, rate limits.
Security: auth on connect; validate messages.
Tests: unit (validation), integration (WS flow).
Acceptance: live events without refresh; targeted delivery.
Future: scaling (multiple gateway instances).
Phase: 4,7
Subscription-based delivery to avoid over-sending.
