# Phase M3 - Distribution And Paid Delivery Flow

## Decision

Para el primer lanzamiento comercial de SQX Edge Pro, el canal recomendado es:

- Lemon Squeezy como canal principal de cobro, suscripcion y entrega de licencia.
- ZIP portable de SQX Edge como artefacto principal.
- GitHub Releases para builds publicos o controlados.
- Gumroad como alternativa simple para packs/plantillas si se quiere validar rapido.
- Stripe Payment Links solo como alternativa si construimos nuestro propio sistema de licencias y fulfillment.
- Paddle como opcion futura si el producto escala y necesita billing mas avanzado.

Esta fase no implementa cobros dentro de la app. Define el flujo de venta y entrega que debe guiar M4.

## Research Snapshot

Fecha de revision: 2026-05-05.

Fuentes revisadas:

- Lemon Squeezy License Keys: https://docs.lemonsqueezy.com/help/licensing/generating-license-keys
- Lemon Squeezy Pricing: https://www.lemonsqueezy.com/pricing
- Gumroad Pricing: https://gumroad.com/pricing
- Gumroad Features: https://gumroad.com/features
- Stripe Payment Links: https://stripe.com/payments/payment-links
- Stripe Payment Links Docs: https://docs.stripe.com/payment-links
- Paddle Billing: https://www.paddle.com/billing

Resumen:

- Lemon Squeezy soporta claves de licencia, limites de activacion, licencias asociadas a suscripciones, webhooks y Merchant of Record.
- Gumroad permite vender productos digitales, membresias, suscripciones y generar license keys, con friccion baja para creadores.
- Stripe Payment Links permite vender productos y suscripciones sin codigo, pero requiere mas trabajo propio para entregar licencias, archivos y estado de acceso.
- Paddle es fuerte para SaaS y billing avanzado como Merchant of Record, pero es mas pesado para una primera validacion indie.

## Recommended Product Setup

### Product 1 - SQX Edge Pro Monthly

Precio recomendado desde M1: 24 EUR/mes.

Configuracion:

- payment type: subscription
- license keys: enabled
- activation limit: 1
- customer receives license key after purchase
- receipt message includes download instructions
- product note links to latest portable ZIP

Acceso:

- `plan`: `pro_monthly`
- `features`: Pro core features
- renewal required to keep Pro active

### Product 2 - SQX Edge Pro Annual

Precio recomendado desde M1: 199 EUR/ano.

Configuracion:

- payment type: subscription
- license keys: enabled
- activation limit: 1
- annual billing
- customer receives license key after purchase

Acceso:

- `plan`: `pro_annual`
- `features`: same Pro core features

### Product 3 - Setup Assist

Precio recomendado desde M1: 149 EUR pago unico.

Configuracion:

- payment type: one-time
- no automatic app unlock required
- delivery: booking/contact instructions
- optional intake form

Acceso:

- no app feature required at launch
- manual service fulfillment

### Product 4 - Premium Template Pack 1

Precio recomendado desde M1: 79 EUR pago unico.

Configuracion:

- payment type: one-time
- digital download or protected delivery page
- license key optional
- pack version included in receipt

Acceso:

- `features`: `template_pack_1`
- can later be imported into SQX Edge

## Delivery Flow V1

### Free User Flow

1. User visits public page.
2. Downloads SQX Edge Free portable ZIP.
3. Extracts ZIP.
4. Double-clicks `START_SQX_EDGE.bat`.
5. Uses dashboard and demo workflows.
6. Sees Pro functions with upgrade path.

### Pro User Flow

1. User buys Monthly or Annual Pro.
2. Lemon Squeezy sends receipt and license key.
3. User downloads the portable ZIP from the receipt or release page.
4. User extracts ZIP.
5. User starts the app with one click.
6. User opens License / Activar Pro.
7. User pastes license key or imports license file.
8. App validates license.
9. Pro features become available.

### Manual License Flow For V1

Until the app has full online activation, use one of these safe options:

Option A:

- buyer receives Lemon Squeezy license key
- user sends key/email manually for activation
- we generate signed local license file
- user imports license file

Option B:

- buyer receives Lemon Squeezy license key
- M4 app validates key against a small local/offline license bridge once we implement it

Recommended for first paid beta: Option A.

Reason:

