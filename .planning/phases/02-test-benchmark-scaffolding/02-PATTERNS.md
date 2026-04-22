# Phase 2: Test & Benchmark Scaffolding - Pattern Map

**Mapped:** 2026-04-22
**Files analyzed:** 13 (7 to create, 6 to modify)
**Analogs found:** 13 / 13 (every new file has a close in-repo analog; no green-field patterns)

**Package path confirmed:** `src/uk_subsidy_tracker/` (verified on working tree — Phase 1 rename complete). All new code MUST import from `uk_subsidy_tracker.*` per 01-CONTEXT D-13/D-14/D-15. No `cfd_payment` imports permitted.

**Existing `.github/` directory:** **absent** (verified via `ls`). Phase 2 creates it. No prior GitHub Actions workflow exists in the repo to copy from — pattern is exogenous (Astral `setup-uv` README + RESEARCH.md §"Pattern 6").

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `tests/test_counterfactual.py` | test (formula pin) | request-response (pure function) | `tests/data/test_lccc.py` | role-match (both: flat function tests, package-root imports; data flow differs — pin vs CSV load) |
| `tests/test_schemas.py` | test (schema validation) | transform / read-only | `tests/data/test_lccc.py` + `tests/data/test_ons.py` | exact (loader-calls-then-asserts pattern identical) |
| `tests/test_aggregates.py` | test (invariant) | batch / groupby | `tests/data/test_lccc.py` (imports) + `src/uk_subsidy_tracker/plotting/**` for groupby idioms | role-match |
| `tests/test_benchmarks.py` | test (reconciliation) | batch / parametrised | `tests/data/test_lccc.py` + `src/uk_subsidy_tracker/data/lccc.py::load_lccc_config` (YAML+Pydantic) | role-match (composite) |
| `tests/fixtures/benchmarks.yaml` | fixture (data) | static config | `src/uk_subsidy_tracker/data/lccc_datasets.yaml` | exact (YAML-as-config-with-provenance) |
| `tests/fixtures/__init__.py` | fixture loader (Pydantic + YAML) | config load | `src/uk_subsidy_tracker/data/lccc.py::LCCCAppConfig` + `load_lccc_config` | exact |
| `.github/workflows/ci.yml` | CI workflow | event-driven (push/PR) | — (no prior workflow in repo) | **no analog** — use RESEARCH.md §"Pattern 6" + Astral `setup-uv` README verbatim |
| `src/uk_subsidy_tracker/counterfactual.py` (MODIFY) | source (add constant + column) | transform | existing file itself (module-level constants above `compute_counterfactual`) | self-analog (insert alongside `CCGT_EFFICIENCY` etc.) |
| `src/uk_subsidy_tracker/data/elexon.py` (OPTIONAL MODIFY — add schema) | source (pandera schema) | transform | `src/uk_subsidy_tracker/data/lccc.py` lines 36–69 | exact |
| `src/uk_subsidy_tracker/data/ons_gas.py` (OPTIONAL MODIFY — add schema) | source (pandera schema) | transform | `src/uk_subsidy_tracker/data/lccc.py` lines 36–69 | exact |
| `pyproject.toml` (VERIFY) | config | — | current contents | no change expected (pytest ≥9.0.3 already pinned, line 17) |
| `CHANGES.md` (MODIFY) | doc | — | current `## Methodology versions` stub (lines 55–63) + Keep-a-Changelog `[Unreleased]` block (line 8) | exact |
| `.planning/REQUIREMENTS.md` (MODIFY) | doc/traceability | — | current traceability table rows 168–173 | exact (row moves only) |
| `.planning/ROADMAP.md` (MODIFY) | doc/roadmap | — | current Phase 2 section lines 43–50 | exact (reword + list move only) |

## Pattern Assignments

### `tests/test_counterfactual.py` (test, formula pin)

**Analogs:**
- **Imports + flat-function style:** `tests/data/test_lccc.py` lines 1–9
- **Symbols under test:** `src/uk_subsidy_tracker/counterfactual.py` lines 12–83 (constants + `compute_counterfactual`)

**Imports pattern** — copy the shape of `tests/data/test_lccc.py` lines 1–9:
```python
"""Test LCCC dataset config and loading. Ensure datasets have been downloaded first."""

import pytest

from uk_subsidy_tracker.data.lccc import (
    download_lccc_datasets,
    load_lccc_config,
    load_lccc_dataset,
)
```
New file adapts this to:
```python
"""Pin the gas counterfactual formula against known inputs (TEST-01, GOV-04)."""

import pandas as pd
import pytest

from uk_subsidy_tracker.counterfactual import (
    METHODOLOGY_VERSION,
    compute_counterfactual,
)
```

