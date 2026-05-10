# T10ag OpenNext Local Smoke

## Objective

T10ag runs the prepared OpenNext/Cloudflare Workers package locally and proves whether the tester portal can build and answer a health request before any provider action.

This phase remains local-only. It does not create a Cloudflare project, does not connect GitHub to Cloudflare, does not create a Cloudflare Access application or policy, does not deploy and does not publish a tester URL.

## Local Commands Executed

Native Windows attempt from `templates/SQX_Edge_Tester_Portal/`:

```powershell
npm install --no-package-lock
npm run cf:build
npx opennextjs-cloudflare preview
```

WSL/Linux attempt from a temporary Linux filesystem copy:

```bash
tar --exclude=node_modules --exclude=.next --exclude=.open-next --exclude=.wrangler --exclude=package-lock.json --exclude=tsconfig.tsbuildinfo --exclude=cloudflare-env.d.ts --exclude=.dev.vars -cf - . | tar -xf - -C "$HOME/sqx_t10ag_portal"
cd "$HOME/sqx_t10ag_portal"
npm install --no-package-lock
npm run cf:build
cp .dev.vars.example .dev.vars
npx opennextjs-cloudflare preview
curl http://127.0.0.1:8787/api/health
```

The temporary `.dev.vars` file was created only inside the smoke workspace and removed after the preview process stopped.

## Result

```text
GO_OPENNEXT_LOCAL_LINUX_PREVIEW_SMOKE_NO_PROVIDER_ACTION
```

The WSL/Linux smoke returned:

```text
status=200
ok=1
worker=present
assets=present
```

Health response:

```json
{"ok":true,"service":"sqx-edge-tester-portal","phase":"T8","containsTesterData":false}
```

## Native Windows Finding

Native Windows preview started on `127.0.0.1:8787`, but every tested route returned 500:

- `/`
- `/login`
- `/expired`
- `/api/health`

OpenNext printed its own warning that native Windows is not fully compatible and may encounter unpredictable runtime failures. The same package passed when copied to a WSL/Linux filesystem, so this is treated as a local runtime environment limitation rather than a portal compatibility failure.

Decision for operators:

```text
NO_GO_NATIVE_WINDOWS_PREVIEW_ROUTE_500
```

Use WSL/Linux for OpenNext preview smoke until we have a stronger native Windows path.

## WSL/Linux Finding

The Linux copy built and previewed successfully:

- Next.js: `16.2.6`
- `@opennextjs/cloudflare`: `1.19.8`
- Wrangler: `4.90.0`
- Worker generated: `.open-next/worker.js`
- Assets generated: `.open-next/assets`
- Local health endpoint: `200 OK`

Warnings observed:

- no lockfile found
- `middleware` file convention is deprecated and should move to `proxy`
- `punycode` Node module deprecation warning

These warnings do not block T10ag, but the middleware/proxy warning should be cleaned before external provider work.

## Security Boundary

- No Cloudflare project was created.
- No Cloudflare deployment was created.
- No Cloudflare Access application or policy was created.
- No GitHub repository was connected to Cloudflare.
- No Cloudflare token or account ID was committed.
- No tester URL was shared.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.

## Decision

Next gate:

```text
T10ah_next_middleware_to_proxy_migration_no_provider_action
```

T10ah should migrate the Next.js `middleware` convention to `proxy` or otherwise silence that build warning, then rerun the WSL/Linux local smoke. It must remain no-provider and no-deploy unless Ivan explicitly approves an external action later.

## Verification

T10ag is accepted when:

- this document exists
- `scripts/opennext-local-smoke-proof.mjs` exists
- `package.json` exposes `proof:opennext-local-smoke`
- the proof returns `GO_OPENNEXT_LOCAL_LINUX_PREVIEW_SMOKE_NO_PROVIDER_ACTION`
- the native Windows 500 finding is documented as `NO_GO_NATIVE_WINDOWS_PREVIEW_ROUTE_500`
- the WSL/Linux smoke records health `200`
- docs and roadmap point to T10ah as the no-provider middleware/proxy cleanup phase
- no Cloudflare project, deployment, Access policy, tester URL, tester account, tester email or production database state is introduced
- static tests and typecheck pass
- sensitive scan finds no tester emails, secrets, provider tokens, deployment URLs or account IDs in touched public files
- temporary WSL, `.next`, `.open-next`, `.wrangler`, `.dev.vars`, `node_modules`, lock and typegen artifacts are cleaned
- `git diff --check` passes
