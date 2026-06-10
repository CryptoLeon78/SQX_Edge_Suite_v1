# BS-AI1 BlockSettings Generator Contract

Marker: `bs-ai1-blocksettings-generator-contract-v1`

Status: `built_local_operator_overlay_ready_manual_install_gate`

Policy marker: official BlockSettings immutable in V1.

## Scope

BS-AI1 adds a local/operator-only BlockSettings generator for SQX144 Full. It combines a Flask-mediated backend, a sanitized BlockSettings catalog and an optional SQX144 overlay so the operator can ask for a custom BlockSetting candidate, save it under a separate namespace and generate a complete Capa1/Capa2 project pair for browser download.

The implementation is deliberately an overlay. It does not replace the official SQX BlockSettings library and it does not promote generated candidates into the official manifest.

## Versioning Contract

- Official `.sqb` files under `backend/sqx-edge-tool/resources/blocksettings/` are immutable for BS-AI1.
- Manifest truth remains `backend/sqx-edge-tool/config/blocksettings_manifest.json` with `version=2`.
- Capa1 methodology defaults stay on `_v6`, including the existing intraday variants where the resolver already selects them.
- Capa2 defaults stay on `BS_Filtros_v6` for `M5/M15/M30/H1/H4` and `BS_Filtros_v6_D1` for `D1`.
- Existing `BS_Filtros_v7_M5/M15/M30/H1/H4` resources remain compatibility/explicit-selection material. They are never the implicit Capa2 default.
- Marker: `BS_Filtros_v7_* only with explicitBaseCanonicalId`.
- BS-AI candidates live only under `.local/blocksettings_ai/candidates/`.
- Candidate names must use `BSAI_<Family>_L<layer>_<TF|ALL>_from_<BaseCanonicalId>_rNNN.sqb`.
- A candidate that tries to reuse an official `canonicalId` or official filename is blocked.

Every candidate records:

- `baseCanonicalId`
- `baseVariant`
- `baseSha256`
- `candidateRevision`
- `sourceVersionPolicy`
- `activeBlocks`
- `activeIndicators`
- `promotionState=local_candidate`

## Backend Contract

Core modules:

- `backend/sqx-edge-tool/core/blocksettings_ai_generator.py` owns catalog, sessions, recipe planning, local candidate `.sqb` creation and Capa1/Capa2 `.cfx` generation.
- `backend/sqx-edge-tool/core/blocksettings.py` continues to resolve official resources normally and accepts only approved local candidates through the internal override path.
- `backend/sqx-edge-tool/core/project_generator.py` can receive a `blocksetting_entry_override` for the BS-AI candidate layer without changing normal Project Generator resolution.

Local APIs:

- `GET /api/blocksettings/ai/catalog`
- `POST /api/blocksettings/ai/sessions`
- `POST /api/blocksettings/ai/sessions/<id>/plan`
- `POST /api/blocksettings/ai/sessions/<id>/save-candidate`
- `POST /api/blocksettings/ai/sessions/<id>/generate-project`
- `GET /api/blocksettings/ai/download/<artifact_id>`

Public responses must not include local paths, raw XML, provider secrets or raw prompt text. Browser payloads cannot choose `path`, `output`, `output_dir`, `dbPath`, `sqxRoot`, `fileName`, `template`, `template_capa1`, `template_capa2`, `templateCapa1` or `templateCapa2`.

## Overlay Contract

SQX144 overlay source:

- `integrations/sqx144/blocksettings_ai_overlay/sqx-edge-bsai.js`
- `integrations/sqx144/blocksettings_ai_overlay/sqx-edge-bsai.css`
- `tools/sqx144_blocksettings_ai_overlay.ps1`

The wrapper supports `status|plan|install|rollback`. Install is dry-run unless `-Apply` is passed, requires SQX closed, creates backup and injects only the overlay assets/HTML markers. It does not run SQX tasks and does not write `data.db`, `user/projects` or databanks.

## Output Contract

BS-AI1 creates a full Capa1/Capa2 `.cfx` pair in the backend output area and returns browser download URLs. It does not write automatically into SQX `user/projects`, does not patch SQX `data.db` and does not mutate databanks.

The candidate is injected only into the matching layer:

- Layer 1 candidate -> Capa1 uses `sourceScope=local_candidate`; Capa2 keeps the normal official Capa2 default.
- Layer 2 candidate -> Capa2 uses `sourceScope=local_candidate`; Capa1 keeps the normal official Capa1 resolver.

## Verification

Required checks:

- `python -m pytest backend\sqx-edge-tool\test_blocksettings.py -q`
- `python -m pytest backend\sqx-edge-tool\test_blocksettings_ai_generator.py -q`
- `python -m pytest backend\sqx-edge-tool\test_docs_state_consistency.py -q`
- `node tests\js\contracts\blocksettings_ai_overlay_contracts.mjs`

Acceptance:

- Official manifest hashes are unchanged after candidate generation.
- Candidate `.sqb` is a ZIP containing `config.xml`.
- H1 Capa2 without explicit selection resolves `BS_Filtros_v6`.
- D1 Capa2 without explicit selection resolves `BS_Filtros_v6_D1`.
- v7 filters require `explicitBaseCanonicalId`.
- Overlay contract stays local-only and does not call Ollama directly from SQX browser code.
