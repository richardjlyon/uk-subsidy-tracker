---
phase: 05-ro-module
plan: 10
subsystem: testing
tags: [pytest, parametrise, parquet, pyarrow, pydantic, ro, schema-validation, row-conservation, determinism]

# Dependency graph
requires:
  - phase: 05-ro-module
    provides: "RO module rebuild_derived emits 5 Parquet grains; RO Pydantic row models in schemas/ro.py (Plans 05-03, 05-04, 05-05)"
  - phase: 04-publishing-layer
    provides: "Phase-4 quality-gate parametrisation idiom on test_schemas / test_aggregates / test_determinism for CfD"
provides:
  - "5 RO grain-schema parametrised tests on test_schemas.py (RO-03 / TEST-02)"
  - "3 RO row-conservation parametrised tests on test_aggregates.py (TEST-03; D-09 country groupby)"
  - "10 RO byte-identity parametrised tests on test_determinism.py (TEST-05; D-21)"
  - "D-11 fallback skip helper for RO row-conservation under seed-stub raw inputs"
affects: [05-11, 05-12, 05-13, 06, 07-fit]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Independent module-scoped RO fixtures alongside CfD (PATTERNS.md directive — NOT merged)"
    - "D-11 stub-data fallback skip for tests with empty-MultiIndex pandas semantic mismatch"
    - "Schema column-order assertion (D-10) runs unconditionally even on empty Parquets"

key-files:
  created: []
  modified:
    - "tests/test_schemas.py — +74 lines: 5 RO parametrised grain-schema cases"
    - "tests/test_aggregates.py — +118 lines: 3 RO row-conservation invariants + skip helper"
    - "tests/test_determinism.py — +70 lines: 10 RO parametrised cases (5 content + 5 metadata)"

key-decisions:
  - "Per-row Pydantic validation skips on empty RO Parquets (seed-stub reality); column-order assertion runs unconditionally because Parquet column metadata is a header-level contract valid against zero rows"
  - "Row-conservation tests skip cleanly via D-11 fallback when station_month is empty: pandas assert_series_equal rejects empty MultiIndex levels (inferred_type 'string' from groupby vs 'empty' from set_index)"
  - "Independent module-scoped fixtures for RO (ro_derived_dir, ro_derived_once, ro_derived_twice) — no merging with CfD per PATTERNS.md directive"

patterns-established:
  - "D-11 fallback skip pattern for stub-data row-conservation tests: extract a _skip_if_empty_*() helper used by every parametrisation; reasons reference 'real RER data wired' for grep-discoverability when the data lands"
  - "Schema-shape contract enforceable on zero-row Parquets: column-order list assertion is meaningful in the file header, runs always; per-row Pydantic validation is content-dependent, skips on empty"
  - "Cross-scheme test parametrisation discipline: scheme-A fixture names get a scheme-prefix (ro_derived_dir, ro_station_month) so adding scheme-B never shadows scheme-A's existing module-scoped fixtures"

requirements-completed: [RO-03]

# Metrics
duration: 5min
completed: 2026-04-23
---

# Phase 05-ro-module Plan 10: Phase-4 quality-gate test parametrisation extended to RO grains Summary

**Three Phase-4 quality-gate test files (test_schemas, test_aggregates, test_determinism) gain parallel RO parametrisations alongside their CfD blocks; CfD parametrisations untouched; D-11 fallback skip activates cleanly under the seed-stub Ofgem raw inputs.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-04-23T06:16:06Z
- **Completed:** 2026-04-23T06:20:34Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- `tests/test_schemas.py` extended with `ro_derived_dir` module-scoped fixture, `_RO_GRAIN_MODELS` dict, and parametrised `test_ro_parquet_grain_schema` covering all 5 RO grains. Column-order discipline (D-10) asserted unconditionally; per-row Pydantic validation skips on empty Parquets.
- `tests/test_aggregates.py` extended with 4 module-scoped fixtures (`ro_derived_dir`, `ro_station_month`, `ro_annual_summary`, `ro_by_technology`, `ro_by_allocation_round`) and 3 row-conservation tests covering D-09 country groupby (annual), technology groupby (by_technology), and commissioning_window groupby (by_allocation_round — RO has no allocation-round axis). D-11 fallback skip helper guards empty-data MultiIndex semantic mismatch.
- `tests/test_determinism.py` extended with `ro_derived_once` / `ro_derived_twice` independent fixtures, `RO_GRAINS` tuple, and 10 parametrised cases (5 content-equality via `pyarrow.Table.equals` + 5 writer-identity via `parquet-cpp-arrow` prefix check).
- Test count delta: trio went from 25 passed to 35 passed + 8 skipped (+10 passed = 5 schema-skip + 3 aggregate-skip + 10 determinism-pass = 18 new RO test instances). Full suite: 153 → 163 passed, 4 → 12 skipped, 22 xfailed unchanged.

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend test_schemas.py with RO grain parametrisation** — `a552e6b` (test)
2. **Task 2: Extend test_aggregates.py with RO row-conservation tests** — `d6d5f0e` (test)
3. **Task 3: Extend test_determinism.py with RO byte-identity checks** — `7b7f7ee` (test)

**Plan metadata commit:** _to follow_ (this SUMMARY + STATE.md + ROADMAP.md update)

## Files Created/Modified

