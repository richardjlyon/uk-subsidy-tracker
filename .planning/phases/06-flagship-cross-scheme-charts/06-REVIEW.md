---
phase: 06-flagship-cross-scheme-charts
reviewed: 2026-04-25T00:00:00Z
depth: standard
files_reviewed: 36
files_reviewed_list:
  - CHANGES.md
  - docs/index.md
  - docs/portal/index.md
  - docs/portal/methodology.md
  - docs/portal/x1-stacked-total.md
  - docs/portal/x2-cumulative-premium.md
  - docs/portal/x3-per-household.md
  - docs/portal/x4-cost-per-mwh.md
  - docs/portal/x5-2022-crisis.md
  - docs/schemes/cfd.md
  - mkdocs.yml
  - src/uk_subsidy_tracker/data/uk_households.py
  - src/uk_subsidy_tracker/plotting/__main__.py
  - src/uk_subsidy_tracker/plotting/colors.py
  - src/uk_subsidy_tracker/plotting/portal/__init__.py
  - src/uk_subsidy_tracker/plotting/portal/x1_stacked_total.py
  - src/uk_subsidy_tracker/plotting/portal/x2_cumulative_premium.py
  - src/uk_subsidy_tracker/plotting/portal/x3_per_household.py
  - src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py
  - src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py
  - src/uk_subsidy_tracker/publish/manifest.py
  - src/uk_subsidy_tracker/refresh_all.py
  - src/uk_subsidy_tracker/schemas/__init__.py
  - src/uk_subsidy_tracker/schemas/portal.py
  - src/uk_subsidy_tracker/schemes/__init__.py
  - src/uk_subsidy_tracker/schemes/portal/__init__.py
  - src/uk_subsidy_tracker/schemes/portal/_refresh.py
  - src/uk_subsidy_tracker/schemes/portal/cross_scheme_model.py
  - tests/fixtures/benchmarks.yaml
  - tests/fixtures/constants.yaml
  - tests/test_aggregates.py
  - tests/test_benchmarks.py
  - tests/test_constants_provenance.py
  - tests/test_determinism.py
  - tests/test_headline_sync.py
  - tests/test_refresh_loop.py
  - tests/test_schemas.py
findings:
  critical: 0
  warning: 4
  info: 7
  total: 11
status: issues_found
---

# Phase 6: Code Review Report

**Reviewed:** 2026-04-25
**Depth:** standard
**Files Reviewed:** 36
**Status:** issues_found

## Summary

Phase 6 ships the cross-scheme portal: a third scheme module (`schemes/portal/`)
that joins CfD + RO `annual_summary.parquet` outputs into long-format
`data/derived/portal/cross_scheme.parquet`, five flagship X-charts, narrative
+ methodology docs, and a parametrised headline-sync regression test covering
seven cross-surface assertions.

Numerical correctness in the plotting layer is solid: NaN-generation rows are
explicitly dropped before any per-MWh division (X4, X5), the X3 per-household
divisor filters NaN/non-positive denominators, and the deterministic write
path inherits from `schemes/cfd/cost_model._write_parquet` (D-22). Provenance
discipline holds: `UK_HOUSEHOLDS` carries a structured `Provenance:` docstring,
its 11 per-year keys are tracked in `tests/fixtures/constants.yaml`, and the
SEED-001 drift tripwire fires on any silent edit. The `SCHEME_COLORS` palette
also carries a `Provenance:` block. Public-facing markdown is clinically
framed: REF Constable and Andrew Turver are described as "test-file tolerance
anchors", "NOT co-publishers" (`docs/portal/methodology.md` §"Reference
checks"), exactly per the project's adversarial-proofing posture.

The issues below are mostly correctness-edge or documentation-precision
concerns rather than security/data-loss problems. The most material warning
is a Pydantic schema vs Parquet contents mismatch (`households_uk: int`
declared non-nullable in `CrossSchemeRow`, but the column is written as
nullable `Int64` containing pd.NA for pre-2014 RO rows) — this drift surfaces
in published `cross_scheme.schema.json` and could mislead external consumers.

