# Phase 4: Publishing Layer - Research

**Researched:** 2026-04-22
**Domain:** Parquet publishing pipeline, manifest.json contract, GitHub Actions CI automation, deterministic serialization
**Confidence:** HIGH (stack, patterns, architecture); MEDIUM (LCCC ARA 2024/25 transcription — requires reading the PDF); HIGH (determinism pattern — documented in pyarrow API)

## Summary

Phase 4 converts the project from a single-scheme chart generator into a citable public data resource. The research surfaces four load-bearing facts: (1) Parquet determinism is achievable via `pa.Table.equals()` content comparison and is the only viable strategy because file-level `created_by` metadata is unavoidable; (2) Pydantic v2 does not support `sort_keys` on `model_dump_json()` — the correct pattern is `json.dumps(model.model_dump(mode="json"), sort_keys=True, indent=2)`; (3) `peter-evans/create-pull-request@v8` (NOT v6 — v8 is current as of October 2025) is the PR-based refresh mechanism with a known `GITHUB_TOKEN` cascading-workflow limitation the planner must acknowledge; (4) the LCCC ARA 2024/25 PDF is publicly available and secondary reporting places calendar-year 2024 CfD payments at £2.4 bn — a figure that is good enough for the D-26 floor if the planner cross-checks by transcribing the ARA's quarterly tables.

**Primary recommendation:** Plan five tightly-scoped plans — (A) raw-layer migration + sidecar backfill; (B) derived-layer schemas + `schemes/cfd/` contract + rebuild_derived; (C) publish layer (manifest + csv_mirror + snapshot) + Parquet determinism test; (D) refresh.yml + deploy.yml workflows + Issue-on-failure; (E) SEED-001 Tier 2 + LCCC floor activation + docs/data/index.md. Treat `refresh.yml` PAT question and LCCC-ARA figure confirmation as open questions surfaced early so Wave 0 can resolve them.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Scheme-module refactor scope (D-01 … D-03)**

- **D-01:** Minimal-wrap refactor. `src/uk_subsidy_tracker/schemes/cfd/` exposes the five §6.1 contract functions, with real (not stub) implementations. Aggregation logic is hoisted out of chart files into `schemes/cfd/cost_model.py`, `aggregation.py`, `forward_projection.py`. The contract must be load-bearing because Phase 5 (RO) copies it verbatim — a stub would rot immediately.
- **D-02:** Chart files keep their current data path in Phase 4. They can continue reading from `load_lccc_dataset` + in-memory aggregation, OR they can read from derived Parquet — planner's choice per chart. Forcing a full chart-migration into this phase risks scope blowout; the Parquet layer exists whether or not charts consume it today, because manifest.json + benchmarks + external consumers need it. Chart migration can land as a Phase 4.1 follow-up or piecemeal during Phase 5+.
- **D-03:** `rebuild_derived()` is the canonical derivation path. It re-derives the five grain tables directly from `data/raw/` and writes Parquet to `data/derived/cfd/`. Not "save whatever the charts produced" — the derivation must be independent and reproducible in CI without running Plotly. TEST-03 (row-conservation) and TEST-05 (determinism) exercise this path.

**Raw-layer migration (D-04 … D-06)**

- **D-04:** Migrate `data/` → `data/raw/<publisher>/<file>` in Phase 4 (5 files renamed with publisher nesting and underscores→hyphens). Use `git mv`.
- **D-05:** Backfill `.meta.json` sidecars for all five existing raw files in the same commit as the rename. Sidecar shape: `{retrieved_at, upstream_url, sha256, http_status, publisher_last_modified}` + `"backfilled_at": "2026-04-22"` marker. `retrieved_at` best-effort from git log last-change; `publisher_last_modified` is `null` where unknown; `http_status` is `null` (backfill marker).
- **D-06:** All loaders updated atomically in the rename commit: `lccc.py`, `elexon.py`, `ons_gas.py`, `lccc_datasets.yaml` (if paths carried), four `tests/data/*` files, `tests/test_schemas.py`. CI stays green across the rename commit.

**Publishing layer contract (D-07 … D-12)**

- **D-07:** `manifest.json` shape is ARCHITECTURE §4.3 verbatim. Fields: `version`, `generated_at`, `methodology_version`, `datasets[]` with each carrying `{id, title, grain, row_count, schema_url, parquet_url, csv_url, versioned_url, sha256, sources[], methodology_page}`. Source entries: `{name, upstream_url, retrieved_at, source_sha256}`.
- **D-08:** Pydantic model is source of truth. `publish/manifest.py` defines `Manifest` + `Dataset` + `Source`; `json.dumps(model.model_dump(), indent=2, sort_keys=True)` produces `site/data/manifest.json`.
- **D-09:** URLs in `manifest.json` are absolute. Base from `mkdocs.yml::site_url` (env-var override for local). Format: `https://<host>/data/latest/cfd/station_month.parquet`, `https://<host>/data/v2026-04-21/cfd/station_month.parquet`.
- **D-10:** CSV mirror is faithful. Same column order as Parquet; pandas defaults (no index column, ISO timestamps, UTF-8, `\n` line endings, full float precision).
- **D-11:** Per-table `schema.json`. Each published Parquet gets a sibling `<table>.schema.json` with column name, dtype, description, nullability, unit. Derived from the Pydantic schema. JSON Schema-compatible.
- **D-12:** `methodology_version` flows end-to-end. Constant in `counterfactual.py` → DataFrame column → Parquet column (where counterfactual used) → `manifest.json::methodology_version`. Phase 4 does NOT bump the value (stays at `"0.1.0"`); bump-to-1.0.0 is Phase-6-or-later.

**Versioned snapshot storage (D-13 … D-15)**

- **D-13:** Snapshots ship as GitHub release artifacts on tag push. Not committed into git; not in R2. `manifest.json::versioned_url` points at release asset URL: `https://github.com/richardjlyon/uk-subsidy-tracker/releases/download/v2026.04/cfd_station_month.parquet`.
- **D-14:** Tag naming: `v<YYYY.MM>` calendar-based. `site/data/v<date>/` is a virtual URL path (Cloudflare redirect rule or small index) resolving to the release asset.
- **D-15:** `latest/` under Cloudflare Pages. `site/data/latest/cfd/*.parquet` produced daily; served from Cloudflare Pages. Cache: short TTL on manifest, longer on data files.

**Daily-refresh workflow posture (D-16 … D-18)**

- **D-16:** PR-based commit-back. 06:00 UTC cron triggers `refresh.yml`; if `upstream_changed()` returns True, opens a PR on `refresh/<date>-<run_id>`. Human reviewer merges. Auto-merge enabled later via branch protection without code change.
- **D-17:** Fail-loud on errors. Scrape/derive/benchmark-floor failures fail the job; workflow opens a GitHub Issue with label `refresh-failure` (new label) citing failing scheme + upstream URL + run link.
- **D-18:** Per-scheme dirty-check via SHA-256. `refresh_all.py` reads `.meta.json`, re-fetches upstream, computes new SHA, invokes `scheme.refresh() → rebuild_derived() → regenerate_charts()` only if changed.

**Test-class formal satisfaction (D-19 … D-22)**

- **D-19:** TEST-02 (`test_schemas.py`) adds Parquet variants beside existing raw-CSV scaffolding. Each derived table's Pydantic schema loads → validates via pandera → asserts no exception.
- **D-20:** TEST-03 (`test_aggregates.py`) adds Parquet row-conservation. Invariants: `sum(payment by year) == sum(payment by year × technology) == sum(payment by station_month grouped by year)`. Exact equality via `pd.testing.assert_series_equal`.
- **D-21:** TEST-05 (`test_determinism.py`) compares Parquet content modulo file-level metadata. Write, read back, re-write, compare: schema + row count + row-wise content + per-column sums identical. Raw bytes NOT compared (file-level `created_by` and row-group metadata timestamps differ).
- **D-22:** Parquet engine pinned. Every `to_parquet()` passes `engine="pyarrow"`, `compression="snappy"`, `index=False`. Default pandas row-group size acceptable. `pyarrow` becomes a required dependency.

**SEED-001 partial fold-in (D-23 … D-25)**

- **D-23:** `tests/fixtures/constants.yaml` ships. Mirrors `benchmarks.yaml` shape; covers six `counterfactual.py` constants. Loaded via Pydantic model co-located with `BenchmarkEntry`.
- **D-24:** `tests/test_constants_provenance.py` drift test ships. Two parametrised tests: (1) every live constant has YAML entry (reflection-based); (2) each YAML value matches its live constant to exact equality. Third test warns but does not fail when `next_audit` has passed.
- **D-25:** Auto-rendered provenance page deferred. `docs/methodology/gas-counterfactual.md` keeps Tier 1 `Provenance:` blocks. Auto-rendering from YAML moves to later polish.

**Benchmark floor activation (D-26)**

- **D-26:** Transcribe LCCC ARA 2024/25 calendar-year CfD aggregate into `benchmarks.yaml::lccc_self`. Reconcile to calendar-year CfD payments via the per-quarter tables. Tolerance stays 0.1% per Phase 2 D-06. External anchors "as located" — researcher folds any found but does not block.

**Documentation (D-27)**

- **D-27:** `docs/data/index.md` audience + contents. Sections: (1) What we publish; (2) How to use it (pandas + DuckDB + R snippets); (3) How to cite it; (4) Provenance guarantees; (5) Known caveats; (6) Corrections. Linked from `docs/index.md`; reachable from theme navigation via a new "Data" top-level tab.

### Claude's Discretion

- `refresh.yml` exact action versions — pin `astral-sh/setup-uv@v8.1.0` (Phase 2 precedent); `actions/checkout@v5` (Phase 2 precedent). Planner refreshes at plan-time.
- PR creation mechanism — default `peter-evans/create-pull-request@v6`. Planner may choose alternative.
- Parquet row-group size — default pandas default. Only tune if DuckDB scan performance emerges as concern.
- `snapshot.py` interaction with release workflow — default: `deploy.yml` calls `snapshot.py` which produces a temp dir; workflow uploads via `softprops/action-gh-release@v2`.
- `schemes/cfd/validate()` return contract — default: `list[str]` where each entry is a human-readable warning.
- CSV column-order source of truth — default: Pydantic schema field-declaration order. Changing column order is a manifest-breaking change (MAJOR bump).
- Manifest indent level + line-ending policy — default: `indent=2`, LF line endings.

### Deferred Ideas (OUT OF SCOPE)

- Chart migration to read from derived Parquet (Phase 4.1 or Phase 5+).
- Auto-rendered provenance doc page (SEED-001 Tier 3) — post-P11 steady-state.
- External benchmark anchors beyond LCCC self (OBR EFO, DESNZ, HoC, NAO) — "as located."
- CF-formula pin test (`tests/test_capacity_factor.py`) — chart-methodology phase.
- `docs/abbreviations.md` glossary — docs-polish phase.
- `data/derived/combined/` cross-scheme tables — Phase 6.
- DuckDB-WASM client-side queries — V2-WASM-01.
- Zenodo DOI registration — V2-COMM-01, triggers after Phase 5.
- Custom domain — post-Phase 6.
- Cloudflare R2 for oversized raw files (>100 MB) — Phase 8 (NESO BM).
- Automated tag-release pipeline on schedule — Phase 4 fires on manual `git tag` only.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PUB-01 | `publish/manifest.py` builds `site/data/manifest.json` with provenance | §2 manifest Pydantic shape; §8 methodology propagation; §3 sidecar `.meta.json` feeds source SHA / retrieved_at |
| PUB-02 | `publish/csv_mirror.py` writes CSV alongside every published Parquet | §6 CSV mirror faithfulness — pandas args documented |
| PUB-03 | `publish/snapshot.py` creates versioned snapshot on tagged release | §4 snapshot flow via `softprops/action-gh-release@v2`; `deploy.yml` pattern |
| PUB-04 | `docs/data/index.md` documents journalist/academic use | §9 DuckDB + pandas + R snippets researched |
| PUB-05 | Three-layer pipeline operational end-to-end for CfD | §5 scheme-module contract; §11 migration sequence |
| PUB-06 | External consumer can fetch manifest, follow URL, get Parquet+CSV + provenance | §2 manifest shape + §9 absolute URL strategy from `site_url` |
| GOV-02 | Provenance per dataset (URL, retrieval timestamp, source SHA-256, pipeline git SHA, methodology version) | §1 Parquet determinism; §3 sidecar; §8 methodology version; §2 manifest (all provenance fields present) |
| GOV-03 | Daily refresh CI (06:00 UTC) with per-scheme dirty-check | §4 `refresh.yml` PR-based; §5 `upstream_changed()` + dirty-check pattern |
| GOV-06 (snapshot URL portion) | `CITATION.cff` + versioned snapshot URLs enable academic citation | §4 release artifact URL pattern |
| TEST-02 | `test_schemas.py` validates every derived Parquet against Pydantic schemas | §13 Parquet variant pattern |
| TEST-03 | `test_aggregates.py` proves sum-by-year = sum-by-year-tech; no row leakage | §13 Parquet aggregate-variant pattern |
| TEST-05 | `test_determinism.py` proves rebuilds produce content-identical Parquet | §1 Parquet determinism strategy; §13 test implementation |

