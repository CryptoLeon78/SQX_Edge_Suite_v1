# T10ah Next Proxy Migration Gate

## Objective

T10ah evaluates the tester portal request gate migration from the deprecated Next.js `middleware.ts` convention to `proxy.ts`, preserving the existing access, security header, kill-switch and rate-limit behavior.

This phase remains local-only. It does not create a Cloudflare project, does not connect GitHub to Cloudflare, does not create a Cloudflare Access application or policy, does not deploy and does not publish a tester URL.

## Why This Phase Exists

The T10ag OpenNext local smoke passed in WSL/Linux, but the build/preview logs warned that the `middleware` file convention is deprecated and should use `proxy`. Next.js now documents `proxy.ts` as the request gate file convention and expects a named `proxy` export.

However, the official Next.js 16 upgrade guide says `proxy` runs in the Node.js runtime and cannot be configured to Edge. The OpenNext Cloudflare adapter currently does not support Node Middleware. A local T10ah WSL smoke confirmed this: after renaming to `proxy.ts`, `npm run cf:build` stopped with `Node.js middleware is not currently supported`.

T10ah therefore keeps `src/middleware.ts` for the current Cloudflare route and turns the migration into a blocked compatibility gate.

## Changes

- `src/middleware.ts` remains the active request gate.
- `src/proxy.ts` is intentionally absent until OpenNext Cloudflare supports Node Middleware or the hosting route changes.
- `export function middleware`, `export const config` and the existing matcher were preserved.
- The protected-route gate still uses `SECURITY_HEADERS`, `isProtectedPath`, `hasPrototypeSession`, `buildLoginUrl`, kill switch and rate-limit checks.
- `scripts/vercel-preview-preflight.mjs` continues validating `src/middleware.ts`.
- `scripts/cloudflare-runtime-compatibility-proof.mjs` records the active middleware file and the absence of `proxy.ts`.
- `scripts/next-proxy-migration-proof.mjs` was added as the T10ah compatibility contract.

## Result

```text
NO_GO_NEXT_PROXY_MIGRATION_BLOCKED_BY_OPENNEXT_NODE_MIDDLEWARE_UNSUPPORTED
```

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
T10ai_cloudflare_provider_project_preflight_no_deploy
```

T10ai should prepare a Cloudflare provider-project preflight checklist and command contract without deployment, without tester URL publication and without creating tester accounts.

## Verification

T10ah is accepted when:

- this document exists
- `src/middleware.ts` exists and `src/proxy.ts` is absent
- `scripts/next-proxy-migration-proof.mjs` exists
- `package.json` exposes `proof:next-proxy-migration`
- the proof returns `NO_GO_NEXT_PROXY_MIGRATION_BLOCKED_BY_OPENNEXT_NODE_MIDDLEWARE_UNSUPPORTED`
- `scripts/vercel-preview-preflight.mjs` validates `middleware.ts`
- static tests, typecheck and Cloudflare/OpenNext proofs pass
- WSL/Linux local OpenNext preview still returns `/api/health` 200
- no Cloudflare project, deployment, Access policy, tester URL, tester account, tester email or production database state is introduced
- sensitive scan finds no tester emails, secrets, provider tokens, deployment URLs or account IDs in touched public files
- temporary WSL, `.next`, `.open-next`, `.wrangler`, `.dev.vars`, `node_modules`, lock and typegen artifacts are cleaned
- `git diff --check` passes