**Formula under test** — `src/uk_subsidy_tracker/counterfactual.py` lines 72–83:
```python
df = gas_df.copy()
df["gas_fuel_cost"] = df["gas_p_per_kwh"] * 10.0 / ccgt_efficiency

co2_intensity = GAS_CO2_INTENSITY_THERMAL / ccgt_efficiency
df["carbon_price_per_t"] = df["date"].dt.year.map(carbon_prices).fillna(0.0)
df["carbon_cost"] = df["carbon_price_per_t"] * co2_intensity
df["plant_opex"] = non_fuel_opex_per_mwh
df["counterfactual_total"] = (
    df["gas_fuel_cost"] + df["carbon_cost"] + df["plant_opex"]
)
```
This is the formula the pin test freezes. Sample inputs computed against this exact code in RESEARCH.md lines 274–281:

| date | gas_p_per_kwh | expected `counterfactual_total` (£/MWh) |
|------|---------------|-----------------------------------------|
| 2019-01-01 | 1.5 | 39.6327 |
| 2019-06-01 | 1.2 | 34.1782 |
| 2022-10-01 | 8.0 | 168.1855 |
| 2019-01-01 | 0.0 | 12.3600 (zero-gas regression) |

**Test-body pattern** — RESEARCH.md lines 315–338 gives a complete `@pytest.mark.parametrize` skeleton; copy verbatim. Key idioms:
- Construct input via `pd.to_datetime([date_str])` per RESEARCH.md "Pitfall 2" guard (use `coerce=True` schemas elsewhere, but pin-test inputs go straight into `compute_counterfactual` which does not validate dtype).
- Float comparison via `round(actual, 4) == expected` — NOT `==` on raw floats (RESEARCH.md "Anti-Patterns" §5).
- Failure message names `METHODOLOGY_VERSION` + `CHANGES.md` explicitly so the fix path is obvious.

**Idioms to replicate from `tests/data/test_lccc.py`:**
- Flat `def test_*` functions; no classes, no shared `conftest.py` fixtures (except optional module-scope per RESEARCH.md §"Pattern 4" style).
- Module-level docstring in triple-quotes first line (see line 1 of the analog).
- No shared fixtures between test files unless inside the same file (`@pytest.fixture(scope="module")` is fine — see Pattern 4 skeleton in RESEARCH.md lines 435–439).

---

### `tests/test_schemas.py` (test, schema validation — pre-Parquet scaffolding)

**Analog:** `tests/data/test_lccc.py` lines 26–29 + `tests/data/test_ons.py` lines 13–16.

**Loader-then-assert pattern** — verbatim from `tests/data/test_lccc.py:26–29`:
```python
def test_load_dataset():
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    assert not df.empty
    assert "Settlement_Date" in df.columns
```
And from `tests/data/test_ons.py:13–16`:
```python
def test_load_dataset():
    df = load_gas_price()
    assert not df.empty
    assert "date" in df.columns
```

**Key insight — `load_lccc_dataset` already runs `schema.validate()` internally** (see `src/uk_subsidy_tracker/data/lccc.py` lines 105–114):
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
So `test_schemas.py` can simply call the loader and assert shape/columns — if validation fails, the loader raises `SchemaError` and the test fails automatically. **No need to import pandera in the test file for LCCC cases.**

**Elexon / ONS gas — no schema exists yet.** The optional modification adds sibling `pa.DataFrameSchema` objects in `src/uk_subsidy_tracker/data/elexon.py` and `src/uk_subsidy_tracker/data/ons_gas.py`, following `src/uk_subsidy_tracker/data/lccc.py` lines 36–54 verbatim:
```python
lccc_generation_schema = pa.DataFrameSchema(
    {
        "Settlement_Date": pa.Column("datetime64[ns]"),
        "CfD_ID": pa.Column(str),
        "Name_of_CfD_Unit": pa.Column(str),
        "Technology": pa.Column(str),
        "Allocation_round": pa.Column(str),
        "Reference_Type": pa.Column(str),
        "CFD_Generation_MWh": pa.Column(float, nullable=True),
        "Avoided_GHG_tonnes_CO2e": pa.Column(float, nullable=True),
        "Strike_Price_GBP_Per_MWh": pa.Column(float, nullable=True),
        "CFD_Payments_GBP": pa.Column(float),
        "Avoided_GHG_Cost_GBP": pa.Column(float, nullable=True),
        "Market_Reference_Price_GBP_Per_MWh": pa.Column(float, nullable=True),
        "Weighted_IMRP_GBP_Per_MWh": pa.Column(float, nullable=True),
    },
    strict=False,
    coerce=True,
)
```
Key idioms:
- `import pandera.pandas as pa` (see `src/uk_subsidy_tracker/data/lccc.py:6`) — NEVER `import pandera as pa` per RESEARCH.md Anti-Patterns §1.
- `strict=False` (allow upstream extra columns) + `coerce=True` (dtype alignment, covers the pandas 3.0 `datetime64[us]` vs `datetime64[ns]` trap per RESEARCH.md "Pitfall 2").
- Nullable floats use `nullable=True` — apply to every metric column; LCCC publishes negative/null values legitimately (RESEARCH.md "Pitfall 8").

