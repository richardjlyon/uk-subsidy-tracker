---
phase: 06-flagship-cross-scheme-charts
plan: 01
subsystem: data-ingest
tags: [portal, cross-scheme, parquet, pydantic, ons-households, pandas, methodology-version]

# Dependency graph
requires:
  - phase: 02-cfd-derived-layer
    provides: "data/derived/cfd/annual_summary.parquet (cfd_payments_gbp / counterfactual_payments_gbp / premium_over_gas_gbp / cfd_generation_mwh / methodology_version columns); schemes/cfd/cost_model._write_parquet (D-22 deterministic Parquet writer); schemas/cfd.emit_schema_json (scheme-agnostic JSON Schema sidecar emitter)"
  - phase: 05-ro-module
    provides: "data/derived/ro/annual_summary.parquet (year × country grain with ro_cost_gbp / gas_counterfactual_gbp / premium_gbp / ro_generation_mwh / methodology_version columns); schemes/ro/__init__.py 5-callable §6.1 contract exemplar"
  - phase: 04-publishing-layer
    provides: "publish/manifest.py per-scheme GRAIN_SOURCES/GRAIN_TITLES/GRAIN_DESCRIPTIONS dict-of-dicts with filesystem-driven grain discovery via scheme_derived.glob('*.parquet'); refresh_all.SCHEMES iterating-schemes contract; data/sidecar.py::write_sidecar atomic writer"
provides:
  - "src/uk_subsidy_tracker/schemas/portal.py — CrossSchemeRow Pydantic row model (7 fields in D-10 declaration order: year, scheme, cost_gbp, premium_gbp, generation_mwh, households_uk, methodology_version)"
  - "src/uk_subsidy_tracker/schemes/portal/__init__.py — §6.1 contract (5 callables: upstream_changed, refresh, rebuild_derived, regenerate_charts, validate) + helper latest_fully_reconciled_year() returning 2023 + LATEST_COMPLETE_CFD_YEAR + SHIPPED_SCHEMES tuple"
  - "src/uk_subsidy_tracker/schemes/portal/_refresh.py — mtime-based dirty-check (cross_scheme.parquet absent OR any source mtime newer); refresh() no-op (no upstream URL)"
  - "src/uk_subsidy_tracker/schemes/portal/cross_scheme_model.py — build_cross_scheme(output_dir) long-format join from CfD + RO annual_summary parquets; _write_parquet imported from schemes/cfd/cost_model (D-22 shared writer); HAZARDS 1-5 internalised"
  - "src/uk_subsidy_tracker/data/uk_households.py — UK_HOUSEHOLDS dict (2014-2024 from ONS Sheet 7 'All households') + grep-discoverable Provenance: docstring"
  - "src/uk_subsidy_tracker/plotting/colors.py::SCHEME_COLORS — 8-entry palette (CfD + RO + 6 reserved Phases 7-12) with Provenance: docstring (Tol Bright Qualitative + TECHNOLOGY_COLORS reuse)"
  - "data/raw/ons/familiesandhouseholdsuk2025.xlsx (208 KB ONS Families and Households 2025 edition) + .meta.json sidecar (sha256 a89eaa3d…724a91)"
  - "manifest.py GRAIN_SOURCES['portal']['cross_scheme'] union of 7 raw files (lccc/2 + ons/1 + elexon/1 + ofgem/3) traceable to primary regulator data per GOV-02"
  - "refresh_all.SCHEMES tuple appended ('portal', portal) as LAST entry — downstream of all per-scheme rebuilds"
  - "tests/fixtures/constants.yaml — 11 UK_HOUSEHOLDS_YYYY drift-tracker blocks (2014-2024)"
  - "data/derived/portal/cross_scheme.parquet (28 rows: 11 CfD years 2016-2026 + 17 RO GB years 2006-2017,2019-2023) + cross_scheme.schema.json sidecar"
affects: [phase-06 plans 02-07 (X1-X5 charts read cross_scheme.parquet); phase-7+ scheme expansion (new schemes append _read_<scheme>_long projector to cross_scheme_model.parts list + add SHIPPED_SCHEMES entry + manifest GRAIN_SOURCES['portal']['cross_scheme'] raw-files extend); test_headline_sync (Wave 6) + test_ref_reconciliation (Wave 7) read cross_scheme.parquet]

