# Phase 2: Test & Benchmark Scaffolding - Research

**Researched:** 2026-04-22
**Domain:** Python test scaffolding (pytest 9.x + pandera 0.31 + pandas 3.0) with GitHub Actions CI, formula-pin regression test, methodology versioning, and regulator-native benchmark reconciliation
**Confidence:** HIGH for stack mechanics (Context7-verified); HIGH for LCCC floor source; MEDIUM for external regulator anchors (located, figures cited from secondary summaries)

## Summary

Phase 2 ships four pytest test classes, one GitHub Actions workflow, and a methodology-version constant for the CfD gas counterfactual. The stack is already locked by `pyproject.toml` + `uv.lock`: `pytest 9.0.3`, `pandera 0.31.1`, `pandas 3.0.2`, Python 3.12 floor. None of this is novel — every pattern needed exists in the project's current `tests/data/test_lccc.py` and `src/uk_subsidy_tracker/data/lccc.py`. The unusual deliverable is the **regulator-native benchmark fixture** at `tests/fixtures/benchmarks.yaml`, which Phase 2 seeds with a mandatory LCCC self-reconciliation floor and whatever external anchors the researcher could locate.

**Canonical benchmark sources located (in CONTEXT D-09 priority order):**

1. **LCCC Annual Reports** (annual, mandatory floor). The latest is FY 2024/25, published 16-Sept-2025 at `/documents/293/LCCC_ARA_24-25_11.pdf`. Published aggregate figures are not extractable from the landing page alone — the PDF must be opened to pull the specific £bn figure. Historical ARAs (2023/24) exist.
2. **LCCC Data Portal — `advanced-forecast-ilr-tra` dataset** (quarterly). Publishes a forward-looking 6-month forecast of CfD payments by quarter (two quarterly obligation periods). UUID `21aba9f8-02f3-4898-94f0-c98b4f95142c`. Adds up to a rolling forecast annual total but does not publish a single-row annual aggregate.
3. **Ofgem** (MISSING as a canonical annual-total publisher). Ofgem's role in CfD is price-cap allowance methodology, not aggregate spend publication. The closest we have is "cumulative CfD payments to end-Aug 2024 = £8.9bn" quoted in Ofgem/secondary sources, not a primary transparency dashboard.
4. **OBR (Office for Budget Responsibility)** — discovered as a **regulator-native external anchor** not on CONTEXT D-09 but authoritative. OBR publishes CfD cost forecasts in its Economic & Fiscal Outlook supplementary fiscal tables (quarterly), including RO + CfD spend year-by-year. Secondary reporting cites OBR saying 2024/25 CfD = £2.3bn, RO = £7.8bn.
5. **DESNZ Energy Trends** (quarterly) publishes electricity data but does not publish a specific CfD spend line. The relevant DESNZ document is the November 2025 *LCCC and ESC Operational Costs Consultation 2026-27–2029-30* which does forecast CfD payments by year, but the figures are inside a PDF that WebFetch could not extract.
6. **House of Commons Library CBP-9871 "Contracts for Difference Scheme"** — independent scrutineer briefing. PDF at `researchbriefings.files.parliament.uk/documents/CBP-9871/CBP-9871.pdf`.
7. **NAO** — only located the 2014 "Early contracts for renewable electricity" report (£16.6bn lifetime cost for eight pre-AR1 contracts). No recent CfD-wide audit.

**Primary recommendation:** Ship `test_benchmarks.py` with (a) the LCCC self-reconciliation floor as a mandatory red-line check per CONTEXT D-10; (b) as many OBR / LCCC-ARA external anchors as the implementer can extract from PDFs during execution; and (c) CONTEXT D-11 fallback posture — Phase 2 does NOT block on external anchor availability. Tolerance-rationale discipline is more important than anchor count.

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Test-class scope — pre-Parquet interpretation of TEST-02/03/05**

- **D-01:** TEST-02 (`tests/test_schemas.py`) ships as pandera validation of the current raw CSV sources (LCCC generation, LCCC portfolio, Elexon AGWS, Elexon system prices, ONS gas SAP). Uses the existing `lccc_generation_schema` / `lccc_portfolio_schema` patterns; adds new schemas for Elexon and ONS where absent. File grows into Parquet-schema variants in Phase 4.
- **D-02:** TEST-03 (`tests/test_aggregates.py`) ships as in-memory pandas row-conservation assertions on the current CfD pipeline. Invariant: `sum(payment by year) == sum(payment by year × technology)` across the LCCC daily → monthly → yearly aggregation chain. File grows into Parquet-aggregate variants in Phase 4.
- **D-03:** TEST-05 (`tests/test_determinism.py`) is fully deferred to Phase 4. **No file is created in Phase 2.** Byte-identical Parquet output has no meaning without Parquet writes, which arrive in Phase 4.
- **D-04:** REQ-ID bookkeeping — update `.planning/REQUIREMENTS.md` traceability rows so **TEST-02, TEST-03, TEST-05 move from Phase 2 → Phase 4**. Update `.planning/ROADMAP.md` Phase 2 requirements list (drop TEST-02/03/05), Phase 4 requirements list (add TEST-02/03/05), and Phase 2 success criterion 1 (reword from "all five test classes present and passing" to **"four test classes present and passing: `test_counterfactual.py`, `test_schemas.py`, `test_aggregates.py`, `test_benchmarks.py`"**).

**Benchmark format (TEST-04)**

- **D-05:** Benchmark values live in `tests/fixtures/benchmarks.yaml`. Structure per entry: `source`, `year`, `value_gbp_bn`, `url`, `retrieved_on`, `notes`, `tolerance_pct`. A Pydantic model validates the YAML on load.
- **D-06:** Tolerances live as named constants in `tests/test_benchmarks.py` (e.g., `LCCC_SELF_TOLERANCE_PCT = 0.1`, `DESNZ_ANNUAL_TOLERANCE_PCT = 5.0`) with docstring rationale.
- **D-07:** A tolerance bump requires a `CHANGES.md` entry under `## Methodology versions` explaining the rationale.
- **D-08:** **Ben Pile and Dav Turver are NOT canonical benchmark sources.** Phase 2 canon is UK regulator / audit-grade publications.
- **D-09:** Researcher source prioritisation, in order: LCCC → Ofgem → DESNZ/BEIS → NAO/HoC Library/CCC.
- **D-10:** **LCCC self-reconciliation is a mandatory red-line check.** `abs(our - lccc) / lccc <= 0.001` (0.1%). Always green, always included, never parameterised away.
- **D-11:** Fallback posture — if researcher cannot locate external anchors beyond LCCC, ship `test_benchmarks.py` with the LCCC floor only. Phase 2 does NOT block on external anchor availability.

### Claude's Discretion

- **CI workflow shape (TEST-06):** single-job GitHub Actions workflow at `.github/workflows/ci.yml`, on push to `main` + pull_request, Python 3.12 only, `astral-sh/setup-uv@v4` (research recommends **v8**, see below) with built-in cache, `uv sync --frozen` then `uv run pytest`. No ruff/pyright/mkdocs-strict gate in Phase 2.
- **Methodology versioning (GOV-04):** `METHODOLOGY_VERSION: str = "1.0.0"` as module-level constant in `src/uk_subsidy_tracker/counterfactual.py`, returned as a column in the DataFrame. SemVer semantics: patch = tolerance/constant tweak; minor = additive parameter; major = formula-shape change. `CHANGES.md` seeds `## Methodology versions` → `### 1.0.0 — 2026-04-22 — Initial formula`.
- **Pin test mechanics:** hardcoded expected float to 4 decimal places. Sample inputs: 2022 + 2019 slices + synthetic all-zeros.
- **Benchmark YAML schema location:** Pydantic model in `tests/fixtures/__init__.py` OR `tests/conftest.py`.

### Deferred Ideas (OUT OF SCOPE)

- `tests/test_determinism.py` (Phase 4).
- Parquet-variant checks in `test_schemas.py` / `test_aggregates.py` (Phase 4).
- `mkdocs build --strict` as a CI gate (Phase 3 owns the doc restructure).
- ruff, pyright, pre-commit hooks (Phase 3+).
- Daily-refresh CI workflow with 06:00 UTC cron (Phase 4, GOV-03).
- Multi-scheme benchmark reconciliations (later scheme phases).
- Coverage reports.
- Benchmark drift monitoring.
- Ben Pile / Turver commentator reconciliations — if ever added, under a `commentators:` key flagged "non-canonical."

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TEST-01 | `tests/test_counterfactual.py` pins the gas counterfactual formula against known inputs | §"Formula Pinning Pattern"; pandas/python version lock confirmed; synthetic sample inputs computed below |
| TEST-02 | `tests/test_schemas.py` validates raw CSV sources via pandera (pre-Parquet variant; Parquet variant in Phase 4) | §"Pandera 0.31 Patterns"; existing `lccc_generation_schema` / `lccc_portfolio_schema` reusable; Elexon + ONS need new schemas |
| TEST-03 | `tests/test_aggregates.py` in-memory row-conservation on current CfD pipeline | §"Aggregate Invariants"; CSV-derived annual totals computed below; groupby-sum idiom established |
| TEST-04 | `tests/test_benchmarks.py` reconciles CfD totals against LCCC self-reconciliation + regulator-native anchors | §"Benchmark Sources" — 4 sources located with URLs and cadence |
| TEST-05 | **MOVED TO PHASE 4** per D-04 | N/A in Phase 2 |
| TEST-06 | GitHub Actions CI workflow runs pytest on push to main + pull_request | §"GitHub Actions + uv Integration"; `astral-sh/setup-uv@v8` + `uv run --frozen pytest`; cache auto-keyed on `uv.lock` |
| GOV-04 | `counterfactual.py` carries `METHODOLOGY_VERSION`; `CHANGES.md` logs initial version | §"Methodology Versioning"; CHANGES.md hook already seeded at `## Methodology versions` header |

