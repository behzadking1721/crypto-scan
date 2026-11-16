# MODULE: Localization
Purpose: i18n and RTL support.
Features: English + Persian, RTL/LTR layout, Persian numerals, Shamsi dates, currency/number formatting.
Inputs: locale setting, user preference.
Outputs: translated UI, formatted values.
Relations: frontend, user management.
DB: user_settings (locale).
Files: apps/web/i18n/, locales/{en,fa}.json, utils/format.
Deps: next-intl.
Errors: missing key → fallback to English.
Config: default locale, supported locales.
Security: none.
Tests: unit (format), integration (locale switch).
Acceptance: RTL works; Persian numerals; Shamsi dates.
Future: more languages.
Phase: 1
Must be in place from Phase 1 (RTL affects layout).