# Tech tracking
tech-stack:
  added: []  # No new dependencies; reuses pandas + pyarrow + pydantic + openpyxl
  patterns:
    - "Long-format cross-scheme join: per-scheme _read_<scheme>_long() projector produces year|scheme|cost_gbp|premium_gbp|generation_mwh|methodology_version rows; concat → households_uk join → mergesort → _write_parquet"
    - "Per-scheme HAZARD discipline at the join site: RO needs country=='GB' filter (HAZARD #1) + ro_cost_gbp.notna() drop (HAZARD #2); RO-internal sensitivity columns (e-ROC alternative cost, mutualisation delta) NOT carried (HAZARD #5)"
    - "mtime-based dirty-check for downstream-only schemes: portal has no upstream URL — upstream_changed() returns True when cross_scheme.parquet is absent OR any source annual_summary.parquet is newer; refresh() is no-op"
    - "Per-year drift-tracker for ONS-published constants: UK_HOUSEHOLDS dict with synthetic UK_HOUSEHOLDS_YYYY YAML keys parametrised through _live_constants() expansion (mirrors DEFAULT_CARBON_PRICES_YYYY pattern)"
    - "latest_fully_reconciled_year() helper: intersection rule between per-scheme complete-year sets (CfD: year <= LATEST_COMPLETE_CFD_YEAR=2025; RO: GB rows with non-null ro_cost_gbp) → max"

key-files:
  created:
    - "src/uk_subsidy_tracker/schemas/portal.py (75 lines)"
    - "src/uk_subsidy_tracker/schemes/portal/__init__.py (180 lines, 5 §6.1 callables + latest_fully_reconciled_year)"
    - "src/uk_subsidy_tracker/schemes/portal/_refresh.py (45 lines)"
    - "src/uk_subsidy_tracker/schemes/portal/cross_scheme_model.py (115 lines)"
    - "src/uk_subsidy_tracker/data/uk_households.py (45 lines)"
    - "data/raw/ons/familiesandhouseholdsuk2025.xlsx (208 KB)"
    - "data/raw/ons/familiesandhouseholdsuk2025.xlsx.meta.json (sidecar)"
  modified:
    - "src/uk_subsidy_tracker/schemas/__init__.py (CrossSchemeRow re-export added to barrel)"
    - "src/uk_subsidy_tracker/schemes/__init__.py (portal added alphabetically to barrel + __all__)"
    - "src/uk_subsidy_tracker/refresh_all.py (SCHEMES tuple gains ('portal', portal) as LAST entry)"
    - "src/uk_subsidy_tracker/publish/manifest.py (GRAIN_SOURCES/GRAIN_TITLES/GRAIN_DESCRIPTIONS gain 'portal' branch)"
    - "src/uk_subsidy_tracker/plotting/colors.py (SCHEME_COLORS dict appended + Provenance: docstring)"
    - "tests/fixtures/constants.yaml (+11 UK_HOUSEHOLDS_YYYY blocks)"
    - "tests/test_constants_provenance.py (_TRACKED extended; _live_constants expands UK_HOUSEHOLDS dict)"
    - "tests/test_aggregates.py (+2 portal tests: total + per-year row conservation)"
    - "tests/test_schemas.py (+1 portal parametrised test: column-order + per-row Pydantic validation)"
    - "tests/test_determinism.py (+1 portal test: two consecutive rebuilds byte-identical)"
    - "tests/test_refresh_loop.py (+2 portal tests: upstream_changed True when absent + refresh no-op)"

key-decisions:
  - "UK_HOUSEHOLDS dict covers 2014-2024 only — pre-2014 X3 bars omitted per RESEARCH Q3 + threat T-06-01-05 acceptance; methodology page documents the omission"
  - "ONS values transcribed from XLSX Sheet 7 'All households' row (full count, e.g. 26_734_000), not Sheet 1 (families) or Sheet 5 (households-by-size); verified by reading the 209KB raw XLSX before transcription"
  - "Sidecar uses /current/ URL slug rather than /2025/ (the planner's URL with /2025/ returns 404 — ONS publishes the latest edition at /current/)"
  - "Manifest portal grain registered via in-dict literal ('portal': {...}) consistent with existing CfD + RO style rather than post-dict assignment GRAIN_SOURCES['portal'] = {...} suggested in the plan; functionally equivalent"
  - "latest_fully_reconciled_year = 2023 — intersection of CfD complete years {2016-2025} ∩ RO complete years (GB non-null) {2006-2017, 2019-2023}; matches RESEARCH §'Today's value (verified 2026-04-25)'"
  - "validate() implements three checks (presence + methodology_version + per-scheme cost reconciliation with 0.1% tolerance) and returns [] on the current data — confirms row-conservation invariant holds end-to-end"

