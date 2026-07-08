# Phase 6: Flagship Cross-Scheme Charts — Research

**Researched:** 2026-04-25
**Domain:** Cross-scheme aggregation parquet + 5 flagship Plotly X-charts + portal homepage retrofit on a static MkDocs Material site
**Confidence:** HIGH (all primary findings verified against the live codebase + ran `mkdocs build --strict` + executed Plotly+kaleido smoke tests)

---

## Summary

Phase 6 sits on top of an unusually mature substrate. Two scheme modules (`schemes/cfd/` + `schemes/ro/`) already conform to the §6.1 five-function contract; their `annual_summary.parquet` outputs are the only data this phase needs to consume. The publishing pipeline (`publish/manifest.py`, `publish/csv_mirror.py`, `refresh_all.SCHEMES`) was deliberately refactored in Phase 05.2 to iterate over schemes, so adding a `("portal", portal)` entry should publish the cross-scheme parquet + CSV mirror with zero refactor. The chart pattern (`ChartBuilder.save(export_twitter=True, export_html=True, export_div=True)`) is a verbatim 5-step recipe with 11 live exemplars in `plotting/subsidy/`. The narrative-page template (Phase 3 D-01 6-section, exemplified by `docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md`) is locked. Headline-sync test pattern is exemplified by `tests/test_docs_ro_headline_sync.py`. The Provenance: docstring shape is exemplified by `src/uk_subsidy_tracker/counterfactual.py:CCGT_EFFICIENCY` and tracked in `tests/fixtures/constants.yaml`.

The schema mapping in CONTEXT D-02 is a clean fit: CfD has `cfd_payments_gbp` + `counterfactual_payments_gbp` + `premium_over_gas_gbp` + `cfd_generation_mwh`; RO has `ro_cost_gbp` + `gas_counterfactual_gbp` + `premium_gbp` + `ro_generation_mwh` (per (year, country) with `country='GB'` for the headline scope). A trivial column rename + per-scheme filter produces the long-format `year | scheme | cost_gbp | premium_gbp | generation_mwh | households_uk | methodology_version` shape verbatim. Today's `latest_fully_reconciled_year = 2023` (verified by `set(cfd.year) ∩ set(ro.year where ro_cost_gbp not null) = {2016, 2017, 2019, 2020, 2021, 2022, 2023}`; max = 2023).

The Plotly rangeselector (D-07) survives kaleido PNG export — both PNG and interactive HTML rendered cleanly in a smoke test (Plotly 6.7.0, kaleido 1.2.0). A subtle constraint: rangeselector requires `type="date"` on the x-axis, so X1's `year` column needs to be coerced to `pd.to_datetime(year, format='%Y')` in the plotting layer (parquet `year` stays `int64` per existing schema convention).

Two CONTEXT items need correction the planner must absorb: (1) `constants.yaml` lives at `tests/fixtures/constants.yaml`, NOT `src/uk_subsidy_tracker/data/constants.yaml` — the `uk_households` constant should be defined as a literal Python constant (or per-year dict) on a new `src/uk_subsidy_tracker/data/uk_households.py` module with a `Provenance:` docstring, and tracked in `tests/fixtures/constants.yaml` for SEED-001 Tier 2 drift detection. (2) The `manifest.py::GRAIN_SOURCES` registration is per-scheme dict-of-dicts; the planner must add a `"portal": {"cross_scheme": [...]}` entry alongside `"cfd"` and `"ro"`.

**Primary recommendation:** Build `schemes/portal/` as a third scheme module that mirrors `schemes/ro/__init__.py` shape verbatim — `refresh()` is a no-op, `upstream_changed()` mtime-compares each shipped scheme's `annual_summary.parquet` against `cross_scheme.parquet`, `rebuild_derived()` calls a new `cross_scheme_model.build_cross_scheme()` that reads each `annual_summary.parquet` and emits the long-format parquet + schema.json, `regenerate_charts()` delegates to `runpy.run_module("uk_subsidy_tracker.plotting", run_name="__main__")` (after the planner appends 5 X-chart `main()`s to the `__main__.py` charts list), `validate()` runs row-conservation + presence checks. Then register `("portal", portal)` as the LAST entry in `refresh_all.SCHEMES` so it runs after CfD + RO rebuilds in cron order.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01 New published `data/derived/portal/cross_scheme.parquet`.** Single canonical cross-scheme aggregation table joining all shipped scheme `annual_summary.parquet` files. All five X-charts read from this single file. Lands in `manifest.json` + CSV mirror.
- **D-02 Long-format row schema.** `year | scheme | cost_gbp | premium_gbp | generation_mwh | households_uk | methodology_version`. One row per scheme-year. X1 sums by year; X2 takes cumulative premium; X3 divides cost by households; X4 divides cost by generation. Future-scheme additions (Phases 7-12) are append-only rows — no schema migration. `households_uk` carried per-row so X3's per-household figure is reproducible from the parquet alone. `methodology_version` per-row inherits Phase 4 D-08 / GOV-04 discipline.
- **D-03 Test discipline = row-conservation + REF benchmark cross-check (with phase-6 caveat).** `tests/test_aggregates.py::test_cross_scheme_row_conservation` asserts sum of `cross_scheme.parquet[cost_gbp]` filtered by scheme-year equals each scheme's `annual_summary.parquet[year, total]` to a fixed GBP-tolerance. `tests/test_benchmarks.py::test_ref_total_reconciliation` asserts total UK subsidy approaches REF Constable's £25.8bn aggregate within a coverage-gap-aware tolerance. Determinism (Phase 4 D-21) inherited.
- **D-04 Single-row manifest entry.** `manifest.json` gains a `portal` scheme entry with `cross_scheme.parquet` + CSV mirror, source URL, retrieval timestamp, sha256, pipeline git SHA, methodology_version — same shape as `cfd` and `ro` entries.
- **D-05 Three top headline cards show covered-only totals + 'partial coverage' caveat.** No mixing of REF aggregate or external estimates with our reconstruction.
- **D-06 Time slice = latest fully-reconciled scheme year.** `latest_fully_reconciled_year` is the most recent year for which both CfD and RO have validated `annual_summary.parquet` rows. Apr-Mar (RO) vs calendar-year (CfD) mismatch reconciled in `docs/portal/methodology.md` with a footnote on the cards.
- **D-07 Plotly native rangeselector buttons in interactive HTML.** Single Plotly figure with `rangeselector` buttons (`1y` / `5y` / `All`) built into the chart. Twitter-PNG hero shows All-time view. Tabs only function in the interactive view — accepted tradeoff.
- **D-08 Unshipped schemes omitted from X1 stack with caveat in chart subtitle.** Chart subtitle reads "Covers 2 of 8 schemes — see scheme grid for coverage status."
- **D-09 Hardcoded markdown + regression test.** Headline figures live as plain text in `docs/index.md`, `docs/schemes/cfd.md`, and `docs/schemes/ro.md`. `tests/test_headline_sync.py` reads the parquet pipeline and asserts each prose figure matches to 1 decimal place. No mkdocs-macros plugin; no build-time substitution; no jinja templating layer.
- **D-10 Six placeholder scheme tiles keep current 'Coming in Phase N' labels, no headline figure.**
- **D-11 Single regression test covers all surfaces.** `tests/test_headline_sync.py` asserts: (a) homepage card numbers, (b) cfd.md headline numbers (£29bn paid + £14bn premium), (c) ro.md headline numbers (£58.6bn covered + £65-70bn range), (d) `cross_scheme.parquet` totals, (e) per-scheme `annual_summary.parquet` totals.
- **D-12 Cadence = every refresh + manual prose update via PR.**
- **D-13 Ship all five X-charts in Phase 6.** ROADMAP supersedes ARCH §11 P5's 'X1/X2/X3 only' wording.
- **D-14 New `docs/portal/` directory with one page per X-chart.** Files: `docs/portal/{x1-stacked-total,x2-cumulative-premium,x3-per-household,x4-cost-per-mwh,x5-2022-crisis}.md` + shared `docs/portal/methodology.md`.
- **D-15 X5 shape = vertical bar chart, per-scheme premium 2022 vs adjacent years.** X-axis = scheme; each scheme has 3 grouped bars for 2021 / 2022 / 2023 premium-per-MWh.
- **D-16 X4 + X5 omit schemes without gas counterfactual + footnote.** Capacity Market, Balancing, Grid Socialisation excluded once those modules ship.

### Claude's Discretion

- **Portal scheme module shape.** Planner-decided: `__init__.py` (contract entry points) + `cross_scheme_model.py` (the join logic) + module-level constants for households-count + scheme order. `refresh()` is effectively a no-op; `upstream_changed()` returns true when any scheme's `annual_summary.parquet` mtime is newer than `cross_scheme.parquet`.
- **`docs/portal/methodology.md` depth.** Matches `docs/methodology/gas-counterfactual.md` precedent — 5-10 paragraphs, length and section structure planner-decided.
- **Households-count constant source.** Planner sources URL + sha256 + retrieved_on per Phase 4 SEED-001 Tier 2 constants drift discipline. Per-year preferred for X3 historical accuracy.
- **`latest_fully_reconciled_year` precise definition.** Planner specifies the rule in `docs/portal/methodology.md`.
- **REF benchmark tolerance for partial-coverage phase.** Recommend option (b) — REF Constable Table 1 transcribes per-scheme; cross-checking CfD + RO subsets against REF's CfD + RO entries is methodologically cleaner than a coverage-fraction estimate.
- **mkdocs.yml nav placement of the Portal tier.** Top-level `Portal` tab vs sub-section under `Schemes`/`Themes`.
- **Atomic-commit slicing.** Suggested 7-wave grouping in CONTEXT.md.
- **Methodology version bump.** Planner decides whether portal-launch warrants 0.1.0 → 1.0.0.

### Deferred Ideas (OUT OF SCOPE)

