# MODAL-TRACE Modal Traceability Audit

## Objetivo

Cada modal activo de SQX Edge debe decirle al usuario que va a pasar antes de confirmar: origen, destino, impacto, recuperacion y siguiente paso. A nivel tecnico, cada modal debe tener propietario, datos leidos, datos escritos, fallos esperados y cobertura de tests.

## Registro activo

El registro runtime vive en `SQX.modalRegistry` y cubre estas superficies:

| Modal | Tab | Proposito | Trazabilidad minima |
| --- | --- | --- | --- |
| `tm-modal-audit` | Template Maker | Auditar estrategias cargadas | CSV/view, contrato, registros, clusters, ganadoras C2 |
| `tm-modal-c2` | Template Maker | Generar template C2 | Asset, BlockSetting, indicador, cluster, direccion, timeframe, origen, politica de salidas |
| `strat-modal-backdrop` | Strategy Control | Crear JSON manual | Origen manual, mining, asset, template, blocksetting, status |
| `strat-import-backdrop` | Strategy Control | Importar CSV | Batch, archivo, columnas, seleccion, duplicados, localStorage destino |
| `ps-add-mining-backdrop` | Mining Control | Anadir mining | Fase, asset, timeframe, blocksetting, direccion, tag MANUAL |
| `ps-add-phase-backdrop` | Mining Control | Crear fase | Numero, nombre, descripcion, orden, fase visible aunque este vacia |
| `state-restore-backdrop` | Control Panel | Restaurar snapshot | Snapshot, fecha, scope local/workspace, claves permitidas, backup previo automatico |
| `sqx-decision-backdrop` | Global | Confirmar decisiones criticas | Origen, impacto, destino, recuperacion |

## Reglas

- Ningun modal critico debe depender solo de `confirm`, `prompt` o `alert` nativos cuando escribe estado persistido.
- Las alertas nativas solo son aceptables para avisos menores que no escriben datos o como fallback si el modal global no existe.
- Cualquier modal nuevo debe registrarse en `SQX.modalRegistry`, declarar fallos esperados y tener test estatico.
- El analyzer antiguo queda retirado: no debe volver al HTML, load order ni navegacion primaria.

## Rutas de fallo revisadas

- Usuario cancela una decision critica: no debe escribir estado.
- Duplicado detectado: no debe crear estado fantasma.
- CSV invalido: no debe importar registros parciales sin aviso.
- Restore state: debe crear backup previo antes de aplicar claves permitidas y, en remoto, usar solo snapshots del workspace activo.
- Template Maker C2: debe avisar si usa `SIN_INDICADOR` o `CL00`, y debe bloquear salidas desconocidas activas hasta que exista decision explicita en la politica `sqx-exit-policy-v1`.

## Verificacion

- `tests/js/contracts/modal_trace_contracts.mjs` valida registro, load order, trazas HTML y exclusion del analyzer.
- E2E abre los modales principales, confirma decisiones criticas con `sqx-decision-backdrop` y comprueba que los flujos siguen funcionando.
