# Phase M10 - Manual Pro License Issuer

Objetivo: reducir el error humano al emitir licencias Pro para ventas manuales, usando un comando interno que crea y firma el JSON final listo para entregar al cliente.

## Decision

- `license_issue.py` queda como capa operativa por encima de `license_signer.py`.
- El vendedor/soporte ya no necesita escribir el payload completo a mano.
- La herramienta acepta cliente, email, plan, pedido, fechas, limite de equipos, soporte y notas.
- La salida es una licencia firmada con `RS256` compatible con la activacion offline existente.
- `license_issue.py` no se incluye en el ZIP portable para usuario final.

## Example

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\license_issue.py --private-key C:\SQX_PRIVATE_KEYS\sqx-prod-2026-05-v1_private_key.json --customer-name "Cliente Demo" --customer-email cliente@example.com --plan pro_monthly --order-id LS-ORDER-001 --out C:\SQX_PRIVATE_KEYS\license_signed_cliente_demo.json
```

## Defaults

- `pro_monthly`: 31 dias.
- `pro_annual`: 366 dias.
- `setup_assist`: 31 dias.
- `machine_limit`: 1.
- `support_level`: `standard`.
- `license_id`: generado como `SQX-YYYYMMDD-XXXXXXXX`.

## Release Guardrails

- `.gitignore` ignora payloads sin firmar y licencias firmadas generadas localmente.
- `package_portable.ps1` excluye `license_issue.py`.
- `audit_distribution.ps1` falla si el ZIP contiene el issuer interno o artefactos locales de licencias.
- `release_checklist.ps1` valida que el issuer no viaje al usuario final.

## Residual Risks

- El flujo sigue siendo manual; es correcto para beta/primeras ventas, pero debe conectarse a Lemon Squeezy/Gumroad cuando haya volumen.
- Las notas dentro de una licencia entregada al cliente deben ser sobrias, porque el cliente puede abrir el JSON.
- El issuer no debe ejecutarse con claves privadas guardadas dentro del repo.

Estado: Done.