</phase_requirements>

## Project Constraints (from CLAUDE.md)

Actionable directives extracted from `./CLAUDE.md`. The planner MUST verify each plan honours these.

- **Python 3.12+ only** — no Rust, Go, Polars migration, non-Python frameworks. Maintainability dominates.
- **Parquet + DuckDB** — no relational database. OLAP workload; 1:1,000,000 read:write ratio.
- **Static hosting on Cloudflare Pages only** — no backend, no containers, no workflow engines. GitHub Actions cron acceptable.
- **Plotly 6.x for charts** — already in production.
- **MkDocs Material for docs** — Python-native, 10-year stable, zero JS build pipeline.
- **Provenance non-negotiable** — every Parquet file carries source hash, retrieval timestamp, pipeline git SHA.
- **Reproducibility** — `git clone` + `uv sync` + one command must reproduce every published number byte-identically (modulo Parquet file-level metadata per D-21).
- **Adversarial-proofing** — every PRODUCTION chart = narrative + methodology + test + source-file link (GOV-01 from Phase 3, already closed).
- **File size policy** — raw CSVs ≤100 MB in git; larger files push to Cloudflare R2 with manifest pointer.
- **GSD workflow enforcement** — all repo edits must go through a GSD command; Phase 4 execution via `/gsd-execute-phase 4`.
- **Atomic commits per concern** — rename commit, sidecar commit, schemes commit, publish commit, workflow commits distinct.
- **Absolute paths everywhere** in agent threads.

## Architectural Responsibility Map

Maps each Phase-4 capability to its primary architectural tier.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Raw data (CSV/XLSX + sidecar meta.json) | Source layer (`data/raw/<publisher>/`) | — | ARCHITECTURE §4.1; preserves upstream-published artifacts |
| Pandera schema validation | Source layer (inside loaders) | — | Phase 2 D-owner: loader-owned `.validate()` discipline |
| Derived Parquet tables (five grains) | Derived layer (`data/derived/cfd/`) | — | ARCHITECTURE §4.2; columnar analytical outputs |
| Scheme-module contract (five functions) | Python package (`schemes/cfd/`) | Orchestration (`refresh_all.py`) | §6.1 base protocol; Phase 5+ copies this template |
| Aggregation / cost_model / forward_projection | Derivation code (`schemes/cfd/*.py`) | — | D-01 hoists from chart files |
| Pydantic table schemas | Type layer (`src/uk_subsidy_tracker/schemas/`) | Derivation + tests | Single source of truth for Parquet columns + `schema.json` emission |
| Publish artifacts (Parquet + CSV + schema.json) | Publishing layer (`site/data/latest/cfd/`) | CDN (Cloudflare Pages) | §4.3 ARCHITECTURE; served via Pages |
| `manifest.json` | Publishing layer (root of `site/data/`) | — | Public contract |
| Versioned snapshots | GitHub Releases (asset storage) | Publishing layer (virtual URL) | D-13: release artifacts, not git-committed |
| Daily refresh orchestration | CI (`.github/workflows/refresh.yml`) | Python (`refresh_all.py`) | D-16 PR-based; cron + script separation |
| On-tag release publishing | CI (`.github/workflows/deploy.yml`) | Python (`publish/snapshot.py`) | D-13 triggered on `git push --tags` |
| Journalist docs + citation | Docs layer (`docs/data/index.md` + MkDocs Material) | — | D-27 + PUB-04 |
| Benchmark reconciliation (LCCC floor + drift) | Test layer (`tests/test_benchmarks.py` + `tests/test_constants_provenance.py`) | Pipeline (fail the CI job) | D-26 + D-24 |

## Standard Stack

### Core additions for Phase 4

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pyarrow` | **24.0.0** (published 2026-04-21 `[VERIFIED: PyPI]`) | Parquet read/write; determinism strip via `Table.equals()`; file-metadata inspection | The canonical Arrow implementation. `pandas.to_parquet(engine='pyarrow')` delegates to it. Required for D-21 test. No Python alternative for true Parquet content comparison. |
| `duckdb` | **1.5.2** (published 2026-04-13 `[VERIFIED: PyPI]`) | Reference DuckDB for `docs/data/index.md` snippets; optional for `schemes/cfd/validate()` helper | ARCHITECTURE §3 declared. The `docs/data/index.md` SELECT query example demonstrates DuckDB reads Parquet natively. Low-cost addition now; unlocks Phase 6+ cross-scheme joins. |

**Version verification performed 2026-04-22 against PyPI JSON API.** Both packages have CPython 3.12 + 3.13 wheels for macOS-arm64 and linux-x86_64. No conflict with existing pins.

### Supporting (already present — re-used)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pandas` | 3.0.2 (already installed) | DataFrame I/O; `to_parquet()`, `to_csv()` | All I/O |
| `pydantic` | 2.13.1 | `Manifest`, `Dataset`, `Source` models; table schemas; `ConstantProvenance` | All validated data shapes |
| `pandera` | 0.31.1 | DataFrame schema validation inside loaders | Derived-layer loader validators (`schemes/cfd/`) |
| `pyyaml` | ≥6.0.3 | Load `constants.yaml` | YAML fixture loading |
| `pytest` | ≥9.0.3 | TEST-02/03/05 runner | All tests |

**Installation (planner — add to `pyproject.toml` under `dependencies`):**

```bash
uv add pyarrow>=24.0.0 duckdb>=1.5.2
# Then: uv lock && uv sync --frozen
```

### GitHub Actions (no Python deps; version pins for workflows)

