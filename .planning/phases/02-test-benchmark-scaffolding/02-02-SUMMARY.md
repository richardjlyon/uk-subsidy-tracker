---
phase: 02-test-benchmark-scaffolding
plan: 02
subsystem: testing
tags: [schemas, pandera, aggregates, pre-parquet-scaffolding, test-02, test-03]

# Dependency graph
requires:
  - phase: 01-foundation-tidy
    provides: "uk_subsidy_tracker package path; pandera >= 0.31.1 in pyproject.toml; data/ raw CSVs + XLSX on disk"
  - plan: 02-01
    provides: "METHODOLOGY_VERSION constant (co-landed, not consumed by this plan); CHANGES.md ## Methodology versions 1.0.0 section"
  - plan: 02-05
    provides: "CHANGES.md [Unreleased] ### Changed block (scope correction) — this plan extends with ### Added above it; TEST-02/03 traceability rows formally Phase-4-owned so this plan only ships scaffolding"
provides:
  - "Pandera schemas elexon_agws_schema, elexon_system_price_schema, ons_gas_schema importable at module level"
  - "load_elexon_wind_daily / load_elexon_prices_daily / load_gas_price now call schema.validate() internally — upstream schema drift raises SchemaError at load"
  - "tests/test_schemas.py with 5 loader-driven tests (LCCC gen, LCCC portfolio, Elexon wind, Elexon prices, ONS gas) — pre-Parquet scaffolding for TEST-02"
  - "tests/test_aggregates.py with 2 invariant tests (row-conservation on CfD_Payments_GBP + no-orphan-Technology guard) — pre-Parquet scaffolding for TEST-03"
  - "CHANGES.md [Unreleased] ### Added block enumerating Plan 01 + Plan 02 artefacts"
affects: [02-03, 02-04, phase-04]

# Tech tracking
tech-stack:
  added: []  # pandera already a dependency (>= 0.31.1); no new packages
  patterns:
    - "Pandera schema sibling pattern: each raw-source loader owns one pa.DataFrameSchema with strict=False + coerce=True + nullable=True on metric columns, defined at module level next to the loader"
    - "schema.validate(df) called inside the loader immediately after pd.read_csv (or after DataFrame construction for XLSX) and before any downstream filtering/aggregation — so all callers transparently benefit from validation"
    - "test_schemas.py idiom: call loader + assert not df.empty + assert key column present + assert dtype kind ('M' for datetime, 'f' for float) — SchemaError from loader fails the test without the test file needing to import pandera"
    - "test_aggregates.py idiom: module-scope fixture derives `year` column once, flat test functions assert invariants via pd.testing.assert_series_equal (row conservation) or .notna().all() (no orphan rows)"
    - "import pandera.pandas as pa (canonical pandera >= 0.24 form); NEVER `import pandera as pa` (deprecated, emits FutureWarning)"
    - "Keep-a-Changelog [Unreleased] ordering: ### Added above ### Changed — this plan extends 02-05's pre-existing ### Changed block by inserting ### Added before it, preserving chronological order of Plan 01 → Plan 02 landings"

key-files:
  created:
    - "tests/test_schemas.py"
    - "tests/test_aggregates.py"
    - ".planning/phases/02-test-benchmark-scaffolding/02-02-SUMMARY.md"
  modified:
    - "src/uk_subsidy_tracker/data/elexon.py"
    - "src/uk_subsidy_tracker/data/ons_gas.py"
    - "CHANGES.md"

key-decisions:
  - "Loader-owned validation (schema.validate() inside the loader, not in the test) — callers and tests both benefit; test_schemas.py does not need to import pandera; schema drift fails at read-time, not only under `pytest`"
  - "Pre-Parquet scaffolding does NOT mark TEST-02 / TEST-03 complete in REQUIREMENTS.md traceability — 02-05 moved them to Phase 4 where the Parquet-variant assertions land; today's variants are useful-today scaffolding, not formal satisfaction"
  - "Row-conservation test uses pd.testing.assert_series_equal (not element-wise tolerance) because the decomposed-then-collapsed sum is algebraically identical to the direct sum under pandas groupby, so exact equality is the correct assertion"
  - "Test file does NOT assert payments >= 0 — LCCC publishes legitimate negative CFD_Payments_GBP when market-reference-price exceeds strike-price (see 02-RESEARCH Pitfall 7/8); a non-negative guard would be a false positive"
  - "Three atomic commits (one per task) rather than bundling — matches Phase 1 D-16 atomic-commit discipline and makes the Elexon/ONS schema change, the schema tests, and the aggregate tests + CHANGES bump independently revertable"

