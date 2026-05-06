# Monetization M38 - Commercial Feedback Loop

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar el sistema de feedback comercial: clasificacion de incidencias, versionado de mejoras y decision de precio/copy antes de escalar mas.

## Entregables

- Estado `commercial_feedback_loop_ready`.
- Tool `backend/sqx-edge-tool/tools/commercial_feedback_loop.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-tool/data/commercial_feedback_loop`.
- Consumo de evidencia M37 `post_launch_control`.
- Clasificacion de feedback: bugs, activacion, documentacion, features, precio, copy y senales positivas.
- Decisiones `pricing_decision`, `copy_decision` y `next_action`.
- Guia `docs/sales/COMMERCIAL_FEEDBACK_LOOP.md`.

## Decision

M38 no permite cambiar precio, copy u oferta sin feedback revisado, roadmap actualizado, version planificada y owner de release notes.

## Uso

```powershell
python backend\sqx-edge-tool\tools\commercial_feedback_loop.py --use-latest-post-launch --bug-count 1 --activation-friction-count 1 --documentation-gap-count 2 --feature-request-count 3 --pricing-objection-count 0 --copy-confusion-count 1 --positive-signal-count 4 --severe-bug-count 0 --planned-fix-version "v1.0.1" --pricing-decision keep_price --copy-decision revise_copy --next-action update_docs --confirm-feedback-reviewed --confirm-roadmap-updated --release-notes-owner "Ivan"
```

Revision seca:

```powershell
python backend\sqx-edge-tool\tools\commercial_feedback_loop.py --allow-no-go-post-launch --no-write
```

## Siguiente Paso

M39 debe preparar la pagina/oferta publica controlada con copy revisado, FAQ comercial, pruebas sociales y un paquete de release notes legible para comprador basico.
