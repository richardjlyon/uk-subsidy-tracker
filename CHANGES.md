# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Phase 5 — Renewables Obligation Module

- **Ofgem RO scrapers + raw seed** (Plan 05-01). `src/uk_subsidy_tracker/data/ofgem_ro.py`
  + `src/uk_subsidy_tracker/data/roc_prices.py` with Phase 4 D-17 error-path
  discipline (`output_path` bound BEFORE `try`, `timeout=60` on `requests.get()`,
  bare `raise` in `except`). Three header-only Option-D stub raw files seeded under
  `data/raw/ofgem/{ro-register.csv, ro-generation.csv, roc-prices.csv}` with sibling
  `.meta.json` sidecars written via the shared `sidecar.write_sidecar()` helper.
  Each scraper raises `RuntimeError("manual refresh — see INVESTIGATION.md ...")`
  when its URL constant is empty so accidental cron firings fail-loud rather than
  silently overwriting committed seeds. RER-access investigation report at
  `.planning/phases/05-ro-module/05-01-TASK-1-INVESTIGATION.md` documents 6
  follow-up items routed to Plan 05-13 post-execution review (real RER plumbing,
  PDF transcription, Playwright-OIDC Option-B/C decisions). Closes **RO-01**.
- **RO bandings table** (Plan 05-02). `src/uk_subsidy_tracker/data/ro_bandings.yaml`
  transcribes REF "Notes on the Renewable Obligation" Table 1 into 85
  (technology × commissioning-window × country) cells: 69 GB banded entries
  across 5 commissioning windows (pre-2013, 2013/14, 2014/15, 2015/16,
  2016/17) + 12 NIROC `[ASSUMED]` entries + 4 grandfathered (pre-2006-07-11
  1 ROC/MWh) entries. Every row carries a full `Provenance:` block (source
  SI + URL + basis + retrieved_on); NIROC entries flag `[ASSUMED]` in `basis:`
  for grep-discoverability (verification routed to Plan 05-13 follow-up).
  `src/uk_subsidy_tracker/data/ro_bandings.py` (138 lines) two-layer Pydantic
  loader (`RoBandingEntry` + `RoBandingTable` + `load_ro_bandings()`) mirroring
  `LCCCDatasetConfig` + `LCCCAppConfig` from Phase 2 D-07.
  `RoBandingTable.lookup(technology, country, commissioning_date, chp=False)`
  resolves the four dimensions with an explicit pre-2006-07-11 grandfathering
  short-circuit; banded-rate scan `continue`s past `grandfathered=true` rows
  so YAML ordering cannot change behaviour. `data/__init__.py` re-exports the
  loader so Plan 05-05 `schemes/ro/cost_model.py` imports directly from
  `uk_subsidy_tracker.data`. Used as the **audit cross-check** for Ofgem-published
  ROCs_Issued per CONTEXT D-01. (Foundation for **RO-02**.)
- **RO Pydantic row schemas** (Plan 05-03). `src/uk_subsidy_tracker/schemas/ro.py`
  exports 5 BaseModel subclasses (`RoStationMonthRow` 17 fields,
  `RoAnnualSummaryRow` 9, `RoByTechnologyRow` 6, `RoByAllocationRoundRow` 6,
  `RoForwardProjectionRow` 7) mirroring `schemas/cfd.py` shape verbatim. Field
  declaration order IS Parquet column order on every grain (D-10).
  `emit_schema_json` imported from `schemas.cfd` (cross-scheme shared, T-5.03-02
  mitigation; no redeclaration). `schemas/__init__.py` barrel re-exports the 5
  RO row models alongside the CfD models. (Foundation for **RO-03**.)
- **`schemes/ro/` module** (Plan 05-05). Full ARCHITECTURE §6.1 conformance
  (D-01: load-bearing, not stubbed). 5 contract callables (`upstream_changed`,
  `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`) + `DERIVED_DIR`.
  Internal modules: `_refresh.py` (3-downloader wiring + 3 sidecars via shared
  `sidecar.write_sidecar()`; `_URL_MAP` byte-matches `scripts/backfill_sidecars.py::URL_MAP`
  on all 3 Ofgem keys); `cost_model.py` (11-step `build_station_month` pipeline:
  3-way join + dual cost columns per D-02 + bandings cross-check per D-01 +
  counterfactual integration via `_annual_counterfactual_gbp_per_mwh()` helper +
  mutualisation delta per D-11); `aggregation.py` (3 rollup builders re-reading
  `station_month.parquet` per D-03; int64 year cast per Phase 4 Rule-1 fix);
  `forward_projection.py` (per-station accreditation-end anchor per RESEARCH §6
  Option (c); deterministic current-year anchor; 2037 scheme-close cap).
  `_write_parquet` imported from `schemes.cfd.cost_model` (shared deterministic
  writer; intentional cross-scheme coupling per PATTERNS.md). Empty-input
  short-circuits in all 3 builders produce canonical-shape empty Parquets
  (every expected column present with correct dtype) so downstream tests +
  schemas hold even on Plan 05-01 Option-D stub flow-through. `isinstance(ro,
  SchemeModule)` returns True — second §6.1-conformant scheme after CfD.
  Closes **RO-02** and **RO-03**.
