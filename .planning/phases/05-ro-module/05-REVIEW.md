---
phase: 05-ro-module
reviewed: 2026-04-23T00:00:00Z
depth: standard
files_reviewed: 32
files_reviewed_list:
  - src/uk_subsidy_tracker/data/ofgem_ro.py
  - src/uk_subsidy_tracker/data/roc_prices.py
  - src/uk_subsidy_tracker/data/ro_bandings.py
  - src/uk_subsidy_tracker/data/ro_bandings.yaml
  - src/uk_subsidy_tracker/counterfactual.py
  - src/uk_subsidy_tracker/schemas/ro.py
  - src/uk_subsidy_tracker/schemes/ro/__init__.py
  - src/uk_subsidy_tracker/schemes/ro/_refresh.py
  - src/uk_subsidy_tracker/schemes/ro/cost_model.py
  - src/uk_subsidy_tracker/schemes/ro/aggregation.py
  - src/uk_subsidy_tracker/schemes/ro/forward_projection.py
  - src/uk_subsidy_tracker/publish/manifest.py
  - src/uk_subsidy_tracker/refresh_all.py
  - src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py
  - src/uk_subsidy_tracker/plotting/subsidy/ro_by_technology.py
  - src/uk_subsidy_tracker/plotting/subsidy/ro_concentration.py
  - src/uk_subsidy_tracker/plotting/subsidy/ro_forward_projection.py
  - src/uk_subsidy_tracker/plotting/__main__.py
  - scripts/backfill_sidecars.py
  - tests/data/test_ofgem_ro.py
  - tests/data/test_ro_bandings.py
  - tests/test_ro_schemas_smoke.py
  - tests/test_ro_rebuild_smoke.py
  - tests/test_refresh_loop.py
  - tests/test_benchmarks.py
  - tests/test_schemas.py
  - tests/test_aggregates.py
  - tests/test_determinism.py
  - tests/test_manifest.py
  - tests/test_constants_provenance.py
  - tests/fixtures/__init__.py
  - tests/fixtures/benchmarks.yaml
  - tests/fixtures/constants.yaml
findings:
  critical: 0
  warning: 3
  info: 8
  total: 11
status: issues_found
---

# Phase 5: Code Review Report

**Reviewed:** 2026-04-23T00:00:00Z
**Depth:** standard
**Files Reviewed:** 32
**Status:** issues_found

## Summary

Phase 5 delivers the RO scheme module end-to-end: three Ofgem raw scrapers
(Option-D stubs), a bandings YAML + Pydantic loader, five derived Parquet
grains, four chart pages, the manifest upgrade to multi-scheme iteration,
and carbon-price back-extension to 2002. The overall code quality is high —
D-17 error-path discipline is correctly applied to all three RO scrapers,
the D-21 determinism contract is respected (deterministic `current_year_anchor`
from data rather than `datetime.now`), the schema module imports
`emit_schema_json` from `schemas.cfd` rather than re-declaring it, and the
RO row models follow the CfD template (field-order-is-column-order; trailing
`methodology_version` per D-12).

Findings are concentrated in three areas:

1. **Dead REF-drift check in `validate()`** (WR-01) — the post-rebuild REF
   Constable drift warner points at a path (`src/uk_subsidy_tracker/data/benchmarks.yaml`)
   that does not exist; the real file lives under `tests/fixtures/`. Wrapped in
   `try/except Exception: pass`, so the check silently never fires. Companion
   hard-block in `test_benchmarks.py` still catches divergence, but the cheap
   in-pipeline warner is currently inert.

2. **Dtype drift on `mutualisation_gbp` between empty and non-empty rebuilds**
   (WR-02) — empty-frame branch explicitly sets `Float64` (nullable pandas
   extension dtype); non-empty branch emerges as `float64` from pandas
   `groupby.sum`. When real RO data lands this changes the Parquet column
   logical type without a methodology bump. Phase 5 is currently stub-only so
   the determinism test passes today, but the transition will expose the
   inconsistency.

3. **Stub-data fallback masking** (WR-03) — `_annual_counterfactual_gbp_per_mwh`
   swallows any exception from `compute_counterfactual()` and returns `{}`,
   producing silent all-zero `gas_counterfactual_gbp`. On real data this would
   hide a legitimate failure of the shared counterfactual (e.g. missing ONS
   sheet). The comment acknowledges this is intentional for Wave-2 smoke but
   the escape hatch should be narrowed to `FileNotFoundError` or made opt-in.

The remaining items are informational: a few redundancies (`observed=True`
on non-categorical object columns is a no-op in pandas 3.x), a minor
docstring-vs-code mismatch on the `ro_cost_gbp` formula shape, and some
suggestions around the forward-projection fall-back `avg_banding_factor = 1.0`
which silently propagates into the Parquet when station_month is absent.

