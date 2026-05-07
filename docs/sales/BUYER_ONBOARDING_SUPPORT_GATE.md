# Buyer Onboarding Support Gate

## Objetivo

Usar este gate antes de entregar o activar el primer grupo de compradores Pro. El foco es que una persona basica pueda comprar, descomprimir, abrir, activar licencia y pedir soporte sin improvisacion.

## Checklist de entrega

- Pago u orden confirmada.
- Plan identificado: `pro_monthly`, `pro_annual` o `setup_assist`.
- ZIP portable final preparado.
- Licencia Pro firmada preparada.
- `START_HERE.md` incluido o adjunto.
- FAQ basica incluida.
- Plantilla de soporte incluida.
- Claims seguros revisados.

## Criterios NO-GO

- Falta email u order id.
- Falta ZIP o licencia.
- No se ha revisado la activacion.
- No hay canal de soporte preparado.
- Hay tickets abiertos del comprador.
- Hay errores de activacion pendientes.
- El comprador espera rentabilidad, resultados financieros o consejos de inversion.

## Criterios de pausa o reembolso

- El usuario no puede arrancar la app tras seguir la guia.
- La licencia no activa Pro y no se resuelve con soporte inicial.
- El comprador compro esperando resultados financieros.
- Hay un fallo critico reproducible que bloquea el uso basico.

Codigo de bloqueo operativo: `refund_or_pause_risk_unreviewed`.

## Comando recomendado

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\buyer_onboarding_support_gate.py `
  --customer-email cliente@example.com `
  --order-id ORDER-001 `
  --plan pro_monthly `
  --confirm-purchase-confirmed `
  --confirm-portable-zip-ready `
  --confirm-license-file-ready `
  --confirm-start-here-attached `
  --confirm-activation-steps-reviewed `
  --confirm-support-contact-ready `
  --confirm-faq-ready `
  --confirm-safe-claims-reviewed
```

La evidencia se guarda en `backend/sqx-edge-tool/data/buyer_onboarding_support_gate` y no debe viajar en el ZIP portable.