patterns-established:
  - "Raw-source schema pattern: every future raw-data module (Ofgem RO register, NESO BM half-hourly, EMR capacity auctions, etc.) will follow the Elexon pattern — module-level pa.DataFrameSchema + .validate() call inside the loader body. tests/test_schemas.py extends by adding one `def test_<source>_schema` per new loader."
  - "Row-conservation invariant pattern: whenever a pipeline decomposes a total into a by-dimension breakdown, there must be a test that the decomposed-and-recomposed total equals the direct total. Applies cleanly to Phase-4 derived Parquet (station-month × month = annual) and to every future scheme module."

requirements-completed: []  # Deliberate: TEST-02 and TEST-03 are Phase-4-owned per 02-05 bookkeeping.
requirements-in-progress: [TEST-02, TEST-03]

# Metrics
duration: 2min
tasks: 3
files: 5
completed: 2026-04-22
---

# Phase 02 Plan 02: Pandera Schemas + Schema/Aggregate Scaffolding Summary

**Elexon and ONS loaders now validate via pandera on read; 5 loader-driven schema tests plus 2 row-conservation invariants ship as pre-Parquet scaffolding for TEST-02 / TEST-03 (formal Phase-4 variants still pending).**

## Performance

- **Duration:** ~2 min (159 s)
- **Started:** 2026-04-22T10:48:53Z
- **Completed:** 2026-04-22T10:51:32Z
- **Tasks:** 3 / 3
- **Files created:** 3 (`tests/test_schemas.py`, `tests/test_aggregates.py`, this summary)
- **Files modified:** 3 (`elexon.py`, `ons_gas.py`, `CHANGES.md`)
- **Tests added:** 7 passing (5 schema + 2 aggregate). Full suite now 16 passing + 2 skipped in 1.58 s.

## Accomplishments

- **Elexon loaders gained pandera validation.** `elexon_agws_schema` (settlementDate + settlementPeriod + businessType + quantity) and `elexon_system_price_schema` (settlementDate + settlementPeriod + systemSellPrice + systemBuyPrice) are now module-level schemas in `src/uk_subsidy_tracker/data/elexon.py`. Both `load_elexon_wind_daily()` and `load_elexon_prices_daily()` call `.validate(df)` immediately after `pd.read_csv` and before the filter/groupby — upstream column-name or dtype drift now raises `SchemaError` at load-time, not silently downstream.
- **ONS gas loader gained pandera validation.** `ons_gas_schema` (date + gas_p_per_kwh) validates the constructed 2-column DataFrame inside `load_gas_price()` after `dropna` and before `return`. Guards against the XLSX header-row detection drifting in a future ONS publication.
- **Canonical `import pandera.pandas as pa` everywhere.** No `import pandera as pa` (deprecated since pandera 0.24) anywhere in the modified files — verified via ripgrep.
- **`tests/test_schemas.py` scaffolding landed.** Five flat loader-driven tests cover every raw source the CfD pipeline reads: LCCC CfD generation (with dtype checks on `Settlement_Date` and `CFD_Payments_GBP`), LCCC portfolio, Elexon AGWS → daily wind MW, Elexon system prices → daily £/MWh, and ONS SAP gas → daily pence/kWh. No fixtures, no classes, no pandera import — a SchemaError from any loader fails the corresponding test automatically.
- **`tests/test_aggregates.py` scaffolding landed.** `test_year_vs_year_tech_sum_match` asserts that `sum(CFD_Payments_GBP) by year` equals the same total re-aggregated as `(year × Technology)` and collapsed back to year, via `pd.testing.assert_series_equal` — catching the classic pandas pitfall where a groupby on a NaN dimension silently drops rows. `test_no_orphan_technologies` adds an explicit non-null guard on `Technology`. Both tests share a module-scope `lccc_gen` fixture so the CSV is loaded once per test module.
- **CHANGES.md `[Unreleased]` now has `### Added` above `### Changed`.** Enumerates the Plan-01 + Plan-02 artefacts (counterfactual pin test, METHODOLOGY_VERSION, three schemas, three test files). Existing 02-05 `### Changed` block and `## Methodology versions` 1.0.0 entry are untouched.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add pandera schemas + `.validate()` calls to `elexon.py` and `ons_gas.py`** — `be34caf` (feat)
2. **Task 2: Create `tests/test_schemas.py`** — `6f8a2bb` (test)
3. **Task 3: Create `tests/test_aggregates.py` + extend CHANGES.md `[Unreleased] ### Added`** — `af68831` (test)

