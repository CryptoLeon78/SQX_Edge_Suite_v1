# Private Commercial Documents Boundary

SQX Edge keeps the public repository useful for buyers, contributors and releases, while sensitive commercial operations must move to a private repository before wider distribution.

## Recommended Target

- Target: private GitHub repository owned by the operator.
- Public repo keeps: README, public roadmap, architecture map, safe claims, user-facing setup, release notes and non-sensitive feature documentation.
- Private repo keeps: buyer logs, commercial gates, pricing experiments, support scripts, checkout evidence, launch operations, internal go/no-go records and sales playbooks.

## Why A Private Repo

A protected branch is still inside the public project boundary and is easy to expose accidentally through merges, releases or local packaging. A separate private repository creates a clearer operational line for sales material and customer operations.

## Migration Rules

1. Create the private repository before deleting or moving public files.
2. Copy sensitive files listed in `docs/private_commercial_manifest.json` into the private repository.
3. Replace public files with short redacted pointers only when the private copy has been verified.
4. Keep public buyer-facing docs claim-safe and free of customer, checkout, support or revenue evidence.
5. Treat existing public Git history as already exposed. If a document contained real secrets or personal data, rotate the secret and handle history cleanup separately.

## Local Private Workspace

The following paths are ignored and can be used as a temporary local staging area:

- `docs/private-commercial/`
- `commercial-private/`
- `private-commercial/`

Do not package these folders into the portable ZIP and do not attach them to public releases.

## Prepared Export

Use the prepared export tool before creating redacted public pointers:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\private_commercial_split.py
```

The tool copies the sensitive commercial source set into `commercial-private/sqx-edge-commercial-private/` and writes `MIGRATION_INDEX.json` plus `MIGRATION_INDEX.md` with SHA256 hashes. Public files remain in place until the private repository copy is verified.
