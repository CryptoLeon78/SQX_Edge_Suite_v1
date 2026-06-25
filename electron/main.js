'use strict';
const { app, BrowserWindow, dialog } = require('electron');
const { spawn }                        = require('child_process');
const path                             = require('path');
const { pickFreePort, sidecarCommand, waitForHealth } = require('./lib');

const HEALTH_TIMEOUT_MS = 15_000;

let sidecarProc = null;
let quitting    = false;

function killSidecar() {
  if (!sidecarProc) return;
  if (process.platform === 'win32') {
    try {
      // Kill the full process tree so Flask worker threads also die.
      require('child_process').execSync(
        `taskkill /PID ${sidecarProc.pid} /T /F`,
        { stdio: 'ignore' }
      );
    } catch (_) {
      sidecarProc.kill();
    }
  } else {
    sidecarProc.kill();
  }
  sidecarProc = null;
}

app.whenReady().then(async () => {
  const port          = await pickFreePort();
  const packaged      = app.isPackaged;
  const resourcesPath = process.resourcesPath;
  // In dev: electron/ lives one level inside the repo root.
  const repoRoot      = path.resolve(__dirname, '..');

  const { cmd, args, env } = sidecarCommand({ packaged, port, resourcesPath, repoRoot });

  sidecarProc = spawn(cmd, args, { env, stdio: 'inherit' });

  sidecarProc.on('exit', (code) => {
    // Ignore exits that we triggered via killSidecar() on before-quit.
    if (quitting) return;
    dialog.showErrorBox(
      'SQX Edge — Startup error',
      `The API sidecar exited with code ${code} before the window could open.\n` +
      'Check the console output for details.'
    );
    app.quit();
  });

  try {
    await waitForHealth(port, HEALTH_TIMEOUT_MS);
  } catch (err) {
    killSidecar();
    dialog.showErrorBox('SQX Edge — Startup timeout', err.message);
    app.quit();
    return;
  }

  const win = new BrowserWindow({
    width:  1280,
    height: 860,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  win.loadURL(`http://127.0.0.1:${port}/`);
});

app.on('window-all-closed', () => app.quit());

app.on('before-quit', () => {
  quitting = true;
  killSidecar();
});

// SIGINT (Ctrl+C in terminal) and SIGTERM (systemd/launchd) give us a chance
// to kill the sidecar before this process exits.  killSidecar() is idempotent
// (guards on sidecarProc != null), so concurrent calls from before-quit and a
// signal are safe.
//
// NOTE: Windows cannot deliver SIGTERM to a native process, and a hard main
// crash runs none of these handlers -- the Python watchdog (SQX_PARENT_PID)
// is the backstop for those scenarios.
process.on('SIGINT',  () => { killSidecar(); process.exit(0); });
process.on('SIGTERM', () => { killSidecar(); process.exit(0); });