- **4 RO charts** (Plan 05-08). `plotting/subsidy/ro_dynamics.py` (S2 4-panel:
  generation TWh / ROC £/ROC with e-ROC sensitivity overlay / premium £/MWh /
  cumulative £bn with per-year mutualisation annotation driven by
  `mutualisation_gbp > 0` — D-11 verified scope SY 2021-22 only).
  `plotting/subsidy/ro_by_technology.py` (S3 stacked area with cofiring-vs-dedicated
  biomass split per D-10; 6 categories — Offshore #1f77b4 / Onshore #6baed6 /
  Biomass dedicated #8c564b / Biomass cofiring #d62728 / Solar PV #ff7f0e /
  Other #2ca02c). `plotting/subsidy/ro_concentration.py` (S4 Lorenz on
  station-level lifetime `ro_cost_gbp`, GB-only per D-09/D-12 with 50% + 80%
  threshold markers + top-3 station_id callouts).
  `plotting/subsidy/ro_forward_projection.py` (S5 2-panel drawdown to 2037 —
  no NESO-growth scenario since RO closed to new accreditations per SI 2017/1084).
  Filenames match RO-MODULE-SPEC Appendix A verbatim;
  `subsidy_ro_dynamics_twitter.png` + 3 siblings. Empty-upstream graceful-degradation:
  each chart's `_prepare()` returns empty DataFrame when `data/derived/ro/*.parquet`
  is absent/empty, and `main()` short-circuits to `_placeholder()` emitting a
  titled single-panel annotation figure — `uv run python -m uk_subsidy_tracker.plotting`
  succeeds end-to-end (18 charts OK; 0 ERR) even with the committed Plan 05-01
  Option-D stub seeds. GB-only + NIRO-via-filter annotation landed on every
  RO chart (T-5.08-02 mitigation). Closes **RO-04**.
- **REF Constable benchmark anchor + reconciliation test** (Plan 05-09).
  `tests/fixtures/benchmarks.yaml::ref_constable` section transcribes REF
  Constable 2025-05-01 Table 1 verbatim (22 entries SY 2002-03 through 2023-24,
  each carrying `tolerance_pct: 3.0` + REF PDF URL + `retrieved_on: 2026-04-22`
  + per-year SY notes flagging ROADMAP SC #3 window anchors, the D-11
  mutualisation year, and the series end). YAML header declares D-13/D-14
  posture (REF = primary anchor, 3.0% = HARD BLOCK), REF basis (SY April–March,
  £bn nominal, GB-only, includes cofiring + mutualisation, excludes NIRO),
  and scope alignment with pipeline D-12 headline + CY-vs-SY tolerance
  alignment note + Turver SY21 ~6% delta explanation. `tests/fixtures/__init__.py`
  grows `Benchmarks.ref_constable: list[BenchmarkEntry]` + relaxes
  `BenchmarkEntry.year` lower bound from `ge=2015` to `ge=2002` (admits RO
  2002-start). `all_external_entries()` deliberately excludes `ref_constable`
  (REF has dedicated hard-block test, not D-11 fallback dispatch).
  `tests/test_benchmarks.py` grows `REF_TOLERANCE_PCT = 3.0` module constant
  (D-14 docstring with 3-step diagnostic ladder: REF scope / banding /
  carbon-price extension) + `_TOLERANCE_BY_SOURCE["ref_constable"]` dispatch
  + `ro_annual_totals_gbp_bn` module-scoped fixture + `_DIVERGENCE_SENTINEL`
  constant + `test_ref_constable_ro_reconciliation` parametrised test (22 REF
  years; D-14 hard block at ±3% with `pytest.xfail(strict=False)` activated
  when `.planning/phases/05-ro-module/05-09-DIVERGENCE.md` exists).
  `.planning/phases/05-ro-module/05-09-DIVERGENCE.md` sentinel authored:
  Plan 05-01 Option-D fallback state means `ro-register.csv` absent +
  `ro-generation.csv` is 72-byte header-only stub + `station_month.parquet`
  emits zero rows → divergence class is data-absence (NOT methodological);
  Plan 05-13 reviewer skips the D-14 methodological ladder and goes straight
  to Ofgem RER plumbing as the resolution path. Closes **RO-06**
  (sentinel-gated; re-arms once Plan 05-13 lands non-stub Ofgem data).
- **RO test parametrisations on quality gates** (Plan 05-10). `tests/test_schemas.py`
  gains `ro_derived_dir` module-scoped fixture + `_RO_GRAIN_MODELS` dict + 5
  parametrised `test_ro_parquet_grain_schema` cases (5 grains × Pydantic row
  models; column-order discipline D-10 enforced unconditionally even on empty
  Parquets; per-row Pydantic validation skips on zero-row stub data).
  `tests/test_aggregates.py` gains 4 module-scoped RO fixtures + 3 RO
  row-conservation tests (annual via D-09 year+country groupby; by_technology
  via year+technology; by_allocation_round via year+commissioning_window — RO
  has no allocation-round axis) + `_skip_if_empty_ro_station_month()` D-11
  fallback helper. `tests/test_determinism.py` gains independent `ro_derived_once`
  + `ro_derived_twice` fixtures + `RO_GRAINS` tuple + 10 parametrised cases (5
  content-equality via `pyarrow.Table.equals` + 5 writer-identity via
  `parquet-cpp-arrow` prefix check). Per PATTERNS.md directive: CfD + RO use
  INDEPENDENT module-scoped fixtures and remain SEPARATE parametrisations —
  no merging.
