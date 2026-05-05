# Modularization Next Steps

Persistent planning note for the next SQX Edge phases.

## Recommended Order

1. Phase 36: harden Project Generator module boundaries. Done.
2. Phase 37: split the remaining `main.js` orchestration into focused files. Done.
3. Phase 38: add more granular contracts per frontend submodule. Done.
4. Phase 39: regenerate and test the portable ZIP after modularization. Done.
5. Phase 40: document the final architecture map and load order. Done.
6. Phase 41: guard architecture load-order documentation with a living contract. Done.
7. Phase 42: reduce Project Generator legacy bridge with a focused DOM helper module. Done.
8. Phase 43: add a release checklist script for tests, portable packaging and ZIP validation. Done.
9. Phase 44: polish release flow with one-click strict release, summary output and package guardrails. Done.
10. Phase 45: extract Project Generator event bindings and polling from the legacy bridge. Done.
11. Phase 46: apply operational visual polish for Project Generator, Strategies and responsive dense views. Done.

## Working Discipline

- Create a backup before changing files.
- Verify with JS contracts, Python tests, and E2E screenshots when frontend behavior is touched.
- Remove temporary Playwright dependencies after E2E.
- Use one commit per phase.
- Push only when explicitly requested or when the active instruction includes continuing the planned push step.

## Monetization Track

1. Phase M1: define monetization model for SQX Edge Pro subscription, services and templates. Done.
2. Phase M2: design licensing and access model. Done.
3. Phase M3: define distribution channels and paid delivery flow. Done.
4. Phase M4: separate Free/Pro/internal product packaging. Done.
5. Phase M5: prepare branding and go-to-market assets. Done.
6. Phase M6: run security and distribution audit. Done.
7. Phase M7: design support and diagnostics flow. Done.
8. Phase M8: implement offline signed license activation. Done.
9. Phase M9: prepare production license key management and release guardrails. Done.
10. Phase M10: add manual Pro license issuer for first paid sales. Done.