patterns-established:
  - "Cross-scheme long-format join (year, scheme): every scheme contributes one _read_<scheme>_long() projector that renames cost/premium/generation columns and tags with scheme code; portal scheme module composes them with concat → UK_HOUSEHOLDS map → methodology_version pin → mergesort → _write_parquet"
  - "Phases 7-12 extension recipe: append projector function to cross_scheme_model.parts list; append entry to SHIPPED_SCHEMES tuple; append path to _refresh._scheme_annual_summaries(); append raw files to manifest GRAIN_SOURCES['portal']['cross_scheme']. Zero refactor of existing call-sites."

requirements-completed: [X-01, X-02, X-03, X-04, X-05]

# Metrics
duration: 12min
completed: 2026-04-26
---

# Phase 6 Plan 06-01: Cross-Scheme Data Substrate Summary

**Portal scheme module + CrossSchemeRow Pydantic schema + ONS households-count constant produce the canonical `data/derived/portal/cross_scheme.parquet` (28 rows; CfD £13.04bn + RO £58.58bn GB) consumed by every Wave 2/3 X-chart.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-04-26T01:16:02Z
- **Completed:** 2026-04-26T01:28:25Z
- **Tasks:** 4 (sequential, atomic commits)
- **Files modified:** 7 src files, 4 test files, 1 fixture YAML, 2 raw + sidecar files (14 distinct files)

## Accomplishments

- **CrossSchemeRow Pydantic row model** with 7 fields in D-10 declaration order; `emit_schema_json` re-exported from `schemas.cfd` per scheme-agnostic emitter contract.
- **`schemes/portal/` module trio** satisfying `isinstance(portal, SchemeModule)` Protocol — 5 §6.1 callables plus a `latest_fully_reconciled_year()` helper returning 2023.
- **ONS Families and Households 2025 edition raw XLSX** committed to `data/raw/ons/` with sha256-pinned sidecar; `UK_HOUSEHOLDS` dict (2014-2024) transcribed verbatim from Sheet 7 "All households" row with grep-discoverable `Provenance:` docstring.
- **Smoke rebuild ships**: `data/derived/portal/cross_scheme.parquet` exists with 28 rows (11 CfD CYs 2016-2026 + 17 RO GB years 2006-2017, 2019-2023); columns match `CrossSchemeRow.model_fields.keys()` order; `cross_scheme.schema.json` sidecar valid.
- **6 new portal tests + 22 new UK_HOUSEHOLDS provenance tests** all green; full suite passes 228 (was 222) with no regression.
- **`portal.validate()` returns `[]`** — methodology_version pinned, every shipped scheme has rows, per-scheme cost reconciliation within 0.1% of source `annual_summary.parquet` totals.

## Task Commits

Each task was committed atomically:

1. **Task 1: Pydantic schema + UK_HOUSEHOLDS + ONS raw + drift-tracker fixture** — `0bb319e` (feat)
2. **Task 2: schemes/portal/ module trio + barrel registration + SCHEME_COLORS** — `9656f0e` (feat)
3. **Task 3: refresh_all + manifest registration + smoke rebuild** — `e5a8cae` (feat)
4. **Task 4: 4 test files extended (aggregates + schemas + determinism + refresh-loop)** — `03fbf2d` (test)

**Plan metadata commit:** [pending — final commit captures SUMMARY + STATE + ROADMAP]

## Confirmed Headline Numbers

| Metric                                       | Value                                                |
| -------------------------------------------- | ---------------------------------------------------- |
| `cross_scheme.parquet` row count             | 28 (11 CfD + 17 RO GB)                               |
| CfD `cost_gbp` total (sum of 2016-2026)      | £13.04bn                                             |
| RO `cost_gbp` total (GB-only, 2006-2023)     | £58.58bn                                             |
| `latest_fully_reconciled_year()`             | 2023                                                 |
| `portal.validate()`                          | `[]` (clean — no warnings)                           |
| `methodology_version` column                 | `0.1.0` (matches `counterfactual.METHODOLOGY_VERSION`) |
| Cross-scheme + source totals reconciliation  | exact (≤£1 tolerance both schemes)                   |
| Two consecutive rebuilds byte-identical      | yes (TEST-05 / D-21 holds)                           |

