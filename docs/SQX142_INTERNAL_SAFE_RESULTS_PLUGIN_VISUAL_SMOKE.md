# SQX142-INTERNAL-SAFE3 Results Plugin Manual Visual Smoke

Estado: `blocked_plugin_not_listed_in_results`.

Este bloque abrio SQX 142 para confirmar manualmente si `SQX Edge Readiness Panel` aparece dentro de Results tras la instalacion SAFE2. La observacion del operador fue clara: `No se ve: no aparece en Results`.

## Evidencia

- SQX 142 abierto durante el smoke: si.
- Build observado en shell local: `142.2336`.
- Evidencia local ignorada: `.local/sqx142_internal_safe/sqx142_internal_safe3_results_plugin_manual_visual_smoke_20260526_214000.json`.
- Snapshot web local: `.local/sqx142_internal_safe/sqx142_internal_safe3_localhost_shell_20260526_214000.json`.
- Plugin instalado sigue presente en `SQX142_ROOT/user/extend/ResultsPlugins/SQX Edge Readiness Panel`.
- Hashes fuente/instalado siguen coincidiendo:
  - `index.html`: `DACE1D0A26A0B013C60A19668C25158FAE0D28D554325821B856073994BFB3F0`
  - `fixtures/fixtures.js`: `365045FA198DF8B246DE766652EACE54142772F05E522ED0877A7ADCF19A98DB`

## Diagnostico

El fallo no es de render del HTML: SAFE2 ya paso smoke offline sobre el HTML instalado. El fallo es de descubrimiento/listado dentro de la UI de SQX 142.

Hallazgo local saneado:

- `user/extend/ResultsPlugins` contiene `Source Code Translator` y `SQX Edge Readiness Panel`.
- `SQX Edge Readiness Panel` no aparece en Results.
- La instalacion local tiene una integracion estatica visible para `Source Code Translator` en `internal/web/common/templates.html`.
- No se encontro evidencia de que SQX 142 liste dinamicamente todos los folders de `user/extend/ResultsPlugins` como paneles visibles.

Conclusion: SQX142 necesita una fase separada para registrar visualmente el panel en una superficie UI real. Ese registro ya no es un simple "copiar plugin HTML"; requiere una decision explicita de parche UI con backup y rollback.

## Limites Mantenidos

- No se ejecuto ningun retest.
- No se abrio ni modifico ningun proyecto desde Codex.
- No se escribio en `data.db`, databanks vivos ni `user/projects`.
- No se tocaron motor, binarios, jars, licencia ni activacion.
- No se uso `run_project`, importacion MT5 directa ni Migration Tool.

## Siguiente Decision Recomendada

`SQX142-INTERNAL-SAFE4 Static UI Registration Spike`.

Objetivo propuesto: con SQX cerrado, hacer backup/hash de la plantilla UI exacta que controla la superficie Results o una superficie equivalente ya visible, insertar una entrada minima para `SQX Edge Readiness Panel`, verificar en localhost y reabrir SQX para confirmar visualmente. Si no hay superficie estable sin tocar motor/binarios/jars, SAFE4 debe cerrar como no-go y dejar el plugin instalado solo como artefacto offline/externo.
