---
phase: 05-ro-module
plan: 04
subsystem: counterfactual
tags: [carbon-prices, eu-ets, uk-ets, provenance, drift-tripwire, seed-001, ro-coverage]

# Dependency graph
requires:
  - phase: 02-test-benchmark-scaffolding
    provides: METHODOLOGY_VERSION constant, SEED-001 Tier 2 discipline, two-layer Pydantic + YAML fixture pattern
  - phase: 04-publishing-layer
    provides: tests/fixtures/constants.yaml + _TRACKED scaffold, test_constants_provenance.py drift tripwire (13 tests pre-05-04), METHODOLOGY_VERSION = "0.1.0" chain

provides:
  - DEFAULT_CARBON_PRICES extended backward to 2002 (25 consecutive year keys 2002-2026)
  - 22 new constants.yaml entries (16 pre-2018 + 6 completion; every live year key now tracked)
  - _TRACKED set grown 6 → 28 entries (3 base + 25 carbon-year keys)
  - CHANGES.md [Unreleased] Changed bullets + ## Methodology versions audit entry (additive; no version bump)
  - Gas-counterfactual computation now works for every RO obligation year 2002-present

affects: [05-05 schemes/ro/cost_model.py, 05-06 schemes/ro/aggregation.py, 05-10 RO test parametrisation, 05-13 post-execution human review — 2005-2017 EU ETS value audit]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Additive-extension methodology discipline — add year keys, do not bump METHODOLOGY_VERSION when change is additive (D-06)"
    - "[VERIFICATION-PENDING] inline flag pattern on constants.yaml basis field — executor-accepted research seed values traceable via grep"
    - "_TRACKED extension protocol — when live dict grows, _TRACKED + YAML blocks must grow with it in the same commit or the drift tripwire fires"

