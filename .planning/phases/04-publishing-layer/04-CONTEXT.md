# Phase 4: Publishing Layer — Context

**Gathered:** 2026-04-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Stand up the three-layer data pipeline end-to-end for CfD and publish the machine-readable contract external consumers use to discover, fetch, and cite our datasets. This is the phase where the project stops being "CfD visualization" and starts being a citable national resource.

In scope:

- **Derived layer for CfD.** `data/derived/cfd/{station_month, annual_summary, by_technology, by_allocation_round, forward_projection}.parquet` per ARCHITECTURE §4.2. Pydantic schemas in `src/uk_subsidy_tracker/schemas/`; loader-owned pandera validation.
- **Publishing layer.** `site/data/latest/cfd/*.parquet` + CSV mirror + `.schema.json` per table. `site/data/manifest.json` as the stable public contract.
- **`src/uk_subsidy_tracker/publish/` package.** `manifest.py`, `csv_mirror.py`, `snapshot.py`.
- **Scheme-module contract (§6.1).** `src/uk_subsidy_tracker/schemes/cfd/` exposing `upstream_changed`, `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`. First implementation of the pattern Phase 5 (RO) and every subsequent scheme copy.
- **`refresh_all.py`** — CI entry point with per-scheme dirty-check.
- **Raw-layer migration.** `data/*.csv` → `data/raw/<publisher>/<file>.csv` per ARCHITECTURE §4.1. Sidecar `.meta.json` backfilled for all five existing raw files.
- **`.github/workflows/refresh.yml`** — 06:00 UTC cron; PR-based posture (see D-04).
- **`docs/data/index.md`** — journalist/academic how-to-use-our-data page (PUB-04).
- **Test-class formal satisfaction.** TEST-02 (Parquet schema conformance), TEST-03 (Parquet row-conservation), TEST-05 (Parquet determinism) — previously scaffolded; now satisfied on real Parquet output.
- **LCCC self-reconciliation floor activation.** Transcribe LCCC ARA 2024/25 calendar-year CfD aggregate into `tests/fixtures/benchmarks.yaml::lccc_self`; the mandatory D-10 floor check from Phase 2 becomes green rather than skipped.
- **SEED-001 Tiers 2/3 (partial).** `tests/fixtures/constants.yaml` + `tests/test_constants_provenance.py` drift test. The adversarial-audit drift incident that planted the seed is evidence Tier 1 grep-discipline does not scale; this is the tripwire. Auto-rendered provenance doc page deferred to later polish.

Out of scope (belongs to later phases):

- External benchmark anchors beyond LCCC self (OBR EFO, DESNZ, HoC Library, NAO) — planner/researcher may add any they locate opportunistically, but Phase 4 does not block on anchor availability.
- `docs/abbreviations.md` glossary — Material `content.tooltips` feature sits empty; not a publishing-layer concern. Later polish.
- `tests/test_capacity_factor.py` (CF-formula pin) — chart methodology hardening, not publishing. Later phase.
- Second-scheme work — RO is Phase 5.
- Cross-scheme Parquet tables (`data/derived/combined/`) — Phase 6 creates these when X1–X5 charts read them.
- DuckDB-WASM / client-side query UI — V2-WASM-01.
- Zenodo DOI registration — V2-COMM-01, triggers after Phase 5.
- `uksubsidytracker.org` custom domain — deferred to post-Phase 6 per PROJECT.md.

</domain>

<decisions>
## Implementation Decisions

### Scheme-module refactor scope (D-01 … D-03)

- **D-01:** **Minimal-wrap refactor.** `src/uk_subsidy_tracker/schemes/cfd/` exposes the five §6.1 contract functions, with real (not stub) implementations. Aggregation logic is hoisted out of chart files into `schemes/cfd/cost_model.py`, `aggregation.py`, `forward_projection.py`. The contract must be load-bearing because Phase 5 (RO) copies it verbatim — a stub would rot immediately.
- **D-02:** **Chart files keep their current data path in Phase 4.** They can continue reading from `load_lccc_dataset` + in-memory aggregation, OR they can read from derived Parquet — planner's choice per chart. Forcing a full chart-migration into this phase risks scope blowout; the Parquet layer exists whether or not charts consume it today, because manifest.json + benchmarks + external consumers need it. Chart migration can land as a Phase 4.1 follow-up or piecemeal during Phase 5+.
- **D-03:** **`rebuild_derived()` is the canonical derivation path.** It re-derives the five grain tables directly from `data/raw/` and writes Parquet to `data/derived/cfd/`. Not "save whatever the charts produced" — the derivation must be independent and reproducible in CI without running Plotly. TEST-03 (row-conservation) and TEST-05 (determinism) exercise this path.

### Raw-layer migration (D-04 … D-06)