## Warnings

### WR-01: REF-drift check in `validate()` reads a non-existent path

**File:** `src/uk_subsidy_tracker/schemes/ro/__init__.py:150-181`
**Issue:** Check 2 of `validate()` builds a path `PROJECT_ROOT / "src" /
"uk_subsidy_tracker" / "data" / "benchmarks.yaml"` and calls `.exists()` before
reading `ref_constable`. This file does not exist in the repo — the actual
benchmarks fixture lives at `tests/fixtures/benchmarks.yaml`. The `if
ref_path.exists():` guard means the block silently no-ops, and the enclosing
`try: ... except Exception: pass` swallows any other failure mode. Net effect:
the post-rebuild REF drift warner is currently dead code. The D-14 hard-block
reconciliation in `tests/test_benchmarks.py::test_ref_constable_ro_reconciliation`
still catches divergence at test time, but the cheap pipeline-level warner is
inert.
**Fix:** Point the path at the real fixture location (or move `benchmarks.yaml`
into `src/` as a runtime-accessible resource if the design intent is to make
it available to non-test code paths):
```python
ref_path = (
    PROJECT_ROOT / "tests" / "fixtures" / "benchmarks.yaml"
)
```
Alternatively, keep `validate()` test-only by deleting Check 2 entirely — the
test_benchmarks hard-block already covers the contract, and having a silently-
disabled check in production is worse than no check.

### WR-02: `mutualisation_gbp` dtype drifts between empty and non-empty rebuilds

**File:** `src/uk_subsidy_tracker/schemes/ro/aggregation.py:54-89`
**Issue:** In `build_annual_summary`, the empty-input branch constructs
`mutualisation_gbp` as `pd.Series([], dtype="Float64")` (nullable extension
dtype), while the non-empty branch computes it via `groupby.agg(..., sum)` which
produces `float64` (NumPy dtype) when the upstream `station_month.mutualisation_gbp`
arrives as `float64` (which it will, per the pandera coerce rule in
`cost_model.station_month_schema`). The post-sum `None` assignment in
```python
agg.loc[agg["mutualisation_gbp"].fillna(0) == 0, "mutualisation_gbp"] = None
```
then silently converts `None` back to `NaN` on a `float64` column. The current
repo posture (Option-D stubs, empty inputs) writes Float64 Parquet; the first
real-data rebuild will write float64. This is a logical-type change across
refreshes that tests/fixtures won't flag until the real data lands, and is a
subtle determinism/schema-drift hazard (the D-10 Parquet column contract covers
order, but consumers doing dtype introspection will see the change).
**Fix:** Pin the dtype consistently on both branches. Either cast both to the
nullable extension dtype:
```python
# In the non-empty branch, immediately after the .reset_index() agg:
agg["mutualisation_gbp"] = agg["mutualisation_gbp"].astype("Float64")
agg.loc[agg["mutualisation_gbp"].fillna(0) == 0, "mutualisation_gbp"] = pd.NA
```
or standardise both on `float64` with NaN semantics and drop the `Float64`
empty-frame declaration. The CfD analogue (`schemes/cfd/aggregation.py`) uses
plain `float64` end-to-end — matching that is the lowest-surprise fix.

### WR-03: Blanket `except Exception:` in `_annual_counterfactual_gbp_per_mwh`

**File:** `src/uk_subsidy_tracker/schemes/ro/cost_model.py:133-140`
**Issue:** The gas-counterfactual lookup wraps `compute_counterfactual()` in a
bare `try/except Exception:` block that returns `{}` on any failure, producing
silent all-zero `gas_counterfactual_gbp` in the station_month Parquet. The
docstring says "If gas SAP data is unavailable ... return an empty lookup
rather than raise", but `Exception` also catches genuine bugs (schema drift
in ONS XLSX, pandera validation failures, missing columns from upstream
refactors) that SHOULD propagate. Once real RO data lands, a zero
counterfactual cascades into `premium_gbp = ro_cost_gbp - 0 = ro_cost_gbp`,
which silently inflates the subsidy-premium headline figure. `validate()`
Check 2 is the intended backstop, but that check currently points at a
non-existent path (WR-01), so there is no defence-in-depth.
**Fix:** Narrow the catch to the one failure mode you want to tolerate
(missing ONS file during Wave-2 bootstrap) and let everything else propagate:
```python
try:
    cf = compute_counterfactual(carbon_prices=DEFAULT_CARBON_PRICES)
except FileNotFoundError:
    # ONS gas SAP not yet downloaded (Wave-2 bootstrap) — return empty
    # lookup so cost_model emits zero counterfactual, caught later by
    # validate() Check 2.
    return {}
```
A `# noqa: BLE001` comment is not a substitute here — the blanket except
genuinely masks correctness bugs in production.

## Info

