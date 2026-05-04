# SQX Edge - Setup

## Uso para usuario basico

Haz doble click en el archivo de la raiz:

```text
START_SQX_EDGE.bat
```

El launcher usa `backend\sqx-edge-tool\runtime\python\python.exe`, arranca la API local y abre `app\SQX_Dashboard_v6.html`.

Para cerrar la API:

```text
STOP_SQX_EDGE.bat
```

## Setup solo dashboard

Abre directamente:

```text
app\SQX_Dashboard_v6.html
```

El dashboard funciona offline. El tab Project Generator necesita la API local para generar `.cfx`, leer configuracion y limpiar `.sqx`.

## Preparar Python embebido

Si falta `backend\sqx-edge-tool\runtime\python\python.exe`, ejecuta una vez:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\bootstrap_embedded_python.ps1
```

## Uso tecnico

Arrancar API:

```bat
backend\sqx-edge-tool\run-web-embedded.bat
```

CLI:

```bat
backend\sqx-edge-tool\run-embedded.bat list
```

Config local:

```text
backend\sqx-edge-tool\config.json
```

Outputs generados:

```text
backend\sqx-edge-tool\output\
```

## Empaquetar

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\package_portable.ps1 -RequireEmbeddedPython
```

El paquete se genera en `dist/`.
