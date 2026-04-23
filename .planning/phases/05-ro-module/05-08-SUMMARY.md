---
phase: 05-ro-module
plan: 08
subsystem: plotting
tags: [plotly, pandas, pyarrow, ro, lorenz, stacked-area, chart-builder]

requires:
  - phase: 05-ro-module
    provides: "schemes/ro/ module with 5 derived Parquet grains (station_month, annual_summary, by_technology, by_allocation_round, forward_projection) + DERIVED_DIR; manifest.py RO provenance registered; refresh_all.SCHEMES += ('ro', ro)"
provides:
  - "src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py — S2 4-panel flagship (generation TWh / ROC £/ROC + e-ROC sensitivity / premium £/MWh / cumulative £bn with mutualisation annotation on SY 2021-22)"
  - "src/uk_subsidy_tracker/plotting/subsidy/ro_by_technology.py — S3 2-panel stacked (annual bars + cumulative area) across 6 categories with D-10 biomass cofiring/dedicated split"
  - "src/uk_subsidy_tracker/plotting/subsidy/ro_concentration.py — S4 Lorenz curve on station-level lifetime RO cost with 50%/80% threshold markers + top-3 station callouts (GB-only per D-09/D-12)"
  - "src/uk_subsidy_tracker/plotting/subsidy/ro_forward_projection.py — S5 2-panel drawdown to 2037 by technology (no NESO-growth scenario; RO closed to new accreditations)"
  - "4 new chart-builder invocations registered in plotting/__main__.py orchestrator"
  - "Empty-upstream placeholder pattern: each RO chart emits a titled placeholder figure when data/derived/ro/*.parquet is empty, so `python -m uk_subsidy_tracker.plotting` succeeds under CI pre-Plan 05-13"
affects: [05-09-benchmarks, 05-10-themes-gallery, 05-11-ro-docs-page, 05-12-mkdocs-nav, 05-13-post-execution-review]

tech-stack:
  added: []
  patterns:
    - "Empty-parquet graceful degradation: _prepare() returns empty DataFrame, main() short-circuits to _placeholder() helper that emits a single-panel titled annotation figure via ChartBuilder.create_basic()"
    - "RO chart family colour convention: Offshore #1f77b4, Onshore #6baed6, Biomass dedicated #8c564b, Biomass cofiring #d62728, Solar PV #ff7f0e, Other #2ca02c (aligned across ro_by_technology and ro_forward_projection)"
    - "GB-only headline + NIRO-available-via-filter annotation (D-09/D-12 + T-5.08-02 mitigation) pinned in a paper-coordinate annotation on the top-left of every RO chart"

key-files:
  created:
    - "src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py (240 lines)"
    - "src/uk_subsidy_tracker/plotting/subsidy/ro_by_technology.py (196 lines)"
    - "src/uk_subsidy_tracker/plotting/subsidy/ro_concentration.py (183 lines)"
    - "src/uk_subsidy_tracker/plotting/subsidy/ro_forward_projection.py (178 lines)"
  modified:
    - "src/uk_subsidy_tracker/plotting/__main__.py (+11 lines: 4 import stanzas + 4 charts-list tuples + 1 section comment)"
    - "src/uk_subsidy_tracker/plotting/subsidy/__init__.py (previously empty; now carries package docstring documenting D-02 discipline for RO additions)"

key-decisions:
  - "Empty-upstream fallback pattern: each RO chart emits a placeholder figure when data/derived/ro/*.parquet is empty rather than raising (stub-data reality per prompt's prior_wave_context — Plan 05-13 regenerates after Ofgem RER URLs are plumbed)"
  - "Panel 2 of ro_dynamics shows a proxy £/ROC series (cost/rocs_issued) rather than re-reading raw roc-prices.csv — station_month.parquet does not carry buyout+recycle columns independently of the cost multiplicatively; proxy is generation-weighted and honest (label names the approximation)"
  - "ro_forward_projection drops the NESO-growth 2×2 layout to a single-column 2-panel chart (RO closed to new accreditations per SI 2017/1084; growth multiplier meaningless)"
  - "Station-id used as the Lorenz callout label in ro_concentration (station_month.parquet has no station_name column); Plan 05-13 post-execution review can enrich with Ofgem register station names if warranted"

