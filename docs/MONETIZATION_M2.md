# Phase M2 - Licensing And Access Model

## Decision

SQX Edge Pro debe usar una licencia local firmada como primer modelo comercial.

Objetivo:

- mantener la experiencia portable y sencilla
- evitar que el usuario basico necesite crear cuentas complejas
- permitir uso offline diario
- dejar preparada una activacion online futura
- proteger las funciones Pro en el backend, no solo en la interfaz

Modelo recomendado para el primer lanzamiento:

1. El usuario compra SQX Edge Pro mensual o anual.
2. Recibe un archivo de licencia firmado.
3. La app permite importar la licencia desde una pantalla simple.
4. La licencia se guarda localmente.
5. La app valida la firma y la fecha de expiracion sin internet.
6. Las funciones Pro quedan activas hasta la fecha de expiracion, con un pequeno periodo de gracia.

## License Format

La licencia debe ser un JSON firmado.

Campos recomendados:

| Field | Purpose |
| --- | --- |
| `license_id` | Identificador unico de licencia |
| `customer_name` | Nombre visible para soporte |
| `customer_email_hash` | Hash del email, no email plano obligatorio |
| `plan` | `free`, `pro_monthly`, `pro_annual`, `pro_support`, `template_pack` |
| `features` | Lista explicita de capacidades activadas |
| `issued_at` | Fecha de emision |
| `expires_at` | Fecha de expiracion |
| `grace_days` | Dias de tolerancia tras expiracion |
| `max_machines` | Numero de equipos permitidos |
| `machine_binding` | Huella opcional del equipo |
| `license_version` | Version del formato |
| `signature` | Firma criptografica del payload |

Regla importante: la clave privada para firmar licencias no debe estar nunca dentro del repositorio ni del ZIP portable. La app solo debe incluir la clave publica o el material minimo necesario para verificar firmas.

## Access Levels

### Free

Sin licencia o con licencia invalida.

Permitido:

- abrir dashboard
- usar Inicio
- consultar activos, categorias y filtros
- gestionar estrategias demo/manuales
- importar una muestra limitada
- export CSV basico
- ver funciones Pro con llamada clara a actualizar

Bloqueado o limitado:

- Project Generator completo
- Strategy Cleaner con acciones de escritura
- export avanzado
- presets premium
- template packs premium
- backups avanzados
- workflows premium

### Trial

Recomendacion: no lanzar trial automatico en la primera version comercial.

Motivo:

- reduce complejidad tecnica
- evita soporte prematuro
- permite validar ventas manuales antes de construir caducidades agresivas
- protege mejor la primera distribucion publica

Alternativa para demos:

- licencias temporales manuales de 7 o 14 dias
- generadas caso por caso
- mismas reglas que Pro, pero con `expires_at` cercano

### Pro Monthly

Permitido:

- todas las funciones Pro
- actualizaciones mientras la licencia este activa
- import/export completo
- Project Generator completo
- Strategy Cleaner completo
- workflows premium incluidos

Caducidad:

- al llegar `expires_at`, entra en gracia
- durante gracia, mantener acceso Pro y mostrar aviso
- tras gracia, pasar a modo Free sin borrar datos

### Pro Annual

Igual que Pro Monthly, con expiracion anual.

Ventaja comercial:

- mejor caja inicial
- menos friccion de renovacion
- descuento frente al mensual

### Pro Support Add-On

Debe ser una marca adicional de licencia, no otro producto tecnico separado.

Ejemplo:

- `plan`: `pro_annual`
- `features`: incluye `priority_support`

El soporte no debe desbloquear funciones criticas distintas al Pro normal al inicio. Debe vender prioridad, ayuda y acompanamiento.

### Template Packs

Los packs deben licenciarse como derechos independientes.

Ejemplo:

- `template_pack_1`
- `premium_presets_fx`
- `workflow_pack_validation`

Esto permite vender Pro y packs por separado.

## Feature Flags

La app debe trabajar con capacidades, no con textos de plan hardcodeados.

Capacidades iniciales recomendadas:

