# Phase M11 - Checkout And Manual Fulfillment

Objetivo: preparar una venta real de SQX Edge Pro sin construir todavia una plataforma propia de cuentas, usando checkout hospedado y fulfillment manual seguro.

## Decision

- Canal principal: Lemon Squeezy con checkout hospedado.
- Canal alternativo: Gumroad para validar packs o venta simple si Lemon Squeezy tarda.
- La app sigue usando licencia offline firmada propia.
- El checkout del proveedor sirve para cobrar y registrar pedido; la licencia entregada al cliente se genera con `license_issue.py`.
- La entrega por cliente se prepara con `prepare_customer_delivery.ps1`.

## Provider Setup

### Lemon Squeezy

1. Crear producto `SQX Edge Pro`.
2. Crear variantes:
   - `SQX Edge Pro Mensual` -> `pro_monthly`, 24 EUR/mes.
   - `SQX Edge Pro Anual` -> `pro_annual`, 199 EUR/ano.
   - `Setup Assist` -> `setup_assist`, 149 EUR.
3. Activar license keys del proveedor con activation limit 1 para trazabilidad comercial.
4. Guardar los variant ids y checkout URLs en `product_manifest.json`.
5. Configurar receipt/email con instrucciones de entrega manual.
6. En una fase posterior, configurar webhooks para automatizar la emision de licencia firmada.

### Gumroad Fallback

1. Crear producto digital `SQX Edge Pro`.
2. Crear variantes o productos separados para mensual/anual/setup.
3. Activar license keys si se usa como prueba comercial.
4. Entregar ZIP + licencia manualmente hasta automatizar.

## Manual Fulfillment Flow

1. Confirmar pago y plan comprado.
2. Generar licencia:

   ```powershell
   backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\license_issue.py --private-key C:\SQX_PRIVATE_KEYS\sqx-prod-2026-05-v1_private_key.json --customer-name "Cliente Demo" --customer-email cliente@example.com --plan pro_monthly --order-id LS-ORDER-001 --out C:\SQX_PRIVATE_KEYS\license_signed_cliente_demo.json
   ```

3. Preparar carpeta de entrega:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\prepare_customer_delivery.ps1 -ZipPath dist\SQX_Edge_Tool_Portable_YYYYMMDD_HHMMSS.zip -LicensePath C:\SQX_PRIVATE_KEYS\license_signed_cliente_demo.json -CustomerSlug cliente_demo -OrderId LS-ORDER-001 -SupportEmail soporte@example.com
   ```

4. Enviar al cliente:
   - ZIP portable.
   - `SQX_Edge_Pro_license.json`.
   - `LEEME_PRIMERO.txt`.
   - SHA256 si el cliente necesita verificar descarga.

## In-App Checkout Wiring

- `product_manifest.json` incluye `upgrade.checkout`.
- El panel Licencia tiene `license-checkout-link`.
- Mientras `checkout.primaryUrl` este vacio, el enlace queda oculto para evitar botones rotos.
- Cuando exista URL real de Lemon Squeezy, se puede activar sin tocar JS.

## Official References Checked

- Lemon Squeezy checkout hospedado/overlay y custom checkout: https://docs.lemonsqueezy.com/help/checkout
- Lemon Squeezy variants con license key settings: https://docs.lemonsqueezy.com/api/variants/the-variant-object
- Lemon Squeezy license keys para activacion, expiracion y activation limit: https://docs.lemonsqueezy.com/help/licensing/generating-license-keys
- Lemon Squeezy License API: https://docs.lemonsqueezy.com/api/license-api
- Lemon Squeezy webhooks para automatizacion posterior: https://docs.lemonsqueezy.com/help/webhooks
- Gumroad queda como alternativa de validacion simple.

## Residual Risks

- Todavia no hay webhook ni fulfillment automatico.
- El cliente recibe una licencia JSON propia, no solo la license key del proveedor.
- Hay que sustituir URLs e IDs placeholder antes de publicar.
- El correo de soporte real debe decidirse antes de vender.

Estado: Done.
