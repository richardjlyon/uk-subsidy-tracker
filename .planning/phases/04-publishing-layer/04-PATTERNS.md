# Phase 4: Publishing Layer — Pattern Map

**Mapped:** 2026-04-22
**Files analyzed:** 30 (17 new + 13 modified)
**Analogs found:** 28 / 30 (two new workflow/snapshot files have partial analogs only)

This document maps every file created or modified in Phase 4 to the closest existing analog in the repo and extracts the concrete code excerpts the planner and implementers must copy. Sections are ordered in the sequence the planner will likely use them: (1) File classification; (2) Per-file pattern assignments; (3) Shared cross-cutting patterns; (4) Files with no strong analog.

---

## File Classification

### New files (17)

| New file | Role | Data flow | Closest analog | Match quality |
|---|---|---|---|---|
| `src/uk_subsidy_tracker/schemas/__init__.py` | package | — | `src/uk_subsidy_tracker/data/__init__.py` | exact (barrel) |
| `src/uk_subsidy_tracker/schemas/cfd.py` | model (Pydantic) | transform → JSON Schema + column contract | `tests/fixtures/__init__.py` (Pydantic v2) + `src/uk_subsidy_tracker/data/lccc.py` (pandera schemas) | role-match (Pydantic) + role-match (pandera alongside) |
| `src/uk_subsidy_tracker/schemes/__init__.py` | Protocol | — | none in repo — use `typing.Protocol` per RESEARCH §Pattern 3 | no analog |
| `src/uk_subsidy_tracker/schemes/cfd/__init__.py` | module (§6.1 contract) | orchestration | `src/uk_subsidy_tracker/data/__init__.py` (barrel of public callables) | role-match |
| `src/uk_subsidy_tracker/schemes/cfd/cost_model.py` | service / derivation | transform (CSV → Parquet) | `src/uk_subsidy_tracker/plotting/subsidy/cfd_dynamics.py::_prepare()` | exact (logic to hoist) |
| `src/uk_subsidy_tracker/schemes/cfd/aggregation.py` | service / derivation | transform (groupby rollups) | `src/uk_subsidy_tracker/plotting/subsidy/cfd_payments_by_category.py::main()` + `lorenz.py::main()` + `subsidy_per_avoided_co2_tonne.py::main()` | exact (logic to hoist) |
| `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py` | service / derivation | transform (projection) | `src/uk_subsidy_tracker/plotting/subsidy/remaining_obligations.py::main()` | exact (logic to hoist) |
| `src/uk_subsidy_tracker/publish/__init__.py` | package | — | `src/uk_subsidy_tracker/data/__init__.py` | exact (barrel) |
| `src/uk_subsidy_tracker/publish/manifest.py` | service | transform (disk state → JSON) | `src/uk_subsidy_tracker/data/lccc.py::LCCCAppConfig` + `tests/fixtures/__init__.py::Benchmarks` | exact (Pydantic + loader) |
| `src/uk_subsidy_tracker/publish/csv_mirror.py` | service | file I/O (Parquet → CSV) | `src/uk_subsidy_tracker/data/ons_gas.py::load_gas_price()` (file-I/O shape) | role-match |
| `src/uk_subsidy_tracker/publish/snapshot.py` | service / CLI | batch | `src/uk_subsidy_tracker/plotting/__main__.py` (entry-point shape) | role-match |
| `src/uk_subsidy_tracker/refresh_all.py` | CLI / orchestrator | batch + dirty-check | `src/uk_subsidy_tracker/plotting/__main__.py` (entry-point shape) | role-match |
| `.github/workflows/refresh.yml` | CI config | event-driven (cron + dispatch) | `.github/workflows/ci.yml` | exact |
| `.github/workflows/deploy.yml` | CI config | event-driven (tag push) | `.github/workflows/ci.yml` | role-match (same action versions) |
| `tests/test_determinism.py` | test | parametrised pytest | `tests/test_counterfactual.py` (parametrise + remediation message) + `tests/test_aggregates.py` (fixture loader) | exact |
| `tests/test_constants_provenance.py` | test | parametrised pytest | `tests/test_counterfactual.py` (parametrise + remediation message) | exact |
| `tests/fixtures/constants.yaml` | fixture data | YAML | `tests/fixtures/benchmarks.yaml` | exact (shape carryover) |
| `docs/data/index.md` | docs | — | `docs/methodology/gas-counterfactual.md` (prose + code-fence style) | role-match (content differs) |
| `data/raw/lccc/*.meta.json`, `data/raw/elexon/*.meta.json`, `data/raw/ons/*.meta.json` (5 files) | data / sidecar | JSON | none in repo — shape defined by ARCHITECTURE §4.1 + RESEARCH §Pattern 6 | no analog (greenfield) |

### Modified files (13)

