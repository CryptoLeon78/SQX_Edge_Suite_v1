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

## 2. Flujo de Código y Auditoría

*   **Prohibido el Push Directo a `main`**: Todos los desarrollos de módulos o cambios en la arquitectura deben realizarse en ramas de características (`feat/nombre`) y enviarse mediante **Pull Request**.
*   **Validación Automática**: El `Institutional Quality Auditor` (GitHub Actions) revisará cada envío. Si el Auditor falla, el cambio no se fusiona.
*   **Revisión por Pares**: Las PRs deben ser revisadas por el dueño del área según el archivo `CODEOWNERS`.

## 3. Nomenclatura y Certificación C2

*   **Analyzer Obligatorio**: No se aceptan estrategias en el repositorio que no hayan pasado por el módulo de certificación `Analyzer` con el preset correspondiente (Forex, Indices, Crypto).
*   **Nomenclatura Estricta**: Los archivos `.cfx` exportados deben seguir el patrón:
    `template_ACTIVO_DIRECCION_TIMEFRAME_INDICADOR_BLOQUE_ID.cfx`

## 4. Responsabilidades (CODEOWNERS)

*   **CryptoLeon78**: Arquitectura Core, Seguridad, Auditoría y Motores de Generación.
*   **jlivanmaseda-maker**: Metodología de Scoring, Datasets, Estrategias y Análisis de Evidencia.

---
**El incumplimiento de esta disciplina degrada la calidad institucional del proyecto y será reportado automáticamente por los logs del Auditor.**