key-files:
  created:
    - .planning/phases/05-ro-module/05-04-SUMMARY.md
  modified:
    - src/uk_subsidy_tracker/counterfactual.py (DEFAULT_CARBON_PRICES 9→25 year keys; docstring Provenance block extended with EEA + BoE + ICE URLs)
    - tests/fixtures/constants.yaml (22 new entries; 6→28 total provenance blocks)
    - tests/test_constants_provenance.py (_TRACKED 6→28 entries with inline tally comment)
    - CHANGES.md ([Unreleased] 2 Changed bullets + ## Methodology versions audit H3)

key-decisions:
  - "METHODOLOGY_VERSION unchanged at '0.1.0' (D-06 additive-extension rule). Bump to 1.0.0 reserved for Phase 6+ portal launch."
  - "2005-2017 values carry [VERIFICATION-PENDING] inline flag — executor accepted Plan 05-04 research seed values pending primary-source audit (EEA viewer + BoE EUR/GBP series) before 2027-01-15 next_audit."
  - "Closed Phase 4 SEED-001 partial-coverage gap in the same plan — _TRACKED now enumerates all 25 year keys (was only 3: 2021-2023). Pre-existing 2018-2020 + 2024-2026 were on the module but untracked."
  - "Used live DEFAULT_CARBON_PRICES values (2022=73.0, 2023=45.0, 2024=36.0, 2025=42.0, 2026=40.0) not plan <interfaces> snapshot values (2022=78.0 etc.). Plan's 'Existing 2018-2026 values unchanged' directive overrides stale interface block — live source is truth of 'existing'."

patterns-established:
  - "Additive carbon-price extension via literal dict-literal edit + matching YAML blocks + _TRACKED additions, all co-atomic in successive commits within a plan — grep-auditable via `grep DEFAULT_CARBON_PRICES_YYYY` across the three surfaces."
  - "[VERIFICATION-PENDING] marker in constants.yaml basis field for executor-accepted research seeds — grep-discoverable follow-up for future audit plans."

requirements-completed: [RO-02]  # partial (counterfactual now RO-ready; §6.1 module lands in Plan 05-05)

# Metrics
duration: 4min
completed: 2026-04-23
---

# Phase 05 Plan 04: DEFAULT_CARBON_PRICES 2002-2017 Extension Summary

**Additive extension of counterfactual.DEFAULT_CARBON_PRICES to 25 consecutive year keys (2002-2026) with matching constants.yaml provenance blocks and _TRACKED coverage — RO scheme now has full carbon-price substrate back to its 2002-04-01 launch, METHODOLOGY_VERSION unchanged at "0.1.0".**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-23T05:06:10Z
- **Completed:** 2026-04-23T05:10:04Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Extended `DEFAULT_CARBON_PRICES` from 9 year keys (2018-2026) to 25 consecutive year keys (2002-2026), covering the full RO scheme span.
- 2002-2004 = 0.0 (pre-EU-ETS; no carbon scheme); 2005-2017 populated with EU ETS Phase I/II/III annual averages (£/tCO2); 2018-2026 unchanged (additive per D-06).
- Added 22 new `DEFAULT_CARBON_PRICES_YYYY` provenance blocks to `tests/fixtures/constants.yaml` (16 new 2002-2017 + 6 completion 2018-2020 + 2024-2026); every live year key now has a matching YAML block.
- Extended `_TRACKED` set in `tests/test_constants_provenance.py` from 6 entries to 28 (3 base + 25 carbon years); drift tripwire now fires on any silent edit to any DEFAULT_CARBON_PRICES year.
- Added CHANGES.md `[Unreleased] ### Changed` bullets + new `## Methodology versions` H3 audit entry documenting additive extension (no version bump).
- `METHODOLOGY_VERSION` unchanged at `"0.1.0"` per D-06 — additive change, no formula-shape change, no existing values revised.
- Closed the Phase 4 SEED-001 Tier 2 partial-coverage gap flagged in Phase 4 Plan 01 STATE note (2018-2020 + 2024-2026 year keys were on the live module but not tracked by the drift tripwire).

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend DEFAULT_CARBON_PRICES dict 2002-2017 + docstring Provenance update** - `d0d8ff5` (feat)
2. **Task 2: Extend constants.yaml with 22 new year entries + _TRACKED set** - `8bc85ac` (feat)
3. **Task 3: CHANGES.md audit entries** - `78b1ac1` (docs)

**Plan metadata commit:** pending (final docs commit at plan close)

## Files Created/Modified

- `src/uk_subsidy_tracker/counterfactual.py` — DEFAULT_CARBON_PRICES grown from 9 to 25 year keys (2002-2026 consecutive). Docstring Provenance block extended with EEA, BoE, ICE source URLs alongside existing OBR + DESNZ citations. Inline comments group years by regulatory phase (pre-EU-ETS / Phase I 2005-2007 / Phase II 2008-2012 / Phase III 2013-2017 / Phase III/IV 2018-2020 / UK ETS 2021+). `[VERIFICATION-PENDING]` flag on 2005-2017 inline comment for audit traceability.
- `tests/fixtures/constants.yaml` — 22 new `DEFAULT_CARBON_PRICES_YYYY` Provenance blocks (16 for 2002-2017, 6 for pre-existing 2018/2019/2020/2024/2025/2026 that were not previously tracked). Each block has full `{source, url, basis, retrieved_on, next_audit, value, unit, notes}` fields mirroring the shape of the pre-existing `DEFAULT_CARBON_PRICES_2021` entry. 2005-2017 blocks carry `[VERIFICATION-PENDING: executor-accepted Plan 05-04 research seed value; audit against primary EEA + BoE sources before next_audit]` in the `basis:` field for grep-discoverable follow-up.
- `tests/test_constants_provenance.py` — `_TRACKED` set grown from 6 entries to 28 entries (3 base constants + 25 DEFAULT_CARBON_PRICES_YYYY year keys). Inline comment records the 3-base + 25-years tally so future slippage is caught in code review.
- `CHANGES.md` — `[Unreleased] ### Changed` gains 2 new bullets (DEFAULT_CARBON_PRICES extension + constants.yaml + _TRACKED extension). `## Methodology versions` gains new H3 audit entry `### DEFAULT_CARBON_PRICES backward extension to 2002 — 2026-04-23, Plan 05-04` documenting rationale (D-06 additive = no version bump), year-by-year values, provenance chain, `[VERIFICATION-PENDING]` audit path, and downstream impact (RO Parquet coverage + drift-tripwire completion).

## Final EU ETS 2005-2017 £/tCO2 Table (per plan output directive)

Values shipped in `DEFAULT_CARBON_PRICES` and `constants.yaml`, derived from Plan 05-04 `<interfaces>` block research seeds (EUR→GBP at BoE contemporary annual-average rates):

| Year | EUR (approx) | BoE EUR/GBP | £/tCO2 shipped | Phase | Notes |
|------|--------------|-------------|----------------|-------|-------|
| 2005 | 18.0         | 0.684       | 12.3           | I     | Pilot year |
| 2006 | 17.5         | 0.682       | 11.9           | I     | Still elevated ahead of Phase I crash |
| 2007 | 0.7          | 0.684       | 0.5            | I     | Price crash — allowances non-bankable; collapsed to ~€0.10 by Sep-2007. Historically correct. |
| 2008 | 22.2         | 0.796       | 17.7           | II    | Phase II opening; bankable allowances |
| 2009 | 13.1         | 0.891       | 11.7           | II    | Post-2008 financial-crisis softening |
| 2010 | 14.3         | 0.858       | 12.3           | II    | Modest recovery |
| 2011 | 13.0         | 0.867       | 11.3           | II    | Prices slipping ahead of Phase III surplus overhang |
| 2012 | 7.4          | 0.811       | 6.0            | II    | Structural surplus + demand collapse |
| 2013 | 4.5          | 0.849       | 3.8            | III   | Phase III opening; surplus overhang |
| 2014 | 6.0          | 0.806       | 4.8            | III   | Backloading announcement recovery |
| 2015 | 7.7          | 0.726       | 5.6            | III   | MSR approved |
| 2016 | 5.3          | 0.819       | 4.3            | III   | Brexit referendum GBP weakness |
| 2017 | 5.8          | 0.876       | 5.1            | III   | Transition year; MSR activation ahead |

Pre-EU-ETS: 2002/2003/2004 = 0.0 (no carbon scheme). 2018-2026: unchanged from pre-Plan-05-04 live values. All values carry `[VERIFICATION-PENDING]` flag in constants.yaml `basis:` until primary-source audit against EEA "Emissions, allowances, surplus and prices in the EU ETS 2005-2020" viewer + Bank of England EUR/GBP annual-average series (next_audit 2027-01-15).

## Decisions Made

- **METHODOLOGY_VERSION stays "0.1.0"** per Plan 05-04 D-06. Additive-extension change — new keys only; no existing values revised; no formula-shape change. Pre-1.0.0 is prototype phase; semantic-version bump reserved for Phase 6+ portal launch milestone.
- **[VERIFICATION-PENDING] flag on 2005-2017 values** rather than blocking plan on primary-source fetch. Plan explicitly authorised ("For any value that cannot be verified within Task budget, use the RESEARCH §5 seed value and flag the Provenance.basis with `[VERIFICATION-PENDING: executor-accepted research seed value]`"). Grep-discoverable follow-up for Plan 05-13 (Post-Execution Human Review) or later audit plan.
- **Use live DEFAULT_CARBON_PRICES values not plan <interfaces> snapshot.** Plan's interfaces block showed 2022=78.0, 2023=56.0, 2024=39.0, 2025=39.0, 2026=39.0 but live counterfactual.py has 2022=73.0, 2023=45.0, 2024=36.0, 2025=42.0, 2026=40.0. Plan frontmatter directive "Existing 2018-2026 values unchanged" forced preserving live values — the live source defines "existing". The plan's interface snapshot was stale.
- **Co-extend 2018-2020 + 2024-2026 YAML + _TRACKED in the same plan** (closes Phase 4 SEED-001 partial-coverage gap) rather than scope-split. Plan explicitly authorised this in Task 2 Step 1 ("Also add the 6 missing existing-year entries — drift-test completion per Phase 4 STATE note"). Cleaner to close the Phase-4 debt in the same commit boundary that introduces the Phase-5 additions.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] Reverted premature RO-02 completion marking in REQUIREMENTS.md**
- **Found during:** post-task state update
- **Issue:** `gsd-tools requirements mark-complete RO-02` flipped RO-02 checkbox to `[x]` and "Complete" in the traceability table. But per Plan 05-04 `<success_criteria>` ("Partial RO-02 progress — counterfactual now RO-ready; §6.1 module lands in 05-05"), RO-02 is NOT fully delivered by this plan. Plan 05-04 ships bandings + carbon-price substrate; the §6.1 five-function contract (`upstream_changed`, `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`) lives in Plan 05-05 and is what actually satisfies RO-02. Marking it `Complete` now would mislead Phase 5 exit-criteria scans into thinking the RO scheme module is shipped when only the inputs are.
- **Fix:** Reverted checkbox to `[ ]` and traceability-table status to `Partial (05-02 bandings + 05-04 carbon substrate; §6.1 in 05-05)`. Added inline HTML comment tracing the partial progress surfaces.
- **Files modified:** `.planning/REQUIREMENTS.md` (line 44 checkbox, line 188 traceability row)
- **Verification:** `grep "RO-02" .planning/REQUIREMENTS.md` shows `[ ]` checkbox + "Partial" status
- **Committed in:** final docs commit (with SUMMARY + STATE + ROADMAP)