| Modified file | Role | Data flow | Modification type |
|---|---|---|---|
| `pyproject.toml` | config | — | add `pyarrow` + `duckdb` dependencies |
| `src/uk_subsidy_tracker/counterfactual.py` | model | — | propagate `METHODOLOGY_VERSION` into every Parquet column that uses counterfactual output (already done for the DataFrame — Phase 4 ensures it flows through rebuild_derived) |
| `src/uk_subsidy_tracker/data/lccc.py` | loader | file I/O | update `filename`/path to nested `data/raw/lccc/actual-cfd-generation.csv` layout |
| `src/uk_subsidy_tracker/data/elexon.py` | loader | file I/O | rename `AGWS_FILE`, `SYSTEM_PRICE_FILE` constants |
| `src/uk_subsidy_tracker/data/ons_gas.py` | loader | file I/O | rename `GAS_SAP_DATA_FILENAME` |
| `src/uk_subsidy_tracker/data/lccc_datasets.yaml` | config | — | update `filename:` fields to hyphenated names (no path prefix; loader already controls directory) |
| `src/uk_subsidy_tracker/plotting/__main__.py` | CLI | — | possible no-op; only if any chart is migrated to read from derived Parquet |
| `mkdocs.yml` | config | — | add `Data: data/index.md` nav entry |
| `docs/index.md` | docs | — | add "For journalists / academics → Use our data" link |
| `docs/about/citation.md` | docs | — | reference versioned-snapshot release URL pattern |
| `CHANGES.md` | docs | — | `[Unreleased]` entries per D-04/05/07/16/23/26 |
| `tests/fixtures/__init__.py` | fixture loader | — | add `ConstantProvenance` model + `load_constants()` alongside existing `BenchmarkEntry` + `load_benchmarks()` |
| `tests/fixtures/benchmarks.yaml` | fixture data | — | replace `lccc_self: []` with 1+ entry per D-26 |
| `tests/test_schemas.py` | test | — | add Parquet-variant tests alongside existing raw-CSV tests |
| `tests/test_aggregates.py` | test | — | add Parquet-variant tests alongside existing raw-CSV tests |

---

## Pattern Assignments

### A. Pydantic + YAML loader pattern — `publish/manifest.py`, `schemas/cfd.py`, `tests/fixtures/__init__.py`

**Primary analog:** `tests/fixtures/__init__.py` (Pydantic v2 + `yaml.safe_load` + source-key injection).
**Secondary analog:** `src/uk_subsidy_tracker/data/lccc.py::LCCCAppConfig` (matching Pydantic + YAML idiom already adopted in Phase 2).

**Imports block to copy (exactly)** — from `tests/fixtures/__init__.py:13-17`:

```python
from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, HttpUrl
```

**Two-layer Pydantic + source-key injection loader** — `tests/fixtures/__init__.py:57-74`:

```python
def load_benchmarks(config_path: str = "benchmarks.yaml") -> Benchmarks:
    """Load and validate benchmarks from `tests/fixtures/benchmarks.yaml`.

    Injects the parent YAML key as the `source` field on each
    `BenchmarkEntry` so downstream test-failure messages can cite it.
    """
    default_dir = Path(__file__).parent
    with open(default_dir / config_path, "r") as f:
        raw = yaml.safe_load(f) or {}

    # Inject `source` on every entry from its parent key before Pydantic validation.
    for source_key, entries in raw.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            entry["source"] = source_key

    return Benchmarks(**raw)
```

**Simpler variant** — `src/uk_subsidy_tracker/data/lccc.py:77-82`:

```python
def load_lccc_config(config_path: str = "lccc_datasets.yaml") -> LCCCAppConfig:
    """Load the dataset configurations from a YAML file."""
    default_dir = Path(__file__).parent
    with open(default_dir / config_path, "r") as f:
        raw_config = yaml.safe_load(f)
        return LCCCAppConfig(**raw_config)
```

**Pydantic model shape to copy** — `tests/fixtures/__init__.py:20-54`:

```python
class BenchmarkEntry(BaseModel):
    """A single benchmark figure from a named source."""

    source: str = Field(..., description="Parent YAML key, e.g. 'lccc_self' or 'obr_efo'.")
    year: int = Field(..., ge=2015, le=2050)
    value_gbp_bn: float = Field(..., description="Published aggregate value in £bn.")
    url: HttpUrl
    retrieved_on: date
    notes: str
    tolerance_pct: float = Field(..., gt=0, le=50.0)


class Benchmarks(BaseModel):
    lccc_self: list[BenchmarkEntry] = Field(default_factory=list)
    # …
```

**Apply to:**

1. `src/uk_subsidy_tracker/publish/manifest.py` — `Manifest` / `Dataset` / `Source` Pydantic models (field shape given by ARCHITECTURE §4.3 verbatim per D-07; dedicated model-field list in RESEARCH §Pattern 2 lines 510-546). Use `url: str` not `HttpUrl` per RESEARCH pitfall 6. Loader function is the `build()` method (RESEARCH §Pattern 2 lines 578-614).
2. `src/uk_subsidy_tracker/schemas/cfd.py` — `StationMonthRow`, `AnnualSummaryRow`, `ByTechnologyRow`, `ByAllocationRoundRow`, `ForwardProjectionRow` models. Column order = Pydantic field-declaration order (D-10 default). `json_schema_extra={"dtype": "...", "unit": "..."}` on each `Field` per RESEARCH §Pattern 5 lines 770-810.
3. `tests/fixtures/__init__.py` — add `ConstantProvenance` model + `Constants` container model + `load_constants()` function that mirrors `load_benchmarks()`. Inject parent YAML key as the entry name. Use `date` for `retrieved_on` and `next_audit`; use `float | dict[int, float]` for `value` (or expand dict entries into synthetic keys per RESEARCH §Pattern 7 lines 913-935).

