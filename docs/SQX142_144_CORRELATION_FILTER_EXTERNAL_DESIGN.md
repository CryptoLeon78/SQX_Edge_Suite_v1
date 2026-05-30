# SQX142-144-BACKPORT4 Correlation Filter External Design

Estado: `completed_design_no_sqx_mutation`.

Este bloque adapta la idea `DatabankFilterByCorrelation` de Build 144 a SQX 142 como filtro externo gobernado por SQX Edge. No se copia el plugin interno de 144, no se llama `filterByCorrelation/filter`, no se elimina ninguna estrategia de un databank activo y no se ejecuta SQX.

## Objetivo

Disenar un filtro de correlacion externo para Portfolio Lab que pueda comparar candidatos de Capa 2 a partir de CSV/export/equity series y clasificar estrategias como:

- `portfolio`: candidata elegida para shortlist.
- `similar`: demasiado parecida o demasiado correlacionada con una ganadora previa.
- `review`: falta evidencia comparable o no supera contrato de entrada.

El filtro debe complementar Portfolio Lab Phase29, no sustituirlo:

- Phase29 sigue consumiendo supervivientes naturales Forward/Foward.
- Portfolio Lab sigue siendo owner de shortlist, diversidad, sizing base y export.
- SQX 142 sigue intacto: no `CustomAnalysis`, no databank action core, no `FitPortfolio=true`.

## Referencia 144

La superficie estatica de Build 144 detecto:

- Clase/feature: `DatabankFilterByCorrelation`.
- Accion: `Filter by correlation`.
- Endpoint interno: `filterByCorrelation/filter`.
- Parametros observados: periodo por defecto `Day`, `maxCorrelation=0.5`.
- Riesgo: puede eliminar estrategias del databank activo.

Decision para SQX 142:

- Reproducir la logica como benchmark externo.
- Usar copia CSV/equity series, no databank vivo.
- Producir reporte y shortlist, no borrado.

## Entradas Permitidas

Entrada primaria:

- CSV Forward/Foward natural desde Portfolio Lab Phase29.
- Portfolio Lab JSON exportado por Portfolio Lab.
- Equity/return series comparables aportadas por operador.

Columnas aceptadas:

- Identidad: `strategy`, `name`, `Strategy Name`, `id`.
- Trazabilidad: `asset`, `symbol`, `timeframe`, `BlockSetting`, `indicator`, `cluster`, `sourceDatabank`, `forwardSource`.
- Contrato Forward/Foward: `forwardStatus`, `status`, `result`, `passed`, `passSource`, `Example Only`.
- Metricas: `Profit Factor`, `Ret/DD Ratio`, `Max DD %`, `Number of trades`, `Stability`, `SQN`, `Net Profit`.
- Series: `returnSeries`, `Return Series`, `Returns`, `Monthly Returns`, `equitySeries`, `Equity Series`, `EquityCurve`, `Balance Curve`.

Entradas bloqueadas:

- `Example Only`, `Sample Only`, `Demo Only`.
- Filas failed promocionadas manualmente.
- `Results=passed` fabricado.
- Datos de cuenta, login, balance real, broker privado, emails, tokens, rutas locales o URLs protegidas.
- Databank activo SQX como destino de escritura.

## Algoritmo Propuesto

Version: `sqx142-correlation-filter-external-design-v1`.

1. Normalizar filas con el contrato actual de Portfolio Lab.
2. Validar que cada candidato venga de Forward/Foward natural.
3. Construir `returnSeries`:
   - Si existe `returnSeries`, usarla.
   - Si existe `equitySeries`, convertir a retornos relativos.
   - Si no hay serie comparable, marcar `correlationStatus=similarity_only`.
4. Alinear ventanas:
   - Misma longitud minima: `minComparablePoints=12` para build futuro.
   - Misma granularidad declarada: `Day`, `Week`, `Month` o `Trade`.
   - Si la longitud no coincide, truncar solo si existe politica explicita; si no, `review`.
