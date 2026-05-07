# Modularization Next Steps

Persistent planning note for the next SQX Edge phases.

## Current Status

- Last updated: 2026-05-07.
- Current completed phase: M60 - Template Pack 2 Controlled Publication.
- Current product/commercial state: `template_pack_2_controlled_publication_ready`.
- Governance baseline: G2 - Governance Lookup Before Work.
- Last synced base commit before M60: `eb5100b`.
- Latest verified portable ZIP before M47: `dist/SQX_Edge_Tool_Portable_20260507_075847.zip`.
- Latest ZIP SHA256: `FE573CADCB79E2D93E1D1491BADC35DF0295C37DD08017AF3A9C784581E47E09`.
- Next recommended phase: M61 - Template Pack 2 Controlled Purchase Drill.

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

- Before every work phase/message, consult `docs/PROJECT_GOVERNANCE.md` or the Specialist Agents ownership matrix and state the active ownership/checks.
- Create a backup before changing files.
- Verify with JS contracts, Python tests, and E2E screenshots when frontend behavior is touched.
- Remove temporary Playwright dependencies after E2E.
- Use one commit per phase.
- Push only when explicitly requested or when the active instruction includes continuing the planned push step.
- Declare active specialist ownership before broad phases.
- Use prefixed phase IDs for new work: `Mxx`, `Axx`, `Rxx`, `Sxx`, `Qxx`, `Gxx`.
- Follow `docs/PROJECT_GOVERNANCE.md` for phase workflow and M46 entry criteria.

## Governance Track

1. Phase G1: define specialist agent ownership, phase namespaces, workflow and M46 entry criteria. Done.
2. Phase G2: require governance/ownership lookup before each work phase/message. Done.

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
39. Phase M39: add public offer pack for controlled offer copy, FAQ, release notes and buyer steps. Done.
40. Phase M40: add launch assets kit for screenshots, copy, release draft and publication checklist. Done.
41. Phase M41: add public release gate for tag, GitHub Release, ZIP, SHA256, support and rollback. Done.
42. Phase M42: add release publication record for published tag, release, ZIP, SHA256 and rollback evidence. Done.
43. Phase M43: add post-release monitor for incidents, activation errors, support, refunds and scale decision. Done.
44. Phase M44: add hotfix/rollback release kit for action owner, notes, comms, verification and closure evidence. Done.
45. Phase M45: add customer success and renewal loop for Pro onboarding, support outcomes, retention decisions and upsell evidence. Done.
46. Phase M46: add a lightweight commercial customer cockpit for renewals, support state, template opportunities and customer success decisions. Done.
47. Phase M47: prepare real Pro buyer data and templates with safe CSV import, asset universe, activation, support and first-value material. Done.
48. Phase M48: add a basic buyer onboarding and support gate for purchase, install, license activation, FAQ, support macro and refund/pause criteria. Done.
49. Phase M49: package Template Pack 1 as a controlled add-on with sample profiles, safe claims, delivery checklist and support boundaries. Done.
50. Phase M50: prepare public add-on offer, checkout variant wiring and delivery macro for Template Pack 1. Done.
51. Phase M51: connect real checkout URL, variant ID and support email through a controlled publication gate. Done.
52. Phase M52: run a controlled Template Pack 1 purchase drill and validate delivery/support evidence. Done.
53. Phase M53: execute post-purchase handoff, support follow-up and scale/pause decision. Done.
54. Phase M54: consolidate a lightweight add-on sales register before wider public traffic. Done.
55. Phase M55: review the add-on buyer cohort and real feedback before expanding traffic or building Template Pack 2. Done.
56. Phase M56: turn feedback into an offer iteration or Template Pack 2 action plan. Done.
57. Phase M57: execute the selected action plan as Template Pack 2 initial specs with scope, assets, support, delivery and next phase. Done.
58. Phase M58: create Template Pack 2 initial assets from the specs gate. Done.
59. Phase M59: prepare Template Pack 2 offer pack with public copy, FAQ, checkout draft, delivery macro and support macro. Done.
60. Phase M60: prepare controlled Template Pack 2 publication with live checkout URL, support, rollback and purchase drill. Done.
61. Phase M61: execute Template Pack 2 controlled purchase drill with redacted payment, delivery, support and refund/pause evidence. Recommended next.
