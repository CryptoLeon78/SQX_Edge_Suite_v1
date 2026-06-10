# Local Gbrain

Marker: `sqx-edge-local-gbrain-v1`
Status: `local_gbrain_primary_mem_optional_quota_safe`

## Purpose

`LOCAL_GBRAIN1` removes Mem/gbrain write quota as a project blocker.

The local gbrain is the first project memory layer for SQX Edge Suite when durable context is needed. It can index tracked Markdown docs, import pending `LOCAL_MEMORY_OUTBOX` notes, save local memory pages and answer `search`, `query` and `get-page` requests without external network access.

Mem remains useful as an optional mirror, but it is no longer a single point of failure for SQX Edge Suite continuity.

## Storage

- Local ignored DB: `.local/gbrain/local_gbrain.sqlite`
- Source outbox DB: `.local/memory_outbox/memory_outbox.sqlite`
- Version marker: `sqx-edge-local-gbrain-v1`
- Mode: `local_first_mem_optional`
- External network required: `false`
- External marker: `externalNetworkRequired=false`
- Privacy marker: `localPathsReturned=false`
- Tokens/license material returned: `tokensReturned=false`, `licenseMaterialReturned=false`

## Tooling

Core module:

- `backend/sqx-edge-tool/core/local_gbrain.py`

Wrapper:

- `tools/local_gbrain.ps1 status`
- `tools/local_gbrain.ps1 index`
- `tools/local_gbrain.ps1 import-outbox`
- `tools/local_gbrain.ps1 search -Query "..."`
- `tools/local_gbrain.ps1 query -Query "..."`
- `tools/local_gbrain.ps1 get-page -Slug "..."`
- `tools/local_gbrain.ps1 save-page -Title "..." -Content "..."`

The wrapper calls `core.local_gbrain` and supports `status|index|import-outbox|search|query|get-page|save-page`.

## Operating Contract

For project-memory lookups:

1. Run local gbrain search first.
2. Use local gbrain query/get-page when a relevant slug is found.
3. Use external Mem/gbrain search only as an optional supplement when available.
4. Use tracked governance docs as the final repo source of truth for phase/status conflicts.

For durable write-back:

1. Save durable decisions to local gbrain or enqueue through `LOCAL_MEMORY_OUTBOX`.
2. Import outbox notes into local gbrain with `tools/local_gbrain.ps1 import-outbox`.
3. Do not mark an outbox note synced until a real external Mem/gbrain write succeeds.
4. Do not use quota workarounds or duplicate external accounts to bypass service limits.

## LOCAL_MEMORY_OUTBOX Relationship

`LOCAL_MEMORY_OUTBOX` remains the pending-sync queue for notes intended for external Mem/gbrain.

`LOCAL_GBRAIN1` can import those pending notes into local searchable pages. Importing the outbox:

- does not call Mem;
- does not mark outbox notes as synced;
- does not expose local filesystem paths;
- does not store tokens or license material;
- keeps `.local` ignored and private.

## Bootstrap Commands

```powershell
tools\local_gbrain.ps1 index
tools\local_gbrain.ps1 import-outbox -Limit 200
tools\local_gbrain.ps1 status
```

Example lookup:

```powershell
tools\local_gbrain.ps1 search -Query "institutional origin espejo 79b1de36" -Limit 3
tools\local_gbrain.ps1 get-page -Slug "outbox/0036-sqx-edge-suite-remote-mirror-pr-checkpoint"
```

## Verification

Required checks for LOCAL_GBRAIN1:

```powershell
python -m pytest backend\sqx-edge-tool\test_local_gbrain.py -q
python -m pytest backend\sqx-edge-tool\test_docs_state_consistency.py -q
python -m json.tool docs\state_consistency_manifest.json
git diff --check
```

## Boundaries

- No SQX runtime launch.
- No SQX host mutation.
- No `data.db`, `user/projects`, databanks, tasks or Migration Tool.
- No external Mem write is required for local memory to work.
- No quota-bypass behavior is implemented or approved.
