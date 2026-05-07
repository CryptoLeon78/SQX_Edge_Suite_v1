# SQX Edge Pro - Sales Fulfillment Runbook

## Preflight

- ZIP portable final validado con `release_checklist.ps1`.
- Public key de produccion ya configurada en `product_manifest.json`.
- Private key guardada fuera del repo.
- Checkout URL real configurada en `product_manifest.json` si se va a mostrar en la app.
- Email de soporte definido.
- `checkout_live_readiness.py` ejecutado y en `GO` antes de publicar enlaces.
- `commercial_release_candidate.py` ejecutado y en `GO` antes de abrir venta publica.
- `pilot_purchase_kit.py` ejecutado y en `GO` para el primer piloto antes de abrir venta publica.
- `limited_public_launch.py` ejecutado y en `GO` antes de compartir un enlace publico limitado.
- `post_launch_control.py` ejecutado antes de escalar mas alla de la venta limitada.
- `commercial_feedback_loop.py` ejecutado antes de cambiar precio, copy u oferta.
- `public_offer_pack.py` ejecutado antes de publicar pagina u oferta abierta.
- `launch_assets_kit.py` ejecutado antes de crear release publica o publicar assets.
- `public_release_gate.py` ejecutado antes de publicar tag/release final con ZIP y SHA256.
- `release_publication_record.py` ejecutado despues de publicar para registrar tag, release, ZIP, SHA256 y rollback.
- `post_release_monitor.py` ejecutado durante la ventana post-release para decidir mantener, pausar, hotfix, rollback o escalar.
- `hotfix_rollback_release.py` ejecutado si hay que pausar, corregir, hacer rollback o cerrar una incidencia post-release.

## Sale To Delivery

1. Revisar pedido en Lemon Squeezy o Gumroad.
2. Identificar plan: `pro_monthly`, `pro_annual` o `setup_assist`.
3. Ejecutar `license_issue.py` con `--order-id`.
4. Ejecutar `prepare_customer_delivery.ps1`.
5. Enviar carpeta de entrega o subirla a una descarga privada.
6. Registrar internamente customer, order id, license id y fecha de expiracion.

## Customer Email Template

Asunto: SQX Edge Pro - descarga y licencia

Hola,

Gracias por adquirir SQX Edge Pro.

Adjunto tienes:

- ZIP portable de SQX Edge.
- Archivo `SQX_Edge_Pro_license.json`.
- Archivo `LEEME_PRIMERO.txt` con los pasos.

Pasos rapidos:

1. Descomprime el ZIP.
2. Ejecuta `START_SQX_EDGE.bat`.
3. Abre Inicio > Licencia.
4. Pega el contenido de `SQX_Edge_Pro_license.json`.
5. Pulsa `Cargar licencia`.

Si tienes cualquier problema, responde a este email con el diagnostico de soporte generado desde Inicio.

## Internal Renewal

- Para mensual: emitir una nueva licencia si el proveedor confirma renovacion.
- Para anual: emitir una licencia con duracion anual.
- Para cancelacion: dejar que expire la licencia local en la siguiente fecha de corte.

## Notes

- No prometer rentabilidad.
- Vender productividad, trazabilidad y reduccion de errores operativos.
- No enviar private keys ni herramientas internas.
