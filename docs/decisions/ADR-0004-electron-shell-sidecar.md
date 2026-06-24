# ADR-0004: Electron Shell + Nuitka Sidecar

**Status:** Proposed  
**Date:** 2026-06-24  
**Governance:** G2 / Architecture-Docs

---

## Context

ADR-0003 selected pywebview (EdgeChromium/WebView2 backend) as the native window
layer for the compiled desktop build.  During Phase 4a-ii that approach exposed a
hard blocker: pywebview's EdgeChromium backend depends on pythonnet (a CPython↔CLR
bridge) which cannot be reliably included by Nuitka under `--standalone` mode on
Windows — symbol resolution conflicts, incomplete CLR discovery, and DLL side-by-side
errors on clean VMs.

Phase 4a-iii introduced a temporary workaround: launch `msedge.exe`/`chrome.exe` in
`--app=<url>` mode from `subprocess.Popen`.  This unblocks the dev/beta cycle but
has two structural weaknesses:

1. **No lifecycle ownership.** The app process has no reliable way to detect a clean
   window close versus a browser crash.  `proc.wait()` blocks the main thread and
   there is no path for graceful shutdown or restart.
2. **Browser coupling.** `--app` mode is an undocumented Chromium flag; its behavior
   has diverged across Edge/Chrome versions and it may be removed.

Electron solves both problems at the cost of a larger installer (~180 MB), which is
acceptable for a desktop product targeting Power Users / Pro tier buyers.

---

## Decision

**Shell: Electron.  Backend: Nuitka `--standalone` headless sidecar.**

The desktop product ships as two processes:

```
Electron main process (JS)
  │  pickFreePort() → OS assigns port N
  │  spawn(SQX_Edge_Tool.exe, env={SQX_NO_WINDOW=1, SQX_PORT=N})
  │  poll GET http://127.0.0.1:N/api/health  (15 s timeout)
  │  BrowserWindow(1280×860).loadURL(http://127.0.0.1:N/)
  │
  └─ SQX_Edge_Tool.exe  (Nuitka --standalone Flask sidecar)
       Flask listens on 127.0.0.1:N
       serves dashboard + /api/*
       SQX_NO_WINDOW=1 → no browser launched from Python side
```

### Supersession (partial)

This ADR **supersedes the pywebview window decision in ADR-0003** (Phases 4a-i through
4a-iii) only.  All other decisions in ADR-0003 remain in effect:

- Nuitka `--standalone` as the compilation strategy
- `SQX_APP_ROOT` env-var anchor for frozen paths
- `harden_buyer_manifest()` hardening pipeline (H1/H2 constraints)
- Private-key policy (`privateKeyPolicy: "never_commit_never_ship"`)
- `-Dev` switch for internal toolchain spikes
- `build.channel` must not be `"internal"` in buyer artifacts

### Lifecycle

| Event | Action |
|---|---|
| Electron `before-quit` | `taskkill /PID <sidecar_pid> /T /F` (Windows) to kill the full process tree; `child.kill()` elsewhere |
| Sidecar exits before health check resolves | `dialog.showErrorBox` + `app.quit()` |
| Health check timeout (15 s) | `killSidecar()` + `dialog.showErrorBox` + `app.quit()` |
| `window-all-closed` | `app.quit()` (triggers `before-quit`) |

### User data

`app.getPath('userData')` → `%APPDATA%\SQX Edge` (Electron default for `productName`).
The Python sidecar does not write user data directly; it reads only `SQX_APP_ROOT`
config and logs.

### Packaging / installer

| Concern | Decision |
|---|---|
| Installer format | NSIS, per-user install (no UAC elevation required) |
| Auto-update | `electron-updater` targeting GitHub Releases (delta updates) |
| Code signing | EV certificate — **deferred**; first beta ships unsigned to internal testers only |
| Sidecar placement | `resources/SQX_Edge_Tool.exe` inside the Electron package |

### Dev mode

```
npm start            # inside electron/
```

`electron/main.js` detects `app.isPackaged === false` and runs:

```
python  packaging/app_main.py
  env: SQX_NO_WINDOW=1, SQX_PORT=<free>
```

`repoRoot` is resolved as `path.resolve(__dirname, '..')` from `electron/main.js`.

### Rollback

If Electron packaging cannot ship on schedule:

1. Use the Edge `--app`-mode launcher (`-Dev` build) for internal/beta testers.
2. Distribute the Nuitka `--standalone` dir as a ZIP portable (no installer).

---

## Consequences

### Positive

- Full window lifecycle ownership — Electron controls open/close/crash cleanly.
- No dependency on any specific browser being installed; Electron ships Chromium.
- Hot-reload of the dashboard HTML/JS during development without restarting Flask.
- Path to auto-update, deep-link, system tray, and native menus if needed.
- pywebview, pythonnet, and WebView2 Runtime prerequisites are eliminated from the
  target machine requirements.

### Negative / risks

- Installer size increases from ~40 MB (Nuitka ZIP) to ~200 MB (Electron + Nuitka).
- Two separate build pipelines must be maintained (Nuitka for sidecar, electron-builder
  for shell).
- EV signing must cover both the Electron shell installer and the Nuitka `.exe`.
- On macOS/Linux, `taskkill /T /F` is not available; `child.kill()` is used instead
  (sends SIGTERM, not a tree-kill).  The Flask threaded server handles this gracefully.

---

## Alternatives considered

| Alternative | Reason rejected |
|---|---|
| pywebview + pythonnet (ADR-0003 Phase 4a-ii) | Nuitka CLR symbol conflict; unreliable on clean VMs |
| Edge `--app` mode (ADR-0003 Phase 4a-iii) | No lifecycle ownership; undocumented flag; fragile across browser versions |
| Tauri (Rust shell + WebView2) | WebView2 still required on Win 10; Rust toolchain adds complexity; less JS ecosystem |
| CEF / CEFSharp | .NET dependency re-introduces pythonnet class of problems |
