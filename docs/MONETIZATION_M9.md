# Phase M9 - Production License Key Management

Objetivo: convertir la activacion offline firmada de M8 en un flujo mas serio para venta Pro, separando claves publicas, claves privadas y artefactos de entrega.

## Decision

- La app sigue verificando licencias offline con `rsa_sha256_pkcs1_v1_5` (`RS256`).
- La clave publica vive en `config/product_manifest.json` y se distribuye dentro del ZIP.
- La clave privada se genera y se guarda fuera del repo, fuera de backups y fuera del ZIP portable.
- La politica formal del manifiesto es `never_commit_never_ship` para cualquier private key.
- `license_keypair.ps1` genera un par RSA local compatible con `license_signer.py`.
- `license_signer.py` y `license_keypair.ps1` son herramientas internas y no se empaquetan para usuario final.
- Antes de vender un build publico hay que sustituir la public key placeholder por una public key de produccion real.

## Manual License Issuance Flow

1. Generar claves:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\license_keypair.ps1 -OutDir C:\SQX_PRIVATE_KEYS -KeyId sqx-prod-2026-05-v1
   ```

2. Copiar solo el JSON publico a `backend/sqx-edge-tool/config/product_manifest.json`, dentro de `licensing.publicKey`.

3. Crear un payload de licencia sin `signature`.

4. Firmar la licencia con la private key guardada fuera del repo:

   ```powershell
   backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\license_signer.py --private-key C:\SQX_PRIVATE_KEYS\sqx-prod-2026-05-v1_private_key.json --payload C:\SQX_PRIVATE_KEYS\payload.json --out C:\SQX_PRIVATE_KEYS\license_signed_cliente.json
   ```

5. Entregar al cliente solo `license_signed_cliente.json`.

## Release Guardrails

- `.gitignore` ignora carpetas locales de claves y patrones de licencias firmadas.
- `package_portable.ps1` excluye claves privadas, licencias firmadas y tools internos de licencias.
- `audit_distribution.ps1` falla si detecta claves privadas, licencias firmadas o tools internos dentro del ZIP.
- `release_checklist.ps1` valida que el ZIP final no contenga herramientas de firma ni carpetas privadas.

## Residual Risks

- La public key placeholder no debe usarse para venta publica.
- El flujo manual es correcto para beta/primeras ventas, pero conviene automatizar fulfillment cuando haya volumen.
- La proteccion offline reduce manipulacion casual, pero no sustituye ofuscacion o hardening avanzado si el producto escala.

Estado: Done.