**Pandera suggested shapes** (from RESEARCH.md §"Pattern 3" lines 350–377):
```python
elexon_agws_schema = pa.DataFrameSchema(
    {
        "settlementDate": pa.Column("datetime64[ns]", coerce=True),
        "settlementPeriod": pa.Column(int, coerce=True),
        "businessType": pa.Column(str),
        "quantity": pa.Column(float, nullable=True, coerce=True),
    },
    strict=False,
    coerce=True,
)

elexon_system_price_schema = pa.DataFrameSchema(
    {
        "settlementDate": pa.Column("datetime64[ns]", coerce=True),
        "settlementPeriod": pa.Column(int, coerce=True),
        "systemSellPrice": pa.Column(float, nullable=True, coerce=True),
        "systemBuyPrice": pa.Column(float, nullable=True, coerce=True),
    },
    strict=False,
    coerce=True,
)
```

For ONS: the output of `load_gas_price()` is already a constructed 2-column frame (see `src/uk_subsidy_tracker/data/ons_gas.py:35–52`) — schema should be:
```python
ons_gas_schema = pa.DataFrameSchema(
    {
        "date": pa.Column("datetime64[ns]", coerce=True),
        "gas_p_per_kwh": pa.Column(float, coerce=True),
    },
    strict=False,
    coerce=True,
)
```

---

### `tests/test_aggregates.py` (test, row-conservation invariant)

**Analog:** `tests/data/test_lccc.py` (imports + flat style). Groupby idiom already used widely in `src/uk_subsidy_tracker/plotting/**` (see CLAUDE.md "Data Processing Patterns" — `df.groupby([...]).agg({...}).reset_index()`).

**Test-body pattern** — RESEARCH.md lines 430–460, ready to copy:
```python
import pytest

from uk_subsidy_tracker.data import load_lccc_dataset


@pytest.fixture(scope="module")
def lccc_gen():
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df["year"] = df["Settlement_Date"].dt.year
    return df


def test_year_vs_year_tech_sum_match(lccc_gen):
    """TEST-03 scaffolding: no row leakage from tech decomposition."""
    by_year = lccc_gen.groupby("year")["CFD_Payments_GBP"].sum()
    by_year_tech = (
        lccc_gen.groupby(["year", "Technology"])["CFD_Payments_GBP"]
        .sum()
        .groupby("year")
        .sum()
    )
    pd.testing.assert_series_equal(
        by_year.sort_index(),
        by_year_tech.sort_index(),
        check_names=False,
    )


def test_no_orphan_technologies(lccc_gen):
    """Every row has a non-null Technology (else groupby drops it)."""
    assert lccc_gen["Technology"].notna().all()
```

**Idioms to replicate:**
- Import from `uk_subsidy_tracker.data` (the barrel re-export), not the submodule — see `src/uk_subsidy_tracker/data/__init__.py`:
  ```python
  from .elexon import load_elexon_prices_daily, load_elexon_wind_daily
  from .lccc import download_lccc_datasets, load_lccc_dataset
  from .ons_gas import load_gas_price
  ```
  Tests use `from uk_subsidy_tracker.data import load_lccc_dataset` per CONTEXT D-13 and the research "Integration Points" note.
- `@pytest.fixture(scope="module")` is the first shared-fixture usage in the repo; acceptable (RESEARCH.md confirms and `tests/data/*` has no `conftest.py` today). Do not introduce `tests/conftest.py` unless `tests/test_benchmarks.py` also needs the same fixture — then hoist. Planner decides.
- Do **not** assert `>= 0` on `CFD_Generation_MWh` or `CFD_Payments_GBP` — LCCC publishes legitimate negatives (RESEARCH.md "Pitfall 7" + "Pitfall 8"). The 2022 row-sum is `-0.346 bn` and is correct.

---

### `tests/test_benchmarks.py` (test, reconciliation — LCCC floor + external anchors)

**Analogs (composite):**
- Fixture loader: `src/uk_subsidy_tracker/data/lccc.py::load_lccc_config` (lines 77–82) — YAML + Pydantic idiom.
- Parametrised tests: standard pytest — no in-repo prior; RESEARCH.md §"Pattern 5" (lines 465–619) provides the canonical skeleton.