## Warnings

### WR-01: `households_uk` field nullability disagrees with on-disk Parquet

**File:** `src/uk_subsidy_tracker/schemas/portal.py:58-63`
**Issue:** `CrossSchemeRow.households_uk: int` is declared non-nullable
(no `| None`, no default). However, `cross_scheme_model.py:122` writes the
column as `pd.Int64Dtype()` (nullable Int64) populated via
`long["year"].map(UK_HOUSEHOLDS).astype("Int64")`. Pre-2014 RO rows have no
key in `UK_HOUSEHOLDS`, so `.map()` returns NaN and `Int64` carries pd.NA.

The schema test (`tests/test_schemas.py:296-301`) explicitly works around this
by skipping rows with NaN `households_uk` before Pydantic validation —
acknowledging the drift in test code rather than fixing the schema.

The published `cross_scheme.schema.json` (emitted by `emit_schema_json` from
`model_json_schema(mode="serialization")`) will declare `households_uk` as
`{"type": "integer"}` and add it to the `required` array. External consumers
following the GOV-01 contract (`manifest.json → schema.json → Parquet`) and
validating their reads against this schema will see validation errors for
every pre-2014 RO row — the schema and the data disagree.

This is the kind of "schema vs data drift" that hostile readers can use to
assert the project's reproducibility/provenance contract is broken.
**Fix:** Make the field explicitly nullable so the schema document matches
the on-disk content, and document the convention in the docstring (mirrors
the existing `generation_mwh: float | None = None` pattern on the same
model):
```python
households_uk: int | None = Field(
    default=None,
    description=(
        "ONS UK household count for year (per-year for X3 historical "
        "accuracy). None for pre-2014 RO rows where the ONS Families and "
        "Households series does not yet begin (RESEARCH Q3)."
    ),
    json_schema_extra={"dtype": "int64", "unit": "count", "nullable": True},
)
```
After this change, drop the NaN-skip workaround in
`tests/test_schemas.py:296-301` and replace with NaN-to-None coercion (same
pattern as the `generation_mwh` block immediately below). Update
`schemas/portal.py` module docstring per-row shape comment to reflect
nullability.

### WR-02: Homepage premium-card regex cannot match negative `£bn` values

**File:** `tests/test_headline_sync.py:159-162` (and corresponding render in `docs/index.md:26-30`)
**Issue:** `_HOMEPAGE_PREMIUM_RE` is
`r"\*\*£\s*(\d+(?:\.\d+)?)\s*bn\*\*\s*\n\s*\n\s+Premium over gas"`.
The capture group accepts only positive digits — there is no optional `-`
prefix and no handling of "saved" / "cheaper" adjective framing. The
parquet-derived value (`_homepage_premium_bn()`, line 87) sums signed
`premium_gbp` across schemes, which can be **negative** when CfD's clawback
exceeds RO's positive premium for the latest year (the cfd.md narrative
explicitly notes "cumulative net premium across all years is now negative"
post-2022 crisis).

Today's "£0.1 bn" is a marginal positive number; one CfD-favourable refresh
could flip the sign and the test would fail with "No headline found in
'homepage_premium'" — a confusing message that does not reveal the
sign-flip root cause. Worse, a maintainer might paper over by accepting
`£-0.1 bn` prose, which has no convention on this site.