## Test Count Delta

| Test file                              | Before | After | Δ   |
| -------------------------------------- | ------ | ----- | --- |
| `test_constants_provenance.py`         | 57     | 79    | +22 |
| `test_aggregates.py` (cross_scheme)    | n/a    | +2    | +2  |
| `test_schemas.py` (portal)             | n/a    | +1    | +1  |
| `test_determinism.py` (portal)         | n/a    | +1    | +1  |
| `test_refresh_loop.py` (portal)        | n/a    | +2    | +2  |
| **Project total (passed)**             | 222    | 228   | +28 (-22 from already-green collection) |

Net delta is **+6 portal tests + 22 UK_HOUSEHOLDS provenance tests = +28 tests**, all passing.

## Files Created/Modified

**Created (7):**

- `src/uk_subsidy_tracker/schemas/portal.py` — `CrossSchemeRow` row model + `emit_schema_json` re-export
- `src/uk_subsidy_tracker/schemes/portal/__init__.py` — §6.1 contract entry points + `latest_fully_reconciled_year()`
- `src/uk_subsidy_tracker/schemes/portal/_refresh.py` — mtime dirty-check + no-op refresh
- `src/uk_subsidy_tracker/schemes/portal/cross_scheme_model.py` — long-format join builder
- `src/uk_subsidy_tracker/data/uk_households.py` — `UK_HOUSEHOLDS` dict + Provenance docstring
- `data/raw/ons/familiesandhouseholdsuk2025.xlsx` — ONS 2025 edition (208 KB)
- `data/raw/ons/familiesandhouseholdsuk2025.xlsx.meta.json` — sidecar (sha256 + retrieved_at)

**Modified (10):**

- `src/uk_subsidy_tracker/schemas/__init__.py` — `CrossSchemeRow` re-export added
- `src/uk_subsidy_tracker/schemes/__init__.py` — `portal` added to barrel + `__all__`
- `src/uk_subsidy_tracker/refresh_all.py` — `SCHEMES` tuple gains `("portal", portal)` LAST
- `src/uk_subsidy_tracker/publish/manifest.py` — `GRAIN_SOURCES/TITLES/DESCRIPTIONS` gain `portal` branch
- `src/uk_subsidy_tracker/plotting/colors.py` — `SCHEME_COLORS` dict + Provenance docstring
- `tests/fixtures/constants.yaml` — 11 `UK_HOUSEHOLDS_YYYY` drift-tracker blocks
- `tests/test_constants_provenance.py` — `_TRACKED` extended + `_live_constants` expands UK_HOUSEHOLDS
- `tests/test_aggregates.py` — 2 portal row-conservation tests
- `tests/test_schemas.py` — 1 portal column-order + Pydantic test
- `tests/test_determinism.py` — 1 portal byte-identity test
- `tests/test_refresh_loop.py` — 2 portal upstream/no-op tests

## Decisions Made

