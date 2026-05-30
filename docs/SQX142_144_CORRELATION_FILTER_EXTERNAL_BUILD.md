# SQX142-144-BACKPORT5 Correlation Filter External Build

Estado: `completed_build_no_sqx_runtime`.

Este bloque implementa el contrato de `SQX142-144-BACKPORT4` como artefacto propio de SQX Edge. El filtro es externo, local-only y read-only: no copia `DatabankFilterByCorrelation`, no llama `filterByCorrelation/filter`, no borra filas de databank SQX, no escribe `data.db`, no escribe `user/projects` y no ejecuta SQX.

## Artefactos

- Core: `backend/sqx-edge-tool/core/sqx142_correlation_filter_external.py`.
- API local: `POST /api/sqx142/correlation-filter/external`.
- Tests: `backend/sqx-edge-tool/test_sqx142_correlation_filter_external.py`.
- Version de respuesta: `sqx142-correlation-filter-external-v1`.

La API usa el mismo gate local-only que los endpoints MCP-like: remoto/tester recibe `403 local_operator_required`; el operador local puede enviar `rows`, `csv` o `portfolioLab` y opcionalmente `includeCsvExport=true`.

## Contrato Implementado

Entradas aceptadas:

- CSV Forward/Foward natural.
- `Portfolio Lab` JSON saneado.
- Filas mock o listas locales ya normalizadas.
- `returnSeries` o `equitySeries` comparables.

Validaciones aplicadas:

- `sourceDatabank` / `forwardSource` debe apuntar a Forward/Foward.
- `sourcePhase` debe ser `phase28_capa2_forward` cuando exista.
- `status` debe ser PASSED natural.
- `Example Only`, `Sample Only`, `Demo Only`, forced/manual/synthetic/fabricated pass quedan en `review`.
- Campos privados, rutas locales, emails, tokens, secretos, password/account/broker privado quedan redactados o excluidos.

## Algoritmo

Configuracion por defecto:

```json
{
  "period": "Day",
  "maxCorrelation": 0.5,
  "warnCorrelation": 0.35,
  "minComparablePoints": 12,
  "similarityThreshold": 0.78,
  "maxWinners": 12
}
```

Flujo:

1. Parsear CSV/JSON/rows.
2. Normalizar identidad opaca, trazabilidad y metricas public-safe.
3. Construir `returnSeries` desde `returnSeries` o desde `equitySeries`.
4. Ordenar candidatos por score Portfolio Lab compatible.
5. Seleccionar greedy contra ganadores previos.
6. Calcular Pearson solo si las series tienen longitud igual y al menos `minComparablePoints`.
7. Marcar `similar` si `maxObservedCorrelation >= maxCorrelation`.
8. Usar similitud operativa si no hay correlacion real.
9. Marcar `review` si el contrato Forward/Foward falla o si la serie existe pero no es comparable.
10. Devolver JSON y export CSV sin mutar SQX.

## Salida

El payload incluye:

- `version=sqx142-correlation-filter-external-v1`.
- `mode=external_readonly`.
- `source=portfolio_lab_phase29`.
- `summary.inputRows`, `eligibleRows`, `portfolio`, `similar`, `review`, `comparablePairs`, `similarityOnly`, `notComparable`, `redactedFields`.
- `items[].candidateId` opaco.
- `items[].decision`: `portfolio`, `similar` o `review`.
- `items[].correlationStatus`: `available`, `similarity_only` o `not_comparable`.
- `items[].maxObservedCorrelation`.
- `items[].nearestWinnerId`.
- `items[].trace`: asset/timeframe/BlockSetting/indicator/cluster saneados.

## Bloqueos

Sigue bloqueado:

- `filterByCorrelation/filter`.
- `DatabankFilterByCorrelation` copiado.
- `SQX databank deletion`.
- `data.db` writes.
- `user/projects` writes.
- SQX runtime.
- `CustomAnalysis=true`.
- `FitPortfolio=true`.
- Retest rerun.
- Forced pass.
- Sample-as-real.
- Profit guarantees.
- Risk-zero claims.
- Remote/tester access a la API local.

## Verificacion

Suite nueva:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe -m pytest backend\sqx-edge-tool\test_sqx142_correlation_filter_external.py -q
```

Resultado:

- `6 passed`.

Cobertura de casos:

- `portfolio`.
- `similar` por Pearson.
- `review`.
- `similarity_only`.
- `not_comparable`.
- Sample blocked.
- Path/private marker redaction.
- API `403 local_operator_required` para remoto/tester.
- CSV export.

## Evidencia

Evidencia local ignorada:

- `.local/sqx142_144_backport/sqx142_144_backport5_correlation_filter_external_build_20260526_181500.json`

Siguiente bloque recomendado: `SQX142-144-BACKPORT6 Monte Carlo Candidate Benchmarks`.