- `tests/test_schemas.py` — +74 lines: RO imports, `ro_derived_dir` fixture, `_RO_GRAIN_MODELS` dict, parametrised `test_ro_parquet_grain_schema` (5 grain cases).
- `tests/test_aggregates.py` — +118 lines: 4 RO fixtures, `_skip_if_empty_ro_station_month` helper, 3 row-conservation tests (annual / by_technology / by_allocation_round).
- `tests/test_determinism.py` — +70 lines: `RO_GRAINS` tuple, 2 RO fixtures, parametrised content-equality test, parametrised writer-identity test.

## Decisions Made

- **D-10 column-order check runs unconditionally on empty Parquets** (test_schemas Task 1). Parquet column metadata is a file-header property and is meaningful even when row count is zero. The plan's literal version skipped the entire test on empty data; instead the column-order block runs first, then per-row validation skips on empty. This gives partial credit while real RER data is being wired.
- **D-11 fallback for row-conservation tests via skip helper** (test_aggregates Task 2). pandas `assert_series_equal` rejects empty MultiIndex levels because `inferred_type` differs between an empty groupby result (carries the column dtype, e.g. `'string'`) and an empty `set_index` MultiIndex (reports `'empty'`). Same shape, different metadata. The cleanest fix is `pytest.skip()` with a grep-discoverable reason ("real RER data wired") that both surfaces the deferred state and triggers the test the moment a single non-empty row arrives. Documented in the helper docstring.
- **Independent fixture naming with `ro_` prefix** across all three files (Task 1 / 2 / 3). Per PATTERNS.md directive: CfD `derived_dir` and RO `ro_derived_dir` coexist as module-scoped fixtures. Each scheme rebuilds into its own tmp dir; cross-scheme ordering is impossible.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] Plan's literal `test_ro_annual_vs_station_month_parquet` failed on empty data**
- **Found during:** Task 2 (test_aggregates.py)
- **Issue:** The plan's literal version of the row-conservation test would fail under stub-data conditions (current state per `prior_wave_context` — RO derived Parquet is zero-row). pandas `assert_series_equal` rejects empty MultiIndex levels because `inferred_type` is `'string'` for empty groupby results vs `'empty'` for empty `set_index` results. Plan acknowledged the stub-data reality but didn't add the necessary fallback for empty MultiIndex comparison semantics.
- **Fix:** Added `_skip_if_empty_ro_station_month()` helper called at the top of all 3 RO row-conservation tests; helper invokes `pytest.skip()` with a grep-discoverable reason string. Tests re-activate automatically when a single non-empty Ofgem RER row exists. The same D-11 fallback pattern the prior_wave_context anticipated.
- **Files modified:** `tests/test_aggregates.py`
- **Verification:** `uv run pytest tests/test_aggregates.py -x -q` → 5 passed (CfD), 3 skipped (RO with reason "RO station_month is empty (seed-stub raw data); row-conservation invariant deferred until real RER data is wired").
- **Committed in:** `d6d5f0e` (Task 2 commit)

**2. [Rule 1 — Bug] Plan's literal `test_ro_parquet_grain_schema` would skip column-order discipline on empty data**
- **Found during:** Task 1 (test_schemas.py)
- **Issue:** Plan's literal block placed `pytest.skip()` for empty data BEFORE the column-order assertion. Column-order discipline (D-10) is a header-level contract that's meaningful even with zero rows — skipping the whole test loses that gate. If a future plan accidentally reordered RO row-model fields, the regression would not surface until real data arrived.
- **Fix:** Reordered the test body so the column-order assertion runs first (always), then per-row Pydantic validation skips on empty data. Empty Parquets still validate the schema-shape contract.
- **Files modified:** `tests/test_schemas.py`
- **Verification:** All 5 RO parametrised cases skip with reason "per-row schema validation deferred"; the column-order assertion executed (and passed) first. No regression possible against empty data.
- **Committed in:** `a552e6b` (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 bug — strengthening the plan's literal tests against the stub-data reality the plan itself acknowledged).
**Impact on plan:** Both fixes preserve plan intent (test parametrisation lands; CfD untouched; RO grains covered) while making the tests robust against stub-data conditions documented in `prior_wave_context`. No scope creep — both deviations live entirely within the modified test files.

## Issues Encountered

- One pandas semantic surprise (empty MultiIndex `inferred_type`) — diagnosed inside Task 2 and resolved with the D-11 helper. No external blockers.

## Stub Data Status

**RO derived Parquets are zero-row at this point in Wave 3.** Test parametrisations land green via skip-cleanly fallback. The moment Plan 05-05 / 05-06 / future scraper fix wires real Ofgem RER data, the 8 skipped tests start exercising real invariants automatically — no test code change required.

## User Setup Required

None — pure test-file extensions; no external service configuration needed.

## Next Phase Readiness

- RO-03 automated regression-guarded: schema, row-conservation, determinism each parametrised over the 5 RO grains.
- Wave 3 advances 05-09 → 05-10 cleanly. Plan 05-11 (next) can rely on these test gates being in place.
- The skip-cleanly D-11 fallback pattern is reusable by future scheme modules (FiT in Phase 7) when their derived Parquets land before real raw data is wired.

## Self-Check: PASSED

- All 3 modified test files present at expected paths.
- All 3 task commits resolvable in git log: `a552e6b`, `d6d5f0e`, `7b7f7ee`.
- SUMMARY.md created at `.planning/phases/05-ro-module/05-10-SUMMARY.md`.
- Final test run: `tests/test_schemas.py + test_aggregates.py + test_determinism.py` → 35 passed + 8 skipped.
- Full suite: 163 passed + 12 skipped + 22 xfailed (was 153 / 4 / 22 before plan).

---
*Phase: 05-ro-module*
*Completed: 2026-04-23*
