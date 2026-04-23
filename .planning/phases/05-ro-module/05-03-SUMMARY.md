---
phase: 05-ro-module
plan: 03
subsystem: schemas
tags: [pydantic, parquet, ro, schemas, field-order, d10, d11]

# Dependency graph
requires:
  - phase: 02-test-benchmark-scaffolding
    provides: schemas/cfd.py template + emit_schema_json scheme-agnostic emitter
  - phase: 04-publishing-layer
    provides: schemas/ namespace + D-10/D-11 field-order discipline
provides:
  - 5 Pydantic row models for the RO derived Parquet grains (D-10 column-order contract)
  - RoStationMonthRow / RoAnnualSummaryRow / RoByTechnologyRow / RoByAllocationRoundRow / RoForwardProjectionRow
  - Barrel re-export in schemas/__init__.py alongside CfD models
  - emit_schema_json re-use pattern (scheme-agnostic emitter imported, not duplicated)
  - D-10 field-order tripwire tests (5 canonical-list comparisons)
affects: [05-05 cost_model + aggregation + forward_projection, 05-10 test_schemas parametrisation, 05-11 manifest, 05-12 docs, 07-fit-module, phase-06 cross-scheme]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "D-10 canonical-list tripwire: module-level list constant in tests == model_fields.keys() verbatim; reorder requires test + code + CHANGES.md ## Methodology versions entry"
    - "Scheme-agnostic emitter re-use: schemas.ro imports emit_schema_json from schemas.cfd (single source of truth; T-5.03-02 mitigation)"

key-files:
  created:
    - src/uk_subsidy_tracker/schemas/ro.py
    - tests/test_ro_schemas_smoke.py
  modified:
    - src/uk_subsidy_tracker/schemas/__init__.py

key-decisions:
  - "D-10 field-order snapshots pinned verbatim as module-level Python lists in tests (reorder tripwire)"
  - "emit_schema_json imported from schemas.cfd (NOT redeclared) — single source of truth across schemes"
  - "mutualisation_gbp nullable on BOTH RoStationMonthRow and RoAnnualSummaryRow per D-11 (non-null only on OY 2021-22)"
  - "by_allocation_round grain uses commissioning_window axis (RO has no 'allocation round' axis per RESEARCH §5)"
  - "ForwardProjectionRow grain is (year, technology) — one-row-per-projected-year, not one-row-per-station (differs from CfD)"

patterns-established:
  - "D-10 field-order tripwire: test compares list(Model.model_fields.keys()) against a module-level canonical list in the test file"
  - "T-5.03-02 mitigation: grep-style test asserts 'def emit_schema_json' absent from schemas/ro.py AND 'from uk_subsidy_tracker.schemas.cfd import emit_schema_json' present"
  - "Re-export discipline: every new scheme's schemas module surfaces through schemas/__init__.py barrel so downstream code writes `from uk_subsidy_tracker.schemas import RoStationMonthRow`"

requirements-completed: []  # RO-03 is multi-plan: Pydantic contracts shipped here; Parquet production lands in Plan 05-05 (per PLAN success_criteria note)

# Metrics
duration: 3min
completed: 2026-04-23
---

# Phase 05 Plan 03: RO Pydantic Row Schemas Summary

**5 Pydantic BaseModel row schemas for the RO Parquet grains with D-10 field-order discipline and scheme-agnostic emit_schema_json re-use, mirroring schemas/cfd.py verbatim.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-23T04:59:10Z
- **Completed:** 2026-04-23T05:02:00Z
- **Tasks:** 1 (TDD RED → GREEN)
- **Files created:** 2 (`schemas/ro.py`, `tests/test_ro_schemas_smoke.py`)
- **Files modified:** 1 (`schemas/__init__.py`)

## Accomplishments

- 5 Pydantic row models shipped for the RO derived Parquet grains: `RoStationMonthRow` (17 fields), `RoAnnualSummaryRow` (9 fields), `RoByTechnologyRow` (6 fields), `RoByAllocationRoundRow` (6 fields), `RoForwardProjectionRow` (7 fields). Field declaration order IS the Parquet column order on every grain (D-10).
- `emit_schema_json` imported from `schemas.cfd` — scheme-agnostic emitter with a single source of truth (T-5.03-02 mitigation grep-checked in the test suite).
- `schemas/__init__.py` barrel extended so `from uk_subsidy_tracker.schemas import RoStationMonthRow` resolves alongside the existing CfD row models + `emit_schema_json`.
- 9 new smoke tests pin the field-order snapshots, instantiation behaviour, D-11 nullability on `mutualisation_gbp` (both `RoStationMonthRow` and `RoAnnualSummaryRow`), re-use-not-redeclare of `emit_schema_json`, and barrel re-export.
- Test coverage: **98 passing + 4 skipped** (was 89 + 4; +9 from this plan).
- TDD discipline maintained: RED commit proved 9 failing tests (module did not exist), GREEN commit added the module + barrel update and 9 tests pass.

