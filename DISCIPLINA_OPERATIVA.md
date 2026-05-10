# ⚖️ Disciplina Operativa SQX Institutional

Este documento define el estándar de trabajo obligatorio para todos los miembros del equipo (CryptoLeon78 y jlivanmaseda-maker) en el repositorio `SQX_Institutional_Core`.

## 1. Sincronización Continua y Commits Atómicos

A partir de la implementación del Núcleo Institucional, se establece la siguiente regla de oro para el desarrollo:

> **"Cambio realizado = Commit realizado + Push inmediato"**

### Protocolo de Trabajo:
1.  **Atomicidad**: Los cambios deben ser pequeños y enfocados. No acumules horas de trabajo sin commitear.
2.  **Sincronización**: Después de cada cambio funcional, corrección o actualización de datos, se DEBE ejecutar:
    ```bash
    git add .
    git commit -m "feat/fix/docs: descripción clara del cambio"
    git push origin [tu-rama]
    ```
3.  **Conflictos**: Esta práctica minimiza los conflictos de fusión y permite que el **Auditor Institucional** valide el progreso en tiempo real.

## 2. Blindaje de Fugas (Anti-Leakage)

Para evitar que el código "se escape" o quede atrapado en los repositorios antiguos (`sqx-edge-pipeline` y `SQX_Edge_Suite_v1`), el Auditor Institucional realiza una vigilancia periódica.

### Reglas de Sincronización:
*   **Vigilancia Activa**: El Auditor fallará si detecta nuevos commits en los repositorios antiguos que no hayan sido "marcados" como integrados en este núcleo institucional.
*   **Protocolo de Integración**: Si realizas un cambio en los repositorios antiguos (por necesidad técnica o transición), debes registrarlo en este repositorio mediante un commit de sincronización:
    ```bash
    git commit -m "sync: integrating changes from legacy repo [hash_del_commit_antiguo]" --allow-empty
    ```
*   **Prohibición de Deriva**: Se desaconseja fuertemente desarrollar funciones nuevas en los repositorios antiguos. Todo nuevo "Edge" debe nacer en `SQX_Institutional_Core`.

## 3. Flujo de Código y Auditoría

*   **Prohibido el Push Directo a `main`**: Todos los desarrollos de módulos o cambios en la arquitectura deben realizarse en ramas de características (`feat/nombre`) y enviarse mediante **Pull Request**.
*   **Validación Automática**: El `Institutional Quality Auditor` (GitHub Actions) revisará cada envío. Si el Auditor falla, el cambio no se fusiona.
*   **Revisión por Pares**: Las PRs deben ser revisadas por el dueño del área según el archivo `CODEOWNERS`.
*   **Compatibilidad SQX Edge Suite**: Las fases operativas heredadas pueden prepararse en ramas `codex/*`; `main` solo debe avanzar cuando la rama conserve tests, trazabilidad y activos institucionales.

## 4. Nomenclatura y Certificación C2

*   **Analyzer Obligatorio**: No se aceptan estrategias en el repositorio que no hayan pasado por el módulo de certificación `Analyzer` con el preset correspondiente (Forex, Indices, Crypto).
*   **Nomenclatura Estricta**: Los archivos `.cfx` exportados deben seguir el patrón:
    `template_ACTIVO_DIRECCION_TIMEFRAME_INDICADOR_BLOQUE_ID.cfx`

## 5. Responsabilidades (CODEOWNERS)

*   **CryptoLeon78**: Arquitectura Core, Seguridad, Auditoría y Motores de Generación.
*   **jlivanmaseda-maker**: Metodología de Scoring, Datasets, Estrategias y Análisis de Evidencia.
*   **Access/Security Gatekeeper (Agente)**: Auth, testers, sesiones, Vercel, caducidades, renovaciones, auditoría anti-distribución y respuesta ante fuga.

## 6. Ecosistema Cloud y Tester Portal (Vercel)

La exposición del producto a testers externos se preparará como capa separada, sin mezclar credenciales, enlaces privados ni lógica de acceso sensible dentro de la app portable pública.

*   **SQX_Edge_Tester_Portal**: futuro punto de entrada privado para testers finales, preferentemente Next.js/Vercel, documentado desde T1.
*   **Identidad por usuario**: acceso individual por email y contraseña hasheada; queda prohibido depender de una contraseña compartida como control principal.
*   **Caducidad de testers**: ciclos de 15 días con revisión manual de continuidad, denegación o bloqueo.
*   **Anti-distribución**: watermark visible por tester, auditoría de accesos, rate limiting, bloqueo por abuso y kill switch operativo.
*   **Secretos**: las claves, tokens, licencias, credenciales y URLs sensibles deben vivir en variables de entorno o repos privados, nunca en commits públicos.
*   **Vercel Protection**: Deployment Protection, Password Protection, Edge Config, Cron Jobs y Middleware son controles complementarios; no sustituyen la autenticación por tester.
*   **Acciones externas bloqueadas por defecto**: no se despliega en Vercel, no se crean cuentas tester, no se publican URLs, no se rotan contraseñas ni se envían correos sin aprobación explícita del usuario.

---
**El incumplimiento de esta disciplina degrada la calidad institucional del proyecto y será reportado automáticamente por los logs del Auditor.**