patterns-established:
  - "D-02 'charts untouched' discipline: 4 new ro_*.py files alongside existing cfd_*.py modules; zero diff to CfD chart code"
  - "ChartBuilder empty-data graceful degradation: _placeholder() helper pattern for any future scheme whose upstream Parquet may be empty pre-publication"

requirements-completed: [RO-04]

duration: 5min
completed: 2026-04-23
---

# Phase 05 Plan 08: RO Charts (S2-S5) Summary

**Four RO chart modules (ro_dynamics, ro_by_technology, ro_concentration, ro_forward_projection) shipped with CfD-analog structure, RO-specific content (D-10 biomass split, D-11 mutualisation spike, D-12 GB-only headline), and empty-upstream placeholder fallback so the plotting orchestrator succeeds pre-Plan 05-13.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-04-23T05:55:13Z
- **Completed:** 2026-04-23T06:00:12Z
- **Tasks:** 2
- **Files created:** 4 (4 RO chart modules)
- **Files modified:** 2 (`plotting/__main__.py`, `plotting/subsidy/__init__.py`)

## Accomplishments

- **RO-04 closed.** The four RO charts specified in RO-MODULE-SPEC §3 + Appendix A are live with verbatim filenames (`subsidy_ro_dynamics_twitter.png`, `subsidy_ro_by_technology_twitter.png`, `subsidy_ro_concentration_twitter.png`, `subsidy_ro_forward_projection_twitter.png`).
- **End-to-end orchestrator clean.** `uv run python -m uk_subsidy_tracker.plotting` now emits 18 charts (14 prior + 4 new RO) with zero failures, even with `data/derived/ro/*.parquet` currently empty (placeholder fallback).
- **Phase 4 D-02 discipline preserved.** Zero modifications to CfD chart modules; the 3 `subsidy_cfd_*_twitter.png` files unchanged vs pre-plan baseline.
- **Zero regression.** 153 passed + 4 skipped — identical to pre-plan baseline; no test harness changes needed because chart modules are exercised only at `python -m uk_subsidy_tracker.plotting` time, not during pytest.
- **T-5.08-02 mitigation landed.** Every RO chart carries a "GB-only; NIRO rows via country='NI' filter" annotation in the top-left paper-coordinate slot, making the scope choice visible and the NIRO data discoverable.

## Task Commits

Each task was committed atomically:

1. **Task 1: ro_dynamics.py + ro_by_technology.py (S2 + S3)** — `9f75f13` (feat)
2. **Task 2: ro_concentration.py + ro_forward_projection.py + wire __main__** — `0703fde` (feat)

**Plan metadata:** `[pending — final commit]` (docs: complete plan)

## Files Created/Modified

### Created

- `src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py` — S2 4-panel flagship. Panels: [1] annual generation TWh (GB-only); [2] £/ROC with e-ROC sensitivity overlay per D-02; [3] premium £/MWh (red positive / green negative); [4] cumulative £bn with per-year mutualisation annotation when `mutualisation_gbp > 0` (D-11 verified scope: SY 2021-22 only).
- `src/uk_subsidy_tracker/plotting/subsidy/ro_by_technology.py` — S3 2-panel stacked. 6 categories (Offshore Wind, Onshore Wind, Biomass dedicated, Biomass cofiring, Solar PV, Other); D-10 biomass cofiring-vs-dedicated split surfaced in a paper-coordinate footnote.
- `src/uk_subsidy_tracker/plotting/subsidy/ro_concentration.py` — S4 Lorenz curve. GB-only stations; 50% + 80% threshold markers + top-3 station_id callouts; equality diagonal.
- `src/uk_subsidy_tracker/plotting/subsidy/ro_forward_projection.py` — S5 2-panel drawdown to 2037. Stacked annual bars by technology (colour convention mirrors ro_by_technology); cumulative £bn trace on panel 2; 2037 scheme-close vline on both panels.

