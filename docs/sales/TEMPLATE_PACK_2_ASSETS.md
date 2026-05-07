# Template Pack 2 Assets

## Objetivo

Template Pack 2 convierte las specs M57 en un primer set de recursos vendibles para usuarios Pro: perfiles editables, presets CSV y checklists de entrega.

## Comando de validacion

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_2_assets.py --use-latest-specs --confirm-specs-go --confirm-asset-files-present --confirm-profile-schema-validated --confirm-preset-csv-validated --confirm-support-boundaries-included --confirm-safe-claims-reviewed --confirm-addon-delivery-separate --no-write
```

## Empaquetado add-on

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_2_assets.py --use-latest-specs --confirm-specs-go --confirm-asset-files-present --confirm-profile-schema-validated --confirm-preset-csv-validated --confirm-support-boundaries-included --confirm-safe-claims-reviewed --confirm-addon-delivery-separate --package
```

## Estado

- Estado: Done.
- State: `template_pack_2_assets_ready`.
- Tool: `template_pack_2_assets.py`.
- Resource dir: `resources/pro-template-pack-2`.
- Next phase: `M59_template_pack_2_offer_pack`.

## Guardrails

- El pack se entrega como ZIP add-on separado.
- No viaja dentro del ZIP portable principal.
- No contiene licencias, claves privadas, payloads de checkout ni eventos crudos.
- No promete resultados financieros.