- **RO refresh-loop invariant tests** (Plan 05-07). `tests/test_refresh_loop.py`
  grows from 2 tests (CfD only) to 4 via the `importlib.import_module()`
  submodule-shadow bypass established in Plan 04-07:
  `test_ro_refresh_converges_on_unchanged_upstream` pins the D-18 per-scheme
  invariant for RO (after `ro_refresh.refresh()` rewrites sidecars,
  `upstream_changed()` returns False) — passes on first commit because the
  invariant is already established by `schemes/ro/_refresh.py::refresh()`
  shipped in Plan 05-05; `test_manifest_includes_both_schemes_after_end_to_end_refresh`
  pins the plan's core truth (10 Dataset entries = 5 CfD + 5 RO) by
  synthesising a tmp derived + raw tree covering both schemes and calling
  `manifest.build()` directly.
- **RO scheme-detail page + Schemes nav tab** (Plan 05-11). `docs/schemes/ro.md`
  (251 lines, 9 H2 sections) follows CONTEXT D-15 8-section structure verbatim:
  Headline / What is the RO / Cost dynamics (S2) / By technology (S3) /
  Concentration (S4) / Forward commitment (S5) / Methodology / Data & code
  + FAQ + See-also subsections. Adversarial-payload headline lands verbatim
  in opening 3 lines: "The scheme you've never heard of, twice the size of
  the one you have — £67 bn in RO subsidy paid by UK consumers since 2002."
  D-12 breakdown paragraph documents biomass / mutualisation / NIRO scope.
  All 4 RO chart embeds wired with PNG + interactive HTML link. GOV-01
  four-way coverage manifest at page bottom: REF Constable 2025 PDF URL +
  Ofgem RER + 4 chart-source permalinks + 3 pipeline-source permalinks
  (`schemes/ro/` + `ofgem_ro.py` + `ro_bandings.yaml`) + REF reconciliation
  test permalink + reproduce-from-`git clone` bash block. `docs/schemes/index.md`
  (23 lines) is the Schemes-section landing page with How-to-read explainer
  + currently-published vs coming-soon list. `mkdocs.yml`: Schemes nav tab
  inserted between Reliability and Data per RESEARCH §8.2 (Overview entry +
  RO entry). Theme-page cross-links: 2 RO grid-cards in
  `docs/themes/cost/index.md` (S2 dynamics + S3 by-technology), 1 RO grid-card
  in `docs/themes/recipients/index.md` (S4 concentration). `docs/index.md`:
  new "Scheme detail pages" section above For-journalists block surfacing
  the £67 bn RO headline. `.gitignore` extended with `/site/schemes/`.
  Closes **RO-05**.

#### Phase 4 — Publishing Layer (carry-over from prior wave)

- `src/uk_subsidy_tracker/data/sidecar.py` (Plan 04-07) — shared
  `write_sidecar()` helper for `.meta.json` atomicity. Used by both the
  daily refresh path (`schemes/cfd/_refresh.py::refresh()`) and the
  one-shot `scripts/backfill_sidecars.py`. Serialisation is byte-identical
  across both call sites (sort_keys=True, indent=2, trailing newline);
  writes go via `<path>.meta.json.tmp` + `os.replace` so sidecars are
  never partial on crash. Closes gap #1 from 04-VERIFICATION.md.
- `tests/test_refresh_loop.py` (Plan 04-07) — invariant test locking the
  refresh-loop algebraic property: after `scheme.refresh()` rewrites
  sidecars, `upstream_changed()` returns False on the next call, and
  `manifest.generated_at` advances once then stays stable on unchanged
  second runs. Uses `monkeypatch` + `tmp_path` + mocked downloaders; does
  not hit network.
- `tests/test_ons_gas_download.py` (Plan 04-07) — regression test for the
  `ons_gas.download_dataset()` error-path (3 tests: raises on network
  failure, uses timeout=60, returns path on success).
- `docs/data/index.md` (Plan 04-06) — journalist/academic how-to-use-our-data
  page (PUB-04). Six canonical sections (What we publish / How to use it /
  How to cite it / Provenance guarantees / Known caveats and divergences /
  Corrections and updates) matching CONTEXT D-27 verbatim. Copy-pasteable
  working snippets for pandas + DuckDB + R that fetch `manifest.json` and
  follow the URL fields to Parquet/CSV, plus a SHA-256 integrity check.
  BibTeX + APA citation templates referencing the versioned-snapshot URL
  pattern. Cross-links to `methodology/gas-counterfactual.md`,
  `about/corrections.md`, `CITATION.cff`, `CHANGES.md`, and
  `tests/test_benchmarks.py`. Closes PUB-04 + PUB-06.