**Important discipline (already established):** the loader lives in the `__init__.py` (or a dedicated module co-located with the YAML); it is **the only** place that reads the YAML; tests import the loader, not the YAML.

---

### B. Pandera schema + loader-owned validation — `src/uk_subsidy_tracker/schemes/cfd/*.py`

**Primary analog:** `src/uk_subsidy_tracker/data/lccc.py` (lccc_generation_schema + lccc_portfolio_schema with `.validate()` called inside `load_lccc_dataset`).

**Loader-owned validation excerpt** — `src/uk_subsidy_tracker/data/lccc.py:105-114`:

```python
def load_lccc_dataset(description: str) -> pd.DataFrame:
    """Load and vallidate an LCCC dataset from its lccc_datasets.yaml description."""
    config = load_lccc_config()
    filename = config.dataset(description).filename
    df = pd.read_csv(DATA_DIR / filename)

    schema = SCHEMAS[description]
    df = schema.validate(df)

    return df
```

**Pandera schema shape to copy** — `src/uk_subsidy_tracker/data/lccc.py:36-54`:

```python
lccc_generation_schema = pa.DataFrameSchema(
    {
        "Settlement_Date": pa.Column("datetime64[ns]"),
        "CfD_ID": pa.Column(str),
        "CFD_Generation_MWh": pa.Column(float, nullable=True),
        "CFD_Payments_GBP": pa.Column(float),
        # …
    },
    strict=False,
    coerce=True,
)
```

**Pandera import** — `src/uk_subsidy_tracker/data/lccc.py:6` and `src/uk_subsidy_tracker/data/ons_gas.py:6`:

```python
import pandera.pandas as pa
```

Note the `pandera.pandas` submodule (not plain `pandera`) — canonical for this project.

**Apply to:**

- `src/uk_subsidy_tracker/schemes/cfd/cost_model.py`, `aggregation.py`, `forward_projection.py` — each file's *Parquet writer function* calls `schema.validate(df)` immediately before `pq.write_table(df, path)`. Schema lives as a module-level constant (e.g. `station_month_schema = pa.DataFrameSchema({...}, coerce=True)`) or is derived from the Pydantic model in `schemas/cfd.py`. Pandera `.validate()` runs inside the *writer*, not the reader — the pattern "loader owns validation" becomes "derivation owns validation" in this layer.
- Alternatively, derive the pandera schema from the Pydantic schema in `schemas/cfd.py` so there is a single declaration. Planner picks one; document the choice in PLAN.

---

### C. Aggregation logic to hoist — `schemes/cfd/cost_model.py`, `aggregation.py`, `forward_projection.py`

These three files are the direct destination for code currently in the chart files. Below is the concrete mapping.

#### C.1 `schemes/cfd/cost_model.py` — `station_month` grain

**Source to hoist:** `src/uk_subsidy_tracker/plotting/subsidy/cfd_dynamics.py::_prepare()` (lines 32-66) plus `cfd_vs_gas_cost.py::_prepare_monthly()` (lines 68-100). Both produce a station × month grain from LCCC `Actual CfD Generation` keyed on `Settlement_Date` and `CfD_ID`.

**Representative excerpt** — `cfd_dynamics.py:32-66`:

```python
def _prepare() -> pd.DataFrame:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df = df.dropna(subset=["CFD_Generation_MWh", "Strike_Price_GBP_Per_MWh"])
    df = df[df["CFD_Generation_MWh"] > 0]

    cf_daily = compute_counterfactual().set_index("date")["counterfactual_total"]

    df["strike_x_gen"] = df["Strike_Price_GBP_Per_MWh"] * df["CFD_Generation_MWh"]
    daily = df.groupby("Settlement_Date").agg(
        gen=("CFD_Generation_MWh", "sum"),
        strike_x_gen=("strike_x_gen", "sum"),
    )
    daily["strike"] = daily["strike_x_gen"] / daily["gen"]
    daily["counterfactual"] = cf_daily.reindex(daily.index)
    daily = daily.dropna(subset=["counterfactual"])
    # …
    daily["month"] = daily.index.to_period("M").to_timestamp()
    monthly = daily.groupby("month").agg(
        gen=("gen", "sum"),
        strike_x_gen=("strike_x_gen", "sum"),
        cf_x_gen=("cf_x_gen", "sum"),
        premium_gbp=("premium_gbp", "sum"),
    )
```

**Target shape of `build_station_month(output_dir)`**: produce one row per `(CfD_ID, month_end)` with columns `station_id, name, technology, allocation_round, month_end, cfd_generation_mwh, cfd_payments_gbp, strike_price_gbp_per_mwh, market_reference_price_gbp_per_mwh, methodology_version`. Per D-03 this derivation reads `data/raw/` directly — do not call `load_lccc_dataset` (though you may delegate through it) — and writes via `pq.write_table` per RESEARCH §Pattern 1.

#### C.2 `schemes/cfd/aggregation.py` — `annual_summary`, `by_technology`, `by_allocation_round`

