---
phase: 04-publishing-layer
plan: 03
type: execute
wave: 3
depends_on:
  - 01
  - 02
files_modified:
  - src/uk_subsidy_tracker/schemas/__init__.py
  - src/uk_subsidy_tracker/schemas/cfd.py
  - src/uk_subsidy_tracker/schemes/__init__.py
  - src/uk_subsidy_tracker/schemes/cfd/__init__.py
  - src/uk_subsidy_tracker/schemes/cfd/cost_model.py
  - src/uk_subsidy_tracker/schemes/cfd/aggregation.py
  - src/uk_subsidy_tracker/schemes/cfd/forward_projection.py
  - src/uk_subsidy_tracker/schemes/cfd/_refresh.py
  - tests/test_schemas.py                      # extend with Parquet variants
  - tests/test_aggregates.py                   # extend with Parquet variants
  - tests/test_determinism.py                  # new
  - .gitignore                                 # add data/derived/
  - CHANGES.md
autonomous: true
requirements:
  - PUB-05
  - TEST-02
  - TEST-03
  - TEST-05
  - GOV-02    # methodology_version column on derived Parquet — provenance-per-row
tags: [derived-layer, parquet, scheme-contract, schemas, tdd]
user_setup: []

must_haves:
  truths:
    - "cfd.rebuild_derived() produces five Parquet files under data/derived/cfd/ (or an explicit output_dir)"
    - "Every derived Parquet file has a methodology_version column set from counterfactual.METHODOLOGY_VERSION"
    - "Two rebuilds from the same raw state produce content-identical Parquet (pyarrow.Table.equals)"
    - "Row-conservation invariant holds across station_month → annual_summary → by_technology"
    - "Every derived Parquet loads back and validates against its Pydantic schema via pandera"
    - "Chart generation continues to work (D-02: charts untouched in this plan)"
  artifacts:
    - path: "src/uk_subsidy_tracker/schemas/__init__.py"
      provides: "Barrel re-exporting StationMonthRow + AnnualSummaryRow + ByTechnologyRow + ByAllocationRoundRow + ForwardProjectionRow"
    - path: "src/uk_subsidy_tracker/schemas/cfd.py"
      provides: "Five Pydantic table-row models with json_schema_extra={dtype, unit} per field; field-declaration order = column order (D-10)"
      contains: "class StationMonthRow"
      min_lines: 80
    - path: "src/uk_subsidy_tracker/schemes/__init__.py"
      provides: "typing.Protocol SchemeModule with DERIVED_DIR + five §6.1 contract callables"
      contains: "SchemeModule"
    - path: "src/uk_subsidy_tracker/schemes/cfd/__init__.py"
      provides: "DERIVED_DIR + five contract functions (upstream_changed, refresh, rebuild_derived, regenerate_charts, validate)"
      contains: "def rebuild_derived"
      min_lines: 50
    - path: "src/uk_subsidy_tracker/schemes/cfd/cost_model.py"
      provides: "build_station_month(output_dir) — derives station × month grain from data/raw/lccc/ + counterfactual"
      contains: "def build_station_month"
      min_lines: 60
    - path: "src/uk_subsidy_tracker/schemes/cfd/aggregation.py"
      provides: "build_annual_summary + build_by_technology + build_by_allocation_round — rollups of station_month.parquet"
      contains: "def build_annual_summary"
      min_lines: 80
    - path: "src/uk_subsidy_tracker/schemes/cfd/forward_projection.py"
      provides: "build_forward_projection — hoist of remaining_obligations logic"
      contains: "def build_forward_projection"
      min_lines: 50
    - path: "tests/test_determinism.py"
      provides: "Parametrised content-equality test across all five grains using pyarrow.Table.equals()"
      contains: "pq.read_table"
      min_lines: 40
    - path: "tests/test_schemas.py"
      provides: "Raw CSV tests + Parquet variants (D-19) — each derived grain validates on read-back"
      contains: "parquet"
    - path: "tests/test_aggregates.py"
      provides: "Raw scaffolding + Parquet row-conservation (D-20) across grains"
      contains: "parquet"
    - path: ".gitignore"
      provides: "data/derived/ ignored (regenerated, not committed)"
      contains: "data/derived"
  key_links:
    - from: "src/uk_subsidy_tracker/schemes/cfd/__init__.py"
      to: "src/uk_subsidy_tracker/schemes/cfd/cost_model.py"
      via: "from .cost_model import build_station_month"
      pattern: "from .cost_model"
    - from: "src/uk_subsidy_tracker/schemes/cfd/cost_model.py"
      to: "data/raw/lccc/actual-cfd-generation.csv"
      via: "load_lccc_dataset(\"Actual CfD Generation and avoided GHG emissions\") (reads via post-Plan-02 path)"
      pattern: "load_lccc_dataset"
    - from: "src/uk_subsidy_tracker/schemes/cfd/cost_model.py"
      to: "src/uk_subsidy_tracker/counterfactual.py::METHODOLOGY_VERSION"
      via: "df['methodology_version'] = METHODOLOGY_VERSION"
      pattern: "METHODOLOGY_VERSION"
    - from: "tests/test_determinism.py"
      to: "src/uk_subsidy_tracker/schemes/cfd/__init__.py::rebuild_derived"
      via: "cfd.rebuild_derived(output_dir=tmp_path)"
      pattern: "rebuild_derived"
    - from: "tests/test_schemas.py"
      to: "src/uk_subsidy_tracker/schemas/cfd.py"
      via: "StationMonthRow.model_validate(...) on each Parquet row"
      pattern: "StationMonthRow"
---

