# Monetization M34 - Commercial Release Candidate

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar una release candidate comercial controlada, uniendo ZIP portable, SHA256, readiness M33, compra piloto y rollback antes de publicar venta abierta.

## Entregables

- Estado `commercial_release_candidate_ready`.
- Tool `backend/sqx-edge-tool/tools/commercial_release_candidate.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-tool/data/commercial_release_candidate`.
- Validacion de ZIP portable y `ZIP SHA256`.
- Consumo de evidencia M33 `checkout_live_readiness`.
- Bloqueo de public key de produccion placeholder.
- Confirmacion explicita de `pilot purchase`.
- Checklist de piloto y rollback.
- Guia `docs/sales/COMMERCIAL_RELEASE_CANDIDATE.md`.

## Decision

M34 no declara lista la venta publica si faltan URLs reales, readiness `GO`, clave publica final, ZIP portable o compra piloto confirmada.

## Uso

```powershell
python backend\sqx-edge-tool\tools\commercial_release_candidate.py --use-latest-readiness --zip dist\SQX_Edge_Tool_Portable_YYYYMMDD_HHMMSS.zip --pilot-purchase-confirmed
```

Revision seca:

```powershell
python backend\sqx-edge-tool\tools\commercial_release_candidate.py --allow-no-go-readiness --no-write
```

## Siguiente Paso

M35 debe preparar la compra piloto real: actualizar URLs/variant IDs, ejecutar checkout privado y emitir una licencia Pro verificable en la app.
