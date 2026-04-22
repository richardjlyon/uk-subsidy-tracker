# Phase 4: Publishing Layer — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in 04-CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-22
**Phase:** 04-publishing-layer
**Mode:** discuss (user delegated all four areas to Claude's discretion)

---

## Gray areas presented

| # | Area | Presented description |
|---|------|-----------------------|
| 1 | Scheme-module refactor scope | §6.1 contract is the template Phase 5+ scheme modules copy. Three postures: full clean refactor, minimal-wrap, or chart-output-capture. Also affects `data/raw/` layout (flat today, nested per ARCHITECTURE §4.1). |
| 2 | Versioned snapshot storage | GOV-06 + PUB-03 immutable citable URL. Three options: commit into git, push to Cloudflare R2, or GitHub release artifacts. |
| 3 | Daily-refresh workflow posture | GOV-03 06:00 UTC cron. Three postures: fully autonomous commit-back, PR-based, or dry-run-only. |
| 4 | Phase 4 scope fold-in | SEED-001 Tiers 2/3; LCCC ARA 2024/25 lccc_self backfill; external anchors; abbreviations glossary; CF-formula pin test — which belong in Phase 4? |

**User response:** "I'm happy with your discretion on these" (selected "Other" with a free-text note on the multi-select).

The user delegated all four decisions to Claude. No follow-up questions were asked in this session; instead, considered defaults with stated rationale were recorded under each decision block in 04-CONTEXT.md.

---

## Defaults chosen by Claude

### 1. Scheme-module refactor scope → Minimal-wrap

| Option | Pros | Cons | Selected |
|---|---|---|---|
| Full clean refactor | Gold-standard §6.1 template; Phase 5 copies it verbatim; no tech debt | Scope blowout in a phase already carrying manifest + snapshot + CI + provenance + raw-layer migration | |
| **Minimal-wrap** | Real §6.1 contract that Phase 5 can copy; aggregations hoisted into `schemes/cfd/` but charts keep current data path; scope contained | Two derivation paths temporarily coexist (chart in-memory + `rebuild_derived()`); chart migration is future work | ✓ |
| Chart-output-capture | Fastest; least invasive | Structurally wrong — no reusable contract; TEST-03/TEST-05 meaningless | |

**Rationale:** The contract is load-bearing for Phase 5+; a stub would rot. Scope-wise, the phase is already heavy (derived layer + publish/ + two workflows + raw-layer migration + SEED-001 partial + benchmark backfill), so charts continue consuming their current data path and migrate piecemeal later.

**Sub-decision (`data/raw/` layout):** Migrate now to nested layout (`data/raw/lccc/...`, `data/raw/elexon/...`, `data/raw/ons/...`). Phase 5 forces this anyway when it adds `data/raw/ofgem/`; doing it while we're already touching every raw-data path for `.meta.json` sidecars is the right moment.

### 2. Versioned snapshot storage → GitHub release artifacts

| Option | Pros | Cons | Selected |
|---|---|---|---|
| Commit into git | Simplest; snapshots are in the same artefact as the code | Bloats git history on every release; tests the 100 MB file-size policy as schemes land; no hard immutability guarantee | |
| Cloudflare R2 | Clean separation; cheap; fast; scales beyond 100 MB | Requires R2 account + keys + CI secrets; infra overhead before any file actually needs it | |
| **GitHub release artifacts** | Structurally immutable (release assets can't be edited); no git bloat; no infra setup; stable cacheable URLs; academics cite the release-asset URL directly | Release-asset URL is long; potentially wraps through a redirect to look like `/data/v2026-04-21/...` | ✓ |

**Rationale:** Matches the immutability requirement without new infrastructure. R2 is reserved for when raw files actually breach 100 MB (Phase 8+ NESO BM half-hourly). Git commits of snapshot Parquet are structurally wrong for a repo that also hosts source code.

### 3. Daily-refresh workflow posture → PR-based with fail-loud

| Option | Pros | Cons | Selected |
|---|---|---|---|
| Fully autonomous commit-back | Zero human toil; matches ARCHITECTURE §7.2 sketch literally | Scraper publishes garbage on a bad upstream day → production blip before anyone notices | |
| **PR-based commit-back** | Human sees every diff + benchmark CI result before merge; auto-merge trivially added later via branch protection; failure mode is a closed PR, not a production blip | Merge toil until auto-merge is flipped on | ✓ |
| Dry-run only | Safest short-term | Defeats GOV-03's "operational refresh" requirement | |

**Rationale:** Auto-merge is a branch-protection rule, not a code change, so we can upgrade in-place after ~30 days of clean PR-based runs. Fail-loud via GitHub Issue on scrape/derive failure (new `refresh-failure` label, distinct from `correction`).

### 4. Phase 4 scope fold-in → Partial

| Item | Fold in? | Rationale |
|---|---|---|
| SEED-001 Tier 2 (`constants.yaml` + drift test) | ✓ Fold | Seed explicitly names Phase 4; drift incident is concrete evidence grep-discipline doesn't scale; 4-6 hours of work |
| SEED-001 Tier 3 (auto-rendered provenance page) | ✗ Defer | Jinja/pre-build machinery not load-bearing for publishing story; later polish |
| LCCC ARA 2024/25 → `lccc_self` benchmark backfill | ✓ Fold | Phase 4's reconciliation story wants the mandatory D-10 floor live, not skipped |
| OBR/DESNZ/HoC/NAO external anchors | ~ Opportunistic | Phase 2 D-11 fallback remains; researcher folds any located, phase does not block |
| `docs/abbreviations.md` glossary | ✗ Defer | Unrelated to publishing; docs-polish concern |
| `tests/test_capacity_factor.py` CF-pin | ✗ Defer | Chart-methodology hardening, not publishing |

---

## Deferred Ideas (captured in 04-CONTEXT.md <deferred>)

- Chart migration to read from derived Parquet — later polish or piecemeal through Phase 5+.
- SEED-001 Tier 3 (auto-rendered provenance doc) — post-P11 steady state or v1.0.0 audit.
- External benchmark anchors — "as located" per Phase 2 D-11.
- CF-formula pin test — chart-methodology phase.
- `docs/abbreviations.md` glossary — docs-polish phase.
- `data/derived/combined/` cross-scheme tables — Phase 6.
- DuckDB-WASM client-side queries — V2-WASM-01.
- Zenodo DOI registration — V2-COMM-01, post-Phase 5.
- Custom domain — post-Phase 6.
- Cloudflare R2 for raw files >100 MB — first relevant Phase 8+.

---

*Phase: 04-publishing-layer*
*Discussion logged: 2026-04-22*