- mkdocs-macros plugin / live-binding via macros (D-09 explicit reject).
- Calendar-year vs scheme-year normalisation as a project-wide axis convention.
- Three-tier headline display ('reconstructed' + 'full UK estimate' + 'gap').
- REF benchmark line on X1 chart.
- `@pytest.mark.skip` on `test_ref_total_reconciliation` until coverage > 70%.
- Per-technology decomposition on cross_scheme.parquet rows.
- METHODOLOGY_VERSION 0.1.0 → 1.0.0 bump (planner-decided).
- External URL redirects.
- Methodology page split (one per X-chart vs one shared).
- Headline-sync test parametrisation per surface.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| X-01 | Total UK subsidy stacked by scheme, annual, all-time | Cross-scheme parquet schema (D-02 / §"Cross-scheme parquet schema"); X1 plotting recipe inherits `plotting/subsidy` 5-step pattern; rangeselector API verified to survive kaleido export (§"Plotly rangeselector specifics") |
| X-02 | Combined premium over gas, cumulative | `cross_scheme.parquet[premium_gbp].cumsum()` — column carried per-row per D-02; works on the 7-year reconciled span (2016-2017 + 2019-2023) |
| X-03 | Cost per household decomposed by scheme | `cross_scheme.parquet[cost_gbp / households_uk]`; `households_uk` carried per-row per D-02; ONS Families and Households 2025 dataset is the verified source (§"ONS UK households source") |
| X-04 | Cost per MWh of subsidised generation by scheme | `cross_scheme.parquet[cost_gbp / generation_mwh]`; D-16 footnote excludes CM/Balancing/Grid (Phase 9-11 schemes — N/A in Phase 6) |
| X-05 | 2022 crisis comparison: vertical bar chart, per-scheme premium 2021/2022/2023 | `cross_scheme.parquet` filter `year ∈ {2021,2022,2023}`; both CfD + RO have rows for all three years (verified by inspection) |
| PORTAL-01 | Portal homepage renders 3 headline cards + X1 chart with rangeselector + 2×4 scheme grid | Headline cards = Material `grid cards` extension (already used at `docs/themes/cost/index.md` lines 9-59); X1 hero embed = inherited PNG + `[Interactive version]` pattern; 2×4 grid carries forward from Phase 05.1 D-10 (already in `docs/index.md` line 22-76) |
| PORTAL-02 | Each populated scheme tile links to its scheme detail page | Already implemented for CfD + RO in current `docs/index.md` (lines 24, 32 → `schemes/cfd.md`, `schemes/ro.md` without anchor — UI-SPEC §3 confirms top-of-page link convention for homepage tiles); placeholder tiles are non-clickable text |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **Python 3.12+** only (`requires-python = ">=3.12"`). No Rust, Go, Polars-migration, non-Python frameworks.
- **Parquet + DuckDB** as the analytical engine. No relational DB. (DuckDB is declared as a dependency for future use; current code uses `pandas + pyarrow`.)
- **Cloudflare Pages static hosting** only. No backend, no containers, no workflow engines beyond GitHub Actions cron.
- **Plotly 6.x** (verified: `Plotly 6.7.0` installed) + **kaleido ≥1.2.0** (verified: `kaleido 1.2.0`) for PNG export.
- **MkDocs Material** (no JS build pipeline; ships with `attr_list`, `md_in_html`, `pymdownx.superfences` already enabled).
- **Provenance:** every Parquet file carries source hash, retrieval timestamp, pipeline git SHA. `cross_scheme.parquet` inherits via `manifest.py` per-scheme iteration.
- **Reproducibility:** `git clone + uv sync + one command` must reproduce every published number byte-identically. Determinism is a hard contract on `cross_scheme.parquet` (D-21 + D-03).
- **Adversarial-proofing:** every PRODUCTION chart = narrative + methodology + test + source-file link (GOV-01 four-way coverage).
- **GSD workflow:** all file edits go through a GSD command. No direct edits.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Cross-scheme aggregation join (`annual_summary.parquet × N → cross_scheme.parquet`) | Derived layer (`schemes/portal/cross_scheme_model.py`) | — | Pure function of per-scheme parquet content; lives in the scheme-module tier per ARCH §6.1 |
| Cross-scheme parquet schema (Pydantic row model + JSON Schema sibling) | Schema layer (`schemas/portal.py`) | — | Mirrors `schemas/cfd.py` + `schemas/ro.py` discipline; reuses `emit_schema_json` from `schemas/cfd.py` (D-10 contract) |
| 5 X-chart figures + Twitter PNG + interactive HTML + div HTML | Plotting layer (`plotting/portal/`) | — | Inherits `ChartBuilder.save(export_twitter=True, export_html=True, export_div=True)` recipe; new `plotting/portal/` directory mirrors `plotting/subsidy/` shape |
| Plotly rangeselector buttons on X1 (1y/5y/All) | Plotting layer (`plotting/portal/x1_stacked_total.py`) | — | Native Plotly API; no JS build pipeline. Buttons appear in `.html` only; `_twitter.png` is static "All" view |
| Cross-scheme parquet publishing (CSV mirror + `manifest.json` entry) | Publishing layer (`publish/manifest.py`, `publish/csv_mirror.py`) | — | Already iterates `refresh_all.SCHEMES`; planner adds `"portal"` entry to `GRAIN_SOURCES`/`GRAIN_TITLES`/`GRAIN_DESCRIPTIONS` dicts |
| Daily refresh orchestration (CfD → RO → portal) | CI orchestration (`refresh_all.SCHEMES`, `.github/workflows/refresh.yml`) | — | Append `("portal", portal)` AFTER `("cfd", cfd)` and `("ro", ro)`; `upstream_changed()` mtime-checks gate the rebuild |
| Headline-sync regression test (homepage + cfd.md + ro.md vs parquet totals) | Test layer (`tests/test_headline_sync.py`) | — | Generalises `tests/test_docs_ro_headline_sync.py` per D-11; single test file, parametrised over surface |
| Row-conservation invariant on cross_scheme parquet | Test layer (`tests/test_aggregates.py::test_cross_scheme_row_conservation`) | — | Extends existing per-scheme parametrisation pattern (Plan 05-10) |
| REF Constable Table 1 cross-check (per-scheme subset) | Test layer (`tests/test_benchmarks.py::test_ref_total_reconciliation`) | — | Sibling of `test_ref_constable_ro_reconciliation`; per-scheme tolerance dispatch via existing `_TOLERANCE_BY_SOURCE` shape |
| Schema-conformance test for cross_scheme parquet | Test layer (`tests/test_schemas.py`) | — | Parametrise existing `_GRAIN_MODELS` pattern over portal grain |
| Determinism test for cross_scheme parquet | Test layer (`tests/test_determinism.py`) | — | Parametrise existing `RO_GRAINS`-style pattern |
| Constants drift gate on `uk_households` | Test layer (`tests/test_constants_provenance.py`) | — | Add `UK_HOUSEHOLDS_*` synthetic keys to `_TRACKED` set; mirror `DEFAULT_CARBON_PRICES_YYYY` per-year pattern |
| Portal homepage retrofit (3 cards + caveat + X1 hero + scheme grid) | Markdown (`docs/index.md`) | — | Material `grid cards` extension only; no template engine |
| 5 X-chart narrative pages + shared methodology page | Markdown (`docs/portal/`) | — | Phase 3 D-01 6-section template; mirrors `docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md` |
| Portal nav tier registration | MkDocs config (`mkdocs.yml`) | — | Top-level `Portal:` tab per UI-SPEC §6 lock; alternative: under Schemes/Themes (planner-decided per CONTEXT) |

---

## Cross-scheme parquet schema (D-02)

### Concrete column-by-column mapping

The CONTEXT D-02 long-format target is:

```
year | scheme | cost_gbp | premium_gbp | generation_mwh | households_uk | methodology_version
```

Verified against the live per-scheme parquets (`uv run python -c "import pandas; ..."`):

**CfD `data/derived/cfd/annual_summary.parquet`** — 11 rows (years 2016-2026; 2026 is partial); columns:
```
year (int64) | cfd_generation_mwh (float64) | cfd_payments_gbp (float64) |
counterfactual_payments_gbp (float64) | premium_over_gas_gbp (float64) |
methodology_version (string)
```

**RO `data/derived/ro/annual_summary.parquet`** — 22 rows (per-(year, country); years 2006-2017 + 2019-2024; 2024 cost = NaN; 2018 missing per Phase 05.2 SY17 deferral); columns:
```
year (int64) | country (string='GB'|'NI') | ro_generation_mwh (float64) |
ro_cost_gbp (float64) | ro_cost_gbp_eroc (object — always None under aggregate grain) |
gas_counterfactual_gbp (float64) | premium_gbp (float64) |
mutualisation_gbp (float64, nullable) | methodology_version (string)
```

### Long-format mapping

| Cross-scheme column | CfD source | RO source | Notes |
|---------------------|------------|-----------|-------|
| `year` | `year` (int64) | `year` (int64) | RO year is the OBLIGATION-YEAR START calendar year per `aggregate_model.py:Defect 3 fix` (matches REF Constable convention) |
| `scheme` | literal `"CfD"` | literal `"RO"` | Stable string keys; sort order = alphabetical for D-21 determinism |
| `cost_gbp` | `cfd_payments_gbp` | `ro_cost_gbp` (GB rows only) | RO NI rows are excluded from headline scope per RO D-12 (`country == 'GB'` filter at the join site) |
| `premium_gbp` | `premium_over_gas_gbp` | `premium_gbp` (GB rows only) | Sign convention identical: cost − counterfactual; negative = scheme cheaper than gas (e.g. CfD 2022) |
| `generation_mwh` | `cfd_generation_mwh` | `ro_generation_mwh` (GB rows only) | RO pre-SY18 generation is NaN (12-year XLSX has ROCs only, no MWh data per `aggregate_model.py` Defect 1 fix); X4 + X5 must handle NaN-divides cleanly |
| `households_uk` | per-year ONS lookup | per-year ONS lookup | Same value for both scheme rows in a given year (denominator is national, not scheme-specific) |
| `methodology_version` | `methodology_version` (string) | `methodology_version` (string) | Currently `'0.1.0'` for both; D-12 requires per-row carry-through |

### Column-rename / null-handling hazards (for the planner)

1. **RO `country` filter** — the RO parquet has BOTH `country='GB'` and `country='NI'` rows for years 2021-2024. Cross-scheme aggregation must filter `country == 'GB'` (matches `tests/test_benchmarks.py:ro_annual_totals_gbp_bn` fixture and ro.md headline scope D-12). Failing to filter would double-count NI as a separate "scheme".
2. **RO `ro_cost_gbp` NaN for SY1-SY4 + 2024** — pre-2006 years are absent from `annual_summary.parquet`; 2024 has cost=NaN (price-data-gated). Cross-scheme model should DROP NaN-cost rows so X1 stack doesn't render zero-bands. Confirmed: RO complete years (cost not null) = `{2006-2017, 2019-2023}` (16 years).
3. **CfD 2026 partial** — CfD `annual_summary.parquet` has 2026 row with non-NaN cost (~£0.86bn YTD partial). Cross-scheme model should still emit the row (it IS valid year-to-date data); the `latest_fully_reconciled_year` rule excludes partial years from the HEADLINE — but X1's All-time stack legitimately shows all years including in-progress ones.
4. **RO year=2018 GAP** — Phase 05.2 SY17 deferral leaves an explicit hole in the RO time series. X1 stacked chart will show the CfD band but no RO band at year=2018; the partial-coverage caveat in the chart subtitle covers this. The headline-sync test must NOT fail on year=2018 (it is a documented gap, tracked in backlog 999.3).
5. **`ro_cost_gbp_eroc` is NOT carried** to cross_scheme.parquet — it's a sensitivity column irrelevant to the cross-scheme story.
6. **`mutualisation_gbp`** is NOT carried — already folded into `ro_cost_gbp` per RO D-11 ("primary cost includes mutualisation per consumer-cost view").

### Suggested Pydantic row model (`src/uk_subsidy_tracker/schemas/portal.py`)

```python
# Source: mirrors schemas/cfd.py:AnnualSummaryRow + schemas/ro.py:RoAnnualSummaryRow
from pydantic import BaseModel, Field
from uk_subsidy_tracker.schemas.cfd import emit_schema_json  # noqa: F401 (re-exported)


class CrossSchemeRow(BaseModel):
    """One row in portal/cross_scheme.parquet (per (year, scheme), D-02)."""

    year: int = Field(
        description="Calendar year (CfD CY) or RO obligation-year start.",
        json_schema_extra={"dtype": "int64", "unit": "year"},
    )
    scheme: str = Field(
        description="Scheme code: 'CfD', 'RO', + future ('FiT', 'Constraints', etc.).",
        json_schema_extra={"dtype": "string"},
    )
    cost_gbp: float = Field(
        description="Total scheme cost for (year, scheme); GB-only for RO.",
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    premium_gbp: float = Field(
        description="cost_gbp - gas_counterfactual_gbp; negative when scheme cheaper than gas.",
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    generation_mwh: float | None = Field(
        default=None,
        description="Subsidised generation MWh; None for pre-SY18 RO years (XLSX has no MWh).",
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    households_uk: int = Field(
        description="ONS UK household count for `year` (per-year for X3 historical accuracy).",
        json_schema_extra={"dtype": "int64", "unit": "count"},
    )
    methodology_version: str = Field(
        description="counterfactual.METHODOLOGY_VERSION provenance stamp (D-12 / GOV-04).",
        json_schema_extra={"dtype": "string"},
    )
```