## Task Commits

TDD two-commit sequence:

1. **RED — failing tests** — `cdf9d0f` `test(05-03): add failing RO schemas smoke tests (RED)` — `tests/test_ro_schemas_smoke.py` (241 lines).
2. **GREEN — implementation passes tests** — `150fbdd` `feat(05-03): add RO Pydantic row models (GREEN)` — `src/uk_subsidy_tracker/schemas/ro.py` (293 lines) + `src/uk_subsidy_tracker/schemas/__init__.py` (barrel re-export extended).

_(No REFACTOR phase — the RED/GREEN output is already at the target shape.)_

## Files Created / Modified

### Created

- `src/uk_subsidy_tracker/schemas/ro.py` — 5 RO row models following `schemas/cfd.py` shape. Each Field carries `description=` and `json_schema_extra={"dtype": ..., "unit": ...}` so `<grain>.schema.json` siblings (D-11; Plan 05-11/05-05) emit machine-readable dtype + unit metadata. `emit_schema_json` imported, not redeclared (noqa: F401 re-export).
- `tests/test_ro_schemas_smoke.py` — 9 smoke tests: 5 field-order tripwires (`RO_STATION_MONTH_FIELDS`, `RO_ANNUAL_SUMMARY_FIELDS`, `RO_BY_TECHNOLOGY_FIELDS`, `RO_BY_ALLOCATION_ROUND_FIELDS`, `RO_FORWARD_PROJECTION_FIELDS` canonical lists) + instantiation + nullability + emit-reuse grep check + barrel re-export.

### Modified

- `src/uk_subsidy_tracker/schemas/__init__.py` — barrel re-export extended with `RoStationMonthRow`, `RoAnnualSummaryRow`, `RoByTechnologyRow`, `RoByAllocationRoundRow`, `RoForwardProjectionRow`. Module docstring clarifies the scheme-agnostic `emit_schema_json` single-source-of-truth discipline.

## D-10 Field-Order Snapshots (drift tripwire reference)

These lists are the canonical Parquet column orders on each RO grain. The test file (`tests/test_ro_schemas_smoke.py`) pins them verbatim; any change here requires a matching test edit AND a `CHANGES.md ## Methodology versions` entry citing D-10.

### `RoStationMonthRow` (17 fields — `ro/station_month.parquet`)

```
 1. station_id
 2. country                      # D-09
 3. technology
 4. commissioning_window
 5. month_end
 6. obligation_year              # D-08 audit trail
 7. generation_mwh
 8. rocs_issued                  # D-01 primary
 9. rocs_computed                # D-01 audit cross-check
10. banding_factor_yaml
11. ro_cost_gbp                  # D-02 primary (consumer-cost view)
12. ro_cost_gbp_eroc             # D-02 sensitivity (generator-revenue view)
13. ro_cost_gbp_nocarbon         # D-05 sensitivity
14. gas_counterfactual_gbp
15. premium_gbp
16. mutualisation_gbp            # D-11 nullable; non-null OY 2021-22 only
17. methodology_version          # D-12 last column
```

### `RoAnnualSummaryRow` (9 fields — `ro/annual_summary.parquet`)

```
1. year
2. country                       # D-09
3. ro_generation_mwh
4. ro_cost_gbp
5. ro_cost_gbp_eroc
6. gas_counterfactual_gbp
7. premium_gbp
8. mutualisation_gbp             # D-11 nullable
9. methodology_version
```

### `RoByTechnologyRow` (6 fields — `ro/by_technology.parquet`)

```
1. year
2. technology
3. ro_generation_mwh
4. ro_cost_gbp
5. ro_cost_gbp_eroc
6. methodology_version
```

### `RoByAllocationRoundRow` (6 fields — `ro/by_allocation_round.parquet`)

```
1. year
2. commissioning_window          # RO analogue of CfD's allocation_round (RESEARCH §5)
3. ro_generation_mwh
4. ro_cost_gbp
5. ro_cost_gbp_eroc
6. methodology_version
```

