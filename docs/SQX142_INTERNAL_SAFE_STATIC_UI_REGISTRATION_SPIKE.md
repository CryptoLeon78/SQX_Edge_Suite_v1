# SQX142-INTERNAL-SAFE4 Static UI Registration Spike

## Estado

- Estado: `blocked_static_registration_rewritten_on_startup`.
- Fecha: 2026-05-26.
- Decision: el spike confirma que el registro directo en `templates.html` es tecnicamente insertable con backup/hash/rollback, pero no es persistente tras arrancar SQX 142.
- Superficie modificada: `SQX142_ROOT/internal/web/common/templates.html`.
- Version visible: `sqx142-internal-safe4-static-ui-registration-v1`.
- Script: `tools/sqx142_internal_safe4_static_ui_registration.ps1`.
- Test de contrato: `tests/js/contracts/sqx142_internal_safe4_static_ui_registration_contracts.mjs`.
- Evidencia local ignorada: `.local/sqx142_internal_safe/sqx142_internal_safe4_static_ui_registration_20260526_195520.json`.
- Evidencia local ignorada de bloqueo runtime: `.local/sqx142_internal_safe/sqx142_internal_safe4_runtime_rewrite_20260526_200100.json`.

## Hallazgo del spike

`SQX142-INTERNAL-SAFE3` confirmo que `SQX Edge Readiness Panel` existe en `user/extend/ResultsPlugins` y mantiene hashes correctos, pero no aparece automaticamente en Results. La busqueda estatica encontro que `Source Code Translator` no depende de discovery dinamico de carpetas, sino de wiring directo en la plantilla nativa `ResultsSourceCode`.

Tambien se comprobo que el HTML del Results Plugin no queda servido por el localhost SQX 142 desde rutas `user/extend/ResultsPlugins`, por lo que un iframe directo al plugin devolveria 404. El minimo viable seguro para este bloque es un panel estatico pequeno dentro de `ResultsSourceCode`, con marcadores y rollback.

Tras aplicar el panel y arrancar SQX 142, el smoke de arranque fue correcto (`appVersion=142.2336` / `Application started.`), pero SQX reescribio `SQX142_ROOT/internal/web/common/templates.html` durante el arranque y elimino los marcadores `SQX142-INTERNAL-SAFE4-*`. Por tanto, el registro directo sobre el archivo generado no queda activo en runtime.

## Backup y hashes

- Backup creado: `.local/sqx142_internal_safe/backups/sqx142_internal_safe4_static_ui_registration_20260526_195520`.
- Hash anterior de `templates.html`: `3EF23D77EDD87A7A20A33F1406AD9B75D3397C451AF3E77BC090D0883553772F`.
- Hash posterior de `templates.html`: `E1443D3DCEE2B36593A7C3E65753F73D56556CC0E072A1A23EF51E05439A72C9`.
- Hash despues de arrancar SQX 142: `6A056751051B966F78194B6F5D99F656249DE8D2A0E1C6F6A0EF0C51C32CBA8C`.
- Marcadores insertados una sola vez: `SQX142-INTERNAL-SAFE4-BEGIN` y `SQX142-INTERNAL-SAFE4-END`.
- Marcadores despues de arrancar SQX 142: ausentes.
- Barrido de procesos antes de aplicar: `processCount=0`.

## Rollback

```powershell
tools\sqx142_internal_safe4_static_ui_registration.ps1 -Action rollback -BackupId sqx142_internal_safe4_static_ui_registration_20260526_195520
```

El rollback exige SQX cerrado y restaura el `templates.html` respaldado. Tras el smoke de arranque no queda marcador SAFE4 activo en `templates.html`; el rollback queda disponible solo como retorno exacto al backup previo si el operador lo pide.

## Limites

SAFE4 no queda instalado como UI persistente. Es un spike cerrado como no-go para `templates.html` generado: SQX 142 regenera esa superficie al arrancar. No copia internals de 144 ni cambia motor.

Bloqueado:

- engine/binarios/jars.
- licencia/activacion/bypass.
- `data.db` writes.
- `user/projects` writes.
- databanks vivos.
- ejecucion runtime SQX o `run_project`.
- importacion MT5 directa.
- Migration Tool.
- patch de jars/plugins internos como via de persistencia.

## Verificacion

- Pre-start status tras install -> `markerPresent=true`, `anchorPresent=true`, `processCount=0`.
- Marcadores pre-start en plantilla -> `beginCount=1`, `endCount=1`, version presente.
- `node tests\js\contracts\sqx142_internal_safe4_static_ui_registration_contracts.mjs` -> `sqx142 internal safe4 static ui registration contracts ok`.
- Startup smoke: SQX 142 arranca y `http://127.0.0.1:8080/main/getCommon` responde `appVersion=142.2336` / `Application started.` tras espera inicial.
- Post-start status -> `markerPresent=false`, `anchorPresent=true`, `processCount=6`.
- Evidencia local ignorada de arranque: `.local/sqx142_internal_safe/sqx142_internal_safe4_startup_smoke_20260526_200017.json`.

## Siguiente bloque recomendado

No avanzar a patch de jars/plugins internos. Recomendacion: mantener el panel operativo en Edge Factory (`UI-INTEGRATION1`) y cerrar el frente interno de UI nativa como no-go seguro salvo que el operador apruebe un nuevo bloque de investigacion estrictamente read-only sobre el origen generador.
