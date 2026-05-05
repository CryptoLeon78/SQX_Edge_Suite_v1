# Modularization Next Steps

Persistent planning note for the next SQX Edge phases.

## Recommended Order

1. Phase 36: harden Project Generator module boundaries. Done.
2. Phase 37: split the remaining `main.js` orchestration into focused files. Done.
3. Phase 38: add more granular contracts per frontend submodule.
4. Phase 39: regenerate and test the portable ZIP after modularization.
5. Phase 40: document the final architecture map and load order.

## Working Discipline

- Create a backup before changing files.
- Verify with JS contracts, Python tests, and E2E screenshots when frontend behavior is touched.
- Remove temporary Playwright dependencies after E2E.
- Use one commit per phase.
- Push only when explicitly requested or when the active instruction includes continuing the planned push step.