**Source to hoist — annual summary:** `cfd_vs_gas_cost.py::_prepare_monthly()` (monthly → annual sum is one additional `.resample('YE').sum()` or grouping).

**Source to hoist — by_technology:** `subsidy_per_avoided_co2_tonne.py:42-58`:

```python
df["Year"] = df["Settlement_Date"].dt.year
# …
grouped = (
    df.groupby(["Allocation_round", "Year"])
    .agg(
        payments=("CFD_Payments_GBP", "sum"),
        co2_avoided=("Avoided_GHG_tonnes_CO2e", "sum"),
        generation=("CFD_Generation_MWh", "sum"),
    )
    .reset_index()
)
```

and `cfd_payments_by_category.py:48-67`:

```python
df["category"] = df["Technology"].map(_categorise)
df["month"] = df["Settlement_Date"].dt.to_period("M").dt.to_timestamp()
df["cfd_cost"] = (
    df["Market_Reference_Price_GBP_Per_MWh"] * df["CFD_Generation_MWh"]
    + df["CFD_Payments_GBP"]
)

pivot_m = (
    df.pivot_table(
        index="month",
        columns="category",
        values="cfd_cost",
        aggfunc="sum",
        fill_value=0,
    )
    / 1e6
)
```

**Source to hoist — by_allocation_round:** same pattern as `subsidy_per_avoided_co2_tonne.py` group-by `Allocation_round` (note the column capitalisation inconsistency in raw LCCC data — `Allocation_round` in generation CSV, `Allocation_Round` in portfolio CSV — handled in `remaining_obligations.py:83`).

#### C.3 `schemes/cfd/forward_projection.py`

**Source to hoist:** `remaining_obligations.py::main()` (lines 80-124), specifically:

```python
gen = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
cap = load_lccc_dataset("CfD Contract Portfolio Status")
cap = cap.rename(columns={"CFD_ID": "CfD_ID"})

first_gen = gen.groupby("CfD_ID")["Settlement_Date"].min().rename("first_gen_date")
units = cap.merge(first_gen, on="CfD_ID", how="left")

units["start"] = units["Expected_Start_Date"].fillna(units["first_gen_date"])
units["contract_years"] = units["Technology_Type"].apply(
    lambda t: 35 if "Nuclear" in str(t) else 15
)
units["end_year"] = units["start"].dt.year + units["contract_years"]
# …
annual_gen = (
    gen.groupby("CfD_ID")["CFD_Generation_MWh"]
    .sum()
    .div(n_years_per_unit)
    .rename("avg_annual_gen")
)
strike = gen.groupby("CfD_ID").apply(lambda g: np.average(
    g["Strike_Price_GBP_Per_MWh"].dropna(),
    weights=g.loc[g["Strike_Price_GBP_Per_MWh"].notna(), "CFD_Generation_MWh"],
) if g["CFD_Generation_MWh"].sum() > 0 else np.nan).rename("avg_strike")
```

**Note on preservation:** Per D-02, the chart files are permitted to keep their own `_prepare()`-style aggregation in Phase 4. The hoist MUST still happen (D-01) — `schemes/cfd/*` is authoritative — but chart files may continue to re-derive in-memory until Phase 4.1. Planner decides per chart whether to switch chart to read `data/derived/cfd/*.parquet`.

---

### D. Parquet write + determinism — `schemes/cfd/*` + `tests/test_determinism.py`

**Analog:** None in repo (greenfield — pyarrow added as a new dependency per pyproject.toml modification). Pattern sourced from RESEARCH §Pattern 1. These are the canonical forms to copy:

**Pinned Parquet write (D-22)** — apply in every `schemes/cfd/*.py` writer:

```python
import pyarrow as pa
import pyarrow.parquet as pq

def write_parquet(df: pd.DataFrame, path: Path) -> None:
    """Deterministic Parquet writer (D-22).

    Pinned kwargs survive pandas-internal shifts. `preserve_index=False`
    is essential — a stray pandas index column breaks content comparison.
    """
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(
        table, path,
        compression="snappy",     # D-22 pin
        version="2.6",            # pin Parquet format version
        use_dictionary=True,      # default — pin explicitly
        write_statistics=True,    # default — pin explicitly
        data_page_size=1 << 20,   # 1 MB — pin
    )
```

**Content-identity comparison for `test_determinism.py`** — mirror this pattern:

```python
import pyarrow.parquet as pq
import pytest

from uk_subsidy_tracker.schemes import cfd

GRAINS = ("station_month", "annual_summary", "by_technology",
          "by_allocation_round", "forward_projection")


@pytest.fixture(scope="module")
def derived_once(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("derived-run-1")
    cfd.rebuild_derived(output_dir=out)
    return out


@pytest.fixture(scope="module")
def derived_twice(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("derived-run-2")
    cfd.rebuild_derived(output_dir=out)
    return out


@pytest.mark.parametrize("grain", GRAINS)
def test_parquet_content_identical(grain, derived_once, derived_twice):
    t1 = pq.read_table(derived_once / f"{grain}.parquet")
    t2 = pq.read_table(derived_twice / f"{grain}.parquet")
    assert t1.schema.equals(t2.schema, check_metadata=False)
    assert t1.num_rows == t2.num_rows
    assert t1.equals(t2), (
        f"Parquet content drift for {grain} — same input should produce "
        f"identical rows. If intentional (methodology change), bump "
        f"METHODOLOGY_VERSION and add CHANGES.md entry."
    )
```