| Action | Version | Purpose | Source |
|--------|---------|---------|--------|
| `actions/checkout` | `@v5` | Check out repo in workflow | Phase 2 precedent [VERIFIED: .github/workflows/ci.yml] |
| `astral-sh/setup-uv` | `@v8.1.0` | Install uv in GH Actions | Phase 2 precedent [VERIFIED: .github/workflows/ci.yml] |
| `peter-evans/create-pull-request` | `@v8` (latest; Oct 2025) | PR-based commit-back for daily refresh | [CITED: github.com/peter-evans/create-pull-request] — NOTE: CONTEXT D-16 default says `@v6`; v8 is the current major and v6 had a known "must enable PR creation in Settings" breaking change. Planner should pick v8 (current) OR v6 (pinned older stable). Either is acceptable — document the choice in PLAN. |
| `peter-evans/create-issue-from-file` | `@v6` (latest; Oct 2025) | Open GitHub Issue on refresh failure (D-17) | [CITED: github.com/peter-evans/create-issue-from-file] |
| `softprops/action-gh-release` | `@v2` (v2.6.2 Node-20-compatible; v3 requires Node-24) | Upload Parquet assets to GitHub release | [CITED: github.com/softprops/action-gh-release] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `pyarrow` for Parquet | `fastparquet` | fastparquet has weaker roundtrip fidelity and no content-comparison API. Reject — pyarrow is canonical. |
| `peter-evans/create-pull-request` | `gh pr create` in a run step | Higher cognitive load; action is proven and tracks branches automatically. Keep action. |
| `softprops/action-gh-release` | `gh release create --target` + `gh release upload` | Action is simpler for multi-asset uploads via glob. Keep action. |
| `json.dumps(sort_keys=True)` | Pydantic `model_dump_json()` | [CITED: Pydantic issue #7424] Pydantic v2 does NOT support `sort_keys` on `model_dump_json()` — must go via `model.model_dump(mode="json")` + stdlib `json.dumps`. |

## Architecture Patterns

### System Architecture Diagram

```
                             ┌────────────────────────────────────┐
Upstream regulators          │ GitHub Actions — refresh.yml        │
(LCCC, ONS, Elexon, Ofgem,   │  06:00 UTC cron, workflow_dispatch  │
 NESO, EMR)                  └────────────────────────────────────┘
                                       │  (fetches via requests)
                                       ▼
                      ┌──────────────────────────────────────┐
                      │ data/raw/<publisher>/<file>.csv       │  ◄── git (≤100 MB); R2 (>100 MB, Phase 8+)
                      │ data/raw/<publisher>/<file>.meta.json │      { retrieved_at, sha256, upstream_url,
                      └──────────────────────────────────────┘        http_status, publisher_last_modified }
                                       │
                                       │  upstream_changed()  ← dirty-check
                                       │  compares sha256 against sidecar
                                       ▼
                      ┌──────────────────────────────────────┐
                      │ schemes/cfd/                          │
                      │   cost_model.py      (station_month)  │
                      │   aggregation.py     (annual, by_tech,
                      │                       by_round)       │
                      │   forward_projection.py               │
                      │                                       │
                      │   refresh()                           │  ← writes data/raw/
                      │   rebuild_derived()                   │  ← writes data/derived/cfd/*.parquet
                      │   regenerate_charts()                 │  ← writes docs/charts/html/*.png
                      │   validate() -> list[str]             │
                      └──────────────────────────────────────┘
                                       │
                                       │  uses Pydantic schemas from
                                       │  src/uk_subsidy_tracker/schemas/cfd.py
                                       │  for pandera validation + schema.json emission
                                       ▼
            ┌──────────────────────────────────────────────────────────┐
            │ data/derived/cfd/                                          │
            │   station_month.parquet    (grain: station × month)        │
            │   annual_summary.parquet   (grain: year)                   │
            │   by_technology.parquet    (grain: year × technology)      │
            │   by_allocation_round.parquet                              │
            │   forward_projection.parquet                               │
            └──────────────────────────────────────────────────────────┘
                                       │
                                       │  publish/manifest.py + csv_mirror.py
                                       │  snapshot.py (on-tag)
                                       ▼
       ┌───────────────────────────────────────────────────────────────────┐
       │ site/data/                                                          │
       │   manifest.json                     ◄── Pydantic → json.dumps(sort) │
       │   latest/cfd/                                                       │
       │     station_month.parquet                                           │
       │     station_month.csv               ◄── CSV mirror                  │
       │     station_month.schema.json       ◄── from Pydantic               │
       │     ...                                                             │
       │   (virtual) v2026-04/cfd/station_month.parquet                      │
       │     └──────────────────────────────────────► GitHub Release         │
       │                                                v2026.04 artifact    │
       └───────────────────────────────────────────────────────────────────┘
                              │
                              │  Cloudflare Pages serves site/ on push to main
                              ▼
                        External consumers
                        (journalists, academics, adversarial analysts)
                        read manifest.json → follow URL → fetch Parquet/CSV
```

**Control flow on daily refresh:**

```
refresh.yml cron
    ↓
checkout + setup-uv
    ↓
uv run python -m uk_subsidy_tracker.refresh_all
    ↓
for each scheme:
    if scheme.upstream_changed():
        scheme.refresh()              # re-fetch raw; update .meta.json
        scheme.rebuild_derived()      # re-derive Parquet
        scheme.regenerate_charts()    # re-export PNG/HTML
        any_changed = True
    ↓
if any_changed:
    publish.manifest.build()          # stamp manifest.json
    publish.csv_mirror.build()        # CSV alongside Parquet
    ↓
    uv run pytest tests/test_benchmarks.py  # LCCC floor
    uv run mkdocs build --strict            # docs
    ↓
    peter-evans/create-pull-request  # branch refresh/<date>-<run_id>
else:
    echo "no upstream changes; skipping PR" && exit 0

on failure:
    peter-evans/create-issue-from-file  # label: refresh-failure
```

### Recommended Project Structure

```
.github/workflows/
  ci.yml              # [EXISTS — Phase 2] pytest + mkdocs-strict on push/PR
  refresh.yml         # [NEW] daily cron; PR-based commit-back (D-16)
  deploy.yml          # [NEW] on tag push; upload release artifacts (D-13)

data/
  raw/                # [NEW LAYOUT — D-04] git-committed; ≤100 MB
    lccc/
      actual-cfd-generation.csv
      actual-cfd-generation.csv.meta.json
      cfd-contract-portfolio-status.csv
      cfd-contract-portfolio-status.csv.meta.json
    elexon/
      agws.csv
      agws.csv.meta.json
      system-prices.csv
      system-prices.csv.meta.json
    ons/
      gas-sap.xlsx
      gas-sap.xlsx.meta.json
  derived/            # [NEW] .gitignore — regenerated
    cfd/
      station_month.parquet
      annual_summary.parquet
      by_technology.parquet
      by_allocation_round.parquet
      forward_projection.parquet

docs/
  data/
    index.md          # [NEW — D-27]
  ...

site/                 # [.gitignore — MkDocs build output]
  data/
    manifest.json
    latest/
      cfd/
        station_month.parquet
        station_month.csv
        station_month.schema.json
        ...

src/uk_subsidy_tracker/
  schemas/            # [NEW]
    __init__.py
    cfd.py            # Pydantic schemas for 5 derived grains
  schemes/            # [NEW]
    __init__.py       # Protocol/ABC for §6.1 contract
    cfd/
      __init__.py     # DERIVED_DIR + 5 contract functions
      cost_model.py
      aggregation.py
      forward_projection.py
  publish/            # [NEW]
    __init__.py
    manifest.py       # Manifest/Dataset/Source Pydantic + build()
    csv_mirror.py
    snapshot.py
  refresh_all.py      # [NEW] CI entry point

tests/
  fixtures/
    __init__.py       # [EXTEND — add ConstantProvenance + load_constants()]
    benchmarks.yaml   # [MODIFY — add lccc_self: 2024 entry per D-26]
    constants.yaml    # [NEW — 6 counterfactual constants]
  test_schemas.py     # [EXTEND — Parquet variants]
  test_aggregates.py  # [EXTEND — Parquet variants]
  test_determinism.py # [NEW — D-21, D-22]
  test_constants_provenance.py  # [NEW — D-24]
```

### Pattern 1: Parquet Determinism via Content Equality (D-21)

**What:** Write a DataFrame to Parquet twice; compare the two files by reading back and using `pyarrow.Table.equals()`. Never compare raw bytes — pyarrow writes a `created_by` string and row-group metadata that differ on every write.

**When to use:** Every Parquet file that `rebuild_derived()` produces.

**Example:**

```python
# tests/test_determinism.py
# Source: https://arrow.apache.org/docs/python/generated/pyarrow.parquet.FileMetaData.html
# and https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_table.html
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from uk_subsidy_tracker.schemes import cfd


GRAINS = ("station_month", "annual_summary", "by_technology",
          "by_allocation_round", "forward_projection")


@pytest.fixture(scope="module")
def derived_once(tmp_path_factory) -> Path:
    """First rebuild — writes to a fresh temp dir."""
    out = tmp_path_factory.mktemp("derived-run-1")
    cfd.rebuild_derived(output_dir=out)  # planner: rebuild_derived must accept output_dir
    return out


@pytest.fixture(scope="module")
def derived_twice(tmp_path_factory) -> Path:
    """Second rebuild — writes to another fresh temp dir."""
    out = tmp_path_factory.mktemp("derived-run-2")
    cfd.rebuild_derived(output_dir=out)
    return out


@pytest.mark.parametrize("grain", GRAINS)
def test_parquet_content_identical(grain, derived_once, derived_twice):
    """TEST-05 (D-21): rebuilds produce content-identical Parquet.

    Compares pyarrow.Table.equals() — NOT raw bytes. Parquet embeds a
    file-level `created_by` string and row-group timestamps that legitimately
    differ on every write. The spec-compliant determinism check is content
    equality.
    """
    t1 = pq.read_table(derived_once / f"{grain}.parquet")
    t2 = pq.read_table(derived_twice / f"{grain}.parquet")

    # Schema identity (column names + types + nullability).
    assert t1.schema.equals(t2.schema, check_metadata=False), (
        f"Parquet schema drift for {grain}:\n"
        f"  run1: {t1.schema}\n  run2: {t2.schema}"
    )
    # Row count identity.
    assert t1.num_rows == t2.num_rows, (
        f"Row count drift for {grain}: {t1.num_rows} vs {t2.num_rows}"
    )
    # Content identity — value by value, column by column.
    assert t1.equals(t2), (
        f"Parquet content drift for {grain} — same input should produce "
        f"identical rows. If intentional (methodology change), bump "
        f"METHODOLOGY_VERSION and add CHANGES.md entry."
    )


@pytest.mark.parametrize("grain", GRAINS)
def test_file_metadata_created_by_is_pyarrow(grain, derived_once):
    """Document the known non-deterministic field.

    Parquet file-level metadata includes `created_by` (a string like
    'parquet-cpp-arrow version 24.0.0') and per-row-group timestamps that
    differ on every write. This test pins the `created_by` prefix so that
    a future migration to another Parquet writer (fastparquet, polars) is
    surfaced explicitly.
    """
    meta = pq.read_metadata(derived_once / f"{grain}.parquet")
    assert meta.created_by.startswith("parquet-cpp-arrow"), (
        f"Parquet writer changed for {grain}: {meta.created_by!r}"
    )
```

**Fixed Parquet write pattern (for `schemes/cfd/` code):**

```python
# schemes/cfd/aggregation.py (sketch)
import pyarrow as pa
import pyarrow.parquet as pq

def write_parquet(df, path):
    """Deterministic Parquet writer (D-22)."""
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(
        table, path,
        compression="snappy",     # D-22 pin
        version="2.6",            # pin Parquet format version
        use_dictionary=True,      # default — pin explicitly
        write_statistics=True,    # default — pin explicitly
        data_page_size=1 << 20,   # 1 MB — pin
    )
```

**Why this matters:** `pd.DataFrame.to_parquet(engine="pyarrow")` goes through the same pyarrow writer. Pinning the pyarrow call at write time guarantees the determinism test sees deterministic content even if pandas internals shift. [CITED: arrow.apache.org/docs/python/parquet.html]

### Pattern 2: Manifest Pydantic Models + Deterministic JSON (D-07, D-08)

**What:** `publish/manifest.py` defines strict Pydantic v2 models; `build()` composes them from derived Parquet + sidecar meta.json + git SHA and writes via stdlib `json.dumps(sort_keys=True, indent=2)`.

**When to use:** Every manifest build (daily refresh + on-tag snapshot).

**Example:**

```python
# src/uk_subsidy_tracker/publish/manifest.py
# Source: ARCHITECTURE.md §4.3 verbatim + Pydantic v2 docs
# https://pydantic.dev/docs/validation/latest/concepts/serialization/
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class Source(BaseModel):
    """One upstream source that fed a derived dataset."""

    name: str
    upstream_url: str           # plain str, NOT HttpUrl — HttpUrl emits as object
                                # in some Pydantic edge cases; str is unambiguous
    retrieved_at: datetime
    source_sha256: str = Field(
        ..., pattern=r"^[0-9a-f]{64}$",
        description="Lowercase hex SHA-256 of the raw file."
    )


class Dataset(BaseModel):
    """One published dataset."""

    id: str                     # e.g. 'cfd.station_month'
    title: str
    grain: str                  # e.g. 'station × month'
    row_count: int = Field(..., ge=0)
    schema_url: str             # absolute URL
    parquet_url: str
    csv_url: str
    versioned_url: str
    sha256: str = Field(..., pattern=r"^[0-9a-f]{64}$")
    sources: list[Source]
    methodology_page: str


class Manifest(BaseModel):
    """Public contract. Shape is ARCHITECTURE §4.3 verbatim (D-07)."""

    version: str                # e.g. '2026-04-22' (date-like tag)
    generated_at: datetime
    methodology_version: str    # from counterfactual.METHODOLOGY_VERSION
    pipeline_git_sha: str       # GOV-02 requires this
    datasets: list[Dataset]


def _git_sha() -> str:
    """Current HEAD short SHA; stable across a single CI run."""
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True
    ).stdout.strip()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _site_url() -> str:
    """Absolute base URL (D-09).

    Reads mkdocs.yml::site_url. Env var SITE_URL overrides for local dev.
    """
    override = os.environ.get("SITE_URL")
    if override:
        return override.rstrip("/")
    with open("mkdocs.yml") as f:
        cfg = yaml.safe_load(f)
    return cfg["site_url"].rstrip("/")


def build(
    version: str,               # e.g. '2026-04-22' or 'v2026.04'
    derived_dir: Path = Path("data/derived"),
    raw_dir: Path = Path("data/raw"),
    output_path: Path = Path("site/data/manifest.json"),
) -> Manifest:
    """Assemble manifest from disk state and write to output_path.

    Deterministic JSON: model.model_dump(mode='json') produces the dict
    (datetimes as ISO-8601 strings); json.dumps(sort_keys=True, indent=2)
    stabilises key order and whitespace.
    """
    base = _site_url()
    git_sha = _git_sha()
    now = datetime.now(timezone.utc).replace(microsecond=0)

    # ... assemble datasets[] by walking derived_dir ...
    manifest = Manifest(
        version=version,
        generated_at=now,
        methodology_version=_read_methodology_version(),
        pipeline_git_sha=git_sha,
        datasets=[...],  # planner implements
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    # D-08: deterministic JSON via stdlib json; Pydantic v2 model_dump_json
    # does not support sort_keys (issue #7424).
    body = json.dumps(
        manifest.model_dump(mode="json"),
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    ) + "\n"  # trailing newline for POSIX-friendly diffs
    output_path.write_text(body, encoding="utf-8", newline="\n")
    return manifest
```

**Field type notes:**
- `upstream_url: str` (NOT `HttpUrl`) — HttpUrl's `__str__` works but Pydantic v2 serialisation of HttpUrl can vary across versions; `str` with optional pattern validation is safer for a public contract.
- `retrieved_at: datetime` — serialises as `"2026-04-22T05:58:00+00:00"` ISO-8601 by default [CITED: pydantic.dev/docs/validation/latest/concepts/serialization]. Always construct with `tzinfo=timezone.utc`.
- `sha256: str = Field(..., pattern=r"^[0-9a-f]{64}$")` — enforce lowercase hex. Hex (not base64) because it grep-matches `shasum -a 256` output and Git blob hashes.

### Pattern 3: Scheme-Module Contract (§6.1) — Duck-Typed Module + Protocol

**What:** Use a `typing.Protocol` in `schemes/__init__.py` to document the contract; individual scheme modules expose the five functions as module-level callables. No ABC — duck typing plus Protocol gives pyright coverage at project-configured "basic" mode.

**When to use:** Every scheme module from CfD (Phase 4) through Grid (Phase 11).

**Example:**

```python
# src/uk_subsidy_tracker/schemes/__init__.py
# Source: ARCHITECTURE.md §6.1 + typing.Protocol discipline
from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class SchemeModule(Protocol):
    """The ARCHITECTURE §6.1 contract every scheme must satisfy.

    Duck-typed: any module exporting these five callables at module scope
    (NOT on a class) conforms. pyright 'basic' mode picks this up when
    callers type-annotate `scheme: SchemeModule`.
    """

    DERIVED_DIR: Path

    def upstream_changed(self) -> bool: ...
    def refresh(self) -> None: ...
    def rebuild_derived(self, output_dir: Path | None = None) -> None: ...
    def regenerate_charts(self) -> None: ...
    def validate(self) -> list[str]: ...
```

```python
# src/uk_subsidy_tracker/schemes/cfd/__init__.py
from pathlib import Path

from uk_subsidy_tracker.schemes.cfd.cost_model import build_station_month
from uk_subsidy_tracker.schemes.cfd.aggregation import (
    build_annual_summary,
    build_by_technology,
    build_by_allocation_round,
)
from uk_subsidy_tracker.schemes.cfd.forward_projection import build_forward_projection
from uk_subsidy_tracker.schemes.cfd._refresh import (
    refresh as _refresh,
    upstream_changed as _upstream_changed,
)

DERIVED_DIR = Path("data/derived/cfd")


def upstream_changed() -> bool:
    """Return True if any LCCC/ONS/Elexon source file hash has changed."""
    return _upstream_changed()


def refresh() -> None:
    """Re-fetch LCCC + ONS + Elexon raw files; update data/raw/*.meta.json."""
    _refresh()


def rebuild_derived(output_dir: Path | None = None) -> None:
    """Build the five CfD derived Parquet tables from data/raw/.

    Args:
        output_dir: override DERIVED_DIR (test fixtures use this). Defaults
                    to `data/derived/cfd/`.
    """
    target = output_dir or DERIVED_DIR
    target.mkdir(parents=True, exist_ok=True)
    build_station_month(target)
    build_annual_summary(target)
    build_by_technology(target)
    build_by_allocation_round(target)
    build_forward_projection(target)


def regenerate_charts() -> None:
    """Regenerate all CfD PRODUCTION charts (delegates to plotting.__main__)."""
    from uk_subsidy_tracker import plotting
    plotting.main()  # or whatever existing entry point exposes


def validate() -> list[str]:
    """Health check. Empty list means healthy (D-discretion: returns warnings).

    Checks: (a) row count within envelope for latest year; (b) no NaN in
    Technology column; (c) manifest field cross-ref (methodology_version
    column matches constant).
    """
    warnings: list[str] = []
    # planner implements
    return warnings
```

**Why duck-typed module over ABC:** Modules can't inherit from an ABC directly. Wrapping each scheme in a class adds boilerplate (instance state with no reason to exist). Protocol documents the contract statically and lets pyright / isinstance checks (`isinstance(cfd, SchemeModule)` works with `@runtime_checkable`) verify conformance without a class. ARCHITECTURE §6.1 itself writes the contract as module-level `def`s.

### Pattern 4: CSV Mirror — Explicit Pandas Args (D-10)

**What:** Pandas defaults differ across OSes (Windows writes `\r\n`). Journalists open these files in Excel on all platforms. Pin every argument that matters.

**Example:**

```python
# src/uk_subsidy_tracker/publish/csv_mirror.py
# Source: pandas.DataFrame.to_csv docs; pandas 1.5 renamed line_terminator -> lineterminator
# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


def write_csv_mirror(parquet_path: Path, csv_path: Path) -> None:
    """Faithful CSV mirror of a derived Parquet (D-10).

    Column order: from the Parquet schema (which originated from the Pydantic
    model's field-declaration order). Writing a fresh mirror on every refresh
    avoids stale CSVs when schema evolves.
    """
    df = pq.read_table(parquet_path).to_pandas()
    df.to_csv(
        csv_path,
        index=False,               # journalists don't want the row number
        encoding="utf-8",          # UTF-8 BOM suppressed — Excel 2016+ is fine
        lineterminator="\n",       # LF even on Windows (D-discretion default)
        date_format="%Y-%m-%dT%H:%M:%S",  # ISO-8601 without fractional seconds
        float_format=None,         # full precision; let pandas repr the float
        na_rep="",                 # empty cell for NaN — Excel-friendly
    )
```

**Key arg rationale:**
- `index=False` — row numbers are meaningless for external consumers.
- `encoding="utf-8"` — explicit; pandas default but worth pinning. No UTF-8 BOM — modern Excel opens UTF-8 without it.
- `lineterminator="\n"` — pandas 1.5+ parameter name. Before 1.5 it was `line_terminator`. The project is on pandas 3.0, so `lineterminator` is correct. [CITED: pandas.DataFrame.to_csv]
- `date_format="%Y-%m-%dT%H:%M:%S"` — ISO-8601 without sub-seconds; Excel parses this without locale surprises.
- `float_format=None` — **do not** truncate; journalists may need full precision. The Parquet file stays canonical.

### Pattern 5: Per-table `schema.json` from Pydantic (D-11)

**What:** Pydantic v2's `model_json_schema()` emits JSON Schema Draft 2020-12 by default. Augment with `json_schema_extra={"unit": "..."}` on `Field` for custom `unit` keyword. `$defs` pulls nested models; use `model_json_schema(mode="serialization")` to capture the serialised shape.

**Example:**

```python
# src/uk_subsidy_tracker/schemas/cfd.py
# Source: https://pydantic.dev/docs/validation/latest/concepts/json_schema
from datetime import date, datetime

from pydantic import BaseModel, Field


class StationMonthRow(BaseModel):
    """One row in cfd/station_month.parquet.

    Field declaration order is the CSV column order (D-10 + D-discretion).
    """

    station_id: str = Field(
        description="LCCC CfD Unit ID.",
        json_schema_extra={"dtype": "string"},
    )
    technology: str = Field(
        description="Technology group (offshore wind, biomass, ...).",
        json_schema_extra={"dtype": "string"},
    )
    allocation_round: str = Field(
        description="CfD allocation round tag (AR1, AR2, AR3, ...).",
        json_schema_extra={"dtype": "string"},
    )
    month_end: date = Field(
        description="Last day of the settlement month.",
        json_schema_extra={"dtype": "date", "unit": "ISO-8601"},
    )
    cfd_generation_mwh: float = Field(
        description="Generation eligible for CfD payments in this month.",
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    cfd_payments_gbp: float = Field(
        description="Gross CfD payments received by the station in this month.",
        json_schema_extra={"dtype": "float64", "unit": "£"},
    )
    methodology_version: str = Field(
        description="Version tag of the gas counterfactual applied (GOV-04).",
        json_schema_extra={"dtype": "string"},
    )


def emit_schema_json(model: type[BaseModel], path) -> None:
    """Write <table>.schema.json sibling to the Parquet file."""
    import json
    schema = model.model_json_schema(mode="serialization")
    path.write_text(
        json.dumps(schema, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
```

**Notes:**
- Pydantic emits `"$schema": "https://json-schema.org/draft/2020-12/schema"` as `$schema` implicitly (no `$schema` key unless `schema_generator` is customised). For the publishing layer this is acceptable — external consumers that need a `$schema` declaration can add it via wrapper.
- `json_schema_extra={"unit": "£"}` lives alongside the type's standard keywords (`"type": "number"`). JSON Schema validators ignore unknown keywords — non-breaking.
- `mode="serialization"` vs `"validation"`: use `serialization` for the published artefact because it reflects what's on the wire, not what the loader will accept (e.g., Pydantic's "parse strings as datetimes" validation mode would list `str` as acceptable for `datetime` fields; serialization mode just says `string` with format `date-time`).