**Fix:** Mirror the `cfd_premium` case pattern — accept a directional
adjective and use `compare_absolute=True`, OR explicitly handle the negative
case in the regex with an optional sign and adjacent "saved"/"premium"
adjective. Minimal change:
```python
_HOMEPAGE_PREMIUM_RE = re.compile(
    r"\*\*£\s*(-?\d+(?:\.\d+)?)\s*bn\*\*\s*\n\s*\n\s+Premium over gas",
    re.IGNORECASE,
)
```
The card text in `docs/index.md` should adopt a clinical sign convention
(e.g. "Net premium over gas" with a leading minus sign, or split into "X bn
above gas" / "X bn below gas" framing). Document the chosen convention in
`docs/portal/methodology.md` so a sign flip is a prose update, not a regex
update.

### WR-03: Portal `publish_latest()` silently emits stale `cross_scheme.parquet` if a per-scheme parquet is deleted

**File:** `src/uk_subsidy_tracker/schemes/portal/_refresh.py:32-43` (and
`src/uk_subsidy_tracker/schemes/portal/cross_scheme_model.py:46-82`)
**Issue:** The portal dirty-check skips missing scheme parquets:
```python
for src in _scheme_annual_summaries():
    if not src.exists():
        continue                           # silent skip
    if src.stat().st_mtime > cross_mtime:
        return True
```
Symmetrically, `_read_cfd_long()` and `_read_ro_long()` short-circuit on
absent parquets:
```python
if not src.exists():
    return pd.DataFrame()
```

If a maintainer or CI accident removes (or rotates out) `data/derived/cfd/
annual_summary.parquet` between two runs, the portal:
1. Reports `upstream_changed() = False` (no source mtime newer than the
   stale cross_scheme.parquet).
2. Even if forced to rebuild, would emit a cross_scheme.parquet without the
   CfD scheme rows — the `_read_cfd_long()` call returns an empty frame.
3. `validate()` Check 1 would catch the missing-CfD case (`SHIPPED_SCHEMES`
   intersection), but `validate()` runs AFTER `rebuild_derived()` writes
   the parquet — so a partial parquet may transiently ship.

This is the "silent fallback that masks data drift" pattern the project
posture explicitly forbids ("failures must be loud" per CLAUDE.md). A
hostile reader could exploit this if any CI artefact-rotation step prunes
derived files between the dirty-check and the build.

**Fix:** Make the absence of any `SHIPPED_SCHEMES` source parquet a hard
failure:
```python
def _read_cfd_long() -> pd.DataFrame:
    src = PROJECT_ROOT / "data" / "derived" / "cfd" / "annual_summary.parquet"
    if not src.exists():
        raise FileNotFoundError(
            f"CfD annual_summary.parquet missing — portal cannot build "
            f"without all SHIPPED_SCHEMES sources. "
            f"Run cfd.rebuild_derived() first."
        )
    ...
```
Apply the same to `_read_ro_long()`. In `_refresh.upstream_changed()`,
treat a missing source as "changed" so the next run attempts rebuild and
fails loudly rather than reusing a stale artefact:
```python
for src in _scheme_annual_summaries():
    if not src.exists():
        return True  # missing sources force rebuild — caller will raise loud
```

### WR-04: `_homepage_per_household_gbp()` indexes `households_uk.iloc[0]` without NaN guard

**File:** `tests/test_headline_sync.py:90-98`
**Issue:** The helper computes
```python
sub = df[df["year"] == year]
total_cost = float(sub["cost_gbp"].sum())
households = int(sub["households_uk"].iloc[0])
return float(total_cost / households)
```

Two correctness gaps:
1. **NaN propagation.** If `latest_fully_reconciled_year()` ever returns a
   year outside `UK_HOUSEHOLDS` keys (currently 2014–2024), the column for
   that year is all-NaN. `int(pd.NA)` raises `TypeError`, surfacing as a
   confusing test failure (not "headline drift", but a generic exception).
2. **Implicit assumption that all rows for the year carry the same
   households_uk.** Today this holds because `cross_scheme_model.py:122`
   maps via the year column unconditionally — but the contract is implicit;
   a future refactor that introduces region-keyed households (per-GB vs
   per-UK) would silently corrupt this calculation. The test would still
   pass with one scheme's denominator while the prose computes on another.

**Fix:** Use a defensive lookup that fails loudly on inconsistency:
```python
def _homepage_per_household_gbp() -> float:
    from uk_subsidy_tracker.schemes import portal
    df = pq.read_table(portal.DERIVED_DIR / "cross_scheme.parquet").to_pandas()
    year = portal.latest_fully_reconciled_year()
    sub = df[df["year"] == year].dropna(subset=["households_uk"])
    if sub.empty:
        raise RuntimeError(
            f"latest_fully_reconciled_year={year} has no rows with "
            f"non-null households_uk in cross_scheme.parquet"
        )
    households_unique = set(int(h) for h in sub["households_uk"].unique())
    if len(households_unique) != 1:
        raise RuntimeError(
            f"households_uk inconsistent across schemes for year {year}: "
            f"{households_unique}"
        )
    households = households_unique.pop()
    total_cost = float(sub["cost_gbp"].sum())
    return float(total_cost / households)
```

## Info

### IN-01: Methodology page cites the dataset landing URL, not the file URL captured in the sidecar

**File:** `docs/portal/methodology.md:48`
**Issue:** The page documents
`https://www.ons.gov.uk/peoplepopulationandcommunity/.../familiesandhouseholdsfamiliesandhouseholds`
(landing page) as the URL provenance for `UK_HOUSEHOLDS`. The
`.meta.json` sidecar (`data/raw/ons/familiesandhouseholdsuk2025.xlsx.meta.json`)
records the actual fetched URL as
`https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/.../current/familiesandhouseholdsuk2025.xlsx`.
A hostile reader checking GOV-01 four-way coverage will follow the prose URL
and not find the exact bytes that produced the sha256.
**Fix:** Document both — the landing page (for human readers) and the file
URL (for byte-exact reproducibility). Consider citing only the file URL with
a comment that it is the direct download link from the landing page.

### IN-02: X1 stack order can flip when CfD aggregate signed cost goes more negative than RO's positive

**File:** `src/uk_subsidy_tracker/plotting/portal/x1_stacked_total.py:59-62`
**Issue:** Stack order computes `df.groupby("scheme")["cost_gbp"].sum()` and
sorts ascending. This uses the **signed** cost. CfD `cost_gbp` includes
clawback years (2022 negative); the cfd.md narrative reports cumulative
**net** £-1.4bn at present. As the time window grows or another extreme
crisis year hits, CfD's aggregate could become more negative than RO's
positive, flipping the visual stack order between two consecutive refreshes
without any methodology change. The chart would silently re-render with a
reversed band order — confusing to repeat-readers comparing today's chart to
a screenshot from last week.
**Fix:** Sort by `abs(cost_gbp).sum()` so the stack-order rule is
"larger-magnitude band on top", which is monotonic in scheme size rather
than in signed direction. Or pin the order with an explicit
`UI_SPEC_STACK_ORDER` constant on `colors.py` alongside `SCHEME_COLORS`,
visited as Phase 7-12 schemes ship.

### IN-03: Public-docs phase-number references leak internal-roadmap nomenclature

**File:** `docs/index.md:64-99` (and `docs/portal/index.md:23`,
`docs/portal/methodology.md`, multiple X-chart pages with "Phase 7-12 schemes
will ship")
**Issue:** Public-facing markdown references "Phase 7", "Phase 8", … "Phase
12" as the future-coverage timeline. Per the project memory rule
`feedback_internal_artefacts_off_public_docs.md`, internal artefact
nomenclature (planning phase numbers) should not bleed into public-facing
docs unless explicitly required. The homepage cards show "Coming in Phase
7", "Coming in Phase 9 (modified methodology)", etc. — these will read as
internal jargon to journalists / academics who do not have ROADMAP.md open.
**Fix:** Replace "Phase 7-12" references in public-facing docs with
relative-time framing (e.g. "Coming in 2026", "Future module") or a
single canonical "Coming soon" + a single explicit cross-reference to the
public ROADMAP.md anchor for readers who want detail. Keeps the planning
nomenclature scoped to `.planning/` artefacts and `CHANGES.md`.

### IN-04: Code duplication: `EXCLUDED_SCHEMES` defined twice in plotting layer

**File:** `src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py:22-26`
+ `src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py:19-23`
**Issue:** The same `frozenset({"Capacity Market", "Balancing Services",
"Grid Socialisation"})` is declared verbatim in both X4 and X5 modules. A
future planner adding a new no-counterfactual scheme (Phase 9-11) must
remember to update both files. Single point of truth would be safer.
**Fix:** Move to `src/uk_subsidy_tracker/plotting/portal/__init__.py` (or
`schemes/portal/__init__.py` alongside `SHIPPED_SCHEMES`) as a module-level
constant; both X4 and X5 import it. Drop the per-file copy. Same pattern
also applies to `CRISIS_YEARS = (2021, 2022, 2023)` if any future chart
re-uses the crisis-window filter.

### IN-05: X4 / X5 chart subtitles assert exclusion in present tense even though no excluded rows exist today

**File:** `src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py:103`
+ `src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py:119`
**Issue:** Chart subtitle reads "Schemes without a gas counterfactual (CM,
Balancing, Grid) excluded — see methodology." But Phase 6 has not shipped
those schemes — the `EXCLUDED_SCHEMES` filter is documented in code as
"no-op in Phase 6". A hostile reader could question why the chart is
labelled with an exclusion that is not in effect.
**Fix:** Two acceptable framings:
1. Tense the subtitle to anticipate ("Schemes without a gas counterfactual
   *will be* excluded"), reverting to present tense when those schemes ship.
2. Keep the present-tense framing but qualify as "where applicable
   (currently no excluded scheme bands present)". Avoids the "exclusion is
   not in effect" line of attack.

### IN-06: `validate()` reads source parquets directly instead of going via the scheme module's `DERIVED_DIR`

**File:** `src/uk_subsidy_tracker/schemes/portal/__init__.py:127-146`
**Issue:** Check 3 hardcodes paths:
```python
sources = {
    "CfD": (cfd_mod.DERIVED_DIR / "annual_summary.parquet", "cfd_payments_gbp"),
    "RO": (ro_mod.DERIVED_DIR / "annual_summary.parquet", "ro_cost_gbp"),
}
```
This pattern bypasses the per-scheme `DERIVED_DIR` Protocol method (each
scheme module exposes its own `DERIVED_DIR` constant). Today the path
resolves identically; tomorrow when a scheme module changes its derived
location (e.g. moving to a per-version subdirectory), this validate() call
will silently misvalidate against a stale parquet. Better is to use a
loop driven by `SHIPPED_SCHEMES` and the scheme module's exposed
`DERIVED_DIR`:
```python
from uk_subsidy_tracker.schemes import cfd as cfd_mod, ro as ro_mod
COST_COLUMN_BY_SCHEME = {"CfD": (cfd_mod, "cfd_payments_gbp"),
                         "RO": (ro_mod, "ro_cost_gbp")}
for scheme_code, (mod, cost_col) in COST_COLUMN_BY_SCHEME.items():
    src = mod.DERIVED_DIR / "annual_summary.parquet"
    ...
```
Same architectural improvement applies to `_scheme_annual_summaries()` in
`schemes/portal/_refresh.py`. Already grep-discoverable; just no
single-source-of-truth in code.
**Fix:** Refactor as above; pin a unit test that asserts the iteration uses
the scheme module's exposed `DERIVED_DIR` so refactors are caught early.

### IN-07: ChartBuilder height parameter (600) declared inconsistently between X-charts

**File:** All five `x{1..5}_*.py` files (each declares `height=600` in the
`ChartBuilder` constructor, line ~134-138 in x1, ~58-62 in x2, etc.)
**Issue:** Each X-chart hard-codes `height=600`. UI-SPEC §"Component
Inventory" presumably has the canonical chart height. If UI-SPEC chooses
to change it (e.g. to 720 for higher-density displays), all five files
must be edited in lockstep, with no test to catch a drift.
**Fix:** Move to `src/uk_subsidy_tracker/plotting/portal/__init__.py` as
`PORTAL_CHART_HEIGHT: int = 600` with a brief docstring citing the UI-SPEC
clause. Each X-chart imports and uses the constant. Same applies to the
subtitle font color "#a0a4b8" repeated across all five files (lines 121,
91, 95, 105, 120 respectively).

---

_Reviewed: 2026-04-25_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
