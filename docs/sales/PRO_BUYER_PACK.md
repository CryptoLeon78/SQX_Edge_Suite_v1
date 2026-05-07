# Pro Buyer Pack

El Pro Buyer Pack es el material que acompana al comprador Pro dentro del ZIP portable.

## Incluido

- Universo inicial de activos: 28 Forex, 4 indices y oro.
- CSV importable en Estrategias.
- Checklist de activacion de licencia.
- Plantilla starter para Project Generator.
- Plantilla de solicitud de soporte.
- Checklist de primer valor.

## No incluido

- Payloads de licencia de clientes.
- Private keys.
- Eventos checkout crudos.
- Secretos del relay.
- Datos personales de compradores.
- Promesas de rentabilidad o asesoramiento financiero.

## Operacion

Antes de publicar un ZIP comercial, ejecutar:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\pro_buyer_pack.py
```

El resultado debe ser `GO` y generar evidencia local en `backend/sqx-edge-tool/data/pro_buyer_pack`.