### Pattern 6: Sidecar `.meta.json` — Backfill + Fresh-Scrape (D-05, D-18)

**What:** Every raw file has a sibling `<file>.meta.json`. At backfill time (Phase 4 rename commit): best-effort reconstruct. At scrape time (scheme.refresh()): write authoritatively.

**Example (backfill script):**

```python
# scripts/backfill_sidecars.py  [one-shot; run during Phase 4 rename commit]
import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path

RAW_ROOT = Path("data/raw")
BACKFILL_DATE = "2026-04-22"
URL_MAP = {  # upstream URLs — planner audits these against existing loaders
    "lccc/actual-cfd-generation.csv":
        "https://dp.lowcarboncontracts.uk/datastore/dump/37d1bef4-55d7-4b8e-8a47-1d24b123a20e",
    "lccc/cfd-contract-portfolio-status.csv":
        "https://dp.lowcarboncontracts.uk/datastore/dump/fdaf09d2-8cff-4799-a5b0-1c59444e492b",
    "elexon/agws.csv":
        "https://data.elexon.co.uk/bmrs/api/v1/datasets/AGWS",
    "elexon/system-prices.csv":
        "https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices",
    "ons/gas-sap.xlsx":
        "https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/output/datasets/systemaveragepricesapofgas/...",
}


def git_last_change(path: Path) -> str:
    """Best-effort retrieved_at from git log."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cI", "--", str(path)],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip() or f"{BACKFILL_DATE}T00:00:00+00:00"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


for rel_path, upstream_url in URL_MAP.items():
    raw_path = RAW_ROOT / rel_path
    meta = {
        "retrieved_at": git_last_change(raw_path),
        "upstream_url": upstream_url,
        "sha256": sha256_of(raw_path),
        "http_status": None,              # backfill marker
        "publisher_last_modified": None,  # unknown for backfills
        "backfilled_at": BACKFILL_DATE,   # D-05 marker
    }
    meta_path = raw_path.with_suffix(raw_path.suffix + ".meta.json")
    meta_path.write_text(
        json.dumps(meta, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {meta_path}")
```

### Pattern 7: Constants Drift Test (D-23, D-24)

**What:** Reflect on `counterfactual.py` to enumerate constants; compare every UPPERCASE module attr of permitted types against `constants.yaml` entries.

**Example:**

```python
# tests/test_constants_provenance.py
# Source: SEED-001 Tiers 2/3 seed design
from datetime import date

import pytest

from tests.fixtures import ConstantProvenance, load_constants
from uk_subsidy_tracker import counterfactual


# Names the drift test checks. Keeping an explicit allowlist avoids
# accidentally pulling METHODOLOGY_VERSION (checked separately) or
# CCGT_NEW_BUILD_CAPEX_OPEX_PER_MWH (not YAML-backed — sensitivity only).
_TRACKED = {
    "CCGT_EFFICIENCY",
    "GAS_CO2_INTENSITY_THERMAL",
    "CCGT_EXISTING_FLEET_OPEX_PER_MWH",
    "DEFAULT_CARBON_PRICES_2021",   # synthetic keys for dict entries
    "DEFAULT_CARBON_PRICES_2022",
    "DEFAULT_CARBON_PRICES_2023",
}


def _live_constants() -> dict[str, float]:
    """Enumerate live numeric constants on the module."""
    live = {}
    for attr in dir(counterfactual):
        if not attr.isupper():
            continue
        value = getattr(counterfactual, attr)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            live[attr] = float(value)
        elif attr == "DEFAULT_CARBON_PRICES" and isinstance(value, dict):
            for year, price in value.items():
                live[f"DEFAULT_CARBON_PRICES_{year}"] = float(price)
    return live


@pytest.fixture(scope="module")
def constants():
    return load_constants()  # loads tests/fixtures/constants.yaml


@pytest.mark.parametrize("name", sorted(_TRACKED))
def test_every_tracked_constant_in_yaml(name, constants):
    """Every live constant has a YAML provenance entry (SEED-001 Tier 2)."""
    live = _live_constants()
    assert name in live, f"{name} is in _TRACKED but not on counterfactual module."
    assert name in constants.entries, (
        f"No constants.yaml entry for {name}. "
        f"Add provenance {{source, url, basis, retrieved_on, next_audit, value, unit}} "
        f"per SEED-001 Tier 2."
    )


@pytest.mark.parametrize("name", sorted(_TRACKED))
def test_yaml_value_matches_live(name, constants):
    """Drift detector — constant value must match YAML to exact equality.

    The Phase 2 adversarial audit caught `GAS_CO2_INTENSITY_THERMAL = 0.184`
    (wrong) vs 0.18290 (correct) by user inspection only. Tier 1 grep-discipline
    missed it. This test is the tripwire that would have caught it.

    If this fails: either (a) constant was intentionally edited — update YAML
    entry + bump METHODOLOGY_VERSION + add CHANGES.md ## Methodology versions
    entry, OR (b) constant drifted unintentionally — restore original value.
    """
    live = _live_constants()
    entry = constants.entries[name]
    assert live[name] == entry.value, (
        f"Drift detected for {name}: live = {live[name]}, yaml = {entry.value}. "
        f"Per SEED-001 Tier 2, bump METHODOLOGY_VERSION, update "
        f"tests/fixtures/constants.yaml, and add CHANGES.md `## Methodology "
        f"versions` entry. YAML source: {entry.url}"
    )


def test_audits_not_overdue(constants):
    """Warn (not fail) when any constant's next_audit has passed.

    Per SEED-001 seed rationale: overdue audits are an actionable signal,
    not a CI failure — blocking CI on a calendar event punishes downstream
    PRs for an orthogonal problem.
    """
    today = date.today()
    overdue = [
        (name, entry) for name, entry in constants.entries.items()
        if entry.next_audit is not None and entry.next_audit < today
    ]
    if overdue:
        import warnings
        for name, entry in overdue:
            warnings.warn(
                f"Overdue audit for {name}: next_audit = {entry.next_audit} "
                f"({(today - entry.next_audit).days} days ago). "
                f"Review source ({entry.url}) and update retrieved_on + next_audit."
            )
```

**`constants.yaml` shape:**

```yaml
# tests/fixtures/constants.yaml
# Per SEED-001 Tier 2. Mirrors tests/fixtures/benchmarks.yaml structure.
# Entries key = exact attribute name on src/uk_subsidy_tracker/counterfactual.py
# (for dict entries: SYNTHETIC_KEY_FORMAT = f"{ATTR}_{DICT_KEY}").