**Failure-message shape** copies the `test_counterfactual.py` remediation hook:

> `f-string f"…If intentional, bump METHODOLOGY_VERSION (currently {METHODOLOGY_VERSION!r}) and add a CHANGES.md ## Methodology versions entry."`

---

### E. Parametrised pin + remediation-hook tests — `tests/test_constants_provenance.py`, `tests/test_determinism.py`

**Primary analog:** `tests/test_counterfactual.py` (the canonical parametrised-pin template already in the repo; remediation messages cite `METHODOLOGY_VERSION` + `CHANGES.md`).

**Full test shape to copy** — `tests/test_counterfactual.py:38-67`:

```python
@pytest.mark.parametrize(
    "date_str, gas_p_per_kwh, expected",
    [
        ("2019-01-01", 1.5, 39.5887),
        ("2019-06-01", 1.2, 34.1342),
        ("2022-10-01", 8.0, 174.7304),
        ("2019-01-01", 0.0, 12.3160),  # zero-gas regression
    ],
)
def test_counterfactual_pin(date_str, gas_p_per_kwh, expected):
    """TEST-01: pin the formula at 4 decimal places.

    Any change to CCGT_EFFICIENCY, GAS_CO2_INTENSITY_THERMAL, DEFAULT_NON_FUEL_OPEX,
    or DEFAULT_CARBON_PRICES fails this test. If intentional, bump
    METHODOLOGY_VERSION in src/uk_subsidy_tracker/counterfactual.py and add
    an entry to CHANGES.md under ## Methodology versions documenting the change.
    """
    gas = pd.DataFrame({
        "date": pd.to_datetime([date_str]),
        "gas_p_per_kwh": [gas_p_per_kwh],
    })
    df = compute_counterfactual(gas_df=gas)
    actual = df["counterfactual_total"].iloc[0]
    assert round(actual, 4) == expected, (
        f"Formula changed for {date_str} gas={gas_p_per_kwh}: "
        f"expected {expected}, got {round(actual, 4)}. "
        f"If intentional, bump METHODOLOGY_VERSION (currently "
        f"{METHODOLOGY_VERSION!r}) and add a CHANGES.md ## Methodology versions entry."
    )
```

**Module-docstring shape** — `tests/test_counterfactual.py:1-7` (already extended in `tests/test_benchmarks.py:1-16` for the two-check pattern; use the latter when there are multiple related checks).

**Apply to `tests/test_constants_provenance.py`:** RESEARCH §Pattern 7 lines 896-996 spell out the full file. Key imports to copy:

```python
from datetime import date
import pytest

from tests.fixtures import ConstantProvenance, load_constants
from uk_subsidy_tracker import counterfactual
```

Two parametrised tests (`test_every_tracked_constant_in_yaml`, `test_yaml_value_matches_live`), one non-failing warn test (`test_audits_not_overdue`).

**Apply to `tests/test_determinism.py`:** parametrise on `GRAINS` tuple (see section D above). Remediation-hook failure message cites `METHODOLOGY_VERSION` + `CHANGES.md`.

**Cross-reference for fixture loading style:** `tests/test_aggregates.py:18-24` shows the `@pytest.fixture(scope="module")` pattern for loading data once per test module. `tests/test_benchmarks.py:65-77` shows parametrised fixture from YAML via the Pydantic loader.

---

### F. Raw-CSV test scaffolding (extend, don't replace) — `tests/test_schemas.py`, `tests/test_aggregates.py`

**Analog:** the tests themselves (already in repo — Phase 2 scaffolding). Per D-19 and D-20 the **Parquet variants live alongside the existing raw-CSV tests in the same file** — do not create separate files.

**Existing shape to preserve** — `tests/test_schemas.py:1-67` (module docstring explicitly names Phase 4 as the point of completion):

```python
"""Validate raw-source pandera schemas via the public loaders.

Phase 2 pre-Parquet scaffolding for TEST-02. Each test calls a loader
(which runs `schema.validate(df)` internally) and asserts the result is
non-empty with the expected key columns.

Formal TEST-02 is satisfied in Phase 4 when Parquet-schema assertions
are added to this same file.
"""

from uk_subsidy_tracker.data import (
    load_elexon_prices_daily, load_elexon_wind_daily,
    load_gas_price, load_lccc_dataset,
)


def test_lccc_generation_schema():
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    assert not df.empty
    assert "Settlement_Date" in df.columns
    # …
```

**Parquet-variant pattern to add to `tests/test_schemas.py`:** one test per derived grain, each loading the Parquet via `pyarrow.parquet.read_table(...).to_pandas()`, round-tripping through the pandera schema, and asserting no exception plus key-column presence. Use module-level constants (not parametrise) so failures name the grain.

**Parquet-variant pattern to add to `tests/test_aggregates.py`:** row-conservation check across derived grains using `pd.testing.assert_series_equal` — analog already present at lines 27-40:

