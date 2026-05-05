# Phase M8 - Offline Signed License Activation

## Goal

Activar SQX Edge Pro con una licencia local firmada, sin internet y sin guardar secretos privados dentro del ZIP portable.

M8 convierte el modelo definido en M2/M4 en enforcement real:

- el backend verifica firma RS256 offline
- una licencia Pro valida activa `pro_active`
- una licencia manipulada queda `invalid`
- una licencia expirada conserva datos pero bloquea funciones Pro
- el frontend permite cargar y limpiar licencia desde Inicio

## License Format

Licencia JSON canonica:

```json
{
  "schema_version": 1,
  "license_id": "LIC-XXXX",
  "customer_name": "Cliente",
  "plan": "pro_monthly",
  "issued_at": "2026-05-05",
  "expires_at": "2026-06-05",
  "signature_algorithm": "RS256",
  "public_key_id": "sqx-prod-2026-05-placeholder",
  "signature": "..."
}
```

La firma se calcula sobre el JSON sin el campo `signature`, con claves ordenadas y separadores compactos.

## Cryptography

Modo activo:

- `rsa_sha256_pkcs1_v1_5`
- `RS256`
- verificacion con public key embebida en `product_manifest.json`
- private key fuera del repo y fuera del ZIP

El backend usa solo libreria estandar de Python:

- `hashlib`
- `hmac`
- `base64`
- aritmetica RSA con `pow`

Esto evita dependencias adicionales en la entrega portable.

## Backend Endpoints

Endpoints M8:

- `GET /api/license/status`
- `POST /api/license/check`
- `POST /api/license/import`
- `POST /api/license/clear`

`POST /api/license/import` solo instala la licencia en `config/license.json` si la firma es valida.

`POST /api/license/clear` elimina la licencia local y vuelve al estado de build/perfil.

## Feature Enforcement

Cuando una licencia Pro firmada esta activa:

- `project_generator.generate` queda permitido
- `strategy_cleaner.apply` queda permitido
- el estado reporta `pro_active`
- `check_feature()` devuelve `allowed = true`

Cuando la licencia falta, expira o se manipula:

- el estado vuelve a features Free
- endpoints Pro responden `402 pro_required`
- los datos del usuario no se borran

## Signing Tool

Herramienta dev:

```text
backend/sqx-edge-tool/tools/license_signer.py
```

Uso:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\license_signer.py `
  --private-key C:\secure\sqx_private_key.json `
  --payload C:\secure\license_unsigned.json `
  --out C:\secure\license_signed.json
```

La private key nunca debe guardarse en el repo, en backups compartidos ni en el ZIP portable.

`license_signer.py` queda excluido del ZIP para usuario final.

## UI Flow

1. El usuario recibe `license_signed.json`.
2. Abre Inicio.
3. Pega el JSON en el panel Licencia.
4. Pulsa `Cargar licencia`.
5. La API local verifica e instala la licencia.
6. El backend usa `config/license.json` para activar Pro.

## Security Notes

Protecciones:

- firma asymmetric offline
- public key only en app
- private key fuera de distribucion
- `config/license.json` excluido del ZIP
- importacion rechaza firma invalida
- tests cubren activacion, manipulacion y expiracion

Riesgos residuales:

- el public key actual es placeholder y debe reemplazarse antes de venta publica
- no hay vinculacion por equipo todavia
- no hay revocacion online
- no hay firma Authenticode del paquete Windows

## Decision M8

SQX Edge Pro ya puede activar funciones Pro con una licencia local firmada y verificada offline.

Esto permite una beta comercial manual:

- cobro externo
- generacion manual de licencia
- envio del JSON firmado
- activacion local en un click dentro de la app