**Tolerance constants** — per CONTEXT D-06. Named constants with docstring rationale, NOT inline magic numbers:
```python
LCCC_SELF_TOLERANCE_PCT = 0.1
"""Red line per CONTEXT D-10. We read LCCC raw data. A divergence here is a pipeline bug."""

OBR_EFO_TOLERANCE_PCT = 5.0
"""OBR reports financial-year figures; we report calendar-year. April-March vs Jan-Dec adds
quarterly-roll-over skew. Carbon-price CPI basis may also differ."""
```

**LCCC self-reconciliation floor (red-line check, mandatory per CONTEXT D-10):**
```python
def test_lccc_self_reconciliation_floor(annual_totals_gbp_bn):
    """CONTEXT D-10 red line: LCCC self-reconciliation MUST hold within 0.1%."""
    benchmarks = load_benchmarks()
    assert benchmarks.lccc_self, "LCCC self-reconciliation floor is mandatory (D-10)"
    for entry in benchmarks.lccc_self:
        ours = annual_totals_gbp_bn.get(entry.year)
        assert ours is not None, f"No pipeline data for year {entry.year}"
        divergence = abs(ours - entry.value_gbp_bn) / entry.value_gbp_bn
        assert divergence <= LCCC_SELF_TOLERANCE_PCT / 100, (...)
```

**Fallback posture (CONTEXT D-11):** if external anchors unavailable at execution time, ship with LCCC floor only. Keep the parametrised `test_external_benchmark_within_tolerance` present but it simply iterates zero entries — not a failure.

**Idioms to replicate:**
- Module-scoped fixture computing pipeline totals once: `@pytest.fixture(scope="module")` pattern from the aggregates test.
- Tolerance violations produce failure messages citing the three options (fix pipeline / document divergence in CHANGES.md / bump tolerance with rationale) — matches CONTEXT D-06/D-07.

---

### `tests/fixtures/benchmarks.yaml` (fixture data, structured provenance)

**Analog:** `src/uk_subsidy_tracker/data/lccc_datasets.yaml` (verbatim, lines 1–13):
```yaml
datasets:
  - name: "Actual CfD Generation and avoided GHG emissions"
    uuid: "37d1bef4-55d7-4b8e-8a47-1d24b123a20e"
    filename: "lccc-actual-cfd-generation.csv"
    description: "This dataset includes the historic actual CfD generation (from 2016) eligible for CfD payments"
    url: "https://dp.lowcarboncontracts.uk/dataset/actual-cfd-generation-and-avoided-ghg-emissions"
```

**Apply pattern:** top-level keys per *source*, each a YAML list of entries. Shape per entry from CONTEXT D-05 + RESEARCH.md lines 468–498:
```yaml
lccc_self:
  - year: 2024
    value_gbp_bn: 2.40
    url: "https://www.lowcarboncontracts.uk/documents/293/LCCC_ARA_24-25_11.pdf"
    retrieved_on: "2026-04-22"
    notes: "LCCC Annual Report & Accounts 2024/25, calendar-year 2024 aggregate."
    tolerance_pct: 0.1

obr_efo:
  - year: 2024
    value_gbp_bn: 2.3
    url: "https://obr.uk/efo/economic-and-fiscal-outlook-november-2025/"
    retrieved_on: "2026-04-22"
    notes: "OBR EFO 2024/25 CfD = £2.3bn (financial year)."
    tolerance_pct: 5.0
```

**Idioms to replicate from `lccc_datasets.yaml`:**
- Double-quoted strings for URLs + any value with `:` or `/`.
- Blank line separates logical groups (within one source, between years).
- `retrieved_on` in ISO-8601 `YYYY-MM-DD` so Pydantic auto-coerces to `datetime.date` (RESEARCH.md "Don't Hand-Roll" row 7).
- `notes` states "calendar year" vs "financial year" explicitly (RESEARCH.md "Pitfall 6").
- Commentator references (Ben Pile / Turver) — NOT in Phase 2 per CONTEXT D-08. If ever added later, under a separate `commentators:` key with a `non_canonical: true` flag per CONTEXT deferred idea.

---

### `tests/fixtures/__init__.py` (Pydantic + YAML loader)

**Analog:** `src/uk_subsidy_tracker/data/lccc.py` lines 16–32 + 77–82 (Pydantic models + `yaml.safe_load` loader).

**Pydantic-model pattern** — verbatim from `src/uk_subsidy_tracker/data/lccc.py:16–32`:
```python
# Schema for a single dataset entry
class LCCCDatasetConfig(BaseModel):
    name: str
    uuid: str
    filename: str
    description: str
    url: str


# Schema for the datasets
class LCCCAppConfig(BaseModel):
    datasets: list[LCCCDatasetConfig]

    def dataset(self, name: str) -> LCCCDatasetConfig:
        for d in self.datasets:
            if d.name == name:
                return d
        raise KeyError(name)
```

