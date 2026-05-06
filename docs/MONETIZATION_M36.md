# Monetization M36 - Limited Public Launch

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Convertir la compra piloto verificada en una compuerta para apertura publica limitada, con limite de primeras ventas, soporte preparado, checkout confirmado y rollback responsable.

## Entregables

- Estado `limited_public_launch_ready`.
- Tool `backend/sqx-edge-tool/tools/limited_public_launch.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-tool/data/limited_public_launch`.
- Consumo de evidencia M35 `pilot_purchase_kit`.
- Validacion de checkout HTTPS, variantes Lemon/Gumroad, email de soporte, first sale cap y ventana de lanzamiento.
- Confirmacion explicita de public checkout y support inbox.
- Guia `docs/sales/LIMITED_PUBLIC_LAUNCH.md`.

## Decision

M36 no declara `GO` sin piloto `GO`, URLs y variantes reales, soporte operativo, limite de ventas inicial y rollback con responsable.

## Uso

```powershell
python backend\sqx-edge-tool\tools\limited_public_launch.py --use-latest-pilot-kit --support-email soporte@example.com --first-sale-cap 5 --launch-window "2026-05-07 10:00-14:00 Europe/Madrid" --rollback-owner "Ivan" --confirm-public-checkout --confirm-support-inbox
```

Revision seca:

```powershell
python backend\sqx-edge-tool\tools\limited_public_launch.py --allow-no-go-pilot --no-write
```

## Siguiente Paso

M37 debe preparar el post-launch control: registro de primeras ventas, soporte de activaciones, decisiones de escalar/pausar y versionado de feedback.
