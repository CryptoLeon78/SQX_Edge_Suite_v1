# Monetization M40 - Launch Assets Kit

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar el launch assets kit: capturas definitivas, copy corto/largo, README comercial, GitHub Release draft y checklist de publicacion.

## Entregables

- Estado `launch_assets_kit_ready`.
- Tool `backend/sqx-edge-tool/tools/launch_assets_kit.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-tool/data/launch_assets_kit`.
- Consumo de evidencia M39 `public_offer_pack`.
- Validacion de ZIP, SHA256, capturas desktop/mobile, copy corto/largo, README comercial, support macro y `github_release_draft`.
- Guia `docs/sales/LAUNCH_ASSETS_KIT.md`.

## Decision

M40 no declara `GO` sin ZIP final, SHA256 confirmado, capturas desktop/mobile, copy preparado, release draft y publication checklist.

## Uso

```powershell
python backend\sqx-edge-tool\tools\launch_assets_kit.py --use-latest-public-offer --confirm-short-copy --confirm-long-copy --confirm-commercial-readme --confirm-github-release-draft --confirm-support-macro --confirm-publication-checklist --confirm-zip-sha256
```

Revision seca:

```powershell
python backend\sqx-edge-tool\tools\launch_assets_kit.py --allow-no-go-offer --no-write
```

## Siguiente Paso

M41 debe preparar el public release gate: revisar GitHub Release, tag, ZIP, checksum, copy final, rollback y soporte antes de publicar.