CCGT_EFFICIENCY:
  source: "BEIS Electricity Generation Costs 2023, Table ES.1"
  url: "https://www.gov.uk/government/publications/electricity-generation-costs-2023"
  basis: "Net HHV efficiency, H-class CCGT mid-range"
  retrieved_on: 2026-04-22
  next_audit: 2027-06-01
  value: 0.55
  unit: "dimensionless (fraction)"
  notes: "Blend of older F-class and modern H-class; existing fleet counterfactual."

GAS_CO2_INTENSITY_THERMAL:
  source: "DESNZ 2024 UK Government Greenhouse Gas Conversion Factors"
  url: "https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024"
  basis: "Gross CV (UK convention — suppliers bill in kWh gross CV)"
  retrieved_on: 2026-04-22
  next_audit: 2027-04-01
  value: 0.18290
  unit: "tCO2 / MWh thermal"
  notes: "Corrected from 0.184 during 2026-04-22 audit."

CCGT_EXISTING_FLEET_OPEX_PER_MWH:
  source: "BEIS Electricity Generation Costs 2023, Table ES.1"
  url: "https://www.gov.uk/government/publications/electricity-generation-costs-2023"
  basis: "Operational H-class CCGT, fixed + variable O&M"
  retrieved_on: 2026-04-22
  next_audit: 2027-06-01
  value: 5.0
  unit: "£/MWh"
  notes: "Existing fleet — capex sunk."

DEFAULT_CARBON_PRICES_2021:
  source: "OBR Economic & Fiscal Outlook — UK ETS annual average"
  url: "https://obr.uk/forecasts-in-depth/tax-by-tax-spend-by-spend/emissions-trading-scheme-uk-ets/"
  basis: "UK ETS annual average, £/tCO2"
  retrieved_on: 2026-04-22
  next_audit: 2027-01-15
  value: 48.0
  unit: "£/tCO2"
  notes: "First full UK ETS year post-Brexit divergence."

DEFAULT_CARBON_PRICES_2022:
  # ... same structure
  value: 73.0
  ...

DEFAULT_CARBON_PRICES_2023:
  # ... same structure
  value: 45.0
  ...
```

### Pattern 8: Refresh Workflow — PR-based + Issue-on-Failure (D-16, D-17, D-18)

**Example:**

```yaml
# .github/workflows/refresh.yml
# Source: peter-evans/create-pull-request docs + peter-evans/create-issue-from-file
# https://github.com/peter-evans/create-pull-request
# https://github.com/peter-evans/create-issue-from-file
name: Daily Refresh

on:
  schedule:
    - cron: '0 6 * * *'          # 06:00 UTC — after LCCC overnight publish
  workflow_dispatch:

permissions:
  contents: write                # push branch
  pull-requests: write           # open PR
  issues: write                  # D-17 refresh-failure issue

jobs:
  refresh:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0         # git log --follow, sidecar ops

      - name: Install uv
        uses: astral-sh/setup-uv@v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"

      - name: Install deps
        run: uv sync --frozen

      - name: Refresh (dirty-check per scheme)
        id: refresh
        run: uv run --frozen python -m uk_subsidy_tracker.refresh_all

      - name: Benchmark floor (LCCC)
        run: uv run --frozen pytest tests/test_benchmarks.py -v

      - name: Regenerate charts
        run: uv run --frozen python -m uk_subsidy_tracker.plotting

      - name: Build docs
        run: uv run --frozen mkdocs build --strict

      - name: Open PR if anything changed
        uses: peter-evans/create-pull-request@v8   # planner may pin @v6
        with:
          commit-message: "chore(refresh): daily data refresh ${{ github.run_id }}"
          title: "Daily refresh ${{ github.run_id }}"
          body: |
            Automated daily refresh opened by [refresh.yml](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}).
            Review Parquet diffs + rendered charts before merging.
          branch: refresh/${{ github.run_id }}
          delete-branch: true
          labels: daily-refresh
          add-paths: |
            data/raw/
            data/derived/
            docs/charts/html/
            site/data/
          # Note on token — the default GITHUB_TOKEN does NOT trigger
          # ci.yml on PR open (GitHub security feature). If the planner
          # wants the refresh PR to run the normal test gate, substitute
          # a PAT with `repo` scope or a GitHub App token. Default left
          # here; document open question in PLAN.

      - name: Open issue on failure
        if: failure()
        uses: peter-evans/create-issue-from-file@v6
        with:
          title: "Refresh failure — run ${{ github.run_id }}"
          content-filepath: ./.github/refresh-failure-template.md
          labels: refresh-failure
```

**Template file (committed to repo):**

```markdown
<!-- .github/refresh-failure-template.md -->
The daily refresh workflow failed.

**Run:** https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}
**Triggered:** ${{ github.event.schedule || 'manual' }}

Check the run logs for the failing step. Common causes:
- LCCC / Elexon / ONS upstream down or schema changed
- Benchmark floor (`test_lccc_self_reconciliation_floor`) tripped
- `mkdocs build --strict` found broken links

Label: `refresh-failure` (distinct from `correction` which tracks published corrections).
```

**Deploy workflow (tag-triggered):**

```yaml
# .github/workflows/deploy.yml
name: Release snapshot

on:
  push:
    tags: ['v*']

