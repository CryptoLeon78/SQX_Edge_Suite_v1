# Public Release Gate

Esta compuerta evita publicar SQX Edge Suite sin las piezas minimas de una entrega profesional.

## Requisitos

- `launch_assets_kit.py` en `GO`.
- ZIP portable final.
- `release_tag` versionado.
- GitHub Release revisada.
- ZIP adjunto a la release.
- SHA256 publicado junto al ZIP.
- Checkout pausado o conscientemente listo.
- Soporte preparado.
- Rollback preparado con responsable.

## Dry Run

```powershell
python backend\sqx-edge-tool\tools\public_release_gate.py --allow-no-go-assets --no-write
```

Bloqueos esperados hasta preparar una salida real:

- `launch_assets_kit_missing` o `launch_assets_kit_not_go`
- `release_tag_missing`
- `release_draft_url_missing_or_not_https`
- `github_release_not_reviewed`
- `zip_not_attached`
- `sha256_not_published`
- `support_not_ready`
- `rollback_not_ready`

## Flujo Real

```powershell
python backend\sqx-edge-tool\tools\public_release_gate.py --use-latest-launch-assets --release-tag v1.0.0 --release-title "SQX Edge Suite v1.0.0" --release-draft-url https://github.com/CryptoLeon78/SQX_Edge_Suite_v1/releases/tag/v1.0.0 --rollback-owner "Ivan" --support-owner "Ivan" --confirm-github-release-reviewed --confirm-zip-attached --confirm-sha256-published --confirm-checkout-paused-or-ready --confirm-support-ready --confirm-rollback-ready
```

## Checklist

- Confirmar que el tag coincide con el ZIP final.
- Revisar titulo, copy, assets y buyer steps de GitHub Release.
- Adjuntar el ZIP portable final.
- Publicar el SHA256 del ZIP.
- Confirmar checkout pausado o intencionadamente listo.
- Confirmar inbox y macro de soporte.
- Confirmar rollback para pausar checkout, webhook, worker y fulfillment manual.

No publiques si no puedes pausar venta y soporte durante la ventana de lanzamiento.
