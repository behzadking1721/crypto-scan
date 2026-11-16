# MODULE: User Management
Purpose: Manage users and personal settings.
Features: registration, login, profile, favorites, wallet groups, watchlists, saved filters, dashboard prefs, notification prefs, API management.
Auth: email/password + OAuth (Google at least); 2FA; RBAC (Free/Pro-ready).
Rules: read-only API keys in v1; encrypted secrets; usage tracking per user (for future billing).
Inputs: user actions.
Outputs: user data, settings.
Relations: all user-facing modules, alert, realtime.
DB: users, user_profiles, user_settings, api_credentials, favorites, watchlists.
Files: src/user/{auth,profile,settings,api-keys}.*
Deps: auth lib, DB.
Errors: invalid input, auth failure, suspicious login detection.
Config: auth providers, session settings.
Security: hashing, encryption, RBAC, audit logs, CORS, CSP.
Tests: unit (auth), integration (flows), security.
Acceptance: register/login works; keys encrypted; RBAC ready.
Future: Pro tier, billing, SSO.
Phase: 1,9
OAuth + 2FA required from v1.
