# SQX144 Results Plugin Install Gate

Estado: `SQX144-COMPAT5 Results Plugin Install Gate` completado como decision gate local-only, sin instalacion ejecutada.

Este gate decide si el prototipo `SQX Edge Readiness Panel` puede pasar de prototipo offline a instalacion manual en un SQX 144 lab aislado. No copia archivos a StrategyQuant, no lanza SQX 144, no toca SQX 142 y no habilita runtime/MCP.

## Resultado

Decision: `ready_for_manual_install_in_sqx144_lab_only`.

Condiciones verificadas:

- Preflight limpio: no habia procesos SQX/Java relevantes activos.
- Build 144 lab local existe y conserva carpeta `user/extend/ResultsPlugins`.
- El destino futuro `SQX Edge Readiness Panel` no existe, por lo que no hay sobrescritura.
- Plugins existentes observados solo como nombres: `CustomPlugin`, `Prop analytics`, `Prop Monte Carlo`.
- Prototipo COMPAT4 existe bajo `.local/sqx144_lab_intake/plugin_prototypes/`.
- `offline_smoke.ps1` paso con 5 archivos requeridos y 3 fixtures.
- La evidencia COMPAT4 mantiene render Playwright con estados `ready`, `review` y `blocked`.

Evidencia local ignorada: `.local/sqx144_lab_intake/sqx144_compat5_results_plugin_install_gate_20260526_151000.json`.

## Alcance Permitido

El siguiente movimiento permitido es manual, reversible y solo en SQX 144 lab aislado:

1. Cerrar SQX 142 y SQX 144 antes de copiar.
2. Crear carpeta destino `user/extend/ResultsPlugins/SQX Edge Readiness Panel` dentro de la build 144 lab.
3. Copiar solamente el payload minimo del prototipo: `index.html` y `fixtures/fixtures.js`.
4. Lanzar SQX 144 lab para smoke visual del tab Results.
5. Registrar evidencia local saneada del resultado.
6. Si algo falla, borrar solo la carpeta `SQX Edge Readiness Panel` del lab 144.

## Bloqueos

Sigue bloqueado:

- Instalar en SQX 142.
- Sobrescribir plugins existentes.
- Copiar a builds activas o rutas no-lab.
- Lanzar proyectos, imports MT5, MCP calls, `run_project` o `stop_project`.
- Usar `GET_SOURCE_CODE` o `GET_ORDERS`.
- Llamar `resultsPlugins/create`, `resultsPlugins/rename` o `resultsPlugins/delete`.
- Persistir datos en navegador, escribir archivos desde el plugin o modificar databanks.
- Usar Migration Tool, migrar datos entre versiones o cambiar `sqx_path` activo.

## Criterios Del Siguiente Bloque

`SQX144-COMPAT6 Results Plugin Lab Smoke` solo puede empezar tras instalacion manual aprobada por el operador en SQX 144 lab.

Aceptacion de COMPAT6:

- SQX 142 permanece cerrado/intocable.
- SQX 144 abre el plugin en Results sin errores visibles.
- `STRATEGY_DATA`, `GET_STATS`, `GET_LAST_SETTINGS_XML` y `GET_SYMBOL_INFO` se observan solo si SQX los emite en el lab.
- No aparece ninguna solicitud de source code, orders, MCP, escritura, importacion o proyecto.
- La evidencia queda local-only y saneada.
