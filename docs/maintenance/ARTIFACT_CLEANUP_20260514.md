# Artifact Cleanup 2026-05-14

## Scope

Mini fase de limpieza local para reducir espacio sin tocar codigo fuente, documentos de producto, paquetes `dist`, licencias privadas ni material comercial privado.

## Criterio aplicado

- Conservar el repositorio versionado como fuente de verdad.
- Conservar el paquete portable actual en `dist/`.
- Conservar material privado/licencias: `private-commercial/`, `commercial-private/`, `license_keys/`, `licenses_private/`.
- Eliminar solo artefactos regenerables: caches, capturas E2E, salidas temporales y backups antiguos.
- Mantener los dos backups mas recientes en `backups/` y registrar el manifiesto previo en un backup local ligero.

## Elementos limpiados

- `.pytest_cache/`
- `output/`
- `analysis_output/`
- Backups antiguos en `backups/`, manteniendo:
  - `cleanup-artifact-prune-20260514-000057`
  - `ux-tma1-template-maker-selected-delete-prechange-20260513-234650`
  - `ux-tma1-template-maker-step5-full-reset-prechange-20260513-233216`

## Verificacion

- `git diff --check`
- `npm run test:js`
- `python -m pytest backend\sqx-edge-tool -q`

E2E completo no se ejecuta en esta mini fase porque la limpieza borra capturas generadas y no modifica comportamiento UI.
