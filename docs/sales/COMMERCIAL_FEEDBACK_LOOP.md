# Commercial Feedback Loop

Este runbook transforma feedback de primeras ventas en decisiones de producto, precio y mensaje comercial.

## Requisitos

- `post_launch_control.py` en `GO`.
- Feedback clasificado en categorias primarias.
- Version de mejora planificada.
- Decision de precio.
- Decision de copy.
- Roadmap actualizado.
- Owner de release notes.

## Categorias

- `bugs`: defectos reales.
- `activation_friction`: problemas al activar licencia o arrancar app.
- `documentation_gap`: falta de instrucciones o FAQ.
- `feature_request`: mejoras pedidas.
- `pricing_objection`: objecion o duda sobre precio.
- `copy_confusion`: el comprador no entiende la promesa.
- `positive_signal`: senales de valor, ahorro de tiempo o satisfaccion.

## Dry Run

```powershell
python backend\sqx-edge-tool\tools\commercial_feedback_loop.py --allow-no-go-post-launch --no-write
```

Bloqueos esperados hasta tener feedback real:

- `post_launch_control_missing` o `post_launch_control_not_go`
- `feedback_counts_missing`
- `no_feedback_recorded`
- `planned_fix_version_missing`
- `feedback_not_reviewed`
- `roadmap_not_updated`
- `release_notes_owner_missing`

## Flujo Real

1. Clasificar cada feedback en una categoria principal.
2. Separar bugs severos y friccion de activacion antes de tocar precio o copy.
3. Elegir `pricing_decision`:
   - `keep_price`
   - `test_discount`
   - `raise_price_later`
   - `pause_pricing_change`
4. Elegir `copy_decision`:
   - `keep_copy`
   - `revise_copy`
   - `run_ab_test`
5. Elegir `next_action`:
   - `ship_fix`
   - `update_docs`
   - `revise_offer`
   - `continue_observing`
   - `pause_sales`
6. Ejecutar:

```powershell
python backend\sqx-edge-tool\tools\commercial_feedback_loop.py --use-latest-post-launch --bug-count 1 --activation-friction-count 1 --documentation-gap-count 2 --feature-request-count 3 --pricing-objection-count 0 --copy-confusion-count 1 --positive-signal-count 4 --severe-bug-count 0 --planned-fix-version "v1.0.1" --pricing-decision keep_price --copy-decision revise_copy --next-action update_docs --confirm-feedback-reviewed --confirm-roadmap-updated --release-notes-owner "Ivan"
```

## Reglas

- Bug severo exige `ship_fix`.
- Friccion de activacion exige `ship_fix` o `update_docs`.
- Objecion de precio bloquea `raise_price_later`.
- Confusion de copy bloquea `keep_copy`.
- No escalar mensaje ni precio sin roadmap actualizado.

No cambies precio por intuicion; cambia precio por evidencia.