## Files Created/Modified

- **`src/uk_subsidy_tracker/data/elexon.py`** — added `import pandera.pandas as pa`; added two module-level `pa.DataFrameSchema` instances (`elexon_agws_schema`, `elexon_system_price_schema`) after the `MAX_WORKERS` constant and before the first function; inserted `df = elexon_agws_schema.validate(df)` and `df = elexon_system_price_schema.validate(df)` inside the two public loaders. +30 lines, no other logic changed.
- **`src/uk_subsidy_tracker/data/ons_gas.py`** — added `import pandera.pandas as pa`; added `ons_gas_schema` above `download_dataset`; inserted `df = ons_gas_schema.validate(df)` inside `load_gas_price()` after the `dropna` and before the `return`. +10 lines, no other logic changed.
- **`tests/test_schemas.py`** — new file, 66 lines. Five flat test functions (`test_lccc_generation_schema`, `test_lccc_portfolio_schema`, `test_elexon_wind_daily_schema`, `test_elexon_prices_daily_schema`, `test_ons_gas_schema`). Module docstring documents the "formal TEST-02 in Phase 4" relationship. Imports from `uk_subsidy_tracker.data` (barrel).
- **`tests/test_aggregates.py`** — new file, 50 lines. `@pytest.fixture(scope="module")` + two flat test functions. Imports `pandas as pd` + `pytest` + `load_lccc_dataset` from the data barrel.
- **`CHANGES.md`** — `[Unreleased]` block now has `### Added` sub-section above the existing `### Changed` sub-section (5 bullets covering counterfactual test, schemas test, aggregates test, METHODOLOGY_VERSION, pandera schemas). `## [0.1.0]` and `## Methodology versions` sections untouched.

## Decisions Made

- **Loader-owned validation, not test-owned validation.** The alternative (call the loader in the test, then invoke `schema.validate()` on the returned frame) would force `tests/test_schemas.py` to import pandera and would only catch schema violations when `pytest` runs. Putting the `.validate()` call inside the loader body means every code path that reads raw data benefits — charts, ad-hoc notebooks, future scheme modules — not only the test suite. Matches the existing `load_lccc_dataset` idiom verbatim.
- **`TEST-02` and `TEST-03` are NOT marked Complete in REQUIREMENTS.md.** 02-05 formally moved them to Phase 4 where the Parquet-variant assertions land. Today's work ships the pre-Parquet scaffolding as useful-today infrastructure. Marking them Complete now would mis-signal phase coverage. The plan's frontmatter listed them for traceability but `must_haves.truths` explicitly frame the deliverables as "present and scaffolded pre-Parquet" — honoured by leaving the Phase-4 rows Pending and noting in-progress status under `requirements-in-progress` in this summary.
- **`pd.testing.assert_series_equal` for row-conservation, not tolerance-based comparison.** The decomposed-then-collapsed sum is algebraically identical to the direct sum under pandas groupby (floating-point operations commute for this aggregation pattern with fully populated keys). Exact equality is the correct assertion. If a future dataset introduces NaN-key rows, the fail mode is an observable key mismatch, not a floating-point drift — `assert_series_equal` surfaces both.
- **No `>= 0` assertion on `CFD_Payments_GBP`.** LCCC publishes legitimate negative payments when market-reference-price exceeds strike-price (see 02-RESEARCH Pitfall 7/8). The 2022 row-sum is `-£0.346 bn` and is correct. A non-negative guard would produce false positives and reviewer confusion.
- **Three atomic commits, not two or one.** Task 1 (source-code change adding validation) is independently revertable from Task 2 (new test file asserting the validation works) is independently revertable from Task 3 (new test file + doc update). Matches Phase 1 D-16 atomic-commit discipline.

## Deviations from Plan

None — plan executed exactly as written. Each task's acceptance-criteria grep checks passed first-pass; `uv run pytest tests/test_schemas.py` returned 5 passed and `uv run pytest tests/test_aggregates.py` returned 2 passed on first run. No auto-fixes under Rule 1/2/3 were required. No architectural pauses. No CLAUDE.md directives required adjustments. The full suite smoke test (`uv run pytest`) shows 16 passed + 2 skipped in 1.58 s, i.e. every pre-existing test still green.