### Modified

- `src/uk_subsidy_tracker/plotting/__main__.py` — 4 imports + 4 tuples in `charts` list; explanatory section comment `# RO subsidy economics (Plan 05-08)` above the new block.
- `src/uk_subsidy_tracker/plotting/subsidy/__init__.py` — previously empty; now carries package docstring citing D-02 discipline for RO additions.

## Decisions Made

- **Empty-upstream fallback over skip.** Plan's prompt flagged stub-data reality (`data/derived/ro/*.parquet` has zero rows on the committed seed state) and instructed charts to "emit safely on empty input — either produce a 'no data' placeholder PNG/HTML or skip gracefully". Chose placeholder over skip because the plotting orchestrator's per-chart try/except-with-summary contract assumes every chart attempts to save; skipping silently would hide the "no data yet" state. Placeholder carries the "Regenerate after Ofgem RER URLs are plumbed (Plan 05-13)" attribution so the empty chart is self-documenting rather than mysterious.
- **Panel 2 of ro_dynamics uses a proxy £/ROC series.** The `station_month.parquet` schema does not carry `buyout_gbp_per_roc` or `recycle_gbp_per_roc` as independent columns — they are embedded multiplicatively into `ro_cost_gbp`. The chart surfaces a generation-weighted proxy = `ro_cost_gbp / rocs_issued` for buyout+recycle, and `ro_cost_gbp_eroc / rocs_issued` for the e-ROC sensitivity. Labels name the series honestly ("buyout + recycle", "e-ROC sensitivity") rather than hiding the approximation. Plan 05-13 post-execution review can swap in a direct read of `roc-prices.csv` if higher fidelity is wanted.
- **`ro_forward_projection` drops the 2×2 growth-scenario layout.** RO closed to new accreditations 2017-03-31 (SI 2017/1084). The NESO demand-growth multiplier that `remaining_obligations.py` applies to CfD has no meaning for a closed scheme; dropping it collapses the chart from 2×2 to 2×1, eliminating irrelevant panels.
- **Top-3 station callouts use `station_id`** (not station name). `station_month.parquet` has no `station_name` column. Plan 05-13 can enrich with Ofgem register names if post-execution review warrants it.

## Deviations from Plan

None — plan executed exactly as written.

The plan's skeleton code for `ro_dynamics.py` (lines 134-214 of 05-08-PLAN.md) and `ro_by_technology.py` (lines 218-299) was prescriptive; deviations from the skeleton were limited to:

- Adding the empty-upstream `_placeholder()` fallback (flagged as required by the prompt's prior_wave_context and by the plan's implicit "stub seeds produce zero rows" reality).
- Wiring Panel 2 of ro_dynamics with a stacked (e-ROC on top of buyout+recycle) fill rather than a two-series no-fill overlay, making the "sensitivity band" more visually legible.
- Category colour-ordering in `ro_by_technology.CATEGORIES` adjusted so Offshore Wind sits at the bottom of the stack (largest-lifetime recipient first) — consistent with `cfd_payments_by_category`'s stacking convention.

None of these qualify as auto-fix deviations (Rule 1-4) — they are plan-internal implementation choices documented in the `key-decisions` frontmatter.

## Issues Encountered

None. Both tasks compiled and ran first-try:

