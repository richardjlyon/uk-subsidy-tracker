---
phase: 05-ro-module
plan: 09
subsystem: testing
tags: [pytest, pydantic, yaml, benchmarks, ref-constable, ro, xfail-sentinel]

# Dependency graph
requires:
  - phase: 02-test-benchmark-scaffolding
    provides: "BenchmarkEntry + Benchmarks Pydantic models; load_benchmarks() with source-key injection; _TOLERANCE_BY_SOURCE dispatch; per-source tolerance constants idiom"
  - phase: 05-ro-module
    provides: "schemes/ro/ §6.1 module (Plan 05-05); DERIVED_DIR + rebuild_derived(); RoStationMonthRow/RoAnnualSummaryRow schemas (Plan 05-03); refresh_all.SCHEMES registration (Plan 05-07); RO chart modules (Plan 05-08)"

provides:
  - "REF Constable 2025 Table 1 benchmark anchor (22 entries SY 2002-03 to 2023-24) transcribed into tests/fixtures/benchmarks.yaml::ref_constable with audit header (URL, retrieved_on, basis, scope alignment, tolerance)"
  - "Benchmarks.ref_constable Pydantic list field + BenchmarkEntry.year lower bound relaxed from ge=2015 to ge=2002 (admits RO 2002-start)"
  - "REF_TOLERANCE_PCT = 3.0 module constant + _TOLERANCE_BY_SOURCE dispatch entry ('ref_constable' -> REF_TOLERANCE_PCT)"
  - "ro_annual_totals_gbp_bn module-scoped fixture (reads data/derived/ro/station_month.parquet, GB filter, CY groupby, £bn dict; returns {} on empty/missing Parquet)"
  - "test_ref_constable_ro_reconciliation parametrised test (22 REF years; D-14 hard block at ±3% with xfail-via-sentinel escape hatch) + full D-14 three-step diagnostic ladder in failure message"
  - ".planning/phases/05-ro-module/05-09-DIVERGENCE.md sentinel documenting the Plan 05-01 Option-D zero-row state for Plan 05-13 Task 4 review"

affects: [06-portal, 07-fit-module, 13 (all downstream benchmark work inherits the ref_constable pattern)]

# Tech tracking
tech-stack:
  added: []  # no new libraries; reuses pytest + pydantic + pyyaml + pyarrow already in place
  patterns:
    - "xfail-via-sentinel escape hatch for D-14 hard-block tests under unattended execution — file-existence gate allows Phase chains to complete without silently deleting/lowering the discipline"
    - "Two-class divergence reporting in DIVERGENCE.md: data-absence (N/A per-year entries, zero-row Parquet) vs methodological (actual per-year £bn values computed, ±N% divergence) — distinguished at ladder Step-0 before D-14 scope/banding/carbon diagnosis"
    - "Per-source tolerance extensibility: _TOLERANCE_BY_SOURCE dispatch grown to 6 sources; new anchors plug in with one tolerance constant + one dict entry + (optional) dedicated test if harder-than-D-11-fallback"

key-files:
  created:
    - ".planning/phases/05-ro-module/05-09-DIVERGENCE.md"
    - ".planning/phases/05-ro-module/05-09-SUMMARY.md"
  modified:
    - "tests/fixtures/benchmarks.yaml"
    - "tests/fixtures/__init__.py"
    - "tests/test_benchmarks.py"

key-decisions:
  - "Pre-emptively authored 05-09-DIVERGENCE.md in the same commit as the REF reconciliation test because RO raw Ofgem data flows from Plan 05-01 Option-D stubs (zero-row Parquet); divergence class is data-absence, not methodological; Plan 05-13 Task 4 is the authored resolution gate"
  - "Classified the observed divergence explicitly as 'data-absence' (not methodological) to prevent Plan 05-13 reviewer from wasting effort on the D-14 diagnostic ladder (REF scope / banding / carbon-price extension) when the root cause is the absence of any station-month rows"
  - "Excluded ref_constable from Benchmarks.all_external_entries() — REF has its own dedicated hard-block test (test_ref_constable_ro_reconciliation) rather than riding the D-11 fallback parametrisation (test_external_benchmark_within_tolerance). Prevents the wrong tolerance-dispatch-key semantics"
  - "Relaxed BenchmarkEntry.year lower bound once (ge=2002) rather than gating per-source — minimal blast radius, all existing entries >=2015 unaffected, RO 2002-start admitted for the single source that needs it"