### `RoForwardProjectionRow` (7 fields — `ro/forward_projection.parquet`)

```
1. year                          # projected future CY
2. technology
3. remaining_committed_mwh
4. remaining_cost_gbp
5. station_count_active
6. avg_banding_factor
7. methodology_version
```

## Decisions Made

1. **Canonical field lists pinned in the test module** — Not in the schema module itself: tests are the drift tripwire (T-5.03-01 mitigation). Rejected alternative: expose `FIELDS = [...]` class attributes on each row model — would duplicate Pydantic's own `model_fields.keys()` and invites drift.
2. **`emit_schema_json` re-used via plain import with `# noqa: F401`** — Included in `schemas/ro.py` module body so downstream code can write `from uk_subsidy_tracker.schemas.ro import emit_schema_json` if preferred, mirroring CfD module surface. The barrel `__init__.py` also re-exports it from `schemas.cfd` directly to avoid circular import risk.
3. **`mutualisation_gbp` defaults to `None` with explicit `float | None` type** — Matches CfD's `strike_price_gbp_per_mwh: float | None = Field(default=None, ...)` pattern in `schemas/cfd.py:58-62`. Both row models (`RoStationMonthRow` AND `RoAnnualSummaryRow`) carry this nullable column per D-11.
4. **`RoForwardProjectionRow` grain shape diverges from CfD** — CfD's `ForwardProjectionRow` is one-row-per-station (carries `station_id`, `contract_start_year`, `contract_end_year`). RO's is one-row-per-(projected-year, technology) carrying `station_count_active` + `avg_banding_factor` — consistent with Plan 05-07's forward-projection methodology deferred-design (per `05-CONTEXT.md` "Forward projection methodology is a planner decision"). Decoupling is intentional: RO's accreditation-window drawdown to 2037 is more naturally expressed at the aggregated grain.

## Deviations from Plan

None — plan executed exactly as written. RED/GREEN TDD sequence produced the intended 9/9 pass state on first run; no auto-fixes (Rule 1-3) needed; no architectural escalations (Rule 4) encountered.

## Issues Encountered

None. The PATTERNS.md closest-analog snippet (lines 494-531) was a near-verbatim template for the row-model declarations; only the ForwardProjectionRow grain shape required extrapolation from the plan's field list (PLAN 05-03 lines 92-94) rather than the PATTERNS snippet.

## User Setup Required

None — pure refactor/scaffolding task; no external services, no environment variables, no dashboards.

## Next Plan Readiness

- **Plan 05-04 (counterfactual carbon-price extension)** — unblocked; does not depend on this plan directly.
- **Plan 05-05 (cost_model + aggregation + forward_projection)** — **unblocked by this plan**. `schemes/ro/cost_model.py` will produce DataFrames whose column order matches `RoStationMonthRow.model_fields.keys()`; `schemes/ro/aggregation.py` will do the same for the 3 rollup grains; `schemes/ro/forward_projection.py` will do the same for `RoForwardProjectionRow`.
- **Plan 05-10 (test_schemas parametrisation over RO grains)** — unblocked by this plan. Tests will parametrise over the 5 new row models just like CfD does in `tests/test_schemas.py`.
- **Plan 05-11 (manifest / publish layer)** — unblocked by this plan. `publish/manifest.py` already iterates SCHEMES; it will pick up RO grains automatically once Plan 05-05 lands and schemas here ensure the per-grain `*.schema.json` emission via `emit_schema_json`.

## Self-Check: PASSED

Verified via:

```
$ [ -f src/uk_subsidy_tracker/schemas/ro.py ] && echo FOUND
FOUND
$ [ -f tests/test_ro_schemas_smoke.py ] && echo FOUND
FOUND
$ git log --oneline --all | grep -E "cdf9d0f|150fbdd"
150fbdd feat(05-03): add RO Pydantic row models (GREEN)
cdf9d0f test(05-03): add failing RO schemas smoke tests (RED)
$ uv run pytest tests/ -q
98 passed, 4 skipped in 6.20s
$ grep -c "def emit_schema_json" src/uk_subsidy_tracker/schemas/ro.py
0
$ grep -c "from uk_subsidy_tracker.schemas.cfd import emit_schema_json" src/uk_subsidy_tracker/schemas/ro.py
1
```

All acceptance gates from PLAN 05-03 `<verification>` block passing.

---

*Phase: 05-ro-module*
*Plan: 03*
*Completed: 2026-04-23*
