# Monetization M42 - Release Publication Record

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Registrar evidencia post-publicacion de una release visible: tag, GitHub Release publicada, ZIP adjunto, SHA256 coincidente, notas visibles, soporte y rollback.

## Entregables

- Estado `release_publication_record_ready`.
- Tool `backend/sqx-edge-tool/tools/release_publication_record.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-tool/data/release_publication_record`.
- Consumo de evidencia M41 `public_release_gate`.
- Validacion de `github_release_published`, tag creado, ZIP, `.sha256`, `sha256_mismatch`, descarga probada, soporte y rollback.
- Guia `docs/sales/RELEASE_PUBLICATION_RECORD.md`.

## Decision

M42 no declara `GO` si la release no esta publicada, si el ZIP no tiene checksum coincidente o si soporte/rollback no estan abiertos durante la ventana de salida.

## Uso

```powershell
python backend\sqx-edge-tool\tools\release_publication_record.py --use-latest-public-release-gate --release-tag v1.0.0 --release-url https://github.com/CryptoLeon78/SQX_Edge_Suite_v1/releases/tag/v1.0.0 --download-url https://github.com/CryptoLeon78/SQX_Edge_Suite_v1/releases/download/v1.0.0/SQX_Edge_Tool_Portable_20260506_233908.zip --published-by "Ivan" --confirm-git-tag-created --confirm-github-release-published --confirm-zip-download-tested --confirm-sha256-matches --confirm-release-notes-visible --confirm-support-window-open --confirm-rollback-window-open
```

Revision seca:

```powershell
python backend\sqx-edge-tool\tools\release_publication_record.py --allow-no-go-gate --no-write
```

## Siguiente Paso

M43 debe preparar monitorizacion post-release: incidencias, descargas, tickets, errores de activacion, hotfix/rollback y decision de mantener, pausar o escalar difusion.
