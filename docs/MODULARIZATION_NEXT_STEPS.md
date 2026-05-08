# Modularization Next Steps

Persistent planning note for the next SQX Edge phases.

## Current Status

- Last updated: 2026-05-08.
- Current completed phase: R45 - controlled publication plan prepared for the verified portable ZIP without publishing a GitHub Release.
- Current product/commercial state: `controlled_traffic_expansion_review_ready`.
- Governance baseline: G2 - Governance Lookup Before Work.
- Last synced base commit before S2/M-pre: `cc8dbf0`.
- Latest verified portable ZIP: `dist/SQX_Edge_Tool_Portable_20260508_201652.zip`.
- Latest ZIP SHA256: `2725D2FC7CB9FD6E05AFDF1C7E20772B629BFBE8BE98532D4F5622A08628116E`.
- Next recommended phase: J3 - add OOS block parsing and stability scoring with contracts, R46 - publish the verified GitHub Release only with explicit approval, PG7 - Project Generator buyer-specific `.cfx` handoff notes, V10 - SQX Views pack comparison, or SB1 - Strategy Builder discovery.

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

## Project Generator Track

1. Phase PG1: add Custom Libre generation outside the plan mining while preserving plan-based bulk generation. Done.
2. Phase PG2: add reusable local custom presets for frequent buyer assets/timeframes. Done.
3. Phase PG3: add portable export/import JSON packs for custom preset portability between installations. Done.
4. Phase PG4: add starter custom preset examples by asset/timeframe profile with load/save/export flow. Done.
5. Phase PG5: add richer custom profile families or buyer-specific `.cfx` starter guidance if Project Generator continues. Done.
6. Phase PG6: add buyer-specific `.cfx` handoff notes or Project Generator pack import preview if this track continues. Done.
7. Phase PG7: add buyer-specific `.cfx` handoff notes if this track continues.

## Working Discipline

- Before every work phase/message, consult `docs/PROJECT_GOVERNANCE.md` or the Specialist Agents ownership matrix and state the active ownership/checks.
- Create a backup before changing files.
- Verify with JS contracts, Python tests, and E2E screenshots when frontend behavior is touched.
- Remove temporary Playwright dependencies after E2E.
- Use one commit per phase.
- Push immediately after every successful commit unless the user explicitly asks to hold the push or the remote is unavailable.
- Declare active specialist ownership before broad phases.
- Use prefixed phase IDs for new work: `Mxx`, `Axx`, `Rxx`, `Sxx`, `Qxx`, `Gxx`.
- Use `Vxx` for SQX view/template generation and StrategyQuant operator tools.
- Follow `docs/PROJECT_GOVERNANCE.md` for phase workflow and M46 entry criteria.

## Governance Track

1. Phase G1: define specialist agent ownership, phase namespaces, workflow and M46 entry criteria. Done.
2. Phase G2: require governance/ownership lookup before each work phase/message. Done.

## Architecture / External Comparison Track

