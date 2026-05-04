# Changelog

## 2026-05-04 - Entrega profesional

Version entregable de SQX Edge Suite v1.

### Incluido

- Diseno `Premium SaaS Dark v2` con fase `Design Pro`.
- Pagina `Inicio` como cockpit operativo por defecto.
- Navegacion visual refinada para desktop y mobile.
- Tab `Estrategias` con eliminacion de cualquier estrategia visible.
- Restauracion de estrategias base eliminadas de la vista.
- Importacion, consolidacion y exportacion de estrategias.
- Project Generator con asistente de arranque y controles visuales refinados.
- Scripts analiticos y endpoints de backup integrados.
- Tests E2E opcionales con Playwright.
- Empaquetado portable con Python embebido.
- Launchers de un click: `START_SQX_EDGE.bat` y `STOP_SQX_EDGE.bat`.

### Verificacion

- Suite normal: `24 passed, 2 skipped`.
- E2E opcional con Playwright: cubre Inicio, Estrategias, eliminar/restaurar y mobile.
- ZIP portable validado en extraccion limpia.
- Runtime portable validado importando `flask` y `api.server`.

### Paquete

El ZIP final se genera en:

```text
dist/SQX_Edge_Tool_Portable_*.zip
```
