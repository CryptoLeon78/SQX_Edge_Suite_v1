# REMOTE-DOWNLOADS2 - Universal Browser Downloads

## Summary

REMOTE-DOWNLOADS2 closes the user-facing export rule for the remote web model:
SQX Edge Suite must never ask the final user to open a server folder or choose a
server path. Every user-facing artifact is delivered as a normal browser
download.

Project Generator `.cfx` downloads were already covered by REMOTE-OUTPUT1. This
phase audits and aligns the remaining export surfaces:

- SQX Views: `.vw` and preset packs.
- Template Maker: generated `.sqx` C2 templates.
- Strategy Control: CSV export and consolidated JSON.
- Champion vs Challenger: redacted review JSON.
- Control Panel support: redacted diagnostic JSON.
- Mining Control: consolidated Plan Mining JSON.

## Product Rule

Browser download is the only user-facing delivery mechanism for files.
Rule id: every user-facing export must be a browser download.

- The server may store artifacts temporarily inside the authenticated workspace.
- The user receives files through browser download mechanics.
- Chrome/Edge normally saves those files to the user's `Downloads` folder.
- If the user enabled "ask where to save each file", the browser may show a save
  picker. SQX Edge Suite does not bypass that browser setting.
- The UI must not say or imply that the user should open a server folder.

## Changes

- Mining Control `Descargar JSON` now downloads the consolidated plan JSON
  instead of opening a popup window.
- Strategy Control `Descargar JSON` now downloads the consolidated strategies
  JSON instead of opening a popup window.
- Existing non-Project-Generator exports already use `link.download` or
  equivalent browser download semantics and remain aligned.
- Governance now treats this as a cross-product download gate, not a single-tab
  feature.

## Guardrail

Static tests must block regressions in user-facing surfaces:

- no `window.open` based export previews in the main dashboard controller;
- no visible `Abrir carpeta`, `carpeta local`, `ruta local` or `rutas locales`
  copy in user-facing UI;
- key export modules must keep explicit browser download helpers or
  `download` attributes.

## Out Of Scope

- Operator-only tools may still mention local folders, ignored evidence paths or
  laptop/server folders.
- Control Panel may keep operator language where it is explicitly about backend,
  tunnel, local evidence or support diagnostics.
- Browser settings decide the final physical destination on the user's PC.