One operational subtlety worth recording: the four PreToolUse "read-before-edit" hook reminders during Task 1 + Task 3 were false positives (all four files had been Read in the opening context-load batch). The edits themselves applied cleanly each time.

## Issues Encountered

- None substantive.
- The hook reminder false-positives (above) are a local workflow artefact, not a code issue.

## User Setup Required

None — no external service, credential, or manual step required. All tests run offline against committed fixtures in `data/`.

## Threat Flags

None — plan does not introduce new trust boundaries. All four threat-register rows (T-02-01 through T-02-05) were marked `N/A for this plan` in the plan frontmatter and remain so: this plan does not touch `.github/workflows`, CI env, `benchmarks.yaml`, counterfactual constants, or branch protection. No new security-relevant surface introduced.

## Known Stubs

None. Every new line of code is wired end-to-end:

- The three pandera schemas are live-used by three production loaders on every read.
- `tests/test_schemas.py` exercises each loader against the actual committed CSV/XLSX fixtures.
- `tests/test_aggregates.py` exercises the LCCC generation pipeline and actually evaluates the row-conservation arithmetic.
- CHANGES.md `### Added` bullets all reference files that exist on disk.

No placeholder text, no hardcoded mock data, no "TODO / FIXME / coming soon" strings introduced.

## Next Phase Readiness

**Plan 02-03 (`tests/test_benchmarks.py` + `tests/fixtures/benchmarks.yaml`) unblocked.** Required handshakes:

- The module-scope `lccc_gen` fixture in `tests/test_aggregates.py` is a candidate for hoisting to `tests/conftest.py` if 02-03 also needs LCCC annual totals. The 02-02 PATTERNS.md guidance (Shared Patterns, §C "Barrel re-exports") explicitly says "do not hoist preemptively; planner for 02-03 decides." If 02-03 needs the same fixture, the reasonable move is adding `tests/conftest.py` in that plan and merging the fixture there.
- CHANGES.md `[Unreleased] ### Added` block now exists; 02-03 can simply append bullets for `test_benchmarks.py` + `benchmarks.yaml` + `fixtures/__init__.py` without needing to create the sub-section.

**Plan 02-04 (`.github/workflows/ci.yml`) unblocked.** The test suite is now 16 passing + 2 skipped in 1.58 s locally. The CI workflow will exercise `test_schemas.py` and `test_aggregates.py` against the same committed `data/` CSVs/XLSX — no network dependency, no secrets, no matrix complexity.

**Downstream (Phase 4) handshake confirmed:**

- The Phase-4 Parquet-variant of `test_schemas.py` extends the same file with Parquet-schema assertions on `data/derived/**.parquet`. Today's scaffolding establishes the loader-calls-then-asserts idiom the Parquet variant inherits.
- The Phase-4 Parquet-variant of `test_aggregates.py` adds row-conservation assertions on Parquet station-month / annual-summary tables. Today's LCCC row-conservation invariant is the canonical shape the Parquet assertions copy.
- `TEST-02` and `TEST-03` formally satisfy in Phase 4 Plan `05` (per 02-05 ROADMAP bookkeeping).

---

*Phase: 02-test-benchmark-scaffolding*
*Completed: 2026-04-22*

## Self-Check: PASSED

- All 5 declared files exist on disk: `src/uk_subsidy_tracker/data/elexon.py`, `src/uk_subsidy_tracker/data/ons_gas.py`, `tests/test_schemas.py`, `tests/test_aggregates.py`, `CHANGES.md`.
- All 3 task commits present in `git log`: `be34caf`, `6f8a2bb`, `af68831`.
- `uv run pytest tests/test_schemas.py tests/test_aggregates.py -v` → 7 passed in 1.65 s.
- Full-suite smoke: `uv run pytest` → 16 passed + 2 skipped in 1.58 s.
- All per-task grep acceptance criteria returned PASS.
- No deletions introduced by any of the 3 commits (`git diff --diff-filter=D --name-only HEAD~3 HEAD` empty).
- No `import pandera as pa` (deprecated) anywhere in modified files — ripgrep confirmed.
- Three schemas importable + correct type: `DataFrameSchema DataFrameSchema DataFrameSchema`.
