# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `docs/data/index.md` (Plan 04-06) — journalist/academic how-to-use-our-data
  page (PUB-04). Six canonical sections (What we publish / How to use it /
  How to cite it / Provenance guarantees / Known caveats and divergences /
  Corrections and updates) matching CONTEXT D-27 verbatim. Copy-pasteable
  working snippets for pandas + DuckDB + R that fetch `manifest.json` and
  follow the URL fields to Parquet/CSV, plus a SHA-256 integrity check.
  BibTeX + APA citation templates referencing the versioned-snapshot URL
  pattern. Cross-links to `methodology/gas-counterfactual.md`,
  `about/corrections.md`, `CITATION.cff`, `CHANGES.md`, and
  `tests/test_benchmarks.py`. Closes PUB-04 + PUB-06 (external consumer
  can fetch manifest → follow URL → retrieve Parquet/CSV with provenance).
- `mkdocs.yml` Data nav tab (Plan 04-06) — top-level `Data: data/index.md`
  entry added to the 22-entry 5-theme tree, lifting the nav to 23 entries.
  `mkdocs build --strict` stays green (0 warnings, 0 errors).
- `docs/index.md` homepage link (Plan 04-06) — "For journalists and
  academics → [Use our data]" pointer to `docs/data/index.md`. Completes
  the navigation surface so academic readers land on the citation workflow
  without hunting through theme tabs.
- `.github/workflows/refresh.yml` (Plan 04-05) — daily 06:00 UTC cron
  automation. PR-based posture (D-16): scheme dirty-check
  (`refresh_all.py`) runs on a scheduled trigger; if any raw file's
  SHA-256 drifted, workflow regenerates Parquet + charts + manifest +
  rebuilds docs, then opens a PR on `refresh/<run_id>` via
  `peter-evans/create-pull-request@v8` with label `daily-refresh`.
  In-workflow test gates (benchmark floor, determinism, schema,
  aggregates, constants drift, manifest round-trip, CSV mirror) run
  BEFORE the PR is opened — catches issues upstream of the reviewer.
  On any step failure, `peter-evans/create-issue-from-file@v6` opens an
  Issue with label `refresh-failure` using the new
  `.github/refresh-failure-template.md` (distinct from the `correction`
  label — automation-breakage vs published-corrections are different
  concerns, D-17). Permissions least-privilege: `contents: write` +
  `pull-requests: write` + `issues: write`. Default `GITHUB_TOKEN`
  does not cascade to `ci.yml` on the refresh PR (Pitfall 2 — a GitHub
  security feature); reviewers dispatch ci.yml manually if they want a
  pre-merge test run. Adding `REFRESH_PAT` is a future Phase-4.1 option
  documented in the workflow file. Closes part of GOV-03.
- `.github/workflows/deploy.yml` (Plan 04-05) — on `git push --tags`
  matching `v*`, validates the calendar tag format `v<YYYY.MM>(-rc<N>)?`
  (D-14), assembles a self-contained versioned snapshot via
  `uk_subsidy_tracker.publish.snapshot` (PUB-03) and uploads the
  manifest + per-table parquet/csv/schema.json as release assets via
  `softprops/action-gh-release@v2`. Permissions are `contents: write`
  only. The `manifest.json::versioned_url` fields resolve to these
  release-asset URLs — academic citations are durable because GitHub
  releases are retention-guaranteed (D-13, D-14, GOV-06).
- `.github/refresh-failure-template.md` (Plan 04-05) — GitHub Issue
  body template referenced by `refresh.yml`'s fail-loud step; lists
  the four common failure modes (upstream schema drift, benchmark
  floor trip, mkdocs --strict breakage, determinism/schema gate
  failure) and the `refresh-failure` vs `correction` label distinction.
