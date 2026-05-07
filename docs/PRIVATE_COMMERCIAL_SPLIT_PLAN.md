# Private Commercial Split Plan

Estado: private_repo_published.

Esta fase prepara la migracion de documentos comerciales sensibles a un repositorio privado sin borrar todavia las fuentes publicas. La razon es trazabilidad: primero se exporta, se valida el indice SHA256 y solo despues se sustituyen documentos publicos por punteros redactados.

## Destino Recomendado

- Repositorio privado: `sqx-edge-commercial-private`.
- Export local ignorado: `commercial-private/sqx-edge-commercial-private/`.
- Herramienta: `backend/sqx-edge-tool/tools/private_commercial_split.py`.
- Indices generados en el export: `MIGRATION_INDEX.json` y `MIGRATION_INDEX.md`.
- Commit local privado preparado: `ed79719 Initial private commercial export`.
- Repo privado publicado: `https://github.com/CryptoLeon78/sqx-edge-commercial-private`.
- Visibilidad verificada con GitHub CLI: private.

## Material Que Debe Migrar

- `docs/MONETIZATION_ROADMAP.md`
- `docs/MONETIZATION_M*.md`
- `docs/sales/`
- `resources/pro-buyer-pack/`
- `resources/pro-template-pack-1/`
- `resources/pro-template-pack-2/`

## Material Que Puede Seguir Publico

- README, CHANGELOG y documentacion de release.
- `docs/PUBLIC_ROADMAP.md`.
- `docs/ARCHITECTURE.md`.
- `docs/COMMERCIAL_README.md`, siempre que mantenga claims seguros y no incluya evidencias privadas.
- `docs/PRIVATE_COMMERCIAL_DOCS.md`, este plan y el manifiesto de frontera.

## Procedimiento

1. Ejecutar el export local:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\private_commercial_split.py
```

2. Crear el repositorio privado `sqx-edge-commercial-private`. Done.
3. Desde `commercial-private/sqx-edge-commercial-private/`, configurar `origin` y ejecutar `git push -u origin main`. Done.
4. Verificar `MIGRATION_INDEX.json`, los hashes SHA256 y que GitHub marca el repo como privado. Done.
5. Sustituir documentos publicos sensibles por punteros redactados. Done in S5.

## Public Redaction State

- Public redaction phase: `S5_public_commercial_redaction`.
- Public files now keep path-level pointer stubs only.
- Complete commercial content remains in the private repo at commit `ed79719`.
- Pointer index: `docs/PUBLIC_COMMERCIAL_POINTERS.md`.

## Regla De Seguridad

El historial publico se considera ya expuesto. Si algun documento contuvo secretos reales, datos personales o credenciales, no basta con moverlo: hay que rotar el secreto o tratar el historial con una fase separada.