patterns-established:
  - "D-14 hard-block + sentinel-file escape hatch: tests that represent binary ROADMAP success criteria should fail loud by default but expose a file-existence escape hatch (xfail strict=False) that allows unattended chains to complete while documenting the divergence event for post-execution human review"
  - "DIVERGENCE.md structure: executive summary -> observed divergence (per-year table) -> root cause with commands -> D-14 classification (data-absence vs methodological) -> three-option remediation (recommended / fallback / forbidden) -> re-arm verification bash block with explicit assertion"
  - "Per-entry tolerance_pct field preserved on every BenchmarkEntry (even when _TOLERANCE_BY_SOURCE overrides at dispatch) so YAML readers can audit per-row tolerance intent"

requirements-completed: [RO-06]  # Sentinel-gated — re-arms once Plan 05-13 lands non-stub Ofgem data

# Metrics
duration: 5min
completed: 2026-04-23
---

# Phase 5 Plan 09: REF Constable Reconciliation Test Summary

**22-year REF Constable 2025 Table 1 anchor transcribed + parametrised RO reconciliation test with D-14 hard-block discipline and sentinel-file xfail escape hatch — RO-06 gate wired, tested, and bookmarked for Plan 05-13 resolution**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-23T06:05:17Z
- **Completed:** 2026-04-23T06:11:07Z
- **Tasks:** 2 (both `type="auto"`, Task 2 `tdd="true"`)
- **Files modified:** 3 (benchmarks.yaml, tests/fixtures/__init__.py, tests/test_benchmarks.py)
- **Files created:** 1 (05-09-DIVERGENCE.md sentinel)

## Accomplishments