<objective>
Build the CfD scheme module and the derived Parquet layer. This plan is the
Phase 5 (RO) + Phase 7+ template — every future scheme module copies this
structure verbatim, so the contract MUST be real (D-01 "load-bearing, not
stubbed"). Ship pyarrow-pinned deterministic Parquet writers, the five derived
grains, three test axes (schema / row-conservation / determinism), and a
Protocol declaring the §6.1 contract.

Purpose: formally satisfy TEST-02, TEST-03, TEST-05 on Parquet output (not
just raw-CSV scaffolding); deliver PUB-05 end-to-end pipeline; propagate
`METHODOLOGY_VERSION` into every derived row (GOV-02 provenance-per-row).

Output: `src/uk_subsidy_tracker/{schemas,schemes}/` packages with five Parquet
grains emitted by `cfd.rebuild_derived()`; Parquet-variant tests alongside
the Phase-2 raw-CSV scaffolding in `tests/test_schemas.py` + `tests/test_aggregates.py`;
new `tests/test_determinism.py` turning green on content equality.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/04-publishing-layer/04-CONTEXT.md
@.planning/phases/04-publishing-layer/04-RESEARCH.md
@.planning/phases/04-publishing-layer/04-PATTERNS.md
@.planning/phases/04-publishing-layer/04-VALIDATION.md
@.planning/phases/04-02-SUMMARY.md
@ARCHITECTURE.md
@src/uk_subsidy_tracker/counterfactual.py
@src/uk_subsidy_tracker/data/lccc.py
@src/uk_subsidy_tracker/plotting/subsidy/cfd_dynamics.py
@src/uk_subsidy_tracker/plotting/subsidy/cfd_payments_by_category.py
@src/uk_subsidy_tracker/plotting/subsidy/subsidy_per_avoided_co2_tonne.py
@src/uk_subsidy_tracker/plotting/subsidy/remaining_obligations.py
@tests/test_schemas.py
@tests/test_aggregates.py
@tests/test_counterfactual.py

<interfaces>
<!-- Current scheme contract — ARCHITECTURE §6.1 verbatim (also in RESEARCH Pattern 3) -->

```python
# src/uk_subsidy_tracker/schemes/__init__.py  (NEW — to author)
from __future__ import annotations
from pathlib import Path
from typing import Protocol, runtime_checkable

@runtime_checkable
class SchemeModule(Protocol):
    """ARCHITECTURE §6.1 contract — duck-typed module-level callables."""
    DERIVED_DIR: Path
    def upstream_changed(self) -> bool: ...
    def refresh(self) -> None: ...
    def rebuild_derived(self, output_dir: Path | None = None) -> None: ...
    def regenerate_charts(self) -> None: ...
    def validate(self) -> list[str]: ...
```

<!-- Loader that cost_model.py consumes (post-Plan-02 paths) -->

```python
# src/uk_subsidy_tracker/data/__init__.py (existing barrel — re-exports)
from .lccc import load_lccc_dataset     # reads data/raw/lccc/*.csv per Plan 02
from .elexon import load_elexon_wind_daily, load_elexon_prices_daily
from .ons_gas import load_gas_price

# src/uk_subsidy_tracker/counterfactual.py
METHODOLOGY_VERSION: str = "0.1.0"  # line 38 — stamp on every derived row
def compute_counterfactual(
    gas_df: pd.DataFrame | None = None,
    carbon_prices: dict[int, float] | None = None,
    ccgt_efficiency: float = CCGT_EFFICIENCY,
    non_fuel_opex_per_mwh: float = DEFAULT_NON_FUEL_OPEX,
) -> pd.DataFrame: ...
# Returns date, counterfactual_fuel, counterfactual_carbon, counterfactual_total
# (all daily) plus methodology_version column per Phase-2 GOV-04.
```

<!-- Pinned Parquet writer (D-22; RESEARCH Pattern 1) — reuse verbatim -->

```python
# In each schemes/cfd/*.py writer:
import pyarrow as pa
import pyarrow.parquet as pq

def _write_parquet(df: pd.DataFrame, path: Path) -> None:
    """D-22 pinned call pattern."""
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(
        table, path,
        compression="snappy",
        version="2.6",
        use_dictionary=True,
        write_statistics=True,
        data_page_size=1 << 20,
    )
```

<!-- Source excerpts to hoist — see PATTERNS.md §C for the full mapping -->

```python
# PATTERNS §C.1 — station_month source: cfd_dynamics.py::_prepare() lines 32-66
# PATTERNS §C.2 — by_technology source: cfd_payments_by_category.py lines 48-67 + subsidy_per_avoided_co2_tonne.py lines 42-58
# PATTERNS §C.3 — forward_projection source: remaining_obligations.py lines 80-124
```

<!-- Pandera schema canonical idiom — mirror src/uk_subsidy_tracker/data/lccc.py:36-54 -->

```python
# In cost_model.py (or sibling schemas file):
import pandera.pandas as pa
station_month_schema = pa.DataFrameSchema(
    {
        "station_id": pa.Column(str),
        "technology": pa.Column(str),
        "allocation_round": pa.Column(str),
        "month_end": pa.Column("datetime64[ns]", coerce=True),
        "cfd_generation_mwh": pa.Column(float),
        "cfd_payments_gbp": pa.Column(float),
        "strike_price_gbp_per_mwh": pa.Column(float, nullable=True),
        "market_reference_price_gbp_per_mwh": pa.Column(float, nullable=True),
        "methodology_version": pa.Column(str),
    },
    strict=False, coerce=True,
)
```

<!-- Pydantic row schema canonical shape — RESEARCH Pattern 5 -->

```python
# src/uk_subsidy_tracker/schemas/cfd.py (NEW)
from datetime import date
from pydantic import BaseModel, Field

class StationMonthRow(BaseModel):
    """One row in cfd/station_month.parquet (order = Parquet column order, D-10)."""
    station_id: str = Field(description="LCCC CfD Unit ID.",
                            json_schema_extra={"dtype": "string"})
    technology: str = Field(description="Technology group.",
                            json_schema_extra={"dtype": "string"})
    allocation_round: str = Field(description="AR1, AR2, AR3, ...",
                                  json_schema_extra={"dtype": "string"})
    month_end: date = Field(description="Last day of the settlement month.",
                            json_schema_extra={"dtype": "date", "unit": "ISO-8601"})
    cfd_generation_mwh: float = Field(description="MWh eligible for CfD in this month.",
                                      json_schema_extra={"dtype": "float64", "unit": "MWh"})
    cfd_payments_gbp: float = Field(description="Gross CfD payments received in this month.",
                                    json_schema_extra={"dtype": "float64", "unit": "£"})
    strike_price_gbp_per_mwh: float | None = Field(
        default=None, description="Strike price applicable this month.",
        json_schema_extra={"dtype": "float64", "unit": "£/MWh"})
    market_reference_price_gbp_per_mwh: float | None = Field(
        default=None, description="Market reference price (IMRP / season-ahead).",
        json_schema_extra={"dtype": "float64", "unit": "£/MWh"})
    methodology_version: str = Field(
        description="Version tag of the gas counterfactual applied (GOV-04).",
        json_schema_extra={"dtype": "string"})
```

<!-- Test-file extensions — preserve existing shape; D-19/D-20 -->

See PATTERNS §F for full "extend, don't replace" discipline on tests/test_schemas.py + tests/test_aggregates.py.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Pydantic table schemas (schemas/cfd.py) + SchemeModule Protocol + five test axes scaffolding</name>
  <files>
    src/uk_subsidy_tracker/schemas/__init__.py,
    src/uk_subsidy_tracker/schemas/cfd.py,
    src/uk_subsidy_tracker/schemes/__init__.py,
    tests/test_determinism.py
  </files>
  <read_first>
    - .planning/phases/04-publishing-layer/04-RESEARCH.md §Pattern 3 (Protocol template, lines 621-719), §Pattern 5 (Pydantic → JSON Schema, lines 763-826), §Pattern 1 (determinism test full template, lines 376-460)
    - .planning/phases/04-publishing-layer/04-PATTERNS.md §A (Pydantic idiom), §D (determinism test)
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-01 / D-02 / D-03 / D-07 / D-10 / D-11 / D-21 / D-22
    - src/uk_subsidy_tracker/data/lccc.py lines 36-54 (pandera DataFrameSchema idiom to mirror in schemas/cfd.py)
    - tests/fixtures/__init__.py (Pydantic v2 discipline + HttpUrl import example)
    - tests/test_counterfactual.py lines 38-67 (remediation-hook failure message shape)
  </read_first>
  <behavior>
    <!-- TDD: test_determinism.py is written FIRST — it imports cfd and calls
         rebuild_derived, which doesn't exist yet. It MUST fail with ImportError
         or ModuleNotFoundError at the start of this plan. After Task 2
         implements cfd + rebuild_derived, the test should turn green. -->

    tests/test_determinism.py behavior:
    - Parametrised over the five grain names.
    - Module-scoped fixtures `derived_once` and `derived_twice` invoke
      `cfd.rebuild_derived(output_dir=tmp_path)` twice into fresh temp dirs.
    - For each grain, assert:
      (a) `t1.schema.equals(t2.schema, check_metadata=False)`
      (b) `t1.num_rows == t2.num_rows`
      (c) `t1.equals(t2)` — content identity
    - One non-parametrised test asserts `pq.read_metadata(...).created_by`
      starts with `parquet-cpp-arrow` (pins writer identity).
    - Remediation-hook failure message cites `METHODOLOGY_VERSION` + `CHANGES.md`.

    schemas/cfd.py behavior:
    - Five BaseModel subclasses, one per grain: StationMonthRow, AnnualSummaryRow,
      ByTechnologyRow, ByAllocationRoundRow, ForwardProjectionRow.
    - Field declaration order IS the canonical column order (D-10 source of truth).
    - Every Field has `description=` and `json_schema_extra={"dtype": "..."}`.
    - Monetary fields carry `"unit": "£"`; MWh fields carry `"unit": "MWh"`;
      CO2 fields `"unit": "tCO2"`; dates carry `"unit": "ISO-8601"`.
    - `methodology_version: str` last field on every row (provenance stamp).

    schemes/__init__.py behavior:
    - Single `SchemeModule` typing.Protocol decorated with `@runtime_checkable`.
    - Five callables matching §6.1 exactly.
    - No ABC (Python `abc.ABC`) — RESEARCH rejects class-wrapping.
  </behavior>
  <action>
    ### Step 1.0 — Pre-flight: determine StationMonthRow shape

    Before authoring the Pydantic row model, confirm which LCCC column names
    are actually present in the raw files. In particular, `Market_Reference_Price_GBP_Per_MWh`
    may or may not exist under that exact name — if absent, drop the
    `market_reference_price_gbp_per_mwh` field from StationMonthRow (Step 1C)
    and from `station_month_schema` (Task 2 Step 2B) in one coherent edit:

    ```bash
    grep -l 'Market_Reference_Price_GBP_Per_MWh' data/raw/lccc/*.csv
    head -1 data/raw/lccc/actual-cfd-generation.csv | tr ',' '\n'
    ```

    Record the outcome in the Task 1 SUMMARY so Task 2 authors the same
    column set. Do NOT guess; if the column is missing, remove it from the
    Pydantic model before Step 1A, not after determinism fails.

    ### Step 1A — Author `tests/test_determinism.py` FIRST (RED)

    File content = RESEARCH §Pattern 1 Code Examples lines 386-460 verbatim,
    with grain names matching Phase 4 decisions. Full skeleton:

    ```python
    """Parquet determinism across rebuilds (TEST-05, D-21).

    Rebuild the five CfD derived grains twice from the same raw state;
    pyarrow.Table.equals() MUST return True. Does NOT compare raw bytes —
    Parquet embeds a file-level `created_by` string and row-group metadata
    timestamps that legitimately differ on every write. Content identity is
    the spec-compliant determinism check.

    If this fails: either (a) a non-determinism was introduced in
    rebuild_derived() (clock reads, random.shuffle, groupby sort instability,
    platform FMA drift), or (b) the methodology constants actually changed
    — in which case bump METHODOLOGY_VERSION and add a CHANGES.md entry.
    """
    from pathlib import Path

    import pyarrow.parquet as pq
    import pytest

    from uk_subsidy_tracker.schemes import cfd
    from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION


    GRAINS = (
        "station_month",
        "annual_summary",
        "by_technology",
        "by_allocation_round",
        "forward_projection",
    )


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
        assert t1.schema.equals(t2.schema, check_metadata=False), (
            f"Parquet schema drift for {grain}:\n  run1: {t1.schema}\n  run2: {t2.schema}"
        )
        assert t1.num_rows == t2.num_rows, (
            f"Row count drift for {grain}: {t1.num_rows} vs {t2.num_rows}"
        )
        assert t1.equals(t2), (
            f"Parquet content drift for {grain} — same raw input should produce "
            f"identical rows. If intentional (methodology change), bump "
            f"METHODOLOGY_VERSION (currently {METHODOLOGY_VERSION!r}) and add a "
            f"CHANGES.md `## Methodology versions` entry."
        )


    @pytest.mark.parametrize("grain", GRAINS)
    def test_file_metadata_created_by_is_pyarrow(grain, derived_once):
        """Pin the writer-identity so a migration to fastparquet/polars surfaces."""
        meta = pq.read_metadata(derived_once / f"{grain}.parquet")
        assert meta.created_by.startswith("parquet-cpp-arrow"), (
            f"Parquet writer changed for {grain}: {meta.created_by!r}"
        )
    ```

    Run: `uv run pytest tests/test_determinism.py -v` — MUST fail with
    ModuleNotFoundError: No module named 'uk_subsidy_tracker.schemes'.
    Confirm failure, proceed.

    ### Step 1B — Author `src/uk_subsidy_tracker/schemas/__init__.py`

    ```python
    """Pydantic row schemas for the derived Parquet layer.

    Field declaration order on each row model IS the canonical column order
    (D-10). Every model emits JSON Schema via `model_json_schema(mode='serialization')`
    for the per-table `<grain>.schema.json` sidecars (D-11, built in Plan 04).
    """
    from uk_subsidy_tracker.schemas.cfd import (
        StationMonthRow,
        AnnualSummaryRow,
        ByTechnologyRow,
        ByAllocationRoundRow,
        ForwardProjectionRow,
    )

    __all__ = [
        "StationMonthRow",
        "AnnualSummaryRow",
        "ByTechnologyRow",
        "ByAllocationRoundRow",
        "ForwardProjectionRow",
    ]
    ```

    ### Step 1C — Author `src/uk_subsidy_tracker/schemas/cfd.py` (full file)

    Five BaseModel classes. Expand the StationMonthRow from the interface
    block above; author the other four by analogy:

    - **AnnualSummaryRow:** `year: int`, `cfd_generation_mwh: float`,
      `cfd_payments_gbp: float`, `counterfactual_payments_gbp: float`,
      `premium_over_gas_gbp: float`, `methodology_version: str`.
    - **ByTechnologyRow:** `year: int`, `technology: str`,
      `cfd_generation_mwh: float`, `cfd_payments_gbp: float`,
      `methodology_version: str`.
    - **ByAllocationRoundRow:** `year: int`, `allocation_round: str`,
      `cfd_generation_mwh: float`, `cfd_payments_gbp: float`,
      `avoided_co2_tonnes: float`, `methodology_version: str`.
    - **ForwardProjectionRow:** `station_id: str`, `technology: str`,
      `contract_start_year: int`, `contract_end_year: int`,
      `avg_annual_generation_mwh: float`, `avg_strike_gbp_per_mwh: float`,
      `remaining_committed_mwh: float`, `methodology_version: str`.

    Every Field MUST carry `description` + `json_schema_extra` with `dtype`
    (one of: `"string"`, `"int64"`, `"float64"`, `"date"`) and `unit` where
    applicable (`"MWh"`, `"£"`, `"£/MWh"`, `"tCO2"`, `"ISO-8601"`).

    Add a module-level helper:

    ```python
    def emit_schema_json(model: type[BaseModel], path) -> None:
        """Write <grain>.schema.json sibling to a Parquet file (D-11)."""
        import json
        schema = model.model_json_schema(mode="serialization")
        path.write_text(
            json.dumps(schema, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n",
        )
    ```

    ### Step 1D — Author `src/uk_subsidy_tracker/schemes/__init__.py`

    Exactly the RESEARCH Pattern 3 SchemeModule Protocol — no more, no less.
    40-50 lines including docstring.

    ### Step 1E — Confirm red/green transition

    ```bash
    uv run pytest tests/test_determinism.py -v
    ```

    Still fails because `cfd` module doesn't exist. That's expected — Task 2
    ships cfd and turns determinism green.

    <tdd_note>
    Before Task 2 runs, `uv run pytest tests/test_determinism.py` should error
    with ModuleNotFoundError (no `uk_subsidy_tracker.schemes` package yet) —
    this is the expected RED state. Task 2 flips it to GREEN by implementing
    the `schemes/cfd/` package. This is a TDD expectation, not a gate — do
    NOT add pytest-output-grep acceptance criteria (output format varies
    across versions). The module-import smoke test in `<verify><automated>`
    remains a valid gate (it checks successful imports after Task 1's schema
    files land; the `cfd` module import only succeeds after Task 2).
    </tdd_note>
  </action>
  <verify>
    <automated>uv run python -c "from uk_subsidy_tracker.schemas import StationMonthRow, AnnualSummaryRow, ByTechnologyRow, ByAllocationRoundRow, ForwardProjectionRow; from uk_subsidy_tracker.schemes import SchemeModule; print('OK')"</automated>
  </verify>
  <acceptance_criteria>
    - `test -f src/uk_subsidy_tracker/schemas/__init__.py` exits 0
    - `test -f src/uk_subsidy_tracker/schemas/cfd.py` exits 0
    - `test -f src/uk_subsidy_tracker/schemes/__init__.py` exits 0
    - `test -f tests/test_determinism.py` exits 0
    - `grep -c "^class " src/uk_subsidy_tracker/schemas/cfd.py` returns 5 (five row models)
    - All five row models export from `schemas/__init__.py`: `grep -c "Row," src/uk_subsidy_tracker/schemas/__init__.py` ≥ 5
    - `grep -q "@runtime_checkable" src/uk_subsidy_tracker/schemes/__init__.py` exits 0
    - `grep -q "class SchemeModule" src/uk_subsidy_tracker/schemes/__init__.py` exits 0
    - `grep -cE "def (upstream_changed|refresh|rebuild_derived|regenerate_charts|validate)" src/uk_subsidy_tracker/schemes/__init__.py` returns 5
    - `grep -q "DERIVED_DIR" src/uk_subsidy_tracker/schemes/__init__.py` exits 0
    - Every row model field has json_schema_extra dtype: `grep -c "json_schema_extra" src/uk_subsidy_tracker/schemas/cfd.py` ≥ 20
    - `grep -q "methodology_version" src/uk_subsidy_tracker/schemas/cfd.py` — every row model has this field
    - `grep -q "emit_schema_json" src/uk_subsidy_tracker/schemas/cfd.py` exits 0
    - `uv run python -c "from uk_subsidy_tracker.schemas import StationMonthRow; import json; s = StationMonthRow.model_json_schema(mode='serialization'); assert 'properties' in s; assert 'methodology_version' in s['properties']"` exits 0
    - `uv run pytest tests/test_counterfactual.py tests/test_constants_provenance.py tests/test_schemas.py tests/test_aggregates.py -x` all pass (no regression from adding packages)
  </acceptance_criteria>
  <done>Pydantic table schemas + Protocol + determinism test authored. Determinism test fails in expected way (cfd module missing). Pre-existing tests still green.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Implement schemes/cfd/ — cost_model, aggregation, forward_projection, _refresh, __init__ wiring</name>
  <files>
    src/uk_subsidy_tracker/schemes/cfd/__init__.py,
    src/uk_subsidy_tracker/schemes/cfd/cost_model.py,
    src/uk_subsidy_tracker/schemes/cfd/aggregation.py,
    src/uk_subsidy_tracker/schemes/cfd/forward_projection.py,
    src/uk_subsidy_tracker/schemes/cfd/_refresh.py,
    .gitignore
  </files>
  <read_first>
    - .planning/phases/04-publishing-layer/04-PATTERNS.md §C (full aggregation-hoist mapping with exact source-file line ranges)
    - .planning/phases/04-publishing-layer/04-RESEARCH.md §Pattern 1 (pinned Parquet writer), §Pattern 3 (scheme-module contract)
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-01 (minimal-wrap real impl), D-03 (canonical derivation path), D-22 (pinned Parquet writer)
    - src/uk_subsidy_tracker/plotting/subsidy/cfd_dynamics.py lines 32-66 (station_month source)
    - src/uk_subsidy_tracker/plotting/subsidy/cfd_payments_by_category.py lines 48-67 (by_technology pattern)
    - src/uk_subsidy_tracker/plotting/subsidy/subsidy_per_avoided_co2_tonne.py lines 42-58 (by_allocation_round + avoided-co2 pattern)
    - src/uk_subsidy_tracker/plotting/subsidy/remaining_obligations.py lines 80-124 (forward_projection source)
    - src/uk_subsidy_tracker/data/lccc.py lines 105-114 (loader-owned validation idiom)
    - src/uk_subsidy_tracker/counterfactual.py (compute_counterfactual signature, METHODOLOGY_VERSION)
    - src/uk_subsidy_tracker/schemas/cfd.py (Pydantic models, field names, column order)
    - .gitignore (append data/derived/ — do not overwrite existing entries)
  </read_first>
  <behavior>
    <!-- TDD already RED from Task 1 (test_determinism.py cannot import cfd).
         After Task 2, tests/test_determinism.py MUST be green for all 10 cases
         (5 content-equality + 5 writer-identity). -->

    cfd.rebuild_derived(output_dir=None) behavior:
    - If `output_dir is None`: write to `DERIVED_DIR = PROJECT_ROOT/data/derived/cfd/`.
    - Else: write to the caller-supplied `output_dir` (test fixtures depend on this).
    - Writes five Parquet files via pinned `_write_parquet` helper (D-22).
    - Every row in every grain has a `methodology_version` column populated from
      `counterfactual.METHODOLOGY_VERSION` (GOV-02).
    - Emits a sibling `<grain>.schema.json` for each Parquet via
      `schemas.cfd.emit_schema_json(model, path)` — keeps manifest.py simple
      later (Plan 04 reads these).
    - Is a PURE function of `data/raw/` content (Pitfall 1): NO `datetime.now()`,
      NO `random`, NO global mutable state. Sort orders are stable (groupby keys
      explicit). Ensures determinism test passes.

    cfd.upstream_changed() behavior (Plan 04 refines; basic here):
    - Compares computed sha256 of each raw file against its sidecar.sha256.
    - Returns True if ANY differs; False if all match.

    cfd.refresh() behavior:
    - Delegates to the existing `download_lccc_datasets` + elexon/ons re-fetch
      routines, then re-writes each sidecar from ground truth.
    - For Phase 4: may be a thin wrapper — full refresh wiring is Plan 05.

    cfd.regenerate_charts() behavior:
    - Delegates to `uk_subsidy_tracker.plotting.__main__.main` if it exists,
      or `plotting.main()` equivalent.

    cfd.validate() behavior (D-discretion default):
    - Returns list[str]. Three checks: (a) row count for latest year within
      ±10% of previous year; (b) no null technology in station_month;
      (c) methodology_version column matches constant.
  </behavior>
  <action>
    ### Step 2A — `.gitignore` for derived layer

    Append (do not replace):

    ```gitignore
    # Phase 4: derived Parquet tables are regenerated from data/raw/ on every refresh.
    # Only raw data + workflows + source + tests live in git.
    data/derived/
    ```

    ### Step 2B — `src/uk_subsidy_tracker/schemes/cfd/cost_model.py`

    Canonical shape (hoist from `plotting/subsidy/cfd_dynamics.py::_prepare`
    + `cfd_vs_gas_cost.py::_prepare_monthly`):

    ```python
    """Station × month derivation for the CfD scheme (derived-layer writer).

    Reads `data/raw/lccc/actual-cfd-generation.csv` + `cfd-contract-portfolio-status.csv`
    + `data/raw/ons/gas-sap.xlsx` via the existing loaders; joins the gas
    counterfactual; writes `station_month.parquet` via the pinned writer.
    """

    from __future__ import annotations

    from pathlib import Path

    import pandas as pd
    import pandera.pandas as pa
    import pyarrow as pa_arrow  # rename to avoid pandera collision
    import pyarrow.parquet as pq

    from uk_subsidy_tracker.counterfactual import (
        METHODOLOGY_VERSION, compute_counterfactual,
    )
    from uk_subsidy_tracker.data import load_lccc_dataset
    from uk_subsidy_tracker.schemas.cfd import StationMonthRow, emit_schema_json


    # Loader-owned pandera schema; every field name == StationMonthRow field.
    station_month_schema = pa.DataFrameSchema(
        {
            "station_id": pa.Column(str),
            "technology": pa.Column(str),
            "allocation_round": pa.Column(str),
            "month_end": pa.Column("datetime64[ns]", coerce=True),
            "cfd_generation_mwh": pa.Column(float),
            "cfd_payments_gbp": pa.Column(float),
            "strike_price_gbp_per_mwh": pa.Column(float, nullable=True),
            "market_reference_price_gbp_per_mwh": pa.Column(float, nullable=True),
            "methodology_version": pa.Column(str),
        },
        strict=False, coerce=True,
    )


    def _write_parquet(df: pd.DataFrame, path: Path) -> None:
        """Deterministic Parquet writer (D-22). NO `now()`, NO random."""
        table = pa_arrow.Table.from_pandas(df, preserve_index=False)
        pq.write_table(
            table, path,
            compression="snappy",
            version="2.6",
            use_dictionary=True,
            write_statistics=True,
            data_page_size=1 << 20,
        )


    def build_station_month(output_dir: Path) -> pd.DataFrame:
        """Build and persist `station_month.parquet` + `station_month.schema.json`.

        Pure function of data/raw/ content — no clock, no randomness. Column
        order = StationMonthRow field-declaration order (D-10).
        """
        gen = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions").copy()
        portfolio = load_lccc_dataset("CfD Contract Portfolio Status").copy()

        # Hoisted from cfd_dynamics.py::_prepare lines 32-66:
        gen = gen.dropna(subset=["CFD_Generation_MWh", "Strike_Price_GBP_Per_MWh"])
        gen = gen[gen["CFD_Generation_MWh"] > 0]

        # Month-end anchor. `to_period("M").to_timestamp(how="end")` gives the
        # last day of the month; `.normalize()` strips time (stable sort, determinism).
        gen["month_end"] = (
            gen["Settlement_Date"].dt.to_period("M").dt.to_timestamp(how="end").dt.normalize()
        )

        # Station × month grain: sum generation + payments; weighted strike.
        gen["strike_x_gen"] = gen["Strike_Price_GBP_Per_MWh"] * gen["CFD_Generation_MWh"]
        grp = gen.groupby(["CfD_ID", "month_end"], sort=True).agg(
            cfd_generation_mwh=("CFD_Generation_MWh", "sum"),
            cfd_payments_gbp=("CFD_Payments_GBP", "sum"),
            strike_x_gen=("strike_x_gen", "sum"),
            market_reference_price_gbp_per_mwh=(
                "Market_Reference_Price_GBP_Per_MWh", "mean",  # placeholder if column exists
            ),
        ).reset_index()

        grp["strike_price_gbp_per_mwh"] = grp["strike_x_gen"] / grp["cfd_generation_mwh"]
        grp = grp.drop(columns=["strike_x_gen"])

        # Join portfolio for technology + allocation_round. Handle LCCC column-
        # name inconsistency per plotting/subsidy/remaining_obligations.py:83.
        portfolio = portfolio.rename(columns={"CFD_ID": "CfD_ID"})
        pf = portfolio[["CfD_ID", "Technology_Type", "Allocation_Round"]].rename(
            columns={
                "Technology_Type": "technology",
                "Allocation_Round": "allocation_round",
            }
        )
        df = grp.merge(pf, on="CfD_ID", how="left")
        df = df.rename(columns={"CfD_ID": "station_id"})
        df["methodology_version"] = METHODOLOGY_VERSION

        # Column order must match StationMonthRow for D-10.
        columns = [f for f in StationMonthRow.model_fields.keys()]
        df = df[columns].sort_values(["station_id", "month_end"]).reset_index(drop=True)

        # Loader/derivation-owned validation (discipline carried from Phase 2).
        df = station_month_schema.validate(df)

        output_dir.mkdir(parents=True, exist_ok=True)
        _write_parquet(df, output_dir / "station_month.parquet")
        emit_schema_json(StationMonthRow, output_dir / "station_month.schema.json")
        return df
    ```

    NOTE: The exact pandas aggregation above is a best-effort hoist. Executor
    MUST verify column names against the actual CSV schemas (pandera schemas
    in src/uk_subsidy_tracker/data/lccc.py lines 36-54) — some columns
    (`Market_Reference_Price_GBP_Per_MWh`) may not exist; if absent, drop
    from `StationMonthRow` and `station_month_schema` in Step 1C above and
    here in one coherent edit.

    ### Step 2C — `src/uk_subsidy_tracker/schemes/cfd/aggregation.py`

    Implement three builders (hoist per PATTERNS §C.2). Each:
    1. Reads `station_month.parquet` (the canonical upstream grain), via
       `pq.read_table(output_dir / "station_month.parquet").to_pandas()` if
       writing to `output_dir`, OR re-reads raw. Choose one pattern and
       document in the module docstring. Recommended: re-read from
       `station_month.parquet` to ensure rollup consistency (D-03: the
       derivation is canonical; annual = sum of station_month by year).
    2. Groups + aggregates.
    3. Stamps `methodology_version`.
    4. Writes Parquet + schema.json via the same `_write_parquet` + `emit_schema_json`.

    Three functions:
    - `build_annual_summary(output_dir)`
    - `build_by_technology(output_dir)`
    - `build_by_allocation_round(output_dir)`

    ### Step 2D — `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py`

    Hoist from `plotting/subsidy/remaining_obligations.py::main` lines 80-124.
    Produce one row per station_id with: technology, contract_start_year,
    contract_end_year, avg_annual_generation_mwh, avg_strike_gbp_per_mwh,
    remaining_committed_mwh, methodology_version.

    Preserve the `Allocation_round` vs `Allocation_Round` handling from
    remaining_obligations.py:83.

    ### Step 2E — `src/uk_subsidy_tracker/schemes/cfd/_refresh.py`

    Minimal implementation: sha-compare for `upstream_changed()`, thin wrapper
    for `refresh()`. Plan 04's `refresh_all.py` orchestrates.

    ```python
    """Dirty-check + refresh helpers for the CfD scheme."""
    import hashlib
    import json
    from pathlib import Path

    from uk_subsidy_tracker import DATA_DIR

    _RAW_FILES = [
        "raw/lccc/actual-cfd-generation.csv",
        "raw/lccc/cfd-contract-portfolio-status.csv",
        "raw/elexon/agws.csv",
        "raw/elexon/system-prices.csv",
        "raw/ons/gas-sap.xlsx",
    ]


    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 16), b""):
                h.update(chunk)
        return h.hexdigest()


    def upstream_changed() -> bool:
        """Return True iff any raw file's sha256 differs from its sidecar."""
        for rel in _RAW_FILES:
            raw = DATA_DIR / rel
            meta = raw.with_suffix(raw.suffix + ".meta.json")
            if not meta.exists():
                return True  # missing sidecar == assume drift
            sidecar = json.loads(meta.read_text())
            if _sha256(raw) != sidecar.get("sha256"):
                return True
        return False


    def refresh() -> None:
        """Re-fetch LCCC/Elexon/ONS raw files. Plan 05 wires the workflow."""
        from uk_subsidy_tracker.data.lccc import download_lccc_datasets
        download_lccc_datasets()
        # Elexon + ONS refresh calls exist in their respective modules;
        # wire as needed. Plan 05 turns this into an end-to-end refresh
        # with sidecar rewrites.
    ```

    ### Step 2F — `src/uk_subsidy_tracker/schemes/cfd/__init__.py`

    Tie the five contract callables together. RESEARCH Pattern 3 provides
    the template (lines 656-717). Set `DERIVED_DIR` to
    `PROJECT_ROOT / "data" / "derived" / "cfd"`.

    ```python
    """CfD scheme module — ARCHITECTURE §6.1 contract.

    Five module-level callables satisfying the SchemeModule Protocol. This
    is the template Phase 5 (RO) and every subsequent scheme module copies.
    """
    from __future__ import annotations

    from pathlib import Path

    from uk_subsidy_tracker import PROJECT_ROOT
    from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
    from uk_subsidy_tracker.schemes.cfd._refresh import (
        refresh as _refresh,
        upstream_changed as _upstream_changed,
    )
    from uk_subsidy_tracker.schemes.cfd.aggregation import (
        build_annual_summary, build_by_allocation_round, build_by_technology,
    )
    from uk_subsidy_tracker.schemes.cfd.cost_model import build_station_month
    from uk_subsidy_tracker.schemes.cfd.forward_projection import build_forward_projection

    DERIVED_DIR = PROJECT_ROOT / "data" / "derived" / "cfd"


    def upstream_changed() -> bool:
        return _upstream_changed()


    def refresh() -> None:
        _refresh()


    def rebuild_derived(output_dir: Path | None = None) -> None:
        target = output_dir if output_dir is not None else DERIVED_DIR
        target.mkdir(parents=True, exist_ok=True)
        build_station_month(target)
        build_annual_summary(target)
        build_by_technology(target)
        build_by_allocation_round(target)
        build_forward_projection(target)


    def regenerate_charts() -> None:
        """Delegate to existing plotting entry point (D-02 — charts untouched)."""
        from uk_subsidy_tracker import plotting as _plotting
        # Plotting module exposes a main() via __main__; call it.
        if hasattr(_plotting, "main"):
            _plotting.main()
        else:
            import runpy
            runpy.run_module("uk_subsidy_tracker.plotting", run_name="__main__")


    def validate() -> list[str]:
        """Return human-readable warnings (D-discretion default: 3 checks)."""
        import pyarrow.parquet as pq
        warnings: list[str] = []
        station_month = DERIVED_DIR / "station_month.parquet"
        if not station_month.exists():
            return [f"validate: {station_month} missing — run rebuild_derived()"]
        df = pq.read_table(station_month).to_pandas()

        # Check 1: latest-year row count within ±10% of previous year.
        df["year"] = df["month_end"].dt.year
        yearly = df.groupby("year").size().sort_index()
        if len(yearly) >= 2:
            latest, previous = yearly.iloc[-1], yearly.iloc[-2]
            if abs(latest - previous) / max(previous, 1) > 0.10:
                warnings.append(
                    f"validate: latest-year row count drift > 10% ({previous} -> {latest})"
                )

        # Check 2: no null technology.
        if df["technology"].isna().any():
            warnings.append("validate: null technology in station_month")

        # Check 3: methodology_version matches constant.
        unique_versions = df["methodology_version"].unique()
        if len(unique_versions) != 1 or unique_versions[0] != METHODOLOGY_VERSION:
            warnings.append(
                f"validate: methodology_version drift — column has {unique_versions!r}, "
                f"constant is {METHODOLOGY_VERSION!r}"
            )

        return warnings
    ```

    ### Step 2G — Verify determinism test turns GREEN

    ```bash
    uv run pytest tests/test_determinism.py -v
    ```

    Expected: 10 passed (5 content-equality + 5 writer-identity). If a content-
    equality test fails:
    - Check Pitfall 1 — any `datetime.now()` or `random.*` in the derivation?
    - Check groupby sort — pass `sort=True` explicitly.
    - Check float determinism — if FMA differs, isolate with `df.round(n)` on
      aggregated columns; document in the function docstring.

    ### Step 2H — Full test suite green

    ```bash
    uv run pytest tests/ -v
    ```

    Must pass. Also run charts + mkdocs to confirm D-02 compliance:

    ```bash
    uv run python -m uk_subsidy_tracker.plotting  # charts still work
    uv run mkdocs build --strict
    ```
  </action>
  <verify>
    <automated>uv run pytest tests/test_determinism.py -v &amp;&amp; uv run pytest tests/ &amp;&amp; uv run python -c "from pathlib import Path; from uk_subsidy_tracker.schemes import cfd; import tempfile; tmp = Path(tempfile.mkdtemp()); cfd.rebuild_derived(output_dir=tmp); assert (tmp / 'station_month.parquet').exists(); assert (tmp / 'annual_summary.parquet').exists(); assert (tmp / 'by_technology.parquet').exists(); assert (tmp / 'by_allocation_round.parquet').exists(); assert (tmp / 'forward_projection.parquet').exists(); print('All 5 grains produced')"</automated>
  </verify>
  <acceptance_criteria>
    - `test -d src/uk_subsidy_tracker/schemes/cfd` exits 0
    - All five module files exist: `for f in __init__.py cost_model.py aggregation.py forward_projection.py _refresh.py; do test -f "src/uk_subsidy_tracker/schemes/cfd/$f" || exit 1; done`
    - `grep -q "^data/derived/" .gitignore` exits 0
    - `grep -q "DERIVED_DIR" src/uk_subsidy_tracker/schemes/cfd/__init__.py` exits 0
    - `grep -cE "^def (upstream_changed|refresh|rebuild_derived|regenerate_charts|validate)" src/uk_subsidy_tracker/schemes/cfd/__init__.py` returns 5
    - `grep -q "def build_station_month" src/uk_subsidy_tracker/schemes/cfd/cost_model.py` exits 0
    - `grep -cE "^def build_(annual_summary|by_technology|by_allocation_round)" src/uk_subsidy_tracker/schemes/cfd/aggregation.py` returns 3
    - `grep -q "def build_forward_projection" src/uk_subsidy_tracker/schemes/cfd/forward_projection.py` exits 0
    - `grep -q "methodology_version" src/uk_subsidy_tracker/schemes/cfd/cost_model.py` exits 0
    - `grep -q "METHODOLOGY_VERSION" src/uk_subsidy_tracker/schemes/cfd/cost_model.py` exits 0
    - Pinned Parquet writer present in cost_model: `grep -q 'version="2.6"' src/uk_subsidy_tracker/schemes/cfd/cost_model.py` exits 0
    - `grep -q 'compression="snappy"' src/uk_subsidy_tracker/schemes/cfd/cost_model.py` exits 0
    - No forbidden non-determinism: `! grep -rE 'datetime\.now|time\.time|random\.' src/uk_subsidy_tracker/schemes/cfd/` returns no matches (exit 1 from grep = acceptance)
    - `uv run pytest tests/test_determinism.py -v` — 10 passed (5 content + 5 writer-identity)
    - `uv run pytest tests/` — full suite green; no regression
    - `isinstance(cfd, SchemeModule)` check: `uv run python -c "from uk_subsidy_tracker.schemes import cfd, SchemeModule; assert isinstance(cfd, SchemeModule), 'cfd module does not satisfy SchemeModule Protocol'"` exits 0
    - `uv run python -c "from pathlib import Path; from uk_subsidy_tracker.schemes import cfd; import tempfile; tmp = Path(tempfile.mkdtemp()); cfd.rebuild_derived(output_dir=tmp); assert (tmp / 'station_month.parquet').exists(); assert (tmp / 'station_month.schema.json').exists()"` exits 0
    - Per-table schema.json sibling exists: after rebuild, `ls data/derived/cfd/*.schema.json | wc -l` = 5 (or tmp dir equivalent)
    - `uv run python -m uk_subsidy_tracker.plotting` — charts still regenerate without error (D-02 — charts unchanged)
    - `uv run mkdocs build --strict` — docs still build
  </acceptance_criteria>
  <done>cfd.rebuild_derived() produces 5 Parquet files + 5 schema.json siblings. Determinism test green (10/10). Full test suite green. Chart gen + mkdocs still work. cfd module satisfies SchemeModule Protocol via isinstance check.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Extend test_schemas.py + test_aggregates.py with Parquet variants (D-19, D-20)</name>
  <files>tests/test_schemas.py, tests/test_aggregates.py</files>
  <read_first>
    - tests/test_schemas.py (current file — EXTEND; do NOT replace)
    - tests/test_aggregates.py (current file — EXTEND; do NOT replace)
    - .planning/phases/04-publishing-layer/04-PATTERNS.md §F (extend-don't-replace discipline; exact test name conventions)
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-19, D-20
    - src/uk_subsidy_tracker/schemas/cfd.py (Pydantic row models for validation)
    - src/uk_subsidy_tracker/schemes/cfd/__init__.py (rebuild_derived signature)
  </read_first>
  <behavior>
    New Parquet-variant tests in `tests/test_schemas.py`:

    - `test_station_month_parquet_schema` — read station_month.parquet, validate
      each row via `StationMonthRow.model_validate(dict_row)`; assert key columns
      present with expected dtypes.
    - `test_annual_summary_parquet_schema` — same for AnnualSummaryRow.
    - `test_by_technology_parquet_schema` — same.
    - `test_by_allocation_round_parquet_schema` — same.
    - `test_forward_projection_parquet_schema` — same.

    New Parquet-variant tests in `tests/test_aggregates.py`:

    - `test_annual_vs_station_month_parquet` — sum(cfd_payments_gbp by year) via
      station_month == sum via annual_summary (exact equality,
      `pd.testing.assert_series_equal`).
    - `test_by_tech_vs_annual_parquet` — sum(cfd_payments_gbp by year via
      by_technology) == sum via annual_summary.
    - `test_by_round_vs_annual_parquet` — same for by_allocation_round.

    All six tests use a module-scoped fixture that invokes
    `cfd.rebuild_derived(output_dir=tmp_path)` ONCE (reuse across tests).
  </behavior>
  <action>
    ### Step 3A — Extend `tests/test_schemas.py`

    APPEND under the existing tests (preserve the module docstring, imports,
    and five existing `test_*_schema` functions). Add a module-scoped fixture
    and five Parquet-variant tests:

    ```python
    # Below the existing tests — APPEND

    import pyarrow.parquet as pq
    import pytest
    from pathlib import Path

    from uk_subsidy_tracker.schemas import (
        StationMonthRow, AnnualSummaryRow, ByTechnologyRow,
        ByAllocationRoundRow, ForwardProjectionRow,
    )
    from uk_subsidy_tracker.schemes import cfd


    @pytest.fixture(scope="module")
    def derived_dir(tmp_path_factory) -> Path:
        """Rebuild all five grains once for the module (reused across tests)."""
        out = tmp_path_factory.mktemp("test-schemas-derived")
        cfd.rebuild_derived(output_dir=out)
        return out


    _GRAIN_MODELS = {
        "station_month": StationMonthRow,
        "annual_summary": AnnualSummaryRow,
        "by_technology": ByTechnologyRow,
        "by_allocation_round": ByAllocationRoundRow,
        "forward_projection": ForwardProjectionRow,
    }


    @pytest.mark.parametrize("grain, model", list(_GRAIN_MODELS.items()))
    def test_parquet_grain_schema(grain, model, derived_dir):
        """TEST-02 (D-19): each derived Parquet validates row-by-row against its Pydantic schema."""
        path = derived_dir / f"{grain}.parquet"
        assert path.exists(), f"{path} missing — cfd.rebuild_derived did not emit"
        df = pq.read_table(path).to_pandas()
        assert not df.empty, f"{grain}.parquet is empty"
        # Column set matches the model exactly.
        expected_columns = list(model.model_fields.keys())
        assert list(df.columns) == expected_columns, (
            f"{grain} column order/set mismatch: "
            f"expected {expected_columns}, got {list(df.columns)}"
        )
        # Validate every row (can be slow on large tables — sample first N
        # if this is a problem; all five grains are small for Phase 4 CfD).
        for row in df.to_dict(orient="records"):
            model.model_validate(row)
    ```

    ### Step 3B — Extend `tests/test_aggregates.py`

    APPEND under the existing `test_year_vs_year_tech_sum_match` +
    `test_no_orphan_technologies`. Add fixture + three conservation tests:

    ```python
    # Below the existing tests — APPEND

    from pathlib import Path

    import pyarrow.parquet as pq

    from uk_subsidy_tracker.schemes import cfd


    @pytest.fixture(scope="module")
    def derived_dir(tmp_path_factory) -> Path:
        out = tmp_path_factory.mktemp("test-aggregates-derived")
        cfd.rebuild_derived(output_dir=out)
        return out


    @pytest.fixture(scope="module")
    def station_month(derived_dir) -> pd.DataFrame:
        df = pq.read_table(derived_dir / "station_month.parquet").to_pandas()
        df["year"] = df["month_end"].dt.year
        return df


    @pytest.fixture(scope="module")
    def annual_summary(derived_dir) -> pd.DataFrame:
        return pq.read_table(derived_dir / "annual_summary.parquet").to_pandas()


    @pytest.fixture(scope="module")
    def by_technology(derived_dir) -> pd.DataFrame:
        return pq.read_table(derived_dir / "by_technology.parquet").to_pandas()


    @pytest.fixture(scope="module")
    def by_allocation_round(derived_dir) -> pd.DataFrame:
        return pq.read_table(derived_dir / "by_allocation_round.parquet").to_pandas()


    def test_annual_vs_station_month_parquet(station_month, annual_summary):
        """TEST-03 (D-20): annual_summary.cfd_payments_gbp = sum(station_month.cfd_payments_gbp by year)."""
        from_sm = station_month.groupby("year")["cfd_payments_gbp"].sum().sort_index()
        from_annual = annual_summary.set_index("year")["cfd_payments_gbp"].sort_index()
        pd.testing.assert_series_equal(from_sm, from_annual, check_names=False)


    def test_by_tech_vs_annual_parquet(by_technology, annual_summary):
        """TEST-03: sum(by_technology.cfd_payments_gbp by year) = annual_summary.cfd_payments_gbp by year."""
        from_tech = by_technology.groupby("year")["cfd_payments_gbp"].sum().sort_index()
        from_annual = annual_summary.set_index("year")["cfd_payments_gbp"].sort_index()
        pd.testing.assert_series_equal(from_tech, from_annual, check_names=False)


    def test_by_round_vs_annual_parquet(by_allocation_round, annual_summary):
        """TEST-03: sum(by_allocation_round.cfd_payments_gbp by year) = annual_summary.cfd_payments_gbp by year."""
        from_round = by_allocation_round.groupby("year")["cfd_payments_gbp"].sum().sort_index()
        from_annual = annual_summary.set_index("year")["cfd_payments_gbp"].sort_index()
        pd.testing.assert_series_equal(from_round, from_annual, check_names=False)
    ```

    ### Step 3C — Confirm green

    ```bash
    uv run pytest tests/test_schemas.py tests/test_aggregates.py -v
    ```

    Expected: all existing raw-CSV tests green (5 in test_schemas + 2 in
    test_aggregates) PLUS 5 new parametrised Parquet-schema tests + 3 new
    Parquet-row-conservation tests. Grand total in these two files: ≥15
    passing.

    If any Parquet-conservation test fails, the derivation has a bug —
    a groupby key is losing rows, or a NaN is being swallowed. Diagnose by
    comparing the non-matching values row-by-row; do NOT weaken the
    assertion from exact equality.
  </action>
  <verify>
    <automated>uv run pytest tests/test_schemas.py tests/test_aggregates.py -v &amp;&amp; uv run pytest tests/ -x</automated>
  </verify>
  <acceptance_criteria>
    - Existing raw-CSV tests preserved: `grep -c "^def test_" tests/test_schemas.py` ≥ 6 (5 original + 1 parametrised new ≥ 6 total function defs; parametrize itself counts as one def)
    - New Parquet-parametrised test present: `grep -q "test_parquet_grain_schema" tests/test_schemas.py` exits 0
    - New Parquet aggregate tests present: `grep -c "_parquet\b" tests/test_aggregates.py` ≥ 3 (three new test function names end with _parquet)
    - `test_annual_vs_station_month_parquet`, `test_by_tech_vs_annual_parquet`, `test_by_round_vs_annual_parquet` all defined in tests/test_aggregates.py (grep each name individually)
    - Module-scoped rebuild fixture used: `grep -q 'tmp_path_factory.mktemp' tests/test_schemas.py` exits 0 AND `grep -q 'tmp_path_factory.mktemp' tests/test_aggregates.py` exits 0
    - `uv run pytest tests/test_schemas.py -v` reports both raw-CSV and Parquet-variant tests passing (≥10 passed)
    - `uv run pytest tests/test_aggregates.py -v` reports ≥5 passed (2 raw + 3 new parquet)
    - `uv run pytest tests/` full-suite green (no regression from test extensions)
    - Verify TDD-check regression discipline: momentarily break one derivation (e.g. `cfd_payments_gbp *= 2` in cost_model), rerun `uv run pytest tests/test_aggregates.py::test_annual_vs_station_month_parquet` → fails with `pd.testing.assert_series_equal` mismatch; REVERT. This is a manual check executed only if any suspicious change is observed.
  </acceptance_criteria>
  <done>tests/test_schemas.py and tests/test_aggregates.py now carry Parquet variants alongside the original raw-CSV scaffolding (D-19, D-20). Full test suite green across all six validation axes (counterfactual, benchmarks, schemas-raw, schemas-parquet, aggregates-raw, aggregates-parquet, determinism, constants-drift).</done>
</task>

<task type="auto" tdd="false">
  <name>Task 4: CHANGES.md entry for derived layer + scheme contract</name>
  <files>CHANGES.md</files>
  <read_first>
    - CHANGES.md (existing [Unreleased] — Plan 01 + Plan 02 entries)
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-01 / D-03 / D-19 / D-20 / D-21 / D-22
  </read_first>
  <action>
    Under `## [Unreleased]`:

    ### Added:

    ```markdown
    - `src/uk_subsidy_tracker/schemas/` package — Pydantic row schemas for the five CfD derived grains (StationMonthRow, AnnualSummaryRow, ByTechnologyRow, ByAllocationRoundRow, ForwardProjectionRow). Field declaration order is the canonical Parquet column order (D-10). `emit_schema_json(model, path)` writes per-table JSON Schema siblings.
    - `src/uk_subsidy_tracker/schemes/__init__.py` — `SchemeModule` `typing.Protocol` declaring the ARCHITECTURE §6.1 contract (`DERIVED_DIR`, `upstream_changed`, `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`). Phase 5 (RO) and every subsequent scheme module copy this pattern.
    - `src/uk_subsidy_tracker/schemes/cfd/` — first real implementation of §6.1. Five module-level callables; `rebuild_derived()` emits five Parquet grains under `data/derived/cfd/` via pinned pyarrow writer (`compression="snappy"`, `version="2.6"`, `data_page_size=1MB` per D-22). Aggregation logic hoisted out of chart files per D-01.
    - `tests/test_determinism.py` — TEST-05 satisfied. Parametrised content-equality via `pyarrow.Table.equals()` across all five grains; second parametrised test pins the Parquet writer identity (`created_by.startswith("parquet-cpp-arrow")`).
    - Parquet-variant tests in `tests/test_schemas.py` (D-19) and `tests/test_aggregates.py` (D-20) — formalises TEST-02 + TEST-03 on derived output alongside the Phase-2 raw-CSV scaffolding.
    - `.gitignore` — `data/derived/` ignored (regenerated on every rebuild).
    ```

    ### Changed:

    ```markdown
    - `methodology_version` column added to every derived Parquet row (GOV-02 provenance-per-row). Propagates from `src/uk_subsidy_tracker/counterfactual.py::METHODOLOGY_VERSION = "0.1.0"` (unchanged; bump is Phase 6+).
    ```

    Do NOT add a `## Methodology versions` entry — the constant stays at
    `"0.1.0"`.
  </action>
  <verify>
    <automated>grep -q "schemes/cfd" CHANGES.md &amp;&amp; grep -q "test_determinism" CHANGES.md &amp;&amp; grep -q "D-19\|D-20\|D-21\|D-22" CHANGES.md &amp;&amp; uv run mkdocs build --strict</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "schemes/cfd\|schemes/__init__" CHANGES.md` ≥ 1
    - `grep -q "SchemeModule" CHANGES.md` exits 0 OR `grep -q "§6.1" CHANGES.md` exits 0
    - `grep -q "test_determinism" CHANGES.md` exits 0
    - `grep -q "TEST-02\|TEST-03\|TEST-05" CHANGES.md` exits 0 (at least one req ID cited)
    - `grep -q "methodology_version" CHANGES.md` exits 0 (GOV-02 propagation noted)
    - `! grep -q "^## Methodology versions$" CHANGES.md | grep -c "0.2.0\|1.0.0"` — no new methodology version entry
    - `uv run mkdocs build --strict` exits 0
  </acceptance_criteria>
  <done>CHANGES.md records derived layer + scheme contract + test-class formalisation (TEST-02/03/05).</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| raw CSV → derived Parquet (`rebuild_derived`) | Type conversion + aggregation. A malformed CSV (non-numeric payment column, duplicated station_id) becomes a malformed Parquet without loader-owned pandera validation at the derivation step. |
| counterfactual.METHODOLOGY_VERSION → Parquet column → manifest.json | End-to-end methodology-version propagation. A skipped version-stamp step leaks a mis-labelled figure to external consumers. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-04-03-01 | Tampering | Derivation silently drops rows via groupby NaN keys | mitigate | `test_annual_vs_station_month_parquet` + `test_by_tech_vs_annual_parquet` + `test_by_round_vs_annual_parquet` use `pd.testing.assert_series_equal` (exact equality). Per Phase 2 D-row-conservation precedent. |
| T-04-03-02 | Tampering | Derivation introduces non-determinism (clock / random / groupby sort) | mitigate | `tests/test_determinism.py` parametrised across all five grains via `pyarrow.Table.equals()`. Every `groupby` in schemes/cfd/* uses explicit `sort=True`. Pitfall 1 (`no datetime.now() in rebuild_derived`) enforced by grep in acceptance criteria. |
| T-04-03-03 | Tampering | Parquet writer default shifts between pandas versions (column encoding, compression) | mitigate | Pinned `version="2.6"`, `compression="snappy"`, `use_dictionary=True`, `write_statistics=True`, `data_page_size=1MB` in the shared `_write_parquet()` helper (D-22). Writer identity test `test_file_metadata_created_by_is_pyarrow` surfaces any engine migration. |
| T-04-03-04 | Information Disclosure | A derived Parquet ends up containing row-level PII because a column not scrubbed | accept | Source data is 100% UK gov open data (LCCC CfD unit IDs + regulator publications). No PII vector. StationMonthRow lists every field explicitly — new columns must pass Pydantic model update, which is grep-visible in review. |
| T-04-03-05 | Repudiation | A derived figure is disputed, but we cannot prove which METHODOLOGY_VERSION produced it | mitigate | `methodology_version` column on every derived row; `emit_schema_json` captures the contract; Plan 04 surfaces the version on `manifest.json::methodology_version`. Triple-redundant provenance stamp. |
| T-04-03-06 | Denial of Service | `rebuild_derived()` is O(N^2) in station count and blocks the CI refresh | accept | CfD station count is <200; pandas groupby is <1 sec on the full dataset. Performance is monitoring-only; not a Phase 4 correctness concern. Phase 8 (NESO BM half-hourly) may trigger this threat for other schemes. |
</threat_model>

<verification>
Phase-4 Plan 03 verifications (automated):

1. `uv run pytest tests/test_determinism.py -v` — 10 passed (5 content + 5 writer)
2. `uv run pytest tests/test_schemas.py -v` — 5 raw-CSV + 5 Parquet parametrised = ≥10 passed
3. `uv run pytest tests/test_aggregates.py -v` — 2 raw + 3 Parquet = 5 passed
4. `uv run pytest tests/` — full suite green
5. `uv run python -c "from uk_subsidy_tracker.schemes import cfd, SchemeModule; assert isinstance(cfd, SchemeModule)"` — Protocol conformance
6. `uv run python -m uk_subsidy_tracker.plotting` — D-02 charts untouched (still work)
7. `uv run mkdocs build --strict` — docs still build
8. No non-determinism sources: `! grep -rE "datetime\.now|time\.time|random\." src/uk_subsidy_tracker/schemes/cfd/` (exit 1 = acceptance)

Manual (post-task):
- Regression probe: edit one derivation constant, observe determinism/conservation test failing, revert.
</verification>

<success_criteria>
- `cfd.rebuild_derived()` produces 5 Parquet files + 5 schema.json siblings under data/derived/cfd/ (or passed output_dir)
- TEST-02 formalised: Parquet-variant tests in `tests/test_schemas.py` validate each grain against its Pydantic model
- TEST-03 formalised: Parquet row-conservation tests in `tests/test_aggregates.py` pass with exact equality
- TEST-05 formalised: `tests/test_determinism.py` passes 10/10 (content + writer)
- `SchemeModule` Protocol declared in `schemes/__init__.py` and `cfd` module satisfies `isinstance(cfd, SchemeModule)`
- `methodology_version` column on every derived row (GOV-02 propagation chain started)
- Full pytest suite green
- Chart generation + mkdocs-strict build still work (D-02)
- `.gitignore` updated to exclude `data/derived/`
- `CHANGES.md` records derived layer + scheme contract + formalised TEST-02/03/05
</success_criteria>

<output>
After completion, create `.planning/phases/04-publishing-layer/04-03-SUMMARY.md`.
Must include:
- Row counts per grain from one rebuild (e.g. `station_month: 14,832 rows`) — becomes the envelope for Plan 04's `validate()` check
- Time to rebuild all five grains on the CfD data (cheap sanity bound for Phase 4's refresh.yml timeout)
- Note whether any column had to be dropped from Pydantic models vs the interface sketch (column-availability in raw LCCC CSV may force adjustments)
- Confirmation that `isinstance(cfd, SchemeModule)` succeeds (Protocol-conformance smoke)
- Confirmation that a momentary edit to a constant makes the determinism test fail (TDD self-check)
</output>
