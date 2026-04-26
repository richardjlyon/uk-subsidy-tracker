---
phase: 06-flagship-cross-scheme-charts
plan: 03
subsystem: plotting
tags: [portal, cross-scheme, plotly, x-charts, excluded-schemes, nan-guard]

# Dependency graph
requires:
  - phase: 06-flagship-cross-scheme-charts
    plan: 01
    provides: "data/derived/portal/cross_scheme.parquet (28 rows; cost_gbp/premium_gbp/generation_mwh columns); src/uk_subsidy_tracker/schemes/portal/__init__.py (DERIVED_DIR); src/uk_subsidy_tracker/plotting/colors.py::SCHEME_COLORS"
  - phase: 06-flagship-cross-scheme-charts
    plan: 02
    provides: "_prepare/_placeholder/main scaffold from portal/x1_stacked_total.py + portal/x2_cumulative_premium.py; orchestrator append pattern (3 imports + 3 tuples) at plotting/__main__.py"
provides:
  - "src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py — X4 chart (line per scheme); EXCLUDED_SCHEMES guard (D-16) armed for Phases 9-11; NaN-generation drop (HAZARD #2)"
  - "src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py — X5 chart (grouped bars 2021/2022/2023 per scheme); EXCLUDED_SCHEMES guard (D-16); CRISIS_YEARS chronological tuple per UI-SPEC Q4"
  - "6 chart artefacts in docs/charts/html/: x{4,5}_*_twitter.png + x{4,5}_*.html + x{4,5}_*.div.html (gitignored — regenerated)"
  - "plotting/__main__.py wiring — 2 portal-chart imports + 2 charts-list entries; orchestrator runs 23 charts (21 OK + 2 SKIP-dormant + 0 ERR)"
