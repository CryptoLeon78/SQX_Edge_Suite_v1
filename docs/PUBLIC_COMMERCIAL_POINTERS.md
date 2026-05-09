# Public Commercial Pointers

Phase S5 redacted the public commercial surface after the private repository copy was verified.

The complete commercial roadmap, buyer operations, checkout runbooks and Pro template assets live in the private repository:

- Private repository: `https://github.com/CryptoLeon78/sqx-edge-commercial-private`
- Private baseline commit: `ed79719 Initial private commercial export`
- Public redaction date: `2026-05-07`
- Public manifest: `docs/private_commercial_manifest.json`

The public repository intentionally keeps only pointer files for these source sets:

- `docs/MONETIZATION_ROADMAP.md`
- `docs/MONETIZATION_M*.md`
- `docs/sales/`
- `resources/pro-buyer-pack/`
- `resources/pro-template-pack-1/`
- `resources/pro-template-pack-2/`

This preserves path-level traceability without publishing operational buyer evidence, pricing experiments, checkout details, support macros or paid template payloads.

New commercial phases after S5 follow the same rule: public files are pointer stubs, while the complete operational documents live in the private repository.
M72 continues this rule: the controlled distribution details live privately, while public files keep traceability only.
M73 continues this rule: controlled distribution review details live privately, while public files keep traceability only.
M74 continues this rule: buyer-facing asset preparation details live privately, while public files keep traceability only.
M75 continues this rule: private asset review details live privately, while public files keep traceability only.
M76 continues this rule: controlled publication gate details live privately, while public files keep traceability only.
M77 continues this rule: limited publication draft details live privately, while public files keep traceability only.
M78 continues this rule: operator publication review details live privately, while public files keep traceability only.
M79 continues this rule: manual limited publication record details live privately, while public files keep traceability only.
M80 continues this rule: manual publication monitor details live privately, while public files keep traceability only.
M81 continues this rule: controlled traffic expansion review details live privately, while public files keep traceability only.
M82 continues this rule: tiny controlled traffic expansion step details live privately, while public files keep traceability only.
M83 continues this rule: tiny controlled traffic expansion monitoring details live privately, while public files keep traceability only.
M84 continues this rule: controlled traffic expansion decision details live privately, while public files keep traceability only.
M85 continues this rule: controlled traffic expansion execution details live privately, while public files keep traceability only.
M86 continues this rule: controlled traffic expansion execution monitoring details live privately, while public files keep traceability only.
M87 continues this rule: controlled commercial next movement details live privately, while public files keep traceability only.
M88 continues this rule: controlled commercial next movement execution details live privately, while public files keep traceability only.

Treat public Git history as already exposed. Rotate any credential, checkout secret, token or private key that ever appeared outside the private boundary.