- `mkdocs.yml` Data nav tab (Plan 04-06) — top-level `Data: data/index.md`
  entry added to the 22-entry 5-theme tree, lifting the nav to 23 entries.
- `docs/index.md` homepage link (Plan 04-06) — "For journalists and
  academics → [Use our data]" pointer to `docs/data/index.md`.
- `.github/workflows/refresh.yml` (Plan 04-05) — daily 06:00 UTC cron
  automation. PR-based posture (D-16): scheme dirty-check
  (`refresh_all.py`) runs on a scheduled trigger; if any raw file's
  SHA-256 drifted, workflow regenerates Parquet + charts + manifest +
  rebuilds docs, then opens a PR on `refresh/<run_id>` via
  `peter-evans/create-pull-request@v8` with label `daily-refresh`.
  In-workflow test gates run BEFORE the PR is opened. On any step failure,
  `peter-evans/create-issue-from-file@v6` opens an Issue with label
  `refresh-failure` using the new `.github/refresh-failure-template.md`.
  Permissions least-privilege: `contents: write` + `pull-requests: write`
  + `issues: write`. Closes part of GOV-03.
- `.github/workflows/deploy.yml` (Plan 04-05) — on `git push --tags`
  matching `v*`, validates the calendar tag format `v<YYYY.MM>(-rc<N>)?`
  (D-14), assembles a self-contained versioned snapshot via
  `uk_subsidy_tracker.publish.snapshot` (PUB-03) and uploads the
  manifest + per-table parquet/csv/schema.json as release assets via
  `softprops/action-gh-release@v2`. Permissions are `contents: write` only.
  The `manifest.json::versioned_url` fields resolve to these release-asset
  URLs — academic citations are durable because GitHub releases are
  retention-guaranteed (D-13, D-14, GOV-06).
- `.github/refresh-failure-template.md` (Plan 04-05) — GitHub Issue body
  template referenced by `refresh.yml`'s fail-loud step.
- `src/uk_subsidy_tracker/publish/` package (Plan 04-04) — the publishing
  layer that makes the project citable. Three module-level callables:
  - `publish/manifest.py` — Pydantic `Manifest` / `Dataset` / `Source`
    models; `build()` assembles `site/data/manifest.json` via
    `json.dumps(model.model_dump(mode="json"), sort_keys=True, indent=2)`.
    Shape is ARCHITECTURE §4.3 verbatim (D-07): top-level `version`,
    `generated_at`, `methodology_version` (read from
    `counterfactual.METHODOLOGY_VERSION`, D-12 chain), `pipeline_git_sha`,
    and `datasets[]`. URLs are absolute (D-09); `upstream_url: str`
    (not `HttpUrl`, Pitfall 6); `generated_at` sources from
    `max(retrieved_at across sidecars)` not `datetime.now()` (Pitfall 3).
  - `publish/csv_mirror.py` — sibling CSV for every derived Parquet
    (PUB-02). Pinned pandas args per D-10 (`index=False`,
    `encoding="utf-8"`, `lineterminator="\n"`,
    `date_format="%Y-%m-%dT%H:%M:%S"`, `float_format=None`, `na_rep=""`).
  - `publish/snapshot.py` — CLI (`--version`, `--output`, `--dry-run`)
    assembles a self-contained versioned-snapshot directory for
    `deploy.yml` to upload as release assets via
    `softprops/action-gh-release@v2` on `git push --tags` (D-13, D-14).
- `src/uk_subsidy_tracker/refresh_all.py` — CI entry point for
  `.github/workflows/refresh.yml` (D-16, D-18). Walks `SCHEMES` tuple,
  per-scheme: if `scheme.upstream_changed()` then
  `scheme.refresh() → rebuild_derived() → regenerate_charts() → validate()`.
- `tests/test_manifest.py` — 8/8 green (round-trip byte-identity,
  provenance-field presence, absolute-URL D-09, URL-type-is-str Pitfall 6,
  sha256-matches-parquet, methodology-version-matches-constant D-12,
  `generated_at` stability Pitfall 3).
- `tests/test_csv_mirror.py` — 7/7 green (sibling presence, column order
  matches Parquet D-10, LF line endings Pitfall 4, no UTF-8 BOM, no
  pandas index leak, ISO-8601 dates, float precision at 1e-9 rel_tol).
- `src/uk_subsidy_tracker/schemas/` package — Pydantic row schemas for
  the five CfD derived grains (`StationMonthRow`, `AnnualSummaryRow`,
  `ByTechnologyRow`, `ByAllocationRoundRow`, `ForwardProjectionRow`).
  Field declaration order is the canonical Parquet column order (D-10).
  Every `Field` carries `description=` + `json_schema_extra={"dtype",
  "unit"}` so per-table `<grain>.schema.json` siblings carry dtype + unit
  metadata. `emit_schema_json(model, path)` helper writes byte-stable JSON
  (sort_keys + LF newlines) next to each Parquet file (D-11).