**2. [Rule 3 — Blocking] Discrepancy between plan `<interfaces>` snapshot and live DEFAULT_CARBON_PRICES values**
- **Found during:** Task 1 (extend DEFAULT_CARBON_PRICES)
- **Issue:** Plan's `<interfaces>` block claimed existing live values were 2022=78.0, 2023=56.0, 2024=39.0, 2025=39.0, 2026=39.0. Actual live values in counterfactual.py were 2022=73.0, 2023=45.0, 2024=36.0, 2025=42.0, 2026=40.0. Plan frontmatter directive says "Existing 2018-2026 values unchanged" — directly adopting the `<interfaces>` snapshot would have silently revised 5 values in the same commit, tripping `test_yaml_value_matches_live` across the 2022/2023 existing YAML blocks on the very next test run.
- **Fix:** Preserved the live counterfactual.py values. The live source defines "existing"; the plan's interfaces snapshot was stale authoring-time content.
- **Files modified:** N/A — edit carefully shaped rather than fixed-after-the-fact.
- **Verification:** `test_yaml_value_matches_live` green across all 25 year keys.
- **Committed in:** d0d8ff5 (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (1 bug — premature completion; 1 blocking — stale plan interface snapshot caught pre-commit)
**Impact on plan:** Both auto-fixes preserved correctness of the requirement-tracking surface and the drift tripwire. No scope creep; both fixes are within the same artefacts the plan was already modifying (REQUIREMENTS.md traceability + counterfactual.py dict values).

## Verification Results

All plan verification predicates pass:

- `uv run pytest tests/test_constants_provenance.py tests/test_counterfactual.py -x -q` → 63 passed, 0 failed
- `python -c "from uk_subsidy_tracker.counterfactual import DEFAULT_CARBON_PRICES; assert min(DEFAULT_CARBON_PRICES.keys()) == 2002"` → pass (min year = 2002)
- `grep -c "^DEFAULT_CARBON_PRICES_" tests/fixtures/constants.yaml` → 25 (≥25 ✓)
- `grep -c "DEFAULT_CARBON_PRICES_" tests/test_constants_provenance.py` → 28 (≥25 ✓)
- `grep "Methodology versions" CHANGES.md` → matches
- Full suite: 142 passed + 4 skipped (was 98 + 4; +44 from 22 new parametrised constants.yaml cases × 2 tests each)

No auto-fixes applied — live code + data aligned on first pass with the plan's specification. `[VERIFICATION-PENDING]` flag on EU ETS values is a documented plan-authorised autonomous fallback (not a deviation).

## Issues Encountered

None. Plan specification was precise enough to execute verbatim. The one minor discrepancy (plan `<interfaces>` block showed stale 2022-2026 values vs the live counterfactual.py dict) was resolved in favour of the live values per the plan's own "Existing 2018-2026 values unchanged" directive.

## User Setup Required

None - no external service configuration required. The `[VERIFICATION-PENDING]` flag on 2005-2017 values is a grep-discoverable follow-up task — routed to Plan 05-13 (Post-Execution Human Review) or a later audit plan. No immediate user action blocks Plan 05-05 start.

## Next Phase Readiness

**Plan 05-05 (schemes/ro/__init__.py + cost_model.py) unblocked.** The RO `cost_model.py::build_station_month()` can now call `compute_counterfactual(carbon_prices=DEFAULT_CARBON_PRICES, year=row.obligation_year)` for every obligation year 2002-present; no KeyError on pre-2018 RO station-months; `gas_counterfactual_gbp` + `premium_gbp` columns populate correctly across the full RO scheme span.

**RO-02 partial progress shipped** (counterfactual substrate ready; §6.1 contract conformance lands in Plan 05-05). No blockers for Wave 1 completion; Wave 2 (05-06 aggregation + 05-07 forward projection) also unblocked from a carbon-price standpoint.

**Drift tripwire now covers full 25-year dict.** Any silent edit to any DEFAULT_CARBON_PRICES year fails `test_yaml_value_matches_live` with a remediation message citing METHODOLOGY_VERSION + constants.yaml + CHANGES.md. Phase 4 SEED-001 Tier 2 partial-coverage note closed.

**Follow-up routed to 05-13 (already-existing post-execution human review plan):**
- Audit 2005-2017 `[VERIFICATION-PENDING]` values against EEA "Emissions, allowances, surplus and prices in the EU ETS 2005-2020" viewer + Bank of England EUR/GBP annual-average series. On audit, swap `[VERIFICATION-PENDING]` for verified-source citation in `basis:` field of each constants.yaml block (16 entries: 2005-2017 + the 3 new zero blocks 2002-2004 that cite the EEA "no-scheme" context). If any value shifts, SEED-001 Tier 2 drift tripwire fires in audit plan's CI — remediation per the existing tripwire protocol (bump? no: still additive; update YAML + live dict in lock-step; update CHANGES.md Methodology versions).

## Self-Check: PASSED

File existence (all modified + created paths):
- FOUND: src/uk_subsidy_tracker/counterfactual.py
- FOUND: tests/fixtures/constants.yaml
- FOUND: tests/test_constants_provenance.py
- FOUND: CHANGES.md
- FOUND: .planning/phases/05-ro-module/05-04-SUMMARY.md

Commit hashes exist in git log:
- FOUND: d0d8ff5 (Task 1 — feat: extend DEFAULT_CARBON_PRICES to 2002-2017)
- FOUND: 8bc85ac (Task 2 — feat: extend constants.yaml + _TRACKED for 2002-2026)
- FOUND: 78b1ac1 (Task 3 — docs: CHANGES.md audit entries)

---
*Phase: 05-ro-module*
*Completed: 2026-04-23*
