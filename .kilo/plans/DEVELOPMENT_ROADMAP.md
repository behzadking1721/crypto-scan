# DEVELOPMENT ROADMAP

## Order
1. Open-source audit (OPEN_SOURCE_AUDIT.md)
2. Data source audit (DATA_SOURCE_AUDIT.md)
3. Tech stack finalization (TECHNICAL_STACK.md)
4. Architecture (ARCHITECTURE.md)
5. DB design (DATABASE_DESIGN.md)
6. Module contracts (MODULE_SPECIFICATIONS.md)
7. UI/UX design (DESIGN_SYSTEM.md)
8. Repo structure (PROJECT_STRUCTURE.md)
9. GitHub + CI (GIT_WORKFLOW.md)
10. Core system build (Phase 1)

## Phases
0 Design & Audit → 1 Core Infra → 2 Data Infra → 3 Market Data → 4 Dashboard → 5 Wallet Intel → 6 Trader Intel → 7 Live & Signals → 8 Analytics → 9 Alerts → 10 Polish

## Dependencies
- Phase 2 requires Phase 1.
- Phase 3 requires Phase 2.
- Phase 4 requires Phase 3.
- Phase 5 requires Phase 2,3.
- Phase 6 requires Phase 3.
- Phase 7 requires Phase 5,6.
- Phase 8 requires Phase 6,7.
- Phase 9 requires Phase 7,8.
- Phase 10 requires Phase 9.

## Principle
Infrastructure first → valid data → accurate analysis → UI → advanced features. No AI until data infra stable.
