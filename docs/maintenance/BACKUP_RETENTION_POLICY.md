# Backup Retention Policy

## Objetivo

Evitar que los backups locales crezcan sin control, manteniendo trazabilidad suficiente para revertir fases recientes y saber por que se elimina cada artefacto pesado.

## Regla base

Cada vez que se cree un backup de fase se debe ejecutar tambien una mini revision de retencion:

1. Crear backup previo con nombre versionado: `<phase>-prechange-YYYYMMDD-HHMMSS`.
2. Registrar alcance: rutas incluidas, motivo, fase, agente propietario y si contiene material privado.
3. Medir tamano de `backups/`, `output/`, `.pytest_cache/`, `analysis_output/` y `dist/`.
4. Clasificar backups antiguos como `keep`, `superseded`, `obsolete`, `private-evidence` o `release-evidence`.
5. Eliminar solo los elementos `superseded` u `obsolete` despues de dejar manifiesto local.
6. Mantener los backups recientes minimos definidos abajo.

## Retencion local por defecto

- Mantener los 2 backups mas recientes de la fase activa.
- Mantener 1 backup de entrada por macro-fase viva cuando no exista commit estable posterior.
- Mantener paquetes en `dist/` hasta que exista una entrega superior verificada o el usuario apruebe su retirada.
- Mantener evidencia privada, licencias y comercial privado salvo decision explicita de Seguridad/Distribucion.
- Eliminar caches y artefactos regenerables despues de pruebas: `.pytest_cache/`, `output/`, `.playwright-*`, `analysis_output/` temporal.

## Nunca borrar automaticamente

- `dist/` de una entrega vigente.
- `license_keys/`, `licenses_private/`, `commercial-private/`, `private-commercial/`.
- Evidencias `private-evidence` o `release-evidence` sin manifiesto y aprobacion de ownership.
- Archivos versionados por git.
- Cualquier backup si el arbol de trabajo esta sucio y el backup podria ser la unica copia de cambios no commiteados.

## Manifiesto minimo

Antes de una poda agresiva, guardar un manifiesto ignorado en `backups/cleanup-<phase>-YYYYMMDD-HHMMSS/` con:

- listado de backups existentes;
- tamano aproximado;
- fecha de ultima modificacion;
- criterio de retencion aplicado;
- rutas eliminadas;
- rutas conservadas.

## Ownership

- `Backup/Artifact Steward`: decide retencion local, manifiestos y limpieza de artefactos pesados.
- `QA/Release`: protege paquetes `dist/`, checksums y evidencias de entrega.
- `Security/Distribution`: protege licencias, claves, buyer logs y material privado.
- `Architecture/Docs`: mantiene esta politica y referencias desde gobernanza.

## Verificacion minima

Para cambios de politica o limpieza documental:

- `git diff --check`
- `npm run test:js`
- `python -m pytest backend\sqx-edge-tool -q`

Para limpieza puramente local sin cambios versionados, registrar resultado en el resumen de fase y no hacer commit vacio.
