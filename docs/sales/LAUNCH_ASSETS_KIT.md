# Launch Assets Kit

Este runbook agrupa los activos necesarios antes de publicar una oferta o release visible.

## Requisitos

- `public_offer_pack.py` en `GO`.
- ZIP portable final.
- SHA256 confirmado.
- Capturas desktop y mobile.
- Copy corto.
- Copy largo.
- README comercial revisado.
- Draft de GitHub Release.
- Macro de soporte.
- publication checklist completada.

## Activos Obligatorios

- `portable_zip`
- `zip_sha256`
- `desktop_screenshots`
- `mobile_screenshots`
- `short_copy`
- `long_copy`
- `commercial_readme`
- `github_release_draft`
- `support_macro`
- `publication_checklist`

## Dry Run

```powershell
python backend\sqx-edge-tool\tools\launch_assets_kit.py --allow-no-go-offer --no-write
```

Bloqueos esperados hasta tener activos finales:

- `public_offer_pack_missing` o `public_offer_pack_not_go`
- `zip_sha256_not_confirmed`
- `desktop_screenshot_missing`
- `mobile_screenshot_missing`
- `short_copy_not_ready`
- `long_copy_not_ready`
- `commercial_readme_not_ready`
- `github_release_draft_not_ready`
- `support_macro_not_ready`
- `publication_checklist_not_ready`

## Flujo Real

```powershell
python backend\sqx-edge-tool\tools\launch_assets_kit.py --use-latest-public-offer --confirm-short-copy --confirm-long-copy --confirm-commercial-readme --confirm-github-release-draft --confirm-support-macro --confirm-publication-checklist --confirm-zip-sha256
```

## publication checklist

- Adjuntar ZIP portable final y SHA256.
- Incluir copy corto y largo.
- Incluir capturas desktop y mobile.
- Incluir buyer steps y ruta de soporte.
- Enlazar README comercial y release notes.
- Confirmar checkout y support inbox antes de publicar.
- Mantener rollback owner disponible durante la ventana de publicacion.

No publiques una release visible si no puedes responder rapidamente a una instalacion fallida.
