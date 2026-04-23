---
phase: 05-ro-module
plan: 05
subsystem: scheme-module
tags: [ro, schemes, parquet, pandera, pydantic, counterfactual, §6.1-contract, determinism]

# Dependency graph
requires:
  - phase: 05-ro-module (Wave 1)
    provides: Plan 05-01 Ofgem scrapers + stub raw files + sidecars; Plan 05-02 ro_bandings YAML + RoBandingTable; Plan 05-03 schemas/ro.py (5 row models + emit_schema_json re-export); Plan 05-04 DEFAULT_CARBON_PRICES extended 2002-2026; Plan 05-06 manifest SCHEMES-parametric refactor
  - phase: 04-publishing-layer
    provides: schemes/cfd/ §6.1 template; sidecar.write_sidecar; SchemeModule Protocol; schemes/cfd/cost_model._write_parquet deterministic writer
provides:
  - schemes/ro/ module (5 Python files) satisfying ARCHITECTURE §6.1 SchemeModule Protocol
  - build_station_month → data/derived/ro/station_month.parquet (17 cols, RoStationMonthRow)
  - build_annual_summary / build_by_technology / build_by_allocation_round rollups
  - build_forward_projection → 2037-capped per-technology drawdown (RESEARCH §6 Option c)
  - validate() implementing all four D-04 post-rebuild sanity checks
  - 6 smoke tests proving §6.1 conformance + D-21 determinism + D-12 methodology-version chain
affects: [05-07-refresh-all-register, 05-08-charts, 05-09-ref-benchmark, 05-10-docs-ro-page, 05-11-test-parametrisation, 05-12-changes-log, 05-13-post-execution-review, phase-06-cross-scheme-charts, phase-07-fit-scheme-module]

# Tech tracking
tech-stack:
  added: []  # reuses pandera / pydantic / pyarrow / pandas already in pyproject.toml
  patterns:
    - "Cross-scheme shared deterministic writer import (_write_parquet from schemes.cfd)"
    - "Empty-input short-circuit preserves canonical Parquet schema on Wave-2 stubs"
    - "Obligation-year represented as int64 start-year internally; string label used only for roc-prices.csv merge"
    - "Generation-weighted per-technology banding factor from last 3 years of station_month.parquet"

key-files:
  created:
    - src/uk_subsidy_tracker/schemes/ro/__init__.py (243 lines; 5 §6.1 callables + D-04 4-check validate)
    - src/uk_subsidy_tracker/schemes/ro/_refresh.py (109 lines; _URL_MAP + _sha256 + refresh wiring)
    - src/uk_subsidy_tracker/schemes/ro/cost_model.py (336 lines; build_station_month 11-step pipeline)
    - src/uk_subsidy_tracker/schemes/ro/aggregation.py (186 lines; 3 rollup builders)
    - src/uk_subsidy_tracker/schemes/ro/forward_projection.py (201 lines; 2037 drawdown)
    - tests/test_ro_rebuild_smoke.py (107 lines; 6 smoke tests)
  modified:
    - src/uk_subsidy_tracker/schemes/__init__.py (barrel-export extended to include ro)

key-decisions:
  - "obligation_year stored as int64 start-year (e.g. 2021 for OY 2021-22) matching Plan 05-03 RoStationMonthRow contract; plan skeleton's str YYYY-YY treatment was a Rule 1 schema-mismatch bug"
  - "Annual counterfactual lookup via compute_counterfactual() daily → yearly mean (plan skeleton's compute_counterfactual(year=...) kwarg does not exist in counterfactual.py — Rule 1 fix)"
  - "build_annual_summary emits full 9-column RoAnnualSummaryRow (incl. gas_counterfactual_gbp + premium_gbp aggregates which the plan skeleton omitted — Rule 1 fix)"
  - "ro_cost_gbp_nocarbon == ro_cost_gbp by construction because RO ROC price is legislatively fixed; column kept for schema parity with future carbon-embedding schemes (D-05 contract)"
  - "Empty-input short-circuits write canonical-shape Parquets even with 0 data rows (Wave-2 stub compatibility) — every expected column present with correct dtype"

