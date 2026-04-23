---
phase: 05-ro-module
plan: 07
subsystem: infra
tags: [refresh-loop, manifest, schemes, ro, pytest, importlib, sidecar]

# Dependency graph
requires:
  - phase: 04-publishing-layer
    provides: "refresh_all.SCHEMES tuple + per-scheme dirty-check (D-18) + sidecar.write_sidecar() + Phase 4 Plan 07 refresh-loop invariant test pattern"
  - phase: 05-ro-module
    provides: "schemes/ro/_refresh.py::refresh/upstream_changed (Plan 05-05) + manifest.py multi-scheme iteration scaffolding (Plan 05-06)"
provides:
  - "SCHEMES tuple extended to ('cfd', cfd) + ('ro', ro) — refresh_all.main() now dirty-checks and refreshes both schemes"
  - "manifest.GRAIN_SOURCES/GRAIN_TITLES/GRAIN_DESCRIPTIONS populated for RO — manifest.build() emits Dataset entries for the five RO grains"
  - "test_refresh_loop.py pins the D-18 invariant for RO: after refresh(), upstream_changed()==False"
  - "test_refresh_loop.py pins the Plan 05-07 must_have truth: manifest.build() produces 10 Dataset entries across both schemes"
affects: [05-08, 05-09, 05-10, 05-11, 05-12, 05-13, 06, 07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "importlib submodule-shadow bypass for RO (mirrors Plan 04-07 CfD pattern; _refresh alias shadows submodule at package level)"
    - "Multi-scheme manifest provenance — per-(scheme, grain) GRAIN_SOURCES/TITLES/DESCRIPTIONS dicts fully populated for both schemes"

key-files:
  created: []
  modified:
    - "src/uk_subsidy_tracker/refresh_all.py — SCHEMES tuple gets ('ro', ro); import extended"
    - "src/uk_subsidy_tracker/publish/manifest.py — GRAIN_SOURCES/TITLES/DESCRIPTIONS extended with 'ro' sub-dicts"
    - "tests/test_refresh_loop.py — 2 new RO-invariant tests + shared tmp_ro_raw_tree fixture + _patched_ro_refresh_downloaders helper"

key-decisions:
  - "RO provenance maps mirror CfD narrowing exactly: by_allocation_round drops gas/balancing inputs; forward_projection is register-only — matches CfD Phase 4 pattern"
  - "Test 1 (test_ro_refresh_converges_on_unchanged_upstream) passes on first run because the invariant is already established by schemes/ro/_refresh.py::refresh() shipped in Plan 05-05; the test PINS the invariant algebraically"
  - "Rule 2 auto-fix: Plan 05-06 left manifest provenance dicts CfD-only; filling the RO half is a correctness requirement for the '10 Dataset entries' must_have truth"

patterns-established:
  - "RED phase for invariant-pinning tests: tests may pass on first commit if the invariant is already established by prior-plan code; the commit is still test(...) because it ADDS the invariant gate, not implementation"
  - "GREEN-phase Rule 2 auto-fix commits cite the RED commit hash in their body for cycle traceability (this plan: 86bf146 → 6bb38b7)"

requirements-completed: [RO-02, RO-03]

# Metrics
duration: 4min
completed: 2026-04-23
---

# Phase 05 Plan 07: Registering RO in refresh_all.SCHEMES Summary

**One-line SCHEMES append + manifest provenance population + 2 RO-invariant tests lock the end-to-end refresh → manifest path for RO (153 passed + 4 skipped, up from 151+4).**

## Performance

- **Duration:** 4 min (plan start 05:43:57Z → final commit 05:47:41Z wall, less the SUMMARY write)
- **Started:** 2026-04-23T05:43:57Z
- **Completed:** 2026-04-23T05:47:41Z
- **Tasks:** 2 executed (Task 1 atomic feat; Task 2 TDD RED→GREEN = 2 commits)
- **Files modified:** 3 (refresh_all.py, manifest.py, test_refresh_loop.py)
- **End-to-end refresh_all.main() runtime on clean-sidecar state:** 0.49s (both schemes short-circuit upstream-unchanged)

## Accomplishments

- `refresh_all.SCHEMES` now contains both `('cfd', cfd)` and `('ro', ro)`; `main()` iterates both with per-scheme D-18 dirty-check unchanged.
- Smoke-verified on the committed seed state: `refresh_all.main()` emits `[cfd] upstream unchanged — skipping refresh` and `[ro] upstream unchanged — skipping refresh` and exits 0 without rebuilding the manifest (exactly the Phase 4 Plan 07 short-circuit semantics).
- `manifest.GRAIN_SOURCES / GRAIN_TITLES / GRAIN_DESCRIPTIONS` now carry full `"ro"` sub-dicts — the multi-scheme iterator scaffolding added in Plan 05-06 now actually emits RO Dataset entries when `data/derived/ro/*.parquet` exists.
- `tests/test_refresh_loop.py` grew from 2 tests (CfD-only) to 4 (CfD + RO). The new tests pin:
  1. `test_ro_refresh_converges_on_unchanged_upstream` — after `ro_refresh.refresh()` rewrites sidecars, `upstream_changed()` returns False. This is the D-18 per-scheme invariant for RO.
  2. `test_manifest_includes_both_schemes_after_end_to_end_refresh` — `manifest.build()` produces exactly 10 Dataset entries (5 CfD + 5 RO) given a synthesised derived+raw tree covering both schemes. Pins the plan's core `must_have.truths` entry.
- Full test suite: **153 passed + 4 skipped** (was 151+4 pre-plan; +2 new RO tests, 0 regressions).

## Task Commits

Each task was committed atomically:

1. **Task 1: Append RO to refresh_all.SCHEMES** — `8b2fc1d` (feat)
2. **Task 2 RED: add RO refresh-loop invariant tests** — `86bf146` (test)
3. **Task 2 GREEN: register RO grains in manifest provenance maps** — `6bb38b7` (feat, Rule 2 auto-fix)

_Note: Task 2 is TDD per the plan's `tdd="true"` attribute; Test 1 passed on first commit because the invariant is already established by `schemes/ro/_refresh.py::refresh()` shipped in Plan 05-05, but Test 2 failed in RED with "grain ro.* not in GRAIN_SOURCES; skipping" warnings. The Rule 2 auto-fix (adding RO entries to the three provenance dicts) makes Test 2 pass — that is the GREEN gate for this plan._

## Files Created/Modified

- `src/uk_subsidy_tracker/refresh_all.py` — Import extended to `cfd, ro`; SCHEMES tuple gets `("ro", ro)` entry; comment updated to point at the next scheme (FiT/Phase 7) as the next append site.
- `src/uk_subsidy_tracker/publish/manifest.py` — `GRAIN_SOURCES["ro"]`, `GRAIN_TITLES["ro"]`, `GRAIN_DESCRIPTIONS["ro"]` sub-dicts added (51 lines). The RO provenance follows the same narrowing shape as CfD: `station_month`/`annual_summary`/`by_technology` carry all 5 inputs (3 Ofgem + gas-sap + system-prices); `by_allocation_round` drops gas/balancing; `forward_projection` is register-only.
- `tests/test_refresh_loop.py` — `ro_refresh` module import added at the top; `tmp_ro_raw_tree` fixture + `_patched_ro_refresh_downloaders` helper mirror the existing CfD infrastructure; `test_ro_refresh_converges_on_unchanged_upstream` and `test_manifest_includes_both_schemes_after_end_to_end_refresh` added below the existing CfD tests under a clearly-marked Plan-05-07 section divider.

## Decisions Made

- **Test file structure: extended in-place rather than split.** The plan didn't mandate a separate RO test file and the existing `test_refresh_loop.py` already houses the invariant gate for the refresh loop as a whole. Adding a clearly-marked section divider (`# Plan 05-07 — RO parallels`) keeps the two CfD tests and two RO tests grep-discoverable under a single file.
- **Rule 2 auto-fix was the GREEN gate.** Rather than splitting the manifest provenance population into a separate out-of-scope commit, we treated it as the GREEN gate for Test 2's RED failure. The plan's core must_have truth ("10 Dataset entries") could not be satisfied without this fix, so it lands inside the plan's atomic task commits with a clear commit body pointing at the RED hash.
- **`forward_projection` narrowed to register-only for RO.** CfD's `forward_projection` uses the portfolio-status CSV only (pure extrapolation off signed contracts). The RO analog uses `ro-register.xlsx` only — station accreditation register carries expected end dates per CONTEXT §"RO-specific `forward_projection.parquet`". This keeps the provenance narrowing shape symmetric across schemes.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Populated `manifest.GRAIN_SOURCES/TITLES/DESCRIPTIONS` for RO**
- **Found during:** Task 2 RED phase — `test_manifest_includes_both_schemes_after_end_to_end_refresh` failed with `AssertionError: RO: got []` and 5 `grain ro.* not in GRAIN_SOURCES; skipping` warnings.
- **Issue:** Plan 05-06 refactored `manifest.py` to iterate `schemes: Iterable[tuple[str, Any]]` and keyed `GRAIN_SOURCES/TITLES/DESCRIPTIONS` as `dict[scheme_name, dict[grain, ...]]`, but only populated the `"cfd"` sub-dicts. Without `"ro"` sub-dicts, `_build_dataset_entry` returns None for every RO grain and `manifest.datasets` contains zero RO entries — breaking the plan's must_have truth "manifest.json with 10 Dataset entries (5 CfD + 5 RO)".
- **Fix:** Added `"ro"` sub-dicts to all three provenance maps (51 lines). Provenance shape mirrors CfD: station-level / annual / by-technology grains carry all 5 inputs (3 Ofgem + gas-sap + system-prices for the counterfactual premium column); by_allocation_round drops gas/balancing; forward_projection is register-only.
- **Files modified:** `src/uk_subsidy_tracker/publish/manifest.py`
- **Verification:** `tests/test_refresh_loop.py::test_manifest_includes_both_schemes_after_end_to_end_refresh` passes; full suite 153 passed + 4 skipped (was 151+4 pre-plan).
- **Committed in:** 6bb38b7 (GREEN phase of Task 2)

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** The Rule 2 auto-fix was a pre-condition for the plan's core must_have truth being satisfiable — not scope creep. Without it, Plan 05-06's multi-scheme iteration scaffolding would remain inert for RO and the end-to-end refresh → manifest path would silently produce a CfD-only manifest.json (5 datasets instead of 10). The fix is within the `src/uk_subsidy_tracker/publish/manifest.py` MOD surface that Plan 05-06's PATTERNS mapping already flagged as requiring population (line 858 of 05-PATTERNS.md: "Without this refactor, RO grains silently fail to publish to site/data/manifest.json"). Landing here closes the loop.

## Issues Encountered

None. Task 1 was a literal one-line append as the plan described. Task 2 followed the TDD RED→GREEN cycle cleanly: Test 1 passed on first commit (invariant already established by 05-05), Test 2 surfaced the missing RO manifest entries in RED, the Rule 2 fix in GREEN made it pass. Full test suite jumped from 151+4 to 153+4 with zero regressions.

## TDD Gate Compliance

Task 2 is marked `tdd="true"` in the plan. Gate sequence in git log:

1. RED gate: `86bf146 test(05-07): add RO refresh-loop invariant tests (RED)` — Test 2 failed in RED with clear diagnostic output (grain ro.* not in GRAIN_SOURCES).
2. GREEN gate: `6bb38b7 feat(05-07): register RO grains in manifest provenance maps (GREEN)` — Test 2 passes post-fix.

No REFACTOR gate needed — the fix is literal dict-literal population with no duplication pressure.

## Known Stubs

None introduced in this plan. The Option-D stubs in `data/raw/ofgem/*.csv,.xlsx` remain from Plan 05-01 (resolved in Plan 05-13); this plan's test fixtures use `tmp_path` synthesis and do not depend on the real raw data state.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 05-08 (RO chart files) can proceed: `refresh_all.py` + `manifest.py` are now fully wired for RO and will auto-publish any grains that appear under `data/derived/ro/` once real Ofgem data lands in Plan 05-13.
- `manifest.build()` will emit 10 Dataset entries (5 CfD + 5 RO) as soon as `data/derived/ro/*.parquet` is rebuilt from non-stub raw data.
- RO refresh-loop invariant is algebraically pinned — any future refactor of `schemes/ro/_refresh.py` that breaks the "refresh() → upstream_changed() == False" contract will trip `test_ro_refresh_converges_on_unchanged_upstream`.

## Self-Check: PASSED

Files verified present:
- `.planning/phases/05-ro-module/05-07-SUMMARY.md` ✓
- `src/uk_subsidy_tracker/refresh_all.py` ✓
- `src/uk_subsidy_tracker/publish/manifest.py` ✓
- `tests/test_refresh_loop.py` ✓

Commits verified present on branch:
- `8b2fc1d` — feat(05-07): register RO in refresh_all.SCHEMES ✓
- `86bf146` — test(05-07): add RO refresh-loop invariant tests (RED) ✓
- `6bb38b7` — feat(05-07): register RO grains in manifest provenance maps (GREEN) ✓

Test gate verified: `uv run pytest tests/ -q` → 153 passed + 4 skipped (was 151+4 pre-plan; +2 new RO tests; no regressions).

---
*Phase: 05-ro-module*
*Completed: 2026-04-23*