- `src/uk_subsidy_tracker/publish/` package (Plan 04-04) — the publishing
  layer that makes the project citable. Three module-level callables:
  - `publish/manifest.py` — Pydantic `Manifest` / `Dataset` / `Source`
    models; `build()` assembles `site/data/manifest.json` via
    `json.dumps(model.model_dump(mode="json"), sort_keys=True, indent=2)`
    (Pydantic v2 does NOT support `sort_keys` on `model_dump_json` — issue
    #7424). Shape is ARCHITECTURE §4.3 verbatim (D-07): top-level
    `version`, `generated_at`, `methodology_version` (read from
    `counterfactual.METHODOLOGY_VERSION`, D-12 chain), `pipeline_git_sha`
    (via `git rev-parse HEAD`, GOV-02), and `datasets[]`; each dataset
    carries `id`, `title`, `grain`, `row_count`, `schema_url`,
    `parquet_url`, `csv_url`, `versioned_url`, `sha256`, `sources[]`,
    `methodology_page`. URLs are absolute (D-09) — base comes from
    `SITE_URL` env var or `mkdocs.yml::site_url`; `upstream_url: str`
    (not `HttpUrl`, Pitfall 6) keeps serialisation stable across Pydantic
    minor versions. `generated_at` sources from
    `max(retrieved_at across sidecars)` not `datetime.now()` — byte-stable
    manifest when nothing upstream changes (Pitfall 3).
  - `publish/csv_mirror.py` — sibling CSV for every derived Parquet
    (PUB-02). Pinned pandas args per D-10: `index=False`, `encoding="utf-8"`
    (no BOM), `lineterminator="\n"` (LF even on Windows, Pitfall 4),
    `date_format="%Y-%m-%dT%H:%M:%S"` (ISO-8601 no sub-seconds),
    `float_format=None` (full precision), `na_rep=""`.
  - `publish/snapshot.py` — CLI (`--version`, `--output`, `--dry-run`)
    assembles a self-contained versioned-snapshot directory for
    `deploy.yml` to upload as release assets via
    `softprops/action-gh-release@v2` on `git push --tags` (D-13, D-14).
    Layout: `manifest.json` + `cfd/` with 5 parquet + 5 csv + 5 schema.json.
- `src/uk_subsidy_tracker/refresh_all.py` — CI entry point for
  `.github/workflows/refresh.yml` (D-16, D-18). Walks `SCHEMES` tuple,
  per-scheme: if `scheme.upstream_changed()` then
  `scheme.refresh() → rebuild_derived() → regenerate_charts() → validate()`.
  On any change: copies `data/derived/<scheme>/` to
  `site/data/latest/<scheme>/`, writes CSV mirrors, rebuilds
  `site/data/manifest.json`. On no change: short-circuits with exit 0
  and "no upstream changes; skipping manifest rebuild" — Pitfall 3
  avoids noisy daily empty PRs. CLI: `--version` (default `latest`).
- `tests/test_manifest.py` — 8/8 green. Round-trip byte-identity (guards
  against Pydantic serialisation drift), provenance-field presence
  (PUB-06 / GOV-02), absolute-URL (D-09), URL-type-is-str (Pitfall 6),
  sha256-matches-parquet (integrity), methodology-version-matches-constant
  (D-12), generated_at stability when nothing upstream changed (Pitfall 3).
- `tests/test_csv_mirror.py` — 7/7 green. Every-parquet-has-sibling-CSV,
  column order matches Parquet (D-10), LF line endings (Pitfall 4),
  no UTF-8 BOM, no pandas index leak, ISO-8601 dates, float precision
  survives round-trip at 1e-9 rel_tol.

- `src/uk_subsidy_tracker/schemas/` package — Pydantic row schemas for
  the five CfD derived grains (`StationMonthRow`, `AnnualSummaryRow`,
  `ByTechnologyRow`, `ByAllocationRoundRow`, `ForwardProjectionRow`).
  Field declaration order is the canonical Parquet column order (D-10).
  Every `Field` carries `description=` + `json_schema_extra={"dtype",
  "unit"}` so per-table `<grain>.schema.json` siblings carry dtype + unit
  metadata for Plan 04's `manifest.py`. `emit_schema_json(model, path)`
  helper writes byte-stable JSON (sort_keys + LF newlines) next to each
  Parquet file (D-11).
- `src/uk_subsidy_tracker/schemes/__init__.py` — `SchemeModule`
  `typing.Protocol` (runtime-checkable) declaring the ARCHITECTURE §6.1
  contract: `DERIVED_DIR` + five callables (`upstream_changed`,
  `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`). Phase
  5 (Renewables Obligation) and every subsequent scheme module copy
  this pattern; `isinstance(scheme_module, SchemeModule)` is the runtime
  conformance check.
- `src/uk_subsidy_tracker/schemes/cfd/` — first real implementation of
  §6.1 (D-01: load-bearing, not stubbed). `rebuild_derived()` emits the
  five CfD Parquet grains under `data/derived/cfd/` (or a caller-supplied
  `output_dir`) via the pinned pyarrow writer (`compression="snappy"`,
  `version="2.6"`, `use_dictionary=True`, `data_page_size=1 MiB` per
  D-22). Aggregation logic hoisted out of the chart files:
  `cost_model.py` from `plotting/subsidy/cfd_dynamics.py::_prepare`;
  `aggregation.py` from `cfd_payments_by_category.py` +
  `subsidy_per_avoided_co2_tonne.py`; `forward_projection.py` from
  `remaining_obligations.py:80-124`. Charts still work unchanged
  (D-02: chart files not rewritten in this plan).
- `tests/test_determinism.py` — TEST-05 satisfied. Parametrised
  content-equality via `pyarrow.Table.equals()` across all five grains;
  second parametrised test pins writer identity
  (`created_by.startswith("parquet-cpp-arrow")`). 10/10 green.
- Parquet-variant tests in `tests/test_schemas.py` (D-19) + `tests/test_aggregates.py`
  (D-20) — formalises TEST-02 and TEST-03 on derived Parquet output
  alongside the Phase-2 raw-CSV scaffolding. Full test suite: 54 passed
  + 4 skipped (+18 from Phase-4 Plan 03; zero regression).
- `.gitignore` — `data/derived/` excluded (regenerated on every rebuild).
- `.meta.json` sidecars for all five raw files (D-05):
  `{retrieved_at, upstream_url, sha256, http_status, publisher_last_modified, backfilled_at}`.
  `retrieved_at` best-effort from git log (falls back to the backfill
  date for the initial commit that creates the files at their new
  paths); `http_status` + `publisher_last_modified` are `null`
  (backfill markers); `backfilled_at: "2026-04-22"` flags reconstructed
  entries. These five sidecars feed the Phase-4 Plan 04 `manifest.json`
  provenance contract (GOV-02).
- `scripts/backfill_sidecars.py` — one-shot helper that (re-)computes
  SHA-256 + git-log `retrieved_at` for every `data/raw/<publisher>/<file>`
  entry. Retained after this plan as reusable tooling for future
  full re-scrapes.
- `pyarrow>=24.0.0` and `duckdb>=1.5.2` added to `pyproject.toml`
  dependencies (04-01 Wave 0). Phase 4 uses `pyarrow` for Parquet I/O
  in the derived layer + the `test_determinism.py` content-identity
  strip (D-21/D-22); `duckdb` is referenced in `docs/data/index.md`
  how-to-use-our-data snippets and declared in ARCHITECTURE §3 stack.
- `tests/fixtures/constants.yaml` — provenance blocks for the six
  tracked `src/uk_subsidy_tracker/counterfactual.py` constants
  (CCGT_EFFICIENCY, GAS_CO2_INTENSITY_THERMAL, DEFAULT_NON_FUEL_OPEX,
  DEFAULT_CARBON_PRICES_2021/2022/2023). SEED-001 Tier 2 scaffold.
- `tests/fixtures/__init__.py` — `ConstantProvenance`, `Constants`,
  `load_constants()` alongside existing `BenchmarkEntry` +
  `load_benchmarks()` (same two-layer Pydantic + YAML + parent-key
  injection pattern).
- `tests/test_constants_provenance.py` — drift tripwire: every live
  uppercase numeric constant on `counterfactual.py` listed in
  `_TRACKED` must have a YAML entry with exact-equality value. A
  non-failing `next_audit` overdue warning surfaces calendar due-dates
  in pytest output. Remediation-hook failure message cites
  `METHODOLOGY_VERSION` + `tests/fixtures/constants.yaml` +
  `CHANGES.md ## Methodology versions` (Phase-2 `test_counterfactual.py`
  template). Closes the SEED-001 gap that the Phase-2 `0.184` vs
  `0.18290` incident exposed.
- `tests/test_counterfactual.py` — pins the gas counterfactual formula
  against known inputs to 4 decimal places (TEST-01). Asserts
  `METHODOLOGY_VERSION` presence + DataFrame propagation.
- `tests/test_schemas.py` — pandera validation of raw CSV/XLSX sources
  via the existing loaders (pre-Parquet scaffolding; formal TEST-02 in
  Phase 4).
- `tests/test_aggregates.py` — row-conservation assertions on the
  LCCC CfD pipeline (pre-Parquet scaffolding; formal TEST-03 in Phase 4).
- `METHODOLOGY_VERSION` constant in `src/uk_subsidy_tracker/counterfactual.py`
  (GOV-04); `compute_counterfactual()` returns it as a DataFrame column.
- Pandera schemas `elexon_agws_schema`, `elexon_system_price_schema`,
  and `ons_gas_schema`; corresponding loaders now call `.validate()`.
- `tests/test_benchmarks.py` — reconciles CfD pipeline yearly totals
  against the mandatory LCCC self-reconciliation floor (0.1% red line
  per D-10) + regulator-native external anchors at named tolerances
  (TEST-04).
- `tests/fixtures/benchmarks.yaml` — structured benchmark values with
  per-entry source, year, URL, retrieval date, notes, and tolerance;
  Pydantic-validated loader at `tests/fixtures/__init__.py`.

### Changed
- `docs/about/citation.md` (Plan 04-06) — updated to document the
  versioned-snapshot URL pattern (GOV-06). Adds a "Citing a specific
  data snapshot" section with a BibTeX template anchored on
  `releases/tag/v<YYYY.MM>` — the durable academic citation target that
  survives repo renames and custom-domain migrations. Pattern: always
  tag-name; never `main` or `latest/`. Cross-links to
  `docs/data/index.md` for the full reader-side documentation.
- `tests/fixtures/benchmarks.yaml::lccc_self` (Plan 04-06 Task 3) —
  D-11 fallback re-confirmed per Disposition C. Phase 4 Plan 06
  re-examined the D-10 mandatory floor activation per CONTEXT D-26
  and kept the Phase-2 empty-list posture. YAML header extended with
  a 2026-04-22 audit note: the LCCC ARA 2024/25 PDF
  (https://www.lowcarboncontracts.uk/documents/293/LCCC_ARA_24-25_11.pdf)
  reports financial-year Apr 2024 – Mar 2025 without a quarterly
  breakdown that reconstructs calendar-year 2024 cleanly. A 0.1% floor
  tolerance against an FY-vs-CY mismatch (RESEARCH Pitfall 7) is
  strictly worse than no floor per Phase 2 D-10/D-11 — a wrong floor
  silently pins the pipeline to a misaligned reference. Follow-up
  remains open: populate when a future LCCC quarterly publication
  supplies a clean CY aggregate. `test_lccc_self_reconciliation_floor`
  continues to skip cleanly with a D-11-citing reason string. TEST-04
  stays satisfied (benchmark infrastructure lives; activation deferred).
- `.gitignore` (Plan 04-04) — replaced blanket `site/` ignore with explicit
  patterns for each mkdocs-build subtree (`/site/assets/`,
  `/site/stylesheets/`, `/site/search/`, `/site/themes/`,
  `/site/methodology/`, `/site/charts/`, `/site/about/`, `/site/index.html`,
  `/site/404.html`, sitemap files). Git cannot re-include paths under an
  ignored directory, so `!site/data/` cannot carve `site/data/` out of
  `site/`. The explicit list of mkdocs outputs leaves `site/data/latest/*`
  and `site/data/manifest.json` tracked — the Phase-4 publishing-layer
  subtree the daily refresh workflow commits (D-15). Verified: `mkdocs
  build --strict` output paths are all still ignored; publishing-layer
  files under `site/data/` are not.
- `methodology_version` column added to every derived Parquet row
  (GOV-02 provenance-per-row). Propagates from
  `src/uk_subsidy_tracker/counterfactual.py::METHODOLOGY_VERSION = "0.1.0"`
  (unchanged; bump is Phase 6+ at first public release). Plan 04-04's
  `manifest.json` reads it from the derived schema sidecars; a disputed
  figure can be traced to the methodology revision that produced it
  (TEST-02/03/05 formally satisfied on derived output).
- **Raw data layout migrated** from flat `data/*.csv` / `data/*.xlsx`
  to the canonical `data/raw/<publisher>/<file>` nested structure per
  ARCHITECTURE §4.1 (D-04). Filenames hyphenated (underscores → hyphens).
  Five files renamed atomically via `git mv` (100% rename similarity —
  `git log --follow` resolves pre-rename history):
  - `data/lccc-actual-cfd-generation.csv` → `data/raw/lccc/actual-cfd-generation.csv`
  - `data/lccc-cfd-contract-portfolio-status.csv` → `data/raw/lccc/cfd-contract-portfolio-status.csv`
  - `data/elexon_agws.csv` → `data/raw/elexon/agws.csv`
  - `data/elexon_system_prices.csv` → `data/raw/elexon/system-prices.csv`
  - `data/ons_gas_sap.xlsx` → `data/raw/ons/gas-sap.xlsx`
- Loaders updated in the same commit (D-06):
  `src/uk_subsidy_tracker/data/elexon.py` (`AGWS_FILE`, `SYSTEM_PRICE_FILE`),
  `src/uk_subsidy_tracker/data/ons_gas.py` (`GAS_SAP_DATA_FILENAME`),
  and `src/uk_subsidy_tracker/data/lccc_datasets.yaml` (both `filename:`
  fields). CI stayed green across the rename commit
  (36 passed + 4 skipped, zero regressions) and `uv run python
  -m uk_subsidy_tracker.plotting` + `uv run mkdocs build --strict`
  both green.
- Phase 2 scope correction (CONTEXT D-04): formal `TEST-02`, `TEST-03`,
  `TEST-05` requirement IDs reassigned from Phase 2 to Phase 4.
  Phase 2 still ships pre-Parquet scaffolding variants of
  `tests/test_schemas.py` and `tests/test_aggregates.py` (today), plus
  CI, pin test, and methodology versioning (TEST-01, TEST-04, TEST-06,
  GOV-04). Phase 4 will add the Parquet-schema + Parquet-aggregate
  variants + `tests/test_determinism.py` to satisfy the three formal
  requirements. `.planning/ROADMAP.md` and `.planning/REQUIREMENTS.md`
  updated.
- Phase 2 ROADMAP success criterion 1 reworded from "all five test classes" to "four test classes present and passing: `test_counterfactual.py`, `test_schemas.py`, `test_aggregates.py`, `test_benchmarks.py`" to reflect D-03 deferring `test_determinism.py` to Phase 4 (per Phase 2 CONTEXT D-04).
- Phase 2 ROADMAP success criterion 3 re-anchored from "Ben Pile (2021 + 2026), REF subset, and Turver aggregate" to "LCCC self-reconciliation and any regulator-native external sources the researcher located (OBR, Ofgem, DESNZ, HoC Library, NAO)" (per Phase 2 CONTEXT D-11).
- `ARCHITECTURE.md` §11 P1 deliverables block updated to match the
  above (per user memory: when ARCHITECTURE.md and ROADMAP disagree,
  the spec wins; the spec was amended first, ROADMAP + REQUIREMENTS
  then aligned to it).

## [0.1.0] — 2026-04-21

First tagged pre-release of the UK Renewable Subsidy Tracker, renamed
from the `cfd-payment` single-scheme prototype. Establishes the
publishable baseline for scheme expansion (P1 onward).

### Added
- `ARCHITECTURE.md` at repo root — single source of truth design document.
- `RO-MODULE-SPEC.md` at repo root — per-scheme module template.
- `CHANGES.md` — this file.
- `CITATION.cff` — machine-readable academic citation metadata (CFF 1.2.0).
- `README.md` — repo overview with clone + reproduce block.
- `docs/about/corrections.md` — public corrections mechanism (GOV-05).
- `docs/about/citation.md` — citation stub pointing at root `CITATION.cff`.

### Changed
- Python package renamed from `cfd_payment` to `uk_subsidy_tracker`
  (`src/cfd_payment/` → `src/uk_subsidy_tracker/` via `git mv`).
- `pyproject.toml` project name changed from `cfd-payment` to `uk-subsidy-tracker`;
  wheel packages path updated.
- Bumped Python floor from 3.11 to 3.12 to match project constraint
  (`pyproject.toml` `requires-python = ">=3.12"`; `uv.lock` regenerated;
  `CLAUDE.md` Runtime section aligned with Constraints "Python 3.12+ only").
- All 24 Python source files, 2 test files, and `demo_dark_theme.py`
  rewritten from `from cfd_payment` to `from uk_subsidy_tracker`.
- MkDocs theme changed from `readthedocs` to `material` with opinionated
  baseline config (navigation.tabs, navigation.sections, toc.follow,
  search.suggest, search.highlight, content.code.copy) and light/dark
  palette toggle.
- `mkdocs.yml` site identity updated: `site_name`, `site_url`, `repo_url`,
  `repo_name`, `extra.social.link` all point at `uk-subsidy-tracker`.
- `docs/technical-details/gas-counterfactual.md` moved to
  `docs/methodology/gas-counterfactual.md`; inbound references in
  `docs/index.md`, `docs/charts/index.md`, and the three chart pages
  (`cfd-dynamics.md`, `cfd-vs-gas-cost.md`, `remaining-obligations.md`)
  updated.
- Fixed two stale GitHub URL bugs where `richlyon/cfd-payment` should
  have been `richardjlyon/uk-subsidy-tracker` — one at
  `methodology/gas-counterfactual.md:108` and one at
  `charts/subsidy/cfd-vs-gas-cost.md` lines 162/163.

### Removed
- `docs/technical-details/` directory (all contents either moved to
  `docs/methodology/` or previously deleted).

## Methodology versions

<!--
GOV-04 hook: the gas counterfactual formula in
src/uk_subsidy_tracker/counterfactual.py carries a methodology_version
constant starting in Phase 2 (test scaffolding). Changes to that constant
are logged in this section with rationale and the affected chart list.
-->

### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)

- Formula: `counterfactual_total = gas_fuel_cost + carbon_cost + plant_opex` (all £/MWh).
- Constants pinned: `CCGT_EFFICIENCY = 0.55`; `GAS_CO2_INTENSITY_THERMAL = 0.184`
  tCO2/MWh_thermal; `DEFAULT_NON_FUEL_OPEX = 5.0` £/MWh; annual
  `DEFAULT_CARBON_PRICES` 2018–2026 (EU ETS 2018–2020, UK ETS 2021+).
- Sources: BEIS Electricity Generation Costs 2023 Table ES.1 (CCGT O&M);
  GOV.UK UK ETS published prices (carbon).
- Pinned in `tests/test_counterfactual.py` at 4 decimal places; any change to
  these constants fails the pin test and requires a CHANGES.md entry here.
