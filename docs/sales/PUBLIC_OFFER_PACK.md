# Public Offer Pack

Este runbook convierte el feedback revisado en una oferta publica controlada y entendible para un comprador basico.

## Requisitos

- `commercial_feedback_loop.py` en `GO`.
- ZIP portable final validado.
- Capturas recientes.
- `offer_headline` y subheadline revisados.
- FAQ comercial preparada.
- Release notes legibles.
- Buyer steps para usuario no tecnico.
- Copy de soporte preparado.
- Checkout preparado.
- Claims seguros revisados.

## buyer steps

1. Descargar el ZIP portable.
2. Descomprimir la carpeta.
3. Hacer doble click en `START_SQX_EDGE.bat`.
4. Abrir Inicio > Licencia.
5. Importar el JSON de licencia Pro firmado.
6. Generar diagnostico de soporte si la activacion falla.

## Dry Run

```powershell
python backend\sqx-edge-tool\tools\public_offer_pack.py --allow-no-go-feedback --no-write
```

Bloqueos esperados hasta tener oferta publica real:

- `commercial_feedback_loop_missing` o `commercial_feedback_loop_not_go`
- `offer_headline_missing`
- `offer_subheadline_missing`
- `faq_not_ready`
- `release_notes_not_ready`
- `buyer_steps_not_ready`
- `support_copy_not_ready`
- `safe_claims_not_reviewed`
- `checkout_not_ready`
- `public_page_not_ready`

## Flujo Real

```powershell
python backend\sqx-edge-tool\tools\public_offer_pack.py --use-latest-feedback --offer-headline "SQX Edge Pro" --offer-subheadline "Ordena tu flujo StrategyQuant X con una app portable, local y guiada." --confirm-faq-ready --confirm-release-notes-ready --confirm-buyer-steps-ready --confirm-support-copy-ready --confirm-safe-claims-reviewed --confirm-checkout-ready --confirm-public-page-ready
```

## Claims Prohibidos

- Rentabilidad garantizada.
- Beneficios garantizados.
- Estrategias ganadoras.
- Resultados financieros garantizados.

## Secciones De Oferta

- Headline.
- Subheadline.
- Audiencia.
- Que incluye.
- FAQ.
- Claims seguros.
- Release notes.
- Buyer steps.
- Soporte.
- Disclaimer.

No publiques la oferta si el comprador no puede entender como descargar, arrancar, activar y pedir ayuda.
