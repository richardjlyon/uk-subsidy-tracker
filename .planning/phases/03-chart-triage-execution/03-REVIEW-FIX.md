---
phase: 03-chart-triage-execution
fixed_at: 2026-04-22T00:00:00Z
review_path: .planning/phases/03-chart-triage-execution/03-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 8
skipped: 0
status: all_fixed
---

# Phase 03: Code Review Fix Report

**Fixed at:** 2026-04-22T00:00:00Z
**Source review:** `.planning/phases/03-chart-triage-execution/03-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 8 (0 Critical, 8 Warning; 11 Info out of scope)
- Fixed: 8
- Skipped: 0

All eight Warning-severity findings were addressed. No Critical findings.
Verification: `uv run pytest -q` (23 passed, 4 skipped) and
`uv run mkdocs build --strict` (clean build) after each Python/docs
change. YAML validated with `yaml.safe_load` for the CI workflow edit.

## Fixed Issues

### WR-01 / WR-02: Cumulative-premium figure inconsistency across cost pages and methodology

**Files modified:**
`docs/themes/cost/cfd-vs-gas-cost.md`,
`docs/themes/cost/cfd-dynamics.md`,
`docs/methodology/gas-counterfactual.md`
**Commit:** `e5582fa`
**Applied fix:** Re-computed the authoritative Jan 2018 – Apr 2026
cumulative premium from the live code
(`compute_counterfactual()` + LCCC dataset):

- Row-level decomposition (`wholesale + levy − gas`): **£14.12bn**
- Daily fleet-weighted aggregation (panel [4] of the dynamics chart):
  **£14.00bn**
- Full LCCC-window CfD cost: **£29.1bn**

Reconciled the three pages:

- `cfd-vs-gas-cost.md:25-26` — updated headline table Gas alternative
  **£14.3bn → £14.4bn** and Premium **£14.2bn → £14.1bn**; tightened
  the 2016–17 footnote from £29.2bn/£0.7bn to **£29.1bn / ~£0.6bn**.
- `cfd-vs-gas-cost.md:117` — replaced standalone **£14.9bn** with
  **£14.1bn** scoped explicitly to the Jan 2018 – Apr 2026 window.
- `cfd-vs-gas-cost.md:152-156` — refreshed the sensitivity paragraph
  and linked to the gas-counterfactual sensitivity table as the single
  source of truth.
- `cfd-dynamics.md:33` — updated **£14.1bn → £14.0bn** (matching the
  chart's own rendered subtitle) and added a one-sentence cross-link
  explaining why the row-level page reports £14.1bn.
- `gas-counterfactual.md:60-85` — full sensitivity table refreshed
  against current code: default gas £14.4bn / premium £14.1bn (was
  £14.3 / £14.9); all other scenario rows recomputed from the live
  `compute_counterfactual(...)` overrides. Window explicitly labelled
  Jan 2018 – Apr 2026 against £28.5bn CfD cost, with a standalone
  paragraph documenting the £29.1bn full-window headline.

### WR-03: AR3 / "above UK ETS" claim unsupported by the rendered chart

**Files modified:**
`docs/themes/efficiency/index.md`,
`docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md`
**Commit:** `6d54ea2`
**Applied fix:** Softened both pages to attribute the "above UK ETS"
observation to the plotted rounds (Investment Contracts, AR1, AR2)
only, acknowledging AR3–AR6 are omitted pending sufficient generation
history. The detail-page headline now reads *"the plotted rounds
(Investment Contracts, AR1, AR2) already sit well above the UK ETS
ceiling"* which is a chart-readable claim.

### WR-04: Colour labelling for AR1-wind levy contradicts between pages

**Files modified:** `docs/themes/cannibalisation/methodology.md`
**Commit:** `f040d66`
**Applied fix:** Ground-truthed against
`src/uk_subsidy_tracker/plotting/cannibalisation/capture_ratio.py:137-138`:
positive levy is `#1f77b4` (blue), negative is `#2ca02c` (green).
`capture-ratio.md` was already correct; `methodology.md` said "red"
for consumer top-up. Updated methodology.md to match the chart.

### WR-05: Stale Phase-3 status paragraph on the homepage

**Files modified:** `docs/index.md`
**Commit:** `c94bce8`
**Applied fix:** Replaced the "three charts above / not yet
documented" paragraph with the post-Phase-3 status: all five themes
published with their flagship charts and methodology pages.

### WR-06: `compute_counterfactual_monthly` silently drops `non_fuel_opex_per_mwh` override

**Files modified:** `src/uk_subsidy_tracker/counterfactual.py`
**Commit:** `6c78ce3`
**Applied fix:** Added `non_fuel_opex_per_mwh: float = DEFAULT_NON_FUEL_OPEX`
kwarg to `compute_counterfactual_monthly`, forwarded it to the daily
`compute_counterfactual` call, and documented the passthrough in the
docstring. Monthly and daily wrappers now share an identical keyword
contract.

### WR-07: `plotting/__main__.py` executes at import time

**Files modified:** `src/uk_subsidy_tracker/plotting/__main__.py`
**Commit:** `d4f7f4e`
**Applied fix:** Wrapped the 14 chart-generation calls in a `main()`
function guarded by `if __name__ == "__main__":`. Also wrapped each
chart call in a `try/except` that collects failures and reports them
via a single `SystemExit` at the end — CI now shows every failing
chart, not just the first one. Verified
`import uk_subsidy_tracker.plotting.__main__` does not trigger chart
regeneration.

### WR-08: CI `docs` job does not depend on `test` job

**Files modified:** `.github/workflows/ci.yml`
**Commit:** `b967f08`
**Applied fix:** Added `needs: test` to the `docs` job. Broken tests
now block the docs build, removing the "green docs / red tests"
ambiguity on PR status. YAML validated via `yaml.safe_load`.

---

_Fixed: 2026-04-22T00:00:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
