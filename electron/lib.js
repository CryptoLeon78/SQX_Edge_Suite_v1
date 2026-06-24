'use strict';
/**
 * lib.js -- Pure, testable helpers for the SQX Edge Electron shell.
 *
 * Nothing in this module spawns a process or opens a window.
 * Free of Electron APIs so the entire file runs under plain `node --test`.
 */

const http = require('http');
const net  = require('net');
const path = require('path');

/**
 * Bind a TCP socket to port 0 on 127.0.0.1 and return the OS-assigned port.
 * The socket is closed before the promise resolves, so the port is free for
 * the caller to bind.  There is a small TOCTOU window; acceptable here because
 * the sidecar will bind the port within milliseconds.
 *
 * @returns {Promise<number>}
 */
function pickFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      server.close(() => resolve(port));
    });
    server.on('error', reject);
  });
}

/**
 * Build the command descriptor for the Flask sidecar without spawning it.
 *
 * Dev mode  (packaged=false):
 *   cmd  = "python"
 *   args = [<repoRoot>/packaging/app_main.py]
 *
 * Packaged mode (packaged=true):
 *   cmd  = <resourcesPath>/SQX_Edge_Tool.exe
 *   args = []
 *
 * In both cases env inherits the current process environment and overrides
 * SQX_NO_WINDOW=1 and SQX_PORT=<port> so the Python side runs headlessly on
 * a specific port.  The original process.env is NOT mutated.
 *
 * @param {object}  opts
 * @param {boolean} opts.packaged        true when running from an installed build
 * @param {number}  opts.port            the port Flask must listen on
 * @param {string}  opts.resourcesPath   Electron process.resourcesPath (packaged)
 * @param {string}  opts.repoRoot        path to the git repo root (dev)
 * @returns {{ cmd: string, args: string[], env: Record<string,string> }}
 */
function sidecarCommand({ packaged, port, resourcesPath, repoRoot }) {
  const env = Object.assign({}, process.env, {
    SQX_NO_WINDOW: '1',
    SQX_PORT: String(port),
  });

  if (packaged) {
    return {
      cmd:  path.join(resourcesPath, 'SQX_Edge_Tool.exe'),
      args: [],
      env,
    };
  }

  return {
    cmd:  'python',
    args: [path.join(repoRoot, 'packaging', 'app_main.py')],
    env,
  };
}

/**
 * Poll GET http://127.0.0.1:<port>/api/health until it returns HTTP 200, or
 * reject with an error if timeoutMs elapses first.
 *
 * Retries on any error (connection refused, non-200 status, socket timeout).
 * Uses a 1-second per-request timeout and 100 ms inter-attempt delay.
 *
 * @param {number} port
 * @param {number} [timeoutMs=15000]
 * @returns {Promise<void>}
 */
function waitForHealth(port, timeoutMs = 15_000) {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + timeoutMs;

    function attempt() {
      if (Date.now() >= deadline) {
        return reject(
          new Error(`/api/health did not respond within ${timeoutMs} ms on port ${port}`)
        );
      }

      const req = http.get(
        { hostname: '127.0.0.1', port, path: '/api/health', timeout: 1000 },
        (res) => {
          res.resume(); // discard body -- we only care about the status code
          if (res.statusCode === 200) {
            resolve();
          } else {
            setTimeout(attempt, 100);
          }
        }
      );

      req.on('error', () => setTimeout(attempt, 100));
      req.on('timeout', () => { req.destroy(); setTimeout(attempt, 100); });
    }

    attempt();
  });
}

module.exports = { pickFreePort, sidecarCommand, waitForHealth };