5. Calcular correlacion Pearson sobre retornos comparables.
6. Comparar contra umbral base:
   - `maxCorrelation=0.50` por defecto, en linea con la referencia 144 observada.
   - `warnCorrelation=0.35` para revision humana.
7. Aplicar diversidad operativa cuando no haya correlacion real:
   - asset/timeframe/blockSetting/indicator/cluster.
   - umbral de similitud actual Portfolio Lab `similarityThreshold=0.78`.
8. Seleccionar shortlist greedy:
   - ordenar por score Portfolio Lab.
   - aceptar si cumple contrato y no supera correlacion con ganadores.
   - marcar como `similar` si supera umbral real o similitud operativa.
   - marcar como `review` si falta evidencia, hay serie incompleta o contrato no natural.

## Salida Propuesta

```json
{
  "version": "sqx142-correlation-filter-external-v1",
  "mode": "external_readonly",
  "source": "portfolio_lab_phase29",
  "settings": {
    "period": "Day",
    "maxCorrelation": 0.5,
    "warnCorrelation": 0.35,
    "minComparablePoints": 12,
    "similarityThreshold": 0.78
  },
  "summary": {
    "inputRows": 0,
    "eligibleRows": 0,
    "portfolio": 0,
    "similar": 0,
    "review": 0,
    "comparablePairs": 0
  },
  "items": []
}
```

Cada item debe incluir:

- `candidateId` opaco.
- `decision`: `portfolio`, `similar`, `review`.
- `reason`.
- `maxObservedCorrelation`.
- `correlationStatus`: `available`, `similarity_only`, `not_comparable`.
- `nearestWinnerId`.
- `trace`: asset/timeframe/BlockSetting/indicator/cluster saneados.

## Integracion Con Portfolio Lab

El codigo actual de `app/js/modules/edge-factory.js` ya contiene:

- `portfolioReturnSeries`.
- `pearsonCorrelation`.
- `bestCorrelation`.
- `correlationThreshold=0.50`.
- Distincion entre `correlacion real disponible` y `similitud operativa, no correlacion real`.

BACKPORT4 no cambia esa logica. La formaliza como contrato para el build posterior:

- Reusar parseo y normalizacion existentes cuando sea posible.
- Extraer funciones puras si el build necesita tests directos.
- Mantener export browser-only o backend local-safe, sin paths privados.

## Bloqueos

Queda bloqueado:

- Llamar `filterByCorrelation/filter`.
- Copiar `DatabankFilterByCorrelation` de 144.
- Borrar filas de databank SQX.
- Escribir en `data.db`.
- Escribir en `user/projects`.
- Ejecutar SQX.
- `CustomAnalysis=true` o `FitPortfolio=true`.
- Relanzar retests para fabricar candidatos.
- Forzar `Results=passed`.
- Usar datos sample como reales.
- Prometer rentabilidad, reduccion garantizada de drawdown o riesgo cero.

## Criterios De Aceptacion Para Build

`SQX142-144-BACKPORT5 Correlation Filter External Build` debe:

- Aceptar CSV/JSON local o estado Portfolio Lab ya saneado.
- Validar contrato Forward/Foward natural.
- Calcular Pearson solo con series comparables.
- Diferenciar correlacion real de similitud operativa.
- Devolver reporte sin mutar SQX.
- Exportar JSON/CSV de shortlist y decisiones.
- Testear casos `portfolio`, `similar`, `review`, `similarity_only`, `not_comparable`, sample bloqueado y path/private marker redaction.
- Mantener `phase29_capa2_portfolio` como fuente metodologica.

## Evidencia

Evidencia local ignorada:

- `.local/sqx142_144_backport/sqx142_144_backport4_correlation_filter_external_design_20260526_171500.json`

Verificacion esperada:

- `test_docs_state_consistency.py`
- `git diff --check`

Siguiente bloque recomendado: `SQX142-144-BACKPORT5 Correlation Filter External Build`.