patterns-established:
  - "Pattern 1: schemes/<scheme>/ verbatim mirror of schemes/cfd/ — proves the §6.1 scheme-module template generalises; Phase 7 (FiT) and subsequent schemes copy this layout"
  - "Pattern 2: Internal merge-key columns (prefixed _underscore) are dropped before the final Parquet write (see _oy_label in cost_model); keeps the canonical schema clean"
  - "Pattern 3: Per-technology avg_banding_factor for forward projection via generation-weighted mean over the last 3 years of station_month.parquet (with graceful 1.0 fallback on bootstrap)"

requirements-completed: [RO-02, RO-03]

# Metrics
duration: ~35min
completed: 2026-04-23
---

# Phase 05 Plan 05: schemes/ro/ Scheme Module Summary

**Complete `schemes/ro/` tree (5 Python files) satisfying ARCHITECTURE §6.1 SchemeModule Protocol — `rebuild_derived()` emits all 5 RO Parquet grains deterministically from Ofgem raw data.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-04-23T05:02:00Z
- **Completed:** 2026-04-23T05:37:00Z
- **Tasks:** 4 (all executed; no checkpoints)
- **Files created:** 6
- **Files modified:** 1
- **Rebuild duration on stubs:** 0.11s (well under the 60s smoke-test budget in threat T-5.05-04)

## Accomplishments

- `schemes.ro` satisfies `isinstance(ro, SchemeModule)` runtime Protocol check — the second scheme after CfD, proving the §6.1 contract generalises.
- `ro.rebuild_derived(output_dir=tmp)` produces all 5 Parquet grains plus 5 sibling `.schema.json` files: station_month (17 cols), annual_summary (9 cols), by_technology (6 cols), by_allocation_round (6 cols), forward_projection (7 cols).
- Byte-identical Parquet content across two rebuilds (D-21 determinism) on every grain.
- `methodology_version` column propagates `counterfactual.METHODOLOGY_VERSION = "0.1.0"` (D-12 / GOV-02).
- `ro.validate()` implements all four D-04 checks (banding divergence, REF-Constable drift, methodology_version consistency, forward-projection sanity) and returns `[]` on a clean stub-backed rebuild.
- RO-02 (§6.1 conformance) and RO-03 (5 Parquet grains) are now closeable by Phase 5 exit.

## Task Commits

1. **Task 1: scaffold schemes/ro/ __init__ + _refresh** — `3f01129` (feat)
2. **Task 2: cost_model.py build_station_month** — `0fdc737` (feat)
3. **Task 3: aggregation.py + forward_projection.py** — `d0cfcc0` (feat)
4. **Task 4: smoke tests for §6.1 conformance** — `a671c9f` (test)

## Files Created/Modified

- `src/uk_subsidy_tracker/schemes/ro/__init__.py` — 5 §6.1 contract callables + DERIVED_DIR + 4-check `validate()` implementing every D-04 post-rebuild warner.
- `src/uk_subsidy_tracker/schemes/ro/_refresh.py` — `_URL_MAP` matching `scripts/backfill_sidecars.py::URL_MAP` on all 3 Ofgem keys (Option-D stub markers); `upstream_changed()` SHA-compares against sidecars; `refresh()` wires 3 downloaders + 3 `write_sidecar` calls.
- `src/uk_subsidy_tracker/schemes/ro/cost_model.py` — 11-step `build_station_month` pipeline: load raw → merge register → month-end + OY label (D-08) → country normalise (D-09) → commissioning-window label → banding lookup (D-01 audit) → roc-prices join → dual cost columns (D-02) + no-carbon sensitivity (D-05) → annual counterfactual + premium → mutualisation (D-11) → methodology stamp → validate + write.
- `src/uk_subsidy_tracker/schemes/ro/aggregation.py` — 3 rollup builders (annual_summary, by_technology, by_allocation_round) each re-reading station_month.parquet per D-03; int64 year cast; D-11 null-preserving mutualisation sum.
- `src/uk_subsidy_tracker/schemes/ro/forward_projection.py` — per-station accreditation-end anchor (2037 cap); deterministic `max(output_period_end).year` current-year anchor (D-21); generation-weighted per-technology banding factor from last 3 years.
- `src/uk_subsidy_tracker/schemes/__init__.py` — barrel-export extended from `{cfd}` to `{cfd, ro}`.
- `tests/test_ro_rebuild_smoke.py` — 6 smoke tests: §6.1 `isinstance`, 5 Parquet + 5 schema.json emission, methodology_version propagation, two-rebuild byte-identity, `validate()` returns list, `upstream_changed()` returns bool.