1. Phase A47: compare Jose Livan's `sqx-edge-pipeline` repo and integrate a first-party Plan Quality Advisor. Done.
2. Phase A48: recover valuable HTML-side capabilities as native UI: local state backup/restore, dynamic Plan v2 summary and a locked Priority multi-TF placeholder, explicitly excluding Top Picks and Matrix. Done.
3. Phase A49: convert multi-timeframe analytical scoring into a controlled, dependency-isolated backend tool that consumes supplied metric JSON files and emits TF scores plus weighted consensus. Done.
4. Phase A50: connect multi-timeframe consensus to plan review without changing the dashboard UI until real metrics are available. Done.
5. Phase A51: add a multi-timeframe metric gate for supplied `asset_metrics[_TF].json` folders before exposing or using them as first-party evidence. Done.
6. Phase A52: implement a first-party H1 metric source from existing dashboard scores, write provenance and validate it through the A51 gate without synthetic lower/higher TFs. Done.
7. Phase A53: add a controlled intake gate for real H1/M30/M15/H4 metric folders, with first-party H1 support and strict blocking for missing synthetic lower/higher TFs. Done.
8. Phase A54: connect a validated full multi-timeframe source to Plan Quality Advisor artifacts only after A53 returns GO, otherwise write a blocked NO-GO report. Done.
9. Phase A55: add an OHLC CSV metric builder that converts reviewable market CSVs into `asset_metrics[_TF].json` without synthetic timeframes. Done.
10. Phase A56: add an end-to-end real-data pipeline runner for OHLC CSV -> metrics -> intake -> guarded plan artifacts, returning GO only when every stage passes. Done.
11. Phase A57: expose read-only MTF evidence in dashboard only after A56 returns GO with real data. Done.
12. Phase A58: add an internal MT5/Dukascopy OHLC download gate that writes real CSVs for A55/A56 and stays excluded from buyer portable builds. Done.
13. Phase A59: run the first local A58 smoke against Dukascopy MT5 and record NO-GO if terminal/API readiness blocks real data. Done; see `docs/A59_REAL_DATA_VALIDATION.md`.
14. Phase A60: add active-terminal MT5 initialization mode, retry the smoke against the already-open terminal and record NO-GO if IPC still times out. Done; see `docs/A60_MT5_ACTIVE_TERMINAL_MODE.md`.
15. Phase A61: add a repeatable MT5 IPC diagnostic that records environment, process state and init variants before any full OHLC download. Done; see `docs/A61_MT5_IPC_DIAGNOSTIC.md`.
16. Phase A62: add controlled recent-bars download mode, align the MT5 symbol map to the product manifest universe, produce `EURUSD_H1.csv`, download the full configured OHLC universe and validate A56 GO. Done; see `docs/A62_RECENT_BARS_REAL_MTF_GO.md`.
17. Phase A63/R44: refresh the portable/release story after real A56 GO while keeping OHLC data, `analysis_output/` evidence and internal MT5 tools out of buyer builds. Done; see `docs/R44_A63_PORTABLE_AFTER_REAL_MTF_GO.md`.

## Champion vs Challenger Track

1. Phase J1: document the Champion vs Challenger integration contract from Jose's latest HTML work, including input schemas, aliases, parsing, scoring, OOS evidence, security boundaries and tests. Done; see `docs/J1_CHAMPION_CHALLENGER_CONTRACT.md`.
2. Phase J2: implement the pure parser, alias resolver and formal comparison core with contracts, without dashboard UI. Done; see `docs/J2_CHAMPION_CHALLENGER_CORE.md`.
3. Phase J3: add OOS block parsing and stability scoring with contracts.
4. Phase J4: add native dashboard UI using the current SQX module architecture and visual system, without restoring removed Top Picks or Matrix surfaces.
5. Phase J5: add regime/EGT evidence through first-party historical-data adapters.
6. Phase J6: add export and future Strategy Builder handoff.

## Strategy Builder / Only One Platform Track

1. Phase SB1: discover the minimum viable Strategy Builder scope as a commercial "only one platform" hook, starting from existing SQX indicators, project presets and strategy cleaner outputs.
2. Phase SB2: design a controlled Builder flow that creates a strategy idea/package without bypassing StrategyQuant validation.
3. Phase SB3: prototype read-only previews and export handoff artifacts before any live generation feature is offered to buyers.

## QA / Security Track