- Task 1 verification (`uv run python -c "from ... import ro_dynamics, ro_by_technology"`) passed first run.
- Task 1 smoke-run (`ro_dynamics.main(); ro_by_technology.main()`) emitted 2×3=6 files (html/div.html/png) first run — placeholder path, as expected.
- Task 2 verification (all 4 imports + grep count ≥4 in `__main__.py`) passed first run.
- End-to-end `python -m uk_subsidy_tracker.plotting` emitted 18 OK lines (no ERR) first run.

## Known Stubs

The 4 new chart modules each include an `_placeholder()` helper that emits a titled single-panel annotation figure when the corresponding `data/derived/ro/*.parquet` is empty (file absent OR zero rows OR country='GB' filter returns empty). This is intentional and documented: it is the direct consequence of the Plan 05-01 Option-D stub-seed decision, which keeps the RO pipeline exercising end-to-end without real Ofgem data until Plan 05-13 plumbs the RER URLs.

When Plan 05-13 regenerates `data/derived/ro/*.parquet` from real Ofgem data, the `if len(df) == 0:` branch falls through and the charts render with real content. No additional code changes are needed — the stub path and the real-data path share the same `main()` entry.

| File | Stub pattern | Resolved by |
|------|--------------|-------------|
| `ro_dynamics.py` | `_placeholder()` branch on empty station_month.parquet | Plan 05-13 post-execution review |
| `ro_by_technology.py` | `_placeholder()` branch on empty by_technology.parquet | Plan 05-13 post-execution review |
| `ro_concentration.py` | `_placeholder()` branch on empty station_month.parquet | Plan 05-13 post-execution review |
| `ro_forward_projection.py` | `_placeholder()` branch on empty forward_projection.parquet | Plan 05-13 post-execution review |

## Threat Flags

None — the RO charts are read-only over `data/derived/ro/*.parquet` (trusted pipeline output; pandera-validated upstream in Plan 05-05) and write deterministically to `docs/charts/html/` (gitignored). No new network endpoints, auth paths, or file-access patterns. Plan's `<threat_model>` items T-5.08-01 (footer tampering via ChartBuilder) and T-5.08-02 (GB-only framing) are both mitigated as planned — ChartBuilder's "richardlyon.substack.com" footer is unmodified; GB-only filter + NIRO annotation landed on every RO chart.

## User Setup Required

None.

## Next Phase Readiness

- **RO-04 now closed.** Ready for Plan 05-09 (RO benchmark reconciliation against REF Constable 2025 Table 1).
- **`docs/schemes/ro.md` (Plan 05-11)** can safely reference any of the 4 emitted `subsidy_ro_*.div.html` embeds; the placeholder-mode charts render the "no data yet" message cleanly, so the docs page can be written before Plan 05-13 without visual breakage.
- **Theme gallery integration (Plan 05-10)** can reference the 4 RO chart filenames.
- **Plan 05-13 post-execution review** is the first point where real Ofgem data flows through the charts; expect follow-up polish on axis ranges, colour contrast, and top-3 Lorenz callouts once real station names + volumes are present.

## Self-Check: PASSED

Verified before this section was written:

- [x] `src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py` exists
- [x] `src/uk_subsidy_tracker/plotting/subsidy/ro_by_technology.py` exists
- [x] `src/uk_subsidy_tracker/plotting/subsidy/ro_concentration.py` exists
- [x] `src/uk_subsidy_tracker/plotting/subsidy/ro_forward_projection.py` exists
- [x] Commit `9f75f13` found in git log (Task 1)
- [x] Commit `0703fde` found in git log (Task 2)
- [x] `uv run python -m uk_subsidy_tracker.plotting` emits 4 `subsidy_ro_*_twitter.png` (verified: `ls .../docs/charts/html/subsidy_ro_*_twitter.png | wc -l` → 4)
- [x] 153 passed + 4 skipped (zero regression)
- [x] No deletions in either task commit (belt-and-braces check: `git diff --diff-filter=D --name-only HEAD~1 HEAD` → empty)

---

*Phase: 05-ro-module*
*Completed: 2026-04-23*