### IN-01: `observed=True` on object-dtype groupers is a no-op

**File:** `src/uk_subsidy_tracker/schemes/ro/forward_projection.py:109, 114,
160, 176`; `src/uk_subsidy_tracker/plotting/subsidy/ro_concentration.py:40`;
`src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py:52`;
`src/uk_subsidy_tracker/plotting/subsidy/ro_by_technology.py:75`
**Issue:** Multiple call sites pass `observed=True` to `groupby()` on
columns that are `object` / `string` dtype (`technology`, `station_id`,
`commissioning_window`). `observed=` only affects `CategoricalDtype`
groupers — for object-dtype columns it is silently ignored. Not a bug,
but creates confusion about whether a grouper is expected to be
categorical. In pandas 3.0.0 (the installed version) the kwarg is still
accepted without warning for compatibility.
**Fix:** Either cast the relevant columns to `CategoricalDtype` explicitly
(matches CfD stack if the intent is set-membership optimisation) or drop
the `observed=True` on non-categorical groupers. Consistency matters
more than the specific choice; pick one convention and apply it
package-wide.

### IN-02: `ro_cost_gbp` formula docstring vs code ambiguity

**File:** `src/uk_subsidy_tracker/schemes/ro/cost_model.py:21, 287`
**Issue:** The module docstring states
`ro_cost_gbp = rocs_issued × (buyout + recycle) + mutualisation_gbp`, but
the code evaluates
`ro_cost_gbp = rocs_issued × (buyout + recycle + mutualisation_per_roc)`
and separately computes `mutualisation_gbp = rocs_issued × mutualisation_gbp_per_roc`.
Algebraically these agree (distributivity), but at a glance the reader
sees `ro_cost_gbp` already contains the mutualisation contribution,
while `mutualisation_gbp` is a metadata side column — the docstring
makes it look like the total adds mutualisation twice. A future refactor
or a reviewer checking "does this match the methodology page?" will
stumble on the shape mismatch.
**Fix:** Either rewrite the docstring to reflect the code shape
(`rocs_issued × (buyout + recycle + mutualisation_per_roc)`, then note
that `mutualisation_gbp` is the additive component surfaced separately for
audit), or refactor the code to the docstring shape:
```python
df["ro_cost_gbp"] = rocs * (buyout + recycle) + (rocs * mutualisation_per_roc)
```
The second form is clearer for adversarial readers and matches the
methodology page on `docs/schemes/ro.md` line 124.

### IN-03: `avg_banding_factor` fallback to 1.0 propagates into Parquet

**File:** `src/uk_subsidy_tracker/schemes/ro/forward_projection.py:179`
**Issue:** When `station_month.parquet` is absent (Wave-2 bootstrap) the
tech-banding lookup dict is empty and every `avg_bf` defaults to `1.0`,
which then feeds `remaining_cost_gbp = mwh * 1.0 * latest_price_per_roc`
and the `avg_banding_factor` column is persisted as `1.0` in the Parquet.
For offshore wind (actual banding factor 1.8-2.0) this understates
forward-committed cost by 45-50%. Downstream consumers reading the
Parquet have no signal that `1.0` is a sentinel rather than a real
weighted mean.
**Fix:** Use `NaN` as the sentinel for missing banding and ensure the
row is skipped or clearly flagged:
```python
avg_bf = tech_banding.get(str(tech))
if avg_bf is None:
    continue  # or emit with avg_banding_factor = NaN and a sentinel flag
```
Alternatively, document the `1.0` fallback in the row model docstring so
readers know to filter.

### IN-04: `commissioning_window` label emits invalid windows post-2017

**File:** `src/uk_subsidy_tracker/schemes/ro/cost_model.py:111-119`
**Issue:** `_commissioning_window_label` returns `YYYY/YY` labels for any
commissioning date — including dates after 2017-04-01 when the RO was
closed to new accreditations. The YAML has no banding cell for windows
like `2018/19`, so `bandings.lookup()` will raise KeyError and
`banding_factor_yaml` becomes NaN (handled). But the `by_allocation_round`
rollup still emits rows keyed on the invalid window label, polluting the
Parquet with bogus cohort rows.
**Fix:** Clamp the label to known RO windows. Anything post-2017-03-31
should either be bucketed as `"post-2017-closed"` or excluded entirely:
```python
def _commissioning_window_label(commissioning_date) -> str:
    if commissioning_date is None or pd.isna(commissioning_date):
        return "pre-2013"
    ts = pd.Timestamp(commissioning_date)
    if ts < pd.Timestamp("2013-04-01"):
        return "pre-2013"
    if ts > pd.Timestamp("2017-03-31"):
        return "post-2017-closed"  # D-SCHEME closure
    start_year = ts.year if ts.month >= 4 else ts.year - 1
    return f"{start_year}/{str(start_year + 1)[-2:]}"
```
Real RO stations will never legitimately fall into this bucket, but data
quality in the Ofgem register has historical mis-classifications and
this guards against them.