## Decisions Made

- **obligation_year int64 start-year (not str).** The landed Plan 05-03 schema declares `obligation_year: int` with `dtype: int64`. The plan's skeleton pandera + docstring used string "YYYY-YY". Kept the landed schema as authoritative (it already had 9 smoke tests passing): compute `_oy_label` internally for the roc-prices.csv merge, then drop the label and write the integer start-year. Parquet column is `int64`. This is a Rule 1 schema-mismatch fix, not a contract change.
- **Annual-average counterfactual.** `counterfactual.compute_counterfactual()` takes `gas_df` + `carbon_prices` (not `year=`); it returns a daily DataFrame. Implemented `_annual_counterfactual_gbp_per_mwh()` that calls it once and collapses to `{year: mean(counterfactual_total)}`. Cost model maps station-month calendar year to the annual average — equivalent semantics to the plan's intent, but compatible with the actual signature.
- **9-column annual_summary.** Plan skeleton aggregated only 6 data columns; landed schema declares 9. Added `gas_counterfactual_gbp` + `premium_gbp` sum aggregates to match the contract. Rule 1 / D-10 column-order contract fix.
- **Empty-input short-circuits.** All 3 builders (cost_model, aggregation, forward_projection) explicitly detect `len(input) == 0` and produce canonical-shape empty Parquets with correct dtypes. Prevents pandera coerce failures on the Wave-2 stub inputs while preserving the schema contract for downstream tests.
- **Generation-weighted banding factor (forward projection).** Per-technology avg banding factor is derived from the last 3 complete years of station_month.parquet weighted by generation_mwh. Falls back to 1.0 when station_month.parquet is absent (Wave-2 bootstrap edge). Correctly weights offshore wind (~1.9-2.0 ROCs/MWh) against co-firing (~0.5) rather than assuming a flat 1.0 proxy.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] obligation_year schema-mismatch between plan and landed RoStationMonthRow**
- **Found during:** Task 2 (cost_model.py implementation)
- **Issue:** Plan 05-05 `<action>` skeleton declared `obligation_year` as `str` matching `^\d{4}-\d{2}$` (e.g. "2021-22"). The landed Plan 05-03 `RoStationMonthRow.obligation_year: int` with `json_schema_extra={"dtype": "int64"}`. Writing strings would have violated the schema contract that already had 9 green tests.
- **Fix:** Introduced `_obligation_year_start(month_end)` returning `int` (start year) alongside `_obligation_year_label(start_year)` returning the "YYYY-YY" string used internally for joining to roc-prices.csv. The label column is dropped before the final write; the canonical Parquet column is int64.
- **Files modified:** `src/uk_subsidy_tracker/schemes/ro/cost_model.py`
- **Verification:** Verified `_obligation_year_start(pd.Timestamp('2022-03-31')) == 2021`, `_obligation_year_start(pd.Timestamp('2022-04-01')) == 2022`; pandera `obligation_year: pa.Column("int64", coerce=True)` validates clean; test_ro_rebuild_smoke passes.
- **Committed in:** `0fdc737` (Task 2 commit)

