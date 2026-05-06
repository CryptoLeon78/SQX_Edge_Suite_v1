# Phase M15 - Trusted Relay Ingest

Objetivo: preparar un punto de entrada local y privado para bundles firmados por un relay remoto confiado, evitando exponer directamente el backend local a internet.

## Decision

- El estado contractual de esta fase pasa a `relay_ingest_ready`.
- El endpoint local es `POST /api/fulfillment/relay-ingest`.
- El header de firma del relay es `X-SQX-Relay-Signature`.
- El secreto local del relay se toma desde `SQX_FULFILLMENT_RELAY_SECRET`.
- El modo oficial de esta fase es `trusted_remote_relay_signed_bundle`.

## Flow

1. Lemon Squeezy envia webhook al relay remoto.
2. El relay remoto verifica `X-Signature` con el secreto de Lemon.
3. El relay normaliza o empaqueta el evento en un bundle firmado.
4. El backend local recibe el bundle en `/api/fulfillment/relay-ingest`.
5. La cola privada aplica deduplicacion por `provider_event_id`.
6. El operador procesa la request desde el queue cockpit.

## Technical Pieces

- `relay_bundle.py` genera bundles de prueba o bundles manuales firmados.
- `relay_event_id` identifica el salto relay -> local.
- `relay_event_*.json` queda excluido del ZIP portable final.
- La cola sigue siendo el source of truth local.

## Security Notes

- El secreto del relay es distinto del secreto de Lemon Squeezy.
- El relay no debe compartir la private key de licencias.
- La emision de licencia sigue ocurriendo solo en el entorno privado del operador.
- El backend local no necesita quedar publicado en internet.

## Risks Still Open

- Falta implementar el relay remoto real como servicio desplegable.
- Falta rotacion documentada de `SQX_FULFILLMENT_RELAY_SECRET`.
- Falta un canal seguro operativo para entornos con NAT o equipos portables desconectados.

Estado: Done.