- `src/uk_subsidy_tracker/schemes/__init__.py` — `SchemeModule`
  `typing.Protocol` (runtime-checkable) declaring the ARCHITECTURE §6.1
  contract: `DERIVED_DIR` + five callables (`upstream_changed`, `refresh`,
  `rebuild_derived`, `regenerate_charts`, `validate`). Phase 5 (RO) and
  every subsequent scheme module copy this pattern;
  `isinstance(scheme_module, SchemeModule)` is the runtime conformance check.
- `src/uk_subsidy_tracker/schemes/cfd/` — first real implementation of
  §6.1 (D-01: load-bearing, not stubbed). `rebuild_derived()` emits the
  five CfD Parquet grains under `data/derived/cfd/` via the pinned pyarrow
  writer (`compression="snappy"`, `version="2.6"`, `use_dictionary=True`,
  `data_page_size=1 MiB` per D-22). Aggregation logic hoisted out of the
  chart files (D-02: chart files not rewritten in this plan).
- `tests/test_determinism.py` — TEST-05 satisfied. Parametrised
  content-equality via `pyarrow.Table.equals()` across all five CfD grains;
  second parametrised test pins writer identity. 10/10 green.
- Parquet-variant tests in `tests/test_schemas.py` (D-19) +
  `tests/test_aggregates.py` (D-20) — formalises TEST-02 and TEST-03 on
  derived Parquet output alongside the Phase-2 raw-CSV scaffolding.
- `.gitignore` — `data/derived/` excluded (regenerated on every rebuild).
- `.meta.json` sidecars for all five raw files (D-05):
  `{retrieved_at, upstream_url, sha256, http_status,
  publisher_last_modified, backfilled_at}`.
- `scripts/backfill_sidecars.py` — one-shot helper that (re-)computes
  SHA-256 + git-log `retrieved_at` for every `data/raw/<publisher>/<file>`
  entry. Retained as reusable tooling.
- `pyarrow>=24.0.0` and `duckdb>=1.5.2` added to `pyproject.toml`
  dependencies (04-01 Wave 0).
- `tests/fixtures/constants.yaml` — provenance blocks for the tracked
  `counterfactual.py` constants. SEED-001 Tier 2 scaffold.
- `tests/fixtures/__init__.py` — `ConstantProvenance`, `Constants`,
  `load_constants()` alongside existing `BenchmarkEntry` +
  `load_benchmarks()`.
- `tests/test_constants_provenance.py` — drift tripwire: every live
  uppercase numeric constant on `counterfactual.py` listed in
  `_TRACKED` must have a YAML entry with exact-equality value.
- `tests/test_counterfactual.py` — pins the gas counterfactual formula
  against known inputs to 4 decimal places (TEST-01). Asserts
  `METHODOLOGY_VERSION` presence + DataFrame propagation.
- `tests/test_schemas.py` — pandera validation of raw CSV/XLSX sources
  via the existing loaders (pre-Parquet scaffolding).
- `tests/test_aggregates.py` — row-conservation assertions on the
  LCCC CfD pipeline (pre-Parquet scaffolding).
- `METHODOLOGY_VERSION` constant in
  `src/uk_subsidy_tracker/counterfactual.py` (GOV-04);
  `compute_counterfactual()` returns it as a DataFrame column.
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

#### Phase 5 — Renewables Obligation Module

- **`counterfactual.DEFAULT_CARBON_PRICES` extended backward to 2002**
  (Plan 05-04; D-05/D-06). Years 2002-2004 = 0.0 (pre-EU-ETS Phase I
  start 2005-01-01); years 2005-2017 = EU ETS annual averages
  (Phase I 2005-2007 / Phase II 2008-2012 / Phase III 2013-2017),
  EUR→GBP at BoE contemporary annual-average rates (EEA + ICE/EEX
  reference). Existing 2018-2026 values unchanged (additive per D-06).
  Enables RO scheme counterfactual computation for pre-2018 obligation
  years — RO launched 2002-04-01 so the full 2002-present span is
  required. 2005-2017 values carry `[VERIFICATION-PENDING]` inline flag
  pending audit against primary EEA + BoE sources before next_audit
  (2027-01-15). Per D-06 `METHODOLOGY_VERSION` stays `"0.1.0"` —
  additive change (new year keys only; no existing values revised; no
  formula-shape change). Bump to 1.0.0 reserved for Phase 6+ portal launch.
- **`tests/fixtures/constants.yaml` extended with 22 new entries** (Plan 05-04).
  16 new 2002-2017 `DEFAULT_CARBON_PRICES_YYYY` blocks matching the live
  dict extension, plus 6 completion blocks for pre-existing but untracked
  year keys (2018, 2019, 2020, 2024, 2025, 2026) that close the Phase 4
  SEED-001 Tier 2 partial-coverage gap. `_TRACKED` set in
  `tests/test_constants_provenance.py` grows from 6 entries (3 base + 3
  carbon years) to 28 entries (3 base + 25 carbon years 2002-2026).
  Drift tripwire now covers every live `DEFAULT_CARBON_PRICES` year key
  — any silent edit to the dict fails the drift test with a remediation
  message citing METHODOLOGY_VERSION + constants.yaml + CHANGES.md.
