# PHASE 7 — Live Activity & Signals
Goal: Live feed and signal generation.
Tasks:
1. Live feed UI
2. WebSocket integration (Realtime Gateway)
3. Event classification
4. Signal Engine (all types) with reason+source+version
5. Smart Money consensus (with wash/sybil guard)
6. Signal history, evidence, quality
7. Signal expiry, conflict resolution, versioning
Exit: live events without refresh; dedup handled; every signal has reason+source.
Deps: Phase 5, 6.
Tests: event flow E2E; signal generation unit.
Modules: Smart Money, Signal, Realtime Gateway.
Status: Planned.
Critical: wash trading/sybil must exist first.