affects: [phase-06 plan 06-04 (Wave 4 docs/portal/ pages embed X4+X5 PNGs and divs); phase-9 (CM module — first scheme that triggers EXCLUDED_SCHEMES filter); phase-10 (Balancing); phase-11 (Grid)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "EXCLUDED_SCHEMES armed-but-no-op pattern: hardcoded frozenset of three Phase 9-11 schemes (Capacity Market, Balancing Services, Grid Socialisation); df = df[~df['scheme'].isin(EXCLUDED_SCHEMES)] is no-op in Phase 6 (those rows don't exist) but auto-engages when those schemes ship. Mirrored across X4 + X5 with the same identifier for grep-discoverability."
    - "NaN-generation guard at the per-row division boundary: df = df[df['generation_mwh'].notna() & (df['generation_mwh'] > 0)] — prevents inf/NaN bars when cost_gbp / generation_mwh would divide by zero (HAZARD #2 from cross_scheme schema; pre-SY18 RO years have NaN generation)."
    - "Chronological year-color emphasis pattern (X5): YEAR_COLORS dict maps each crisis year to a color; 2022 = red (#d62728 — crisis emphasis); 2021/2023 = subtitle-grey (#a0a4b8 — pre/post-crisis context). Plotly groups bars in trace-order, so iterating CRISIS_YEARS = (2021, 2022, 2023) preserves the chronological visual order required by UI-SPEC §'Open items for planner' Q4."

key-files:
  created:
    - "src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py (123 lines; _prepare + _placeholder + main; EXCLUDED_SCHEMES + NaN guard + cost_per_mwh derivation)"
    - "src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py (134 lines; _prepare + _placeholder + main; EXCLUDED_SCHEMES + CRISIS_YEARS + YEAR_COLORS + premium_per_mwh derivation)"
  modified:
    - "src/uk_subsidy_tracker/plotting/__main__.py (2 portal imports added after Wave 2's 3; 2 charts-list entries appended; comment-header REQUIREMENTS bumped X-01..X-03 → X-01..X-05)"

key-decisions:
  - "X4 + X5 subtitles collapsed to single source lines for verbatim grep-discoverability (mirrors Wave 2 X3 deviation #2). Rendered output unchanged — Plotly's subtitle.text accepts a single string; Python's compile-time literal concatenation is not visible to source-file grep."
  - "X5 uses local YEAR_COLORS dict rather than SCHEME_COLORS — bars are grouped by year (not by scheme), so the year-color encoding is the visual carrier of the 'crisis-year emphasis' contract per D-15. SCHEME_COLORS would have been wrong: scheme is the x-axis category, not the color dimension."
  - "X5 has 0 rows for 2024+ in the current cross_scheme.parquet (latest_fully_reconciled_year = 2023; CfD 2024 partial; RO 2024 cost = NaN), but the plan's CRISIS_YEARS = (2021, 2022, 2023) constrains the window to 2021-2023 anyway — no information lost."

patterns-established:
  - "X-chart copywriting verbatim discipline: chart title + chart subtitle text from UI-SPEC Copywriting Contract should live as single source lines (not split adjacent literals) so the plan's verbatim-grep acceptance criteria match the source as well as the rendered HTML. Established in Wave 2 (X3 deviation #2); now applied prophylactically in X4 + X5."
  - "Cross-scheme chart EXCLUDED_SCHEMES armed-future-no-op: any future X-chart that depends on a gas counterfactual (premium_gbp, cost_per_mwh, premium_per_mwh) hardcodes the same EXCLUDED_SCHEMES = frozenset({'Capacity Market', 'Balancing Services', 'Grid Socialisation'}) at module level + filters `df = df[~df['scheme'].isin(EXCLUDED_SCHEMES)]` in _prepare(). Phase 9-11 maintainers grep-discover the discipline."

requirements-completed: [X-04, X-05]

# Metrics
duration: 16min
completed: 2026-04-26
---

# Phase 6 Plan 06-03: Cross-Scheme Plotters X4 + X5 Summary

**Two flagship cross-scheme X-charts (X4 cost-per-MWh and X5 2022-crisis grouped-bars) ship as new modules under `plotting/portal/`; both honour D-16 (no-gas-counterfactual schemes excluded — armed for Phase 9-11 ship); both honour HAZARD #2 (NaN-generation row drop); orchestrator now runs 23 charts (21 OK + 2 SKIP + 0 ERR); pytest baseline preserved at 228 passed.**

## Performance

- **Duration:** ~16 min
- **Started:** 2026-04-26T01:44:46Z
- **Completed:** 2026-04-26T02:01:08Z
- **Tasks:** 2 (sequential, atomic commits)
- **Files modified:** 2 new src files + 1 modified orchestrator
- **Artefacts emitted:** 6 chart files in `docs/charts/html/` (2 × {PNG, HTML, div.html})

## Accomplishments

- **EXCLUDED_SCHEMES armed-future-no-op pattern.** Both X4 and X5 hardcode `EXCLUDED_SCHEMES = frozenset({"Capacity Market", "Balancing Services", "Grid Socialisation"})` and filter `df = df[~df["scheme"].isin(EXCLUDED_SCHEMES)]` in `_prepare()`. The filter is a no-op in Phase 6 (those rows don't exist in `cross_scheme.parquet`) but auto-engages when Phases 9-11 ship — Phase 9-11 maintainers grep-discover the discipline.
- **NaN-generation guard.** Both charts compute per-MWh quantities (`cost_per_mwh`, `premium_per_mwh`) by dividing by `generation_mwh`. Both `_prepare()` functions drop `generation_mwh.isna() | generation_mwh <= 0` rows before division — prevents inf/NaN bars when pre-SY18 RO rows have NaN generation (HAZARD #2 from `cross_scheme` schema).
- **Verbatim Copywriting Contract subtitles.** X4 ships `"Schemes without a gas counterfactual (CM, Balancing, Grid) excluded — see methodology."` and X5 ships `"2021 / 2022 / 2023 grouped bars; schemes without gas counterfactual excluded."` — both as single source lines for grep-discoverability.
- **X4 line chart with SCHEME_COLORS palette.** One trace per scheme (CfD blue `#1f77b4`, RO red `#d62728` — same palette as Wave 2's X1, X3); `lines+markers` mode; per-MWh hover format `£%{y:,.0f}/MWh`.
- **X5 grouped bars per D-15 + UI-SPEC Q4.** Three traces (one per crisis year); x-axis = scheme; `barmode="group"`; year-color emphasis (`YEAR_COLORS[2022] = #d62728` red for crisis-year, `YEAR_COLORS[2021]/2023 = #a0a4b8` subtitle-grey for context); chronological order preserved by iterating `CRISIS_YEARS = (2021, 2022, 2023)` in declaration order (Plotly groups bars in trace-order).
- **Graceful degradation.** Each chart's `main()` short-circuits to `_placeholder()` when `_prepare()` returns an empty DataFrame — keeps the orchestrator green on bootstrap-empty pipelines.
- **Orchestrator wiring.** `plotting/__main__.py` imports the two portal `main()` callables and appends them to the charts list; comment-header bumped from "REQUIREMENTS X-01..X-03" to "REQUIREMENTS X-01..X-05". End-to-end run reports 21 OK + 2 SKIP (dormant `ro_concentration` + `ro_forward_projection`) + 0 ERR for 23 charts processed.
- **Test suite green.** `uv run pytest tests/` reports 228 passed, 39 skipped, 13 xfailed — same baseline as Wave 1 + Wave 2; no regression.

## Task Commits

| # | Task | Hash | Type |
|---|------|------|------|
| 1 | Create `x4_cost_per_mwh.py` + `x5_2022_crisis.py` (EXCLUDED_SCHEMES + NaN guard + verbatim subtitles) | `d551839` | feat |
| 2 | Wire X4/X5 into `plotting/__main__.py` (2 imports + 2 charts-list entries; comment header bumped to X-01..X-05) | `110b341` | feat |

**Plan metadata commit:** [pending — final commit captures SUMMARY + STATE + ROADMAP]

## Confirmed Artefact Sizes

| Chart | PNG (twitter) | HTML | div.html |
|-------|---------------|------|----------|
| x4_cost_per_mwh | 204 KB | 4.8 MB | 3.1 KB |
| x5_2022_crisis | 151 KB | 4.8 MB | 3.0 KB |

All PNGs ≥ 5000 bytes (acceptance threshold); all HTML files ≥ 50 KB (Plotly bundle present); div.html files are slim by design (no embedded Plotly; uses `include_plotlyjs="cdn"`).

## Files Created/Modified

**Created (2):**

- `src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py` — X4 chart; `_prepare`/`_placeholder`/`main`; EXCLUDED_SCHEMES + NaN guard + cost_per_mwh derivation; SCHEME_COLORS palette
- `src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py` — X5 chart; `_prepare`/`_placeholder`/`main`; EXCLUDED_SCHEMES + CRISIS_YEARS + YEAR_COLORS + premium_per_mwh derivation

**Modified (1):**

- `src/uk_subsidy_tracker/plotting/__main__.py` — 2 portal imports added; 2 charts-list entries appended; comment-header REQUIREMENTS bumped from X-01..X-03 to X-01..X-05

## Decisions Made

1. **X4 + X5 subtitles as single source lines.** Initial draft used adjacent-literal concatenation (Python compile-time concat → correct rendered output) for the chart subtitles, but `grep` matches per-line — the verbatim-grep acceptance criterion fails. Collapsed both subtitles to single source lines. Rendered output unchanged. Mirrors Wave 2 X3 deviation #2 (same root cause; now applied prophylactically).
2. **X5 uses local YEAR_COLORS dict, not SCHEME_COLORS.** X5's bars are grouped by year (not by scheme — scheme is the x-axis category). The year-color encoding carries the "crisis-year emphasis" contract per D-15, which `SCHEME_COLORS` cannot serve. `YEAR_COLORS[2022] = "#d62728"` (red) emphasises 2022; `YEAR_COLORS[2021] / [2023] = "#a0a4b8"` (subtitle-grey) provide pre/post-crisis context.
3. **EXCLUDED_SCHEMES is no-op in Phase 6.** The cross_scheme.parquet currently contains only CfD + RO rows (Phase 9-11 schemes don't exist yet). The `df = df[~df["scheme"].isin(EXCLUDED_SCHEMES)]` filter is a guaranteed no-op today but auto-engages when Phase 9-11 ship; the methodology subtitle in both charts documents the exclusion explicitly so the discipline ships in code now (not as a backlog ticket).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] X4 + X5 subtitles split across literals fail verbatim-grep acceptance**

- **Found during:** Task 1 first acceptance verification grep.
- **Issue:** Initial draft wrote both X4 and X5 subtitles using adjacent-literal Python concatenation:
  ```python
  text=(
      "Schemes without a gas counterfactual "
      "(CM, Balancing, Grid) excluded — see methodology."
  ),
  ```
  Python compile-time concatenates these into the correct rendered string, but `grep -c "Schemes without a gas counterfactual (CM, Balancing, Grid) excluded — see methodology\." x4_cost_per_mwh.py` returns 0 because grep matches per line. The plan's acceptance criterion requires the verbatim subtitle to appear in the source file (so a future maintainer running `grep` from the Copywriting Contract finds the live source).
- **Fix:** Collapsed both subtitles to single source lines. Rendered output is byte-identical (verified by re-running the smoke tests; PNG + HTML + div.html re-emitted; HTML grep still finds the subtitle string once each).
- **Files modified:** `src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py`; `src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py`
- **Verification:** Source greps return 1 each; smoke-tests succeed.
- **Committed in:** `d551839` (Task 1 commit; both files committed together with the fix in place).

**2. [Rule 1 - Documentation] Title-verbatim grep returns >1 due to docstring + builder + figure**

- **Found during:** Task 1 acceptance verification.
- **Issue:** Plan acceptance criterion `grep -c "Cost per MWh of subsidised generation by scheme" returns 1` is contradicted by the natural shape of the chart files — the title appears in (a) the module docstring's wording, (b) the `ChartBuilder(title=...)` constructor, and (c) the `<b>...</b>` figure title. The title returns 3 matches in X4 and 2 in X5 (X5's docstring uses different wording). This is the **same shape** as Wave 2's X1/X2/X3 (whose acceptance criteria the plan author also wrote `returns 1` for, but which actually return 3 / 2 / 2 — Wave 2 shipped without flagging it).
- **Fix:** None — leaving the natural shape (`docstring describes what the chart is + ChartBuilder title + Plotly title text`). The criterion should have been "≥ 1" not "= 1"; the planner's intent was "the verbatim title from the Copywriting Contract appears in source" which is satisfied multiple-fold.
- **Files modified:** None.
- **Verification:** All three callsites in X4 (docstring, ChartBuilder, fig title) and both callsites in X5 (ChartBuilder, fig title) carry the verbatim Copywriting Contract title.
- **Committed in:** N/A (no code change — flagged here as a planning-doc concern; the Copywriting Contract verbatim discipline is satisfied multiple-fold).

---

**Total deviations:** 2 — 1 Rule 1 source-formatting bug (auto-fixed inline before commit), 1 plan-acceptance-criterion shape note (no code change needed).

**Impact on plan:** Minimal. Both deviations preserve the UI-SPEC visual contract and the Copywriting Contract verbatim discipline. The planning-doc concern (criterion #2 above) is non-actionable for this plan; flagged for future plan-author review.

## Threat Model Conformance

| Threat ID | Status | Evidence |
|-----------|--------|----------|
| T-06-03-01 (NaN-generation rows produce inf/NaN bars in X4) | mitigated | `_prepare()` in X4 + X5 both filter `df["generation_mwh"].notna() & (df["generation_mwh"] > 0)` before division. Source greps return ≥1 for both files. Pre-SY18 RO + 2024 RO (NaN cost) rows are silently excluded from the live data. |
| T-06-03-02 (info disclosure) | accepted | All numbers public from regulator data. |
| T-06-03-03 (X4/X5 silently omit Phase 9-11 schemes when they ship) | mitigated | Both charts hardcode `EXCLUDED_SCHEMES = frozenset({"Capacity Market", "Balancing Services", "Grid Socialisation"})` at module level + filter via `~df["scheme"].isin(EXCLUDED_SCHEMES)`. Subtitles document the exclusion explicitly per Copywriting Contract. Wave 4 docs/portal/ pages will cross-link to the methodology page. |
| T-06-03-04 (empty parquet DoS) | mitigated | Each `main()` short-circuits to `_placeholder()` when `_prepare()` returns empty DataFrame; orchestrator runs 0 ERR even on bootstrap-empty paths (mirrors Wave 2 pattern). |

## Issues Encountered

None blocking. One Rule 1 source-formatting bug documented above (auto-fixed inline).

## User Setup Required

None — no external service configuration required. Charts read the local `data/derived/portal/cross_scheme.parquet` produced by Wave 1.

## Next Phase Readiness

- **Wave 4 (Plan 06-04) docs/portal/ pages** can embed the 6 X4+X5 artefacts that exist on disk:
  - PNG: `docs/charts/html/x{4,5}_*_twitter.png` (Twitter cards, 1200×675)
  - HTML: `docs/charts/html/x{4,5}_*.html` (full-page interactive)
  - DIV: `docs/charts/html/x{4,5}_*.div.html` (markdown-embeddable; uses Plotly CDN)
  - Combined with Wave 2's 9 artefacts, the portal has a full set of 15 X-chart artefacts ready for embed.
- **Wave 5 (Plan 06-05) methodology page** should document the EXCLUDED_SCHEMES list (CM, Balancing, Grid) per X4 + X5 subtitles' "see methodology" cross-link. The list lives at module level in `x4_cost_per_mwh.py` + `x5_2022_crisis.py`; the methodology page should explain *why* those schemes can't have a gas counterfactual (CM = capacity-not-energy; Balancing = delta-only; Grid = TNUoS attribution best-effort).
- **Wave 6 (Plan 06-06) headline-sync regression test** can read `cross_scheme.parquet`'s per-MWh derivations (cost_gbp / generation_mwh; premium_gbp / generation_mwh) and reconcile against the X4/X5 chart axes via the same `_prepare()` helpers.
- **Phase 9 (CM module)** is the first scheme ship that triggers the EXCLUDED_SCHEMES filter — when CM lands a row in `cross_scheme.parquet` with `scheme="Capacity Market"`, X4 + X5 will silently exclude it. The methodology page documents this for hostile readers.

## Self-Check: PASSED

**Files created:**

- FOUND: src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py
- FOUND: src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py

**Files modified:**

- FOUND: src/uk_subsidy_tracker/plotting/__main__.py (with 2 new imports + 2 new charts-list entries; comment-header REQUIREMENTS bumped X-01..X-03 → X-01..X-05)

**Artefacts emitted (gitignored):**

- FOUND: docs/charts/html/x4_cost_per_mwh_twitter.png (204 KB)
- FOUND: docs/charts/html/x4_cost_per_mwh.html (4.8 MB)
- FOUND: docs/charts/html/x4_cost_per_mwh.div.html (3.1 KB)
- FOUND: docs/charts/html/x5_2022_crisis_twitter.png (151 KB)
- FOUND: docs/charts/html/x5_2022_crisis.html (4.8 MB)
- FOUND: docs/charts/html/x5_2022_crisis.div.html (3.0 KB)

**Commits:**

- FOUND: d551839 — Task 1 (X4 + X5 chart files)
- FOUND: 110b341 — Task 2 (orchestrator wiring)

**Verification:**

- FOUND: `uv run python -m uk_subsidy_tracker.plotting` exits 0 (21 OK + 2 SKIP + 0 ERR for 23 charts)
- FOUND: `uv run pytest tests/` exits 0 (228 passed, no regression)

---
*Phase: 06-flagship-cross-scheme-charts*
*Completed: 2026-04-26*