- **`publish/manifest.py` scheme-parametric refactor** (Plan 05-06; D-07).
  `manifest.build()` signature changed from `(derived_dir, raw_dir, ...)`
  to `(schemes, derived_root, raw_dir, ...)` — iterates a `schemes`
  iterable instead of hard-coding `"cfd."` prefixes and `"cfd/"` path
  segments. `refresh_all.publish_latest()` passes `SCHEMES` tuple +
  `DERIVED_ROOT` (parent of per-scheme derived dirs). URL pattern
  preserved verbatim (`/data/latest/<scheme>/<grain>.parquet`); all 8
  pre-existing `test_manifest.py` CfD parity tests remain green. Phase 7
  (FiT) + later schemes auto-publish with zero `manifest.py` changes.
  `GRAIN_SOURCES` / `GRAIN_TITLES` / `GRAIN_DESCRIPTIONS` become nested
  dicts keyed by scheme × grain.
- **`refresh_all.SCHEMES` registered RO** (Plan 05-07). One-line append
  (`(("cfd", cfd), ("ro", ro))`) + one-line import extension; D-18
  per-scheme dirty-check auto-activates. Smoke-verified: both schemes
  short-circuit `upstream unchanged` on committed seed state in 0.49s.
  `publish/manifest.py::GRAIN_SOURCES` / `GRAIN_TITLES` /
  `GRAIN_DESCRIPTIONS` populated with full `"ro"` sub-dicts (51 lines
  added) — Rule 2 auto-fix because Plan 05-06 refactored the iterator
  to be scheme-parametric but left the provenance dicts CfD-only;
  without these, the multi-scheme iterator silently produced a CfD-only
  manifest.json (5 Datasets) instead of the 10 Datasets the plan's
  must_have truth pins.

#### Phase 4 — Publishing Layer (carry-over from prior wave)

- `scripts/backfill_sidecars.py` (Plan 04-07) — refactored to delegate
  SHA computation + atomic JSON write to `write_sidecar()`, then overlay
  the two backfill-specific fields (`retrieved_at` from `git log
  --follow`, `backfilled_at` marker). Output bytes unchanged on all
  common keys.
- `docs/about/citation.md` (Plan 04-06) — updated to document the
  versioned-snapshot URL pattern (GOV-06). Adds a "Citing a specific
  data snapshot" section with a BibTeX template anchored on
  `releases/tag/v<YYYY.MM>` — the durable academic citation target.
- `tests/fixtures/benchmarks.yaml::lccc_self` (Plan 04-06 Task 3) —
  D-11 fallback re-confirmed per Disposition C. Phase 4 Plan 06
  re-examined the D-10 mandatory floor activation per CONTEXT D-26
  and kept the Phase-2 empty-list posture. YAML header extended with
  a 2026-04-22 audit note: the LCCC ARA 2024/25 PDF reports
  financial-year Apr 2024 – Mar 2025 without a quarterly breakdown that
  reconstructs calendar-year 2024 cleanly. A 0.1% floor tolerance against
  an FY-vs-CY mismatch (RESEARCH Pitfall 7) is strictly worse than no
  floor per Phase 2 D-10/D-11. `test_lccc_self_reconciliation_floor`
  continues to skip cleanly with a D-11-citing reason string. TEST-04
  stays satisfied (benchmark infrastructure lives; activation deferred).
- `.gitignore` (Plan 04-04) — replaced blanket `site/` ignore with
  explicit patterns for each mkdocs-build subtree. Git cannot re-include
  paths under an ignored directory, so `!site/data/` cannot carve
  `site/data/` out of `site/`. The explicit list of mkdocs outputs leaves
  `site/data/latest/*` and `site/data/manifest.json` tracked — the
  Phase-4 publishing-layer subtree the daily refresh workflow commits.
- `methodology_version` column added to every derived Parquet row
  (GOV-02 provenance-per-row). Propagates from
  `src/uk_subsidy_tracker/counterfactual.py::METHODOLOGY_VERSION = "0.1.0"`.
- **Raw data layout migrated** from flat `data/*.csv` / `data/*.xlsx`
  to the canonical `data/raw/<publisher>/<file>` nested structure per
  ARCHITECTURE §4.1 (D-04). Filenames hyphenated (underscores → hyphens).
  Five files renamed atomically via `git mv` (100% rename similarity):
  - `data/lccc-actual-cfd-generation.csv` → `data/raw/lccc/actual-cfd-generation.csv`
  - `data/lccc-cfd-contract-portfolio-status.csv` → `data/raw/lccc/cfd-contract-portfolio-status.csv`
  - `data/elexon_agws.csv` → `data/raw/elexon/agws.csv`
  - `data/elexon_system_prices.csv` → `data/raw/elexon/system-prices.csv`
  - `data/ons_gas_sap.xlsx` → `data/raw/ons/gas-sap.xlsx`
- Loaders updated in the same commit (D-06):
  `src/uk_subsidy_tracker/data/elexon.py` (`AGWS_FILE`, `SYSTEM_PRICE_FILE`),
  `src/uk_subsidy_tracker/data/ons_gas.py` (`GAS_SAP_DATA_FILENAME`),
  and `src/uk_subsidy_tracker/data/lccc_datasets.yaml` (both `filename:`
  fields).
