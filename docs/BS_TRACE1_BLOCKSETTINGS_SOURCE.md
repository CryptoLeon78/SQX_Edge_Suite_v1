# BS-TRACE1 BlockSettings Source Contract

## Source Of Truth

The official real SQX BlockSettings are versioned under:

`backend/sqx-edge-tool/resources/blocksettings/`

`backend/sqx-edge-tool/tools/build_blocksettings_manifest.py` parses each `.sqb` as a ZIP, reads `config.xml`, hashes the original file and writes:

`backend/sqx-edge-tool/config/blocksettings_manifest.json`

## Resolution Rules

- Capa 1 resolves from methodology family plus timeframe.
- `_v6` is the default Capa 1 source where the real file exists.
- `Volatilidad`, `Volumen` and `SoporteResistencia` use `*_intraday_v6` for `M5/M15/M30/H1`.
- `H4/D1` use the general `_v6` source where available. `Volatilidad` keeps `BS_Volatilidad_v4` as explicit fallback because no general `BS_Volatilidad_v6.sqb` was provided in the v6 batch.
- Capa 2 is selected manually in Project Generator, with automatic recommendation by timeframe:
  - `M5/M15/M30/H1/H4`: `BS_Filtros_v6`
  - `D1`: `BS_Filtros_v6_D1`
  - fallback: `BS_Filtros_v6`

## Traceability Rule

Every mining or generated project should keep:

- `family`
- `canonicalId`
- `filename`
- `sha256`
- `layer`
- `timeframeRule`
- origin (`manual`, `asset-card`, `csv-import`, or generated)

Legacy labels such as `BS_Tendencia` and the previous v4/v5/v7 files remain aliases/resources for compatibility, but functional generation must use the resolved real v6 `.sqb` unless the operator explicitly chooses a legacy file.
