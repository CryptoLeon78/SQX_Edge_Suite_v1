# SQX Edge - Setup

## Uso para usuario basico
Haz doble click en: START_SQX_EDGE.bat
El launcher usa backend\sqx-edge-tool\runtime\python\python.exe, arranca la
API local y abre app\SQX_Dashboard_v6.html.
Para cerrar: STOP_SQX_EDGE.bat

## Setup solo dashboard
Abre directamente: app\SQX_Dashboard_v6.html
El dashboard funciona offline. El tab Project Generator necesita la API local
para generar .cfx, leer configuracion y limpiar .sqx.

## Preparar Python embebido
Si falta runtime\python\python.exe, ejecuta una vez:
  powershell -NoProfile -ExecutionPolicy Bypass -File
    backend\sqx-edge-tool\tools\bootstrap_embedded_python.ps1

## Vincular SQX la primera vez
El tab Project Generator lee la data.db de StrategyQuant X para obtener
spread/swap/commission reales por simbolo. Hay que vincular la ruta de SQX
una sola vez.

Por el dashboard (recomendado):
  Project Generator -> SQX install path -> Autodetect -> Guardar

Importante: Autodetect y Validate solo DEVUELVEN la ruta; NO la guardan.
La persistencia la hace POST /api/config, que escribe la clave sqx_data_db
en backend\sqx-edge-tool\config.json.

Equivalente por PowerShell (con la API ya arrancada):
  $body = @{ sqx_path = "C:\StrategyQuantX144"; sqx_data_db = "C:\StrategyQuantX144\user\data\data.db" } | ConvertTo-Json
  Invoke-RestMethod -Method Post http://127.0.0.1:5050/api/config -ContentType "application/json" -Body $body

Sin este paso, /api/symbol-info/<activo> e /api/instruments devuelven 404
y la Auditoria del dashboard queda en 5/6 (SQX Path: ruta pendiente).

## Puerto 5050 y StrategyQuant X
La API local usa el puerto 5050, que coincide con el puerto web por defecto
de StrategyQuant X (rango 5050:5059). Si SQX esta abierto, el arranque puede
fallar por puerto ocupado.

Opciones:
  - Arrancar la app con SQX cerrado (lo mas simple).
  - O mover el puerto de SQX: clave WebServerPort en
    C:\StrategyQuantX144\user\settings\settings.xml (p.ej. 5060) y reiniciar SQX.

## Verificacion (setup completo)
Con la API arrancada:
  Invoke-RestMethod http://127.0.0.1:5050/api/health
  Invoke-RestMethod http://127.0.0.1:5050/api/config              # debe incluir sqx_data_db
  Invoke-RestMethod http://127.0.0.1:5050/api/symbol-info/EURUSD  # ok:true, source db
  Invoke-RestMethod http://127.0.0.1:5050/api/instruments         # brokers + simbolos

En el dashboard (tab Inicio): Readiness 100%, Auditoria 6/6,
tarjeta SQX Path = "ruta configurada" en verde, Backend conectado v0.2.0.

Nota: MTF Evidence puede quedar en NO_GO; es esperado (requiere
real_mtf_pipeline_run.py con datos OHLC reales) y no forma parte del setup basico.

## Solucion de problemas
  symbol-info / instruments devuelven 404
    Falta sqx_data_db en config.json. Repite "Vincular SQX la primera vez".
  El arranque falla o no abre el dashboard
    Puerto 5050 ocupado por SQX. Cierra SQX o mueve WebServerPort.
  Falta runtime\python\python.exe
    Ejecuta el bootstrap (ver "Preparar Python embebido").

## Uso tecnico
  Arrancar API:  backend\sqx-edge-tool\run-web-embedded.bat
  CLI:           backend\sqx-edge-tool\run-embedded.bat list
  Config local:  backend\sqx-edge-tool\config.json
  Outputs:       backend\sqx-edge-tool\output\

## Empaquetar
  powershell ... package_portable.ps1 -RequireEmbeddedPython
  -> genera en dist/
