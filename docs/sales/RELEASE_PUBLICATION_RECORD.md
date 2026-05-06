# Release Publication Record

Este runbook registra la evidencia despues de publicar una release visible. No publica por API ni modifica GitHub; valida y documenta que la salida quedo completa.

## Requisitos

- `public_release_gate.py` en `GO`.
- Tag creado.
- GitHub Release publicada.
- ZIP portable adjunto.
- `.sha256` publicado y coincidente.
- Descarga probada por operador.
- Release notes visibles.
- Ventana de soporte abierta.
- Ventana de rollback abierta.

## Dry Run

```powershell
python backend\sqx-edge-tool\tools\release_publication_record.py --allow-no-go-gate --no-write
```

Bloqueos esperados hasta publicar de verdad:

- `public_release_gate_missing` o `public_release_gate_not_go`
- `github_release_not_published`
- `git_tag_not_confirmed`
- `release_url_missing_or_not_https`
- `sha256_file_missing`
- `sha256_mismatch`
- `zip_download_not_tested`
- `release_notes_not_visible`
- `support_window_not_open`
- `rollback_window_not_open`

## Flujo Real

```powershell
python backend\sqx-edge-tool\tools\release_publication_record.py --use-latest-public-release-gate --release-tag v1.0.0 --release-url https://github.com/CryptoLeon78/SQX_Edge_Suite_v1/releases/tag/v1.0.0 --download-url https://github.com/CryptoLeon78/SQX_Edge_Suite_v1/releases/download/v1.0.0/SQX_Edge_Tool_Portable_20260506_233908.zip --published-by "Ivan" --confirm-git-tag-created --confirm-github-release-published --confirm-zip-download-tested --confirm-sha256-matches --confirm-release-notes-visible --confirm-support-window-open --confirm-rollback-window-open
```

## Evidencia Minima

- Tag y URL de release.
- Campo `github_release_published` confirmado.
- ZIP local usado para el hash.
- `.sha256` publicado.
- Confirmacion de descarga probada.
- Responsable que publica.
- Estado de soporte.
- Estado de rollback.

No cierres la ventana de salida hasta haber probado la descarga publicada como si fueras un usuario basico.
