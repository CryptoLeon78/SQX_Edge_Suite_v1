# SQX142-144-BACKPORT7 MT5 Data Intake Probe

Estado: `completed_probe_no_import`.

Este bloque adapta la idea de importacion directa MT5 de Build 144 como un probe externo de SQX Edge para una copia CSV/OHLC. No importa datos en SQX 142, no alimenta generacion real y no escribe `data.db`.

## Implementacion

- Core: `backend/sqx-edge-tool/core/sqx142_mt5_data_intake_probe.py`.
- API local-only: `POST /api/sqx142/mt5-data-intake/probe`.
- Tests: `backend/sqx-edge-tool/test_sqx142_mt5_data_intake_probe.py`.
- Version de respuesta: `sqx142-mt5-data-intake-probe-v1`.
- Modo: `external_readonly`.
- Fuente esperada: `mt5_csv_copy`.

El endpoint acepta un CSV OHLC copiado o `rows` ya parseadas, mas `asset`, `timeframe` y opcionalmente `sqxDataRows`/`dataDbRows`/`catalogRows` para fixtures. Si no se aportan filas de catalogo y el operador local lo llama, el probe puede leer `data.db` en SQLite URI `mode=ro` para buscar el simbolo/timeframe. Esa lectura no devuelve rutas ni simbolos crudos.

## Entradas

OHLC requerido:

- `time` / `datetime` / `date`.
- `open`.
- `high`.
- `low`.
- `close`.
- `volume` opcional.

Catalogo SQX opcional:

- `SYMBOL` o `INSTRUMENT`.
- `TIMEFRAME`.
- `DATEFROM`.
- `DATETO`.
- `DATATYPE`.
- `TIMEZONE`.

Defaults: `minBars=20`, `maxBars=2000`, `minOverlapDays=1`.

## Salidas

La respuesta devuelve:

- `decision`: `intake_probe_pass`, `intake_probe_review` o `intake_probe_fail`.
- `summary`: `inputRows`, `validBars`, `invalidRows`, `duplicateTimes`, `timeGaps`, `catalogRows`, `catalogMatches`, `bestOverlapDays`, `redactedFields`.
- `probe`: `assetRef`, `timeframe`, `dateFrom`, `dateTo`, `barsHash`.
- `sqxCatalog`: origen `payload` o `data_db_readonly`, matches saneados con `seriesId`, `symbolRef`, `dateFrom`, `dateTo`, `dataType`, `timezone`, `overlapDays`.
- `CSV export` opcional con `includeCsvExport=true`.

## Decisiones

- `intake_probe_pass`: OHLC valido, barras suficientes, match de catalogo SQX y solape de rango.
- `intake_probe_review`: OHLC valido pero falta match, falta solape, hay gaps/duplicados o filas invalidas ignoradas.
- `intake_probe_fail`: no hay barras suficientes o la copia OHLC no puede validarse.

## Gate Y Privacidad

El endpoint exige operador local y devuelve `403 local_operator_required` a remoto/tester. La respuesta mantiene:

- `privacy.local_paths_returned=false`.
- `privacy.raw_mt5_symbol_returned=false`.
- `privacy.raw_sqx_symbol_returned=false`.
- `privacy.private_fields_returned=false`.
- `privacy.tokens_returned=false`.

Tambien mantiene guards explicitos:

- `mt5_terminal_started=false`.
- `mt5_ipc_called=false`.
- `sqx_runtime_started=false`.
- `sqx_data_imported=false`.
- `generation_enabled=false`.

## Bloqueado

- Arrancar terminal MT5 desde este endpoint.
- Llamar IPC MT5 / `copy_rates_from_pos` desde este endpoint.
- Ejecutar import directo a SQX.
- Escribir `data.db`.
- Escribir `user/projects`.
- Alimentar Project Generator, Template Maker, Capa1/Capa2 o Portfolio Master.
- Llamar API interna SQX, `run_project`, `project/start` o retests.
- Copiar internals de SQX 144, licencia, activacion, bypass o Migration Tool.
- Usar CSV sample/demo como dato real.

## Verificacion

- `test_sqx142_mt5_data_intake_probe.py` -> `6 passed`.
- Evidencia local ignorada: `.local/sqx142_144_backport/sqx142_144_backport7_mt5_data_intake_probe_20260526_190500.json`.

Siguiente bloque recomendado: `SQX142-144-BACKPORT8 Copy-Only Migration Checklist`.
