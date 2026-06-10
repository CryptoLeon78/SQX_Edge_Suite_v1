# SQX142-INTERNAL-SAFE1 Supported Internal Extension Audit

Estado: `completed_readonly_extension_audit`.

Este bloque responde a la peticion de parchear internamente SQX 142, pero fija primero una frontera soportada y reversible. El resultado no autoriza cambios sobre motor, binarios, jars, licencia, activacion ni internals propietarios; autoriza trabajar solo en superficies de extension y artefactos SQX Edge-owned cuando haya backup, hash y rollback.

## Fuentes Revisadas

- Documentos cerrados BACKPORT1..9 y `UI-INTEGRATION1 Backport Operator Panel`.
- Snapshot local saneado de `SQX142_ROOT` en modo lectura.
- Barrido de procesos antes de registrar el gate: `sqxJavaProcessCount=0`.
- Evidencia local ignorada: `.local/sqx142_internal_safe/sqx142_internal_safe1_supported_internal_extension_audit_20260526_210000.json`.

## Snapshot Saneado

| Superficie | Estado | Lectura SAFE1 |
| --- | --- | --- |
| `user/extend` | existe | Capa de extension soportada para artefactos propios. |
| `user/extend/ResultsPlugins` | existe | Punto preferente para UI interna reversible. |
| `SQX Edge Readiness Panel` | detectado | Plugin propio ya instalado; candidato principal para SAFE2. |
| `Source Code Translator` | detectado | Extension existente; tocar solo si el cambio es propio, documentado y reversible. |
| `user/data` | existe | Solo lectura para catalogo; `data.db` no se escribe. |
| `user/projects` | existe | Solo checklist/copia manual futura; no escritura desde este gate. |
| `user/settings` | existe | Requiere revision explicita y backup si algun ajuste propio fuera necesario. |
| `custom_indicators` | existe | Requiere revision explicita; no forma parte del primer parche. |
| `internal` | existe | Bloqueado para parches. |

## Matriz De Superficies

| Decision | Superficie | Uso permitido |
| --- | --- | --- |
| Permitido | `user/extend/ResultsPlugins/<plugin SQX Edge>` | Actualizar HTML/JS/CSS propio con backup previo, hashes, evidencia render y rollback. |
| Permitido | `SQX Edge Readiness Panel` | Convertirlo en panel operativo interno para backport/readiness, sin runtime ni escritura SQX. |
| Permitido | Views `.vw` generadas por SQX Edge | Entregar/importar manualmente vistas de revision; no modificar databanks. |
| Permitido | CSV/JSON exportados por operador | Consumirlos externamente en Correlation, MC benchmarks, MT5 probe y Migration checklist. |
| Revisar | `Source Code Translator` | Cambios propios sobre extension existente, solo con backup/hash y sin leer source privado mas alla del flujo de usuario. |
| Revisar | `user/settings` | Solo ajustes operator-owned y reversibles; nunca como requisito oculto del parche. |
| Revisar | `user/projects` | Solo mediante checklist copy-only y con SQX cerrado; SAFE1 no escribe. |
| Revisar | `custom_indicators` | Solo si el operador confirma indicador propio y licencia/material permitido. |
| Bloqueado | `internal`, ejecutables, clases, jars, motor | Fuera de alcance. No se parchean ni se copian internals. |
| Bloqueado | licencia, activacion, bypass, material de terceros | Fuera de alcance por seguridad y legalidad. |
| Bloqueado | `data.db`, databanks vivos, logs SQX | Solo lectura o evidencia saneada; no mutation path. |
| Bloqueado | `run_project`, retests, importacion MT5 directa, Migration Tool | No forman parte de un parche interno seguro. |
| Bloqueado | Build 144 internals | Las ideas se reimplementan como SQX Edge-owned; no se trasladan piezas internas. |

## Candidato De Parche Interno Seguro

`SQX142-INTERNAL-SAFE2 Results Plugin Internal Patch Build` queda como siguiente bloque recomendado.

Alcance propuesto:

- Actualizar `SQX Edge Readiness Panel` bajo `user/extend/ResultsPlugins`.
- Mostrar estado local de backport, MCP-like read-only, Correlation external, MC benchmarks, MT5 probe y Migration checklist.
- Incluir fixture offline y render smoke antes de instalar.
- Crear backup del plugin instalado y registrar hashes antes/despues.
- Mantener SQX cerrado durante copia manual/local.

Fuera de alcance para SAFE2:

- Arrancar SQX, Java, MT5 o terminal externo.
- Tocar `data.db`, `user/projects`, databanks, logs o settings activos.
- Usar APIs internas SQX, `run_project`, Migration Tool o importacion directa.
- Cambiar motor, binarios, jars, licencia, activacion o internals.

## Decision

La forma segura de "parchear internamente" SQX 142 es actuar en la capa de extension soportada, empezando por `user/extend/ResultsPlugins/SQX Edge Readiness Panel`. Cualquier cambio por debajo de esa capa queda bloqueado salvo que el proveedor lo documente como extension soportada y se pueda ejecutar con backup, hash, rollback y SQX cerrado.
