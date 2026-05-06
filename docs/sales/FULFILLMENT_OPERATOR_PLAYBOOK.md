# Fulfillment Operator Playbook

## Daily Loop

1. Abrir `Inicio`.
2. Revisar el panel de fulfillment.
3. Comprobar `queued`, `needs_review` y `failed`.
4. Confirmar que private key y ZIP apuntan a los artefactos correctos.
5. Procesar o recolocar solo las requests que correspondan.

## Retry Loop

- `failed` significa que hubo al menos un intento con error registrado.
- Antes de reintentar, revisar `last_error`.
- Corregir rutas, clave o ZIP si el error fue operativo.
- Pulsar `Reintentar` desde el mismo panel.
- Verificar que la request termina en `completed`.

## Ignore And Requeue Rules

- Usar `ignored` para eventos no entregables o cancelaciones.
- Usar `queued` para devolver una request al circuito tras una revision.
- `needs_review` es el estado natural cuando el evento no es elegible automaticamente.
- No borrar requests manualmente del disco salvo operacion extraordinaria.

## Good Practices

- Mantener un unico ZIP final aprobado por release checklist.
- Usar siempre la private key privada correcta para produccion.
- Comprobar que `attempt_count` no crece sin entender el motivo del fallo.
- Si hay duda comercial, detenerse antes de emitir una licencia incorrecta.