- fastest to ship
- less backend risk
- avoids exposing private signing keys
- lets us learn from real buyers before automating

## Release Distribution

### Public Free Build

Recommended channel:

- GitHub Releases
- public ZIP
- clear README for non-technical users

Contains:

- Free features
- demo data
- upgrade messaging
- no private keys
- no personal paths

### Pro Build

Recommended initial channel:

- same codebase with license-gated features
- Pro enabled by signed license
- not a separate secret ZIP unless needed

Reason:

- fewer support problems
- simpler updates
- easier verification
- same portable packaging flow

### Premium Packs

Recommended channel:

- Lemon Squeezy file delivery or private download page
- pack checksum
- pack version
- install instructions

Future:

- in-app import wizard
- pack manifest validation
- pack license check

## Customer Messages

### Receipt Message

Recommended copy:

```text
Gracias por comprar SQX Edge Pro.

1. Descarga el ZIP portable desde el enlace de esta compra.
2. Descomprime la carpeta.
3. Haz doble click en START_SQX_EDGE.bat.
4. Abre la seccion Activar Pro.
5. Usa tu licencia para activar las funciones Pro.

Si necesitas ayuda con la instalacion, responde a este email.
```

### Upgrade Message In App

Recommended copy:

```text
Esta funcion forma parte de SQX Edge Pro.
Activa Pro para usar Project Generator, Strategy Cleaner y workflows premium.
```

### Expired Subscription Message

Recommended copy:

```text
Tu licencia Pro ha expirado. Tus datos siguen disponibles en modo Free.
Renueva tu licencia para volver a activar las funciones Pro.
```

## Operational Checklist

Before first paid beta:

- Create Lemon Squeezy store.
- Create Monthly Pro product.
- Create Annual Pro product.
- Enable license keys with activation limit 1.
- Create Setup Assist product.
- Create Template Pack 1 product.
- Prepare public download page or GitHub Release.
- Prepare receipt copy.
- Prepare refund policy.
- Prepare privacy policy.
- Prepare terms/license terms.
- Prepare manual license generation process.
- Prepare support email.
- Test purchase in sandbox/test mode.
- Test receipt flow.
- Test license delivery flow.
- Test ZIP download on clean Windows user flow.

## Provider Comparison

| Provider | Best Use | Strength | Risk |
| --- | --- | --- | --- |
| Lemon Squeezy | Main Pro launch | MoR, subscriptions, license keys, activation limits | Need account approval and operational setup |
| Gumroad | Fast template/service validation | Simple creator storefront, memberships, license keys | Less ideal for polished software licensing |
| Stripe Payment Links | Custom future stack | Strong payments, links, subscriptions | Need our own tax/licensing/fulfillment stack unless extra Stripe services are added |
| Paddle | Later scale-up | MoR, SaaS billing, subscriptions | Heavier than needed for first beta |

## GitHub Release Strategy

Recommended release names:

- `SQX Edge Free v0.9.x`
- `SQX Edge Pro Beta v0.9.x`
- `SQX Edge Pro v1.0.0`

Artifacts:

- `SQX_Edge_Suite_Portable_vX.Y.Z.zip`
- `SQX_release_summary.txt`
- `CHANGELOG.md`
- optional checksum file

Release notes should include:

- what changed
- how to install
- how to activate Pro
- known limitations
- support contact
- no trading profit promises

## Risk Controls

- Do not store payment credentials in the app.
- Do not store private license signing keys in the repo.
- Do not make payment provider APIs required for normal daily offline use.
- Do not publish Pro-only packs directly inside the public Free ZIP.
- Do not promise investment outcomes.
- Do not let frontend-only checks protect write actions.
- Do not make activation impossible for non-technical users.

## Final Recommendation

Use this sequence:

1. Launch a Free public ZIP via GitHub Releases.
2. Sell Pro Monthly and Pro Annual with Lemon Squeezy.
3. Start paid beta with manual signed license delivery.
4. Sell Setup Assist manually as a one-time service.
5. Sell Template Pack 1 as a separate one-time product.
6. Implement in-app license activation in M4.
7. Automate license lifecycle later only after real buyers validate the offer.

This keeps SQX Edge sellable quickly, protects the product enough, and avoids building a complex commerce backend before the market tells us it is worth it.
