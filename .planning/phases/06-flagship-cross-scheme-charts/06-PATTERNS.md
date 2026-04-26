# Phase 6: Flagship Cross-Scheme Charts — Pattern Map

**Mapped:** 2026-04-25
**Files analyzed:** 27 (created or modified) across 7 roles
**Analogs found:** 27 / 27 (every file has an in-tree exemplar named in RESEARCH.md and verified on disk)

---

## File Classification

| File (relative to repo root) | Status | Role | Data flow | Closest analog | Match |
|------------------------------|--------|------|-----------|----------------|-------|
| `src/uk_subsidy_tracker/schemes/portal/__init__.py` | NEW | scheme-module (§6.1 contract) | event-driven (downstream of CfD+RO rebuilds) | `src/uk_subsidy_tracker/schemes/ro/__init__.py` | exact (with no-op `refresh()`) |
| `src/uk_subsidy_tracker/schemes/portal/_refresh.py` | NEW | scheme-module dirty-check | mtime check (no upstream URL) | `src/uk_subsidy_tracker/schemes/ro/_refresh.py` | role-match (mtime not sha256) |
| `src/uk_subsidy_tracker/schemes/portal/cross_scheme_model.py` | NEW | derived-layer build (long-format join) | transform / batch | `src/uk_subsidy_tracker/schemes/ro/aggregate_model.py::build_annual_summary_aggregate` | exact (read-parquets-rename-concat-write) |
| `src/uk_subsidy_tracker/schemas/portal.py` | NEW | parquet-schema (Pydantic row model) | schema definition | `src/uk_subsidy_tracker/schemas/cfd.py::AnnualSummaryRow` + `schemas/ro.py::RoAnnualSummaryRow` | exact |
| `src/uk_subsidy_tracker/data/uk_households.py` | NEW | constants module + Provenance docstring | static-lookup dict | `src/uk_subsidy_tracker/counterfactual.py::DEFAULT_CARBON_PRICES` | exact |
| `src/uk_subsidy_tracker/plotting/portal/__init__.py` | NEW | plotting subpackage barrel | n/a (re-exports) | `src/uk_subsidy_tracker/plotting/subsidy/__init__.py` | exact |
| `src/uk_subsidy_tracker/plotting/portal/x1_stacked_total.py` | NEW | plotting module (stacked bar + rangeselector) | request-response (read parquet → render) | `src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py` | role-match (1-panel + rangeselector vs 4-panel) |
| `src/uk_subsidy_tracker/plotting/portal/x2_cumulative_premium.py` | NEW | plotting module (cumulative line) | request-response | `src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py` panel 4 | role-match |
| `src/uk_subsidy_tracker/plotting/portal/x3_per_household.py` | NEW | plotting module (per-household decomposition) | request-response | `src/uk_subsidy_tracker/plotting/subsidy/cfd_payments_by_category.py` | role-match (stacked decomposition) |
| `src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py` | NEW | plotting module (per-MWh by scheme) | request-response | `src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck.py` | role-match |
| `src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py` | NEW | plotting module (grouped bars) | request-response | `src/uk_subsidy_tracker/plotting/subsidy/ro_by_technology.py` | role-match (grouped bars by category) |
| `src/uk_subsidy_tracker/plotting/colors.py` | MODIFIED | palette constant (extend) | static lookup | existing same file (`TECHNOLOGY_COLORS`, `ALLOCATION_ROUND_COLORS`) | exact |
| `src/uk_subsidy_tracker/plotting/__main__.py` | MODIFIED | chart-orchestrator (append 5 entries) | event-driven (CI loop) | existing same file lines 14-46 + 66-90 | exact |
| `src/uk_subsidy_tracker/schemes/__init__.py` | MODIFIED | barrel re-export | n/a | existing line 54 (`from ... import cfd, ro`) | exact (one-line append) |
| `src/uk_subsidy_tracker/refresh_all.py` | MODIFIED | CI orchestration tuple | event-driven | existing lines 30-36 (`SCHEMES = ((cfd, …), (ro, …))`) | exact |
| `src/uk_subsidy_tracker/publish/manifest.py` | MODIFIED | publishing dispatch dict-of-dicts | static config | existing `GRAIN_SOURCES["cfd"]` + `["ro"]` (lines 74-139) | exact |
| `data/derived/portal/cross_scheme.parquet` | NEW (emitted) | derived parquet artefact | output-only | `data/derived/ro/annual_summary.parquet` | exact |
| `data/derived/portal/cross_scheme.schema.json` | NEW (emitted) | JSON-schema sidecar | output-only | `data/derived/ro/annual_summary.schema.json` | exact (via `emit_schema_json`) |
| `data/raw/ons/familiesandhouseholdsuk2025.xlsx` + `.meta.json` | NEW | raw fixture + sidecar | file-I/O | `data/raw/ons/gas-sap.xlsx` + `gas-sap.xlsx.meta.json` | exact |
| `tests/test_aggregates.py` | MODIFIED | row-conservation parametrisation | unit | existing `test_annual_vs_station_month_parquet` lines 95-103 + RO `test_ro_annual_vs_station_month_parquet` lines 191-209 | exact |
| `tests/test_schemas.py` | MODIFIED | schema-conformance parametrisation | unit | existing `_GRAIN_MODELS` (lines 105-111) + RO `_RO_GRAIN_MODELS` (lines 155-161) | exact |
| `tests/test_determinism.py` | MODIFIED | byte-identity parametrisation | unit | existing `GRAINS` (line 24-30) + RO `RO_GRAINS` (line 86-92) | exact |
| `tests/test_constants_provenance.py` | MODIFIED | drift-tracker `_TRACKED` extension | unit | existing `_TRACKED` set + `_live_constants()` `DEFAULT_CARBON_PRICES` expansion | exact |
| `tests/test_refresh_loop.py` | MODIFIED | mtime-invariant test for portal | integration | existing CfD `test_refresh_loop_converges_on_unchanged_upstream` + RO `test_ro_refresh_converges_on_unchanged_upstream` | role-match (mtime not sha256) |
| `tests/test_benchmarks.py` | MODIFIED | append `test_ref_total_reconciliation` | integration | existing `test_ref_constable_ro_reconciliation` (lines 290-335) | exact |
| `tests/test_headline_sync.py` | NEW | cross-surface prose↔parquet regression | unit (parametrised) | `tests/test_docs_ro_headline_sync.py` (whole file, 65 lines) | exact (generalised) |
| `tests/fixtures/constants.yaml` | MODIFIED | per-year `UK_HOUSEHOLDS_*` provenance | yaml fixture | existing `DEFAULT_CARBON_PRICES_2002`..`_2026` blocks (lines 51-end) | exact |
| `docs/portal/index.md` | NEW (recommended) | docs landing page | static markdown | `docs/schemes/index.md` | exact |
| `docs/portal/x{1..5}-*.md` (5 files) | NEW | docs narrative page (6-section template) | static markdown | `docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md` (172 lines) | exact |
| `docs/portal/methodology.md` | NEW | docs methodology page (8-section) | static markdown | `docs/methodology/gas-counterfactual.md` | exact |
| `docs/index.md` | MODIFIED | homepage retrofit (3 cards + caveat + X1 hero) | static markdown | existing `docs/themes/cost/index.md` `grid cards` block (lines 9-59) | exact (markup pattern) |
| `mkdocs.yml` | MODIFIED | nav append `Portal:` block | yaml config | existing `Schemes:` block (lines ~60-65) | exact |

---

## Pattern Assignments

### Scheme module (§6.1 contract) — `schemes/portal/`

#### `src/uk_subsidy_tracker/schemes/portal/__init__.py`