**Loader pattern** — verbatim from `src/uk_subsidy_tracker/data/lccc.py:77–82`:
```python
def load_lccc_config(config_path: str = "lccc_datasets.yaml") -> LCCCAppConfig:
    """Load the dataset configurations from a YAML file."""
    default_dir = Path(__file__).parent
    with open(default_dir / config_path, "r") as f:
        raw_config = yaml.safe_load(f)
        return LCCCAppConfig(**raw_config)
```

**Apply pattern to benchmarks** — RESEARCH.md §"Pattern 5" (lines 501–543) gives the exact model + loader. Key adaptations:
- Two model layers (`BenchmarkEntry`, `Benchmarks`) mirroring the two-layer LCCC shape (`LCCCDatasetConfig`, `LCCCAppConfig`).
- `Benchmarks` exposes a helper method (`all_entries()`) — mirrors `LCCCAppConfig.dataset(name)` helper pattern.
- Loader signature identical in spirit: resolves path via `Path(__file__).parent / "benchmarks.yaml"`.
- Return type is the Pydantic model, not a dict — consistent with `load_lccc_config() -> LCCCAppConfig`.

**Idioms to replicate:**
- Pydantic v2 syntax: `from pydantic import BaseModel, Field, HttpUrl` (project pins `pydantic>=2.13.1` in `pyproject.toml:15`).
- `HttpUrl` for `url` field (auto-validates); `date` type for `retrieved_on` (yaml.safe_load returns `datetime.date` natively for ISO strings — RESEARCH.md "Don't Hand-Roll" row 7).
- `Field(..., ge=2015, le=2050)` for year bounds, `Field(..., gt=0)` for tolerance — consistent with Pydantic v2 style used in `LCCCDatasetConfig` (plain `str` today, but validators are idiomatic where applicable).

**Pytest-discovery guard (RESEARCH.md "Pitfall 3"):** the loader lives in `__init__.py`, not `test_*.py`. Do NOT add a `test_*.py` file inside `tests/fixtures/`. Benchmark-loader self-tests (if ever added) go in `tests/test_fixtures.py` at the top level.

---

### `.github/workflows/ci.yml` (CI workflow) — **NO IN-REPO ANALOG**

**Why no analog:** `.github/` directory does not exist in the repo (verified). Phase 2 introduces GitHub Actions wholesale.

**Exogenous pattern source:** Astral `setup-uv` README v8 example + `docs.astral.sh/uv/guides/integration/github/`. RESEARCH.md §"Pattern 6" (lines 622–666) gives the verbatim skeleton that matches the project constraints (Python 3.12 floor, uv.lock reproducibility, no deploys):

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
        uses: astral-sh/setup-uv@v8
        with:
          enable-cache: true
          python-version: "3.12"

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run tests
        run: uv run --frozen pytest -v
```

**Pin discipline (CONTEXT + RESEARCH divergence):** CONTEXT suggests `setup-uv@v4`; RESEARCH recommends `@v8` (current stable, April 2026, includes default `cache-dependency-glob` matching `uv.lock` + `pyproject.toml`). Planner picks one; RESEARCH argues for `@v8`.

**Key idioms:**
- `uv sync --frozen` (not `--locked`) per RESEARCH.md "Alternatives Considered" row 1 — mirrors setup-uv README example; stricter lockfile guard.
- No `ruff`/`pyright`/`mkdocs build --strict` steps in Phase 2 — deferred to Phase 3+ per CONTEXT "Claude's Discretion" and "Deferred Ideas."
- No matrix (single Python 3.12) — matches `pyproject.toml:5` floor.
- No secrets needed (no deploys, no external APIs exercised by tests).

---

### `src/uk_subsidy_tracker/counterfactual.py` (MODIFY — add METHODOLOGY_VERSION + DataFrame column)

**Self-analog:** the existing module itself. Insertion points are literal and unambiguous.

**Constant insertion site** — after line 13, before line 15 (or next to the other top-level constants `CCGT_EFFICIENCY`, `GAS_CO2_INTENSITY_THERMAL`, `DEFAULT_NON_FUEL_OPEX`):
```python
CCGT_EFFICIENCY = 0.55
GAS_CO2_INTENSITY_THERMAL = 0.184  # tCO2 per MWh thermal (natural gas)
```
Insert (per RESEARCH.md §"Pattern 1" lines 250–258 + §"Code Examples" lines 763–775):
```python
METHODOLOGY_VERSION: str = "1.0.0"
"""Semantic version for the gas counterfactual formula.

Bumps require an entry in CHANGES.md under ## Methodology versions.

- PATCH: Constant tweak with identical formula shape.
- MINOR: Additive parameter (new kwarg with default preserving old calls).
- MAJOR: Formula-shape change (new/dropped term, changed unit).
"""
```

**DataFrame-column insertion site** — inside `compute_counterfactual`, immediately before the `return df` on line 83:
```python
df["counterfactual_total"] = (
    df["gas_fuel_cost"] + df["carbon_cost"] + df["plant_opex"]
)