## Project Constraints (from CLAUDE.md)

- **Python 3.12+ only.** No Rust, no Go, no Polars migration, no non-Python frameworks.
- **Analytical engine: Parquet + DuckDB.** No relational DB. (Phase 2 doesn't touch this — it ships tests against CSV.)
- **Hosting: Cloudflare Pages only.** No backend, no containers, no workflow engines beyond GitHub Actions cron.
- **Provenance non-negotiable.** Every Parquet file carries source hash, retrieval timestamp, pipeline git SHA. (Phase 2 doesn't produce Parquet — this is a Phase 4 concern — but `tests/fixtures/benchmarks.yaml` inherits the ethos: every benchmark entry carries `url` + `retrieved_on`.)
- **Reproducibility:** `git clone` + `uv sync` + one command must reproduce every published number byte-identically. CI must use `--frozen` / `--locked` sync.
- **Adversarial-proofing:** Every PRODUCTION chart = narrative + methodology + test + source-file link. Phase 2 establishes the test leg of this contract for CfD.
- **File size ≤ 100 MB for git commits.** Current raw CSVs (LCCC 104k rows, Elexon AGWS 475k rows, Elexon system prices 163k rows) stay in git; CI has them available without network.
- **All sources UK government open data.** Benchmarks sourced accordingly.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Formula pin (counterfactual) | Python source (`src/uk_subsidy_tracker/counterfactual.py`) + `tests/test_counterfactual.py` | CHANGES.md | Constant lives in source; assertion lives in test; methodology log lives in CHANGES.md |
| CSV schema validation | `tests/test_schemas.py` + existing schemas in `src/uk_subsidy_tracker/data/*.py` | — | Tests call loader functions that run `schema.validate()` internally; test asserts loader succeeds and re-validates edge fields |
| Row-conservation aggregates | `tests/test_aggregates.py` | `src/uk_subsidy_tracker/data/lccc.py` (loader) | Test owns invariants; loader is read-only source of truth |
| Benchmark reconciliation | `tests/test_benchmarks.py` + `tests/fixtures/benchmarks.yaml` + Pydantic model | LCCC data + `compute_counterfactual` are unused here | Test computes aggregates from CSV, compares against YAML fixture |
| Methodology versioning | `src/uk_subsidy_tracker/counterfactual.py` (constant) + `compute_counterfactual()` (returns column) + `CHANGES.md` (log) | Future: `manifest.json` (Phase 4, GOV-02) | Constant-in-source means SemVer PR diffs are grep-friendly; column-in-DataFrame means it flows into derived Parquet downstream |
| CI orchestration | `.github/workflows/ci.yml` | `pyproject.toml` (dependency declaration), `uv.lock` (cache key) | Single-job workflow; uv-managed |

## Standard Stack

### Core (all already in pyproject.toml + uv.lock — no new deps)

| Library | Locked Version | Purpose | Why Standard |
|---------|----------------|---------|--------------|
| pytest | 9.0.3 | Test runner + `@pytest.mark.skip(reason=...)` idiom | Python testing standard; already the project runner `[VERIFIED: uv.lock, tests pass]` |
| pandera | 0.31.1 | DataFrame schema validation via `pa.DataFrameSchema({...})` | Already used by `data/lccc.py`; canonical import is `import pandera.pandas as pa` per pandera 0.24+ migration `[CITED: pandera migration docs]` |
| pandas | 3.0.2 | DataFrame aggregation in `test_aggregates.py` | Already the project's DataFrame lib `[VERIFIED: uv.lock]` |
| pydantic | 2.13.3 | BaseModel for benchmarks.yaml loader + LCCCAppConfig pattern | Already used by `LCCCAppConfig` — mirror that idiom `[VERIFIED: data/lccc.py lines 16-32]` |
| pyyaml | 6.0.3 | Parsing `tests/fixtures/benchmarks.yaml` | Already used by `load_lccc_config()`; use `yaml.safe_load()` `[VERIFIED: data/lccc.py line 81]` |

### Supporting (already declared; no changes)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| numpy | (pandas-bundled) | Floating-point comparison with `np.isclose` | In pin-test + benchmark tolerance checks |
| openpyxl | declared | Reading `ons_gas_sap.xlsx` during `test_schemas.py` | Already used by `data/ons_gas.py` |

### GitHub Actions

| Action | Recommended Pin | Purpose |
|--------|-----------------|---------|
| `actions/checkout` | `@v5` | Check out code `[CITED: astral-sh/setup-uv README example]` |
| `astral-sh/setup-uv` | `@v8` (latest stable as of 2026-04-16, v8.1.0) | Install uv, configure Python, enable cache `[CITED: astral-sh/setup-uv README]` |

**Version verification (2026-04-22):**
```
pandera: 0.31.1  (published 2026-04-15)
pytest: 9.0.3    (published 2026-04-07)
pandas: 3.0.2    (published 2026-03-31)
pyyaml: 6.0.3    (published 2025-09-25)
pydantic: 2.13.3 (published 2026-04-20)
```

**CONTEXT.md note:** CONTEXT suggests `astral-sh/setup-uv@v4`. Research recommends upgrading to `@v8` (current stable per upstream README, April 2026). Not a blocking decision — `v4` still works — but `@v8` includes the `cache-dependency-glob` defaults that hash `uv.lock` + `pyproject.toml` automatically, which is what we want.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `uv run --frozen pytest` | `uv sync --locked` then `uv run pytest` | Equivalent; `--frozen` forbids lockfile updates, `--locked` verifies lockfile matches `pyproject.toml`. Both fail CI on drift. Use `--frozen` to mirror the setup-uv README example. `[CITED: astral-sh/setup-uv README]` |
| Pydantic model for benchmarks YAML | Raw dict loaded by `yaml.safe_load` | Pydantic gives validation + type errors pointing at the offending field; matches project `LCCCAppConfig` pattern (D-05 commits to Pydantic). |
| Benchmark YAML | Benchmark TOML / inline Python dicts | YAML preferred per D-05 for PR-diff readability and to surface retrieval metadata (provenance). |
| Separate benchmark test file per source | Single `test_benchmarks.py` parametrised by source | Single file with parametrised tests keeps the test surface flat (~100 lines per §9.6 target). |

**Installation:** No new deps. Phase 2 confirms `uv sync --frozen` installs everything already.

## Architecture Patterns

### System Architecture Diagram

```
Developer push / PR                  Test run (local or CI)
       │                                      │
       ▼                                      ▼
 ┌──────────────────┐            ┌──────────────────────────┐
 │ .github/workflows│            │   uv run --frozen pytest │
 │      ci.yml      │            └─────────────┬────────────┘
 └────────┬─────────┘                          │
          │ triggers                           │
          ▼                                    ▼
 ┌────────────────────┐       ┌─────────────────────────────────────┐
 │ setup-uv@v8        │       │ pytest discovers tests/             │
 │  + Python 3.12     │       │  ├── data/ (existing)               │
 │  + cache uv.lock   │       │  ├── test_counterfactual.py  [new]  │
 └────────┬───────────┘       │  ├── test_schemas.py         [new]  │
          │                   │  ├── test_aggregates.py      [new]  │
          ▼                   │  ├── test_benchmarks.py      [new]  │
 ┌────────────────────┐       │  └── fixtures/               [new]  │
 │ uv sync --frozen   │       │      ├── __init__.py               │
 │ (installs deps)    │       │      └── benchmarks.yaml           │
 └────────┬───────────┘       └──────────────┬──────────────────────┘
          │                                  │
          ▼                                  ▼
       ╔══════════════════════════════════════════════╗
       ║  test_counterfactual.py                      ║
       ║    import from uk_subsidy_tracker.           ║
       ║      counterfactual (METHODOLOGY_VERSION,    ║
       ║      compute_counterfactual, constants)      ║
       ║    assert_almost_equal(result, 39.6327, 4)   ║
       ║                                              ║
       ║  test_schemas.py                             ║
       ║    from uk_subsidy_tracker.data import       ║
       ║      load_lccc_dataset, load_gas_price, ...  ║
       ║    each loader runs schema.validate()        ║
       ║                                              ║
       ║  test_aggregates.py                          ║
       ║    df = load_lccc_dataset(...)               ║
       ║    assert year_sum == year_tech_sum          ║
       ║                                              ║
       ║  test_benchmarks.py                          ║
       ║    benchmarks = load_benchmarks_fixture()    ║
       ║    for entry: compute our_total,             ║
       ║      assert within tolerance_pct             ║
       ║    LCCC self-reconciliation: RED LINE        ║
       ╚══════════════════════════════════════════════╝
                           │
                           ▼
               pass / fail reported to GitHub
               (PR check, main-branch status)

Metadata flow (GOV-04):
  METHODOLOGY_VERSION = "1.0.0"  in counterfactual.py
     │
     ├─► returned as DataFrame column by compute_counterfactual()
     │     (so it flows into Phase-4 derived Parquet + Phase-4 manifest.json)
     │
     └─► logged in CHANGES.md ## Methodology versions
           ### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)
```

### Recommended Project Structure

```
.github/
  workflows/
    ci.yml                          # NEW (Phase 2, TEST-06)
src/uk_subsidy_tracker/
  counterfactual.py                 # MODIFIED: add METHODOLOGY_VERSION + return-column
  data/
    lccc.py                         # UNCHANGED (schemas already exist)
    elexon.py                       # MODIFIED: add pandera schema alongside loader
    ons_gas.py                      # MODIFIED: add pandera schema alongside loader
tests/
  __init__.py                       # optional, only if pytest collection demands it (current tree has none)
  conftest.py                       # OPTIONAL (see D-05 location discretion)
  data/
    test_lccc.py                    # UNCHANGED
    test_ons.py                     # UNCHANGED
  fixtures/                         # NEW
    __init__.py                     # Pydantic benchmark loader (recommended location)
    benchmarks.yaml                 # NEW
  test_counterfactual.py            # NEW (TEST-01 + GOV-04 pin-test)
  test_schemas.py                   # NEW (TEST-02 scaffolding)
  test_aggregates.py                # NEW (TEST-03 scaffolding)
  test_benchmarks.py                # NEW (TEST-04)
CHANGES.md                          # MODIFIED: fill ## Methodology versions + Unreleased note
.planning/REQUIREMENTS.md           # MODIFIED: TEST-02/03/05 Phase 2 → Phase 4
.planning/ROADMAP.md                # MODIFIED: Phase 2 criterion 1 reword; criterion 3 re-anchor; req lists
```

### Pattern 1: Methodology-Version Constant + DataFrame Column

**What:** Module-level `METHODOLOGY_VERSION: str = "1.0.0"` in `counterfactual.py`. `compute_counterfactual()` returns it as a column on the output DataFrame so it flows into Phase-4 Parquet and Phase-4 `manifest.json`.

**When to use:** GOV-04 — single cross-cutting formula, SemVer-disciplined.

**Example:**
```python
# src/uk_subsidy_tracker/counterfactual.py
# Source: CONTEXT D-05 + ARCHITECTURE §9.4

METHODOLOGY_VERSION: str = "1.0.0"
"""Semantic version for the gas counterfactual formula.

- patch: tolerance/constant tweak (e.g., new DEFAULT_CARBON_PRICES entry).
- minor: additive parameter (e.g., new kwarg with default preserving old calls).
- major: formula-shape change (new/dropped term, changed unit).

Bumps require a CHANGES.md entry under ## Methodology versions.
"""

def compute_counterfactual(...) -> pd.DataFrame:
    ...
    df["counterfactual_total"] = (
        df["gas_fuel_cost"] + df["carbon_cost"] + df["plant_opex"]
    )
    df["methodology_version"] = METHODOLOGY_VERSION  # NEW
    return df
```

### Pattern 2: Formula Pin Test (TEST-01)

**What:** Assert `compute_counterfactual(known_inputs)["counterfactual_total"]` matches hardcoded expected floats to 4 decimal places. Any change to `CCGT_EFFICIENCY`, `GAS_CO2_INTENSITY_THERMAL`, `DEFAULT_NON_FUEL_OPEX`, `DEFAULT_CARBON_PRICES` fails the test.

**Known-good expected values** (computed 2026-04-22 against current constants):

| Input date | `gas_p_per_kwh` | Expected `counterfactual_total` (£/MWh) |
|------------|-----------------|-----------------------------------------|
| 2019-01-01 | 1.5 | 39.6327 |
| 2019-06-01 | 1.2 | 34.1782 |
| 2022-10-01 | 8.0 | 168.1855 |

**Zero-input regression check:** `gas_p_per_kwh = 0.0`, date = 2019-01-01 → `gas_fuel_cost=0, carbon_cost=7.3600, plant_opex=5.0, counterfactual_total=12.3600`.

**Example:**
```python
# tests/test_counterfactual.py
# Source: phase research 2026-04-22; values verified against current constants

import pandas as pd
import pytest

from uk_subsidy_tracker.counterfactual import (
    METHODOLOGY_VERSION,
    compute_counterfactual,
)


def test_methodology_version_present():
    """GOV-04: the version constant is importable and SemVer-shaped."""
    assert isinstance(METHODOLOGY_VERSION, str)
    parts = METHODOLOGY_VERSION.split(".")
    assert len(parts) == 3 and all(p.isdigit() for p in parts)


def test_methodology_version_in_output():
    """GOV-04: the column flows into the DataFrame so it reaches Parquet/manifest."""
    gas = pd.DataFrame({
        "date": pd.to_datetime(["2019-01-01"]),
        "gas_p_per_kwh": [1.5],
    })
    df = compute_counterfactual(gas_df=gas)
    assert "methodology_version" in df.columns
    assert (df["methodology_version"] == METHODOLOGY_VERSION).all()


@pytest.mark.parametrize(
    "date_str, gas_p_per_kwh, expected",
    [
        ("2019-01-01", 1.5, 39.6327),
        ("2019-06-01", 1.2, 34.1782),
        ("2022-10-01", 8.0, 168.1855),
        ("2019-01-01", 0.0, 12.3600),  # zero-gas regression
    ],
)
def test_counterfactual_pin(date_str, gas_p_per_kwh, expected):
    """TEST-01: pin the formula. Any constant change fails this test
    and forces a METHODOLOGY_VERSION bump + CHANGES.md entry."""
    gas = pd.DataFrame({
        "date": pd.to_datetime([date_str]),
        "gas_p_per_kwh": [gas_p_per_kwh],
    })
    df = compute_counterfactual(gas_df=gas)
    actual = df["counterfactual_total"].iloc[0]
    assert round(actual, 4) == expected, (
        f"Formula changed for {date_str} gas={gas_p_per_kwh}: "
        f"expected {expected}, got {round(actual, 4)}. "
        f"If intentional, bump METHODOLOGY_VERSION and add a "
        f"CHANGES.md ## Methodology versions entry."
    )
```

### Pattern 3: Pandera 0.31 Schema Validation (TEST-02 scaffolding)

**Canonical import (verified):** `import pandera.pandas as pa` — NOT `import pandera as pa` (FutureWarning since 0.24, deprecated 0.29+). `[VERIFIED: data/lccc.py line 6 already uses this]`

**What:** Each raw dataset has a pandera `DataFrameSchema`; the loader calls `schema.validate(df)`; the test calls the loader and asserts shape + key columns.

**Reuse:** `lccc_generation_schema` + `lccc_portfolio_schema` already exist in `data/lccc.py`. Elexon + ONS need sibling schemas.

**Example (new sibling schema — to add in `data/elexon.py`):**
```python
# src/uk_subsidy_tracker/data/elexon.py
# Source: pandera 0.31 docs via Context7 [VERIFIED: context7 /unionai-oss/pandera]

import pandera.pandas as pa

elexon_agws_schema = pa.DataFrameSchema(
    {
        "settlementDate": pa.Column("datetime64[ns]", coerce=True),
        "settlementPeriod": pa.Column(int, coerce=True),
        "businessType": pa.Column(str),
        "quantity": pa.Column(float, nullable=True, coerce=True),
    },
    strict=False,  # source may have extra cols we don't model
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

**Example (test):**
```python
# tests/test_schemas.py
# Source: ARCHITECTURE §9.6 + CONTEXT D-01

from uk_subsidy_tracker.data import load_gas_price, load_lccc_dataset


def test_lccc_generation_schema_validates():
    """TEST-02 scaffolding (pre-Parquet). Formal TEST-02 in Phase 4."""
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    # schema.validate() already ran inside the loader; assert it returned data
    assert not df.empty
    assert "CFD_Payments_GBP" in df.columns
    assert df["Settlement_Date"].dtype.kind == "M"  # datetime64


def test_ons_gas_schema_validates():
    df = load_gas_price()
    assert not df.empty
    assert "gas_p_per_kwh" in df.columns
    assert df["gas_p_per_kwh"].dtype.kind == "f"
```

### Pattern 4: Row-Conservation Aggregate Invariant (TEST-03 scaffolding)

**What:** For the current CfD pipeline, prove `sum(payment grouped by year) == sum(payment grouped by year × technology)`.

**Derived reference values** (computed 2026-04-22 directly from the committed raw CSV):

| Year | Total CfD payments (£bn, calendar year) |
|------|----------------------------------------|
| 2016 | 0.011 |
| 2017 | 0.420 |
| 2018 | 0.903 |
| 2019 | 1.496 |
| 2020 | 2.296 |
| 2021 | 0.997 |
| 2022 | **-0.346** (generators paid back during gas-price crisis — a real feature) |
| 2023 | 1.394 |
| 2024 | 2.360 |
| 2025 | 2.641 |
| 2026 (YTD) | 0.864 |

The cumulative to end-2024 is ~£9.6bn — broadly consistent with Ofgem's quoted "~£8.9bn cumulative to end-Aug 2024" (~£0.7bn of Sep-Dec 2024 payments accounts for the delta). This is a healthy sanity check on our own pipeline before we even build the fixture.

**Example:**
```python
# tests/test_aggregates.py
# Source: CONTEXT D-02

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

### Pattern 5: Benchmark YAML + Pydantic Loader (TEST-04)

**What:** `tests/fixtures/benchmarks.yaml` carries one top-level key per source; Pydantic validates on load; `test_benchmarks.py` parametrises a reconciliation test across entries.

**YAML shape:**
```yaml
# tests/fixtures/benchmarks.yaml

lccc_self:
  # LCCC's own published aggregate totals. Red-line check per CONTEXT D-10.
  # Tolerance 0.1% — we read LCCC raw data, so this must reconcile.
  - year: 2024
    value_gbp_bn: 2.40        # PLACEHOLDER — extract from LCCC ARA 2024/25 PDF during execution
    url: "https://www.lowcarboncontracts.uk/documents/293/LCCC_ARA_24-25_11.pdf"
    retrieved_on: "2026-04-22"
    notes: "LCCC Annual Report & Accounts 2024/25, published 16-Sep-2025. Calendar year 2024 CfD payments aggregate. Extract from PDF financial statements."
    tolerance_pct: 0.1

obr_efo:
  # OBR Economic & Fiscal Outlook supplementary tables. Forward forecasts + outturn.
  - year: 2024
    value_gbp_bn: 2.3
    url: "https://obr.uk/efo/economic-and-fiscal-outlook-november-2025/"
    retrieved_on: "2026-04-22"
    notes: "OBR quoted 2024/25 CfD = £2.3bn (financial year). Pipeline gives calendar-year 2024 = £2.36bn. Tolerance widened to allow FY-vs-CY mismatch."
    tolerance_pct: 5.0

hoc_library:
  # House of Commons Library CBP-9871. Independent scrutineer briefing.
  - year: 2024
    value_gbp_bn: 2.4
    url: "https://researchbriefings.files.parliament.uk/documents/CBP-9871/CBP-9871.pdf"
    retrieved_on: "2026-04-22"
    notes: "CBP-9871 Contracts for Difference Scheme briefing. Extract exact figures from PDF during execution."
    tolerance_pct: 5.0
```

**Pydantic model (in `tests/fixtures/__init__.py`):**
```python
# tests/fixtures/__init__.py
# Source: CONTEXT D-05; mirrors LCCCAppConfig pattern from data/lccc.py

from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, HttpUrl


class BenchmarkEntry(BaseModel):
    year: int = Field(..., ge=2015, le=2050)
    value_gbp_bn: float
    url: HttpUrl
    retrieved_on: date
    notes: str
    tolerance_pct: float = Field(..., gt=0)


class Benchmarks(BaseModel):
    lccc_self: list[BenchmarkEntry] = []
    obr_efo: list[BenchmarkEntry] = []
    hoc_library: list[BenchmarkEntry] = []
    ofgem_transparency: list[BenchmarkEntry] = []
    desnz_consultation: list[BenchmarkEntry] = []
    nao: list[BenchmarkEntry] = []

    def all_entries(self) -> list[tuple[str, BenchmarkEntry]]:
        out: list[tuple[str, BenchmarkEntry]] = []
        for src in ["lccc_self", "obr_efo", "hoc_library",
                    "ofgem_transparency", "desnz_consultation", "nao"]:
            for entry in getattr(self, src):
                out.append((src, entry))
        return out


def load_benchmarks() -> Benchmarks:
    path = Path(__file__).parent / "benchmarks.yaml"
    with open(path) as f:
        raw = yaml.safe_load(f) or {}
    return Benchmarks(**raw)
```

**Test file skeleton:**
```python
# tests/test_benchmarks.py
# Source: CONTEXT D-05, D-06, D-10; research 2026-04-22

import pytest

from tests.fixtures import BenchmarkEntry, load_benchmarks
from uk_subsidy_tracker.data import load_lccc_dataset

# Per-source tolerances (D-06). Rationale in docstrings, not inline magic numbers.
LCCC_SELF_TOLERANCE_PCT = 0.1
"""Red line per CONTEXT D-10. We read LCCC raw data. A divergence here is a pipeline bug."""

OBR_EFO_TOLERANCE_PCT = 5.0
"""OBR reports financial-year figures; we report calendar-year. April-March vs Jan-Dec adds
quarterly-roll-over skew. Carbon-price CPI basis may also differ."""

HOC_LIBRARY_TOLERANCE_PCT = 5.0
"""CBP briefings may cite quarterly snapshots or rounded figures. Loose tolerance."""


@pytest.fixture(scope="module")
def annual_totals_gbp_bn() -> dict[int, float]:
    """Compute our pipeline's calendar-year CfD payment totals in £bn."""
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df["year"] = df["Settlement_Date"].dt.year
    by_year = df.groupby("year")["CFD_Payments_GBP"].sum()
    return (by_year / 1e9).to_dict()


def test_lccc_self_reconciliation_floor(annual_totals_gbp_bn):
    """CONTEXT D-10 red line: LCCC self-reconciliation MUST hold within 0.1%.
    A failure here is a pipeline bug, not a methodology divergence."""
    benchmarks = load_benchmarks()
    assert benchmarks.lccc_self, "LCCC self-reconciliation floor is mandatory (D-10)"
    for entry in benchmarks.lccc_self:
        ours = annual_totals_gbp_bn.get(entry.year)
        assert ours is not None, f"No pipeline data for year {entry.year}"
        divergence = abs(ours - entry.value_gbp_bn) / entry.value_gbp_bn
        assert divergence <= LCCC_SELF_TOLERANCE_PCT / 100, (
            f"LCCC self-reconciliation FLOOR breached for {entry.year}: "
            f"ours={ours:.3f}, LCCC-published={entry.value_gbp_bn:.3f}, "
            f"divergence={divergence*100:.3f}% > {LCCC_SELF_TOLERANCE_PCT}%. "
            f"This is a pipeline bug, not a methodology divergence."
        )


def _iter_external(benchmarks):
    for src in ["obr_efo", "hoc_library", "ofgem_transparency",
                "desnz_consultation", "nao"]:
        for entry in getattr(benchmarks, src):
            yield src, entry


@pytest.mark.parametrize("source_entry", [
    pytest.param(se, id=f"{se[0]}-{se[1].year}")
    for se in _iter_external(load_benchmarks())
])
def test_external_benchmark_within_tolerance(source_entry, annual_totals_gbp_bn):
    source, entry = source_entry
    tolerance = {
        "obr_efo": OBR_EFO_TOLERANCE_PCT,
        "hoc_library": HOC_LIBRARY_TOLERANCE_PCT,
    }.get(source, 5.0)

    ours = annual_totals_gbp_bn.get(entry.year)
    assert ours is not None, f"No pipeline data for year {entry.year}"
    divergence = abs(ours - entry.value_gbp_bn) / entry.value_gbp_bn
    assert divergence <= tolerance / 100, (
        f"{source} {entry.year}: ours={ours:.3f}, published={entry.value_gbp_bn:.3f}, "
        f"divergence={divergence*100:.2f}% > {tolerance}%. "
        f"Action: (a) fix pipeline, (b) document divergence in CHANGES.md, "
        f"or (c) bump tolerance with rationale."
    )
```

### Pattern 6: GitHub Actions + uv Integration (TEST-06)

**Canonical workflow** `[VERIFIED: astral-sh/setup-uv README + uv integration docs via Context7-adjacent lookup]`:

```yaml
# .github/workflows/ci.yml
# Source: https://github.com/astral-sh/setup-uv (v8.1.0 example, 2026-04-16)
#         https://docs.astral.sh/uv/guides/integration/github/

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
          # cache-dependency-glob defaults to uv.lock + pyproject.toml,
          # which is exactly the invalidation surface we want.
          python-version: "3.12"

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run tests
        run: uv run --frozen pytest -v
```

**Key verified claims:**
- `astral-sh/setup-uv@v8` is current stable (v8.1.0, April 2026). `[VERIFIED: GitHub README]`
- Default `cache-dependency-glob` includes `uv.lock` and `pyproject.toml`. `[VERIFIED: action inputs docs]`
- `uv sync --frozen` enforces lockfile-only install; fails on drift. `[VERIFIED: uv docs]`
- `uv run --frozen pytest` runs pytest in the synced env without updating the lockfile. `[VERIFIED: setup-uv README example]`
- `python-version: "3.12"` sets `UV_PYTHON` env var; uv installs Python 3.12 if not present. `[VERIFIED: setup-uv README inputs]`

**Alternative `--locked` flag:** The uv integration docs (`docs.astral.sh/uv/guides/integration/github/`) show `uv sync --locked`, which verifies the lockfile matches `pyproject.toml`. `--frozen` is stricter (does not allow any lockfile update). Both fail CI on drift. CONTEXT D-Claude's discretion picks `--frozen`; research concurs — use `--frozen`.

### Anti-Patterns to Avoid

- **`import pandera as pa`** — deprecated since 0.29; emits `FutureWarning`. Always `import pandera.pandas as pa` for pandas DataFrames `[CITED: pandera 0.24 migration]`.
- **`pytest.skip(msg=...)` / `pytest.fail(msg=...)`** — `msg` keyword deprecated. Use `reason=...` `[CITED: pytest deprecation docs]`.
- **Adding `tests/__init__.py`** — not needed for pytest 9 discovery; adding it forces test collection as a package which can break the existing `tests/data/test_lccc.py` imports. Keep tests un-packaged unless a specific import path requires it.
- **Per-source `test_benchmarks_lccc.py` / `test_benchmarks_obr.py`** splits — use `@pytest.mark.parametrize` with the YAML fixture. Keeps one file per ARCHITECTURE §9.6 (~100 lines).
- **Inline floating-point equality** (`assert actual == 39.6327`) — use `round(actual, 4) == expected` or `math.isclose(..., abs_tol=1e-4)`. Floating-point equality is unreliable across platforms.
- **Hand-rolled YAML loader** — use `yaml.safe_load` + Pydantic, mirroring `LCCCAppConfig`. Consistency across the codebase; Pydantic surfaces validation errors at the offending YAML key.
- **Benchmark entries without `retrieved_on` + `url`** — defeats provenance (adversarial-proofing). Pydantic model enforces both.
- **Adding `pyarrow` to deps in Phase 2** — determinism test is deferred to Phase 4 per D-03. Keep `pyproject.toml` untouched.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML parsing + validation for benchmarks.yaml | Custom dict-walker | `pydantic.BaseModel` + `yaml.safe_load` | Matches `LCCCAppConfig` idiom; surfaces per-field errors; handles date/url/float coercion automatically |
| DataFrame schema validation for Elexon/ONS CSVs | Hand-written type checks | `pandera.pandas.DataFrameSchema` with `coerce=True, strict=False` | Already how `data/lccc.py` validates LCCC CSVs. Zero new concepts |
| Floating-point comparison in pin test | `assert a == b` on floats | `round(a, 4) == b` OR `pytest.approx(b, abs=1e-4)` | Float equality fails on platform ABI drift |
| GitHub Actions uv setup | Manual `pip install uv` + `PATH` manipulation | `astral-sh/setup-uv@v8` | Built-in cache keyed on uv.lock; handles uv + Python install in one step; maintained upstream |
| CI cache key derivation | Hand-crafted `${{ hashFiles('uv.lock') }}` | `enable-cache: true` (default glob matches uv.lock + pyproject.toml) | Upstream owns the glob; one breaking change away from biting if we duplicate |
| SemVer parsing in the methodology-version test | `re.match` on the version string | Simple `"1.0.0".split(".")` + `.isdigit()` | Overkill to import packaging. A trivial sanity check, not a full-blown parser |
| Date parsing in YAML | Custom string→date conversion | Pydantic `date` field — yaml.safe_load returns datetime.date natively for `YYYY-MM-DD` strings | Zero code |

**Key insight:** Every tool in this phase already exists in the codebase. Phase 2 is a *pattern replication* phase — not an introduction phase. The only new external dependency is `astral-sh/setup-uv`, and that's a GitHub Action, not a Python package.

## Runtime State Inventory

> Phase 2 is additive (new files + a few targeted modifications). It is not a rename/refactor. But the atomic-commit discipline from Phase 1 creates a runtime-state concern worth noting.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — Phase 2 creates no stored data. Raw CSVs in `data/` are read-only. | None |
| Live service config | None — no n8n/Mem0/Tailscale/SOPS integrations touched. | None |
| OS-registered state | GitHub Actions is not yet configured for this repo (`.github/` does not exist). Phase 2 creates it — so GitHub will start sending workflow status back to the repo on push/PR. The `main` branch protection settings may need updating to require the new `test` check. | User action after first workflow run: optionally add "Require status checks to pass before merging → test" to branch protection via GitHub UI. Not blocking. |
| Secrets/env vars | None — Phase 2 workflow needs no secrets (no deploys, no external APIs in the test path). | None |
| Build artifacts / installed packages | `uv sync --frozen` will install into `.venv/`. Existing `.venv/` was built under the post-rename package `uk_subsidy_tracker` — already clean. | None |

**Nothing found in most categories** — verified by the phase-boundary being "add files, don't mutate runtime state."

## Common Pitfalls

### Pitfall 1: pandera import migration trap
**What goes wrong:** A new contributor writes `import pandera as pa` instead of `import pandera.pandas as pa`. Tests pass locally (old behaviour still supported) but emit `FutureWarning`. Silent drift.
**Why it happens:** Most tutorials on the web still show the old import.
**How to avoid:** Copy the existing `data/lccc.py` import line verbatim when writing new schemas. Reviewer check: grep for `^import pandera as pa` or `^from pandera import` in diffs.
**Warning signs:** Pytest prints `FutureWarning: importing from top-level pandera`.

### Pitfall 2: pandas 3.0 `datetime64[us]` vs `datetime64[ns]`
**What goes wrong:** pandas 3.0 changed the default datetime resolution for string parsing to microseconds (`datetime64[us]`), falling back to ns only when precision requires. A pandera column declared `pa.Column("datetime64[ns]")` may or may not match depending on how the date was constructed. Current LCCC load still returns `datetime64[ns]` because `pd.to_datetime` on CSV strings with ISO format + the way pandas reads the Excel dates both preserve ns (verified 2026-04-22: our `load_lccc_dataset` returns `datetime64[ns]`).
**Why it happens:** Only bites if someone constructs a test DataFrame inline with `pd.to_datetime("2024-01-01")` — that *may* come back `datetime64[us]` under pandas 3.0.
**How to avoid:** In tests, construct datetimes with `pd.to_datetime([...]).as_unit("ns")` when a specific dtype is asserted. Or use `coerce=True` (already set everywhere). Or assert with `df["date"].dtype.kind == "M"` (timezone-family match) rather than the specific unit.
**Warning signs:** SchemaError with message containing `expected datetime64[ns], got datetime64[us]`.
**Mitigation in our code:** All existing schemas use `coerce=True, strict=False` — coercion auto-converts `us → ns`. No action needed unless this rule changes.

### Pitfall 3: Pytest discovery picks up `tests/fixtures/__init__.py` as tests
**What goes wrong:** Pytest walks into `tests/fixtures/` looking for `test_*.py`. If someone later adds a `test_benchmarks_fixture.py` there, it might double-collect.
**Why it happens:** Pytest default `testpaths` is recursive.
**How to avoid:** Pydantic loader lives in `tests/fixtures/__init__.py` (dunder file, not a test file). Benchmark YAML is not a Python file. No `test_*.py` inside `fixtures/`. If you later want to test the Pydantic loader itself, add `tests/test_fixtures.py` at the top level.
**Warning signs:** Pytest discovers tests inside `tests/fixtures/` that weren't intentional.

### Pitfall 4: CI cache staleness when `pyproject.toml` changes but `uv.lock` doesn't
**What goes wrong:** Someone bumps a dep caret in `pyproject.toml` without running `uv lock`. Cache hits on the unchanged `uv.lock`, but `uv sync --frozen` fails because the lockfile no longer satisfies `pyproject.toml`.
**Why it happens:** `cache-dependency-glob` default covers both files, but the failure mode is clean — `--frozen` refuses to sync.
**How to avoid:** The failure is the intended behaviour — it tells the PR author to run `uv lock` + commit the updated lockfile.
**Warning signs:** CI logs show `error: The lockfile at uv.lock needs to be updated…`.

### Pitfall 5: Benchmark tolerance creep
**What goes wrong:** A PR raises `OBR_EFO_TOLERANCE_PCT` from 5.0 to 10.0 to make a failing test pass. No CHANGES.md entry. The fixture value was wrong but nobody notices; divergence is now silent.
**Why it happens:** Tolerances are knobs, and knobs get turned.
**How to avoid:** D-07 requires a CHANGES.md entry under `## Methodology versions` for any tolerance bump. Enforce in PR review. Consider a pre-commit or CI check that greps for tolerance-constant changes + cross-references CHANGES.md in the same PR (deferred to Phase 3+ polish per CONTEXT).
**Warning signs:** PR changes `TOLERANCE_PCT` constants with no matching CHANGES.md diff.

### Pitfall 6: LCCC ARA PDF extraction delivers a financial-year figure, we compare against calendar-year
**What goes wrong:** LCCC publishes FY 2024/25 (April 2024 – March 2025). Our pipeline aggregates calendar year 2024. These are different numbers.
**Why it happens:** UK public-sector financial year is 1-April to 31-March. Our analytical frame is calendar year (ARCHITECTURE §4).
**How to avoid:** YAML `notes` field MUST state "calendar year" vs "financial year" explicitly. Tolerance for FY-vs-CY benchmarks widened to 10-15% or the entry is split into two quarterly-summed entries matching the LCCC FY window. Alternatively: if LCCC ARA publishes *both* a FY total and a CY breakdown, use the CY figure.
**Warning signs:** A benchmark entry passes at 0.1% one year and fails at 3% the next — the likely cause is FY/CY confusion.

### Pitfall 7: Negative payment years (2022) misinterpreted as pipeline bug
**What goes wrong:** A reviewer sees `-0.346 bn` for 2022 and files a correction issue.
**Why it happens:** During the 2022 gas-price crisis, CfD generators PAID BACK money (reference price > strike price, which is exactly what CfDs do). This is a feature of the scheme, not a bug.
**How to avoid:** The 2022 figure should be in `benchmarks.yaml` with a `notes` field explaining the negative value is correct. Methodology page (Phase 3 docs) should explain it.
**Warning signs:** Anyone asks "why does 2022 look weird?" — refer them to the notes field.

### Pitfall 8: CFD_Generation_MWh carries negative values too
**What goes wrong:** Someone writes `assert (df["CFD_Generation_MWh"] >= 0).all()` in `test_schemas.py` or `test_aggregates.py`. It fails.
**Why it happens:** LCCC published data contains correction entries with negative generation figures (revised-down reconciliation). Legitimate.
**How to avoid:** Don't assert non-negativity on generation or payments. The existing `lccc_generation_schema` correctly declares them `nullable=True` without a value check.
**Warning signs:** Schema-test failures citing negative values in columns that "should" be positive.

## Code Examples

### Methodology-version header added to `counterfactual.py`
```python
# src/uk_subsidy_tracker/counterfactual.py
# Source: GOV-04, CONTEXT D-Claude's discretion

METHODOLOGY_VERSION: str = "1.0.0"
"""Semantic version for the gas counterfactual formula.

Bumps require an entry in CHANGES.md under ## Methodology versions.

- PATCH: Constant tweak with identical formula shape (e.g., new year in
  DEFAULT_CARBON_PRICES, refined CCGT_EFFICIENCY from newer BEIS figure).
- MINOR: Additive parameter (new kwarg with default preserving old calls).
- MAJOR: Formula-shape change (new/dropped term, changed unit convention).
"""
```

### CHANGES.md fill-in
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
- `tests/test_benchmarks.py` — LCCC self-reconciliation floor (0.1% tolerance,
  red-line per project governance) + regulator-native external anchors (TEST-04).
- `tests/fixtures/benchmarks.yaml` — structured benchmark values with per-entry
  source, year, URL, retrieval date, notes, and tolerance.
- `tests/fixtures/__init__.py` — Pydantic loader for `benchmarks.yaml`.
- `METHODOLOGY_VERSION` constant in `src/uk_subsidy_tracker/counterfactual.py`
  (GOV-04); `compute_counterfactual()` returns it as a DataFrame column.

### Changed
- `src/uk_subsidy_tracker/data/elexon.py` — added `elexon_agws_schema` and
  `elexon_system_price_schema` pandera DataFrameSchemas.
- `src/uk_subsidy_tracker/data/ons_gas.py` — added `ons_gas_schema`.
- `.planning/REQUIREMENTS.md` — TEST-02, TEST-03, TEST-05 traceability rows
  moved from Phase 2 to Phase 4 (pre-Parquet variants ship in Phase 2 as
  scaffolding but don't formally satisfy those requirements until their
  Parquet variants ship in Phase 4).
- `.planning/ROADMAP.md` — Phase 2 success criterion 1 reworded from
  "five test classes" to "four test classes"; Phase 2 success criterion 3
  re-anchored from Ben Pile / REF / Turver to LCCC self-reconciliation +
  regulator-native sources.

## Methodology versions

### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)
Initial published version of the gas counterfactual formula:
```
counterfactual £/MWh = fuel cost + carbon cost + O&M
  fuel cost   = gas_p_per_kwh * 10 / CCGT_EFFICIENCY
  carbon cost = UK_ETS_£_per_tCO2 * GAS_CO2_INTENSITY_THERMAL / CCGT_EFFICIENCY
  O&M         = DEFAULT_NON_FUEL_OPEX (existing-fleet CCGT, capex sunk)
```
Constants:
- `CCGT_EFFICIENCY = 0.55` (BEIS Electricity Generation Costs 2023, Table ES.1)
- `GAS_CO2_INTENSITY_THERMAL = 0.184` tCO2/MWh thermal (natural gas default)
- `DEFAULT_NON_FUEL_OPEX = 5.0` £/MWh (existing CCGT fleet, capex sunk per
  BEIS 2023 Table ES.1: fixed O&M ~£3/MWh + variable O&M ~£2/MWh)
- `DEFAULT_CARBON_PRICES`: annual averages 2018-2026 (EU ETS 2018-2020
  converted EUR→GBP; UK ETS 2021+ published by GOV.UK)

Affected charts: `cfd_vs_gas_cost`, `bang_for_buck`,
`subsidy_per_avoided_co2_tonne`, `scissors` (pending Phase 3 removal),
`cfd_dynamics` (references `gas_fuel_cost` indirectly via cost decomposition).
```

## Benchmark Sources

**Retrieved 2026-04-22 by `gsd-phase-researcher`.** All sources conform to CONTEXT D-08 canon (UK regulator / audit-grade). Ben Pile, Dav Turver, REF excluded per D-08.

### 1. LCCC Annual Report & Accounts (MANDATORY FLOOR per D-10)

| Field | Value |
|-------|-------|
| Source name | LCCC Annual Report & Accounts |
| Publication | "Low Carbon Contracts Company (LCCC) Annual Report 2024/25" |
| Landing URL | https://www.lowcarboncontracts.uk/resources/guidance-and-publications/low-carbon-contracts-company-lccc-annual-report-202425/ |
| PDF URL | https://www.lowcarboncontracts.uk/documents/293/LCCC_ARA_24-25_11.pdf |
| Publication date | 16 September 2025 |
| Cadence | Annual (follows UK fiscal year end 31 March) |
| Latest figure available | FY 2024/25 "record CfD contracts" (specific £bn requires PDF extraction) |
| Historical | FY 2023/24 ARA also exists at `/electricity-settlements-company-esc-annual-report-20232024/` |
| Tolerance band | **0.1%** (red-line; we read LCCC raw data) |
| Scope caveat | LCCC ARA reports FY figures (Apr-Mar). Our pipeline reports calendar-year. Either (a) restrict the comparison to FY sums from our CSV, or (b) document the FY/CY difference in the YAML `notes` field and widen tolerance. |

**CRITICAL EXECUTION NOTE:** The ARA PDF must be opened and the specific £bn CfD settlement aggregate extracted during Phase 2 execution. This research could not extract it via WebFetch (landing page only). The implementer should note the section/page in the YAML `notes`. `[ASSUMED: Fig exists in PDF; VERIFIED: PDF exists at URL]`

### 2. LCCC Data Portal — Actual CfD Generation (OUR UPSTREAM)

| Field | Value |
|-------|-------|
| Source name | LCCC Data Portal — "Actual CfD Generation and avoided GHG emissions" |
| URL | https://dp.lowcarboncontracts.uk/dataset/actual-cfd-generation-and-avoided-ghg-emissions |
| Cadence | Daily (T+3 to T+7 lag from settlement date) |
| What it publishes | Row-level settlement data (station × day). Our pipeline aggregates. |
| Use in benchmarks | This is our **source** — it cannot be used as an external check. But a publication-cadence check (is the LCCC CSV we ship in git up-to-date?) belongs in Phase 4 (GOV-03 daily refresh). |
| `[VERIFIED: Context7-adjacent WebFetch 2026-04-22]` |

### 3. LCCC Data Portal — Forecast ILR/TRA (forward-looking anchor)

| Field | Value |
|-------|-------|
| Source name | LCCC Forecast ILR/TRA dataset |
| URL | https://dp.lowcarboncontracts.uk/dataset/forecast-ilr-tra |
| UUID | 21aba9f8-02f3-4898-94f0-c98b4f95142c |
| CSV direct | https://dp.lowcarboncontracts.uk/dataset/21aba9f8-02f3-4898-94f0-c98b4f95142c/resource/1cb4eaa6-1108-482d-a84a-1862b880a943/download/forecast_ilr_tra.csv |
| Cadence | Quarterly (updated end of each Quarterly Obligation Period) |
| Columns | Period Start/End, Eligible Demand MWh, Forecast Accrued BMRP/IMRP, Interim Levy Rate, Total Reserve Amount |
| Aggregation to annual | No single annual row. Sum 4 quarters → forward-looking annual forecast. |
| Example (Q4 2025): ILR = £10.298/MWh, TRA = £360,719,889.83 | `[CITED: news.lccc.uk 2025-06-17]` |
| Example (Q3 2025): ILR = £8.812/MWh, TRA = £235,897,859.06 | `[CITED: news.lccc.uk]` |
| Tolerance band | 10% (forecast vs actual) — use sparingly, mostly as a sanity check |
| Use | Forward-year sanity check in Phase 2; becomes GOV-03 refresh input in Phase 4. |

### 4. OBR Economic & Fiscal Outlook (external scrutineer)

| Field | Value |
|-------|-------|
| Source name | Office for Budget Responsibility — Economic & Fiscal Outlook (EFO) |
| Landing URL | https://obr.uk/efo/economic-and-fiscal-outlook-november-2025/ |
| PDF URL (Nov 2025) | https://d1e00ek4ebabms.cloudfront.net/production/uploaded-files/OBR_Economic_and_fiscal_outlook_November_2025-e48e1cf8-cf63-4d3a-aca1-1d6a05d6109f.pdf |
| Cadence | Biannual (spring + autumn, alongside Budget/Autumn Statement) |
| Data format | Supplementary fiscal tables (spreadsheets) alongside each EFO |
| Figures cited by secondary source | 2024/25: CfD = £2.3bn, RO = £7.8bn | `[CITED: IER secondary summary; VERIFIED: OBR is primary and publishes the tables]` |
| Forecast horizon | Typically 5 years forward |
| Tolerance band | **5%** (FY-vs-CY mismatch; OBR uses different price basis in some tables) |
| Notes | OBR is the **strongest regulator-native external anchor we've located**, independent of LCCC. |

**EXECUTION NOTE:** The CfD line in OBR supplementary tables needs specific-page/sheet identification during Phase 2 execution. `[ASSUMED: line item exists in fiscal supplementary spreadsheet]` — confirm by downloading the supplementary workbook from `obr.uk/data/`.

### 5. DESNZ / LCCC Operational Costs Consultation (forecast anchor)

| Field | Value |
|-------|-------|
| Source name | DESNZ "Low Carbon Contracts Company and Electricity Settlements Company operational costs 2026-27 to 2029-30" |
| URL | https://assets.publishing.service.gov.uk/media/69243d7f90a8c154e90261e2/lccc-and-esc-operational-costs-consultation-2026-27-2027-28-2029-30.pdf |
| Publication date | November 2025 |
| Cadence | Ad-hoc (consultations run every 2-3 years) |
| Content | Forecasts CfD payments by year for operating cost period. |
| Tolerance band | 5-10% (government forecast vs reality) |
| Extraction note | WebFetch could not extract figures (PDF stream encoded). Implementer must download and extract manually. `[ASSUMED: contains year-by-year CfD payment forecasts]` — this is standard for such consultations. |

### 6. House of Commons Library CBP-9871 — Contracts for Difference Scheme

| Field | Value |
|-------|-------|
| Source name | HoC Library Research Briefing — "Contracts for Difference Scheme" |
| Paper number | CBP-9871 |
| PDF URL | https://researchbriefings.files.parliament.uk/documents/CBP-9871/CBP-9871.pdf |
| Landing URL | https://commonslibrary.parliament.uk/research-briefings/cbp-9871/ |
| Cadence | Updated on major scheme developments (not fixed schedule) |
| Content | CfD overview, costs to consumers, recent auction results |
| Tolerance band | 5% (briefing cites Ofgem/LCCC/OBR figures at a snapshot; rounding + retrieval-year drift expected) |
| Related briefings | CBP-8891 "Support for low carbon power"; CBP-9888 (March 2026 update) |

### 7. Ofgem (weaker anchor — mostly for context, not a reconcilation target)

| Field | Value |
|-------|-------|
| Source name | Ofgem — CfD supplier-obligation / default tariff cap methodology |
| Relevant URL | https://www.ofgem.gov.uk/sites/default/files/2025-08/Energy-price%20cap-methodology-contracts-for-difference-review-call-for-input.pdf |
| Content | Price-cap methodology; quotes "cumulative CfD payments to end-Aug 2024 = £8.9bn". |
| Use | **Sanity cross-check only**, not a primary benchmark. Ofgem does not publish a standalone CfD annual total dashboard. |
| Tolerance | N/A (cited, not asserted) |

### 8. NAO (only 2014 audit exists)

| Field | Value |
|-------|-------|
| Source name | National Audit Office — "Early contracts for renewable electricity" |
| URL | https://www.nao.org.uk/reports/early-contracts-for-renewable-electricity-2/ |
| Publication date | 2014 |
| Content | Pre-AR1 FID-enabling contracts: £16.6bn lifetime cost. |
| Use | Historical context only. No recent NAO CfD-wide audit located. |
| Tolerance | N/A |

### Not canonical (excluded per D-08)
Net Zero Watch, REF Blog, IER, Turver, Ben Pile — commentators. Ignored.

### What this means for Phase 2 scope

- **LCCC ARA floor is achievable with effort** — PDF extraction by a human during execution. If the extracted figure is not confidence-worthy, fall back to cumulative-to-date from the LCCC daily data portal (which *is* our upstream and thus trivially reconciles).
- **OBR EFO supplementary tables are the strongest external anchor** — implementer downloads the Nov-2025 spreadsheet from obr.uk/data, locates the CfD row, commits the figure + URL.
- **If OBR + HoC + DESNZ all prove extraction-hostile**, CONTEXT D-11 fallback applies: ship `test_benchmarks.py` with LCCC floor only. Phase 2 does NOT block.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `import pandera as pa` | `import pandera.pandas as pa` | pandera 0.24 (deprecation 0.29) | Our code already uses the new form. No migration needed. |
| `pytest.skip(msg=...)` / `pytest.fail(msg=...)` | `pytest.skip(reason=...)` / `pytest.fail(reason=...)` | pytest 8+ | `@pytest.mark.skip(reason=...)` decorator still correct (unchanged). Our existing tests use it correctly. |
| `actions/setup-python@v5` + `pip install uv` | `astral-sh/setup-uv@v8` (uv + Python in one) | Action v1 → v8 stabilisation, 2024-2026 | Simpler CI, built-in cache keyed on uv.lock |
| `uv sync` | `uv sync --frozen` (CI) or `uv sync --locked` (CI) | Established best practice 2024+ | CI refuses to silently update lockfile |
| pandas `datetime64[ns]` default | pandas 3.0 `datetime64[us]` default for string parsing | pandas 3.0 (January 2026) | Pandera schemas with `coerce=True` handle it transparently; our code OK |
| Python 3.9-3.11 supported | Python 3.12 floor | Phase 1 bumped pyproject.toml (STATE.md) | Matches pytest 9's drop of 3.9 support; harmless for us |
| `unittest.mock` + class-based tests | Flat functions + pytest fixtures (`@pytest.fixture`) | Long-established pytest idiom | Our existing `tests/data/test_lccc.py` follows this |

**Deprecated/outdated:**
- `from cfd_payment import ...` — Phase 1 rename; tests MUST use `from uk_subsidy_tracker import ...` per CONTEXT canonical_refs.
- `data/technical-details/` doc path — Phase 1 moved to `docs/methodology/`.
- Five-class test ambition in the `.planning/ROADMAP.md` Phase 2 success criterion 1 — per D-04, reword to four.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | LCCC ARA 2024/25 PDF contains a specific calendar-year or fiscal-year aggregate CfD payment total in £bn extractable by a human reader | §Benchmark Sources 1 | If no aggregate is published, the LCCC floor falls back to "cumulative from raw CSV through a date" (our own pipeline data — still valid per D-10 since it's still "LCCC's published aggregate" in a weaker sense). |
| A2 | OBR Economic & Fiscal Outlook supplementary fiscal tables contain a specific CfD line item year-by-year | §Benchmark Sources 4 | If no CfD-specific line, OBR drops off the list. HoC + DESNZ remain. |
| A3 | DESNZ operational-costs consultation PDF contains year-by-year CfD forecast tables | §Benchmark Sources 5 | Unverified; WebFetch returned encoded stream. Implementer confirms during execution. |
| A4 | `astral-sh/setup-uv@v8` default `cache-dependency-glob` hashes `uv.lock` + `pyproject.toml` | §Pattern 6, §Standard Stack | WebFetch confirmed from README; if wrong, CI still works with manual cache key. |
| A5 | OBR's quoted 2024/25 CfD figure (£2.3bn) matches what we'd compute from our CSV within 5% | §Benchmark Sources 4 | Our 2024 calendar-year figure is £2.36bn, 2025 is £2.64bn. If OBR's FY-24/25 is £2.3bn (covering Apr 2024-Mar 2025), expect ~£2.3-2.4bn from our quarterly sums — within tolerance. |
| A6 | Ben Pile / Turver / REF secondary figures cited in this research doc (e.g., £25.8bn REF total) are NOT committed to `benchmarks.yaml` per D-08 | §Non-canonical sources | If a contributor later commits them without the `commentators:` key flag, it contradicts D-08. Reviewer vigilance required. |
| A7 | pytest 9.0.3 discovery picks up `tests/test_*.py` at the top level AND `tests/data/test_*.py` in sub-directories without `__init__.py` | §Anti-Patterns, §Project Structure | Verified locally: `uv run pytest tests/data/test_lccc.py` works. No action. |

## Open Questions (RESOLVED)

1. **Should CI use Python 3.12 only, or also matrix-test 3.13 / 3.14?**
   - What we know: `pyproject.toml` says `requires-python = ">=3.12"`; `.venv` ran on 3.13 during local testing; package has no 3.13-specific features yet.
   - What's unclear: Does the project intend to stay 3.12-compatible through Phase 11, or bump periodically?
   - Recommendation: Phase 2 ships 3.12 only per CONTEXT. If/when a dep requires 3.13, matrix it then.

2. **Should `pyproject.toml` grow a `[tool.pytest.ini_options]` section?**
   - What we know: No section exists today; pytest discovers tests cleanly; `configfile: pyproject.toml` appears in pytest output because pyproject.toml is the rootdir marker.
   - What's unclear: Does anything need configuring? Timeout? Warnings-as-errors? `tmpdir` cleanup?
   - Recommendation: Ship Phase 2 without it. Add when a concrete need emerges (e.g., Phase 4 determinism test may want `filterwarnings = error`).

3. **Does the LCCC ARA PDF ship CY or FY totals?**
   - What we know: ARA is tied to fiscal year.
   - What's unclear: Whether internal tables break out CY as well.
   - Recommendation: Planner adds an exploratory task for the implementer — "open the ARA PDF, record format in `benchmarks.yaml notes`".

4. **Which OBR supplementary table is the canonical CfD forecast?**
   - What we know: OBR publishes supplementary spreadsheets alongside EFO; secondary reporting cites OBR for CfD = £2.3bn 2024/25.
   - What's unclear: Specific worksheet / table number.
   - Recommendation: Planner adds a spike task — "identify OBR spreadsheet + tab holding CfD forecasts; record URL + tab name in `benchmarks.yaml`".

5. **Should Phase 2 add the `tests/fixtures/__init__.py` Pydantic loader, or wait for a second user (Phase 4 publisher)?**
   - What we know: Only `test_benchmarks.py` needs the loader today.
   - What's unclear: Future tests may want it too.
   - Recommendation: Ship the loader in `tests/fixtures/__init__.py` now (D-05 already blesses this path). Moving it later is trivial if needed.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| uv | Local + CI | ✓ | (uv.lock present, version installed locally) | — |
| Python 3.12 | Local + CI | ✓ (3.13 locally; CI installs 3.12 via setup-uv) | — | — |
| pytest 9.0.3 | Local + CI | ✓ | 9.0.3 locked | — |
| pandera 0.31.1 | Local + CI | ✓ | 0.31.1 locked | — |
| pandas 3.0.2 | Local + CI | ✓ | 3.0.2 locked | — |
| pyyaml 6.0.3 | Local + CI | ✓ | 6.0.3 locked | — |
| pydantic 2.13.3 | Local + CI | ✓ | 2.13.3 locked | — |
| `data/lccc-actual-cfd-generation.csv` | `test_aggregates.py`, `test_benchmarks.py`, `test_schemas.py` | ✓ | 104,013 rows | — |
| `data/elexon_agws.csv` | `test_schemas.py` | ✓ | 474,910 rows | — |
| `data/elexon_system_prices.csv` | `test_schemas.py` | ✓ | 162,844 rows | — |
| `data/ons_gas_sap.xlsx` | `test_schemas.py`, `test_counterfactual.py` (via loader) | ✓ | present | — |
| GitHub Actions runner `ubuntu-latest` | CI | ✓ | N/A (free tier) | — |
| Network access at CI runtime | For pytest | NOT REQUIRED | N/A | All tests run offline — committed CSVs + committed YAML fixture + committed Python code. `@pytest.mark.skip(reason="hits live website")` already in place for network-dependent tests. |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** None.
**Conclusion:** Phase 2 has zero environmental dependencies beyond the locked Python stack. CI boot-to-pass should be < 60 seconds on a cold cache, < 20 seconds on a warm cache.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 + pandera 0.31.1 (schema validation) |
| Config file | `pyproject.toml` (rootdir marker; no `[tool.pytest.ini_options]` section — defaults fine) |
| Quick run command | `uv run --frozen pytest -x --tb=short` |
| Full suite command | `uv run --frozen pytest -v` |
| Focused pin-test | `uv run --frozen pytest tests/test_counterfactual.py -v` |
| Benchmark-only | `uv run --frozen pytest tests/test_benchmarks.py -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TEST-01 | Gas counterfactual formula produces expected totals for 2019 / 2022 / zero-gas inputs | unit + pin | `uv run --frozen pytest tests/test_counterfactual.py::test_counterfactual_pin -v` | ❌ Wave 0 |
| GOV-04 (part a) | `METHODOLOGY_VERSION` is a SemVer string in `counterfactual` module | unit | `uv run --frozen pytest tests/test_counterfactual.py::test_methodology_version_present -v` | ❌ Wave 0 |
| GOV-04 (part b) | `compute_counterfactual()` returns `methodology_version` column | integration | `uv run --frozen pytest tests/test_counterfactual.py::test_methodology_version_in_output -v` | ❌ Wave 0 |
| GOV-04 (part c) | `CHANGES.md ## Methodology versions` section has the 1.0.0 entry | manual | grep: `grep -A 3 "### 1.0.0" CHANGES.md` | ❌ Wave 0 |
| TEST-02 (scaffolding) | Every raw CSV loads + validates against pandera schema | integration | `uv run --frozen pytest tests/test_schemas.py -v` | ❌ Wave 0 |
| TEST-03 (scaffolding) | `sum by year == sum by year × technology` on CfD generation | integration | `uv run --frozen pytest tests/test_aggregates.py -v` | ❌ Wave 0 |
| TEST-04 (floor) | LCCC self-reconciliation within 0.1% for every LCCC entry in fixture | integration + data | `uv run --frozen pytest tests/test_benchmarks.py::test_lccc_self_reconciliation_floor -v` | ❌ Wave 0 |
| TEST-04 (external) | Every external entry in fixture within its stated tolerance | integration + data (parametrised) | `uv run --frozen pytest tests/test_benchmarks.py::test_external_benchmark_within_tolerance -v` | ❌ Wave 0 |
| TEST-06 | GitHub Actions runs pytest on push + PR | smoke | GitHub Actions UI check after first push | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `uv run --frozen pytest -x --tb=short` (fast fail, full suite)
- **Per wave merge:** `uv run --frozen pytest -v` (full green report)
- **Phase gate:** All five success criteria green per CONTEXT D-04; GitHub Actions UI shows green check on `main` after the final push; reviewer confirms `benchmarks.yaml` has at least the LCCC floor entry with a real `value_gbp_bn`.

### Wave 0 Gaps

- [ ] `tests/test_counterfactual.py` — covers TEST-01 + GOV-04
- [ ] `tests/test_schemas.py` — covers TEST-02 (scaffolding)
- [ ] `tests/test_aggregates.py` — covers TEST-03 (scaffolding)
- [ ] `tests/test_benchmarks.py` — covers TEST-04
- [ ] `tests/fixtures/__init__.py` — Pydantic loader
- [ ] `tests/fixtures/benchmarks.yaml` — at minimum one LCCC floor entry with real `value_gbp_bn`
- [ ] `.github/workflows/ci.yml` — covers TEST-06
- [ ] `src/uk_subsidy_tracker/counterfactual.py` modification — `METHODOLOGY_VERSION` constant + column return
- [ ] `src/uk_subsidy_tracker/data/elexon.py` modification — pandera schemas for AGWS + system prices
- [ ] `src/uk_subsidy_tracker/data/ons_gas.py` modification — pandera schema for gas SAP
- [ ] `CHANGES.md` modification — fill `## Methodology versions` + note `[Unreleased]` additions
- [ ] `.planning/REQUIREMENTS.md` modification — TEST-02/03/05 rows Phase 2 → Phase 4
- [ ] `.planning/ROADMAP.md` modification — Phase 2 success criteria 1 & 3 rewords + requirements-list shift

Framework install: None required — `uv.lock` already includes pytest 9.0.3.

## Security Domain

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A — no auth surface; public static site |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A — read-only public data |
| V5 Input Validation | yes | pandera `DataFrameSchema` for all CSV ingestion; pydantic for YAML. Already the project pattern. |
| V6 Cryptography | no-but-related | No cryptographic primitives in Phase 2. Note: Phase 4 will introduce SHA-256 hashing of Parquet files for provenance (GOV-02). |
| V7 Error Handling | low-risk | Test failures surface via pytest; CI error logs on GitHub Actions. No sensitive data in tracebacks. |
| V8 Data Protection | no | All data is UK government open data; no PII. |
| V10 Malicious Code | low-risk | `yaml.safe_load` required for `benchmarks.yaml` (never `yaml.load`, which allows arbitrary Python object construction). |
| V12 API & Web Service | no | N/A |
| V14 Config | yes | `uv.lock` is the reproducibility contract; CI `--frozen` enforces it. |

### Known Threat Patterns for this Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| YAML deserialisation RCE via `yaml.load` | Tampering / Elevation | **Always use `yaml.safe_load`** (already the project pattern). Inspect diffs for `yaml.load(` without `safe_`. |
| CI action supply-chain (compromised third-party actions) | Tampering | Pin `astral-sh/setup-uv` to a version (`@v8` or SHA-pinned `@08807647...` for maximum paranoia); pin `actions/checkout@v5`. Rely on trusted orgs (`astral-sh`, `actions`). |
| Lockfile tampering (PR author edits `uv.lock` to include malicious package) | Tampering | `uv sync --frozen` still installs what the lockfile says. Mitigation is PR review — any `uv.lock` change must be tied to a `pyproject.toml` change and explained in the PR. Dependabot could automate, but deferred (Phase 3+ polish). |
| Test data poisoning | Tampering | Raw CSVs are in git; any tampering is visible in PR diff. Pandera validates schema on load so malformed data fails fast. |
| Malicious PR runs CI with writable secrets | Elevation | CI has no secrets in Phase 2. Only reads `GITHUB_TOKEN` (scoped). No deploy step. |
| Workflow triggering loop (push + PR both trigger) | DoS | Single-job workflow, no matrix, ~20 sec runtime. Free-tier GitHub Actions (2000 min/month) survives easily. |

## Sources

### Primary (HIGH confidence)

- **Context7** `/unionai-oss/pandera` — DataFrameSchema / Column / coerce / validate patterns `[VERIFIED via CLI]`
- **Context7** `/pytest-dev/pytest` — `@pytest.mark.skip(reason=...)` idiom confirmed; `msg → reason` migration noted `[VERIFIED via CLI]`
- **astral-sh/setup-uv** README (v8.1.0) — canonical CI workflow example `[VERIFIED: WebFetch 2026-04-22]`
- **uv docs** https://docs.astral.sh/uv/guides/integration/github/ — `--locked` vs `--frozen` guidance `[VERIFIED]`
- **PyPI** — current package versions: pandera 0.31.1, pytest 9.0.3, pandas 3.0.2, pyyaml 6.0.3, pydantic 2.13.3 `[VERIFIED via pypi.org API 2026-04-22]`
- **Local codebase** `src/uk_subsidy_tracker/data/lccc.py` — existing pandera schemas + YAML/Pydantic loader idiom `[VERIFIED: file read]`
- **Local codebase** `src/uk_subsidy_tracker/counterfactual.py` — formula constants confirmed for pin-test expected values `[VERIFIED: file read + synthetic compute]`
- **Local data** `data/lccc-actual-cfd-generation.csv` — annual totals computed fresh for aggregate tests `[VERIFIED: python3 CSV aggregation]`
- **LCCC Data Portal** https://dp.lowcarboncontracts.uk/dataset/forecast-ilr-tra — dataset UUID, fields, cadence `[VERIFIED: WebFetch 2026-04-22]`
- **LCCC news** https://www.lowcarboncontracts.uk/news/lccc-determines-ilr-and-tra-for-q4-2025/ — Q4 2025 ILR/TRA values `[VERIFIED]`

### Secondary (MEDIUM confidence)

- **LCCC publications** https://www.lowcarboncontracts.uk/resources/guidance-and-publications/ — ARA landing pages exist; specific £bn figures inside PDFs `[MEDIUM: PDFs not extracted]`
- **OBR** https://obr.uk/efo/economic-and-fiscal-outlook-november-2025/ — EFO Nov 2025 exists; CfD £2.3bn figure cited by secondary but not primary-verified by this research session `[MEDIUM: needs spreadsheet download during execution]`
- **HoC Library CBP-9871** https://researchbriefings.files.parliament.uk/documents/CBP-9871/CBP-9871.pdf — briefing exists `[MEDIUM: specific figures need PDF read]`
- **DESNZ Nov 2025 consultation PDF** `assets.publishing.service.gov.uk/media/69243d7f...` — exists, contains forecasts `[MEDIUM: WebFetch returned encoded stream]`
- **pandera blog / KDnuggets "Clean and Validate Your Data Using Pandera"** — migration pattern confirmation `[VERIFIED across multiple sources]`

### Tertiary (LOW confidence — flagged for validation at execution time)

- **OBR's exact per-year CfD figures 2021/22 through 2029/30** — cited via secondary; execution MUST extract directly from OBR supplementary spreadsheets.
- **LCCC ARA 2024/25 specific aggregate £bn** — PDF not extracted during research.
- **Ofgem's "cumulative to end-Aug 2024 = £8.9bn"** — cited by web search of Ofgem price-cap methodology PDF, not directly verified; used as a sanity-check annotation only.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all versions Context7- and PyPI-verified; existing codebase uses the recommended import patterns already.
- Architecture / test patterns: HIGH — direct replication of existing `tests/data/test_lccc.py` + `data/lccc.py` patterns.
- CI / GitHub Actions: HIGH — verified against astral-sh/setup-uv README (v8.1.0, April 2026).
- Pitfalls: HIGH — most are verified (pandera migration, pandas 3.0 dtype change, negative CfD payments in 2022).
- Benchmark sources: MEDIUM — sources located with URLs; specific £bn extraction is an execution-time task the researcher cannot complete without PDF readers.

**Research date:** 2026-04-22
**Valid until:** 2026-05-22 (30 days — stack is stable, but LCCC ARA / OBR EFO cycles publish on predictable cadences and may add newer versions within the window)

---

*Research complete. Planner may now draft PLAN.md files against this scaffold.*