- Phase 2 scope correction (CONTEXT D-04): formal `TEST-02`, `TEST-03`,
  `TEST-05` requirement IDs reassigned from Phase 2 to Phase 4. Phase 2
  ships pre-Parquet scaffolding variants of `tests/test_schemas.py` and
  `tests/test_aggregates.py`, plus CI, pin test, and methodology
  versioning. Phase 4 adds the Parquet-schema + Parquet-aggregate
  variants + `tests/test_determinism.py` to satisfy the three formal
  requirements. `.planning/ROADMAP.md` and `.planning/REQUIREMENTS.md`
  updated.
- Phase 2 ROADMAP success criterion 1 reworded from "all five test
  classes" to "four test classes present and passing:
  `test_counterfactual.py`, `test_schemas.py`, `test_aggregates.py`,
  `test_benchmarks.py`" (per Phase 2 CONTEXT D-04).
- Phase 2 ROADMAP success criterion 3 re-anchored from "Ben Pile (2021 +
  2026), REF subset, and Turver aggregate" to "LCCC self-reconciliation
  and any regulator-native external sources the researcher located (OBR,
  Ofgem, DESNZ, HoC Library, NAO)" (per Phase 2 CONTEXT D-11).
- `ARCHITECTURE.md` §11 P1 deliverables block updated to match the
  above (per user memory: when ARCHITECTURE.md and ROADMAP disagree,
  the spec wins; the spec was amended first, ROADMAP + REQUIREMENTS
  then aligned to it).

### Fixed

- `src/uk_subsidy_tracker/data/ons_gas.py::download_dataset` (Plan 04-07
  gap #2) — `output_path` is now bound BEFORE the `try` block (previously
  raised `UnboundLocalError` on any network failure); `requests.get` now
  carries `timeout=60` matching the Elexon convention; the `except`
  handler now re-`raise`s (fail-loud per CONTEXT D-17) instead of
  silently returning an un-downloaded path. Regression test in
  `tests/test_ons_gas_download.py` locks all three invariants.
- `src/uk_subsidy_tracker/schemes/cfd/_refresh.py::refresh` (Plan 04-07
  gap #1) — now invokes all three downloaders (LCCC + Elexon + ONS;
  previously only LCCC was re-fetched) and calls `write_sidecar()` for
  each of the five raw files after successful download. This closes the
  perpetual dirty-check loop identified in 04-VERIFICATION.md.

(Phase 5 introduced no regressions requiring a Fixed entry — every
discovered Rule-1 / Rule-2 issue was fixed in the originating plan's
commits, not as a separate fix-forward.)

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

### REF Constable 2025-05-01 adopted as primary RO benchmark anchor — 2026-04-23, Plan 05-09

**Audit event — no pipeline-constant change.** Per CONTEXT D-13 post-research
amendment, REF Constable 2025-05-01 Table 1 replaces Turver Net Zero Watch
substack as the primary RO benchmark anchor. REF publishes a full 22-year
transcribable per-year cost series; Turver exposes only 2-3 single-point
figures. `REF_TOLERANCE_PCT = 3.0` (HARD BLOCK per D-14). Turver retained
as peer cross-check in `docs/schemes/ro.md` methodology prose. Matches
ROADMAP SC #3 binary "within 3%" commitment.

- Source: https://www.ref.org.uk/attachments/article/390/renewables.subsidies.01.05.25.pdf
- Retrieved: 2026-04-22
- Basis: Scheme Year aggregate RO cost, £bn nominal, GB-only, includes
  cofiring + mutualisation, excludes NIRO
- Scope alignment: matches pipeline D-12 headline (GB-only all-in incl
  cofiring + mutualisation)
- Sentinel-gated activation: `tests/test_benchmarks.py::test_ref_constable_ro_reconciliation`
  parametrises over 22 REF years and uses `pytest.xfail(strict=False)` while
  `.planning/phases/05-ro-module/05-09-DIVERGENCE.md` exists (Plan 05-01
  Option-D zero-row pipeline state). Re-arms to D-14 hard-block once Plan
  05-13 plumbs Ofgem RER data and the sentinel is deleted.

### DEFAULT_CARBON_PRICES backward extension to 2002 — 2026-04-23, Plan 05-04

**Audit event — no version bump.** Per D-06, `METHODOLOGY_VERSION`
remains `"0.1.0"`. This is an additive change (new year keys 2002-2017;
no existing 2018-2026 values revised; no formula-shape change).
Bump to 1.0.0 remains reserved for the Phase 6+ portal launch milestone.

Change summary:
- 2002-2004: `0.0` (no carbon scheme pre-EU-ETS Phase I start 2005-01-01)
- 2005-2017: EU ETS annual averages, GBP-converted at BoE contemporary
  annual-average rate
  - Phase I 2005-2007: £12.3, £11.9, £0.5 (2007 is Phase I price crash —
    allowances were non-bankable into Phase II and collapsed to ~€0.10
    by September 2007; historically correct, see `docs/schemes/ro.md`
    methodology callout)
  - Phase II 2008-2012: £17.7, £11.7, £12.3, £11.3, £6.0
  - Phase III 2013-2017: £3.8, £4.8, £5.6, £4.3, £5.1

