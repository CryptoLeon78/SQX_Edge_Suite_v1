# SQX142-INTERNAL-SAFE2 Results Plugin Internal Patch Build

Estado: `installed_with_backup_hash_rollback_ready`.

Este bloque instala un parche interno seguro en SQX 142 usando solo la superficie soportada `user/extend/ResultsPlugins`. El plugin actualizado es `SQX Edge Readiness Panel`, mantenido como artefacto propio de SQX Edge y versionado en el repo.

## Superficie Tocada

| Elemento | Resultado |
| --- | --- |
| Plugin | `SQX Edge Readiness Panel` |
| Version | `sqx142-internal-safe2-readiness-panel-v1` |
| Fuente repo | `integrations/sqx142/results_plugins/SQX Edge Readiness Panel` |
| Destino SQX | `SQX142_ROOT/user/extend/ResultsPlugins/SQX Edge Readiness Panel` |
| Script | `tools/sqx142_internal_safe2_results_plugin_patch.ps1` |
| Evidencia local ignorada | `.local/sqx142_internal_safe/sqx142_internal_safe2_results_plugin_install_20260526_213000.json` |

## Instalacion

- SQX/Java process sweep antes de instalar: `sqxJavaProcessCount=0`.
- Backup previo creado: `.local/sqx142_internal_safe/backups/sqx142_internal_safe2_readiness_panel_20260526_192515`.
- Archivos instalados:
  - `index.html`
  - `fixtures/fixtures.js`
- Hashes instalados coinciden con la fuente versionada:
  - `index.html`: `DACE1D0A26A0B013C60A19668C25158FAE0D28D554325821B856073994BFB3F0`
  - `fixtures/fixtures.js`: `365045FA198DF8B246DE766652EACE54142772F05E522ED0877A7ADCF19A98DB`

## Que Cambia

- El panel pasa a `sqx142-internal-safe2-readiness-panel-v1`.
- Mantiene fixtures offline `ready`, `review` y `blocked`.
- Conserva el flujo read-only por `postMessage` para `GET_STATS`, `GET_LAST_SETTINGS_XML` y `GET_SYMBOL_INFO`.
- Anade guardas visibles de SAFE2: extension surface, backup, rollback, SQX cerrado, `data.db` read-only y `user/projects` no escrito.
- Expone `window.SQX_EDGE_READINESS_PANEL_VERSION` y `window.__SQX_EDGE_PANEL__` para smoke/diagnostico.

## Rollback

Rollback disponible desde backup:

```powershell
tools\sqx142_internal_safe2_results_plugin_patch.ps1 -Action rollback -BackupId sqx142_internal_safe2_readiness_panel_20260526_192515
```

El rollback tambien exige SQX cerrado y no toca motor, `data.db`, databanks ni proyectos.

## Limites

- No se arranco SQX, Java, MT5 ni terminal externo.
- No se tocaron motor, binarios, jars, `internal`, licencia ni activacion.
- No se escribio en `data.db`, databanks vivos, logs SQX, `user/projects` ni settings activos.
- No se uso API interna SQX, `run_project`, importacion MT5 directa ni Migration Tool.
- No se copiaron internals de Build 144.

## Verificacion

- `node tests/js/contracts/sqx142_internal_safe2_results_plugin_contracts.mjs` -> `sqx142 internal safe2 results plugin contracts ok`.
- `tools\sqx142_internal_safe2_results_plugin_patch.ps1 -Action status` confirma fuente e instalado con hashes coincidentes tras install.
- Playwright offline sobre HTML instalado -> `offline_visual_smoke_passed`, version `sqx142-internal-safe2-readiness-panel-v1`, readiness `ready`.
- Evidencia de instalacion: `sqx142_internal_safe2_results_plugin_install_20260526_213000.json`.
- Evidencia visual local ignorada: `sqx142_internal_safe2_results_plugin_visual_smoke_20260526_213000.json`.

## Siguiente Decision Recomendada

`SQX142-INTERNAL-SAFE3 Results Plugin Manual Visual Smoke`: abrir SQX 142 manualmente, entrar en Results y confirmar que `SQX Edge Readiness Panel` aparece, renderiza `sqx142-internal-safe2-readiness-panel-v1` y no provoca escrituras ni runtime adicional.
