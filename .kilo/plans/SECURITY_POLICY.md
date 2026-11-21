# SECURITY POLICY

## API management (v1)
Public APIs first. Personal keys read-only only. No withdrawal/trade permissions. No private keys ever.

## Key protection
Encrypted storage; no secrets in frontend or logs; access restriction; revoke/disable; user isolation.

## User security
Auth (email+OAuth Google), 2FA, RBAC (Free/Pro-ready), rate limiting, input validation, session security, audit logs, backups, DB security.

## Code security
Dependency scanning, secret scanning, static analysis, vulnerability checks, security testing. CORS policy, CSP headers, ORM-only (no raw SQL from user input), suspicious login detection.

## Data
No user private keys; read-only keys only; encrypted at rest.