return df
```
Becomes:
```python
df["counterfactual_total"] = (
    df["gas_fuel_cost"] + df["carbon_cost"] + df["plant_opex"]
)
df["methodology_version"] = METHODOLOGY_VERSION

return df
```

**Idioms to replicate:**
- Type annotation `METHODOLOGY_VERSION: str = "1.0.0"` — matches the "Type hints fully present" convention from CLAUDE.md.
- Triple-quoted docstring after the assignment — matches the in-file style of the `DEFAULT_NON_FUEL_OPEX` comment block (lines 15–22 of the existing file).
- Column name `methodology_version` (snake_case, DataFrame convention — CLAUDE.md "Naming Patterns").

**Downstream effect:** the new column flows through `compute_counterfactual_monthly` (line 86–93) automatically because `resample("ME").mean(numeric_only=True)` drops it (string column, non-numeric). That is acceptable — the daily version is the canonical input for Phase-4 Parquet (per CONTEXT "Specific Ideas" note on manifest.json flow). If the planner wants the monthly version to also carry it, re-add after the resample, explicitly.

---

### `pyproject.toml` (VERIFY — no change expected)

**Analog:** itself. Current state (`pyproject.toml:17`):
```toml
    "pytest>=9.0.3",
```
already satisfies the RESEARCH.md standard-stack claim. **No modification expected** per CONTEXT "Claude's Discretion" penultimate bullet and RESEARCH.md Anti-Patterns §7. Planner should include a verification step (read the line, confirm `>=9.0.3`), not an edit step.

Note `pandera>=0.31.1` (line 13), `pydantic>=2.13.1` (line 15), `pyyaml>=6.0.3` (line 18) are all already pinned — Phase 2 adds no new deps.

---

### `CHANGES.md` (MODIFY — fill `## Methodology versions` + append `[Unreleased]` entries)

**Analog:** itself. Two insertion regions.

**Region 1 — `[Unreleased]` block, currently empty at line 8.** Apply Keep-a-Changelog 1.1.0 (per header lines 4–6 + CONTEXT inheritance from Phase 1 D-16). RESEARCH.md §"Code Examples" lines 780–799 gives the complete draft:
```markdown
## [Unreleased]

### Added
- `.github/workflows/ci.yml` — GitHub Actions CI runs `uv run --frozen pytest`
  on push to `main` and on every pull request (TEST-06).
- `tests/test_counterfactual.py` — pins the gas counterfactual formula against
  known inputs to 4 decimal places (TEST-01). Asserts `METHODOLOGY_VERSION`
  presence + DataFrame propagation.
- `tests/test_schemas.py` — pandera validation of raw CSV sources
  (pre-Parquet scaffolding; formal TEST-02 in Phase 4).
- `tests/test_aggregates.py` — row-conservation assertions on the CfD pipeline
  (pre-Parquet scaffolding; formal TEST-03 in Phase 4).
- `tests/test_benchmarks.py` — LCCC self-reconciliation floor + regulator-native
  anchors (TEST-04).
- `tests/fixtures/benchmarks.yaml` — structured benchmark values with per-entry
  source, year, URL, retrieval date, notes, and tolerance.
- `tests/fixtures/__init__.py` — Pydantic loader for `benchmarks.yaml`.
- `METHODOLOGY_VERSION` constant in `src/uk_subsidy_tracker/counterfactual.py`
  (GOV-04); `compute_counterfactual()` returns it as a DataFrame column.
```

**Region 2 — `## Methodology versions` section, currently at line 55 with HTML-comment placeholder (lines 57–62).** Append the first versioned entry beneath the comment:
```markdown
## Methodology versions

<!--
GOV-04 hook: ... (existing placeholder comment retained) ...
-->

### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)

- Formula: `counterfactual_total = gas_fuel_cost + carbon_cost + plant_opex` (all £/MWh).
- Constants pinned: `CCGT_EFFICIENCY = 0.55`; `GAS_CO2_INTENSITY_THERMAL = 0.184`
  tCO2/MWh_thermal; `DEFAULT_NON_FUEL_OPEX = 5.0` £/MWh; annual
  `DEFAULT_CARBON_PRICES` 2018–2026 (EU ETS 2018–2020, UK ETS 2021+).
- Sources: BEIS Electricity Generation Costs 2023 Table ES.1; GOV.UK UK ETS
  published prices.
- Pinned in `tests/test_counterfactual.py` at 4 decimal places; any change to
  these constants fails the pin test and requires a CHANGES.md entry here.
```