Provenance:
- `counterfactual.py::DEFAULT_CARBON_PRICES` docstring `Provenance:`
  block cites EEA + BoE + ICE + OBR + DESNZ source URLs.
- `tests/fixtures/constants.yaml` per-year blocks carry full
  `{source, url, basis, retrieved_on, next_audit, value, unit, notes}`.
- 2005-2017 values carry `[VERIFICATION-PENDING]` inline flag in the
  `basis:` field — executor accepted Plan 05-04 research seed values
  pending audit against primary EEA + BoE sources before next_audit
  (2027-01-15). Research seeds traced to Plan 05-04 `<interfaces>`
  table derived from EEA "Emissions, allowances, surplus and prices
  in the EU ETS 2005-2020" + Bank of England EUR/GBP annual-average
  series.

Impact:
- RO scheme (launched 2002-04-01, `data/derived/ro/station_month.parquet`
  lands in Plan 05-05) can now compute `gas_counterfactual_gbp` for
  every obligation year 2002-present via `compute_counterfactual()`.
- `methodology_version` column on every RO Parquet row will still read
  `"0.1.0"` — version-consistency check in `schemes/ro/validate()` (D-04)
  does not fire.
- Closes Phase 4 SEED-001 partial-coverage gap: drift tripwire now
  enumerates all 25 `DEFAULT_CARBON_PRICES` year keys (was only 3).

### Mutualisation scope correction — SY 2021-22 only — 2026-04-23, Plan 05-05

**Audit event — scope clarification, no constant or formula change.**
CONTEXT D-11 initially listed "affected years 2021-22 and 2022-23"; research
(`.planning/phases/05-ro-module/05-RESEARCH.md` §4) verified that ONLY SY
2021-22 triggered mutualisation (£119.7M shortfall → £44.0M redistribution
December 2022). SY 2022-23 shortfall was £7.2M — well below the £318M
England + Wales + £31.9M Scotland statutory mutualisation ceilings.

- The `mutualisation_gbp` column in `data/derived/ro/station_month.parquet`
  is non-null for OY 2021-22 ONLY; null on every other obligation year.
- The S2 dynamics chart (`plotting/subsidy/ro_dynamics.py` Panel 4
  cumulative-£bn axis) annotates the mutualisation event as a single-year
  spike; no second 2022-23 marker.
- Ensures REF Constable reconciliation (Plan 05-09) does not over-attribute
  mutualisation cost in non-trigger years.

Reference:
- Ofgem "Renewables Obligation 2021/22: Mutualisation" transparency
  document + Utility Week 2024 reporting confirming SY 2022-23 non-trigger.

### `publish/manifest.py` scheme-parametric refactor — 2026-04-23, Plan 05-06

**Audit event — contract-shape change, externally URL-stable.**
`manifest.build()` signature changed from `(derived_dir, raw_dir, ...)`
to `(schemes, derived_root, raw_dir, ...)` to support multi-scheme
publishing without per-scheme branches in `manifest.py`. The external
URL pattern is preserved verbatim (`/data/latest/<scheme>/<grain>.parquet`)
and all 8 pre-existing `test_manifest.py` CfD parity tests remain green
byte-identical.

- Rationale: Phase 7 (FiT), Phase 8 (Constraint Payments), and every
  later scheme module surface in `manifest.json` automatically via
  `SCHEMES` tuple registration without `manifest.py` edits.
- Plan 05-07 then registered `("ro", ro)` in `refresh_all.SCHEMES` as
  the first multi-scheme proof point; `manifest.json` now emits 10
  Dataset entries (5 CfD + 5 RO) once `data/derived/ro/*.parquet` is
  rebuilt from non-stub raw data (gated on Plan 05-13 Ofgem RER
  plumbing).
- `GRAIN_SOURCES` / `GRAIN_TITLES` / `GRAIN_DESCRIPTIONS` migrated from
  flat dicts to nested dicts keyed by `{scheme: {grain: ...}}`. Plan 05-07
  populated the `"ro"` sub-dicts (Rule 2 auto-fix) so the multi-scheme
  iterator produces the full 10-Dataset manifest, not a CfD-only 5-Dataset
  one.

### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)

- Formula: `counterfactual_total = gas_fuel_cost + carbon_cost + plant_opex` (all £/MWh).
- Constants pinned: `CCGT_EFFICIENCY = 0.55`; `GAS_CO2_INTENSITY_THERMAL = 0.184`
  tCO2/MWh_thermal; `DEFAULT_NON_FUEL_OPEX = 5.0` £/MWh; annual
  `DEFAULT_CARBON_PRICES` 2018–2026 (EU ETS 2018–2020, UK ETS 2021+).
- Sources: BEIS Electricity Generation Costs 2023 Table ES.1 (CCGT O&M);
  GOV.UK UK ETS published prices (carbon).
- Pinned in `tests/test_counterfactual.py` at 4 decimal places; any change to
  these constants fails the pin test and requires a CHANGES.md entry here.