- **REF Constable 2025 Table 1 landed as primary RO benchmark anchor.** 22 entries SY 2002-03 through SY 2023-24 (verbatim from 05-RESEARCH.md §5 lines 1101-1122), each carrying per-entry tolerance_pct: 3.0, REF PDF URL, retrieved_on 2026-04-22, SY notes (scheme launch, ROADMAP SC #3 window anchors, D-11 mutualisation year, series end). Audit header documents D-13/D-14 posture, REF basis (SY April-March, £bn nominal, GB-only, includes cofiring + mutualisation, excludes NIRO), CY-vs-SY tolerance alignment note, and Turver SY21 ~6% delta explanation (Turver reports £6.8bn vs REF £6.4bn because Turver snapshots later Ofgem Annual Report).
- **Pydantic model extensions.** `Benchmarks.ref_constable: list[BenchmarkEntry]` list field added (default empty); `BenchmarkEntry.year` lower bound relaxed from `ge=2015` to `ge=2002` (admits the RO 2002-start). `all_external_entries()` deliberately excludes `ref_constable` — REF has its own dedicated hard-block test, not D-11 fallback.
- **REF_TOLERANCE_PCT = 3.0** module constant declared in `tests/test_benchmarks.py` with D-14 docstring (three-step diagnostic ladder: REF scope / banding / carbon-price extension); `_TOLERANCE_BY_SOURCE` dispatch grown to 6 sources with `"ref_constable": REF_TOLERANCE_PCT`.
- **Parametrised reconciliation test** (`test_ref_constable_ro_reconciliation`) — 22 cases (one per REF-transcribed year 2002-2023) with `ro_annual_totals_gbp_bn` module-scoped fixture (reads `data/derived/ro/station_month.parquet`, filters to `country='GB'` per D-12, groups by `month_end.dt.year` per D-07 CY primary axis, sums `ro_cost_gbp`, returns £bn dict). Fixture returns `{}` on missing/empty Parquet so the test body raises through the D-14 diagnostic path (not silent skip).
- **05-09-DIVERGENCE.md sentinel authored** documenting the data-absence divergence class caused by Plan 05-01 Option-D fallback (ro-register.csv absent; ro-generation.csv 72-byte header-only stub; station_month.parquet zero-row). Per-year table (all 22 REF years, pipeline = "no data"), root-cause commands, D-14 ladder classification (data-absence, NOT methodological), three-option remediation (recommended / fallback / forbidden), and re-arm verification bash block. Plan 05-13 Task 4 is the authored resolution gate.
- **Test suite: 153 passed + 4 skipped + 22 xfailed** (was 153 + 4 skipped + 0). Zero regressions; the 22 xfails are the REF parametrisations activated by the sentinel-file gate. Hard block re-arms automatically when the sentinel is deleted after Plan 05-13 produces non-stub data.

## Task Commits

Each task was committed atomically:

1. **Task 1: Transcribe REF Constable Table 1 + extend Pydantic Benchmarks model** — `21b3438` (feat)
2. **Task 2: REF_TOLERANCE_PCT + fixture + parametrised reconciliation test + DIVERGENCE sentinel** — `1153fcc` (test)

**Plan metadata commit:** _pending_ (will include this SUMMARY.md, STATE.md, ROADMAP.md).

## Files Created/Modified

- `tests/fixtures/benchmarks.yaml` — Added `ref_constable:` section with 22 entries (SY 2002-23) + audit header (D-13/D-14 posture, REF URL + retrieved_on, basis, scope alignment, Turver note, unattended-execution sentinel pointer). Added master header note declaring REF primary-anchor status.
- `tests/fixtures/__init__.py` — Added `Benchmarks.ref_constable` list field with D-13 inline comment; updated `all_external_entries()` docstring to explain exclusion of REF (dedicated hard-block test); relaxed `BenchmarkEntry.year` lower bound from `ge=2015` to `ge=2002` with D-13 comment.
- `tests/test_benchmarks.py` — Added `from uk_subsidy_tracker import PROJECT_ROOT` import; added `REF_TOLERANCE_PCT = 3.0` constant with D-14 docstring (three-step diagnostic ladder); added `"ref_constable": REF_TOLERANCE_PCT` to `_TOLERANCE_BY_SOURCE`; added `ro_annual_totals_gbp_bn` module-scoped fixture (CY/GB aggregation with empty-Parquet short-circuits); added `_ref_entries()` collection-time collector; added `_DIVERGENCE_SENTINEL` constant; added `test_ref_constable_ro_reconciliation` parametrised test (22 cases, xfail-via-sentinel, D-14 diagnostic failure message).
- `.planning/phases/05-ro-module/05-09-DIVERGENCE.md` — NEW. Full sentinel-file contents: executive summary, per-year divergence table (22 REF years all "no data"), root cause + verification commands, D-14 ladder classification, three-option remediation, re-arm verification bash block, cross-references.

## Decisions Made

- **Pre-emptive DIVERGENCE.md authoring.** The plan authorises the executor to write `05-09-DIVERGENCE.md` if divergence exceeds 3% during Plan 09 execution. Because RO raw data flows from Plan 05-01 Option-D stubs (ro-register.csv absent; ro-generation.csv 72-byte header), `station_month.parquet` emits zero rows and every REF-year parametrisation fails with "Pipeline has no data". This IS divergence per the plan's broader definition (the test cannot complete its ±3% check). Authored the sentinel same-commit as the test and committed both together — matches the plan's `<action>` directive "Commit this file in the same commit as the reconciliation test".
- **Data-absence vs methodological divergence distinction.** DIVERGENCE.md explicitly classifies the observed state as data-absence (not banding error, not REF scope mismatch, not carbon-price extension regression) so Plan 05-13 Task 4 reviewer does not waste effort on the D-14 methodological ladder. The three D-14 categories become N/A when there is no pipeline output to compare against.
- **REF excluded from `all_external_entries()`.** The existing `test_external_benchmark_within_tolerance` parametrised test uses `_TOLERANCE_BY_SOURCE.get(entry.source, entry.tolerance_pct)` dispatch but its tolerance semantics (D-11 fallback, D-07 CHANGES.md bump for drift) differ from REF's hard-block stance. Rather than special-casing REF inside that test, REF gets its own parametrised test with matching semantics. `all_external_entries()` docstring explicitly documents the exclusion.
- **Single-line BenchmarkEntry.year Field relaxation.** Could have subclassed `BenchmarkEntry` or added a per-source validator to allow only REF entries pre-2015. Rejected — minimal blast radius preferred; all existing entries are >=2015 so no existing validation behaviour is reduced. Single-line change with inline comment citing D-13.

## Deviations from Plan

None - plan executed exactly as written.

The plan explicitly anticipated the Plan 05-01 Option-D stub state and pre-authored the xfail-via-sentinel escape hatch with `<action>`-block instructions for the executor to write `05-09-DIVERGENCE.md` in-same-commit when divergence is detected. Both tasks executed per plan text; no Rule 1/2/3 auto-fixes were needed; no Rule 4 architectural escalation; no scope creep.

The one mild judgment call was classifying the observed stub-data zero-row state as "divergence" for DIVERGENCE.md purposes. The plan's `<action>` block phrases the trigger as "divergence >3%", but the deeper semantic is "the test cannot complete its reconciliation check". Under zero-data conditions the per-year check raises before the ±3% comparison runs at all — which matches the plan's intent to document-and-continue for Plan 05-13 Task 4 review rather than stop the Phase 5 unattended chain.

## Issues Encountered

- **pyarrow timestamp vs python date handling in the RO fixture.** `RoStationMonthRow.month_end` is typed as `datetime.date` but pyarrow may return either a date object or a timestamp depending on Parquet round-trip. Defensive fix in the fixture: `gb["cy"] = pd.to_datetime(gb["month_end"]).dt.year` normalises through pandas datetime before `.dt.year` access. Not a bug fix (the code path isn't exercised under stub conditions since the fixture returns {} first), but future-proofs the fixture for Plan 05-13 real-data conditions.
- No other issues.

## User Setup Required

None - no external service configuration required.

The Plan 05-13 Task 4 reviewer should:
1. Verify `data/derived/ro/station_month.parquet` is non-empty post-Ofgem-RER-data-landing.
2. Delete `.planning/phases/05-ro-module/05-09-DIVERGENCE.md`.
3. Re-run `uv run pytest tests/test_benchmarks.py -q -k ref_constable`.
4. Expected: 22 REF years pass within ±3%.
5. If any REF year fails: do NOT recreate the sentinel — follow D-14 diagnostic ladder (REF scope / banding / carbon-price extension) per 05-CONTEXT.md.

Full re-arm instructions in `.planning/phases/05-ro-module/05-09-DIVERGENCE.md` § "Re-arm verification".

## Next Phase Readiness

Within Phase 5:
- **Plan 05-10** (Phase 5 docs/schemes/ro.md) is unblocked next — RO-06 is the last gating item before documentation lands.
- **Plan 05-11** (theme-gallery cross-links) unblocked.
- **Plan 05-12** (Phase-exit verification) remains — REF reconciliation xfail visibility is the explicit signal that Plan 05-13 Task 4 is the phase-exit human-review gate, not a silent skip.
- **Plan 05-13** (Post-Execution Human Review) now carries an explicit 05-09-DIVERGENCE.md input into Task 4 review scope, matching the plan's authored handoff.

Beyond Phase 5:
- **Phase 07 (FiT module)** inherits the `_TOLERANCE_BY_SOURCE` extensibility pattern and the D-14-with-sentinel hard-block idiom for any FIT benchmark anchors that carry binary ROADMAP gates.
- **Phase 06 (Portal)** inherits the master header's "primary anchor" pattern (clear designation of ONE primary benchmark per scheme, peer anchors cited in prose but not used for binary gating).

## Self-Check

**Claimed files exist:**
- tests/fixtures/benchmarks.yaml — FOUND (modified)
- tests/fixtures/__init__.py — FOUND (modified)
- tests/test_benchmarks.py — FOUND (modified)
- .planning/phases/05-ro-module/05-09-DIVERGENCE.md — FOUND (created)

**Claimed commits exist:**
- 21b3438 (Task 1 feat) — FOUND
- 1153fcc (Task 2 test) — FOUND

**Claimed test results:**
- Full suite: 153 passed + 4 skipped + 22 xfailed — VERIFIED
- ref_constable parametrisation: 22 xfailed — VERIFIED
- Plan-specified verify checks (REF_TOLERANCE_PCT >=2; ref_constable in yaml >=1; REF entries >=12): all PASS (4, 1, 22) — VERIFIED

## Self-Check: PASSED

---
*Phase: 05-ro-module*
*Completed: 2026-04-23*