**Idioms to replicate from existing `CHANGES.md`:**
- Section-header style `### X.Y.Z — YYYY-MM-DD — Short descriptor` consistent with the `## [0.1.0] — 2026-04-21` header on line 10.
- Em-dash (`—`, U+2014) separators (line 10 uses this), not hyphen.
- Bulleted sub-list beneath the header; each bullet a short clause with concrete constants/sources.
- Keep the existing `<!-- GOV-04 hook: ... -->` HTML comment — do not delete. The 1.0.0 entry slots below it.

---

### `.planning/REQUIREMENTS.md` (MODIFY — traceability row moves)

**Analog:** itself (lines 168–173). Current rows:
```
| TEST-02 | Phase 2 | Pending |
| TEST-03 | Phase 2 | Pending |
| TEST-04 | Phase 2 | Pending |
| TEST-05 | Phase 2 | Pending |
| TEST-06 | Phase 2 | Pending |
| GOV-04 | Phase 2 | Pending |
```

**Apply per CONTEXT D-04:**
- TEST-02 → change `Phase 2` to `Phase 4`.
- TEST-03 → change `Phase 2` to `Phase 4`.
- TEST-05 → change `Phase 2` to `Phase 4`.
- TEST-04, TEST-06, GOV-04 → remain `Phase 2` (Phase 2 moves them from `Pending` to a closed status on phase-exit, but that is a separate Phase-2-closing concern, not the body of this phase).

---

### `.planning/ROADMAP.md` (MODIFY — Phase 2 reword, req-list rebalance)

**Analog:** itself. Current state worth quoting:

Line 11 — Phase 2 summary bullet (top of file):
```
- [ ] **Phase 2: Test & Benchmark Scaffolding** — Five test classes, CI green on main; counterfactual formula pinned
```
→ reword to "Four test classes" per D-04 reword of success criterion 1.

Line 46 — Phase 2 requirements list:
```
**Requirements**: TEST-01, TEST-02, TEST-03, TEST-04, TEST-05, TEST-06, GOV-04
```
→ drop TEST-02, TEST-03, TEST-05 per D-04. New: `TEST-01, TEST-04, TEST-06, GOV-04`.

Line 48 — success criterion 1:
```
  1. `uv run pytest` passes green on `main` — all five test classes present and passing
```
→ reword per D-04 to: "four test classes present and passing: `test_counterfactual.py`, `test_schemas.py`, `test_aggregates.py`, `test_benchmarks.py`".

Line 50 — success criterion 3:
```
  3. `tests/test_benchmarks.py` documents divergence from Ben Pile (2021 + 2026), REF subset, and Turver aggregate explicitly in output or docstring
```
→ re-anchor per D-11 to: "documents divergence from LCCC self-reconciliation and any regulator-native external sources the researcher located."

Phase 4 section (line 68 onwards — read in the file to confirm exact line numbers before editing): add TEST-02, TEST-03, TEST-05 to the Phase 4 **Requirements** list per D-04.

**Idiom to preserve:** markdown checkbox + bold-title pattern `- [ ] **Phase N: ...**` (line 11, 13, 14 etc.).

---

## Shared Patterns

### Pattern A: `import pandera.pandas as pa` (canonical form)
**Source:** `src/uk_subsidy_tracker/data/lccc.py:6`
**Apply to:** `test_schemas.py` (if importing the schema symbols directly) and any new sibling schemas in `elexon.py`, `ons_gas.py`.
```python
import pandera.pandas as pa
```
**Anti-pattern:** `import pandera as pa` (deprecated since 0.24; emits `FutureWarning`). Verified in current code.

### Pattern B: `uk_subsidy_tracker.*` absolute imports (never `cfd_payment.*`, never relative)
**Source:** `tests/data/test_lccc.py:5–9` + `tests/data/test_ons.py:5` + `src/uk_subsidy_tracker/data/lccc.py:11–12`
**Apply to:** every new test file + the fixtures loader.
```python
from uk_subsidy_tracker.data import load_lccc_dataset
from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION, compute_counterfactual
```
Per CONTEXT D-13/D-14/D-15 (Phase 1). The working tree has no `cfd_payment` symbols left; any such import would fail at collection.