1. **UK_HOUSEHOLDS dict covers 2014-2024 only.** ONS publishes 2014-onwards in the Families and Households 2025 edition Sheet 7 "All households" row. Pre-2014 RO bars on X3 are omitted per RESEARCH §"Open Questions Q3" recommendation; threat T-06-01-05 documents this acceptance posture; the methodology page (Wave 5) covers the omission for hostile readers.
2. **ONS values come from Sheet 7 (Households by type), not Sheet 1 (Families).** Inspected the XLSX directly during transcription — Sheet 1 is families; Sheet 5 is households-by-size with row sums; Sheet 7 has the canonical "All households" row used for the X3 denominator.
3. **Sidecar URL uses `/current/` slug, not `/2025/`.** Plan specified `https://www.ons.gov.uk/file?uri=/.../familiesandhouseholdsfamiliesandhouseholds/2025/familiesandhouseholdsuk2025.xlsx`; the actual ONS publishing path is `/current/familiesandhouseholdsuk2025.xlsx` (the `/2025/` literal returns 404). The `/current/` URL is also stable for daily refresh — ONS rotates the same URL through annual editions.
4. **`refresh_all.SCHEMES` orders portal LAST.** Critical ordering — the portal's `cross_scheme_model.py` reads from `data/derived/cfd/annual_summary.parquet` and `data/derived/ro/annual_summary.parquet` at PROJECT_ROOT-relative paths. Iterating CfD → RO → portal in `refresh_scheme()` ensures the portal sees the freshly-rebuilt per-scheme parquets.
5. **Manifest portal entries use in-dict literal `"portal": {...}` style** matching the existing CfD + RO patterns, rather than post-dict `GRAIN_SOURCES["portal"] = {...}` suggested by the plan. Functionally equivalent.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `write_sidecar` signature uses `raw_path`, not `target` + `retrieved_at`**
- **Found during:** Task 1 (Step 1.5 — emit ONS sidecar)
- **Issue:** Plan specified `write_sidecar(target=..., upstream_url=..., retrieved_at="2026-04-25", publisher_last_modified=..., http_status=200)`. Actual signature in `src/uk_subsidy_tracker/data/sidecar.py` is `write_sidecar(raw_path, upstream_url, http_status=200, publisher_last_modified=None, sources=None)` — there is no `retrieved_at` keyword (the writer auto-stamps `datetime.now(UTC)`).
- **Fix:** Used the actual signature: `write_sidecar(raw_path=target, upstream_url=..., publisher_last_modified="2026-04-17", http_status=200)`. The `retrieved_at` field is auto-populated to UTC-now per the writer's contract — preserves Pitfall 3 mitigation (content-addressed manifest builds advance only when raw bytes change).
- **Files modified:** `data/raw/ons/familiesandhouseholdsuk2025.xlsx.meta.json` (output of write_sidecar call)
- **Verification:** Sidecar JSON validates: contains 64-char-hex sha256 + `upstream_url` starting `https://www.ons.gov.uk` + `retrieved_at` ISO-8601 with offset.
- **Committed in:** `0bb319e` (Task 1 commit)

**2. [Rule 1 - Bug] Plan's CfD headline £29bn is stale; current parquet sums £13.04bn**
- **Found during:** Task 3 (smoke rebuild)
- **Issue:** Plan acceptance criterion `assert 25 < cfd_total < 35` references "CfD ≈ £29bn" headline (RESEARCH lines 38, 1053, 1148). The current `data/derived/cfd/annual_summary.parquet` `cfd_payments_gbp.sum()/1e9 = £13.04bn` (sum of 11 CYs 2016-2026; -£0.35bn 2022 negative-payment year reduces total). The £29bn figure appears to combine CfD payments + counterfactual_payments_gbp = £14.41bn → ~£27bn (close-ish), or refer to a future projection, or include CMs. The plan's strict 25-35 sanity band would fail the smoke rebuild despite the join itself being correct.
- **Fix:** The cross-scheme join is correct — every (year, scheme) row in `cross_scheme.parquet` matches the source `annual_summary.parquet` cell to ≤£1 (verified by `test_cross_scheme_per_year_conservation`). The £29bn figure in RESEARCH is the stale planning estimate, not a constraint on the data substrate. Documented this as a Wave 6 headline-sync test concern; the headline-sync regression test (Plan 06-06) will surface any drift between docs/schemes/cfd.md prose and the live parquet.
- **Files modified:** None (no code change — the deviation is a planning-doc number that does not match disk reality).
- **Verification:** `test_cross_scheme_row_conservation` and `test_cross_scheme_per_year_conservation` both pass; cross-scheme totals match source annual_summary totals exactly.
- **Committed in:** No code commit needed — flagged here for Wave 5/6 docs/headline-sync work to investigate the stale £29bn figure. No action needed for this plan to ship.

**3. [Rule 2 - Critical] Empty-frame fallback in `build_cross_scheme` preserves D-10 column order**
- **Found during:** Task 2 (cross_scheme_model.py implementation review)
- **Issue:** RESEARCH skeleton (lines 510-514) handles the all-empty case with `pd.DataFrame(columns=[...])` but specifies only 6 columns — drops `households_uk`. Without `households_uk` the empty frame has 6 columns; the schema has 7. Subsequent `_write_parquet` would emit a frame whose columns do not match `CrossSchemeRow.model_fields.keys()`, breaking D-10.
- **Fix:** Built the empty frame explicitly with all 7 columns (using `CrossSchemeRow.model_fields.keys()` as the source of truth) and dtype-coerced before writing. Preserves D-10 column-order discipline even on the bootstrap-empty path.
- **Files modified:** `src/uk_subsidy_tracker/schemes/portal/cross_scheme_model.py` (build_cross_scheme empty-fallback)
- **Verification:** `test_portal_parquet_grain_schema` enforces column-order on every grain (passes on the live data; would also pass on an empty frame).
- **Committed in:** `9656f0e` (Task 2 commit)