[VERIFIED: `data/derived/cfd/annual_summary.parquet` + `data/derived/ro/annual_summary.parquet` inspected via pandas 2026-04-25]

---

## Plotly rangeselector specifics (D-07)

### Verified API (Plotly 6.7.0 + kaleido 1.2.0)

```python
# Source: smoke-tested 2026-04-25 against plotly 6.7.0 + kaleido 1.2.0;
# both PNG (kaleido) and HTML write_html() succeeded with both x-axis types.
import pandas as pd
import plotly.graph_objects as go

# X1 'year' column comes from cross_scheme.parquet as int64. Coerce to datetime
# at the plotting boundary (cross_scheme.parquet stays int64 for D-21 determinism).
df = ...  # read cross_scheme.parquet
df["year_dt"] = pd.to_datetime(df["year"], format="%Y")

fig = go.Figure()
for scheme_name, sub in df.groupby("scheme", sort=False):
    fig.add_trace(go.Bar(
        x=sub["year_dt"],
        y=sub["cost_gbp"] / 1e9,
        name=scheme_name,
        marker_color=SCHEME_COLORS[scheme_name],  # see UI-SPEC §Color
        hovertemplate="%{x|%Y}<br>" + scheme_name + "<br>£%{y:.2f} bn<extra></extra>",
    ))

fig.update_layout(barmode="stack")

fig.update_xaxes(
    rangeselector=dict(
        buttons=[
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(count=5, label="5y", step="year", stepmode="backward"),
            dict(step="all", label="All"),
        ],
        # UI-SPEC §Typography: top-left of plotting area
        xanchor="left",
        yanchor="bottom",
        x=0.0,
        y=1.02,
    ),
    type="date",  # REQUIRED — rangeselector needs a date-typed axis
)
```

### Key facts

[VERIFIED: smoke test 2026-04-25] kaleido PNG export succeeds for figures with rangeselector. The buttons render as visible UI in both PNG (12,478 bytes for a small smoke chart) and HTML. The CONTEXT D-07 statement "Twitter-PNG hero shows All-time view (no rangeselector buttons; PNG is a static hero)" is achievable in two equivalent ways:
- **Option A (recommended):** Build TWO figures — `fig_html` with rangeselector for `.html` + `.div.html` export, `fig_png` without rangeselector (just `update_xaxes(type='date')`) for `_twitter.png`. Cleanest separation; matches UI-SPEC §2 intent.
- **Option B:** Build ONE figure with rangeselector; the buttons WILL appear in the PNG. UI-SPEC §"X1 hero embed" reads "PNG shows **All-time view** (no rangeselector buttons; PNG is a static hero)" — so Option A is mandatory for PNG cleanliness.

[VERIFIED: Plotly docs] rangeselector requires `type="date"` on the x-axis. Integer years work IF coerced via `type="date"` (Plotly auto-promotes ints to a numeric date axis), but the cleanest path is `pd.to_datetime(year, format='%Y')`.

