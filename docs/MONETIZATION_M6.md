# Phase M6 - Security And Distribution Audit

## Goal

Preparar SQX Edge Pro para distribucion comercial reduciendo riesgo operativo en tres frentes:

- que el ZIP portable no incluya datos locales, backups, entornos dev o licencias privadas
- que la API local no quede expuesta fuera de localhost por accidente
- que las funciones Pro que escriben archivos tengan enforcement backend, no solo UI

## Threat Model

Activos a proteger:

- `config.json` local del usuario
- `config/license.json` futuro
- rutas personales de StrategyQuant X
- estrategias `.sqx` y proyectos `.cfx`
- backups locales y artefactos de salida
- ZIP portable publicado

Entradas relevantes:

- navegador local con `file://` o `http://localhost`
- endpoints Flask en `127.0.0.1`
- archivos `.sqx` seleccionados por el usuario
- rutas de salida y plantillas `.cfx`
- licencia local futura

Riesgos principales:

- exponer la API en red local
- publicar un ZIP con `config.json`, licencias, backups o salida del usuario
- permitir escritura Pro en modo Free si alguien llama directamente al endpoint
- abrir rutas no autorizadas en Explorer
- modificar `.sqx` fuera de los roots permitidos

## Finding Discovery

Superficies revisadas:

- `api/server.py`
- `core/license_manager.py`
- `core/strategy_cleaner.py`
- `tools/package_portable.ps1`
- `tools/release_checklist.ps1`
- `.gitignore`
- `product_manifest.json`

Hallazgos M6:

1. Los endpoints de escritura Pro (`/api/generate`, `/api/generate-all`, `/api/sqx-clean`) dependian del estado interno actual, pero no tenian guard explicito por feature antes de ejecutar.
2. El ZIP ya excluia varias rutas peligrosas, pero faltaba un auditor independiente y checksum de release.
3. La API tenia CORS local, pero faltaba una respuesta explicita `local_api_only` para host/remoto no local si alguien arranca el servidor con host inseguro.

## Validation

Controles ya existentes:

- CORS solo permite `null`, `localhost` y `127.0.0.1`.
- `sqx-list`, `sqx-clean`, `sqx-preview-rename` y `open-folder` validan rutas contra workspace roots permitidos.
- `config.json` ya se excluye del ZIP.
- `venv`, `node_modules`, `backups`, `dist`, `output` y `.git` ya estan fuera del paquete portable.
- Flask se ejecuta con `debug=False`.

Controles anadidos:

- `enforce_local_api_boundary()` rechaza host/remoto no local con `local_api_only`.
- Cabeceras `X-Content-Type-Options: nosniff` y `Cache-Control: no-store`.
- `require_feature()` bloquea endpoints Pro con `402 pro_required`.
- Los guards usan `project_generator.generate` y `strategy_cleaner.apply` como features canonicas.
- `package_portable.ps1` excluye tambien `config/license.json` y `.env`.
- `audit_distribution.ps1` valida guards del empaquetado, inspecciona ZIP si se le pasa ruta, genera reporte y SHA256.
- `release_checklist.ps1` ejecuta auditoria de distribucion despues de crear el ZIP y anade SHA256 al resumen.
- `product_manifest.json` documenta el boundary local y los archivos sensibles excluidos.

## Attack Path Analysis

Camino A: un usuario Free manipula el frontend y llama a `/api/generate`.

- Antes: el endpoint podia continuar si el build actual lo permitia.
- Despues: el backend llama a `require_feature("project_generator.generate")` antes de validar o escribir.
- Resultado: en Free/Pro expirado responde `402 pro_required`.

Camino B: un ZIP comercial se publica con datos locales.

- Antes: habia exclusiones en `package_portable.ps1`, pero no comprobacion independiente ni checksum.
- Despues: `audit_distribution.ps1` falla si detecta segmentos/archivos denegados y genera `.sha256`.
- Resultado: release checklist no puede cerrar si el paquete contiene contenido sensible conocido.

Camino C: API arrancada con host inseguro.

- Antes: CORS reducia el riesgo desde navegador, pero no bloqueaba por host/remoto.
- Despues: la API rechaza peticiones no locales con `local_api_only`.
- Resultado: reduce exposicion accidental si alguien cambia el host.

## Distribution Rules

Contenido que no debe entrar en ZIP comercial:

- `.git`
- `venv`
- `node_modules`
- `backups`
- `dist`
- `output`
- `.pytest_cache`
- `.playwright-cli`
- `backend/sqx-edge-tool/config.json`
- `backend/sqx-edge-tool/config/license.json`
- `.env`
- `RELEASE_SQX_EDGE.bat`

Cada release portable debe generar:

- ZIP portable
- reporte `SQX_distribution_audit.txt`
- checksum `.sha256`
- resumen `SQX_release_summary.txt` con SHA256

## Residual Risk

M6 no implementa firma criptografica real de licencia. Esa parte sigue prevista para una fase posterior.

Tampoco implementa instalador Windows ni firma Authenticode. Para venta amplia, lo recomendable sera:

- firmar el ejecutable/launcher o instalador
- publicar checksums junto al release
- preparar canal de soporte para falsos positivos de antivirus
- mover activation/licensing real a una fase dedicada

## Decision M6

SQX Edge Pro queda con una primera barrera comercial seria:

- distribucion auditable
- checksums de release
- endpoint gating en backend
- boundary local explicito
- documentacion de riesgos residuales

Esto es suficiente para preparar una beta vendible manual, todavia sin activacion criptografica completa.