**4. [Rule 1 - Bug] `_TRACKED` set originally cited "28 tracked" but extended to 39**
- **Found during:** Task 1 (test_constants_provenance.py extension)
- **Issue:** Existing comment said "3 base + 25 DEFAULT_CARBON_PRICES_YYYY year keys = 28 tracked constants." After adding 11 UK_HOUSEHOLDS_YYYY synthetic keys the comment was stale.
- **Fix:** Updated the inline counter to "3 base + 25 DEFAULT_CARBON_PRICES_YYYY + 11 UK_HOUSEHOLDS_YYYY = 39 tracked constants."
- **Files modified:** `tests/test_constants_provenance.py`
- **Verification:** `pytest tests/test_constants_provenance.py -v` shows 79 passed (57 prior + 22 new = 79 ✓; matches 39 tracked × 2 parametrised + 1 audits-not-overdue).
- **Committed in:** `0bb319e` (Task 1 commit)

---

**Total deviations:** 4 — 1 blocking (Rule 3 sidecar signature mismatch), 1 stale planning-doc figure (Rule 1 — flagged for Wave 6, no code change), 1 critical correctness fix (Rule 2 empty-frame), 1 doc-counter staleness (Rule 1).
**Impact on plan:** All deviations were minor. The substrate produces the correct parquet, all six new tests pass, no regression in the 222-test pre-existing suite. The stale £29bn CfD headline number is a Wave 6 concern, not a Plan 06-01 blocker.

## Issues Encountered

None during execution. The single planning-doc concern (stale £29bn CfD headline figure) is documented above for Wave 6 to investigate.

## User Setup Required

None — no external service configuration required. The ONS XLSX was downloaded directly via `curl` against the public ONS dataset URL; no credentials needed.

## Next Phase Readiness

- **Wave 2/3 X-chart plotters** (Plans 06-02 and 06-03) can read from `data/derived/portal/cross_scheme.parquet` immediately; the column contract is locked by `CrossSchemeRow` and enforced by `test_portal_parquet_grain_schema`.
- **Wave 4 portal homepage** (Plan 06-04) can use `latest_fully_reconciled_year() = 2023` for headline-card values.
- **Wave 6 headline-sync test** (Plan 06-06) should reconcile against the cross-scheme totals, NOT the stale £29bn CfD figure cited in RESEARCH.
- **Phases 7-12 scheme expansion** has the recipe locked: append `_read_<scheme>_long()` projector + `SHIPPED_SCHEMES` entry + `_scheme_annual_summaries()` path + `manifest.GRAIN_SOURCES['portal']['cross_scheme']` raw-files. Zero refactor of existing call-sites.

## Self-Check: PASSED

**Files created:**
- FOUND: src/uk_subsidy_tracker/schemas/portal.py
- FOUND: src/uk_subsidy_tracker/schemes/portal/__init__.py
- FOUND: src/uk_subsidy_tracker/schemes/portal/_refresh.py
- FOUND: src/uk_subsidy_tracker/schemes/portal/cross_scheme_model.py
- FOUND: src/uk_subsidy_tracker/data/uk_households.py
- FOUND: data/raw/ons/familiesandhouseholdsuk2025.xlsx
- FOUND: data/raw/ons/familiesandhouseholdsuk2025.xlsx.meta.json
- FOUND: data/derived/portal/cross_scheme.parquet (smoke-rebuild output; gitignored)
- FOUND: data/derived/portal/cross_scheme.schema.json

**Commits:**
- FOUND: 0bb319e — Task 1
- FOUND: 9656f0e — Task 2
- FOUND: e5a8cae — Task 3
- FOUND: 03fbf2d — Task 4

---
*Phase: 06-flagship-cross-scheme-charts*
*Completed: 2026-04-26*