[CITED: [Plotly Range Slider docs](https://plotly.com/python/range-slider/)] Default rangeselector position is above the plot area at top-left; the x/y/xanchor/yanchor params override it. UI-SPEC §Typography specifies `xanchor="left", yanchor="bottom", x=0.0, y=1.02`.

### Default-active button on page load

Per UI-SPEC §"X1 hero embed", default is `All`. Plotly defaults to "All" automatically when no `active` button index is set (the last button in the list, `step="all"`, is the natural default). If the planner wants to force this, set `rangeselector=dict(buttons=[...], active=2)` (0-indexed; 2 = "All" in the 3-button list).

### Survives ChartBuilder.save() pipeline

`ChartBuilder.save()` (chart_builder.py:310-393) calls `fig.write_html()` + `fig.write_image()` with no figure mutation beyond an attribution annotation. The rangeselector dict on `fig.layout.xaxis` is preserved end-to-end.

### Hazard

Per the Plotly 6.x API, `fig.update_xaxes(rangeselector=...)` only applies to the FIRST x-axis. For multi-panel charts (X-charts X1-X5 are single-panel per UI-SPEC, so this is non-issue) the rangeselector would need to be set on each x-axis explicitly with `fig.update_xaxes(rangeselector=..., row=R, col=C)`.

---

## `schemes/portal/` module shape (§6.1)

### File layout (mirrors `schemes/ro/`)

```
src/uk_subsidy_tracker/schemes/portal/
├── __init__.py              # §6.1 contract entry points
├── _refresh.py              # upstream_changed() + refresh() (no-op)
└── cross_scheme_model.py    # build_cross_scheme(): the long-format join
```

### `__init__.py` skeleton (verbatim contract)

```python
"""Portal scheme module — ARCHITECTURE §6.1 contract.

Five module-level callables satisfying the SchemeModule Protocol declared in
schemes.__init__. The portal is downstream of all per-scheme refreshes — it
reads each shipped scheme's annual_summary.parquet and emits cross_scheme.parquet.

refresh() is a no-op: there is no upstream URL for the portal to fetch.
upstream_changed() returns True when any scheme's annual_summary.parquet mtime
is newer than cross_scheme.parquet (forcing a downstream rebuild).
rebuild_derived() reads each shipped scheme's annual_summary.parquet, joins
into the long-format cross_scheme.parquet, emits + schema.json sibling.
regenerate_charts() delegates to the existing plotting __main__ entry point
(the new plotting/portal/x1..x5 modules are appended to its charts list).
validate() runs row-conservation + presence checks.

Protocol conformance::
    >>> from uk_subsidy_tracker.schemes import portal, SchemeModule
    >>> isinstance(portal, SchemeModule)
    True
"""
from __future__ import annotations

from pathlib import Path

from uk_subsidy_tracker import PROJECT_ROOT
from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.schemes.portal._refresh import (
    refresh as _refresh,
    upstream_changed as _upstream_changed,
)

DERIVED_DIR: Path = PROJECT_ROOT / "data" / "derived" / "portal"

# Stable registration order — appended to as Phases 7-12 ship new schemes.
# Order is the visual band-stacking order on X1 (alphabetical by scheme code,
# bottom-to-top by total cost — UI-SPEC §"Stack order on X1" reorders at render time).
SHIPPED_SCHEMES: tuple[str, ...] = ("CfD", "RO")


def upstream_changed() -> bool:
    return _upstream_changed()


def refresh() -> None:
    _refresh()  # no-op; the portal has no upstream URL


def rebuild_derived(output_dir: Path | None = None) -> None:
    target = output_dir if output_dir is not None else DERIVED_DIR
    target.mkdir(parents=True, exist_ok=True)
    from uk_subsidy_tracker.schemes.portal.cross_scheme_model import build_cross_scheme
    build_cross_scheme(target)


def regenerate_charts() -> None:
    import runpy
    runpy.run_module("uk_subsidy_tracker.plotting", run_name="__main__")


def validate() -> list[str]:
    """Three checks: presence, row-conservation against per-scheme parquets, methodology_version."""
    import pyarrow.parquet as pq
    import pandas as pd

    warnings: list[str] = []
    cross = DERIVED_DIR / "cross_scheme.parquet"
    if not cross.exists():
        return [f"validate: {cross} missing — run rebuild_derived()"]
    df = pq.read_table(cross).to_pandas()

    # Check 1: every shipped scheme has at least one row.
    schemes_present = set(df["scheme"].unique().tolist())
    missing = set(SHIPPED_SCHEMES) - schemes_present
    if missing:
        warnings.append(f"validate: missing scheme rows: {missing}")

    # Check 2: methodology_version matches live constant.
    versions = set(df["methodology_version"].dropna().unique().tolist())
    if versions and versions != {METHODOLOGY_VERSION}:
        warnings.append(
            f"validate: methodology_version drift — column has {versions!r}, "
            f"constant is {METHODOLOGY_VERSION!r}"
        )

    # Check 3: per-scheme cost reconciliation against source annual_summary.
    from uk_subsidy_tracker.schemes import cfd as cfd_mod, ro as ro_mod
    sources = {"CfD": cfd_mod.DERIVED_DIR / "annual_summary.parquet",
               "RO":  ro_mod.DERIVED_DIR  / "annual_summary.parquet"}
    for scheme_code, src in sources.items():
        if not src.exists():
            continue
        src_df = pq.read_table(src).to_pandas()
        if scheme_code == "RO":
            src_df = src_df[src_df["country"] == "GB"]
        cost_col = "cfd_payments_gbp" if scheme_code == "CfD" else "ro_cost_gbp"
        src_total = float(src_df[cost_col].dropna().sum())
        cross_total = float(df[df["scheme"] == scheme_code]["cost_gbp"].sum())
        if src_total > 0 and abs(cross_total - src_total) / src_total > 0.001:
            warnings.append(
                f"validate: {scheme_code} cost drift — cross_scheme £{cross_total:,.0f} "
                f"vs annual_summary £{src_total:,.0f} (>0.1%)"
            )

    return warnings


__all__ = [
    "DERIVED_DIR", "SHIPPED_SCHEMES",
    "upstream_changed", "refresh", "rebuild_derived",
    "regenerate_charts", "validate",
]
```

### `_refresh.py` skeleton

```python
"""Portal dirty-check — mtime-based against shipped scheme parquets.

upstream_changed() returns True when any shipped scheme's annual_summary.parquet
mtime is newer than cross_scheme.parquet, OR cross_scheme.parquet is absent.
"""
from __future__ import annotations

from pathlib import Path

from uk_subsidy_tracker import PROJECT_ROOT


def _scheme_annual_summaries() -> list[Path]:
    return [
        PROJECT_ROOT / "data" / "derived" / "cfd" / "annual_summary.parquet",
        PROJECT_ROOT / "data" / "derived" / "ro"  / "annual_summary.parquet",
        # Phases 7-12 append here (one path per scheme).
    ]


def upstream_changed() -> bool:
    cross = PROJECT_ROOT / "data" / "derived" / "portal" / "cross_scheme.parquet"
    if not cross.exists():
        return True
    cross_mtime = cross.stat().st_mtime
    for src in _scheme_annual_summaries():
        if not src.exists():
            continue
        if src.stat().st_mtime > cross_mtime:
            return True
    return False


def refresh() -> None:
    """No-op — portal has no upstream URL to fetch."""
    return None
```

### `cross_scheme_model.py` skeleton

```python
"""Cross-scheme aggregation — long-format join over shipped scheme annual_summary parquets.

Determinism (D-21): pure function of upstream parquet content. Final sort is
(year ASC, scheme ASC). No clock reads, no randomness. Uses the shared
deterministic Parquet writer from schemes/cfd/cost_model._write_parquet (D-22).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from uk_subsidy_tracker import PROJECT_ROOT
from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.data.uk_households import UK_HOUSEHOLDS  # see §"Provenance"
from uk_subsidy_tracker.schemas.portal import CrossSchemeRow, emit_schema_json
from uk_subsidy_tracker.schemes.cfd.cost_model import _write_parquet  # shared D-22 writer


def _read_cfd_long() -> pd.DataFrame:
    src = PROJECT_ROOT / "data" / "derived" / "cfd" / "annual_summary.parquet"
    if not src.exists():
        return pd.DataFrame()
    df = pq.read_table(src).to_pandas()
    return pd.DataFrame({
        "year": df["year"],
        "scheme": "CfD",
        "cost_gbp": df["cfd_payments_gbp"],
        "premium_gbp": df["premium_over_gas_gbp"],
        "generation_mwh": df["cfd_generation_mwh"],
        "methodology_version": df["methodology_version"],
    })


def _read_ro_long() -> pd.DataFrame:
    src = PROJECT_ROOT / "data" / "derived" / "ro" / "annual_summary.parquet"
    if not src.exists():
        return pd.DataFrame()
    df = pq.read_table(src).to_pandas()
    # D-12: GB-only headline scope. Drop NI rows and NaN-cost rows.
    df = df[(df["country"] == "GB") & df["ro_cost_gbp"].notna()]
    return pd.DataFrame({
        "year": df["year"],
        "scheme": "RO",
        "cost_gbp": df["ro_cost_gbp"],
        "premium_gbp": df["premium_gbp"],
        "generation_mwh": df["ro_generation_mwh"],
        "methodology_version": df["methodology_version"],
    })


def build_cross_scheme(output_dir: Path) -> pd.DataFrame:
    """Emit cross_scheme.parquet + cross_scheme.schema.json under output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)

    parts = [_read_cfd_long(), _read_ro_long()]  # Phases 7-12 append here
    parts = [p for p in parts if not p.empty]
    long = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(
        columns=["year", "scheme", "cost_gbp", "premium_gbp",
                 "generation_mwh", "methodology_version"],
    )

    # Per-year UK households join (per CONTEXT Discretion: per-year preferred).
    long["households_uk"] = long["year"].map(UK_HOUSEHOLDS).astype("int64")

    columns = list(CrossSchemeRow.model_fields.keys())
    long = (long[columns]
            .sort_values(["year", "scheme"], kind="mergesort")
            .reset_index(drop=True))

    _write_parquet(long, output_dir / "cross_scheme.parquet")
    emit_schema_json(CrossSchemeRow, output_dir / "cross_scheme.schema.json")
    return long
```

### `schemes/__init__.py` registration (one-line append)

```python
# Source: src/uk_subsidy_tracker/schemes/__init__.py:54
from uk_subsidy_tracker.schemes import cfd, ro, portal  # noqa: E402

__all__ = ["SchemeModule", "cfd", "ro", "portal"]
```

### `refresh_all.SCHEMES` registration (one-line append)

```python
# Source: src/uk_subsidy_tracker/refresh_all.py:36-39
from uk_subsidy_tracker.schemes import cfd, portal, ro

SCHEMES = (
    ("cfd", cfd),
    ("ro", ro),
    ("portal", portal),  # MUST be last — downstream of all per-scheme rebuilds
)
```

The existing `refresh_all.publish_latest()` already iterates `SCHEMES` and calls `manifest_mod.build(schemes=SCHEMES, ...)`, so the manifest registration is automatic provided `manifest.GRAIN_SOURCES["portal"]` is populated.

### `manifest.py` GRAIN_* registration (3-key dict-of-dicts append)

```python
# Source: src/uk_subsidy_tracker/publish/manifest.py:71-150
GRAIN_SOURCES["portal"] = {
    "cross_scheme": [
        # Portal reads downstream parquets, but raw provenance flows from each
        # shipped scheme's raw inputs. List the union of CfD + RO raw files so
        # the manifest entry's `sources[]` block traces back to primary regulator
        # data.
        "lccc/actual-cfd-generation.csv",
        "lccc/cfd-contract-portfolio-status.csv",
        "ons/gas-sap.xlsx",
        "elexon/system-prices.csv",
        "ofgem/ro-generation.csv",
        "ofgem/ro-annual-aggregate.csv",
        "ofgem/roc-prices.csv",
    ],
}
GRAIN_TITLES["portal"] = {"cross_scheme": "Cross-scheme annual aggregation (CfD + RO)"}
GRAIN_DESCRIPTIONS["portal"] = {"cross_scheme": "year × scheme"}
```

[VERIFIED: `src/uk_subsidy_tracker/publish/manifest.py:_assemble_dataset_entries` discovers grains via `scheme_derived.glob('*.parquet')` — adding the GRAIN_* entries above is sufficient.]

---

## ONS UK households source

### Canonical source

[CITED: [ONS Families and households dataset](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/datasets/familiesandhouseholdsfamiliesandhouseholds)]

| Property | Value |
|----------|-------|
| Dataset | "Families and households" |
| Current edition file | `familiesandhouseholdsuk2025.xlsx` (204.2 KB) |
| Publisher URL | `https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/datasets/familiesandhouseholdsfamiliesandhouseholds` |
| Latest publication | 17 April 2026 |
| Update cadence | Annual (LFS quarterly survey, April-June reference quarter) |
| Headline 2024 figure | 28.6 million UK households (7.0% increase from 26.7M in 2014) |
| Methodology | Labour Force Survey (~40,000 households per quarter) |

### Per-year vs single-value

CONTEXT Discretion: "Per-year preferred for X3 historical accuracy." The "Families and households" XLSX contains a multi-year time series (2014-2024 in the 2025 edition); each year's household count is published as a single integer. Per-year is the right call for X3 because the per-household division denominator changes ~7% over the chart's time window.

### Suggested constant module: `src/uk_subsidy_tracker/data/uk_households.py`

```python
"""UK households-count constant — ONS Families and Households time series.

Phase 6 cross-scheme X3 chart denominator. Per-year for historical accuracy
(2014: 26.7M; 2024: 28.6M — 7% drift would mis-scale early bars by 7%).

Provenance:
  source:       ONS Families and Households Dataset 2025 edition
  url:          https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/datasets/familiesandhouseholdsfamiliesandhouseholds
  basis:        Labour Force Survey April-June quarter; UK total of single-family
                + multi-family + lone-person households.
  retrieved_on: 2026-04-25
  next_audit:   2027-04-30  (ONS publishes annually in April)
  file:         familiesandhouseholdsuk2025.xlsx (204.2 KB)
  sha256:       <planner computes during Wave 1; raw file lives in data/raw/ons/>
"""
from __future__ import annotations

# Per-year UK household count (millions, expressed as integer count).
# Source: ONS Families and Households 2025 edition, Table 1 ("Households by type").
# Planner verifies each value during Wave 1 transcription.
UK_HOUSEHOLDS: dict[int, int] = {
    # 2006: ...,  # transcribe from "Families and Households" historical archive
    # 2007: ...,
    # ...
    # 2014: 26_700_000,  # ONS published figure rounded to nearest 100k
    # 2015: ...,
    # ...
    2024: 28_600_000,  # ONS published, 17 April 2026 release
}
"""Per-year UK households count (households, not millions). Keys cover the
union of years present in cross_scheme.parquet; values are the ONS-published
figure for that year.

For SY years before ONS data is available (RO pre-2006), use the earliest
ONS figure (2006) — the X3 chart's pre-2006 bars are RO-only and the
denominator approximation is acceptable per `docs/portal/methodology.md`.
"""
```

### Sidecar + raw-file convention

The XLSX should land in `data/raw/ons/familiesandhouseholdsuk2025.xlsx` with a `.meta.json` sidecar matching the existing `data/raw/ons/gas-sap.xlsx.meta.json` shape (atomic write via `data/sidecar.py::write_sidecar()`). The sha256 is computed by `write_sidecar()` automatically.

### Constants drift fixture (`tests/fixtures/constants.yaml`)

Per the SEED-001 Tier 2 pattern (`tests/test_constants_provenance.py:_TRACKED`), the planner should:
1. Add each `UK_HOUSEHOLDS_YYYY` synthetic key to `_TRACKED` set in `test_constants_provenance.py`
2. Add corresponding entries in `tests/fixtures/constants.yaml` (mirror `DEFAULT_CARBON_PRICES_YYYY` entries)
3. Extend `_live_constants()` in `test_constants_provenance.py` to expand `UK_HOUSEHOLDS` dict the way it expands `DEFAULT_CARBON_PRICES`

[ASSUMED] The X3 chart needs UK households for the union of years in `cross_scheme.parquet` (currently 2006-2017 + 2019-2024 — 19 years). ONS publishes 2014-onwards in the current edition; pre-2014 figures need to come from the ONS Census-derived historical series or be approximated to the 2014 value with a methodology-page footnote. **Planner must confirm the year coverage available from ONS during Wave 1 transcription.**

---

## latest_fully_reconciled_year rule (D-06)

### Exact intersection logic

```python
# Source: smoke-tested 2026-04-25 against current parquets
def latest_fully_reconciled_year() -> int:
    """Most recent year present in EVERY shipped scheme's annual_summary.parquet
    where the scheme's primary cost column is non-null AND the scheme is past
    its publication-cutoff date for that year."""
    import pyarrow.parquet as pq
    from uk_subsidy_tracker import PROJECT_ROOT

    cfd = pq.read_table(
        PROJECT_ROOT / "data/derived/cfd/annual_summary.parquet"
    ).to_pandas()
    ro = pq.read_table(
        PROJECT_ROOT / "data/derived/ro/annual_summary.parquet"
    ).to_pandas()

    # CfD: a year is "complete" when its cost is non-null AND it is at least
    # one full calendar year after year-end. CfD 2026 is partial today (in-progress).
    # Heuristic: drop the latest CfD year if it has < 12 months coverage. For
    # Phase 6 we use a simpler stable rule: cfd_complete = years <= year_now - 1
    # (RO has its own SY end-of-March cutoff). Document in methodology.
    import pandas as pd
    cfd_complete = set(int(y) for y in cfd["year"].unique() if int(y) <= 2025)

    # RO: a year is "complete" when GB row has non-null ro_cost_gbp.
    ro_gb = ro[ro["country"] == "GB"]
    ro_complete = set(int(y) for y in ro_gb.dropna(subset=["ro_cost_gbp"])["year"].unique())

    intersection = cfd_complete & ro_complete
    if not intersection:
        raise RuntimeError("No fully-reconciled year — neither CfD nor RO has complete data.")
    return max(intersection)
```

### Today's value (verified 2026-04-25)

- CfD complete years (assuming 2026 is partial; 2016-2025 are complete): `{2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025}`
- RO complete years (GB rows with non-null `ro_cost_gbp`): `{2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023}` (note: 2018 is the SY17 deferred gap; 2024 has cost=NaN)
- Intersection: `{2016, 2017, 2019, 2020, 2021, 2022, 2023}`
- **`latest_fully_reconciled_year = 2023`**

### Reconciliation note for `docs/portal/methodology.md`

> The `year` column convention diverges between schemes: CfD `year` is the calendar year of the settlement-month anchor; RO `year` is the **obligation-year start calendar year** (e.g. SY18 — Apr 2019 to Mar 2020 — is stored as `year=2019`, matching the REF Constable Table 1 convention). The intersection rule treats these as comparable: the headline-card "latest fully-reconciled scheme year = 2023" therefore corresponds to:
> - CfD CY 2023 (Jan 2023 – Dec 2023 settlements)
> - RO SY23 (Apr 2023 – Mar 2024 obligation year)
>
> The 9-month overlap is documented as the partial-coverage caveat. A more precise reconciliation (mid-year alignment) is deferred per CONTEXT.md "Calendar-year vs scheme-year normalisation."

### Edge case: CfD's "partial year" detection

The CfD parquet has 2026 row with non-NaN cost (~£0.86bn YTD). The recommended heuristic is `year <= current_year - 1` because the LCCC settlement publication lags the calendar year by ~3-6 months. The planner should hard-code `2025` as the CfD cutoff for Phase 6 plans, OR introspect the `meta.json` `retrieved_at` to detect partial years dynamically. **Recommendation:** hard-code for Phase 6 (simpler; matches D-21 determinism); revisit if Phase 7 introduces a scheme with a different lag profile.

---

## Plotting pattern in `plotting/subsidy/` — canonical 5-step recipe

Inherited verbatim by `plotting/portal/`. Pattern observed in 11 chart modules:

```python
# Source: plotting/subsidy/cfd_dynamics.py + plotting/subsidy/ro_dynamics.py
"""[Module docstring — 1-paragraph chart purpose]."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pyarrow.parquet as pq

from uk_subsidy_tracker.plotting import ChartBuilder
from uk_subsidy_tracker.schemes import portal  # cross_scheme parquet source


def _prepare() -> pd.DataFrame:
    """Step 1 — Read derived parquet, restrict to chart scope, derive helper columns.

    Robust to empty/missing parquet (returns empty DataFrame, _placeholder() handles)."""
    src = portal.DERIVED_DIR / "cross_scheme.parquet"
    if not src.exists():
        return pd.DataFrame()
    df = pq.read_table(src).to_pandas()
    # Coerce year → datetime for rangeselector compatibility (X1 only)
    df["year_dt"] = pd.to_datetime(df["year"], format="%Y")
    return df


def _placeholder(builder: ChartBuilder) -> go.Figure:
    """Empty-data placeholder so __main__ orchestration succeeds in CI."""
    fig = builder.create_basic()
    fig.add_annotation(
        x=0.5, y=0.5, xref="paper", yref="paper",
        text="<b>No cross-scheme data yet</b><br><br>"
             "data/derived/portal/cross_scheme.parquet is empty.<br>"
             "Run schemes.portal.rebuild_derived() first.",
        showarrow=False, font={"size": 14, "color": "#9ca3af"},
    )
    return fig


def main() -> None:
    """Step 2 — Build figure; Step 3 — Layout + axes; Step 4 — Save 3 formats."""
    df = _prepare()

    builder = ChartBuilder(
        title="Total UK subsidy stacked by scheme",
        height=600,
    )

    if df.empty:
        fig = _placeholder(builder)
        builder.save(fig, "x1_stacked_total", export_twitter=True)
        return

    fig = builder.create_basic()
    # Step 2: traces (one per scheme, stacked)
    for scheme_name, sub in df.groupby("scheme", sort=False):
        fig.add_trace(go.Bar(
            x=sub["year_dt"],
            y=sub["cost_gbp"] / 1e9,
            name=scheme_name,
            marker_color=SCHEME_COLORS[scheme_name],
            hovertemplate="%{x|%Y}<br>" + scheme_name +
                          "<br>£%{y:.2f} bn<extra></extra>",
        ))

    # Step 3: layout + rangeselector + subtitle
    fig.update_layout(
        barmode="stack",
        title=dict(
            text="<b>Total UK subsidy stacked by scheme</b>",
            subtitle=dict(
                text="Covers 2 of 8 schemes — see scheme grid for coverage status.",
                font=dict(size=12, color="#a0a4b8"),
            ),
            x=0.05, xanchor="left",
        ),
    )
    fig.update_xaxes(
        rangeselector=dict(
            buttons=[
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(step="all", label="All"),
            ],
            xanchor="left", yanchor="bottom", x=0.0, y=1.02,
        ),
        type="date", title="Year",
    )
    builder.format_currency_axis(fig, axis="y", suffix=" bn", title="Subsidy cost (£bn)")

    # Step 4: save (PNG + HTML + div HTML)
    builder.save(fig, "x1_stacked_total",
                 export_twitter=True, export_html=True, export_div=True)


if __name__ == "__main__":
    main()
```

### Step 5 — Wire `main()` into `plotting/__main__.py`

```python
# Source: src/uk_subsidy_tracker/plotting/__main__.py:14-46 + :66-90
from uk_subsidy_tracker.plotting.portal.x1_stacked_total import main as x1_stacked_total
from uk_subsidy_tracker.plotting.portal.x2_cumulative_premium import main as x2_cumulative_premium
from uk_subsidy_tracker.plotting.portal.x3_per_household import main as x3_per_household
from uk_subsidy_tracker.plotting.portal.x4_cost_per_mwh import main as x4_cost_per_mwh
from uk_subsidy_tracker.plotting.portal.x5_2022_crisis import main as x5_2022_crisis

# Append to charts list (in main())
charts = [
    # ... existing 18 charts
    # Cross-scheme portal flagship charts (Phase 6)
    ("x1_stacked_total", x1_stacked_total),
    ("x2_cumulative_premium", x2_cumulative_premium),
    ("x3_per_household", x3_per_household),
    ("x4_cost_per_mwh", x4_cost_per_mwh),
    ("x5_2022_crisis", x5_2022_crisis),
]
```

### Output filenames

The save() call writes 3 files per chart:
- `docs/charts/html/x1_stacked_total.html` (interactive full HTML)
- `docs/charts/html/x1_stacked_total.div.html` (div-only for embedding)
- `docs/charts/html/x1_stacked_total_twitter.png` (1200×675 @ scale=2)

Per UI-SPEC §"X1 hero embed", the embed pattern in `docs/index.md` and `docs/portal/x1-stacked-total.md` is:

```markdown
![Total UK subsidy stacked by scheme — covered schemes only](charts/html/x1_stacked_total_twitter.png)

[Interactive version](charts/html/x1_stacked_total.html){target="_blank"}
```

[VERIFIED: chart_builder.py:310-393 — save() signature accepts `export_twitter`, `export_html`, `export_div` kwargs; output dir defaults to `OUTPUT_DIR = PROJECT_ROOT / "docs" / "charts" / "html"`.]

---

## `docs/portal/` 6-section narrative template (Phase 3 D-01)

Verified via the canonical exemplar `docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md`. Each X-chart page follows this structure (different from scheme-page 8-section template):

| § | Heading (H2) | Content shape | Source exemplar lines |
|---|--------------|---------------|----------------------|
| 1 | `# {Chart title}` (H1) + headline blurb (1 bold-prose paragraph) + Twitter PNG embed + `[Interactive version]` link | "Adversarial lead — 1 sentence headline, then 2-3 sentences expanding" | lines 1-7 |
| 2 | `## What the chart shows` | Pure description: axes, panels, color-coded categories, annotations, what the eye sees first | lines 9-31 |
| 3 | `## The argument` | The reading: what the chart proves; 3-5 numbered points; cross-references to scheme pages | lines 33-69 |
| 4 | `## Methodology` | Formula sketch (code block) + key column references + scope (CY vs SY, GB vs UK-wide); for X4 + X5: footnote linking to portal/methodology.md | lines 71-111 |
| 5 | `## Caveats` | 3-6 bulleted caveats — coverage gap; SY mismatch; partial-coverage tolerance; per-household division (X3 only); excluded schemes (X4 + X5 only) | lines 113-138 |
| 6 | `## Data & code` | GOV-01 four-way coverage block: (a) Primary source (link to cross_scheme.parquet via manifest.json); (b) Chart source code (GitHub permalink); (c) Test (GitHub permalinks to test_aggregates + test_benchmarks); (d) Reproduce (bash block) | lines 140-159 |
| 7 (opt) | `## See also` | Cross-link to portal/methodology.md + relevant scheme pages | lines 161-172 |

**Heading depth rule:** H1 = page title (single, top); H2 = section name; H3 only inside §3 or §4 if a sub-argument warrants it (e.g. X5 may use `### 2021 vs 2022 vs 2023`). Avoid H4+.

### `docs/portal/methodology.md` (1 page, locked structure per UI-SPEC §5)

| § | Heading | Content |
|---|---------|---------|
| 1 | `# Cross-scheme methodology` | 1 paragraph framing |
| 2 | `## Cross-scheme aggregation` | Long-format `cross_scheme.parquet` schema; sum-by-year join semantics; `methodology_version` per-row inheritance |
| 3 | `## Scheme-year vs calendar-year reconciliation` | The Apr-Mar (RO) vs CY (CfD) mismatch; `latest_fully_reconciled_year` definition rule |
| 4 | `## No-gas-counterfactual schemes` | Why CM, Balancing, Grid Socialisation are excluded from X4 + X5; cross-reference to ARCH §5.3 modified-S2 treatment for CM |
| 5 | `## Per-household division convention` | ONS households-count source (URL + sha256 + retrieved_on); per-year vs single-value choice |
| 6 | `## Partial-coverage caveat` | The "covers 2 of 8 schemes" framing; how the headline-sync regression test re-arms |
| 7 | `## Reference checks` | Clinical reference to REF Constable + Turver as test-file tolerance anchors only |
| 8 | `## Reproducibility` | `git clone + uv sync + uv run python -c "from uk_subsidy_tracker.schemes import portal; portal.refresh(); portal.rebuild_derived(); portal.regenerate_charts()"` |

**Length target:** 600-1200 words; matches `docs/methodology/gas-counterfactual.md` depth.

---

## Headline-sync regression test pattern (D-09 / D-11)

### Pattern source — `tests/test_docs_ro_headline_sync.py`

The Phase 05.2 precedent (40 lines):

```python
# Source: tests/test_docs_ro_headline_sync.py
import re
from pathlib import Path
import pyarrow.parquet as pq
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
RO_MD = PROJECT_ROOT / "docs" / "schemes" / "ro.md"
ANNUAL_SUMMARY_PARQUET = PROJECT_ROOT / "data" / "derived" / "ro" / "annual_summary.parquet"

_HEADLINE_RE = re.compile(r"£\s*(\d+(?:\.\d+)?)\s*bn", re.IGNORECASE)


def _parquet_gb_total_gbp_bn() -> float:
    df = pq.read_table(ANNUAL_SUMMARY_PARQUET).to_pandas()
    gb = df[df["country"] == "GB"]
    return round(float(gb["ro_cost_gbp"].sum()) / 1e9, 1)


def _prose_headline_gbp_bn() -> float | None:
    text = RO_MD.read_text(encoding="utf-8")
    first_chunk = "\n".join(text.splitlines()[:40])
    m = _HEADLINE_RE.search(first_chunk)
    return round(float(m.group(1)), 1) if m else None


def test_ro_headline_prose_matches_parquet_total_to_one_decimal() -> None:
    if not ANNUAL_SUMMARY_PARQUET.exists():
        pytest.skip("annual_summary.parquet absent — Wave-3 rebuild_derived() has not run yet")
    parquet_bn = _parquet_gb_total_gbp_bn()
    prose_bn = _prose_headline_gbp_bn()
    assert prose_bn == parquet_bn, (
        f"Headline mismatch: prose £{prose_bn}bn vs parquet £{parquet_bn}bn. "
        f"Either update the prose OR record a CHANGES.md ## Methodology versions entry."
    )
```

### Generalised D-11 shape — `tests/test_headline_sync.py`

The single test file covers all surfaces, parametrised over (markdown_path, regex_target, parquet_query). Suggested shape:

```python
"""Cross-surface headline-sync regression (D-09 + D-11).

Each parametrised case asserts a prose £NN.N bn (or £NNN per household)
figure in a docs/*.md file matches a parquet-derived value to 1 decimal place
(or to nearest £). Failure = update prose, run mkdocs --strict, commit.

Generalises tests/test_docs_ro_headline_sync.py per Phase 6 D-11.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
import pyarrow.parquet as pq
import pytest

PROJECT_ROOT = Path(__file__).parent.parent


@dataclass(frozen=True)
class HeadlineCase:
    surface: str            # "homepage_total", "cfd_paid", "ro_covered", ...
    md_path: Path
    md_line_window: tuple[int, int]   # (start, end) line range to scan
    regex: re.Pattern
    expected_value: float   # parquet-derived
    tolerance: float = 0.05  # ±£0.05bn rounding to 1dp


def _parquet_value(case_key: str) -> float:
    """Compute the parquet-side expected value for the given case."""
    if case_key == "homepage_total_latest_year":
        df = pq.read_table(
            PROJECT_ROOT / "data/derived/portal/cross_scheme.parquet"
        ).to_pandas()
        latest = max(set(df["year"]) & ...)  # see latest_fully_reconciled_year
        return round(float(df[df["year"] == latest]["cost_gbp"].sum()) / 1e9, 1)
    if case_key == "cfd_paid_total":
        df = pq.read_table(
            PROJECT_ROOT / "data/derived/cfd/annual_summary.parquet"
        ).to_pandas()
        return round(float(df["cfd_payments_gbp"].sum()) / 1e9, 1)
    if case_key == "ro_covered_total":
        df = pq.read_table(
            PROJECT_ROOT / "data/derived/ro/annual_summary.parquet"
        ).to_pandas()
        return round(float(df[df["country"] == "GB"]["ro_cost_gbp"].sum()) / 1e9, 1)
    raise KeyError(case_key)


# Cases parametrised per surface
_CASES = [
    HeadlineCase(
        surface="cfd_paid",
        md_path=PROJECT_ROOT / "docs" / "schemes" / "cfd.md",
        md_line_window=(1, 40),
        regex=re.compile(r"£\s*(\d+(?:\.\d+)?)\s*bn", re.IGNORECASE),
        expected_value=29.0,  # populated from _parquet_value("cfd_paid_total")
    ),
    HeadlineCase(
        surface="ro_covered",
        md_path=PROJECT_ROOT / "docs" / "schemes" / "ro.md",
        md_line_window=(1, 40),
        regex=re.compile(r"£\s*(\d+(?:\.\d+)?)\s*bn", re.IGNORECASE),
        expected_value=58.6,
    ),
    HeadlineCase(
        surface="homepage_total_card",
        md_path=PROJECT_ROOT / "docs" / "index.md",
        md_line_window=(1, 30),  # the 3-card row sits above the scheme grid
        regex=re.compile(
            r"Total subsidy.*?£\s*(\d+(?:\.\d+)?)\s*bn", re.IGNORECASE | re.DOTALL
        ),
        expected_value=...,  # late-bound from cross_scheme.parquet
    ),
    # Additional cases: homepage premium card, homepage per-household card,
    # CfD £14bn premium, RO £65-70bn range.
]


@pytest.mark.parametrize("case", _CASES, ids=lambda c: c.surface)
def test_headline_matches_parquet(case: HeadlineCase) -> None:
    if not case.md_path.exists():
        pytest.fail(f"Markdown surface missing: {case.md_path}")
    text = "\n".join(case.md_path.read_text().splitlines()[case.md_line_window[0]-1:case.md_line_window[1]])
    m = case.regex.search(text)
    assert m, f"No headline found in {case.surface} (regex: {case.regex.pattern})"
    prose_value = round(float(m.group(1)), 1)
    expected = round(case.expected_value, 1)
    assert abs(prose_value - expected) <= case.tolerance, (
        f"Headline drift ({case.surface}): prose £{prose_value}bn, "
        f"parquet £{expected}bn. Either (a) update {case.md_path.name}, "
        f"(b) record a CHANGES.md ## Methodology versions entry."
    )
```

### Per-household card regex (Card C, UI-SPEC §"Copywriting Contract")

The per-household card uses `£N,NNN` format (no decimal, comma thousands separator):

```python
_PER_HOUSEHOLD_RE = re.compile(r"£\s*([\d,]+)\b")  # captures "£3,200" → "3,200"
# Parse: int(match.group(1).replace(",", ""))
```

### What surfaces to cover in D-11

Per CONTEXT D-11, the single test file MUST cover:
1. **Homepage total card** — `cross_scheme.parquet` total cost for `latest_fully_reconciled_year`
2. **Homepage premium card** — `cross_scheme.parquet` total premium for `latest_fully_reconciled_year`
3. **Homepage per-household card** — `cross_scheme.parquet` total cost / `households_uk[latest_year]`
4. **`cfd.md` £29bn paid** — `cfd/annual_summary.parquet[cfd_payments_gbp].sum() / 1e9`
5. **`cfd.md` £14bn premium** — `cfd/annual_summary.parquet[premium_over_gas_gbp].sum() / 1e9`
6. **`ro.md` £58.6bn covered** — `ro/annual_summary.parquet[country='GB'][ro_cost_gbp].sum() / 1e9`
7. **`ro.md` £65-70bn range** — RANGE check: `58.6 ≤ 65 ≤ 70` (looser; the range is published-as-range and allows ±2 bn of REF Constable cross-check; the planner can encode this as `assert lower <= ref_anchor <= upper` rather than a tight equality)

Future-scheme docs add a parametrised entry, not a new test file.

### Migration of existing `tests/test_docs_ro_headline_sync.py`

Either delete it (covered by the new `test_headline_sync.py::ro_covered` case) OR keep both running side-by-side during Wave 6 and delete the older file in Wave 7. **Recommendation:** delete in Wave 7 to avoid two tests fighting over the same prose; the generalised test is strictly more powerful.

---

## REF benchmark cross-check (Claude's Discretion option b)

### Existing `_TOLERANCE_BY_SOURCE` dispatch pattern

```python
# Source: tests/test_benchmarks.py:102-109
_TOLERANCE_BY_SOURCE: dict[str, float] = {
    "ofgem_transparency": OFGEM_TOLERANCE_PCT,        # 5.0
    "obr_efo": OBR_EFO_TOLERANCE_PCT,                 # 5.0
    "desnz_energy_trends": DESNZ_TOLERANCE_PCT,       # 5.0
    "hoc_library": HOC_LIBRARY_TOLERANCE_PCT,         # 3.0
    "nao_audit": NAO_TOLERANCE_PCT,                   # 3.0
    "ref_constable": REF_TOLERANCE_PCT,               # 3.0 (HARD BLOCK)
}
```

### REF Constable Table 1 entries (verified via `tests/fixtures/benchmarks.yaml`)

22 entries cover years 2002-2023, ALL keyed `ref_constable` and currently consumed by `test_ref_constable_ro_reconciliation`. Each entry has fields: `year`, `value_gbp_bn`, `url`, `retrieved_on`, `notes`, `tolerance_pct: 3.0`.

These are RO-only entries today. The Phase 6 `test_ref_total_reconciliation` needs **CfD entries from REF Table 1 ALSO**, which the planner will need to verify and transcribe. REF Constable's Table 1 covers all 8 schemes in the original PDF; only RO has been transcribed into `benchmarks.yaml::ref_constable` so far.

### Suggested `test_ref_total_reconciliation` shape (Discretion option b)

```python
# Source: extends tests/test_benchmarks.py pattern (HARD BLOCK at REF_TOLERANCE_PCT)
@pytest.fixture(scope="module")
def cross_scheme_totals_per_scheme() -> dict[str, dict[int, float]]:
    """{scheme: {year: cost_gbp_bn}} from data/derived/portal/cross_scheme.parquet."""
    import pyarrow.parquet as pq
    from uk_subsidy_tracker.schemes import portal

    path = portal.DERIVED_DIR / "cross_scheme.parquet"
    if not path.exists():
        return {}
    df = pq.read_table(path).to_pandas()
    out: dict[str, dict[int, float]] = {}
    for scheme in df["scheme"].unique():
        sub = df[df["scheme"] == scheme]
        out[scheme] = {int(r.year): float(r.cost_gbp) / 1e9 for r in sub.itertuples()}
    return out


def test_ref_total_reconciliation(
    benchmarks, cross_scheme_totals_per_scheme,
) -> None:
    """Phase 6 D-03 / Discretion option (b): per-scheme cross-check against REF subset.

    Sums REF entries for the schemes shipped in this phase (CfD + RO; later
    phases auto-extend) and asserts cross_scheme.parquet totals match within
    REF_TOLERANCE_PCT. As Phase 7-12 schemes ship, new ref_constable_<scheme>
    blocks land in benchmarks.yaml and this test auto-includes them.
    """
    if not cross_scheme_totals_per_scheme:
        pytest.fail(
            "cross_scheme.parquet absent — run schemes.portal.rebuild_derived()"
        )

    # NOTE: today's benchmarks.yaml has only `ref_constable` (RO-only). When
    # the planner transcribes REF CfD entries, this test extends naturally.
    # For Phase 6, the test asserts per-scheme RO subset only; CfD subset
    # arms in Wave 7 if/when REF CfD entries land.

    ref_ro_total = sum(
        e.value_gbp_bn for e in benchmarks.ref_constable
        if 2006 <= e.year <= 2023  # match RO complete-years window
    )
    pipeline_ro_total = sum(
        v for y, v in cross_scheme_totals_per_scheme.get("RO", {}).items()
        if 2006 <= y <= 2023
    )
    drift_pct = abs(pipeline_ro_total - ref_ro_total) / ref_ro_total * 100.0
    assert drift_pct <= REF_TOLERANCE_PCT, (
        f"RO total reconciliation FAILED:\n"
        f"  pipeline:    £{pipeline_ro_total:.2f} bn\n"
        f"  REF subset:  £{ref_ro_total:.2f} bn\n"
        f"  drift:       {drift_pct:.2f}% (> {REF_TOLERANCE_PCT}% tolerance)"
    )
```

### Why option (b) over (a) or (c)

- **Option (a)** — "expected_ratio = 2/8 ± N%": the 2/8 fraction assumes equal-sized schemes, which is FALSE (CfD ≈ £29bn, RO ≈ £58.6bn; CM and Constraints will be much larger; FiT and SEG smaller). Phase-6 picking a coverage-fraction would create a false benchmark that re-arms wrong as new schemes ship.
- **Option (c)** — `@pytest.mark.skip(reason=...)`: silent skip surfaces nothing useful; loses signal value.
- **Option (b) (RECOMMENDED)** — per-scheme REF subset cross-check: hard-asserts the schemes we DO have, ignores schemes we don't. Auto-arms as Phases 7-12 ship and REF CfD/FiT/etc. entries are transcribed. Inherits the existing `REF_TOLERANCE_PCT = 3.0` HARD BLOCK; matches the methodological cleanliness of `test_ref_constable_ro_reconciliation`.

### Note on the £25.8bn aggregate

CONTEXT references "REF Constable's £25.8bn aggregate" but the existing benchmarks.yaml `ref_constable` block transcribes RO-only entries summing to ~£58bn over 2006-2023. The £25.8bn figure is REF's full-year-2024 cross-scheme total (CfD + RO + FiT + Constraints + ...). The Phase 6 test should NOT compare against £25.8bn directly (we cover only 2 of 8 schemes); it should compare against the SUBSET of REF Table 1 entries matching our shipped schemes.

---

## mkdocs.yml nav placement options

### Current nav structure (verified via `mkdocs.yml:55-89`)

```yaml
nav:
  - Home: index.md
  - Cost: ...
  - Recipients: ...
  - Efficiency: ...
  - Cannibalisation: ...
  - Reliability: ...
  - Schemes:
      - Overview: schemes/index.md
      - Contracts for Difference (CfD): schemes/cfd.md
      - Renewables Obligation (RO): schemes/ro.md
  - Data: data/index.md
  - Methodology:
      - Gas counterfactual: methodology/gas-counterfactual.md
  - About: ...
```

### Three placement options (Discretion-punted to planner)

#### Option A — top-level `Portal` tab between Schemes and Data (UI-SPEC §6 LOCKED)

```yaml
  - Schemes: ...
  - Portal:
      - Overview: portal/index.md
      - X1 Total subsidy stacked by scheme: portal/x1-stacked-total.md
      - X2 Cumulative premium over gas: portal/x2-cumulative-premium.md
      - X3 Cost per household by scheme: portal/x3-per-household.md
      - X4 Cost per MWh by scheme: portal/x4-cost-per-mwh.md
      - X5 2022 crisis comparison: portal/x5-2022-crisis.md
      - Methodology: portal/methodology.md
  - Data: data/index.md
```

**Pros:** matches ARCH §5.4 "X-charts in their own bucket"; readers learn cross-scheme reading pattern once (cross-scheme symmetry principle from Phase 05.1 D-02); `navigation.tabs` already enabled (line 23) — adding a top-level tab is a one-block edit.
**Cons:** adds an 8th top-level tab (currently 7); mobile nav becomes denser.
**Recommended.** UI-SPEC §6 is explicit and locks this option.

#### Option B — sub-section under `Schemes`

```yaml
  - Schemes:
      - Overview: schemes/index.md
      - Cross-scheme analysis: portal/index.md
      - X1 ...
      ...
      - Contracts for Difference (CfD): schemes/cfd.md
      - Renewables Obligation (RO): schemes/ro.md
```

**Pros:** keeps top-level tab count at 7; conceptually "schemes" includes the cross-scheme tier.
**Cons:** buries flagship X-charts; defeats UI-SPEC's flagship framing; readers click twice to reach the X1 chart.

#### Option C — sub-section under existing `Themes` (one of Cost/Recipients/Efficiency/etc.)

**Pros:** none material.
**Cons:** X-charts span themes; placing them under "Cost" misframes them; rejected as conceptually wrong.

### Recommendation

Adopt UI-SPEC §6 lock: **top-level `Portal` tab**. The UI design contract has already adjudicated this (lines 244-264).

### `portal/index.md` Overview page

UI-SPEC §6 notes the Overview page is recommended-not-required. If the planner skips it, the first nav entry becomes `X1 Total subsidy stacked by scheme: portal/x1-stacked-total.md` — but Material `navigation.tabs` will then render an empty Portal tab when hovered. **Recommend: ship the Overview page** (~200 words mirroring `docs/schemes/index.md` shape).

---

## Material grid cards syntax

### Verified pattern (3 stat cards, no body, no link)

Per UI-SPEC §"Headline-card row" + verified against `docs/themes/cost/index.md:9-59`:

```markdown
<div class="grid cards" markdown>

-   **£N.N bn**

    Total subsidy (latest scheme year)

-   **£N.N bn**

    Premium over gas (latest scheme year)

-   **£N,NNN**

    Per household (latest scheme year)

</div>

*Covers 2 of 8 schemes; full coverage in Phases 7-12.*
```

### Required mkdocs extensions (verified `mkdocs.yml:91-123`)

- `attr_list` ✅ (line 94)
- `md_in_html` ✅ (line 97)

Both already enabled. No `mkdocs.yml` change required for grid cards.

### Card layout convention

- Line 1: `**£N.N bn**` — bold = headline-card-number type (28px / 700, per UI-SPEC §Typography).
- Line 2: small label (14px / 400) — Material renders the trailing paragraph at body-text size.
- **No `---` separator inside the card** (which would render as a horizontal rule per the `docs/themes/cost/index.md` precedent — that pattern is for navigational cards with both a title and body; UI-SPEC §"Headline-card row" specifies stat cards have no separator).

### Number formatting (UI-SPEC §"Number-formatting rules")

- `£N.N bn` for billions (with space, 1 decimal): `£87.5 bn`
- `£N,NNN` for per-household (no decimal, comma thousands separator): `£3,200`
- `£N/MWh` (no decimal where ≥10; 1 decimal where <10)

---

## mkdocs --strict known warnings

### Current state (verified 2026-04-25)

```bash
$ uv run mkdocs build --strict
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/rjl/Code/research-cfd-payments/site
INFO    -  Documentation built in 0.53 seconds
```

**Zero warnings, zero errors.** The Material-team upgrade banner ("MkDocs 2.0 will introduce backward-incompatible changes") prints on stderr but is informational, not a `--strict` failure.

### Risks for Phase 6

`mkdocs.yml:43-53` enables strict validation:

```yaml
validation:
  nav:
    omitted_files: warn       # → fails --strict
    not_found: warn           # → fails --strict
    absolute_links: warn
  links:
    not_found: warn           # → fails --strict
    anchors: warn             # → fails --strict
    absolute_links: warn
    unrecognized_links: info
```

Phase 6 must add 6 new `docs/portal/*.md` files AND register all 7 (incl. `index.md`) in `mkdocs.yml::nav`. If a file is created without a nav entry → `omitted_files` warning. If a nav entry references a non-existent file → `not_found` warning. Both fail `--strict`.

**Action for the planner:** every Wave 4 commit that adds a new `docs/portal/*.md` file MUST also update `mkdocs.yml::nav` in the same commit.

### Cross-link anchor warnings

The X-chart pages cross-link to:
- `methodology.md` (in same `docs/portal/` directory) — relative link `./methodology.md`, low risk
- `docs/schemes/cfd.md` + `docs/schemes/ro.md` — `../schemes/cfd.md` (no anchor; tile clickthrough convention per UI-SPEC §3)
- `docs/methodology/gas-counterfactual.md` — `../methodology/gas-counterfactual.md`
- `docs/index.md` (manifest.json link) — already in scope

All targets exist today; no anchor warnings expected. Run `mkdocs build --strict` after each Wave 4 + Wave 5 commit to catch drift.

### Hazard: chart PNG paths

Each `docs/portal/x{N}-*.md` page embeds `../charts/html/x{N}_*_twitter.png` and links `../charts/html/x{N}_*.html`. These files don't exist until `python -m uk_subsidy_tracker.plotting` regenerates charts. CI runs both steps in order (refresh.yml lines 56 + 58); LOCAL `mkdocs serve` against a fresh clone WILL produce broken-image warnings until charts are generated. The existing repo already has this pattern (CfD + RO charts) so it's an established, accepted limitation.

---

## Validation Architecture (Nyquist Dim 8)

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.x |
| Config file | `pyproject.toml [tool.pytest.ini_options]` (verify; default `testpaths = ["tests"]`) |
| Quick run command | `uv run pytest tests/test_aggregates.py tests/test_schemas.py tests/test_determinism.py tests/test_headline_sync.py -x` |
| Full suite command | `uv run pytest -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| X-01 | X1 stacked chart renders from cross_scheme.parquet | smoke | `uv run python -m uk_subsidy_tracker.plotting.portal.x1_stacked_total` | ❌ Wave 2 |
| X-02 | X2 cumulative premium chart renders | smoke | `uv run python -m uk_subsidy_tracker.plotting.portal.x2_cumulative_premium` | ❌ Wave 2 |
| X-03 | X3 per-household chart renders | smoke | `uv run python -m uk_subsidy_tracker.plotting.portal.x3_per_household` | ❌ Wave 2 |
| X-04 | X4 cost-per-MWh chart renders | smoke | `uv run python -m uk_subsidy_tracker.plotting.portal.x4_cost_per_mwh` | ❌ Wave 3 |
| X-05 | X5 2022-crisis chart renders | smoke | `uv run python -m uk_subsidy_tracker.plotting.portal.x5_2022_crisis` | ❌ Wave 3 |
| X-01..X-05 (data substrate) | cross_scheme.parquet schema conforms to CrossSchemeRow | unit | `uv run pytest tests/test_schemas.py -k portal -x` | ❌ Wave 1 (extend existing) |
| D-03 | sum(cross_scheme by scheme) == per-scheme annual_summary totals | unit | `uv run pytest tests/test_aggregates.py::test_cross_scheme_row_conservation -x` | ❌ Wave 1 (extend existing) |
| D-21 | cross_scheme.parquet byte-identical across rebuilds | unit | `uv run pytest tests/test_determinism.py -k cross_scheme -x` | ❌ Wave 1 (extend existing) |
| D-09 + D-11 | homepage + cfd.md + ro.md prose ↔ parquet totals | unit | `uv run pytest tests/test_headline_sync.py -x` | ❌ Wave 6 |
| D-03 (REF benchmark) | sum(cross_scheme[CfD]+[RO]) ≈ REF subset within ±3% | integration | `uv run pytest tests/test_benchmarks.py::test_ref_total_reconciliation -x` | ❌ Wave 7 |
| GOV-04 | uk_households constant matches yaml fixture | unit | `uv run pytest tests/test_constants_provenance.py -k UK_HOUSEHOLDS -x` | ❌ Wave 1 (extend `_TRACKED`) |
| PORTAL-01 | docs/portal/* + docs/index.md build with --strict zero warnings | integration | `uv run mkdocs build --strict` | ✅ existing |
| GOV-03 | refresh_all per-scheme dirty-check includes portal scheme | integration | `uv run pytest tests/test_refresh_loop.py -k portal -x` | ❌ Wave 1 (extend) |

### Sampling Rate

- **Per task commit:** `uv run pytest tests/test_aggregates.py tests/test_schemas.py tests/test_determinism.py tests/test_headline_sync.py -x` (~30s)
- **Per wave merge:** `uv run pytest -v` + `uv run mkdocs build --strict` + `uv run python -m uk_subsidy_tracker.plotting`
- **Phase gate:** Full suite green + `mkdocs --strict` clean + all 5 X-chart PNG + HTML + .div.html artefacts present in `docs/charts/html/` + `cross_scheme.parquet` byte-identical across two rebuilds

### Wave 0 Gaps

- [ ] `tests/test_headline_sync.py` — net-new file; 7+ parametrised cases (Wave 6)
- [ ] `tests/test_aggregates.py::test_cross_scheme_row_conservation` — append to existing file (Wave 1)
- [ ] `tests/test_schemas.py` — extend `_GRAIN_MODELS` to include `("cross_scheme", CrossSchemeRow)` (Wave 1)
- [ ] `tests/test_determinism.py` — append `PORTAL_GRAINS = ("cross_scheme",)` parametrisation (Wave 1)
- [ ] `tests/test_benchmarks.py::test_ref_total_reconciliation` — append; extends `_TOLERANCE_BY_SOURCE` dispatch (Wave 7)
- [ ] `tests/test_constants_provenance.py::_TRACKED` — extend with `UK_HOUSEHOLDS_*` synthetic keys (Wave 1)
- [ ] `tests/test_refresh_loop.py` — extend with portal scheme invariant (Wave 1)
- [ ] `src/uk_subsidy_tracker/data/uk_households.py` — net-new module + `Provenance:` docstring (Wave 1)
- [ ] `tests/fixtures/constants.yaml` — add per-year UK_HOUSEHOLDS entries mirroring `DEFAULT_CARBON_PRICES_YYYY` shape (Wave 1)
- [ ] `data/raw/ons/familiesandhouseholdsuk2025.xlsx` + `.meta.json` — net-new raw file + sidecar (Wave 1)

No framework install needed (pytest + pyarrow + plotly + kaleido already installed and verified).

---

## Provenance: docstring exemplars

### Live grep results (verified 2026-04-25)

```bash
$ grep -rn "^Provenance:" src/ | head
src/uk_subsidy_tracker/counterfactual.py:19:Provenance:
src/uk_subsidy_tracker/counterfactual.py:30:Provenance:
src/uk_subsidy_tracker/counterfactual.py:59:Provenance:
src/uk_subsidy_tracker/counterfactual.py:73:Provenance:
src/uk_subsidy_tracker/counterfactual.py:143:Provenance:
src/uk_subsidy_tracker/data/ro_bandings.py:13:Provenance: every entry MUST declare ``source`` (SI reference), ``url``, ``basis``,
src/uk_subsidy_tracker/data/ofgem_aggregate.py:9:Provenance: Ofgem 12-year XLSX is the authoritative pre-2019 source (GB aggregate
src/uk_subsidy_tracker/data/ofgem_ro.py:8:Provenance: Ofgem Renewables Energy Register (RER) https://rer.ofgem.gov.uk/
src/uk_subsidy_tracker/data/roc_prices.py:7:Provenance: Ofgem buy-out + mutualisation transparency PDFs
```

### Canonical exemplar (`src/uk_subsidy_tracker/counterfactual.py:CCGT_EFFICIENCY`)

```python
CCGT_EFFICIENCY = 0.55
"""Fleet-average thermal efficiency of UK CCGT, dimensionless.

55% reflects a blend of older F-class plants (~50%) and modern H-class
(~60%). Appropriate for an existing-fleet counterfactual; a new-build-only
study should use 0.60.

Provenance:
  source:       BEIS Electricity Generation Costs 2023, Table ES.1
  url:          https://www.gov.uk/government/publications/electricity-generation-costs-2023
  basis:        Net HHV efficiency, H-class CCGT mid-range
  retrieved_on: 2026-04-22
  next_audit:   when BEIS/DESNZ publishes next Electricity Generation Costs edition
"""
```

### Required fields for `UK_HOUSEHOLDS` constant

Per the canonical pattern, the docstring `Provenance:` block MUST declare:
1. `source:` — human-readable citation (publisher + dataset name + edition)
2. `url:` — primary URL (the dataset landing page on ons.gov.uk)
3. `basis:` — methodological basis (LFS quarterly survey; UK total)
4. `retrieved_on:` — ISO date of download
5. `next_audit:` — date of next ONS publication (annual cadence per the dataset's release calendar)

Plus, mirrored in `tests/fixtures/constants.yaml` per-year entries:
- `value: <integer>`
- `unit: "households (count)"`
- `notes:` — optional, e.g. "Pre-2014 figures from ONS historical archive"

The grep-discoverable test (`grep -rn "^Provenance:" src/`) finds the new block automatically once the file lands.

---

## Open Questions for the planner

### Resolvable from research; just need a planner decision

1. **`docs/portal/index.md` Overview page — ship or skip?**
   - Recommend: ship a thin (~200 word) Overview mirroring `docs/schemes/index.md` shape. Avoids empty-tab UX in Material `navigation.tabs`; gives readers a landing surface for the cross-scheme tier.
   - Resolution: planner-decided in Wave 4.

2. **CfD "partial year" detection — hard-code `<= 2025` or introspect sidecar `retrieved_at`?**
   - Recommend: hard-code `LATEST_COMPLETE_CFD_YEAR = 2025` in `cross_scheme_model.py` for Phase 6; revisit when Phase 7 introduces a scheme with different settlement lag.
   - Resolution: planner-decided in Wave 1.

3. **Pre-2014 UK households data — extrapolate to 2014 value, or skip pre-2014 X3 bars?**
   - Recommend: skip pre-2014 bars on X3 (RO 2006-2013 covered without a UK households denominator); document in `docs/portal/methodology.md` §5 as "pre-2014 bars omitted from X3 because per-household division relies on ONS Families and Households series which begins 2014. RO cumulative cost over 2006-2013 is preserved in cross_scheme.parquet for direct reading."
   - Alternative: use the ONS Census 2001 figure as the 2002-2010 anchor + ONS Census 2011 figure for 2011-2013. Adds 1 sidecar + 2 historical fixtures.
   - Resolution: planner-decided in Wave 1; methodology page documents the choice.

4. **`SCHEME_COLORS` constant — module location?**
   - UI-SPEC §"Per-scheme palette" specifies `src/uk_subsidy_tracker/plotting/colors.py`. Verified: `colors.py` already declares `TECHNOLOGY_COLORS`, `ALLOCATION_ROUND_COLORS`, etc. Append `SCHEME_COLORS: dict[str, str] = {"CfD": "#1f77b4", "RO": "#d62728", ...}` with a `Provenance:` docstring per UI-SPEC §"Selection criteria" point 5.
   - Resolution: planner places in Wave 1 (referenced by all 5 X-chart modules in Wave 2 + 3).

5. **Test ID `test_ref_total_reconciliation` already exists?**
   - Verified: `tests/test_benchmarks.py` has `test_ref_constable_ro_reconciliation` (singular RO). The new `test_ref_total_reconciliation` is a sibling, NOT a rename.
   - Resolution: name confirmed; no collision.

6. **`refresh.yml` step ordering — does the portal scheme rebuild need a new step?**
   - Verified: `.github/workflows/refresh.yml:51` runs `uv run --frozen python -m uk_subsidy_tracker.refresh_all`, which iterates `SCHEMES` and conditionally rebuilds. Adding `("portal", portal)` to the tuple is sufficient — no workflow file change needed.
   - Resolution: no change needed; planner verifies in Wave 1 phase-exit.

### Out of scope for research; punted to discuss-phase / implementation

7. **METHODOLOGY_VERSION 0.1.0 → 1.0.0 bump.**
   - CONTEXT Discretion: "Recommend bump iff the cross-scheme aggregation join introduces any methodology rule not already captured in per-scheme `counterfactual.METHODOLOGY_VERSION`. If pure substrate-and-presentation, hold at 0.1.0."
   - Phase 6 IS pure substrate-and-presentation (no new counterfactual rules; just a join + presentation layer); RECOMMEND HOLD AT 0.1.0. Bump is a planner-level decision once headline numbers stabilise.

8. **REF Constable CfD entries transcription.**
   - REF Constable Table 1 covers all 8 schemes; only RO is in `benchmarks.yaml::ref_constable` today. The Phase 6 `test_ref_total_reconciliation` will only assert the RO subset until CfD entries are transcribed.
   - Recommend: transcribe CfD entries from REF Table 1 in Wave 7 (same wave as the new test), so the test arms with both schemes from day 1.

9. **The £25.8bn aggregate referenced in CONTEXT.**
   - This is REF's full-UK-2024 cross-scheme total, NOT a sum of REF Table 1's per-scheme entries (which span 2002-2023). The Phase 6 test should NOT assert against £25.8bn directly. Document this in `docs/portal/methodology.md` §7 to avoid downstream confusion.

---

## Sources

### Primary (HIGH confidence)

- **Live codebase inspection 2026-04-25** — `src/uk_subsidy_tracker/schemes/{cfd,ro}/__init__.py`, `src/uk_subsidy_tracker/refresh_all.py`, `src/uk_subsidy_tracker/publish/manifest.py`, `src/uk_subsidy_tracker/plotting/{chart_builder,theme,colors,__main__}.py`, `src/uk_subsidy_tracker/schemas/{cfd,ro}.py`, `src/uk_subsidy_tracker/counterfactual.py`, `src/uk_subsidy_tracker/data/sidecar.py`, `src/uk_subsidy_tracker/schemes/ro/aggregate_model.py`, `tests/test_*.py`, `tests/fixtures/{benchmarks,constants}.yaml`, `mkdocs.yml`, `pyrightconfig.json`, `pyproject.toml`, `.github/workflows/refresh.yml`, `data/derived/{cfd,ro}/annual_summary.parquet`, `docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md`, `docs/index.md`, `docs/themes/cost/index.md`, `docs/schemes/{cfd,ro}.md`.
- **Live data inspection 2026-04-25** — pandas `read_parquet` on both annual_summary parquets; columns + dtypes + intersection-of-complete-years computed.
- **Plotly + kaleido smoke test 2026-04-25** — verified rangeselector survives PNG export with both `int x-axis + type='date'` AND `pd.to_datetime(year, format='%Y')` strategies; both produced 12,478-byte PNGs cleanly.
- **`uv run mkdocs build --strict` 2026-04-25** — clean (zero warnings, zero errors).
- **`tests/test_docs_ro_headline_sync.py`** — Phase 05.2 precedent for the headline-sync test pattern; generalised in this research.
- **CONTEXT.md (06-CONTEXT.md)** — locked decisions D-01..D-16 + Discretion items.
- **UI-SPEC.md (06-UI-SPEC.md)** — locked visual contract.

### Secondary (MEDIUM confidence)

- **[ONS Families and Households dataset page](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/datasets/familiesandhouseholdsfamiliesandhouseholds)** — verified canonical URL + 2025 edition file name + 17 April 2026 publication date via WebFetch.
- **[ONS Families and Households 2024 bulletin](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/bulletins/familiesandhouseholds/2024)** — 28.6M households 2024 figure verified via WebSearch.
- **[Plotly Range Slider docs](https://plotly.com/python/range-slider/)** — rangeselector button API verified via WebFetch.
- **[REF Constable PDF](https://ref.org.uk/attachments/article/390/renewables.subsidies.01.05.25.pdf)** — already transcribed into `tests/fixtures/benchmarks.yaml::ref_constable` (RO entries only); CfD entries pending Wave 7.

### Tertiary (LOW confidence — flagged for planner verification)

- **Pre-2014 UK households data availability** [ASSUMED] — ONS publishes Census-derived figures but the per-year Families and Households series begins 2014; planner verifies during Wave 1 transcription whether ONS publishes a continuous 2002-2024 households time series elsewhere.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Pre-2014 UK households data has limited per-year availability; ONS Families and Households series begins 2014 | ONS UK households source; Open Questions Q3 | Medium — if ONS has a longer series, X3 chart can show pre-2014 bars (more complete picture). If absent, footnote handles it. |
| A2 | The MkDocs Material team's "MkDocs 2.0" deprecation banner does NOT cause `--strict` to fail | mkdocs --strict known warnings | Low — verified the banner is informational and the build exits 0 |
| A3 | `LATEST_COMPLETE_CFD_YEAR = 2025` is a stable choice for Phase 6 (will become stale when 2026 closes) | latest_fully_reconciled_year rule; Open Questions Q2 | Low — Phase 6 ships in 2026; the constant is reviewed at next phase. Risk is a one-line edit if the cron runs into 2027. |
| A4 | The £25.8bn REF aggregate referenced in CONTEXT is a full-UK-2024 single-year figure, not a sum of REF Table 1's per-scheme 2002-2023 entries | REF benchmark cross-check; Open Questions Q9 | Medium — if it IS a Table 1 sum, the test should assert against it directly. Planner verifies REF Table 1 cumulative total during Wave 7 transcription. |
| A5 | `docs/portal/index.md` Overview page is recommended-not-required; nav can omit it if the planner decides X1 is the landing surface | mkdocs.yml nav placement options; Open Questions Q1 | Low — UX-only; either choice ships clean |
| A6 | Naming `uk_households` constant module as `src/uk_subsidy_tracker/data/uk_households.py` | ONS UK households source | Low — convention only; planner may prefer `src/uk_subsidy_tracker/data/ons_households.py` to mirror `ons_gas.py` |

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Plotly, kaleido, pandera, pydantic, pyarrow, mkdocs-material all verified at exact versions installed
- Architecture: HIGH — §6.1 contract, refresh_all iteration pattern, manifest.py per-scheme dispatch all read in source
- Pitfalls: HIGH — `RO country='GB'` filter, 2018 SY17 gap, 2024 NaN-cost, CfD 2026 partial-year, rangeselector type='date' requirement all explicitly noted
- Cross-scheme schema mapping: HIGH — every column verified against live parquet schemas
- ONS households source: MEDIUM — current edition URL verified; per-year time series depth pending planner transcription

**Research date:** 2026-04-25
**Valid until:** 2026-05-25 (the manifest URL convention, ONS publication cadence, and Plotly 6.x API are all stable; revisit if ONS publishes a new "Families and Households" edition or if Plotly releases 7.x within the phase window)

---

## RESEARCH COMPLETE
