# Workflow Governance Model Plans

Created: 2026-08-08

## Phase 1: Public composition contract

| Task | Content | DoD | Depends | Status |
| --- | --- | --- | --- | --- |
| 1.1 | Add a versioned, credential-free workflow handoff JSON Schema and examples. | Schema accepts the valid example and rejects invalid fixture in unit tests. | - | cc:完了 |
| 1.2 | Document WGM, Mothership Router, and Mothership compatibility and handoff boundary. | README and compatibility document distinguish advice, approval, and execution. | 1.1 | cc:完了 |
| 1.3 | Add public CI and release metadata for this compatible public surface. | CI syntax is valid and standard test suite succeeds locally. | 1.1, 1.2 | cc:WIP |
