# Phase M4 - Free Pro Internal Product Separation

## Goal

Preparar la app para funcionar como producto comercial con tres perfiles claros:

- Free
- Pro
- Internal

Esta fase crea la arquitectura de acceso sin activar todavia cobro automatico ni verificacion criptografica final.

## Implemented

- `product_manifest.json` como fuente de verdad de producto, features, planes y perfiles de release.
- `license_manager.py` en backend con estado de licencia y chequeo de capacidades.
- Endpoints:
  - `GET /api/license/status`
  - `POST /api/license/check`
- Panel de licencia en Inicio.
- Modulo frontend `SQX.license`.
- Carga del manifest de producto dentro de `SQX_MANIFEST`.
- Contratos estaticos y API actualizados.

## Current Build Mode

La build del repositorio queda en modo `internal`.

Motivo:

- no rompe el uso actual del Project Generator
- permite seguir desarrollando y probando todo
- separa el vocabulario Free/Pro/Internal antes de bloquear acciones reales

Cuando preparemos una build publica Free, el perfil debera cambiar a `free` y los endpoints Pro podran empezar a exigir `required_feature`.

## Access Contract

Feature flags iniciales:

- `dashboard.view`
- `strategies.basic`
- `strategies.import_full`
- `strategies.export_advanced`
- `project_generator.demo`
- `project_generator.generate`
- `strategy_cleaner.preview`
- `strategy_cleaner.apply`
- `backups.advanced`
- `workflows.premium`
- `templates.premium`
- `support.priority`

Regla:

- la UI puede mostrar estado y mensajes
- el backend debe decidir permisos para acciones con escritura
- una licencia sin firma no activa Pro
- el modo Internal habilita todo para desarrollo

## Next Step

M5 deberia preparar la capa visual/comercial:

- mensajes de upgrade mejorados
- pantalla de licencia dedicada si hace falta
- textos de venta in-app
- primer README comercial
- assets para landing

M6 deberia endurecer seguridad:

- firma real con clave publica
- no incluir claves privadas
- enforcement en endpoints Pro
- release Free sin herramientas internas