permissions:
  contents: write                # upload release assets

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Install uv
        uses: astral-sh/setup-uv@v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"

      - name: Install deps
        run: uv sync --frozen

      - name: Build snapshot artifacts
        run: uv run --frozen python -m uk_subsidy_tracker.publish.snapshot \
             --version "${{ github.ref_name }}" --output snapshot-out/

      - name: Publish release assets
        uses: softprops/action-gh-release@v2
        with:
          files: |
            snapshot-out/**/*.parquet
            snapshot-out/**/*.csv
            snapshot-out/**/*.schema.json
            snapshot-out/manifest.json
          body: |
            Immutable snapshot ${{ github.ref_name }}.
            See [manifest.json](https://github.com/${{ github.repository }}/releases/download/${{ github.ref_name }}/manifest.json) for dataset URLs.
```

### Anti-Patterns to Avoid

- **Comparing raw Parquet bytes for determinism.** `created_by` and row-group timestamps differ on every write. Always use `pyarrow.Table.equals()`.
- **Using `model_dump_json(sort_keys=True)`.** Pydantic v2 does not support sort_keys on `model_dump_json` [CITED: Pydantic issue #7424]. Must go via `model_dump(mode="json")` + `json.dumps(sort_keys=True)`.
- **Using `HttpUrl` for `manifest.json` URLs.** Pydantic v2 HttpUrl has had serialisation edge cases; `str` + pattern validation is unambiguous.
- **Letting `to_parquet()` pick defaults.** Defaults shift across pandas versions. Pin `engine`, `compression`, `version`, `index=False`.
- **Saving "whatever the charts produced" as derived Parquet.** D-03 forbids this. `rebuild_derived()` re-derives from raw.
- **Relative URLs in `manifest.json`.** D-09 requires absolute URLs. Academics cite across site moves.
- **Committing `data/derived/` or `site/data/`.** Both are regenerated. Only raw data + workflows + source + tests live in git. Daily refresh PR commits the CSV/Parquet outputs *because* they are reproducibility receipts the public reads — but in a separate `site/data/` subtree on the deploy branch (Cloudflare Pages reads from `main`, so the refresh PR merge does commit them — this is intentional and matches CONTEXT D-15 "latest/ lives under Cloudflare Pages").
- **Using `git mv` on data files without updating loader paths in the same commit.** CI will break mid-migration. D-06 mandates atomicity.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Parquet write with per-column compression tuning | Custom parquet writer | `pyarrow.parquet.write_table` with explicit kwargs | Parquet spec compliance + cross-platform byte compat |
| Deterministic Parquet comparison | SHA-256 of file bytes | `pyarrow.Table.equals()` | File-level metadata unavoidable |
| JSON Schema emission from Python models | Hand-written JSON Schema | `BaseModel.model_json_schema(mode="serialization")` | Automatic Draft 2020-12 compliance; drifts with model |
| Refreshed-data PR creation in a run step | `git push` + `gh pr create` | `peter-evans/create-pull-request` | Handles duplicate branches, metadata, labels automatically |
| GitHub release asset upload | Custom Octokit script | `softprops/action-gh-release` | Stable v2 since 2023; multi-asset glob |
| Cron → "only rebuild if upstream changed" | Polling timestamps | SHA-256 of raw file vs sidecar — `upstream_changed()` per scheme | Single source of truth in sidecar; survives timezone drift |
| Git SHA retrieval in Python | subprocess wrapper with retry | `subprocess.run(["git", "rev-parse", "HEAD"])` plain | GitHub Actions runner always has git; one-line call |
| CSV line-ending normalisation | Custom file rewriter | `pandas.to_csv(lineterminator="\n")` | Documented param; no post-processing step |
| Merkle/content hash of derived data | Custom hasher | `hashlib.sha256` on Parquet file + sidecar `.meta.json` | Same pattern as raw sidecars; manifest stamps these |
| "Render provenance YAML to a doc page" in Phase 4 | Jinja/pre-build pipeline | **Deferred** (D-25, SEED-001 Tier 3) | Out of scope — later polish |

**Key insight:** Phase 4 touches enough surface area (migration + schemas + publishing + workflows + tests) that hand-rolling even small things bloats the phase. The "don't hand-roll" discipline is stricter here than in Phases 1-3.

## Runtime State Inventory

Phase 4 is a greenfield + migration phase. The migration (D-04 raw layer rename) has runtime-state implications.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| **Stored data** | `data/*.csv` / `data/*.xlsx` at flat root (5 files) — will move to `data/raw/<publisher>/`. No database or external datastore. [VERIFIED: `ls -la data/` shows elexon_agws.csv, elexon_system_prices.csv, lccc-actual-cfd-generation.csv, lccc-cfd-contract-portfolio-status.csv, ons_gas_sap.xlsx] | `git mv` rename in a single commit; update loader paths atomically (D-06). |
| **Live service config** | **None.** No n8n, no external orchestrator, no dashboards. `mkdocs.yml::site_url` references `https://richardjlyon.github.io/uk-subsidy-tracker/` which is acceptable for Phase 4 (Cloudflare Pages deployment already works off github.io). If the planner decides to flip to a custom domain, that's an operational cutover not covered by Phase 4. | None required if site_url stays as-is. Planner must verify site_url matches where data will be served from before D-09 absolute-URL build. |
| **OS-registered state** | **None.** No systemd / Task Scheduler / pm2. Daily refresh runs inside GitHub Actions' ephemeral runner. | None. |
| **Secrets / env vars** | `GITHUB_TOKEN` (auto-provided). **No other secrets in use today** (`.env` absent per STACK.md). If the planner chooses PAT-based PR creation to trigger ci.yml on the refresh PR, a new `REFRESH_PAT` secret will need to be created by the user (out of scope for the agent). | If PAT approach adopted: document in PLAN that user creates secret `REFRESH_PAT` before first successful refresh run. Default (no PAT) still works for creating PRs; downstream ci.yml just doesn't trigger automatically. |
| **Build artifacts / installed packages** | `.venv/` is gitignored; `uv.lock` tracks dependency versions. Adding `pyarrow` and `duckdb` to `pyproject.toml` → `uv lock` → new `uv.lock` hash. `site/` is gitignored. `docs/charts/html/*.png`/`*.html` are gitignored. | `uv sync` after `uv lock` will install pyarrow + duckdb on all developers' machines + in CI. No stale state to purge (never built with pyarrow/duckdb before). |

**The canonical question answered:** After every file is updated, what runtime state still carries the old layout?

- **Nothing critical.** The raw data files live only in git. The derived layer doesn't exist yet. The publishing layer doesn't exist yet. There is no external service caching the old paths. The only "state" is the `uv.lock` hash, which updates naturally when `pyproject.toml` adds pyarrow + duckdb.

## Common Pitfalls

### Pitfall 1: Parquet determinism test passes locally, fails in CI

**What goes wrong:** Developer runs `pytest tests/test_determinism.py` twice on the same machine and it passes. GitHub Actions CI runs the same test and it fails because a timestamp field in the DataFrame used `datetime.now()` somewhere during derivation.

**Why it happens:** Non-determinism almost always comes from the **derivation step**, not from `pq.write_table`. A single `pd.Timestamp.now()` or `datetime.utcnow()` in `rebuild_derived()` creates a DataFrame that genuinely has different content on each run.

**How to avoid:** `rebuild_derived()` is a pure function of `data/raw/` content. No `now()`, no `random`, no clock. Timestamps that reflect "when the manifest was built" go in `manifest.json::generated_at`, not in Parquet columns.

**Warning signs:** Any diff between two runs that looks like it's only in a timestamp column. `Table.equals()` reports column-level mismatch at the very top of its error.

### Pitfall 2: `peter-evans/create-pull-request` works, but ci.yml never runs on the refresh PR

**What goes wrong:** The daily refresh opens a PR. CI doesn't trigger on `pull_request`. Reviewer merges blind.

**Why it happens:** `GITHUB_TOKEN` is intentionally restricted from triggering downstream workflows to prevent runaway CI loops. [CITED: peter-evans/create-pull-request docs — "cannot use the default GITHUB_TOKEN if pull requests must trigger on: push or on: pull_request workflows"]

**How to avoid:** Either (a) accept that the reviewer runs tests locally before merge, (b) use a PAT (classic with `repo` scope or fine-grained with `contents: write` + `pull-requests: write`) stored as `REFRESH_PAT` secret, or (c) use a GitHub App token. Option (a) is the default D-16 posture; options (b/c) are Phase-4.1 follow-ups.

**Warning signs:** Refresh PR is opened but no "Checks" appear. Actions tab shows no "pull_request" trigger for that PR.

### Pitfall 3: `manifest.json` changes every build even when nothing upstream changed

**What goes wrong:** Each refresh produces a manifest with a new `generated_at` timestamp, making the PR diff noisy even when data is identical.

**Why it happens:** `generated_at: datetime.now()` is set unconditionally at manifest build time.

**How to avoid:** `upstream_changed()` dirty-check at the top of `refresh_all.py` must **short-circuit** before manifest rebuild. If no scheme's SHA changed, do not rebuild manifest. Only produce a manifest when at least one data table was re-derived. Set `generated_at` to **the latest `retrieved_at` across sources** instead of `now()` — this makes the manifest content-addressed and testable.

**Warning signs:** Daily refresh opens a PR every day with zero Parquet changes but a manifest timestamp diff. Investigate the dirty-check.

### Pitfall 4: CSV mirror has `\r\n` line endings on Windows and breaks journalists' Unix pipelines

**What goes wrong:** A developer on Windows runs `uv run python -m uk_subsidy_tracker.publish.csv_mirror`, pandas writes CRLF line endings, the CSV looks fine in Excel but `wc -l` on Linux reports doubled line count.

**Why it happens:** `pandas.DataFrame.to_csv` with no `lineterminator` arg uses `os.linesep`. [CITED: pandas docs — "defaults to os.linesep ('\n' for Linux, '\r\n' for Windows)"]

**How to avoid:** Always pass `lineterminator="\n"` explicitly per D-discretion default. This is documented in Pattern 4 above.

**Warning signs:** `file site/data/latest/cfd/station_month.csv` reports `with CRLF line terminators`. Or journalists' Python scripts report row counts off by factors.

### Pitfall 5: Raw-layer migration commit breaks CI

**What goes wrong:** `git mv data/lccc-actual-cfd-generation.csv data/raw/lccc/actual-cfd-generation.csv` but `src/uk_subsidy_tracker/data/lccc.py` still references the old path → pytest fails.

**Why it happens:** The Python loaders hard-code relative paths. `lccc_datasets.yaml` only carries the filename, but `DATA_DIR / filename` resolves relative to the wrong location.

**How to avoid:** Single-commit atomic migration (D-06). Commit contains: (a) `git mv` of all 5 files; (b) edits to `lccc.py` / `elexon.py` / `ons_gas.py` filename constants / loader paths; (c) the 5 new `.meta.json` sidecar files. Planner MUST verify `uv run pytest` passes on the tip of this commit before rebasing.

**Warning signs:** `git show HEAD --stat` of the rename commit shows Python source file edits but no `.py` changes = incomplete.

### Pitfall 6: Pydantic HttpUrl serialises to an object instead of a string in some v2 contexts

**What goes wrong:** `manifest.json` ends up with `{"upstream_url": {"scheme": "https", "host": "..."}}` instead of the flat string journalists and academics expect.

**Why it happens:** Pydantic v2's `HttpUrl` is an `Annotated[str]` with validators; `model_dump(mode="python")` gives the `Url` wrapper type whereas `model_dump(mode="json")` coerces to string. If `json.dumps` is called without `mode="json"` dump first, the result may include the wrapped object.

**How to avoid:** Either (a) use `str` with an optional pattern validator (Pattern 2 default), or (b) always call `model_dump(mode="json")` before `json.dumps`. Option (a) is safer for public contract.

**Warning signs:** Test `test_manifest_urls_are_strings` passes locally on Pydantic 2.13 but fails on 2.14 — a hint that type coercion differs by version.

### Pitfall 7: The LCCC ARA 2024/25 figure is financial-year, not calendar-year

**What goes wrong:** Planner transcribes `£2.4bn` from the ARA 2024/25 as the `lccc_self: 2024` benchmark entry, but the ARA reports financial year (April 2024 – March 2025), not calendar year 2024.

**Why it happens:** UK government reports default to fiscal years. CfD payments are reported quarterly on the LCCC data portal, and the ARA aggregates them into FY totals. The Phase 2 tolerance rationale for `OBR_EFO_TOLERANCE_PCT` explicitly cites this FY-vs-CY drift (5%, not 0.1%).

**How to avoid:** For the 0.1% floor to hold, the benchmark entry MUST use a calendar-year aggregate. Two sources:
1. **Secondary reporting** (Watts Up With That, David Turver) cites `£2.4bn calendar-year 2024` — figure is CY. Value is sourced from the LCCC data portal's "Actual CfD Generation" dataset aggregated by calendar year. [CITED: wattsupwiththat.com/2025/01/28 — January 28, 2025 article]
2. **Primary reconstruction:** read LCCC data portal quarterly tables directly and sum Q1+Q2+Q3+Q4 2024.

For the Phase-4 D-26 entry, the planner should: (a) use £2.4bn (rounded) as the placeholder with 0.1% tolerance → will nearly certainly fail on exact reconciliation because the secondary reporting is rounded; (b) better: use the **same LCCC data portal query** our pipeline uses, summed by calendar year, as the "benchmark" — but this is a circular check (our pipeline vs itself). The correct move is to reconstruct from LCCC's own annual / quarterly published reports (not the data portal which is our source).

**Warning signs:** `test_lccc_self_reconciliation_floor` passes at 3% tolerance but fails at 0.1% when the entry is rounded to £2.4bn but our pipeline computes £2.387bn.

**Planner recommendation:** Ship with the best-effort figure from the LCCC ARA 2024/25 PDF (download: `https://www.lowcarboncontracts.uk/documents/293/LCCC_ARA_24-25_11.pdf`), marked in YAML `notes:` as "transcribed from ARA 2024/25 Table X, reconciled to calendar year via quarterly breakdown (pp. Y)". If the PDF only reports FY totals, ship `lccc_self: []` per D-11 fallback and file a Phase-4.1 todo to transcribe from a future regulator-native CY source. Either way, record the choice explicitly in PLAN.

## Code Examples

Verified patterns from official sources. Each is production-grade for the CfD module and is the template Phase 5+ will copy.

### Writing deterministic Parquet via pyarrow

```python
# Source: https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_table.html
import pyarrow as pa
import pyarrow.parquet as pq

def write_parquet(df, path):
    """D-22 pinned call pattern."""
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(
        table, path,
        compression="snappy",
        version="2.6",
        use_dictionary=True,
        write_statistics=True,
    )
```

### Comparing two Parquet files for content identity

```python
# Source: https://arrow.apache.org/docs/python/generated/pyarrow.parquet.FileMetaData.html
import pyarrow.parquet as pq

def parquet_content_identical(p1, p2) -> bool:
    """Compare two Parquet files by content (ignoring file-level metadata)."""
    t1 = pq.read_table(p1)
    t2 = pq.read_table(p2)
    return (
        t1.schema.equals(t2.schema, check_metadata=False)
        and t1.num_rows == t2.num_rows
        and t1.equals(t2)  # row-by-row, column-by-column
    )
```

### Reading a `manifest.json` from outside the project (journalist / academic pattern)

```python
# Source: docs/data/index.md (D-27 snippet)
# Pattern adapted for pandas from the Arrow parquet-reading quickstart.
import pandas as pd
import requests

MANIFEST = "https://richardjlyon.github.io/uk-subsidy-tracker/data/manifest.json"

# 1. Fetch the manifest (small JSON).
manifest = requests.get(MANIFEST).json()

# 2. Find the dataset you want.
station_month = next(
    d for d in manifest["datasets"]
    if d["id"] == "cfd.station_month"
)

# 3. Read the Parquet directly (pandas calls pyarrow).
df = pd.read_parquet(station_month["parquet_url"])

# 4. Verify integrity against published SHA-256.
import hashlib
import urllib.request
with urllib.request.urlopen(station_month["parquet_url"]) as resp:
    published_sha = hashlib.sha256(resp.read()).hexdigest()
assert published_sha == station_month["sha256"]
```

### Reading manifest + Parquet via DuckDB (journalist snippet)

```sql
-- Source: https://duckdb.org/docs/api/python/overview
-- Reproduce the subsidy-per-avoided-CO2 ratio from a fresh machine.
INSTALL httpfs;
LOAD httpfs;

SELECT
    station_id,
    technology,
    SUM(cfd_payments_gbp) AS lifetime_payments_gbp,
    SUM(cfd_generation_mwh) AS lifetime_generation_mwh
FROM read_parquet('https://richardjlyon.github.io/uk-subsidy-tracker/data/latest/cfd/station_month.parquet')
GROUP BY 1, 2
ORDER BY lifetime_payments_gbp DESC
LIMIT 10;
```

### Pydantic model for `.meta.json` sidecar validation

```python
# Source: ARCHITECTURE.md §4.1 + Phase 2 BenchmarkEntry pattern
from datetime import datetime
from pydantic import BaseModel, Field


class RawMeta(BaseModel):
    """Sidecar schema for every data/raw/<publisher>/<file>.meta.json."""

    retrieved_at: datetime
    upstream_url: str
    sha256: str = Field(..., pattern=r"^[0-9a-f]{64}$")
    http_status: int | None = None
    publisher_last_modified: datetime | None = None
    backfilled_at: str | None = None  # D-05 marker on reconstructed entries
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `line_terminator` param in pandas | `lineterminator` | pandas 1.5 (2022) | One-char rename; CI would fail with old name |
| `pyarrow`-the-library vs engine-only | Direct `pq.write_table` for determinism control | pyarrow 10+ (2023) | Explicit control over format_version, compression |
| `peter-evans/create-pull-request@v5` | `@v8` (current) | v6 (early 2024) added the "must enable PR creation in Settings" breaking change | Needed explicit `permissions:` block at workflow level |
| `softprops/action-gh-release@v1` | `@v2` (Node-20) / `@v3` (Node-24) | v2 (2023); v3 (late 2025) | v2.6.2 is the last Node-20-compatible line — pin if still on runners without Node 24 |
| `model_dump_json(sort_keys=True)` | `json.dumps(model.model_dump(mode="json"), sort_keys=True, indent=2)` | Pydantic v2.0+ (Jun 2023) | Pydantic v2 `model_dump_json` does NOT support sort_keys per issue #7424 |
| Parquet v1.0 format | Parquet v2.6 for nanosecond timestamps | Arrow 8+ (2022) | Pin `version="2.6"` explicitly in write_table calls |

**Deprecated/outdated:**
- `json.dump(model.dict())` — Pydantic v1 pattern; `.dict()` is `.model_dump()` in v2. [CITED: Pydantic v2 migration guide]
- GitHub Actions `actions/checkout@v3` — deprecated; repo is already on `@v5` via Phase 2.
- `fastparquet` for the derived layer — inconsistent Arrow-roundtrip fidelity; pyarrow is the canonical choice.
- `EndBug/add-and-commit` for the daily refresh commit-back — acceptable but `peter-evans/create-pull-request` gives PR-based review (D-16) which `add-and-commit` does not. ARCHITECTURE §7.2 example uses `EndBug/add-and-commit` but predates the D-16 decision.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | LCCC calendar-year 2024 CfD payments total £2.4bn (rounded from secondary reporting). | Pitfall 7, D-26 | If ARA 2024/25 transcription yields a materially different figure, the `lccc_self` floor fails at 0.1% and CI is red until fixed. Mitigation: planner cites the PDF table and figure explicitly; fallback to D-11 empty `lccc_self: []` if PDF reports FY only. |
| A2 | `mkdocs.yml::site_url` will remain `https://richardjlyon.github.io/uk-subsidy-tracker/` through Phase 4. | §9, Pattern 2, D-09 | If the user flips to a custom domain mid-phase, every `manifest.json::parquet_url` and `csv_url` reflects the old domain. Mitigation: planner checks site_url at Wave 0; if changing is on the table, do it BEFORE manifest code is written. |
| A3 | The project will continue committing raw CSVs and XLSX to git (all ≤100 MB). | §2.6 Structure, §3 | File growth could push Elexon AGWS past 100 MB (currently 58 MB). Mitigation: R2 migration is Phase 8 (NESO BM); not Phase 4's concern. |
| A4 | GitHub Actions' default `GITHUB_TOKEN` with `contents: write` + `pull-requests: write` is sufficient for `peter-evans/create-pull-request` to open refresh PRs. Downstream ci.yml may not run automatically on the PR. | Pitfall 2, Pattern 8 | If ci.yml must run on refresh PRs for the reviewer to merge with confidence, the user must create a PAT secret. Mitigation: document in PLAN as open question; reviewer manually triggers `workflow_dispatch` to rerun tests on the PR branch until PAT is added. |
| A5 | `pyarrow.Table.equals()` returns False on content drift but True on identical content across two writes of the same DataFrame — i.e., pyarrow 24.0's write path is itself deterministic in content (only file metadata differs). | Pattern 1, D-21 | If pyarrow itself writes non-deterministic content (e.g., row-group boundaries vary), the determinism test fails. Mitigation: pin `data_page_size`, `write_batch_size`, and compression-codec version. [CITED: arrow docs confirm snappy is deterministic]. If still flaky, fall back to schema+row_count+per-column-sum comparison rather than full `equals()`. |
| A6 | Pydantic v2's `model_dump(mode="json")` + `json.dumps(sort_keys=True)` produces byte-identical JSON across pandas/Pydantic minor upgrades. | Pattern 2, D-08 | Pydantic could change serialisation format of a type (e.g., `date` vs `datetime`) between versions. Mitigation: pin Pydantic to `>=2.13,<3.0` in pyproject.toml. |
| A7 | `duckdb` is safe to add now as a dependency even though Phase 4 does not invoke it in hot paths — it is only referenced in `docs/data/index.md` snippets. | Standard Stack | DuckDB wheel is ~30 MB installed; the benefit (unblocking cross-scheme joins + `validate()` helpers + reader example code) outweighs the installed-size cost. |
| A8 | `peter-evans/create-pull-request@v8` is preferred over `@v6` default in CONTEXT D-discretion. | Standard Stack | v6 may be what the user / future maintainer expects. Mitigation: planner picks one and documents in PLAN; either version works for PR-based refresh. |

**User confirmation recommended before execution:**
- A1 (LCCC figure) — planner should surface the exact transcribed value and page number for user sign-off.
- A4 (PAT vs no-PAT) — user must decide whether to create `REFRESH_PAT` secret before Phase 4 execution, or accept that refresh PRs have no auto-CI.

## Open Questions (RESOLVED)

1. **LCCC ARA 2024/25 — what's the calendar-year 2024 CfD total to 4 significant figures?**
   - What we know: LCCC ARA 2024/25 PDF is published at `https://www.lowcarboncontracts.uk/documents/293/LCCC_ARA_24-25_11.pdf`. Secondary reporting (Watts Up With That Jan 2025, David Turver Substack) cites £2.4bn rounded.
   - What's unclear: the exact figure on the primary source; whether the ARA publishes CY quarterly aggregates or only FY totals.
   - **RESOLVED:** Wave 0 of Phase 4 execution: plan-checker agent downloads PDF, transcribes Table X (CfD payments quarterly breakdown), and confirms calendar-year 2024 aggregate before Plan E authoring `benchmarks.yaml`. If PDF has only FY figures, ship D-11 fallback (`lccc_self: []`) and log a follow-up todo for the next ARA (or the annual LCCC quarterly-reconciliation exercise). Implemented via Plan 06 Task 3 checkpoint with A/B/C disposition matrix + 24h autonomous fallback to Disposition C.

2. **Refresh PR CI — do we want a PAT?**
   - What we know: default `GITHUB_TOKEN` is intentionally restricted from triggering workflow cascades. [CITED: GitHub docs]
   - What's unclear: whether the user wants to create a `REFRESH_PAT` secret or whether manual trigger of ci.yml on the refresh PR is acceptable.
   - **RESOLVED:** default to no PAT (simpler); reviewer manually dispatches ci.yml on the refresh branch if they want a test run before merge. Re-evaluate after 30 days. Implemented in Plan 05 Task 1 refresh.yml with comment block documenting the PAT follow-up for Phase 4.1.

3. **Does the first Phase-4 snapshot tag get published immediately?**
   - What we know: `deploy.yml` fires on `git tag -a v<YYYY.MM> && git push --tags`.
   - What's unclear: whether Phase 4 should conclude with an actual v2026.04 snapshot release (to prove the pipeline) or whether the first tag event is Phase 5 (RO module).
   - **RESOLVED:** Phase 4 exit checkpoint should include a dry-run of deploy.yml against a pre-release tag like `v2026.04-rc1`, asserting release artifacts upload cleanly. The "first real" v2026.04 tag can wait for Phase 5. This also lets the planner verify `softprops/action-gh-release@v2` behaves as expected on a real repo. Implemented in Plan 04 Task 3 snapshot.py dry-run + Plan 05 Task 2 deploy.yml with D-14 tag format validation (W-04).

4. **Cloudflare Pages virtual URL for `v<date>/` path — redirect rule or HTML stub?**
   - What we know: D-14 says the `site/data/v<date>/...` URL is a "virtual URL served via Cloudflare Pages redirect rules OR by the deploy.yml workflow writing a small index page". Both are valid.
   - What's unclear: which option the user prefers.
   - **RESOLVED:** default to **Cloudflare Pages redirect rules** (`_redirects` file in site/) — zero GitHub-side workflow changes, and Cloudflare reads `_redirects` natively. Out of scope for Phase 4 direct implementation per Plan 05 objective block (manifest.json::versioned_url fields reference GitHub release asset URLs directly, which are citable without a redirect layer). Plan-checker files a `_redirects` follow-up if/when needed in Phase 5+.

5. **`schemes/cfd/validate()` scope — which warnings does it emit?**
   - What we know: D-discretion says "returns list[str] where each entry is a human-readable warning".
   - What's unclear: exact envelope checks.
   - **RESOLVED:** ship with three checks: (a) row count for latest year within 10% of previous year (catches a broken upstream), (b) no null Technology in station_month (echoes the Phase 2 `test_no_orphan_technologies`), (c) `methodology_version` column matches `counterfactual.METHODOLOGY_VERSION` constant (catches stale Parquet written with an older version). Implemented in Plan 03 Task 2 Step 2F `validate()` body; also forms the D-12 chain closure cross-check cited in Plan 04 manifest.py docstring (W-07).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12+ | pyproject.toml requires-python | ✓ | 3.13 in .venv, 3.12 in CI | — |
| uv | All Python ops | ✓ (installed via Homebrew / curl script; CI uses `astral-sh/setup-uv@v8.1.0`) | Latest stable | — |
| git | Provenance SHA, `git mv`, backfill script | ✓ | — | — |
| pandas | DataFrame I/O | ✓ 3.0.2 | Already pinned | — |
| pandera | Schema validation | ✓ 0.31.1 | Already pinned | — |
| pydantic | Manifest + schema models | ✓ 2.13.1 | Already pinned | — |
| **pyarrow** | Parquet read/write + determinism | ✗ | — | **Block — add to pyproject.toml** |
| **duckdb** | `docs/data/index.md` snippets + possible `validate()` helper | ✗ | — | **Block for docs snippets — add to pyproject.toml** |
| requests | Scrapers (reused) | ✓ ≥2.33.1 | Already pinned | — |
| GitHub Actions runner | CI workflows | ✓ (ubuntu-latest) | — | — |
| GitHub repo permissions (contents:write, pull-requests:write, issues:write) | refresh.yml, deploy.yml | ✓ (default on new repos; user must verify in Settings → Actions → General → Workflow permissions) | — | If restricted, workflows fail at the create-PR step with a clear 403 error; user unblocks in Settings |
| GitHub repo setting "Allow GitHub Actions to create and approve pull requests" | `peter-evans/create-pull-request` v6+ | **Unknown — user must verify** | — | If disabled, the v6+ action fails with "Error: GitHub Actions is not permitted to create or approve pull requests." User enables in Settings → Actions → General. |
| PDF reader (human — to transcribe LCCC ARA 2024/25 if activated) | D-26 benchmark entry | ✓ (user/planner has browser + PDF reader) | — | Fallback to D-11 empty `lccc_self: []` |

**Missing dependencies with no fallback:**
- None — pyarrow and duckdb are addable; the GitHub repo settings toggle is user-level and must be checked.

**Missing dependencies with fallback:**
- GitHub repo setting for PR creation — if disabled, fallback is to use `gh pr create` in a bash `run:` step (but loses peter-evans's duplicate-PR handling).

## Validation Architecture

**Nyquist principle applied:** Phase 4 ships five independent validation axes, more than the ≥3 minimum. Each axis catches a distinct failure class; no single axis subsumes another.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3+ (already installed and green on CI per Phase 2) |
| Config file | No pytest.ini or `[tool.pytest.ini_options]` — default discovery |
| Quick run command | `uv run pytest -x` (fail-fast) |
| Full suite command | `uv run pytest -v` |
| Runs in CI | `.github/workflows/ci.yml` (unchanged) — `uv run --frozen pytest -v` |

### Five Validation Axes

**Axis 1 — Schema conformance (TEST-02).** Every derived Parquet loads into pandas, its Pydantic model loads the row dicts, and pandera re-validates post-load. Three failure sources are caught by this single axis: (a) Parquet dtype mismatch vs schema; (b) unexpected null in a non-nullable column; (c) Pydantic field-count drift (new column without schema update). Test file: `tests/test_schemas.py` (extend with Parquet variants per D-19). Runs: every commit.

**Axis 2 — Row conservation (TEST-03).** `sum(payment by year) == sum(payment by year × technology) == sum(payment by station_month grouped by year)` across the five derived grains. Catches silent NaN drops in groupby keys, duplicate rows, schema-to-schema sum arithmetic errors. Test file: `tests/test_aggregates.py` (extend per D-20). Runs: every commit.

**Axis 3 — Determinism modulo metadata (TEST-05).** Rebuild derived twice from the same raw state; compare via `pyarrow.Table.equals()`. Catches: (a) non-determinism in derivation (clock reads, random sorts, floating-point nondeterminism on platforms with different FMA paths); (b) pandas `groupby` sort-order instability. Test file: `tests/test_determinism.py` (new per D-21). Runs: every commit.

**Axis 4 — Benchmark floor reconciliation (LCCC).** Pipeline aggregate for calendar-year 2024 matches LCCC-published figure within 0.1% (D-26). This is an *external* anchor — if our pipeline diverges from LCCC's own published total, that's a pipeline bug, not a methodology drift. Test file: `tests/test_benchmarks.py::test_lccc_self_reconciliation_floor` (already ships; activated by populating `benchmarks.yaml::lccc_self`). Runs: every commit + daily refresh.

**Axis 5 — Manifest round-trip equivalence.** Build manifest → write JSON → read JSON → reload via `Manifest.model_validate(...)` → compare deeply. Catches: (a) serialisation format drift (datetime ISO-8601 loss), (b) Pydantic version upgrade surprises, (c) sort_keys ordering regressions. Test file: `tests/test_manifest.py` (new). Runs: every commit.

**Axis 6 — Constants drift (D-24).** Every live `counterfactual.py` UPPERCASE numeric constant has a YAML entry, and values match exactly. Three sub-tests per Pattern 7. Test file: `tests/test_constants_provenance.py` (new per D-24). Runs: every commit.

**Axes 1-3 are the `§9.6` formal five-class table on Parquet. Axes 4-6 are the project-specific quality bars.** Together they exceed the ≥3 Nyquist minimum by 2x, giving the planner ample coverage to verify all PUB-0x + GOV-0x requirements are backed by a test.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| PUB-01 | `manifest.json` carries full provenance per dataset | integration | `uv run pytest tests/test_manifest.py::test_manifest_provenance_fields_present -x` | ❌ Wave 0 — `tests/test_manifest.py` created in Plan C |
| PUB-02 | CSV mirror faithful alongside Parquet | unit | `uv run pytest tests/test_csv_mirror.py -x` | ❌ Wave 0 — new file in Plan C |
| PUB-03 | Snapshot ships on tag; versioned URL pattern | integration (smoke) | `uv run python -m uk_subsidy_tracker.publish.snapshot --dry-run` | ❌ Wave 0 — `snapshot.py` built in Plan C |
| PUB-04 | `docs/data/index.md` exists, reachable, renders in mkdocs-strict | docs build | `uv run mkdocs build --strict` | ✓ (ci.yml already runs) |
| PUB-05 | Three-layer pipeline operational end-to-end | integration | `uv run python -c "from uk_subsidy_tracker.schemes import cfd; cfd.rebuild_derived()"` followed by file-exist assertions | ❌ Wave 0 — `schemes/cfd/` built in Plan B |
| PUB-06 | External consumer fetches manifest + follows URL + gets data | manual-only (requires Cloudflare Pages deploy) | N/A — documented in VERIFICATION.md as post-deploy smoke | Manual |
| GOV-02 | Provenance (URL, timestamp, source SHA-256, pipeline git SHA, methodology version) per dataset | unit + integration | `uv run pytest tests/test_manifest.py -v` | ❌ Wave 0 |
| GOV-03 | Daily refresh CI with dirty-check committed | workflow smoke | `gh workflow run refresh.yml` on a feature branch → observe PR opens with expected changes | Manual — workflow_dispatch |
| GOV-06 (snapshot URL) | `CITATION.cff` + versioned snapshot URL resolves | manual | Curl `https://github.com/richardjlyon/uk-subsidy-tracker/releases/download/v2026.04-rc1/manifest.json` post-release | Manual |
| TEST-02 | Parquet schema conformance | unit | `uv run pytest tests/test_schemas.py::test_parquet_station_month_schema -x` | ✓ exists (raw-CSV variants); extend per D-19 |
| TEST-03 | Parquet row conservation | unit | `uv run pytest tests/test_aggregates.py::test_parquet_year_tech_conservation -x` | ✓ exists (raw-CSV variants); extend per D-20 |
| TEST-05 | Parquet determinism | unit | `uv run pytest tests/test_determinism.py -x` | ❌ Wave 0 — new file per D-21 |

### Sampling Rate

- **Per task commit:** `uv run pytest -x` (existing CI gate; all 5 axes run)
- **Per wave merge:** `uv run pytest -v && uv run mkdocs build --strict`
- **Phase gate:** Full suite green + `gh workflow run refresh.yml` smoke + VERIFICATION.md checklist green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_determinism.py` — covers TEST-05. Requires `pyarrow` dep + `schemes/cfd/rebuild_derived(output_dir=)` parameter.
- [ ] `tests/test_manifest.py` — covers PUB-01 + GOV-02 (round-trip and provenance fields).
- [ ] `tests/test_csv_mirror.py` — covers PUB-02 (line-endings, column order, value precision).
- [ ] `tests/test_constants_provenance.py` — covers D-24 (new per SEED-001).
- [ ] `tests/fixtures/constants.yaml` — the drift-test fixture.
- [ ] `tests/fixtures/__init__.py` extensions — `ConstantProvenance` Pydantic model + `load_constants()` loader alongside existing `BenchmarkEntry`.
- [ ] `tests/test_schemas.py` — Parquet variants added beside existing raw-CSV scaffolding (D-19).
- [ ] `tests/test_aggregates.py` — Parquet variants added beside existing raw-CSV scaffolding (D-20).
- [ ] Framework install — none needed (`pyarrow` and `duckdb` are Python deps already added to pyproject.toml in Plan A).

## Security Domain

`security_enforcement` is not explicitly set in `.planning/config.json` — per default-enabled policy, this section is included.

### Applicable ASVS Categories

Phase 4 is a static publishing pipeline with no user-facing authentication, no database, no live API. Most ASVS categories are **not applicable**. Those that apply:

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | No user auth — public read-only site |
| V3 Session Management | no | No sessions — static files only |
| V4 Access Control | no | Everything public |
| V5 Input Validation | **yes** | Pydantic v2 validates raw sidecar JSON, constants.yaml, benchmarks.yaml, and the manifest round-trip. Pandera validates raw CSVs. Any external data path is strictly-typed before reaching production code. |
| V6 Cryptography | **yes (read-only)** | SHA-256 via stdlib `hashlib` — not hand-rolled. Used as content address, not a security boundary. |
| V7 Error Handling & Logging | partial | `print()` for errors (STACK convention); GitHub Actions logs capture run output. No sensitive data in error messages (all our data is public). |
| V8 Data Protection | no | All data is public UK open government data. No PII. |
| V9 Communications | partial | HTTPS for upstream fetches (requests defaults); Cloudflare Pages serves over HTTPS by default. |
| V11 Business Logic | partial | Methodology-version discipline (D-12) + benchmark floor (D-26) + constants drift (D-24) enforce end-to-end correctness of published figures. The "business logic" here is scientific correctness. |
| V12 Files & Resources | **yes** | `data/raw/` → `data/derived/` → `site/data/` flow writes files by well-known paths inside the repo; no upload endpoint; no path traversal vector. R2 for >100 MB files is Phase 8+. |
| V14 Configuration | **yes** | `GITHUB_TOKEN` default; optional `REFRESH_PAT` secret if user adopts Pattern 8 note. `SITE_URL` env-var override for local dev; never checked in. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malicious upstream publishes corrupted CSV | Tampering | Pandera validation in loaders rejects malformed schema at load time; benchmark floor catches silent value drift (D-26); SHA-256 sidecar tracks whether file changed (not whether it's trustworthy — UK gov sources are the trust anchor). |
| PR-based refresh merges bad data | Tampering | D-16 human-in-loop reviewer; ci.yml runs pytest + mkdocs-strict on PR; benchmark floor fires in refresh.yml itself (pre-PR). |
| GitHub Actions token abuse | Elevation of Privilege | Minimal permissions per workflow; `contents: write + pull-requests: write` only on refresh.yml; `contents: write` only on deploy.yml; ci.yml stays default (read-only). |
| Parquet deserialisation RCE (pyarrow CVE class) | Tampering / EoP | pyarrow 24.0 pinned (current); `uv sync --frozen` in CI prevents drift; no `pickle` anywhere in the pipeline. |
| Sensitive data leak via GitHub release | Information Disclosure | All release assets are public data by design; nothing sensitive to leak. Sanity check: scripts/snapshot.py excludes `.env`, `.private/`, `tests/` by construction (strict allowlist of file types: `.parquet`, `.csv`, `.schema.json`, `.json`). |
| `manifest.json` URL tampering | Tampering | `sha256` field in manifest provides client-side integrity verification (code example in §9 Code Examples). |
| Refresh workflow loop — PR triggers CI triggers refresh triggers PR | Availability | `GITHUB_TOKEN` default does NOT trigger workflow cascades (see Pitfall 2) — this loop is impossible by design. PAT-based approach reintroduces the risk; mitigate by filtering `refresh.yml` on `github.event_name != 'pull_request'`. |

## Sources

### Primary (HIGH confidence)

- **ARCHITECTURE.md §4 (three-layer data architecture)** — authoritative for raw/derived/publishing layout.
- **ARCHITECTURE.md §4.3 (manifest.json shape)** — lines 265-295 are the verbatim contract for D-07.
- **ARCHITECTURE.md §6.1 (scheme-module contract)** — Python signature for `upstream_changed`, `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`.
- **ARCHITECTURE.md §7 (refresh cadence + dirty-check)** — drives Pattern 8.
- **ARCHITECTURE.md §9.6 (five-class test table)** — TEST-02/03/05 scope.
- **Phase 4 CONTEXT.md** — 27 locked decisions.
- **Phase 2 CONTEXT.md** — benchmarks.yaml pattern, loader-owned pandera, D-11 fallback posture.
- **pyarrow.parquet.write_table docs** (`arrow.apache.org/docs/python/generated/pyarrow.parquet.write_table.html`) — compression, version, row_group_size, data_page_size parameters.
- **pyarrow.parquet.FileMetaData docs** (`arrow.apache.org/docs/python/generated/pyarrow.parquet.FileMetaData.html`) — `created_by` string, format_version, equals() method.
- **Pydantic JSON Schema docs** (`pydantic.dev/docs/validation/latest/concepts/json_schema`) — Draft 2020-12 compliance, `json_schema_extra`, nested models via `$defs`.
- **Pydantic serialization docs** (`pydantic.dev/docs/validation/latest/concepts/serialization`) — datetime ISO-8601 default, `model_dump(mode="json")`.
- **pandas DataFrame.to_csv docs** (`pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html`) — lineterminator param, encoding default.
- **peter-evans/create-pull-request v8** (`github.com/peter-evans/create-pull-request`) — inputs, permissions, GITHUB_TOKEN limitation.
- **peter-evans/create-issue-from-file v6** (`github.com/peter-evans/create-issue-from-file`) — content-filepath, labels, title inputs.
- **softprops/action-gh-release v2** (`github.com/softprops/action-gh-release`) — multi-asset `files:` glob.
- **LCCC Annual Report 2024/25** (`lowcarboncontracts.uk/resources/.../low-carbon-contracts-company-lccc-annual-report-202425/`) — PDF at `/documents/293/LCCC_ARA_24-25_11.pdf`.
- **PyPI JSON API** (pyarrow 24.0.0 / duckdb 1.5.2 verified 2026-04-22).
- **Codebase reads (HIGH):** `src/uk_subsidy_tracker/counterfactual.py`, `tests/fixtures/__init__.py` (BenchmarkEntry), `.github/workflows/ci.yml`, `mkdocs.yml`, `pyproject.toml`.

### Secondary (MEDIUM confidence)

- **Watts Up With That — "Record £2.4 Billion in CfD Subsidies Paid Out in 2024"** (Jan 28, 2025) — secondary-reporting figure for LCCC calendar-year 2024; planner must cross-check against ARA 2024/25 PDF.
- **Pydantic issue #7424** (sort_keys on model_dump_json) — feature request remains open; confirms the stdlib-json workaround is the current pattern.
- **pandas issue #20353 (to_csv line-terminator on Windows)** — confirms explicit `lineterminator` is required.

### Tertiary (LOW confidence — flagged for validation)

- **David Turver Substack** — cited in Phase 2 D-08 as "commentator, not canonical"; referenced here only for LCCC CY 2024 cross-check.
- **Specific Cloudflare Pages `_redirects` behaviour for GitHub-release URL-templated redirects** — not yet tested; recommended as Phase 4 Wave 0 smoke test.

## Metadata

**Confidence breakdown:**

- **Standard stack:** HIGH — pyarrow 24.0, duckdb 1.5.2 verified via PyPI JSON API 2026-04-22; existing pandas/Pydantic/pandera versions confirmed via `uv pip show`.
- **Architecture patterns:** HIGH — ARCHITECTURE.md §6.1 is verbatim; Pydantic docs cover serialisation and JSON Schema; pyarrow docs cover determinism API.
- **Parquet determinism:** HIGH — pyarrow `FileMetaData.created_by` is documented; `Table.equals()` API is stable since Arrow 0.12. Determinism of snappy compression + default row-group layout is an assumption (A5) but widely observed.
- **GitHub Actions workflow patterns:** HIGH — peter-evans actions are mature (v8 / v6); softprops-action-gh-release v2 is stable; known GITHUB_TOKEN limitation is explicit in vendor docs.
- **LCCC ARA 2024/25 figure:** MEDIUM — secondary reporting converges on £2.4bn CY 2024, but the planner must read the primary PDF to populate `benchmarks.yaml::lccc_self` with 4-significant-figure precision. If the PDF reports only FY, ship D-11 fallback and file a follow-up.
- **Common pitfalls:** HIGH — each pitfall cites documented behaviour (Pydantic issue, pandas docs, peter-evans docs).

**Research date:** 2026-04-22

**Valid until:** 2026-05-22 (30 days — stack is stable; LCCC ARA figure confirmation is the only item that could change earlier).

## RESEARCH COMPLETE