- **D-04:** **Migrate `data/` → `data/raw/<publisher>/<file>`** in Phase 4. Concretely:
  | Current path | New path |
  |---|---|
  | `data/lccc-actual-cfd-generation.csv` | `data/raw/lccc/actual-cfd-generation.csv` |
  | `data/lccc-cfd-contract-portfolio-status.csv` | `data/raw/lccc/cfd-contract-portfolio-status.csv` |
  | `data/elexon_agws.csv` | `data/raw/elexon/agws.csv` |
  | `data/elexon_system_prices.csv` | `data/raw/elexon/system-prices.csv` |
  | `data/ons_gas_sap.xlsx` | `data/raw/ons/gas-sap.xlsx` |
  Use `git mv` to preserve history. Filename underscores → hyphens to match ARCHITECTURE §4.1 layout (e.g. `system-prices.csv`, `gas-sap.xlsx`). This is a one-time churn; Phase 5 adds `data/raw/ofgem/` by necessity and would force the re-layout anyway. Doing it here while we are already touching every raw-data path (adding sidecars) is the right moment.
- **D-05:** **Backfill `.meta.json` sidecars** for all five existing raw files in the same commit as the rename. Sidecar shape per ARCHITECTURE §4.1: `{retrieved_at, upstream_url, sha256, http_status, publisher_last_modified}`. For backfilled entries, `retrieved_at` is "best-effort" (commit date of the raw file's last change in git log); `publisher_last_modified` is `null` where unknown; `http_status` is `null` (backfill marker). A `"backfilled_at": "2026-04-22"` field records this is reconstructed, not scraped.
- **D-06:** **All loaders updated atomically** in the rename commit: `src/uk_subsidy_tracker/data/lccc.py`, `elexon.py`, `ons_gas.py`, `lccc_datasets.yaml` (if it carries paths), plus the four `tests/data/*` test files and `tests/test_schemas.py`. CI must stay green across the rename commit; the commit message notes this is a layout migration, not a functional change.

### Publishing layer contract (D-07 … D-12)

- **D-07:** **`manifest.json` shape is ARCHITECTURE §4.3 verbatim.** Fields: `version`, `generated_at`, `methodology_version`, `datasets[]` with each dataset carrying `{id, title, grain, row_count, schema_url, parquet_url, csv_url, versioned_url, sha256, sources[], methodology_page}`. Source entries carry `{name, upstream_url, retrieved_at, source_sha256}`. No extra fields in Phase 4 — the schema is load-bearing for external consumers and should not churn.
- **D-08:** **Pydantic model is source of truth.** `src/uk_subsidy_tracker/publish/manifest.py` defines a `Manifest` Pydantic model (+ `Dataset`, `Source` sub-models); `json.dumps(model.model_dump(), indent=2, sort_keys=True)` produces `site/data/manifest.json`. Schema drift is a test failure. `sort_keys=True` + fixed indent guarantees byte-identity for determinism.
- **D-09:** **URLs in `manifest.json` are absolute.** Base URL comes from `mkdocs.yml::site_url` (or an env var override for local builds). Academics cite manifest URLs in papers — site-relative URLs are ambiguous. Format: `https://<host>/data/latest/cfd/station_month.parquet`, `https://<host>/data/v2026-04-21/cfd/station_month.parquet`. Local dev builds use `http://localhost:8000/...`.
- **D-10:** **CSV mirror is faithful.** Same column order as the Parquet source; standard pandas defaults otherwise (no index column, ISO timestamps, UTF-8, `\n` line endings, no thousand separators, full float precision). Journalists open the CSV in Excel; it should not need explanation.
- **D-11:** **Per-table `schema.json`.** Each published Parquet gets a sibling `<table>.schema.json` with column name, dtype, description, nullability, and unit where applicable. Derived from the Pydantic schema in `src/uk_subsidy_tracker/schemas/`. JSON Schema-compatible for machine validation.
- **D-12:** **`methodology_version` flows end-to-end.** `METHODOLOGY_VERSION` constant in `counterfactual.py` → DataFrame column on `compute_counterfactual()` output → Parquet column on tables that use the counterfactual → top-level `manifest.json::methodology_version` field. Any methodology change bumps the constant, which forces a manifest rebuild, which cascades into the next snapshot. This is the published-data realisation of Phase 2's GOV-04 discipline.

### Versioned snapshot storage (D-13 … D-15)

- **D-13:** **Snapshots ship as GitHub release artifacts** on tag push. Not committed into git (would bloat history on every release), not in R2 (no infrastructure needed until raw files breach 100 MB). On `git push --tags` the `deploy.yml` workflow uploads each Parquet + CSV + schema.json + the manifest-of-this-snapshot as assets on the release. Manifest's `versioned_url` points at the release asset URL: `https://github.com/richardjlyon/uk-subsidy-tracker/releases/download/v2026.04/cfd_station_month.parquet`.
- **D-14:** **Tag naming: `v<YYYY.MM>` calendar-based,** matching ARCHITECTURE §7.4 example (`v2026.04`). The `site/data/v<date>/` directory in ARCHITECTURE §4.3 is interpreted as a virtual URL-path served by Cloudflare Pages via redirect rules (or by the `deploy.yml` workflow writing a small index page) rather than a git-committed tree. Either way, academics cite `https://<host>/data/v2026-04-21/cfd/station_month.parquet` and it resolves — directly or via redirect — to the immutable release asset.
- **D-15:** **`latest/` lives under Cloudflare Pages.** `site/data/latest/cfd/*.parquet` is produced by the daily refresh and served from Cloudflare Pages alongside the rest of the MkDocs-built static site. Regenerated every refresh. Cache headers: short TTL on `manifest.json` (so consumers see new publications quickly), longer TTL on data files themselves (they are hash-addressable via `sha256` in manifest anyway).

### Daily-refresh workflow posture (D-16 … D-18)

- **D-16:** **PR-based commit-back.** Cron at 06:00 UTC triggers `refresh.yml` which runs `refresh_all.py`. If any scheme's `upstream_changed()` returns True, the workflow creates a branch `refresh/<date>-<run_id>` and opens a PR with the diff. Human reviewer merges after looking at the diff + CI results. Fully-autonomous commit-to-main defers until ~30 days of PR-based runs prove the scrapers don't publish garbage on a bad upstream day; auto-merge can be enabled later via branch protection without code change. Dry-run-only defeats GOV-03's point of an operational refresh.
- **D-17:** **Fail-loud on errors.** Scrape failures, derive failures, or benchmark floor regressions fail the workflow job — no silent skips. Additionally, the workflow opens a GitHub Issue labelled `refresh-failure` (new label; planner creates it) with the failing scheme, the upstream URL that failed, and a link to the run. The `correction` label (from Phase 1) handles corrections; `refresh-failure` handles automation breakage. These are distinct concerns.
- **D-18:** **Per-scheme dirty-check via SHA-256.** `refresh_all.py` reads each raw file's `.meta.json` sidecar, re-fetches the upstream, computes the new SHA, and only invokes `scheme.refresh() → rebuild_derived() → regenerate_charts()` if the SHA changed. Keeps the daily build under 5 min typical (per ARCHITECTURE §7.3) and keeps git history clean — no noisy Parquet reflow when nothing upstream changed.

### Test-class formal satisfaction (D-19 … D-22)

- **D-19:** **TEST-02 (`test_schemas.py`) adds Parquet variants** beside the existing raw-CSV scaffolding. Each derived table's Pydantic schema loads → validates via pandera → asserts no exception. Same "loader-owned validation" pattern as Phase 2 D-owner.
- **D-20:** **TEST-03 (`test_aggregates.py`) adds Parquet row-conservation.** Invariants: `sum(payment by year) == sum(payment by year × technology) == sum(payment by station_month grouped by year)` across the five derived grains. Exact equality via `pd.testing.assert_series_equal` (same precedent as Phase 2 D-owner).
- **D-21:** **TEST-05 (`test_determinism.py`) compares Parquet content modulo file-level metadata.** Write, read back, re-write, compare: schema + row count + row-wise content + per-column sums must be identical. Raw bytes are *not* compared because Parquet carries a file-level `created_by` string and row-group metadata timestamps that differ on every write. ARCHITECTURE §4.2 explicitly permits this interpretation ("modulo Parquet metadata timestamps"). Use pyarrow to strip and diff.
- **D-22:** **Parquet engine pinned.** Every `to_parquet()` call passes `engine="pyarrow"`, `compression="snappy"`, and explicit `index=False`. Default pandas row-group size is acceptable for current dataset sizes. `pyarrow` becomes a required dependency; the test_determinism strip uses it directly.

### SEED-001 partial fold-in (D-23 … D-25)

- **D-23:** **`tests/fixtures/constants.yaml` ships.** Mirrors `benchmarks.yaml` shape; covers the six `counterfactual.py` constants (CCGT_EFFICIENCY, GAS_CO2_INTENSITY_THERMAL, DEFAULT_NON_FUEL_OPEX, and the three DEFAULT_CARBON_PRICES entries). Each entry: `{source, url, basis, retrieved_on, next_audit, value, unit, notes}`. Loaded via a Pydantic model co-located with `BenchmarkEntry` in `tests/fixtures/__init__.py`.
- **D-24:** **`tests/test_constants_provenance.py` drift test ships.** Two parametrised tests: (1) every live constant in `counterfactual.py` has a YAML entry (reflection-based); (2) each YAML value matches its live constant to exact equality (drift detector). A third test warns but does not fail when `next_audit` has passed.
- **D-25:** **Auto-rendered provenance page deferred.** `docs/methodology/gas-counterfactual.md` already carries Tier 1 `Provenance:` blocks linked from chart pages. Auto-rendering from YAML to a standalone `docs/methodology/sources.md` adds Jinja/pre-build machinery that is not load-bearing for Phase 4's publishing story. Moves to a later polish phase (likely post-P11 steady-state, or v1.0.0 audit).

### Benchmark floor activation (D-26)

- **D-26:** **Transcribe LCCC ARA 2024/25 calendar-year CfD aggregate into `benchmarks.yaml::lccc_self`.** Phase 2 shipped the D-11 fallback posture (`lccc_self: []`, floor check skipped). Phase 4's reconciliation story — `manifest.json` carries benchmarks, `test_benchmarks.py` reconciles against them — wants the floor live. Transcribe the calendar-year total from the LCCC Annual Reserve Account 2024/25 report (year-end 31 Mar 2025; reconcile to calendar-year CfD payments via the per-quarter tables). Tolerance stays at 0.1% per Phase 2 D-06. External anchors (OBR, DESNZ, HoC, NAO) remain "as located" — planner/researcher folds any they find but does not block on unavailability.

### Documentation (D-27)

- **D-27:** **`docs/data/index.md` audience + contents.** Audience: journalists first, academics second, adversarial readers always. Sections:
  1. **What we publish** — Parquet canonical, CSV mirror, schema.json, manifest.json. What each is for.
  2. **How to use it** — Copy-pasteable snippets for pandas, DuckDB, and R, fetching the latest manifest and reading one table.
  3. **How to cite it** — Template referencing `CITATION.cff` + a versioned-snapshot URL. Example BibTeX/APA for academics.
  4. **Provenance guarantees** — SHA-256 checksums, retrieval timestamps, pipeline git SHA, methodology version. Link to `CHANGES.md`.
  5. **Known caveats and divergences** — Link to `test_benchmarks.py` reconciliation table.
  6. **Corrections and updates** — Link to `docs/about/corrections.md` + the `correction` GitHub Issues label.
  Linked from `docs/index.md` ("For journalists and academics → Use our data"); reachable from the theme navigation via a new top-level "Data" tab.

### Claude's Discretion

- **`refresh.yml` exact action versions** — pin Astral's `setup-uv` at the latest stable (Phase 2 used `astral-sh/setup-uv@v8.1.0`); use `actions/checkout@v5` per Phase 2 precedent. Planner refreshes versions at plan-time.
- **PR creation mechanism** — default: `peter-evans/create-pull-request@v6` (widely-used, pinned major). Planner may choose alternative if CI concerns emerge.
- **Parquet row-group size** — default: pandas default. Only tune if DuckDB scan performance emerges as a concern (deferred indefinitely).
- **`snapshot.py` interaction with release workflow** — default: `deploy.yml` calls `snapshot.py` which produces a temp dir of snapshot artifacts; the workflow then uploads them as release assets via `softprops/action-gh-release@v2`. Planner may restructure.
- **`schemes/cfd/validate()` return contract** — default: returns `list[str]` where each entry is a human-readable warning (row count outside expected envelope, benchmark floor drift, schema version mismatch). Empty list means healthy. Called as an optional post-rebuild check.
- **CSV column-order source of truth** — default: Pydantic schema field-declaration order. Changing column order is a manifest-breaking change and should bump a MAJOR version.
- **Manifest indent level + line-ending policy** — default: `indent=2`, LF line endings. Stable under `sort_keys=True` so determinism tests pass.

### Folded Todos

These items from STATE.md "Todos" land in Phase 4:

- **Transcribe LCCC ARA 2024/25 calendar-year CfD aggregate → `benchmarks.yaml::lccc_self`** (activates mandatory D-10 floor check) — see D-26.
- **SEED-001 Tiers 2 (partial) — `constants.yaml` + drift test** — see D-23, D-24.

These remain deferred (Phase 4 does not consume):

- **External benchmark anchors beyond LCCC** (OBR EFO, DESNZ, HoC, NAO) — still "as located." Researcher may fold any that surface during Phase 4 research; Phase 4 does not block.
- **`tests/test_capacity_factor.py` CF-formula pin test** — chart methodology hardening, not publishing. Later phase.
- **`docs/abbreviations.md` glossary** — Material `content.tooltips` feature remains empty until a docs-polish phase; unrelated to publishing-layer concerns.
- **SEED-001 Tier 3 — auto-rendered provenance doc page** — see D-25.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Authoritative spec

- `ARCHITECTURE.md` §4 — Three-layer data architecture (§4.1 source / §4.2 derived / §4.3 publishing). Authoritative for `data/raw/` layout, derived-grain naming, and `site/data/` structure.
- `ARCHITECTURE.md` §4.3 — `manifest.json` shape (lines 265–295). Verbatim contract for D-07.
- `ARCHITECTURE.md` §6.1 — Scheme-module contract (five functions). Load-bearing template for `schemes/cfd/` and every Phase 5+ scheme module.
- `ARCHITECTURE.md` §7 — Refresh cadence (§7.1), daily pipeline sketch (§7.2), dirty-check logic (§7.3), release tagging (§7.4).
- `ARCHITECTURE.md` §9.1 — Provenance requirements on derived Parquet files and how they surface in `manifest.json`.
- `ARCHITECTURE.md` §9.4 — Methodology versioning; how `methodology_version` flows from `counterfactual.py` through derived Parquet into `manifest.json`.
- `ARCHITECTURE.md` §9.6 — Five-class test table; Phase 4 formalises TEST-02, TEST-03, TEST-05 on Parquet outputs.
- `ARCHITECTURE.md` §11 P3 — Phase 4 entry/exit criteria (lines 906–918). Exit: "External consumer can fetch manifest.json, follow a URL, and retrieve a Parquet/CSV with provenance metadata."

### Roadmap + requirements

- `.planning/ROADMAP.md` Phase 4 — Five success criteria (lines 83–89). Planner must green every one.
- `.planning/REQUIREMENTS.md` — PUB-01, PUB-02, PUB-03, PUB-04, PUB-05, PUB-06, GOV-02, GOV-03, GOV-06 (snapshot URL portion), TEST-02, TEST-03, TEST-05. Traceability table rows (lines 179–187).
- `.planning/PROJECT.md` — Core-value "reproducible from git clone + uv sync + one command"; file-size policy (≤100 MB git / >100 MB R2); adversarial-proofing quality bar; key decisions (Parquet + DuckDB, Cloudflare Pages, daily refresh, methodology versioning).
- `.planning/STATE.md` — Carried-forward decisions, todos to fold (see D-26, D-23) or defer.

### Prior-phase context (locked decisions apply)

- `.planning/phases/01-foundation-tidy/01-CONTEXT.md` — Atomic-commit discipline (D-16); Material theme + palette config; `CITATION.cff` version field currently `0.1.0`; `CHANGES.md` Keep-a-Changelog format with `## Methodology versions` section.
- `.planning/phases/02-test-benchmark-scaffolding/02-CONTEXT.md` — Methodology-versioning discipline (D-05); TEST-02/03/05 formally mapped to Phase 4 (D-04); LCCC self-reconciliation as mandatory floor (D-10); D-11 fallback posture (external anchors "as located"); loader-owned pandera validation pattern; Pydantic+YAML fixture pattern (`benchmarks.yaml` → `constants.yaml` analog for D-23).
- `.planning/phases/03-chart-triage-execution/03-CONTEXT.md` — D-01 six-section chart page template + GOV-01 four-way coverage; `docs/methodology/gas-counterfactual.md` as single source of truth for counterfactual methodology; no `mkdocs-redirects` policy (D-04a) — same "clean break" applies to any URL changes in Phase 4.

### Seeds + planted context

- `.planning/seeds/SEED-001-constant-provenance-tiers-2-3.md` — Explicit Phase 4 primary trigger. D-23 / D-24 consume Tier 2 (YAML + drift test); D-25 defers Tier 3 (doc rendering).

### Codebase maps

- `.planning/codebase/ARCHITECTURE.md` — Current pattern / abstractions; chart inventory that `schemes/cfd/` hoists aggregations out of.
- `.planning/codebase/STRUCTURE.md` — Target directory layout including `data/raw/`, `data/derived/`, `site/data/`, `src/uk_subsidy_tracker/schemes/`, `src/uk_subsidy_tracker/publish/`, `src/uk_subsidy_tracker/schemas/` — none of which exist yet.
- `.planning/codebase/TESTING.md` — Current test patterns; §9.6 target scope (five classes).
- `.planning/codebase/STACK.md` — Python 3.12, uv, pandas, pandera, pytest 9.0.3. pyarrow + duckdb not yet added (see D-22, and SEED-001 implementation).
- `.planning/codebase/CONVENTIONS.md` — Naming, import, style conventions for new modules.

### Files to modify

- `pyproject.toml` — Add `pyarrow` (Parquet + determinism-strip) and `duckdb` (declared in ARCHITECTURE §3 table; add now since `docs/data/index.md` snippet demonstrates it and a validate() helper may use it). No `polars`.
- `src/uk_subsidy_tracker/counterfactual.py` — Already carries `METHODOLOGY_VERSION`; Phase 4 ensures the value propagates into every Parquet column that uses counterfactual output.
- `src/uk_subsidy_tracker/data/lccc.py`, `elexon.py`, `ons_gas.py`, `lccc_datasets.yaml` — Update paths for `data/raw/<publisher>/<file>` migration (D-04, D-06).
- `src/uk_subsidy_tracker/plotting/__main__.py` — If any chart is migrated to consume derived Parquet (per-chart planner decision), update the import path there. Default: unchanged.
- `mkdocs.yml` — Add `Data: data/index.md` top-level nav entry (D-27); verify `site_url` is correct for absolute-URL generation (D-09).
- `docs/index.md` — Add "For journalists and academics → Use our data" link.
- `docs/about/citation.md` — Update to reference versioned-snapshot release URL pattern.
- `CHANGES.md` — New `[Unreleased]` entries for: raw-layer migration, derived-layer + Parquet, publishing layer, scheme-module contract for CfD, daily-refresh workflow, constants.yaml drift test.
- `tests/fixtures/__init__.py` — Add `ConstantProvenance` Pydantic model + `load_constants()` loader alongside existing `BenchmarkEntry` + `load_benchmarks()`.
- `tests/test_schemas.py`, `tests/test_aggregates.py` — Add Parquet variants beside existing raw-CSV scaffolding (D-19, D-20).
- `tests/fixtures/benchmarks.yaml` — Add `lccc_self` entries from LCCC ARA 2024/25 (D-26).

### Files to create

- `src/uk_subsidy_tracker/schemas/__init__.py` + `cfd.py` — Pydantic schemas for the five CfD derived grains (station_month, annual_summary, by_technology, by_allocation_round, forward_projection).
- `src/uk_subsidy_tracker/schemes/__init__.py` — Base protocol or ABC enforcing §6.1 interface across schemes.
- `src/uk_subsidy_tracker/schemes/cfd/__init__.py` — `DERIVED_DIR` + five contract functions (D-01, D-03).
- `src/uk_subsidy_tracker/schemes/cfd/cost_model.py` — Station-month derivation.
- `src/uk_subsidy_tracker/schemes/cfd/aggregation.py` — Rollups (annual, by_technology, by_allocation_round).
- `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py` — Remaining-obligations projection.
- `src/uk_subsidy_tracker/publish/__init__.py`.
- `src/uk_subsidy_tracker/publish/manifest.py` — `Manifest` / `Dataset` / `Source` Pydantic models + `build()` (D-07, D-08, D-09).
- `src/uk_subsidy_tracker/publish/csv_mirror.py` — `build()` writes CSV alongside every Parquet (D-10).
- `src/uk_subsidy_tracker/publish/snapshot.py` — Produces versioned snapshot artifacts for `deploy.yml` to upload as release assets (D-13, D-14).
- `src/uk_subsidy_tracker/refresh_all.py` — CI entry point; per-scheme dirty-check + orchestration (D-18).
- `.github/workflows/refresh.yml` — Daily cron + PR-based commit-back (D-16, D-17).
- `.github/workflows/deploy.yml` — On-tag versioned-snapshot publishing (D-13, D-14).
- `data/raw/<publisher>/*.meta.json` sidecars — Five files (D-05).
- `tests/test_determinism.py` — Parquet determinism check (D-21, D-22).
- `tests/test_constants_provenance.py` — Drift test for `counterfactual.py` constants vs `constants.yaml` (D-24).
- `tests/fixtures/constants.yaml` — Six entries for `counterfactual.py` constants (D-23).
- `docs/data/index.md` — How-to-use-our-data page (D-27, PUB-04).

### External references

- Parquet spec (pyarrow): https://arrow.apache.org/docs/python/parquet.html — row-group layout + metadata handling for determinism-strip.
- DuckDB Python API: https://duckdb.org/docs/api/python/overview — for `docs/data/index.md` snippets and potential `validate()` queries.
- `peter-evans/create-pull-request`: https://github.com/peter-evans/create-pull-request — PR-based refresh workflow (D-16).
- `softprops/action-gh-release`: https://github.com/softprops/action-gh-release — versioned-snapshot release upload (D-13).
- JSON Schema Draft 2020-12: https://json-schema.org/ — for per-table `*.schema.json` (D-11).
- Keep-a-Changelog 1.1.0: https://keepachangelog.com/en/1.1.0/ — `CHANGES.md` format, already canonical.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`src/uk_subsidy_tracker/counterfactual.py::METHODOLOGY_VERSION`** — the version string + DataFrame column propagation shipped in Phase 2 (02-01). Phase 4 consumes it unchanged; Parquet writes inherit the column automatically.
- **`src/uk_subsidy_tracker/data/lccc.py::LCCCAppConfig`** — Pydantic + PyYAML loader pattern for `lccc_datasets.yaml`. Direct analogue for `tests/fixtures/constants.yaml` loader (D-23) and for the `Manifest` Pydantic model (D-08). Same two-layer pattern as `tests/fixtures/__init__.py::BenchmarkEntry + Benchmarks` from Phase 2 (02-03).
- **`src/uk_subsidy_tracker/data/lccc.py`** — existing pandera schemas (`lccc_generation_schema`, `lccc_portfolio_schema`) with loader-owned `.validate()` discipline. Derived-layer schemas extend this pattern, not replace it.
- **`tests/fixtures/__init__.py::load_benchmarks`** + `tests/fixtures/benchmarks.yaml` — Pydantic + YAML + source-key injection pattern (Phase 2 D-07). `constants.yaml` + `load_constants()` mirror this shape exactly.
- **`tests/test_counterfactual.py`** — 4-parametrised pin + remediation-hook failure message (Phase 2 02-01). The `test_constants_provenance.py` drift test should use the same failure-message pattern ("bump METHODOLOGY_VERSION, update constants.yaml, add CHANGES.md entry").
- **`tests/test_schemas.py` + `tests/test_aggregates.py`** — Phase 2 scaffolding variants. Phase 4 adds Parquet variants beside them in the same files; D-19 and D-20 call for coexistence rather than replacement.
- **`.github/workflows/ci.yml`** — Phase 2's pytest CI. Phase 4's `refresh.yml` + `deploy.yml` are NEW workflows; `ci.yml` stays as the pytest gate. `refresh.yml` may trigger `ci.yml` indirectly when its PR is opened.

### Established Patterns

- **Atomic commits per concern.** Phase 1 D-16, reinforced through Phases 2 and 3. Rename commit, sidecar backfill commit, schemes/cfd/ commit, publish/ commit, workflow commits — each distinct.
- **Loader-owned pandera validation.** Every `.validate()` lives inside the loader body, not in the test. Derived-layer loaders (in `schemes/cfd/`) follow the same rule.
- **Two-layer Pydantic model + source-key injection** (Phase 2 D-07). Used by `benchmarks.yaml`; applied to `constants.yaml` and to `manifest.json` schema.
- **Provenance docstring discipline** (Phase 3 commit `efdfbbc`). Every regulator-sourced constant in `src/` carries `Provenance:` blocks. Phase 4's `constants.yaml` references those blocks as the prose source.
- **Plotly charts are gitignored output** (`docs/charts/html/*.png/html`). Published Parquet + CSV in `site/data/latest/` follow the same rule: gitignored, regenerated by the daily refresh. Only **versioned snapshots** leave the build system, and they go to GitHub release artifacts (D-13).
- **Spec-precedence:** ARCHITECTURE.md beats ROADMAP when they conflict (Phase 2 02-05; user memory `project_spec_source.md`). Relevant because ROADMAP/REQUIREMENTS/ARCHITECTURE overlap heavily in Phase 4's wording.

### Integration Points

- **`counterfactual.py` DataFrame column → Parquet column → manifest.methodology_version** — the GOV-04 chain established in Phase 2 completes here. `manifest.py` reads the `methodology_version` column off one of the produced tables (or the constant directly) and stamps the top-level field.
- **`mkdocs build --strict` + `site/data/`** — MkDocs produces `site/` from `docs/`; Phase 4 adds `site/data/` as a parallel subtree populated by `publish/` modules, not by MkDocs. Both live under `site/` which is committed via `EndBug/add-and-commit` (or PR-equivalent, per D-16) after a refresh. The `docs` job in `ci.yml` + a new Parquet-build step in `refresh.yml` are the two production paths.
- **`CHANGES.md ## Methodology versions`** (Phase 1 D-17 + Phase 2 02-01) — continues to be the log where constants.yaml entries and methodology bumps are recorded. Phase 4 does not re-invent change-log machinery.
- **`tests/fixtures/*.yaml`** — now hosts two structured-provenance datasets (`benchmarks.yaml` from Phase 2, `constants.yaml` in Phase 4). Over time becomes the project's machine-queryable audit trail.
- **Cloudflare Pages deploy on push to `main`** (per PROJECT.md) — unchanged. Phase 4's refresh PR, when merged, triggers the Pages deploy via the existing repo settings. No new hosting infra.
- **GitHub Releases** — new integration point for versioned snapshots (D-13). Requires the `contents: write` GitHub Actions permission on `deploy.yml` only; other workflows stay at default read permissions.

### Known pre-existing considerations

- **`METHODOLOGY_VERSION` is currently `"0.1.0"` in `src/uk_subsidy_tracker/counterfactual.py`** — Phase 2 02-CONTEXT D-05 discussion spoke of `"1.0.0"`, and STATE.md also notes "1.0.0". Actual committed value is `"0.1.0"` (pre-portal, aligned with `CITATION.cff::version: "0.1.0"`). Per ARCHITECTURE §12 version policy, `1.0.0` is reserved for first portal launch. Phase 4 does NOT bump this — the version stays at `0.1.0` and is propagated through the new Parquet column + manifest field. Bump-to-1.0.0 is a Phase 6-or-later milestone event.
- **Raw data committed flat.** Phase 1 shortfall was fixed retroactively (commit `75774b8`); files live at `data/*.csv` / `data/*.xlsx`. Phase 4's D-04 migration normalises to nested layout per ARCHITECTURE §4.1.
- **No `schemes/` directory exists.** First creation is Phase 4 (D-01). No `schemes/__init__.py` base protocol either — create together.
- **No `site/data/` directory.** `site/` is MkDocs build output, gitignored; Phase 4 adds `site/data/` as a publishing-layer subtree that the refresh workflow commits.
- **`mkdocs.yml::site_url` already set** in Phase 1 (D-06). Verify it points at the final Cloudflare Pages / future custom domain before D-09 absolute-URL generation depends on it.

</code_context>

<specifics>
## Specific Ideas

- **"Academics cite the versioned URL"** is the acceptance test for PUB-03 + GOV-06. If a hypothetical reviewer can copy-paste a stable URL from `manifest.json::versioned_url` into a paper and have it resolve three years from now, the phase succeeds. This shapes D-13 (GitHub release artifacts are effectively permanent even if the org moves) and D-14 (calendar-based tag names match ARCHITECTURE's example verbatim).
- **"PR-based with easy upgrade path to auto-merge"** for D-16 — the human sees every refresh diff until the scrapers have earned trust, but branch-protection auto-merge can flip the switch with no code change.
- **"Manifest is the stable contract; everything else is an implementation detail"** — a consumer who reads `manifest.json` and follows URLs should be able to do their work without ever reading the MkDocs site. The tone of `docs/data/index.md` (D-27) reinforces this.
- **"Drift test catches what Tier 1 missed"** — the Phase 2 constant-drift incident (`0.184` vs `0.18290`, `53.0` vs `73.0`) is the concrete motivation for D-23 / D-24. Cite the incident in the test's docstring so future readers understand the tripwire's origin.
- **"The derivation path is the canonical one"** — `rebuild_derived()` must re-derive from raw. Never "save whatever the charts produced." Chart output capture defeats TEST-03 (row conservation is meaningless if the only source of truth is the chart's own aggregation) and TEST-05 (determinism).
- **File naming convention in derived layer: grains are snake_case, one table per grain** (ARCHITECTURE §4.2). `station_month.parquet`, not `stationmonth.parquet` or `station-month.parquet`. Cross-scheme consistency matters for Phase 5+.

</specifics>

<deferred>
## Deferred Ideas

- **Chart migration to read from derived Parquet.** Phase 4 writes the Parquet but does not force charts to consume it (D-02). Later polish phase (Phase 4.1 or piecemeal through Phase 5+) does the migration.
- **Auto-rendered provenance doc page (SEED-001 Tier 3).** D-25. Deferred to post-P11 steady-state or v1.0.0 audit.
- **External benchmark anchors** (OBR EFO, DESNZ, HoC Library, NAO) — still "as located." Researcher opportunistically adds any found; Phase 4 does not block on unavailability.
- **CF-formula pin test** (`tests/test_capacity_factor.py`) — chart-methodology hardening, not publishing. Later phase.
- **`docs/abbreviations.md` glossary** — Material `content.tooltips` feature already enabled but empty. Docs-polish phase, not Phase 4.
- **`data/derived/combined/` cross-scheme tables** — Phase 6 creates these when X1–X5 charts read them.
- **DuckDB-WASM client-side queries** — V2-WASM-01.
- **Zenodo DOI registration** — V2-COMM-01, triggers after Phase 5 lands.
- **Custom domain** (`uksubsidytracker.org` or similar) — post-Phase 6.
- **Cloudflare R2 for oversized raw files** (>100 MB) — first becomes relevant in Phase 8 (NESO BM half-hourly data, ARCHITECTURE §8.2). Not Phase 4.
- **Automated tag-release pipeline on a schedule** — Phase 4 ships `deploy.yml` that fires on manual `git tag` push. Quarterly release cadence per ARCHITECTURE "Post-P11 — steady state" becomes operational policy later; not automated in Phase 4.

### Reviewed Todos (not folded)

- `tests/test_capacity_factor.py` — deferred to a chart-methodology phase.
- `docs/abbreviations.md` — deferred to a docs-polish phase.
- External benchmark anchors — deferred per D-11 fallback posture from Phase 2.

</deferred>

---

*Phase: 04-publishing-layer*
*Context gathered: 2026-04-22*
