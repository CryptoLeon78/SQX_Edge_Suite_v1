# Pilot Purchase Kit

Este runbook convierte la release candidate comercial en una compra piloto verificable.

## Requisitos

- `commercial_release_candidate.py` en `GO`.
- ZIP portable final validado y con SHA256.
- Checkout privado Lemon Squeezy o Gumroad preparado.
- Private key fuera del repo.
- Email, nombre, plan y order id del cliente piloto.
- Ruta donde guardar la licencia firmada y la entrega final.

## Dry Run

```powershell
python backend\sqx-edge-tool\tools\pilot_purchase_kit.py --allow-no-go-commercial-rc --no-write
```

El `NO-GO` esperado antes de la compra real incluye:

- `pilot_customer_name_missing`
- `pilot_customer_email_missing_or_invalid`
- `pilot_order_id_missing`
- `signed_license_missing`
- `customer_delivery_manifest_missing`
- `license_import_not_confirmed`

## Flujo Real

1. Abrir el checkout privado.
2. Ejecutar una compra piloto real o controlada.
3. Confirmar order id, customer email y plan.
4. Emitir licencia:

```powershell
python backend\sqx-edge-tool\tools\license_issue.py --private-key C:\ruta\privada\sqx_private_key.json --out dist\pilot_licenses\SQX_Edge_Pro_license.json --customer-name "Cliente Piloto" --customer-email piloto@example.com --order-id lemon-order-123 --plan pro_monthly
```

5. Preparar entrega:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\prepare_customer_delivery.ps1 -ZipPath dist\SQX_Edge_Tool_Portable_YYYYMMDD_HHMMSS.zip -LicensePath dist\pilot_licenses\SQX_Edge_Pro_license.json -CustomerSlug cliente_piloto -OrderId lemon-order-123 -SupportEmail soporte@example.com
```

6. Extraer el ZIP, arrancar `START_SQX_EDGE.bat`, importar la licencia y confirmar estado Pro.
7. Ejecutar el kit con `--confirm-license-imported` y guardar evidencia.

## Criterios GO

- RC comercial en `GO`.
- ZIP portable existe.
- Customer y email validos.
- Order id presente.
- Plan valido: `pro_monthly`, `pro_annual` o `setup_assist`.
- Licencia firmada existe.
- Manifest de entrega existe.
- Licencia importada y Pro confirmado.

## Rollback

- Reembolsar o anular la compra piloto si no se puede completar la entrega.
- Desactivar enlace de checkout.
- Pausar webhook Lemon si hay duplicados o eventos rotos.
- Pausar worker Render si el dispatch falla.
- Entregar manualmente con licencia firmada si el pago ya se completo.

No abras venta publica hasta que este kit devuelva `GO`.
