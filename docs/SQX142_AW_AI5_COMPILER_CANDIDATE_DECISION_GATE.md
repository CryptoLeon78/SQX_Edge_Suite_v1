# SQX142-AW-AI5 Compiler Candidate Decision Gate

Estado: `candidate_selected_keltner_requires_fixture_ai6`.

Marcador: `sqx142-aw-ai5-compiler-candidate-decision-gate-v1`.

Fecha: `2026-06-04`.

AI5 es un gate de decision, no una fase de compilador. Cierra la seleccion de la siguiente familia candidata tras el roundtrip RSI confirmado, pero no desbloquea ningun draft nuevo ni cambia el comportamiento del AI Wizard.

## Decision

La siguiente candidata sera `Keltner Channel`, limitada a una fase posterior de fixture y contrato: `SQX142-AW-AI6 Keltner Fixture And Contract`.

Motivo:

- Keltner aparece en el catalogo semantico saneado con 12 condiciones detectadas y soporte actual `planning_only_not_draftable`.
- El AST ya puede reconocer la familia y mantenerla bloqueada con `blocked_not_draftable_yet`.
- No existe todavia fixture Keltner probado, contrato de AST cerrado, compilador ZIP verificado ni roundtrip manual.
- Los ejemplos `.sqx` inspeccionados no aportan feature IDs Keltner suficientes para promoverla directamente.

Resultado operativo: Keltner queda seleccionada para preparar evidencia en AI6, pero sigue plan-only en AI5.

## Evidencia Saneada

Inventario read-only del catalogo AI Wizard:

| Familia | Items semanticos | Estado AI5 |
| --- | ---: | --- |
| Keltner Channel | 12 | candidata AI6, plan-only |
| Bollinger Bands | 12 | plan-only |
| ADX | 8 | plan-only |
| Stochastic | 12 | plan-only |
| Directional Index | 12 | plan-only |
| Momentum | 8 | plan-only |

Contrato vigente:

- `draftablePatterns`: `ema_cross`, `candle_atr_sequence`, `rsi_mean_reversion`.
- Keltner/Bollinger/ADX/Stochastic no se anaden a `draftablePatterns`.
- Prompts multi-familia siguen bloqueados con `blocked_multi_family_compiler_not_ready` cuando mezclan una familia compilable con otra no probada.
- Familias entendidas pero sin compilador siguen con `blocked_not_draftable_yet`.

## Alcance AI6

AI6 solo podra empezar si el trabajo se mantiene como fixture/contrato antes de compilador:

- Capturar o construir un fixture Keltner public-safe y verificable.
- Definir una variante estrecha, por ejemplo Keltner mean-reversion o breakout, antes de tocar compilacion.
- Registrar AST esperado, parametros permitidos, direccion, SL/TP y condiciones exactas.
- Mantener `manualReviewRequired=true`.
- Preservar entradas ZIP y parchear solo `strategy_Portfolio.xml` si se llega a compilar.
- Verificar que Bollinger/ADX/Stochastic siguen plan-only.
- Requerir roundtrip manual en AlgoWizard antes de cerrar cualquier nuevo compilador.

## No-Go

- No activar `keltner_*` como patron draftable durante AI5.
- No usar Keltner como fallback para prompts ambiguos.
- No lanzar SQX runtime desde scripts.
- No escribir en `data.db`, `user/projects`, databanks ni settings vivos.
- No tocar licencias, activacion, bypass, jars, binarios ni internals.
- No publicar rutas locales, XML crudo, evidencias privadas, prompts raw, tokens, URLs protegidas ni material de licencia.
- No afirmar rentabilidad, riesgo cero ni calidad trading.

## Log

2026-06-04:

- entrada: AI4 cerrado por operador como `operator_manual_rsi_roundtrip_confirmed_ai4_closed`.
- accion: gate AI5 ejecutado como decision-only.
- evidencia: catalogo saneado con Keltner Channel detectado como familia semantica plan-only.
- decision: `candidate_selected_keltner_requires_fixture_ai6`.
- siguiente paso: `SQX142-AW-AI6 Keltner Fixture And Contract`.
