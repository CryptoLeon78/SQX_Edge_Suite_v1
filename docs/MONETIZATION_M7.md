# Phase M7 - Support And Diagnostics

## Goal

Reducir friccion de soporte para usuarios basicos sin capturar datos sensibles ni introducir telemetria.

M7 prepara un diagnostico local exportable que el usuario puede generar desde Inicio y enviar si pide ayuda.

## Scope

Incluido:

- Endpoint local `GET /api/support/diagnostics`.
- Boton en Inicio para descargar un JSON seguro.
- Payload con rutas, licencia, estrategias y localStorage excluidos.
- Contratos y tests para evitar regresiones de privacidad.
- Documentacion de soporte y riesgos residuales.

No incluido:

- Telemetria automatica.
- Subida a servidor.
- Captura de estrategias `.sqx`.
- Captura de `config.json` en bruto.
- Captura del archivo de licencia.

## Diagnostic Payload

El diagnostico incluye:

- version de la app
- canal de build
- estado resumido de licencia
- runtime Python sin ruta del ejecutable
- checks de configuracion con valores redacted
- contadores de manifiestos
- estado del ultimo ZIP/auditoria de distribucion
- feature gates activos
- `diagnostic_id` anonimo

El diagnostico no incluye:

- rutas completas
- nombre o id de cliente
- payload de licencia
- contenido de estrategias
- localStorage
- contenido completo de `config.json`

## Privacy Contract

Campos canonicos:

- `privacy.safe_to_send = true`
- `privacy.paths = redacted`
- `privacy.license_payload = excluded`
- `privacy.strategy_files = excluded`
- `privacy.local_storage = excluded`

Los paths se resumen como:

```json
{
  "configured": true,
  "exists": true,
  "redacted": true
}
```

Esto permite diagnosticar si algo esta configurado sin exponer la carpeta real del usuario.

## User Flow

1. El usuario abre `START_SQX_EDGE.bat`.
2. En Inicio pulsa `Generar diagnostico`.
3. El navegador descarga `SQX_support_diagnostic_<id>.json`.
4. El usuario envia ese JSON a soporte.
5. Soporte ve version, runtime, checks y estado de distribucion sin datos privados.

## Support Script

Mensaje recomendado para soporte:

```text
Abre SQX Edge, entra en Inicio y pulsa Generar diagnostico. Se descargara un JSON seguro que no incluye rutas personales, licencia ni estrategias. Adjuntalo a tu mensaje junto con una descripcion corta de lo que estabas intentando hacer.
```

## Residual Risk

El diagnostico se genera localmente y no se envia solo. Si un usuario edita manualmente el JSON antes de enviarlo, soporte debe tratarlo como informacion declarativa, no como prueba tecnica absoluta.

En una fase posterior convendra:

- anadir export de logs sanitizados
- generar un ZIP de soporte con consentimiento explicito
- incluir firma/hash del diagnostico
- permitir copiar resumen corto al portapapeles

## Decision M7

SQX Edge Pro queda preparado para soporte humano basico:

- diagnostico local de un click
- sin telemetria
- sin datos privados
- con contrato de privacidad testado
- listo para usar en beta comercial manual
