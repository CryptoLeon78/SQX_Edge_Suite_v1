# Monetization M41 - Public Release Gate

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar la compuerta final antes de publicar una release visible: tag, GitHub Release, ZIP, SHA256, soporte y rollback.

## Entregables

- Estado `public_release_gate_ready`.
- Tool `backend/sqx-edge-tool/tools/public_release_gate.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-tool/data/public_release_gate`.
- Consumo de evidencia M40 `launch_assets_kit`.
- Validacion de `release_tag`, titulo, URL HTTPS de GitHub Release, ZIP adjunto, SHA256 publicado, checkout confirmado, soporte y rollback.
- Guia `docs/sales/PUBLIC_RELEASE_GATE.md`.

## Decision

M41 no declara `GO` sin release revisada, ZIP adjunto, checksum publicado, soporte preparado y rollback con owner claro.

## Uso

```powershell
python backend\sqx-edge-tool\tools\public_release_gate.py --use-latest-launch-assets --release-tag v1.0.0 --release-title "SQX Edge Suite v1.0.0" --release-draft-url https://github.com/CryptoLeon78/SQX_Edge_Suite_v1/releases/tag/v1.0.0 --rollback-owner "Ivan" --support-owner "Ivan" --confirm-github-release-reviewed --confirm-zip-attached --confirm-sha256-published --confirm-checkout-paused-or-ready --confirm-support-ready --confirm-rollback-ready
```

Revision seca:

```powershell
python backend\sqx-edge-tool\tools\public_release_gate.py --allow-no-go-assets --no-write
```

## Siguiente Paso

M42 debe convertir una compuerta `GO` en publicacion real controlada: crear tag/release final, adjuntar ZIP/SHA256 y registrar evidencia post-publicacion.
