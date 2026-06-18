# AGENTS.md — Entry point for AI agents (model-neutral)

> Read this first, then the linked docs, **before any work**. This file is a router; it restates nothing.

Any model-orchestrator (Claude, Codex/GPT, future) operating on this repo MUST, at session start, read:

1. **`docs/PROJECT_GOVERNANCE.md`** — the operating model: specialist-agent ownership matrix, phase namespaces (`Mxx Axx Rxx Sxx Qxx Gxx Vxx PGxx Jxx SBxx Txx`), gates G1-G7, the 13-step phase workflow, automation risk levels, and the Living Contracts Index. Rule **G2** requires consulting it before every work phase.
2. **`docs/PROJECT_STATE.md`** — cross-model routing/handoff queue (single source for routing). Phase state stays authoritative in `PROJECT_GOVERNANCE.md` "Current State". Propose the diff at the close of each work unit; the user approves before it is committed.
3. **`docs/INDEX.md`** — documentation map by namespace.

Multi-model coordination is introduced by proposed **G7 - Multi-Model Orchestration Gate** and **ADR-0002** (G7 becomes a governance baseline in Phase B). Model identity is **orthogonal** to specialist ownership: any model may act as any specialist role; the user routes handoffs (a model suggests, never self-assigns). Sign your state entries `model + date`.