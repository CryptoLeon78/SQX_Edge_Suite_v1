'use strict';
// Tests for electron/lib.js using the built-in Node.js test runner (node:test).
// Run from electron/: node --test tests/lib.test.js
// Never imports or starts Electron.

const { test }  = require('node:test');
const assert    = require('node:assert/strict');
const http      = require('http');
const path      = require('path');
const { pickFreePort, sidecarCommand, waitForHealth } = require('../lib');

// ---------------------------------------------------------------------------
// pickFreePort
// ---------------------------------------------------------------------------

test('pickFreePort returns a valid port number', async () => {
  const port = await pickFreePort();
  assert.ok(typeof port === 'number', `expected number, got ${typeof port}`);
  assert.ok(port > 0 && port < 65536, `port ${port} is outside valid range`);
});

test('pickFreePort returns an integer', async () => {
  const port = await pickFreePort();
  assert.equal(port, Math.floor(port));
});

test('pickFreePort successive calls each return a usable port', async () => {
  const a = await pickFreePort();
  const b = await pickFreePort();
  assert.ok(a > 0 && b > 0);
});

// ---------------------------------------------------------------------------
// sidecarCommand
// ---------------------------------------------------------------------------

test('sidecarCommand dev: cmd=python, arg ends with packaging/app_main.py', () => {
  const result = sidecarCommand({
    packaged:      false,
    port:          5100,
    repoRoot:      path.join('/repo'),
    resourcesPath: '/res',
  });

  assert.equal(result.cmd, 'python');
  assert.equal(result.args.length, 1);

  const arg = result.args[0];
  assert.ok(
    arg.endsWith('app_main.py'),
    `expected app_main.py, got: ${arg}`
  );
  assert.ok(
    arg.includes('packaging'),
    `path must go through packaging/, got: ${arg}`
  );
});

test('sidecarCommand dev: env has SQX_NO_WINDOW=1 and SQX_PORT=5100', () => {
  const { env } = sidecarCommand({
    packaged: false, port: 5100, repoRoot: '/repo', resourcesPath: '/res',
  });
  assert.equal(env.SQX_NO_WINDOW, '1');
  assert.equal(env.SQX_PORT, '5100');
});

test('sidecarCommand packaged: cmd ends with SQX_Edge_Tool.exe, no extra args', () => {
  const result = sidecarCommand({
    packaged:      true,
    port:          5200,
    repoRoot:      '/repo',
    resourcesPath: '/res',
  });

  assert.ok(
    result.cmd.endsWith('SQX_Edge_Tool.exe'),
    `expected SQX_Edge_Tool.exe, got: ${result.cmd}`
  );
  assert.deepEqual(result.args, []);
});

test('sidecarCommand packaged: env has SQX_NO_WINDOW=1 and SQX_PORT=5200', () => {
  const { env } = sidecarCommand({
    packaged: true, port: 5200, repoRoot: '/repo', resourcesPath: '/res',
  });
  assert.equal(env.SQX_NO_WINDOW, '1');
  assert.equal(env.SQX_PORT, '5200');
});

test('sidecarCommand does not mutate process.env', () => {
  const before = process.env.SQX_PORT;
  sidecarCommand({ packaged: false, port: 9999, repoRoot: '/r', resourcesPath: '/p' });
  assert.equal(process.env.SQX_PORT, before);
});

test('sidecarCommand packaged path is under resourcesPath', () => {
  const resourcesPath = path.join('/', 'custom', 'resources');
  const { cmd } = sidecarCommand({
    packaged: true, port: 1, repoRoot: '/r', resourcesPath,
  });
  assert.ok(cmd.startsWith(resourcesPath), `cmd must start with resourcesPath, got: ${cmd}`);
});

// ---------------------------------------------------------------------------
// waitForHealth
// ---------------------------------------------------------------------------

test('waitForHealth resolves when server returns HTTP 200', async () => {
  const server = http.createServer((req, res) => {
    if (req.url === '/api/health') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end('{"ok":true}');
    } else {
      res.writeHead(404);
      res.end();
    }
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address();

  try {
    await waitForHealth(port, 3000);
    // reaching here means the promise resolved correctly
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('waitForHealth rejects when nothing listens on the port (timeout)', async () => {
  // pickFreePort closes the socket before returning, so port is free but NOT listening.
  const port = await pickFreePort();

  await assert.rejects(
    () => waitForHealth(port, 300),
    (err) => {
      assert.ok(
        err.message.includes('did not respond'),
        `unexpected error message: ${err.message}`
      );
      return true;
    }
  );
});

test('waitForHealth rejects when server always returns non-200', async () => {
  const server = http.createServer((req, res) => {
    res.writeHead(503);
    res.end();
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address();

  try {
    await assert.rejects(
      () => waitForHealth(port, 300),
      (err) => {
        assert.ok(
          err.message.includes('did not respond'),
          `unexpected error message: ${err.message}`
        );
        return true;
      }
    );
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});
