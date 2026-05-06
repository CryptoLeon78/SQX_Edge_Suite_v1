# Monetization M22 - Render API Preflight

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Dar el siguiente paso real hacia staging en Render sin crear recursos a ciegas: validar API key, workspace owner y blueprint antes del deploy.

## Entregables

- Estado `relay_render_api_preflight_ready`.
- Tool `backend/sqx-edge-relay/tools/render_api_preflight.py`.
- Variables staging ampliadas:
  - `RENDER_API_KEY`
  - `RENDER_OWNER_ID`
  - `SQX_RENDER_STAGING_BLUEPRINT`
- Guia `docs/sales/RENDER_API_PREFLIGHT.md`.
- Tests para bloqueo sin API key y validacion mock de blueprint.

## Decision

No se usa password de cuenta en scripts. El camino seguro es una API key de Render con permisos adecuados, guardada como variable local o secreta del entorno.

## Preflight

```powershell
python backend\sqx-edge-relay\tools\render_api_preflight.py
```

Sin `RENDER_API_KEY` y `RENDER_OWNER_ID`, devuelve bloqueo esperado.

Con ambas variables, valida:

- acceso a Render API,
- listado de servicios,
- blueprint staging por `/blueprints/validate`.

## Siguiente Paso

M23 deberia usar una API key real para validar el blueprint contra el workspace y, si sale GO, iniciar el deploy desde el Dashboard/Blueprint o desde API segun el plan elegido.
