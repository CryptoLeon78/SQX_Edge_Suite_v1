# Render API Preflight

## Why This Exists

M22 avoids creating staging resources blindly. It verifies that the Render account, workspace and blueprint are ready before pressing deploy.

## Required Variables

- `RENDER_API_KEY`
- `RENDER_OWNER_ID`
- `SQX_RENDER_STAGING_BLUEPRINT`

Do not use or store the Render account password in scripts.

## How To Get Values

1. Render API key: Render Dashboard -> Account Settings -> API Keys.
2. Owner/workspace ID: Render Dashboard -> Workspace Settings.
3. Blueprint path:
   `backend/sqx-edge-relay/deploy/render.staging.yaml.example`

## Command

```powershell
python backend\sqx-edge-relay\tools\render_api_preflight.py
```

Expected before secrets are configured:

- `render_api_key_missing`
- `render_owner_id_missing`

Expected with credentials:

- API list services returns OK.
- Blueprint validation returns `valid: true`.

## What This Does Not Do

- It does not create services.
- It does not deploy.
- It does not persist API keys.
- It does not write secrets to the repo.

## Go Criteria

- `ok: true`
- no blockers
- blueprint validation response is valid
- staging secrets are ready for the Render Blueprint prompt

## Next Action

After GO, create the Render Blueprint from the dashboard or API, then run:

```powershell
python backend\sqx-edge-relay\tools\staging_evidence.py --provider render --base-url <RENDER_STAGING_URL> --send-webhook
```