1. Phase Q1: add GitHub Actions baseline plus root development requirements for Python tests and JS contracts. Done.
2. Phase S1: define private commercial repository boundary, manifest and ignored local staging paths. Done.
3. Phase S2/M-pre: prepare private commercial docs split with export tool, SHA256 migration index and public traceability plan. Done.
4. Phase S3/M-pre: initialize the ignored private commercial export as a local git repository with publication and security instructions. Done.
5. Phase S4/M-pre: create the private GitHub repository and push private export commit `ed79719`. Done.
6. Phase S5/M-pre: replace public sensitive commercial docs and Pro resource packs with traceability pointers. Done.

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
61. Phase M61: execute Template Pack 2 controlled purchase drill with redacted payment, delivery, support and refund/pause evidence. Done.
62. Phase M62: prepare Template Pack 2 post-purchase handoff, first-value support and scale/pause decision. Done.
63. Phase M63: consolidate Template Pack 2 sales register and early cohort tracking before more traffic. Done.
64. Phase M64: review Template Pack 2 early buyer feedback, support signals, refunds and scale decision. Done.
65. Phase M65: close buyer-ready checkout, release, support and delivery readiness for controlled first sales. Done.
66. Phase M66: prepare public buyer page checklist and a calm first-sale operating cadence. Done.
67. Phase M67: prepare first controlled buyer operating log and lightweight post-sale review. Done.
68. Phase M68: prepare a small post-sale improvement loop for onboarding, support macros and public copy. Done.
69. Phase M69: apply approved buyer-facing micro-updates and prepare the next controlled buyer readiness check. Done.
70. Phase M70: run the next controlled buyer readiness check before sharing another private checkout link. Done.
71. Phase M71: record the next controlled buyer outcome and decide repeat, pause or carefully widen. Done.
72. Phase M72: execute the selected outcome decision with a tiny, reversible distribution step. Done.
73. Phase M73: review controlled distribution evidence and choose repeat, hold, pause or prepare the next buyer-facing asset. Done.
74. Phase M74: prepare the next buyer-facing asset if M73 selects it, or route to repeat/hold/pause. Done.
75. Phase M75: privately review the prepared buyer-facing asset before publication or traffic. Done.
76. Phase M76: prepare a controlled publication gate only if M75 selects it. Done.
77. Phase M77: prepare a limited publication draft only if M76 selects it. Done.
78. Phase M78: review the limited publication draft before any manual publication. Done.
79. Phase M79: record a manual limited publication only if M78 approves. Done.
80. Phase M80: monitor the manual limited publication before any traffic expansion. Done.
81. Phase M81: review controlled traffic expansion only if M80 selects it. Done.
82. Phase M82: execute one tiny reversible traffic expansion step only if M81 approves it. Recommended next.

## SQX View Creator Track

1. Phase V1: integrate the annual SQX `.vw` creator as a native dashboard tab with EGT Core preset, XML preview and portable download. Done.
2. Phase V2: add saved view presets and reusable operator templates in localStorage. Done.
3. Phase V3: add JSON export/import packs for saved SQX Views presets. Done.
4. Phase V4: add optional handoff links from Workflow/Estrategias and richer saved-template guidance. Done.
5. Phase V5: close the native SQX View Creator integration, archive the staging prototype in backup and remove the local staging folder. Done.
6. Phase V6: add buyer-ready SQX View template examples for first review, robustness, risk and full audit, with load/save/export flow. Done.
7. Phase V7: expand SQX Views packs by buyer profile, asset family or validation workflow if the View Creator track continues. Done.
8. Phase V8: add asset-family or validation-workflow packs if SQX Views continues. Done.
9. Phase V9: add SQX Views import preview or pack comparison if this track continues. Done.
10. Phase V10: add SQX Views pack comparison if this track continues.

## Release Track

1. Phase R40: regenerate and test the portable ZIP after V6/PG3 because frontend behavior and dev tooling changed. Done.
2. Phase R41: regenerate and test the portable ZIP after PG4 because frontend behavior changed. Done.
3. Phase R42: regenerate and validate a fresh portable release candidate after V9. Done.
4. Phase R43: prepare a public GitHub Release record only when we decide to publish the verified ZIP.
5. Phase R44: regenerate and validate the portable ZIP after real A56 GO, with broad generated-evidence exclusions. Done; see `docs/R44_A63_PORTABLE_AFTER_REAL_MTF_GO.md`.
6. Phase R45: prepare a controlled GitHub Release/publication plan for the verified ZIP without publishing it. Done; see `docs/R45_CONTROLLED_PUBLICATION_PLAN.md`.
7. Phase R46: publish the verified GitHub Release only with explicit approval, then run `release_publication_record.py`.