### IN-05: Stub scraper output_path bound before RuntimeError — defensive but asymmetric

**File:** `src/uk_subsidy_tracker/data/ofgem_ro.py:114-117, 144-147`;
`src/uk_subsidy_tracker/data/roc_prices.py:87-90`
**Issue:** All three RO scrapers correctly bind `output_path` BEFORE the
`try:` block (D-17 discipline) and they also `mkdir` the parent directory
BEFORE the Option-D RuntimeError check. That means invoking
`download_ofgem_ro_register()` under Option D produces the side effect
of creating `data/raw/ofgem/` on disk before raising. The side-effect is
benign (directory is already committed), but the ordering is arguably
backwards: if the user invokes the function expecting to fail, they
don't expect to provoke a filesystem write. The test
`test_ofgem_ro_output_path_bound_before_try` pins `output_path = DATA_DIR`
appearing before `try:` (correct per D-17), but does NOT pin the
relative order of `mkdir` vs the RuntimeError guard.
**Fix:** Move the Option-D check above the `mkdir`:
```python
def download_ofgem_ro_register() -> Path:
    output_path = DATA_DIR / "raw" / "ofgem" / "ro-register.xlsx"
    if not _REGISTER_URL:
        raise RuntimeError(_OPTION_D_MSG)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        ...
```
Minor cleanup, consistent with the principle that guard clauses should
precede side-effects.

### IN-06: `roc_price_eroc` proxy can divide by zero

**File:** `src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py:74-76`
**Issue:** The proxy ROC price for the chart is computed as
`annual["cost_eroc_gbp"] / rocs` where `rocs = annual["rocs_issued"].where(...)`.
The `.where()` call converts zero-value rows to NaN, which makes the
division NaN-safe. However, `cost_eroc_gbp` could be a finite number
even when `rocs_issued == 0` if upstream data is inconsistent (e.g., a
scheme-year zero-generation month). The resulting NaN is plotted as a
gap in the line, which is the intended behaviour, but there is no
validate-time check that flags the upstream inconsistency. The visual
gap silently hides the issue.
**Fix:** Consider logging a warning (or adding a `validate()` Check 5)
if any annual bucket shows non-zero cost against zero ROCs — it would
indicate a cost-attribution bug upstream. Not a blocker; the current
chart behaviour is safe.

### IN-07: Empty-frame defensive handling is repetitive

**File:** `src/uk_subsidy_tracker/schemes/ro/cost_model.py:199-231, 236-239`;
`src/uk_subsidy_tracker/schemes/ro/aggregation.py:53-65, 108-117, 151-159`;
`src/uk_subsidy_tracker/schemes/ro/forward_projection.py:45-56, 67-80`
**Issue:** Every grain builder open-codes an empty-input short-circuit
with hand-typed column dtypes. The pattern repeats six times and each
instance has subtle differences (mutualisation_gbp as Float64 vs float64;
integer year columns as int64; string columns as object). This is the
root cause of WR-02 above. Factor a helper such as
`_empty_row_frame(row_model: type[BaseModel]) -> pd.DataFrame` that
consults the Pydantic model's field annotations and constructs the zero-
row frame with consistent dtypes.
**Fix:** Extract a module-level helper:
```python
def _empty_row_frame(row_model: type[BaseModel]) -> pd.DataFrame:
    """Produce an empty DataFrame with the row_model's column names and
    best-effort dtypes. Single source of truth for empty-frame handling."""
    ...
```
Then each builder calls it and appends `methodology_version`. Lowers the
WR-02 risk class to zero and reduces ~100 lines of boilerplate.

### IN-08: `validate()` Check 1 uses `.to_pandas()` without type stability

**File:** `src/uk_subsidy_tracker/schemes/ro/__init__.py:110, 119-122`
**Issue:** `pq.read_table(sm_path).to_pandas()` materialises the Parquet
into a pandas DataFrame; the subsequent `delta_pct` arithmetic uses
`.abs()` which fails on pd.NA Float64. The pattern works for float64
NaN (the arithmetic propagates), but if upstream dtype drift (WR-02)
lands Float64 into station_month, this check will either throw or
silently skip the divergent stations. Currently the stubs produce
no rows so the issue does not surface.
**Fix:** Cast `rocs_issued` and `rocs_computed` to `float` explicitly
at the start of Check 1:
```python
rocs_issued = nonzero_issued["rocs_issued"].astype(float)
rocs_computed = nonzero_issued["rocs_computed"].astype(float)
nonzero_issued["delta_pct"] = (
    (rocs_issued - rocs_computed).abs() / rocs_issued
)
```
Defensive but cheap.

---

_Reviewed: 2026-04-23T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