### Pattern C: Barrel re-exports from `uk_subsidy_tracker.data`
**Source:** `src/uk_subsidy_tracker/data/__init__.py:1–3`
**Apply to:** test imports — prefer `from uk_subsidy_tracker.data import load_lccc_dataset` over `from uk_subsidy_tracker.data.lccc import load_lccc_dataset`. The existing `tests/data/test_lccc.py` uses the deep import because it also imports `load_lccc_config` + `download_lccc_datasets` (not re-exported). New Phase-2 tests that only need the public loaders should use the barrel.

### Pattern D: Pydantic `BaseModel` + `yaml.safe_load` (config-with-provenance)
**Source:** `src/uk_subsidy_tracker/data/lccc.py:9, 16–32, 77–82`
**Apply to:** `tests/fixtures/__init__.py` for `benchmarks.yaml` loading.
Two-layer model (entry + collection), path resolved via `Path(__file__).parent`, `yaml.safe_load` + `Model(**raw)` — mirrors the LCCC pattern 1:1.

### Pattern E: `@pytest.mark.skip(reason="...")` for network / environment-dependent tests
**Source:** `tests/data/test_lccc.py:12` + `tests/data/test_ons.py:8`
```python
@pytest.mark.skip(reason="hits live website")
def test_download_lccc_datasets(): ...
```
**Apply to:** any Phase-2 test that would hit a live service. **Do NOT apply to Phase-4-deferred tests** — those are not authored in Phase 2 at all (CONTEXT "Established Patterns" bullet 3). The Phase-2 test suite hits no network: CSVs + XLSX are on disk (verified `data/` listing: `elexon_agws.csv`, `elexon_system_prices.csv`, `lccc-actual-cfd-generation.csv`, `lccc-cfd-contract-portfolio-status.csv`, `ons_gas_sap.xlsx`).

### Pattern F: Flat test functions, no classes, module-level docstring
**Source:** `tests/data/test_lccc.py` (entire file — 30 lines, 3 functions, 1 module docstring)
**Apply to:** every new `test_*.py` file in Phase 2. Project convention per CLAUDE.md "Naming Patterns" and CONTEXT "Established Patterns."

### Pattern G: CSV loader = "read + validate" single-call contract
**Source:** `src/uk_subsidy_tracker/data/lccc.py:105–114`
**Apply to:** `test_schemas.py` reliance on loaders to run validation internally; no need to duplicate `schema.validate()` in the test. Same contract should govern any Elexon/ONS loader updated to call a new schema — the test asserts shape on the loader output, the loader raises `SchemaError` on invalid data.

### Pattern H: Atomic commits (one file/concern per commit)
**Source:** Phase 1 D-16 (carried via 01-CONTEXT.md) + git log showing one-concern-per-commit pattern on recent Phase-1 close-out.
**Apply to:** planner should sequence commits: (1) METHODOLOGY_VERSION + CHANGES.md 1.0.0 entry; (2) test_counterfactual.py; (3) Elexon/ONS schemas (if added); (4) test_schemas.py; (5) test_aggregates.py; (6) benchmarks.yaml + fixtures/__init__.py; (7) test_benchmarks.py; (8) ci.yml; (9) REQUIREMENTS.md + ROADMAP.md traceability updates; (10) CHANGES.md [Unreleased] omnibus update. Planner may merge adjacent small commits (e.g., fixture data + loader) but should not bundle a test file with a source-code modification.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `.github/workflows/ci.yml` | CI workflow | event-driven | No prior `.github/` directory in the repo. Pattern sourced from RESEARCH.md §"Pattern 6" (Astral `setup-uv` README + `docs.astral.sh/uv/guides/integration/github/`), not from an in-repo analog. |

This is the only new file without an in-repo pattern. Every other file in the phase maps to an existing analog.

## Metadata

**Analog search scope:**
- `src/uk_subsidy_tracker/` (full tree: `__init__.py`, `counterfactual.py`, `data/`, `plotting/`)
- `tests/` (full tree: `tests/data/test_lccc.py`, `tests/data/test_ons.py`)
- `pyproject.toml`, `CHANGES.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` for modification sites
- `.github/` — confirmed absent via `ls`

**Files scanned:** 15 (6 src modules, 2 existing tests, 2 YAML configs, 1 pyproject, 1 CHANGES, 2 planning docs, 1 package `__init__`)

**Pattern extraction date:** 2026-04-22

**Package path note:** All references to `src/cfd_payment/*` in the upstream CONTEXT.md / pattern-mapping brief are stale. The working tree has completed the Phase-1 rename; only `src/uk_subsidy_tracker/*` paths are valid. New code and tests MUST import `uk_subsidy_tracker.*`. This has been verified via `ls src/` returning `uk_subsidy_tracker` (no `cfd_payment`).