**Analog:** `src/uk_subsidy_tracker/schemes/ro/__init__.py` (262 lines)

**Module docstring shape** (RO lines 1-20):
```python
"""Portal scheme module — ARCHITECTURE §6.1 contract.

Five module-level callables satisfying the ``SchemeModule`` Protocol declared
in ``uk_subsidy_tracker.schemes.__init__``. Mirrors ``schemes/ro/`` verbatim
with portal-specific logic substitutions (no-op refresh; mtime-based dirty-check).

Public surface (ARCHITECTURE §6.1):
- ``DERIVED_DIR``: where this scheme's Parquet lives (``data/derived/portal/``).
- ``upstream_changed()``: mtime-compare against shipped scheme parquets.
- ``refresh()``: NO-OP — portal has no upstream URL.
- ``rebuild_derived(output_dir)``: read scheme annual_summary.parquet files,
  emit cross_scheme.parquet via cross_scheme_model.build_cross_scheme().
- ``regenerate_charts()``: delegate to ``uk_subsidy_tracker.plotting.__main__``.
- ``validate()``: row-conservation + presence + methodology_version checks.
"""
```

**Imports + DERIVED_DIR** (RO lines 21-37):
```python
from __future__ import annotations
from pathlib import Path
from uk_subsidy_tracker import PROJECT_ROOT
from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.schemes.portal._refresh import (
    refresh as _refresh,
    upstream_changed as _upstream_changed,
)

DERIVED_DIR: Path = PROJECT_ROOT / "data" / "derived" / "portal"

# Stable registration order — appended-to as Phases 7-12 ship new schemes.
SHIPPED_SCHEMES: tuple[str, ...] = ("CfD", "RO")
```

**5-function contract pattern** (copy verbatim from RO lines 39-99, substitute "RO" → "portal"):
```python
def upstream_changed() -> bool: return _upstream_changed()
def refresh() -> None: _refresh()                      # no-op for portal
def rebuild_derived(output_dir: Path | None = None) -> None: ...
def regenerate_charts() -> None:
    import runpy
    runpy.run_module("uk_subsidy_tracker.plotting", run_name="__main__")
def validate() -> list[str]: ...
```

**`__all__` discipline** (RO lines 253-261): list every public symbol, alphabetical-by-callable.

**Deviation from RO analog:**
- `refresh()` is a no-op (RO downloads XLSX); document explicitly.
- `upstream_changed()` is mtime-based (RO is sha256-based); see `_refresh.py` below.
- No `DORMANT_*` flag (RO has `DORMANT_STATION_LEVEL=True`).
- `validate()` checks 3 things (presence of every shipped scheme; `methodology_version` consistency; per-scheme cost reconciliation against source `annual_summary.parquet`); RO has 4 checks. Use the skeleton in 06-RESEARCH.md lines 355-399.

---

#### `src/uk_subsidy_tracker/schemes/portal/_refresh.py`

**Analog:** `src/uk_subsidy_tracker/schemes/ro/_refresh.py` (90 lines) — but **inverted control logic** (mtime not sha256, no-op fetch).

**Pattern from RO `_refresh.py` lines 1-49** — replace SHA-compare with mtime-compare:

```python
"""Portal dirty-check — mtime-based against shipped scheme parquets.

upstream_changed() returns True when any shipped scheme's annual_summary.parquet
mtime is newer than cross_scheme.parquet, OR cross_scheme.parquet is absent.
refresh() is a no-op — the portal has no upstream URL to fetch.
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

**Note for executor:** the importlib-shadow pattern in `tests/test_refresh_loop.py` lines 23-33 (where `_refresh` submodule is shadowed by `from ... import refresh as _refresh` alias in `__init__.py`) **applies here too** — the test fixture uses `importlib.import_module("uk_subsidy_tracker.schemes.portal._refresh")` to bypass it.

---

#### `src/uk_subsidy_tracker/schemes/portal/cross_scheme_model.py`

**Analog:** `src/uk_subsidy_tracker/schemes/ro/aggregate_model.py::build_annual_summary_aggregate` (lines 280-340)

**Module docstring shape** (RO aggregate_model lines 1-38):
```python
"""Cross-scheme aggregation — long-format join over shipped scheme annual_summary parquets.

Determinism (D-21): pure function of upstream parquet content. Final sort is
(year ASC, scheme ASC). No clock reads, no randomness. Uses the shared
deterministic Parquet writer from schemes/cfd/cost_model._write_parquet (D-22).

Sources consumed:
  - data/derived/cfd/annual_summary.parquet (cfd_payments_gbp + premium_over_gas_gbp + cfd_generation_mwh)
  - data/derived/ro/annual_summary.parquet (country='GB' filter; ro_cost_gbp + premium_gbp + ro_generation_mwh)
"""
```

**Imports + shared writer** (RO aggregate_model lines 39-65):
```python
from __future__ import annotations
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq

from uk_subsidy_tracker import PROJECT_ROOT
from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.data.uk_households import UK_HOUSEHOLDS
from uk_subsidy_tracker.schemas.portal import CrossSchemeRow, emit_schema_json
# Shared D-22 writer — import, do NOT re-implement (PATTERNS-04 contract carried forward)
from uk_subsidy_tracker.schemes.cfd.cost_model import _write_parquet
```

**Long-format join pattern** (mirrors RO `_unified_annual_frame` shape but simpler — no scheme-year arithmetic, no defect-fix logic). Use the skeleton in 06-RESEARCH.md lines 452-527 (`build_cross_scheme`).

**Per-scheme reader pattern** (RO aggregate_model lines 280-340 reduced):
```python
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
    # D-12: GB-only headline scope. Drop NI rows AND NaN-cost rows.
    df = df[(df["country"] == "GB") & df["ro_cost_gbp"].notna()]
    return pd.DataFrame({
        "year": df["year"],
        "scheme": "RO",
        "cost_gbp": df["ro_cost_gbp"],
        "premium_gbp": df["premium_gbp"],
        "generation_mwh": df["ro_generation_mwh"],
        "methodology_version": df["methodology_version"],
    })
```

**Final write pattern** (RO aggregate_model lines 327-340):
```python
columns = list(CrossSchemeRow.model_fields.keys())
long = (long[columns]
        .sort_values(["year", "scheme"], kind="mergesort")
        .reset_index(drop=True))
_write_parquet(long, output_dir / "cross_scheme.parquet")
emit_schema_json(CrossSchemeRow, output_dir / "cross_scheme.schema.json")
return long
```

**Critical hazards (RESEARCH §"Cross-scheme parquet schema" + Defect notes):**
1. RO `country == 'GB'` filter is mandatory (else NI rows double-count).
2. RO `ro_cost_gbp` NaN for SY1-SY4 + 2024 → drop NaN rows.
3. CfD 2026 partial → still emit (X1 All-time band) but `latest_fully_reconciled_year` excludes via hard-cap `<= 2025`.
4. RO year=2018 absent (SY17 deferred) — gap is documented; don't try to interpolate.
5. Don't carry `ro_cost_gbp_eroc` or `mutualisation_gbp` — they're RO-internal.

---

### Parquet schema — `schemas/portal.py`

**Analog:** `src/uk_subsidy_tracker/schemas/ro.py::RoAnnualSummaryRow` (lines 156-208) for shape + `schemas/cfd.py::AnnualSummaryRow` (lines 74-103) for the `emit_schema_json` re-export pattern.

**Re-export discipline (D-10 trust boundary)** — `schemas/ro.py:48`:
```python
# Import, do NOT re-declare — scheme-agnostic emitter shared via schemas.cfd
from uk_subsidy_tracker.schemas.cfd import emit_schema_json  # noqa: F401 (re-exported)
```
Apply identically to `schemas/portal.py`.

**Pydantic row model pattern** — copy from `RoAnnualSummaryRow` (RO lines 156-208), adapt fields per RESEARCH §"Suggested Pydantic row model" lines 168-208:

```python
from datetime import date
from pydantic import BaseModel, Field
from uk_subsidy_tracker.schemas.cfd import emit_schema_json  # noqa: F401


