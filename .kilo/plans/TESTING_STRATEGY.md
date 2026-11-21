# TESTING STRATEGY

## Test types
Unit, Integration, Contract, Regression, Performance, Security, Data Validation, E2E.

## Data validation
PNL: correct entry/exit price, quantity, fees, funding; internal transfers not counted as P&L; open vs closed separated.

## Acceptance per module
Works as specified; standard I/O; tests pass; integration verified; errors handled; docs updated; no critical open issues; changes recorded in Git.

## Definition of Done checklist
- [ ] Tasks complete
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Docs updated
- [ ] No critical issues
- [ ] Changes committed (WIP ok on feature branch)

## Rules
- Test before merge. No untested changes to stable.
- Mock connectors for tests (no real API in unit tests).
- Reproducible calculations.