| Feature Flag | Free | Pro |
| --- | --- | --- |
| `dashboard.view` | Yes | Yes |
| `strategies.basic` | Yes | Yes |
| `strategies.import_full` | Limited | Yes |
| `strategies.export_advanced` | No | Yes |
| `project_generator.demo` | Yes | Yes |
| `project_generator.generate` | No | Yes |
| `strategy_cleaner.preview` | Yes | Yes |
| `strategy_cleaner.apply` | No | Yes |
| `backups.advanced` | No | Yes |
| `workflows.premium` | No | Yes |
| `templates.premium` | Pack | Pack |
| `support.priority` | Add-on | Add-on |

Regla tecnica: los botones y textos pueden reaccionar al estado de licencia, pero los endpoints de backend que ejecuten acciones Pro tambien deben validar permisos.

## Backend Enforcement

No basta con ocultar botones en HTML/JS.

Endpoints que deberian exigir licencia Pro cuando llegue la implementacion:

- generar proyectos
- generar todos los proyectos
- aplicar limpieza de estrategias
- guardar configuraciones Pro
- export avanzado
- restauracion/backup avanzado
- acceso a packs premium

Endpoints que pueden quedar Free:

- health check
- lectura de dashboard
- lectura de manifiestos
- preview de limpieza
- validacion de rutas sin escritura
- diagnostico local seguro

Respuesta recomendada para acceso bloqueado:

```json
{
  "ok": false,
  "error": "pro_required",
  "message": "Esta funcion requiere SQX Edge Pro.",
  "required_feature": "project_generator.generate"
}
```

## User Experience

La experiencia para usuario basico debe ser:

1. Descargar ZIP.
2. Descomprimir.
3. Doble click en `START_SQX_EDGE.bat`.
4. Abrir Inicio.
5. Pulsar "Activar Pro".
6. Elegir archivo de licencia.
7. Ver estado claro: Free, Pro activo, Pro en gracia o expirado.

Estados visibles recomendados:

| State | User Message |
| --- | --- |
| `free` | SQX Edge Free |
| `pro_active` | SQX Edge Pro activo |
| `pro_grace` | Pro en periodo de gracia |
| `expired` | Licencia expirada |
| `invalid` | Licencia no valida |
| `missing` | Sin licencia |

La app no debe borrar datos ni configuraciones al expirar. Solo debe desactivar acciones Pro y mantener lectura/export basico.

## Machine Binding

Recomendacion inicial:

- permitir 1 equipo por licencia
- no bloquear agresivamente en la primera version
- ofrecer reset manual por soporte
- guardar una huella local simple y reversible solo para comparacion

No conviene construir al inicio un sistema anti-pirateria duro. Es mejor proteger lo suficiente, vender valor y reducir friccion.

## Renewal Flow

Renovacion manual inicial:

1. El usuario renueva mensual/anual.
2. Se genera nueva licencia con nuevo `expires_at`.
3. El usuario importa el nuevo archivo.
4. La app reemplaza la licencia anterior.

Futuro:

- endpoint de activacion
- renovacion automatica
- revalidacion online opcional
- recuperacion por email
- panel de cliente

## Security Rules

- No incluir claves privadas en el repositorio.
- No confiar en estados JS para proteger acciones Pro.
- No guardar emails completos si no hacen falta.
- No enviar rutas locales sin consentimiento.
- No romper modo offline.
- No bloquear lectura de datos del usuario tras expiracion.
- No prometer proteccion absoluta contra copia.

## Implementation Phases After M2

### M3

Elegir canal de cobro y entrega.

### M4

Crear separacion tecnica Free/Pro:

- `license` config
- feature flags
- pantalla de activacion
- validacion backend
- mensajes de upgrade

### M5

Preparar pagina comercial, capturas y mensajes.

### M6

Auditar seguridad de ZIP comercial, endpoints y datos.

## Final Recommendation

Para SQX Edge Pro, el camino mas sensato es:

- licencia local firmada
- activacion manual por archivo en la primera version
- validacion offline
- 1 equipo con reset manual
- sin trial automatico al inicio
- licencias demo manuales para leads serios
- backend enforcing para funciones Pro
- expiracion sin borrado de datos

Este modelo protege lo suficiente sin castigar al usuario basico, y nos deja una ruta limpia hacia activacion online cuando el producto ya tenga ventas reales.