class CrossSchemeRow(BaseModel):
    """One row in portal/cross_scheme.parquet (per (year, scheme), D-02).

    Field declaration order IS the canonical Parquet column order (D-10).
    """

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

**Units convention** — copy from `schemas/ro.py:30-39` docstring (Monetary "GBP", Energy "MWh", year-like int "year", count "count").

**Deviation from analog:**
- `RoAnnualSummaryRow` carries `country` (D-09 GB/NI split); `CrossSchemeRow` does NOT — country filter happens in the join layer.
- `RoAnnualSummaryRow` has 7 columns; `CrossSchemeRow` has 7 columns of which 4 are renamed and `households_uk` is new.

**Schemas barrel** (`schemas/__init__.py`): inspect existing `__init__.py` (1.2 KB) and add a one-line re-export of `CrossSchemeRow` mirroring how `RoAnnualSummaryRow` is exposed.

---

### Constants module — `data/uk_households.py`

**Analog:** `src/uk_subsidy_tracker/counterfactual.py::CCGT_EFFICIENCY` (lines 12-25) for the Provenance docstring pattern; `counterfactual.py::DEFAULT_CARBON_PRICES` for the per-year dict pattern.

**Provenance docstring shape** (counterfactual.py:13-25 — verbatim required by `grep -rn "^Provenance:" src/`):
```python
UK_HOUSEHOLDS: dict[int, int] = {
    # Per-year transcription from ONS "Families and Households" 2025 edition.
    2014: 26_700_000,  # ONS published figure rounded to nearest 100k
    # ...
    2024: 28_600_000,  # ONS published, 17 April 2026 release
}
"""Per-year UK households count (households, not millions). Keys cover the
union of years present in cross_scheme.parquet; values are the ONS-published
figure for that year.

Provenance:
  source:       ONS Families and Households Dataset 2025 edition
  url:          https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/datasets/familiesandhouseholdsfamiliesandhouseholds
  basis:        Labour Force Survey April-June quarter; UK total of single-family
                + multi-family + lone-person households.
  retrieved_on: 2026-04-25
  next_audit:   2027-04-30  (ONS publishes annually in April)
  file:         familiesandhouseholdsuk2025.xlsx (204.2 KB)
  sha256:       <executor computes during Wave 1; raw file lives in data/raw/ons/>
"""
```

**Constants drift YAML pattern** (`tests/fixtures/constants.yaml` lines 21-49 — every UK_HOUSEHOLDS_YYYY synthetic key needs a block of this shape):
```yaml
UK_HOUSEHOLDS_2024:
  source: "ONS Families and Households Dataset 2025 edition"
  url: "https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/datasets/familiesandhouseholdsfamiliesandhouseholds"
  basis: "Labour Force Survey Apr-Jun 2024 reference quarter; UK total."
  retrieved_on: 2026-04-25
  next_audit: 2027-04-30
  value: 28600000
  unit: "households (count)"
  notes: "Released 17 April 2026."
```

**Deviation:** unlike `DEFAULT_CARBON_PRICES`, the dict carries `int` (count) rather than `float` (GBP/tCO2). The drift-tracker `_live_constants()` function (test_constants_provenance.py lines 78-99) currently only handles scalar int/float and the `DEFAULT_CARBON_PRICES` dict by name; it must be extended to also expand `UK_HOUSEHOLDS` (Wave 1 task).

**Sidecar pattern** (`data/raw/ons/gas-sap.xlsx.meta.json` shape via `data/sidecar.py::write_sidecar`): `data/raw/ons/familiesandhouseholdsuk2025.xlsx.meta.json` will be auto-emitted with the same 4-field shape (`retrieved_at`, `upstream_url`, `sha256`, `http_status`, `publisher_last_modified`).

---

### Plotting modules — `plotting/portal/`

#### `src/uk_subsidy_tracker/plotting/portal/__init__.py`

**Analog:** `src/uk_subsidy_tracker/plotting/subsidy/__init__.py` (627 bytes — short barrel-style re-export). Mirror its shape; planner verifies whether to re-export the 5 `main()` functions or leave them as module-level imports only.

#### `src/uk_subsidy_tracker/plotting/portal/x1_stacked_total.py`

**Analog:** `src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py` (273 lines) for the parquet-read + empty-data-placeholder pattern; cfd_dynamics.py for layout discipline.

**5-step recipe** (verbatim from RO `ro_dynamics.py` + RESEARCH §"Plotly rangeselector specifics" lines 218-256):

**Step 1 — Read + prepare** (ro_dynamics.py lines 29-78):
```python
def _prepare() -> pd.DataFrame:
    src = portal.DERIVED_DIR / "cross_scheme.parquet"
    if not src.exists():
        return pd.DataFrame()
    df = pq.read_table(src).to_pandas()
    if len(df) == 0:
        return df
    # Coerce year → datetime for rangeselector compatibility (X1 only)
    df["year_dt"] = pd.to_datetime(df["year"], format="%Y")
    return df
```

**Step 2 — Empty-data placeholder** (ro_dynamics.py lines 81-103, verbatim copy with text substitution):
```python
def _placeholder(builder: ChartBuilder) -> go.Figure:
    fig = builder.create_basic()
    fig.add_annotation(
        x=0.5, y=0.5, xref="paper", yref="paper",
        text="<b>No cross-scheme data yet</b><br><br>"
             "data/derived/portal/cross_scheme.parquet is empty.<br>"
             "Run schemes.portal.rebuild_derived() first.",
        showarrow=False, font={"size": 14, "color": "#9ca3af"},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig
```

**Step 3 — Build figure** (mix of cfd_dynamics + RESEARCH §"Plotting pattern" lines 720-817):
```python
fig = builder.create_basic()
for scheme_name, sub in df.groupby("scheme", sort=False):
    fig.add_trace(go.Bar(
        x=sub["year_dt"],
        y=sub["cost_gbp"] / 1e9,
        name=scheme_name,
        marker_color=SCHEME_COLORS[scheme_name],
        hovertemplate="%{x|%Y}<br>" + scheme_name +
                      "<br>£%{y:.2f} bn<extra></extra>",
    ))
fig.update_layout(barmode="stack")
```

**Step 4 — Plotly rangeselector + subtitle** (verbatim from UI-SPEC §2 + RESEARCH lines 241-256):
```python
fig.update_xaxes(
    rangeselector=dict(
        buttons=[
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(count=5, label="5y", step="year", stepmode="backward"),
            dict(step="all", label="All"),
        ],
        xanchor="left", yanchor="bottom", x=0.0, y=1.02,
    ),
    type="date",  # REQUIRED — rangeselector needs a date-typed axis
    title="Year",
)
fig.update_layout(
    title=dict(
        text="<b>Total UK subsidy stacked by scheme</b>",
        subtitle=dict(
            text="Covers 2 of 8 schemes — see scheme grid for coverage status.",
            font=dict(size=12, color="#a0a4b8"),
        ),
        x=0.05, xanchor="left",
    ),
)
builder.format_currency_axis(fig, axis="y", suffix=" bn", title="Subsidy cost (£bn)")
```

**Step 5 — Save (Twitter PNG + interactive HTML + div HTML)** (chart_builder.py:310-393):
```python
builder.save(fig, "x1_stacked_total",
             export_twitter=True, export_html=True, export_div=True)
```