**2. [Rule 1 - Bug] compute_counterfactual(year=...) signature does not exist**
- **Found during:** Task 2 (cost_model.py implementation)
- **Issue:** Plan 05-05 `<action>` skeleton called `compute_counterfactual(year=int(year), carbon_prices=DEFAULT_CARBON_PRICES)` and expected a `dict` or scalar return. The actual `counterfactual.compute_counterfactual()` signature is `(gas_df, carbon_prices, ccgt_efficiency, non_fuel_opex_per_mwh)` and returns a daily DataFrame with `counterfactual_total` (£/MWh). The plan code would have raised `TypeError: unexpected kwarg 'year'` at runtime.
- **Fix:** Added `_annual_counterfactual_gbp_per_mwh()` helper that calls `compute_counterfactual()` once (no kwargs except `carbon_prices=DEFAULT_CARBON_PRICES`) and groups by calendar year to produce `{year: mean(counterfactual_total)}`. The cost model maps each station-month row's calendar year through this dict; unseen years map to 0.0.
- **Files modified:** `src/uk_subsidy_tracker/schemes/ro/cost_model.py`
- **Verification:** End-to-end `rebuild_derived()` produces `gas_counterfactual_gbp` + `premium_gbp` columns; test_ro_rebuild_smoke determinism test passes (the annual-average path is deterministic).
- **Committed in:** `0fdc737` (Task 2 commit)

**3. [Rule 1 - Bug] build_annual_summary omitted 2 schema columns**
- **Found during:** Task 3 (aggregation.py implementation)
- **Issue:** Plan 05-05 `<action>` skeleton for `build_annual_summary` aggregated only `ro_generation_mwh, ro_cost_gbp, ro_cost_gbp_eroc, gas_counterfactual_gbp(missing), premium_gbp(missing), mutualisation_gbp`. Landed `RoAnnualSummaryRow` declares 9 columns including `gas_counterfactual_gbp` and `premium_gbp`. Plan code would have failed at `df[columns]` column-selection against the 9-field model.
- **Fix:** Added `gas_counterfactual_gbp=("gas_counterfactual_gbp", "sum")` and `premium_gbp=("premium_gbp", "sum")` to the groupby aggregation. All 9 `RoAnnualSummaryRow` columns now present in order.
- **Files modified:** `src/uk_subsidy_tracker/schemes/ro/aggregation.py`
- **Verification:** `pq.read_table(tmp/'annual_summary.parquet').column_names` returns all 9 expected columns; `test_ro_methodology_version_column` parametrised over all 5 grains passes.
- **Committed in:** `d0cfcc0` (Task 3 commit)

**4. [Rule 2 - Missing critical] Task 1 needed skeleton stubs for aggregation/cost_model/forward_projection**
- **Found during:** Task 1 (§6.1 contract shell scaffolding)
- **Issue:** Plan noted "rebuild_derived still raises ImportError until Tasks 2-3 land the derivation modules" but `schemes/ro/__init__.py` performs top-level `from uk_subsidy_tracker.schemes.ro.cost_model import build_station_month` imports. ImportError at module-load time would have broken `from uk_subsidy_tracker.schemes import ro` and failed Task 1's verify command.
- **Fix:** Created minimal skeleton cost_model.py / aggregation.py / forward_projection.py modules with `NotImplementedError`-raising function stubs. Module imports succeed at Task 1 commit time; calling `rebuild_derived()` still raises (as the plan anticipated) until Tasks 2-3 replace the stubs with real implementations.
- **Files modified:** `src/uk_subsidy_tracker/schemes/ro/{cost_model,aggregation,forward_projection}.py`
- **Verification:** Task 1 verify command (`from schemes import ro; assert callable(ro.upstream_changed)` etc.) succeeded; `isinstance(ro, SchemeModule)` returned True at Task 1 boundary.
- **Committed in:** `3f01129` (Task 1 commit — stubs shipped alongside `__init__.py` + `_refresh.py`)

