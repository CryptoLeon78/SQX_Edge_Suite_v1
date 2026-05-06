# Monetization M35 - Pilot Purchase Kit

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar la compra piloto privada con checkout real o controlado, orden trazable, licencia Pro firmada, entrega al cliente e importacion verificada en la app.

## Entregables

- Estado `pilot_purchase_kit_ready`.
- Tool `backend/sqx-edge-tool/tools/pilot_purchase_kit.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-tool/data/pilot_purchase_kit`.
- Consumo de evidencia M34 `commercial_release_candidate`.
- Comandos guiados para `license_issue.py` y `prepare_customer_delivery.ps1`.
- Validacion de customer, order id, plan, licencia firmada, manifest de entrega e importacion Pro.
- Guia `docs/sales/PILOT_PURCHASE_KIT.md`.

## Decision

M35 no declara `GO` sin licencia Pro firmada, manifest de entrega y confirmacion explicita de que la licencia se importo en SQX Edge.

## Uso

```powershell
python backend\sqx-edge-tool\tools\pilot_purchase_kit.py --use-latest-commercial-rc --customer-name "Cliente Piloto" --customer-email piloto@example.com --order-id lemon-order-123 --plan pro_monthly --signed-license dist\pilot_licenses\SQX_Edge_Pro_license.json --delivery-manifest dist\customer_deliveries\cliente_piloto\delivery_manifest.json --confirm-license-imported
```

Revision seca:

```powershell
python backend\sqx-edge-tool\tools\pilot_purchase_kit.py --allow-no-go-commercial-rc --no-write
```

## Siguiente Paso

M36 debe convertir la evidencia del piloto en una checklist de lanzamiento publico limitado: primera venta abierta, soporte post-compra y cierre de rollback.