**CRITICAL deviation from RO analog** — UI-SPEC §"X1 hero embed" requires the **Twitter PNG to NOT show rangeselector buttons**. RESEARCH §"Plotly rangeselector specifics" Option A (lines 261-263) — **build TWO figures**:

```python
def main() -> None:
    df = _prepare()
    builder = ChartBuilder(title="Total UK subsidy stacked by scheme", height=600)
    if df.empty:
        fig = _placeholder(builder)
        builder.save(fig, "x1_stacked_total", export_twitter=True)
        return
    # Build base figure (traces + layout + subtitle), no rangeselector yet
    fig_base = _build_stacked_figure(df, builder)  # extract trace logic here
    # PNG hero — no rangeselector
    fig_png = go.Figure(fig_base)  # deep-copy
    fig_png.update_xaxes(type="date", title="Year")
    builder.save(fig_png, "x1_stacked_total", export_twitter=True, export_html=False, export_div=False)
    # HTML interactive — add rangeselector
    fig_html = go.Figure(fig_base)
    fig_html.update_xaxes(rangeselector=dict(...), type="date", title="Year")
    builder.save(fig_html, "x1_stacked_total", export_twitter=False, export_html=True, export_div=True)
```
The `ChartBuilder.save()` API supports independent flags for `export_twitter`/`export_html`/`export_div` (chart_builder.py:315-317), so a single call cannot produce "PNG without buttons + HTML with buttons". Two `save()` calls is the only pattern.

#### `src/uk_subsidy_tracker/plotting/portal/x2_cumulative_premium.py`

**Analog:** `plotting/subsidy/ro_dynamics.py` panel 4 (lines 184-219) — cumulative premium £bn line with `cumsum() / 1e9` and `fill="tozeroy"`.

**Core pattern** (ro_dynamics.py:206-220):
```python
fig.add_trace(go.Scatter(
    x=df["year_dt"],
    y=df.groupby("year")["premium_gbp"].sum().cumsum() / 1e9,
    mode="lines+markers",
    line={"color": "#d62728", "width": 2.5},
    fill="tozeroy",
    fillcolor="rgba(214,39,40,0.25)",
    hovertemplate="%{x|%Y}<br>£%{y:.1f}bn<extra></extra>",
))
```

**Deviation:** X2 sums premium across both schemes per year (combined) before `cumsum()` — confirm with planner whether also stacked-by-scheme like X1 or single combined line.

#### `src/uk_subsidy_tracker/plotting/portal/x3_per_household.py`

**Analog:** `plotting/subsidy/cfd_payments_by_category.py` for the stacked-bar-with-legend pattern.

**Core pattern (per-household decomposition):**
```python
df["per_household_gbp"] = df["cost_gbp"] / df["households_uk"]
for scheme_name, sub in df.groupby("scheme", sort=False):
    fig.add_trace(go.Bar(
        x=sub["year"], y=sub["per_household_gbp"],
        name=scheme_name, marker_color=SCHEME_COLORS[scheme_name],
        hovertemplate="%{x}<br>" + scheme_name + "<br>£%{y:,.0f}/household<extra></extra>",
    ))
fig.update_layout(barmode="stack")
builder.format_currency_axis(fig, axis="y", title="Cost per household (£)")
```

**Deviation per UI-SPEC §"Open items for planner" Q3:** households_uk is per-row in `cross_scheme.parquet`; pre-2014 bars are skipped per `methodology.md` documentation.

#### `src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py`

**Analog:** `plotting/subsidy/bang_for_buck.py` for the per-MWh scatter pattern.

**Core pattern:**
```python
df["cost_per_mwh"] = df["cost_gbp"] / df["generation_mwh"]
df = df[df["generation_mwh"].notna() & (df["generation_mwh"] > 0)]  # NaN guard
for scheme_name, sub in df.groupby("scheme", sort=False):
    fig.add_trace(go.Scatter(
        x=sub["year"], y=sub["cost_per_mwh"],
        name=scheme_name, mode="lines+markers",
        line={"color": SCHEME_COLORS[scheme_name], "width": 2.5},
    ))
builder.format_currency_axis(fig, axis="y", title="Cost per MWh (£/MWh)")
```

**Footnote subtitle (UI-SPEC Copywriting §):** `"Schemes without a gas counterfactual (CM, Balancing, Grid) excluded — see methodology."`

#### `src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py`

**Analog:** `plotting/subsidy/ro_by_technology.py` for the grouped-bars-by-category pattern.

**Core pattern (3 grouped bars per scheme for 2021/2022/2023):**
```python
crisis = df[df["year"].isin([2021, 2022, 2023])].copy()
crisis["premium_per_mwh"] = crisis["premium_gbp"] / crisis["generation_mwh"]
for year in [2021, 2022, 2023]:
    sub = crisis[crisis["year"] == year]
    fig.add_trace(go.Bar(
        x=sub["scheme"], y=sub["premium_per_mwh"],
        name=str(year),
        hovertemplate="%{x} " + str(year) + "<br>£%{y:.1f}/MWh<extra></extra>",
    ))
fig.update_layout(barmode="group")
```

**Footnote subtitle (UI-SPEC):** `"2021 / 2022 / 2023 grouped bars; schemes without gas counterfactual excluded."`

---

### Plotting palette — `plotting/colors.py` MODIFIED

**Analog:** existing `colors.py` lines 16-29 (`TECHNOLOGY_COLORS`, `ALLOCATION_ROUND_COLORS`).

**Pattern — append** (UI-SPEC §"Per-scheme palette" + Provenance discipline):
```python
SCHEME_COLORS: dict[str, str] = {
    "CfD": "#1f77b4",  # offshore-wind anchor (TECHNOLOGY_COLORS["Offshore Wind"])
    "RO": "#d62728",   # biomass anchor (TECHNOLOGY_COLORS["Biomass"])
    # Phase 7-12 reserved slots:
    "FiT": "#ff7f0e",          # solar PV anchor (TECHNOLOGY_COLORS["Solar PV"])
    "Constraint Payments": "#17becf",  # Tol bright teal
    "Capacity Market": "#9467bd",       # ALLOCATION_ROUND_COLORS["Allocation Round 4"]
    "Balancing Services": "#bcbd22",    # colors.create_color_map fallback
    "Grid Socialisation": "#e377c2",    # ALLOCATION_ROUND_COLORS["Allocation Round 6"]
    "SEG": "#8c564b",                   # ALLOCATION_ROUND_COLORS["Allocation Round 5"]
}
"""Per-scheme color palette for cross-scheme charts (X1, X4, X5).

Selection criteria (UI-SPEC §"Per-scheme palette" — locked):
1. Colorblind-safe (Tol bright qualitative palette).
2. Reuse existing TECHNOLOGY_COLORS / ALLOCATION_ROUND_COLORS hexes where the scheme's
   biggest band already has an established theme color (CfD = offshore wind blue;
   RO = biomass red; FiT = solar PV orange).
3. Stable across X-chart variants — same scheme = same color in X1/X4/X5.
4. Anti-aliasing-safe in PNG (WCAG AA contrast against PLOT_BG=#252936).

Provenance:
  source:       Tol Bright Qualitative Palette + project TECHNOLOGY_COLORS reuse
  url:          https://personal.sron.nl/~pault/
  basis:        Deuteranopia/protanopia/tritanopia tested; reuses existing
                colors.py palette where the scheme's biggest band has a theme anchor.
  retrieved_on: 2026-04-25
  next_audit:   when WCAG / colorblind standards revise
"""
```

---

### Plotting orchestrator — `plotting/__main__.py` MODIFIED

**Analog:** existing `__main__.py` (113 lines) — append 5 entries.