---

**Total deviations:** 4 auto-fixed (3 Rule 1 bugs, 1 Rule 2 missing critical).
**Impact on plan:** All four auto-fixes were correctness requirements — three honoured the landed Plan 05-03 schema contract (which had already passed 9 green tests), and one preserved Task 1's verify command. No scope creep. Plan outcome matches spec: `schemes.ro` is a valid SchemeModule; 5 Parquet grains emit; determinism + methodology_version invariants hold.

## Issues Encountered

- **Ofgem raw files are Option-D header-only stubs.** Expected. Rebuild produces 0-row Parquets on every grain; empty-input short-circuits ensure the canonical schema shape is preserved. Once Plan 05-13 post-execution review lands real Ofgem RER URLs + transcribed ROC prices, the pipeline will populate real rows without code change.
- **`test_ro_upstream_changed_returns_bool` could return True.** The test only type-checks the bool return (not the value). Plan 05-01 committed stub files + backfilled sidecars with matching SHAs, so the expected value IS False — verified manually (`ro.upstream_changed() → False`). If Plan 05-13 review modifies the stub bytes, the test keeps passing (type check) while the value flips to True until sidecars are refreshed.

## Known Stubs

None introduced by this plan. The pre-existing Option-D stubs (Plan 05-01 raw Ofgem files) remain; they are scheduled for resolution in Plan 05-13 Task 5 post-execution human review, and are separately tracked in that plan's scope.

## Next Phase Readiness

- **Plan 05-07** (refresh_all SCHEMES registration): Ready. One-line append `("ro", ro)` to `SCHEMES` in `refresh_all.py` will activate the daily Ofgem dirty-check via the §6.1 contract wired here.
- **Plan 05-08** (4 RO charts): Ready. `data/derived/ro/*.parquet` files exist with correct schemas; chart code can `pq.read_table(...)` and filter. Note: stub inputs produce empty Parquets, so charts will render empty until Plan 05-13 review lands real data.
- **Plan 05-09** (REF Constable benchmark): Ready. `ro.validate()` Check 2 already attempts best-effort drift detection; the hard-block version lives in `tests/test_benchmarks.py` which Plan 05-09 will add. `benchmarks.yaml::ref_constable` section still needs to be transcribed (Plan 05-09 Task 1 scope).
- **Plan 05-11** (test parametrisation): Ready. `test_schemas.py` / `test_aggregates.py` / `test_determinism.py` can parametrise over the same `_GRAINS` list this plan defines.
- **Plan 05-13** (post-execution review): Flagged. Real Ofgem RER URLs + transcribed roc-prices.csv are the unlock for populated Parquets. After that lands, `validate()` Check 2 will produce real REF-drift percentages, driving the adversarial-proofing contract.

---

## Self-Check: PASSED

- src/uk_subsidy_tracker/schemes/ro/__init__.py: FOUND
- src/uk_subsidy_tracker/schemes/ro/_refresh.py: FOUND
- src/uk_subsidy_tracker/schemes/ro/cost_model.py: FOUND
- src/uk_subsidy_tracker/schemes/ro/aggregation.py: FOUND
- src/uk_subsidy_tracker/schemes/ro/forward_projection.py: FOUND
- tests/test_ro_rebuild_smoke.py: FOUND
- Commit 3f01129 (Task 1): FOUND
- Commit 0fdc737 (Task 2): FOUND
- Commit d0cfcc0 (Task 3): FOUND
- Commit a671c9f (Task 4): FOUND
- `isinstance(ro, SchemeModule)`: True
- `rebuild_derived()` emits 5 Parquet + 5 schema.json: confirmed
- 151 tests passed + 4 skipped (up from 145 + 4): confirmed

---
*Phase: 05-ro-module*
*Completed: 2026-04-23*