```python
def test_year_vs_year_tech_sum_match(lccc_gen):
    by_year = lccc_gen.groupby("year")["CFD_Payments_GBP"].sum()
    by_year_tech = (
        lccc_gen.groupby(["year", "Technology"])["CFD_Payments_GBP"]
        .sum().groupby("year").sum()
    )
    pd.testing.assert_series_equal(
        by_year.sort_index(), by_year_tech.sort_index(), check_names=False,
    )
```

Phase-4 additions: `test_annual_vs_station_month_parquet`, `test_by_tech_vs_annual_parquet`, `test_by_round_vs_annual_parquet`. Same exact-equality discipline.

---

### G. `constants.yaml` shape — mirror of `benchmarks.yaml`

**Analog:** `tests/fixtures/benchmarks.yaml`.

**Shape to copy — top-of-file comment block** — `tests/fixtures/benchmarks.yaml:1-14`:

```yaml
# Benchmark reconciliation fixtures for `tests/test_benchmarks.py`.
#
# Each top-level key is a source category. Each entry carries full
# provenance: year, value in £bn, upstream URL, retrieval date, notes
# (scheme-subset / CPI / FY-vs-CY rationale), and per-entry tolerance.
#
# `lccc_self:` is the MANDATORY floor per CONTEXT D-10 (0.1% tolerance) —
# our pipeline reads LCCC raw data, so divergence here is a pipeline bug,
# not a methodology divergence.
```

**`constants.yaml` top-of-file comment block** (adapt):

```yaml
# Constant provenance fixtures for `tests/test_constants_provenance.py`.
#
# Each top-level key is the attribute name on
# `src/uk_subsidy_tracker/counterfactual.py` (or a synthetic
# `{ATTR}_{DICT_KEY}` name for dict entries like DEFAULT_CARBON_PRICES_2022).
#
# Each entry carries structured provenance: source, url, basis,
# retrieved_on, next_audit, value, unit, notes — the same set
# as the `Provenance:` docstring blocks in counterfactual.py (SEED-001
# Tier 2). Drift between the YAML value and the live constant fails
# `test_yaml_value_matches_live` with a remediation message.
```

**Entry shape** — RESEARCH §Pattern 7 example at lines 1007-1055. Example single entry to copy:

```yaml
CCGT_EFFICIENCY:
  source: "BEIS Electricity Generation Costs 2023, Table ES.1"
  url: "https://www.gov.uk/government/publications/electricity-generation-costs-2023"
  basis: "Net HHV efficiency, H-class CCGT mid-range"
  retrieved_on: 2026-04-22
  next_audit: 2027-06-01
  value: 0.55
  unit: "dimensionless (fraction)"
  notes: "Blend of older F-class and modern H-class; existing fleet counterfactual."
```

**Cross-check against existing `counterfactual.py` `Provenance:` docstrings** (lines 12-121) — every entry in `constants.yaml` must match the corresponding docstring block field-for-field. The `Provenance:` grep (`rg "^Provenance:" src/ tests/` per user memory `constant_provenance_pattern`) is the discovery tool.

---

### H. GitHub Actions workflow — `.github/workflows/refresh.yml`, `deploy.yml`

**Primary analog:** `.github/workflows/ci.yml` (Phase 2). Full file is 46 lines; quote it here:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Install uv
        uses: astral-sh/setup-uv@v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run tests
        run: uv run --frozen pytest -v

  docs:
    runs-on: ubuntu-latest
    needs: test   # block docs build until tests pass
    steps:
      - uses: actions/checkout@v5

      - name: Install uv
        uses: astral-sh/setup-uv@v8.1.0
        with:
          enable-cache: true
          python-version: "3.12"

      - name: Install dependencies
        run: uv sync --frozen

      - name: Regenerate charts
        run: uv run --frozen python -m uk_subsidy_tracker.plotting

      - name: Build docs --strict
        run: uv run --frozen mkdocs build --strict