**Import pattern** (existing lines 14-46):
```python
from uk_subsidy_tracker.plotting.portal.x1_stacked_total import main as x1_stacked_total
from uk_subsidy_tracker.plotting.portal.x2_cumulative_premium import main as x2_cumulative_premium
from uk_subsidy_tracker.plotting.portal.x3_per_household import main as x3_per_household
from uk_subsidy_tracker.plotting.portal.x4_cost_per_mwh import main as x4_cost_per_mwh
from uk_subsidy_tracker.plotting.portal.x5_2022_crisis import main as x5_2022_crisis
```

**Charts list append** (existing lines 66-90):
```python
charts: list[tuple[str, Callable[[], None]]] = [
    # ... 18 existing entries ...
    # Cross-scheme portal flagship charts (Phase 6)
    ("x1_stacked_total", x1_stacked_total),
    ("x2_cumulative_premium", x2_cumulative_premium),
    ("x3_per_household", x3_per_household),
    ("x4_cost_per_mwh", x4_cost_per_mwh),
    ("x5_2022_crisis", x5_2022_crisis),
]
```

**Skip-on-dormant pattern** (existing lines 48-61) — does NOT apply (no `# dormant: true` line on portal modules).

---

### Schemes barrel — `schemes/__init__.py` MODIFIED

**Pattern (existing line 54 — one-line append):**
```python
from uk_subsidy_tracker.schemes import cfd, portal, ro  # noqa: E402
__all__ = ["SchemeModule", "cfd", "portal", "ro"]
```

(Alphabetical for grep-discoverability per existing comment line 53.)

---

### CI orchestration — `refresh_all.py` MODIFIED

**Analog:** existing `SCHEMES` tuple (lines 30-36).

**Pattern — one-line append (portal MUST be last per RESEARCH §"refresh_all.SCHEMES registration"):**
```python
from uk_subsidy_tracker.schemes import cfd, portal, ro

SCHEMES = (
    ("cfd", cfd),
    ("ro", ro),
    ("portal", portal),  # MUST be last — downstream of all per-scheme rebuilds
)
```

**No further changes** — `refresh_scheme()` (lines 43-64) and `publish_latest()` (lines 67-89) already iterate `SCHEMES` and call the §6.1 contract methods polymorphically.

---

### Publishing dispatch — `publish/manifest.py` MODIFIED

**Analog:** existing `GRAIN_SOURCES["cfd"]` + `["ro"]` (lines 74-139), `GRAIN_TITLES` (lines 141-156), `GRAIN_DESCRIPTIONS` (lines 158-173).

