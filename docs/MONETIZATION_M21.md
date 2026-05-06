# Monetization M21 - Render Staging Execution Readiness

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Convertir el staging del relay en una ejecucion auditable con proveedor recomendado, evidencia go/no-go y bloqueo explicito cuando falte URL real.

## Proveedor Recomendado

Proveedor recomendado para el primer staging: Render.

Motivos:

- soporta servicios Docker,
- permite `healthCheckPath`,
- permite background workers,
- encaja con el Blueprint ya versionado,
- reduce friccion frente a VPS para una primera validacion.

## Entregables

- Estado `relay_staging_execution_ready`.
- `backend/sqx-edge-relay/deploy/render.staging.yaml.example`.
- `backend/sqx-edge-relay/tools/staging_evidence.py`.
- Guia `docs/sales/RELAY_RENDER_STAGING_RUNBOOK.md`.
- Decision go/no-go en JSON y Markdown.

## Regla De Rigor

Sin `SQX_RELAY_STAGING_BASE_URL` real, M21 no puede declarar GO. La herramienta debe devolver NO-GO con blocker `remote_staging_url_not_tested`.

## Evidencia Esperada

La evidencia debe contener:

- preflight local,
- smoke remoto,
- webhook demo firmado,
- snapshot,
- decision GO/NO-GO,
- blockers y warnings.

## Siguiente Paso

M22 deberia ejecutar el staging real en Render, configurar secretos de prueba y adjuntar evidencia generada por `staging_evidence.py`.
