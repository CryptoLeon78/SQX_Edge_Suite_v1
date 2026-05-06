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
11. Phase M11: prepare checkout wiring and manual sales fulfillment. Done.
12. Phase M12: prepare local webhook-to-fulfillment automation bridge. Done.
13. Phase M13: add private receiver with persistent queue and deduplication. Done.
14. Phase M14: add operator states, retries and dashboard queue cockpit. Done.
15. Phase M15: add trusted relay ingest for remote webhook forwarding. Done.
16. Phase M16: add deployable remote relay service with queue and dispatch. Done.
17. Phase M17: harden relay deployment with config checks, operator token and worker. Done.
18. Phase M18: add relay observability, snapshots and simulated purchase flow. Done.
19. Phase M19: prepare production relay deployment package and provider runbook. Done.
20. Phase M20: add relay staging validation kit and go/no-go checklist. Done.
21. Phase M21: choose Render staging path and add evidence go/no-go collector. Done.
22. Phase M22: add Render API preflight for key, owner and blueprint validation. Done.
23. Phase M23: add Render credential handshake and no-password guardrail. Done.
24. Phase M24: add Render staging go/no-go gate before live deployment. Done.
25. Phase M25: add Render staging launch pack for audited manual deployment. Done.
26. Phase M26: add Render staging secrets kit for safe provider setup. Done.
27. Phase M27: add local ingest tunnel readiness check before Render staging. Done.
28. Phase M28: add local ingest tunnel launcher and provider detection. Done.
29. Phase M29: add local ingest staging session orchestrator. Done.
30. Phase M30: add local ingest Render handoff pack. Done.
31. Phase M31: add Render staging apply gate for handoff confirmation and remote gate evidence. Done.
32. Phase M32: add Render staging purchase drill for webhook, queue and dispatch evidence. Done.
33. Phase M33: add checkout live readiness gate for Lemon Squeezy URLs, variants and rollback. Done.
34. Phase M34: add commercial release candidate gate for ZIP, readiness, pilot purchase and rollback evidence. Done.
35. Phase M35: add pilot purchase kit for private checkout, license issue, delivery and import evidence. Done.
36. Phase M36: add limited public launch gate for first sale cap, support, checkout and rollback evidence. Done.
37. Phase M37: add post-launch control for sales, activations, support, refunds and scale decision evidence. Done.
38. Phase M38: add commercial feedback loop for issue classification, pricing, copy and version decisions. Done.