**Pattern — three dict appends (RESEARCH §"manifest.py GRAIN_* registration"):**
```python
GRAIN_SOURCES["portal"] = {
    "cross_scheme": [
        # Portal reads downstream parquets but raw provenance flows from each
        # shipped scheme's raw inputs. List the union of CfD + RO raw files so
        # manifest entry's sources[] block traces back to primary regulator data.
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

**No further changes** — `_assemble_dataset_entries` already iterates `derived_root/<scheme>/*.parquet` and looks up the dicts by `(scheme, grain)` (verified in RESEARCH).

---

### Tests — extension parametrisations

#### `tests/test_aggregates.py` MODIFIED (Wave 1)

**Analog:** existing CfD `test_annual_vs_station_month_parquet` (lines 95-103) + RO `test_ro_annual_vs_station_month_parquet` (lines 191-209). Both use **independent module-scoped fixtures** (per existing PATTERNS comment line 130-135 + line 138).

**Pattern — append after line 257:**
```python
# ===========================================================================
# Portal cross-scheme row-conservation (Plan 06; TEST-03; D-03).
# ===========================================================================

@pytest.fixture(scope="module")
def portal_derived_dir(tmp_path_factory) -> Path:
    """Rebuild portal cross_scheme.parquet once per module (independent of CfD/RO fixtures)."""
    from uk_subsidy_tracker.schemes import cfd, portal, ro
    out = tmp_path_factory.mktemp("test-aggregates-portal-derived")
    # Portal needs both upstream parquets — rebuild them into sibling dirs first
    # but use real DERIVED_DIR for the join read (planner verifies pattern fits).
    cfd.rebuild_derived(output_dir=PROJECT_ROOT / "data/derived/cfd")  # OR use tmp dir
    ro.rebuild_derived(output_dir=PROJECT_ROOT / "data/derived/ro")
    portal.rebuild_derived(output_dir=out)
    return out


@pytest.fixture(scope="module")
def cross_scheme(portal_derived_dir) -> pd.DataFrame:
    return pq.read_table(portal_derived_dir / "cross_scheme.parquet").to_pandas()


def test_cross_scheme_row_conservation(cross_scheme):
    """D-03: sum(cross_scheme.cost_gbp by scheme) == per-scheme annual_summary totals."""
    # CfD subset
    cfd_total_cross = float(cross_scheme[cross_scheme["scheme"] == "CfD"]["cost_gbp"].sum())
    cfd_src = pq.read_table(PROJECT_ROOT / "data/derived/cfd/annual_summary.parquet").to_pandas()
    cfd_total_src = float(cfd_src["cfd_payments_gbp"].sum())
    assert abs(cfd_total_cross - cfd_total_src) <= 1.0, (  # £1 tolerance
        f"CfD row-conservation failed: cross={cfd_total_cross:,.0f} src={cfd_total_src:,.0f}"
    )
    # RO subset (GB-only, NaN-cost dropped)
    ro_total_cross = float(cross_scheme[cross_scheme["scheme"] == "RO"]["cost_gbp"].sum())
    ro_src = pq.read_table(PROJECT_ROOT / "data/derived/ro/annual_summary.parquet").to_pandas()
    ro_src_gb = ro_src[(ro_src["country"] == "GB") & ro_src["ro_cost_gbp"].notna()]
    ro_total_src = float(ro_src_gb["ro_cost_gbp"].sum())
    assert abs(ro_total_cross - ro_total_src) <= 1.0
```

**Deviation:** unlike the CfD/RO patterns where the test rebuilds into a tmp dir, portal's join reads from `data/derived/cfd/` + `data/derived/ro/` — planner decides whether to (a) symlink/copy CfD+RO parquets into the tmp tree first, or (b) parametrise `cross_scheme_model.build_cross_scheme()` to accept upstream paths.

#### `tests/test_schemas.py` MODIFIED (Wave 1)

**Analog:** existing `_GRAIN_MODELS` dict (lines 105-111) and parametrised test (lines 114-132).

**Pattern — extend `_GRAIN_MODELS` OR add a new `_PORTAL_GRAIN_MODELS` dict** (matches RO precedent of independent dict at line 155):
```python
_PORTAL_GRAIN_MODELS = {
    "cross_scheme": CrossSchemeRow,
}

@pytest.fixture(scope="module")
def portal_derived_dir(tmp_path_factory) -> Path:
    from uk_subsidy_tracker.schemes import cfd, portal, ro
    out = tmp_path_factory.mktemp("test-schemas-portal-derived")
    cfd.rebuild_derived(); ro.rebuild_derived()  # prerequisites
    portal.rebuild_derived(output_dir=out)
    return out


@pytest.mark.parametrize("grain, model", list(_PORTAL_GRAIN_MODELS.items()))
def test_portal_parquet_grain_schema(grain, model, portal_derived_dir):
    """TEST-02 / D-19: cross_scheme.parquet conforms to CrossSchemeRow.

    Column-order discipline (D-10) + per-row Pydantic validation. Mirrors
    test_parquet_grain_schema (CfD, lines 114-132) and test_ro_parquet_grain_schema (lines 164-199).
    """
    path = portal_derived_dir / f"{grain}.parquet"
    assert path.exists()
    df = pq.read_table(path).to_pandas()
    expected_columns = list(model.model_fields.keys())
    assert list(df.columns) == expected_columns
    for row in df.to_dict(orient="records"):
        model.model_validate(row)
```

#### `tests/test_determinism.py` MODIFIED (Wave 1)

**Analog:** existing `GRAINS` tuple (line 24-30) + `test_parquet_content_identical` (lines 47-63) + RO `RO_GRAINS` (line 86-92).

**Pattern — append after line 142:**
```python
# Portal byte-identity (Plan 06; TEST-05; D-21).
PORTAL_GRAINS = ("cross_scheme",)


@pytest.fixture(scope="module")
def portal_derived_once(tmp_path_factory) -> Path:
    from uk_subsidy_tracker.schemes import cfd, portal, ro
    out = tmp_path_factory.mktemp("portal-derived-run-1")
    cfd.rebuild_derived(); ro.rebuild_derived()
    portal.rebuild_derived(output_dir=out)
    return out


@pytest.fixture(scope="module")
def portal_derived_twice(tmp_path_factory) -> Path:
    from uk_subsidy_tracker.schemes import cfd, portal, ro
    out = tmp_path_factory.mktemp("portal-derived-run-2")
    cfd.rebuild_derived(); ro.rebuild_derived()
    portal.rebuild_derived(output_dir=out)
    return out


@pytest.mark.parametrize("grain", PORTAL_GRAINS)
def test_portal_parquet_content_identical(grain, portal_derived_once, portal_derived_twice):
    """TEST-05 / D-21: two consecutive portal.rebuild_derived() calls produce content-identical Parquet."""
    t1 = pq.read_table(portal_derived_once / f"{grain}.parquet")
    t2 = pq.read_table(portal_derived_twice / f"{grain}.parquet")
    assert t1.schema.equals(t2.schema, check_metadata=False)
    assert t1.num_rows == t2.num_rows
    assert t1.equals(t2)
```

#### `tests/test_constants_provenance.py` MODIFIED (Wave 1)

**Analog:** existing `_TRACKED` set (lines 40-74) and `_live_constants()` (lines 78-99).

**Pattern — extend `_TRACKED`:**
```python
_TRACKED = {
    "CCGT_EFFICIENCY", "GAS_CO2_INTENSITY_THERMAL", "DEFAULT_NON_FUEL_OPEX",
    *(f"DEFAULT_CARBON_PRICES_{y}" for y in range(2002, 2027)),
    # Phase 6 — UK households per-year fixtures
    *(f"UK_HOUSEHOLDS_{y}" for y in range(2014, 2025)),  # planner verifies year coverage
}
```

**Pattern — extend `_live_constants()` (lines 78-99) to expand `UK_HOUSEHOLDS` similarly to `DEFAULT_CARBON_PRICES`:**
```python
def _live_constants() -> dict[str, float]:
    live: dict[str, float] = {}
    # ... existing scan of counterfactual module ...
    # NEW — also scan uk_households module
    from uk_subsidy_tracker.data import uk_households
    for year, count in uk_households.UK_HOUSEHOLDS.items():
        live[f"UK_HOUSEHOLDS_{year}"] = float(count)
    return live
```

#### `tests/test_refresh_loop.py` MODIFIED (Wave 1)

**Analog:** RO `test_ro_refresh_converges_on_unchanged_upstream` (lines 211-225).

**Pattern — append portal scheme invariant (mtime-based, no network mock needed):**
```python
import importlib
portal_refresh = importlib.import_module("uk_subsidy_tracker.schemes.portal._refresh")


def test_portal_upstream_changed_returns_true_when_cross_scheme_absent(tmp_path, monkeypatch):
    """Portal dirty-check: cross_scheme.parquet absent → upstream_changed() = True."""
    monkeypatch.setattr("uk_subsidy_tracker.schemes.portal._refresh.PROJECT_ROOT", tmp_path)
    assert portal_refresh.upstream_changed() is True


def test_portal_refresh_is_no_op(tmp_path, monkeypatch):
    """Portal refresh() is a no-op (no upstream URL)."""
    monkeypatch.setattr("uk_subsidy_tracker.schemes.portal._refresh.PROJECT_ROOT", tmp_path)
    portal_refresh.refresh()  # MUST NOT raise
```

#### `tests/test_benchmarks.py` MODIFIED (Wave 7)

**Analog:** `test_ref_constable_ro_reconciliation` (lines 290-335) + `_TOLERANCE_BY_SOURCE` dispatch (lines 102-109).

**Pattern — append `test_ref_total_reconciliation` (RESEARCH §"REF benchmark cross-check" lines 1090-1144):**
```python
@pytest.fixture(scope="module")
def cross_scheme_totals_per_scheme() -> dict[str, dict[int, float]]:
    """{scheme: {year: cost_gbp_bn}} from data/derived/portal/cross_scheme.parquet."""
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


def test_ref_total_reconciliation(benchmarks, cross_scheme_totals_per_scheme):
    """Phase 6 D-03 / Discretion option (b): per-scheme cross-check against REF subset.

    Sums REF entries for shipped schemes (CfD + RO; later phases auto-extend) and
    asserts cross_scheme.parquet totals match within REF_TOLERANCE_PCT.
    """
    if not cross_scheme_totals_per_scheme:
        pytest.fail(
            "cross_scheme.parquet absent — run schemes.portal.rebuild_derived()"
        )
    # RO subset (CfD subset arms in Wave 7 if/when REF CfD entries land in benchmarks.yaml)
    ref_ro_total = sum(
        e.value_gbp_bn for e in benchmarks.ref_constable
        if 2006 <= e.year <= 2023
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

**Deviation from analog:** uses the same `REF_TOLERANCE_PCT = 3.0` constant; HARD BLOCK semantics inherited.

#### `tests/test_headline_sync.py` NEW (Wave 6)

**Analog:** `tests/test_docs_ro_headline_sync.py` (66 lines). Generalised per RESEARCH §"Headline-sync regression test pattern" (lines 942-1036).

**Pattern — single parametrised test file covering all surfaces** (RESEARCH lines 941-1036):
```python
"""Cross-surface headline-sync regression (D-09 + D-11).

Each parametrised case asserts a prose £NN.N bn (or £NNN per household) figure
in a docs/*.md file matches a parquet-derived value to 1 decimal place
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

# 7 cases: homepage_total / homepage_premium / homepage_per_household /
# cfd_paid / cfd_premium / ro_covered / ro_range
# (See RESEARCH §"What surfaces to cover in D-11" lines 1047-1058)

_HEADLINE_RE = re.compile(r"£\s*(\d+(?:\.\d+)?)\s*bn", re.IGNORECASE)
_PER_HOUSEHOLD_RE = re.compile(r"£\s*([\d,]+)\b")  # £3,200 → "3,200"


@dataclass(frozen=True)
class HeadlineCase:
    surface: str
    md_path: Path
    md_line_window: tuple[int, int]
    regex: re.Pattern
    expected_value: float
    tolerance: float = 0.05  # ±£0.05bn for 1dp comparison


# ... cases declared per RESEARCH lines 993-1019 ...


@pytest.mark.parametrize("case", _CASES, ids=lambda c: c.surface)
def test_headline_matches_parquet(case: HeadlineCase) -> None:
    if not case.md_path.exists():
        pytest.fail(f"Markdown surface missing: {case.md_path}")
    text = "\n".join(
        case.md_path.read_text().splitlines()[case.md_line_window[0]-1:case.md_line_window[1]]
    )
    m = case.regex.search(text)
    assert m, f"No headline found in {case.surface} (regex: {case.regex.pattern})"
    prose_value = round(float(m.group(1).replace(",", "")), 1)
    expected = round(case.expected_value, 1)
    assert abs(prose_value - expected) <= case.tolerance, (
        f"Headline drift ({case.surface}): prose £{prose_value}, "
        f"parquet £{expected}. Either (a) update {case.md_path.name}, "
        f"(b) record a CHANGES.md ## Methodology versions entry."
    )
```

**Migration discipline:** delete `tests/test_docs_ro_headline_sync.py` in Wave 7 (covered by `test_headline_sync.py::ro_covered` parametrised case). RESEARCH §"Migration of existing test_docs_ro_headline_sync.py" (line 1060-1062).

#### `tests/fixtures/constants.yaml` MODIFIED (Wave 1)

**Analog:** existing `DEFAULT_CARBON_PRICES_YYYY` blocks (lines 51-end) — one block per year.

**Pattern — append per-year `UK_HOUSEHOLDS_YYYY` blocks** following the Pydantic `ConstantProvenance` schema (`tests/fixtures/__init__.py` lines 94-124). See "Constants module" section above for the YAML shape.

---

### Documentation pages

#### `docs/portal/x{1..5}-*.md` (5 NEW pages)

**Analog:** `docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md` (172 lines, verified as Phase 3 D-01 6-section template).

**Locked 6-section structure** (UI-SPEC §4 + analog walk):

| § | Heading (verbatim) | Source-exemplar lines | Content discipline |
|---|--------------------|----------------------|---------------------|
| 1 | `# {Chart title}` (H1) + bold-prose blurb + Twitter PNG embed + `[Interactive version](...){target="_blank"}` | analog lines 1-7 | 1 sentence headline, 2-3 sentences expanding |
| 2 | `## What the chart shows` | analog lines 9-31 | Pure description: axes, panels, color-coded categories, what the eye sees first |
| 3 | `## The argument` | analog lines 33-69 | Reading: what the chart proves; 3-5 numbered points; cross-references to scheme pages |
| 4 | `## Methodology` | analog lines 71-111 | Formula sketch (code block) + scope. For X4+X5, include verbatim sentence: `Schemes without a gas counterfactual (CM, Balancing, Grid) are excluded from this view; see [methodology](./methodology.md).` |
| 5 | `## Caveats` | analog lines 113-138 | 3-6 bulleted caveats |
| 6 | `## Data & code` | analog lines 140-159 | GOV-01 four-way coverage block: (a) Primary source link to `cross_scheme.parquet` via `manifest.json`; (b) Chart source code GitHub permalink to `src/uk_subsidy_tracker/plotting/portal/{slug}.py`; (c) Test GitHub permalinks to `tests/test_aggregates.py::test_cross_scheme_row_conservation` + `tests/test_benchmarks.py::test_ref_total_reconciliation`; (d) Reproduce bash block |
| 7 (opt) | `## See also` | analog lines 161-172 | Cross-link to `methodology.md` + relevant scheme pages |

**Embed pattern** (UI-SPEC §"X1 hero embed" + analog lines 5-7):
```markdown
![{alt-text from UI-SPEC Copywriting Contract}](../charts/html/{slug}_twitter.png)

[Interactive version](../charts/html/{slug}.html){target="_blank"}
```

**Reproduce block** (analog lines 156-159):
```bash
uv run python -m uk_subsidy_tracker.plotting.portal.{slug}
```

**Heading-depth rule:** H1 (page title only), H2 (section names), H3 (only inside §3 or §4 if a sub-argument warrants it, e.g. X5 may use `### 2021 vs 2022 vs 2023`). Avoid H4+.

**Voice:** adversarial-clinical, third-person, present tense (UI-SPEC §"Voice"). Mirror `cfd.md`/`ro.md` lead paragraphs.

#### `docs/portal/methodology.md` NEW

**Analog:** `docs/methodology/gas-counterfactual.md` (length and section discipline).

**Locked 8-section structure** (UI-SPEC §5):
1. `# Cross-scheme methodology` — 1 framing paragraph
2. `## Cross-scheme aggregation` — long-format schema; sum-by-year join; `methodology_version` per-row
3. `## Scheme-year vs calendar-year reconciliation` — RO Apr-Mar vs CfD CY; `latest_fully_reconciled_year` rule
4. `## No-gas-counterfactual schemes` — CM/Balancing/Grid exclusion; ARCH §5.3 cross-ref
5. `## Per-household division convention` — ONS source URL+sha256+retrieved_on; per-year preferred
6. `## Partial-coverage caveat` — "covers 2 of 8 schemes"; how regression test re-arms
7. `## Reference checks` — REF Constable + Turver as test-file tolerance anchors only (Phase 05.2 D-15/D-16; user-memory `feedback_internal_artefacts_off_public_docs.md`); cite `tests/fixtures/benchmarks.yaml`, NOT as co-publishers
8. `## Reproducibility` — `git clone + uv sync + uv run python -c "from uk_subsidy_tracker.schemes import portal; portal.refresh(); portal.rebuild_derived(); portal.regenerate_charts()"`

**Length target:** 600-1200 words.

#### `docs/portal/index.md` (NEW, recommended per UI-SPEC §6 Note for planner)

**Analog:** `docs/schemes/index.md` (~200 words). Mirror its shape — "what is this section + how to read it + what's currently shipped".

#### `docs/index.md` MODIFIED

**Analog:** `docs/themes/cost/index.md` lines 9-59 for the `grid cards` markup pattern. Existing scheme-grid block (current `docs/index.md` lines 22-76) preserved verbatim — only headline figures inside CfD + RO tiles update.

**Pattern — insert above `## Schemes` (current line 20):**

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

![Total UK subsidy stacked by scheme — covered schemes only](charts/html/x1_stacked_total_twitter.png)

[Interactive version](charts/html/x1_stacked_total.html){target="_blank"}

---
```

**Number formatting** (UI-SPEC §"Number-formatting rules"):
- Cards A/B: `£N.N bn` (with space, 1 decimal, e.g. `£87.5 bn`)
- Card C: `£N,NNN` (no decimal, comma thousands separator, e.g. `£3,200`)
- Caveat: italic single line via `*…*`

**No `---` separator inside the card** (UI-SPEC §"Card layout convention" — distinguishes stat cards from navigational cards).

**Status section update:** existing `docs/index.md` line 94 mentions "Two scheme modules are shipped"; planner verifies whether to update this language to reflect cross-scheme aggregation now exists (CONTEXT §"Known pre-existing considerations").

#### `mkdocs.yml` MODIFIED

**Analog:** existing `Schemes:` block (mkdocs.yml lines ~60-65 per RESEARCH §"mkdocs.yml nav placement"). Insert new top-level `Portal:` between `Schemes` and `Data` (UI-SPEC §6 LOCKED).

**Pattern (UI-SPEC §6 verbatim):**
```yaml
  - Portal:
      - Overview: portal/index.md
      - X1 Total subsidy stacked by scheme: portal/x1-stacked-total.md
      - X2 Cumulative premium over gas: portal/x2-cumulative-premium.md
      - X3 Cost per household by scheme: portal/x3-per-household.md
      - X4 Cost per MWh by scheme: portal/x4-cost-per-mwh.md
      - X5 2022 crisis comparison: portal/x5-2022-crisis.md
      - Methodology: portal/methodology.md
```

**`mkdocs build --strict` discipline** (RESEARCH §"mkdocs --strict known warnings"): every Wave-4 commit that adds a new `docs/portal/*.md` file MUST also update `mkdocs.yml::nav` in the same commit (else `omitted_files: warn` fires). Run `uv run mkdocs build --strict` after every Wave 4+5 commit.

---

## Shared Patterns

### Provenance discipline (constant_provenance_pattern user memory)

**Source:** `src/uk_subsidy_tracker/counterfactual.py::CCGT_EFFICIENCY` (lines 12-25)
**Apply to:** `src/uk_subsidy_tracker/data/uk_households.py` AND `src/uk_subsidy_tracker/plotting/colors.py::SCHEME_COLORS`
**Grep-discoverable test:** `grep -rn "^Provenance:" src/` MUST find the new block.

```python
"""Constant value description.

Provenance:
  source:       Publisher + dataset name
  url:          Primary URL
  basis:        Methodological basis
  retrieved_on: ISO date
  next_audit:   ISO date or descriptive
"""
```

### Determinism (D-21 / D-22 contract)

**Source:** `src/uk_subsidy_tracker/schemes/cfd/cost_model.py::_write_parquet` (lines 47-68)
**Apply to:** `src/uk_subsidy_tracker/schemes/portal/cross_scheme_model.py` — **import, do NOT re-implement**:
```python
from uk_subsidy_tracker.schemes.cfd.cost_model import _write_parquet
```
This is intentional cross-scheme coupling per Phase 5 PATTERNS-04.

**Discipline:**
- No `datetime.now()`, no `time.time()`, no `random.*`.
- Every `groupby` passes `sort=True` explicitly.
- Final sort key explicit and stable: `.sort_values(["year", "scheme"], kind="mergesort").reset_index(drop=True)`.

### `methodology_version` flow (D-12 / GOV-04)

**Source:** `src/uk_subsidy_tracker/counterfactual.py::METHODOLOGY_VERSION = "0.1.0"` (line 38)
**Apply to:** every Pydantic row model AND every parquet writer chain.

Flow: `counterfactual.METHODOLOGY_VERSION` → DataFrame column via `df["methodology_version"] = METHODOLOGY_VERSION` → parquet column → top-level `manifest.methodology_version` field.

### Independent module-scoped fixtures (test pattern)

**Source:** `tests/test_aggregates.py` lines 130-135 PATTERNS comment: "RO uses INDEPENDENT module-scoped fixtures … and does NOT merge into the CfD parametrisation."

**Apply to:** every new test fixture for portal — use `portal_derived_dir`, `portal_derived_once`, `portal_derived_twice` (independent of CfD/RO fixtures) so portal rebuilds amortise independently and cross-scheme ordering assumptions are impossible.

### Empty-data placeholder (chart pattern)

**Source:** `src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py::_placeholder` (lines 81-103)
**Apply to:** all 5 X-chart modules in `plotting/portal/`. Allows `python -m uk_subsidy_tracker.plotting` to succeed under CI even when `cross_scheme.parquet` is absent.

### `importlib.import_module` shadow-bypass (test pattern)

**Source:** `tests/test_refresh_loop.py` lines 23-33 — needed because `__init__.py` aliases `from ._refresh import refresh as _refresh`, which shadows the submodule attribute.

**Apply to:** any test patching portal `_refresh` module:
```python
import importlib
portal_refresh = importlib.import_module("uk_subsidy_tracker.schemes.portal._refresh")
```

### Atomic-commit discipline (Phase 1 D-16)

**Apply to:** every wave per CONTEXT.md Discretion suggested 7-wave grouping. Wave-4 commits MUST update `mkdocs.yml::nav` in the same commit as the `docs/portal/*.md` they add.

### `Twitter PNG hero + Interactive HTML link` embed pattern

**Source:** every existing scheme/theme chart embed (cfd.md, ro.md, all theme pages).

**Apply to:** every X-chart embed in `docs/index.md` and `docs/portal/x{1..5}-*.md`:
```markdown
![{alt-text}](path/to/chart_twitter.png)

[Interactive version](path/to/chart.html){target="_blank"}
```

---

## No Analog Found

**None.** Every file in the Phase 6 scope has a closest analog inside the codebase. RESEARCH.md primary recommendation (line 19) confirms: "Build `schemes/portal/` as a third scheme module that mirrors `schemes/ro/__init__.py` shape verbatim."

---

## Deviations Worth Calling Out (executor MUST internalise)

| File | Deviation from analog | Rationale |
|------|----------------------|-----------|
| `schemes/portal/__init__.py` | `refresh()` is a no-op | Portal is downstream of all per-scheme refreshes; no upstream URL. |
| `schemes/portal/_refresh.py` | mtime-compare instead of sha256-compare | Portal's "upstream" is sibling parquets, not URL-fetched files. |
| `schemes/portal/cross_scheme_model.py` | NO scheme-year arithmetic, NO defect-fix branches | Aggregation is a thin column-rename + concat over already-validated annual_summary parquets. |
| `schemas/portal.py::CrossSchemeRow` | NO `country` column | GB-only filter happens in the join layer. |
| `plotting/portal/x1_stacked_total.py` | Build TWO figures (one with rangeselector for HTML, one without for PNG) | UI-SPEC §"X1 hero embed" requires PNG hero to be a static "All-time" view. |
| `plotting/portal/x{1..5}` | Year column coerced to `pd.to_datetime(year, format='%Y')` | Plotly rangeselector requires `type="date"` axis. Parquet `year` stays `int64` for D-21 determinism. |
| `tests/test_*.py` portal extensions | Independent module-scoped fixtures (`portal_derived_dir`, `portal_derived_once`, etc.) | Same discipline as RO precedent (test_aggregates.py:130-135). |
| `data/uk_households.py` | Per-year `dict[int, int]` (counts, not £) | UI-SPEC X3 needs per-year denominator for historical accuracy. |
| `tests/test_constants_provenance.py::_live_constants` | Extended to scan `uk_households` module too | Currently scans only `counterfactual.py`. |
| `tests/test_benchmarks.py::test_ref_total_reconciliation` | Per-scheme REF subset (option b), NOT the £25.8bn aggregate | RESEARCH §"Note on the £25.8bn aggregate" — that figure is REF's full-year-2024 cross-scheme total, not a sum of REF Table 1 entries. |
| `docs/portal/methodology.md` §7 "Reference checks" | REF + Turver cited clinically as test-file tolerance anchors only | User memory `feedback_internal_artefacts_off_public_docs.md`; Phase 05.2 D-15/D-16. |
| `tests/test_docs_ro_headline_sync.py` | DELETE in Wave 7 | Generalised by `test_headline_sync.py::ro_covered` parametrised case. |

---

## Metadata

**Analog search scope:**
- `src/uk_subsidy_tracker/schemes/{cfd,ro}/__init__.py + _refresh.py`
- `src/uk_subsidy_tracker/schemes/{cfd,ro}/{aggregate_model,cost_model,aggregation}.py`
- `src/uk_subsidy_tracker/schemas/{cfd,ro}.py`
- `src/uk_subsidy_tracker/plotting/{chart_builder,colors,theme,__main__}.py`
- `src/uk_subsidy_tracker/plotting/subsidy/*.py` (11 modules)
- `src/uk_subsidy_tracker/publish/manifest.py`, `refresh_all.py`
- `src/uk_subsidy_tracker/counterfactual.py`, `data/sidecar.py`
- `tests/test_{aggregates,schemas,determinism,benchmarks,constants_provenance,refresh_loop,docs_ro_headline_sync}.py`
- `tests/fixtures/{__init__.py, constants.yaml, benchmarks.yaml}`
- `docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md`, `docs/themes/cost/index.md`, `docs/index.md`, `docs/methodology/gas-counterfactual.md`, `docs/schemes/{cfd,ro}.md`
- `data/derived/{cfd,ro}/`, `data/raw/ons/`
- `mkdocs.yml`

**Files inspected:** 35
**Pattern extraction date:** 2026-04-25
**Substrate confidence:** HIGH — every analog file verified to exist on disk; line numbers and code excerpts taken from the live files (not from RESEARCH.md restatement).
