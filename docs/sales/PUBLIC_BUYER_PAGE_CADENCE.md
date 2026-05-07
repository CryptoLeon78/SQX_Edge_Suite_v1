# Public Buyer Page Checklist And First-Sale Cadence

Esta fase prepara una pagina/checklist publico de comprador sin prisa: copy claro, pasos simples, soporte visible y una cadencia de primera venta que no genere ansiedad operativa.

## Checklist de pagina

- Nombre de producto y oferta exacta.
- Para quien es y para quien no es.
- Que recibe el comprador: ZIP portable, licencia Pro, onboarding y soporte.
- Precio, condiciones y politica de soporte/refund explicadas sin letra pequena.
- Pasos basicos: descargar, descomprimir, doble click, importar licencia, pedir ayuda.
- Primer valor esperado: abrir la app, ver Pro activo y localizar CSV/plantillas iniciales sin tocar datos sensibles.
- Aviso responsable: no promete rentabilidad ni resultados financieros.
- Preguntas frecuentes y soporte visible.
- Rollback operativo: pausar checkout, pausar webhook/worker y volver a entrega manual.

## Cadencia primera venta

1. Publicar primero como enlace privado o audiencia controlada.
2. Confirmar una compra real y registrar order id sin payloads crudos.
3. Entregar ZIP y licencia firmada con instrucciones basicas.
4. Acompanhar la activacion y registrar fricciones agregadas.
5. Esperar feedback temprano antes de ampliar trafico.
6. Pausar ventas si aparece soporte abierto, refund, claim risk o fallo de entrega.

## Comando base

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\public_buyer_page_cadence.py `
  --use-latest-buyer-ready-closeout `
  --public-page-sections 7 `
  --cadence-steps 6 `
  --page-status private_link_ready `
  --support-cadence "same-day priority email for first controlled buyers" `
  --first-sale-owner "operator" `
  --decision keep_draft `
  --cadence-notes "Public buyer checklist and first-sale cadence reviewed; keep the page private until the next controlled buyer." `
  --confirm-buyer-ready-closeout-go `
  --confirm-public-copy-reviewed `
  --confirm-price-terms-reviewed `
  --confirm-buyer-steps-reviewed `
  --confirm-support-cadence-reviewed `
  --confirm-first-sale-cadence-reviewed `
  --confirm-safe-claims-reviewed `
  --confirm-rollback-reviewed
```

## Decisiones

- `publish_private_page`: activar enlace privado/controlado para primera venta.
- `keep_draft`: dejar preparado y esperar otra revision o ventana operativa.
- `revise_copy`: mejorar copy, FAQ, claims, pasos de comprador o soporte.
- `pause_sales`: detener si hay riesgo operativo, soporte, refund, claim o entrega.

## Privacidad

No guardar nombres, emails, licencias firmadas, payloads del proveedor, secretos ni mensajes crudos de comprador. Solo estado agregado y decisiones operativas.