```

**Apply to `.github/workflows/refresh.yml`:**

- **Keep verbatim** the `actions/checkout@v5` + `astral-sh/setup-uv@v8.1.0` (with `enable-cache: true`, `python-version: "3.12"`) + `uv sync --frozen` + `uv run --frozen …` pattern.
- **Add** trigger block (`schedule: - cron: '0 6 * * *'` + `workflow_dispatch`), `permissions` block (`contents: write`, `pull-requests: write`, `issues: write` per D-17), `timeout-minutes: 30`.
- **Add** `peter-evans/create-pull-request@v8` step (planner may pin `@v6`; CONTEXT discretion) and `peter-evans/create-issue-from-file@v6` step per RESEARCH §Pattern 8 lines 1062-1139.
- **Add** a `.github/refresh-failure-template.md` file referenced by `content-filepath` per RESEARCH lines 1143-1156.

**Apply to `.github/workflows/deploy.yml`:**

- **Keep verbatim** the checkout + setup-uv + sync steps from ci.yml.
- **Replace** `on:` block with `push: tags: ['v*']` per D-14.
- **Add** `permissions: contents: write` (upload release assets).
- **Add** `softprops/action-gh-release@v2` step per RESEARCH §Pattern 8 lines 1191-1201.
- Call `uv run --frozen python -m uk_subsidy_tracker.publish.snapshot --version "${{ github.ref_name }}" --output snapshot-out/`.

---

### I. Raw-layer loader path migration — `src/uk_subsidy_tracker/data/*.py` + `lccc_datasets.yaml`

**Analog:** the files being modified. Current shape to preserve during rename:

`src/uk_subsidy_tracker/data/ons_gas.py:12`:

```python
GAS_SAP_DATA_FILENAME = "ons_gas_sap.xlsx"
```

becomes:

```python
GAS_SAP_DATA_FILENAME = "raw/ons/gas-sap.xlsx"
```

(path fragment lives here; `DATA_DIR / GAS_SAP_DATA_FILENAME` resolves correctly because `DATA_DIR` is `PROJECT_ROOT / "data"` per `src/uk_subsidy_tracker/__init__.py:4`).

`src/uk_subsidy_tracker/data/elexon.py:30-31`:

```python
AGWS_FILE = DATA_DIR / "elexon_agws.csv"
SYSTEM_PRICE_FILE = DATA_DIR / "elexon_system_prices.csv"
```

becomes:

```python
AGWS_FILE = DATA_DIR / "raw" / "elexon" / "agws.csv"
SYSTEM_PRICE_FILE = DATA_DIR / "raw" / "elexon" / "system-prices.csv"
```

`src/uk_subsidy_tracker/data/lccc_datasets.yaml:4` and `:10`:

```yaml
filename: "lccc-actual-cfd-generation.csv"
# …
filename: "lccc-cfd-contract-portfolio-status.csv"
```

becomes:

```yaml
filename: "raw/lccc/actual-cfd-generation.csv"
# …
filename: "raw/lccc/cfd-contract-portfolio-status.csv"
```

The LCCC loader (`src/uk_subsidy_tracker/data/lccc.py:109`) already does `pd.read_csv(DATA_DIR / filename)` so prefixing `raw/lccc/` in the YAML is sufficient.

**Atomicity check (D-06):** the rename commit must simultaneously contain (a) `git mv` of all 5 raw files under `data/raw/<publisher>/`, (b) the three Python constant updates + YAML edits above, (c) 5 `.meta.json` sidecars, (d) no other unrelated changes. Verify: `uv run pytest` passes on the rename commit before rebasing.

---

## Shared Patterns

### Import ordering

From `tests/test_benchmarks.py`, `src/uk_subsidy_tracker/data/lccc.py`, and `tests/fixtures/__init__.py`. Every new file follows this order (blank line between groups):

```python
"""Module docstring explaining intent + reference to spec section if any."""

# Standard library
from datetime import datetime, timezone
from pathlib import Path

# Third-party
import pandas as pd
import pyarrow.parquet as pq
import pytest
from pydantic import BaseModel, Field

# Local
from uk_subsidy_tracker import DATA_DIR
from uk_subsidy_tracker.data import load_lccc_dataset
```

- **Absolute imports from `uk_subsidy_tracker`** everywhere; relative imports (`from .lccc import …`) only inside sibling modules in the same package (see `src/uk_subsidy_tracker/data/__init__.py:1-3`).
- **Public API via barrel `__init__.py`** — see `src/uk_subsidy_tracker/data/__init__.py` (three re-exports). Replicate this style in `schemes/__init__.py` and `publish/__init__.py`.

### Type hints

Mandatory on every function signature per CONVENTIONS.md. Example — `compute_counterfactual` signature, `src/uk_subsidy_tracker/counterfactual.py:124-129`:

```python
def compute_counterfactual(
    gas_df: pd.DataFrame | None = None,
    carbon_prices: dict[int, float] | None = None,
    ccgt_efficiency: float = CCGT_EFFICIENCY,
    non_fuel_opex_per_mwh: float = DEFAULT_NON_FUEL_OPEX,
) -> pd.DataFrame:
```

- Union type: `|` operator (Python 3.10+).
- Return type always declared; `-> None` explicit for voids.
- Keyword-only defaults allowed (`*, kwarg=default`) — see `ChartBuilder.format_currency_axis` signature in CONVENTIONS.md:101-114.

### Docstrings

Module-level docstring on every file; triple double-quoted. Pattern from `src/uk_subsidy_tracker/counterfactual.py:1-6`:

```python
"""
Counterfactual electricity cost modelling.

Computes what electricity would cost in a gas-only CCGT grid,
broken down into fuel cost and carbon cost components.
"""
```

Function docstrings: one-line summary + blank line + detail. See `compute_counterfactual:130-141`. No `Args:`/`Returns:` sections required but permitted (inconsistent in repo).

### `Provenance:` docstring block (regulator-sourced constants)

Mandatory for every regulator-sourced constant per user memory `constant_provenance_pattern` and the Phase 3 remediation commit. Grep discoverable via `rg "^Provenance:" src/ tests/`. Shape — `src/uk_subsidy_tracker/counterfactual.py:19-25`:

```
Provenance:
  source:       BEIS Electricity Generation Costs 2023, Table ES.1
  url:          https://www.gov.uk/government/publications/electricity-generation-costs-2023
  basis:        Net HHV efficiency, H-class CCGT mid-range
  retrieved_on: 2026-04-22
  next_audit:   when BEIS/DESNZ publishes next Electricity Generation Costs edition
```

Applies to: any new constant introduced in `schemes/cfd/*.py` (e.g., `DERIVED_DIR` does NOT need it; `NESO_DEMAND_ANCHORS` if hoisted from `remaining_obligations.py` DOES — those three values are regulator-sourced).

### Error handling

Try/except for network operations only; pattern — `src/uk_subsidy_tracker/data/lccc.py:95-102`:

```python
try:
    response = requests.get(url, headers=HEADERS, stream=True)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
except requests.exceptions.RequestException as e:
    print(f"An error occurred while downloading {filename}: {e}")
```

- Never define custom exception classes; rely on stdlib / third-party exceptions.
- No try/except on pandas / pydantic / pandera operations — let them propagate (this is what the tests check).
- `print()` is the project's logging idiom — no `logging` module. Matches CONVENTIONS.md §Logging.

### Atomic commit discipline

Per CONTEXT `### Established Patterns` and user memory: each concern gets its own commit. Phase 4 commit sequence (planner orders):

1. Dependencies (`pyproject.toml` + `uv.lock` refresh for pyarrow / duckdb).
2. Raw-layer rename + loader-path atomic migration (D-06 — single commit, CI must stay green).
3. Pydantic `schemas/cfd.py` + `schemes/__init__.py` Protocol.
4. `schemes/cfd/*.py` (cost_model + aggregation + forward_projection).
5. `schemes/cfd/__init__.py` wiring (§6.1 contract functions).
6. `publish/manifest.py` + `publish/csv_mirror.py` + `publish/snapshot.py`.
7. `refresh_all.py` orchestrator.
8. `tests/fixtures/constants.yaml` + `tests/fixtures/__init__.py` loader extension.
9. `tests/test_constants_provenance.py` + `tests/test_determinism.py`.
10. `tests/test_schemas.py` + `tests/test_aggregates.py` Parquet extensions.
11. `tests/fixtures/benchmarks.yaml` `lccc_self` activation.
12. `.github/workflows/refresh.yml` + `deploy.yml`.
13. `docs/data/index.md` + `mkdocs.yml` nav + `docs/index.md` link + `docs/about/citation.md`.
14. `CHANGES.md` `[Unreleased]` consolidation.

Planner may reorder; the discipline is one-concern-per-commit, CI green at every tip.

### Pydantic + pandera cohabitation

Two validation layers operate independently in this project:
- **Pydantic** validates configuration, fixtures, and wire-format (YAML in, JSON out).
- **pandera** validates DataFrames at load/derivation boundaries.

Pattern — `src/uk_subsidy_tracker/data/lccc.py` uses both: `LCCCAppConfig` (Pydantic) owns the YAML; `lccc_generation_schema` (pandera) owns the DataFrame. Do not try to unify them; Phase-4 derived tables follow the same split — Pydantic for `schemas/cfd.py` (the shape + `schema.json` emission) and pandera for the runtime DataFrame validation inside `schemes/cfd/*.py` writers.

---

## No Analog Found

Files with no close match in the codebase. Planner should use RESEARCH.md patterns (already detailed inline above) and the external-reference URLs in CONTEXT `### External references`.

| File | Role | Rationale for absence |
|---|---|---|
| `src/uk_subsidy_tracker/schemes/__init__.py` (Protocol) | Protocol declaration | No `typing.Protocol` usage exists yet in repo. Copy the shape in RESEARCH §Pattern 3 lines 629-654. |
| `data/raw/<publisher>/*.meta.json` sidecars (5 files) | JSON sidecars | No sidecar JSON exists anywhere in repo today. Shape defined by ARCHITECTURE §4.1 + RESEARCH §Pattern 6 lines 832-891. |

For both, the planner writes from spec — no pre-existing excerpt to copy.

---

## Metadata

**Analog search scope:** `src/uk_subsidy_tracker/` (20 files), `tests/` (7 files), `.github/workflows/` (1 file), `tests/fixtures/` (2 files), `.planning/phases/04-publishing-layer/` (2 files), `.planning/codebase/` (2 files), `docs/` structure listing only.

**Files scanned:** 34.

**Key pattern confirmations:**
- Package name is `uk_subsidy_tracker` (already renamed per Phase 0) — all new imports use this, not `cfd_payment`.
- `pandera.pandas as pa` is the canonical pandera import (not `pandera as pa`).
- `tests/fixtures/__init__.py` is the cleanest Pydantic + YAML + source-key-injection template and should be the anchor for `publish/manifest.py`, `schemas/cfd.py`, and the `load_constants()` extension.
- `tests/test_counterfactual.py` is the anchor for every new parametrised-pin test (remediation-hook failure message cites `METHODOLOGY_VERSION` + `CHANGES.md`).
- `.github/workflows/ci.yml` is the anchor for both `refresh.yml` and `deploy.yml` — reuse the `actions/checkout@v5` + `astral-sh/setup-uv@v8.1.0` + `uv sync --frozen` + `uv run --frozen …` cluster verbatim.

**Pattern extraction date:** 2026-04-22.

## PATTERN MAPPING COMPLETE
