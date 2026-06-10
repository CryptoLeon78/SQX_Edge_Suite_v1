# SQX144 Results Plugin Prototype Design

Estado: `SQX144-COMPAT3 Results Plugin Prototype Design` completado como diseno estatico local-only.

Este documento define el primer prototipo de Results Plugin para SQX Edge sobre la superficie de Build 144. No instala nada en SQX 142/144 y no ejecuta StrategyQuant. Su objetivo es dejar un contrato de producto, datos, privacidad y aceptacion antes de crear archivos de plugin.

## Prototipo

Nombre interno: `SQX Edge Readiness Panel`.

Tipo: Results Plugin read-only para una estrategia seleccionada.

Carpeta futura, solo cuando se apruebe instalacion: `user/extend/ResultsPlugins/SQX Edge Readiness Panel/index.html`.

Primer alcance:

- Mostrar un resumen operativo de la estrategia seleccionada.
- Leer estadisticas mediante `GET_STATS`.
- Leer configuracion de backtest mediante `GET_LAST_SETTINGS_XML`.
- Leer metadatos del simbolo mediante `GET_SYMBOL_INFO` cuando `STRATEGY_DATA` tenga simbolo.
- No usar `GET_SOURCE_CODE` en el primer prototipo.
- No usar `GET_ORDERS` por defecto; se reserva para un subpanel posterior de trade anatomy si se aprueba privacidad.

## Mensajes Permitidos

SQX -> plugin:

- `STRATEGY_DATA`
- `SET_THEME`
- `SET_LANGUAGE`
- `STATS_RESPONSE`
- `LAST_SETTINGS_XML_RESPONSE`
- `SYMBOL_INFO_RESPONSE`

Plugin -> SQX:

- `GET_STATS`
- `GET_LAST_SETTINGS_XML`
- `GET_SYMBOL_INFO`

Mensajes bloqueados en v0:

- `GET_SOURCE_CODE`: puede exponer codigo/estrategia completa; queda para operador local y fase explicita.
- `GET_ORDERS`: puede exponer lista completa de trades; queda para benchmark/diagnostico posterior.
- `resultsPlugins/create`, `resultsPlugins/rename`, `resultsPlugins/delete`: gestionan carpetas de plugin y quedan fuera del prototipo read-only.

## Vista V0

El plugin debe ser una herramienta compacta de decision, no una landing ni un dashboard pesado.

Secciones:

1. Header de contexto: strategy, project/databank si llegan en `STRATEGY_DATA`, symbol/timeframe cuando existan.
2. Readiness score: `ready`, `review`, `blocked` segun reglas SQX Edge.
3. Metrics strip: `NetProfit`, `NumberOfTrades`, `ProfitFactor`, `RExpectancy`, `ReturnDDRatio`, `Drawdown`/`PctDrawdown`.
4. Methodology checks: trade count, expectancy, profit factor, drawdown relation, symbol info availability, settings XML availability.
5. Risk notes: mensajes cortos cuando falte dato, haya metrica no numerica o el contexto no baste para decidir.
6. Disclaimer fijo: productividad/metodologia; sin prometer rentabilidad, riesgo cero ni certificacion externa.

## Reglas De Decision

V0 no decide portfolio, no promueve estrategias y no cambia databanks.

Estados:

- `ready`: datos minimos presentes y metricas superan umbrales configurables de lectura.
- `review`: datos presentes pero una o mas metricas estan cerca del borde o falta simbolo/configuracion.
- `blocked`: faltan `STRATEGY_DATA`/`GET_STATS`, no hay estrategia seleccionada, o los campos numericos esenciales no son validos.

Umbrales iniciales solo para visual review:

- `NumberOfTrades >= 30`
- `RExpectancy > 0`
- `ProfitFactor >= 1.05`
- `ReturnDDRatio >= 1`

Estos umbrales no sustituyen Capa1/Capa2, no escriben en SQX y no convierten el resultado en aprobado por si solos.

## Privacidad

El prototipo no debe persistir:

- project names
- databank names
- strategy names
- source code
- orders/trades
- local paths
- broker account details
- protected URLs
- tokens or license details

El plugin puede mantener estado solo en memoria de la pagina. Cualquier evidencia de prueba debe ir a `.local/sqx144_lab_intake/` con rutas y nombres redacted.

## Compatibilidad Visual

El plugin debe:

- Adaptarse a `SET_THEME`.
- Preparar i18n para `SET_LANGUAGE`, con `en` y `es` como minimo cuando se implemente.
- Caber en el Results tab sin scroll horizontal.
- Evitar dependencias remotas; todo asset debe ser local al folder del plugin.
- Incluir disclaimer visible.

## Plan De Implementacion Posterior

`SQX144-COMPAT4 Results Plugin Prototype Build` puede crear un prototipo fuera de SQX bajo una carpeta de laboratorio, por ejemplo `.local/sqx144_lab_intake/plugin_prototypes/SQX Edge Readiness Panel/`, con mock messages.

Fases sugeridas:

1. Build offline con fixture mock de `STRATEGY_DATA`, `STATS_RESPONSE`, `LAST_SETTINGS_XML_RESPONSE` y `SYMBOL_INFO_RESPONSE`.
2. Browser/local file smoke del prototipo offline.
3. Static privacy scan: sin rutas, tokens, source code ni persistencia.
4. Operator decision para copiar manualmente o instalar en SQX 144 lab, nunca en SQX 142 activo.

## Resultado COMPAT4

`SQX144-COMPAT4 Results Plugin Prototype Build` queda completado como prototipo offline local-only.

Salida:

- Prototipo: `.local/sqx144_lab_intake/plugin_prototypes/SQX Edge Readiness Panel/index.html`.
- Fixtures mock: `ready`, `review` y `blocked`.
- Smoke local: `offline_smoke.ps1`.
- Evidencia local ignorada: `sqx144_compat4_results_plugin_prototype_build_20260526_150500.json`.
- Render Playwright: readiness `ready`, `review` y `blocked` confirmado.

La salida sigue sin instalarse en SQX 142/144, sin runtime, sin MCP calls, sin `GET_SOURCE_CODE`, sin `GET_ORDERS`, sin endpoints `resultsPlugins/create`, `resultsPlugins/rename` o `resultsPlugins/delete`, sin persistencia de navegador y sin escritura en databanks.

Siguiente bloque recomendado: `SQX144-COMPAT5 Results Plugin Install Gate`.

## Criterios De Aceptacion

- No requiere SQX abierto para desarrollarse.
- No usa `GET_SOURCE_CODE` ni `GET_ORDERS` en v0.
- Maneja mensajes vacios o tardios sin errores.
- Muestra `blocked` cuando no hay estrategia seleccionada.
- No escribe archivos, no llama endpoints de gestion `create/rename/delete` y no modifica databanks.
- Mantiene disclaimer y no hace claims de rentabilidad.
