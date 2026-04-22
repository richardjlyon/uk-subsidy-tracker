# Testing Patterns

**Analysis Date:** 2026-04-21

## Test Framework

**Runner:**
- pytest 9.0.3+
- Config: No explicit `pytest.ini` or `[tool.pytest.ini_options]` in `pyproject.toml` detected
- Default discovery: `tests/` directory with `test_*.py` naming convention

**Assertion Library:**
- pytest's built-in assertions (`assert`)

**Run Commands:**
```bash
pytest                      # Run all tests
pytest --collect-only       # List tests without running
pytest -v                   # Verbose output
pytest tests/data/          # Run specific directory
```

Note: No explicit watch mode, coverage config, or CI test command documented in visible config. Inferred from ARCHITECTURE.md §9.6.

## Test File Organization

**Location:**
- Co-located in `tests/` directory (separate from source)
- Organized by module: `tests/data/` mirrors `src/cfd_payment/data/`

**Directory structure:**
```
tests/
├── data/
│   ├── test_lccc.py
│   └── test_ons.py
├── __pycache__/
└── [test_counterfactual.py - ABSENT]
    [test_schemas.py - ABSENT]
    [test_aggregates.py - ABSENT]
    [test_benchmarks.py - ABSENT]
    [test_determinism.py - ABSENT]
```

**Naming:**
- Files: `test_<module>.py`
- Test functions: `test_<feature>()`

## Test Structure

**Suite Organization:**
```python
# tests/data/test_lccc.py
import pytest

from cfd_payment.data.lccc import (
    download_lccc_datasets,
    load_lccc_config,
    load_lccc_dataset,
)


@pytest.mark.skip(reason="hits live website")
def test_download_lccc_datasets():
    config = load_lccc_config()
    download_lccc_datasets(config)


def test_load_config():
    config = load_lccc_config()
    assert len(config.datasets) > 0
    assert config.dataset(
        "Actual CfD Generation and avoided GHG emissions"
    ).filename.endswith(".csv")


def test_load_dataset():
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    assert not df.empty
    assert "Settlement_Date" in df.columns
```

**Patterns:**
- No explicit setup/teardown (fixtures, class-based suites) in current tests
- Module imports at top, followed by test functions
- Tests are flat functions, not class-based

## Test Types and Coverage

**Present (2 test files, 6 tests total):**

1. **`tests/data/test_lccc.py`** (3 tests):
   - `test_download_lccc_datasets()`: Skipped (network dependency)
   - `test_load_config()`: Validates YAML config parsing to Pydantic models
   - `test_load_dataset()`: Validates CSV load + pandera schema validation

2. **`tests/data/test_ons.py`** (3 tests):
   - `test_download_dataset()`: Skipped (network dependency)
   - `test_load_dataset()`: Validates Excel load for ONS gas price data
   - Basic DataFrame validation (not empty, column exists)

**Absent but required by ARCHITECTURE.md §9.6:**

| Test class | Status | Purpose |
|---|---|---|
| `test_counterfactual.py` | **MISSING** | Pin the gas counterfactual formula against known inputs |
| `test_schemas.py` | **MISSING** | Every Parquet file conforms to its Pydantic schema |
| `test_aggregates.py` | **MISSING** | `sum by (year)` = `sum by (year × technology)`; no row leakage |
| `test_benchmarks.py` | **MISSING** | Aggregates match REF/Turver/Ofgem within documented tolerance |
| `test_determinism.py` | **MISSING** | Identical input → byte-identical Parquet output |

**Test scope summary:**
- Current: Data loading and configuration validation only
- Planned: Formula pinning, schema validation, aggregation logic, benchmark comparisons, determinism

## Skipped Tests

**Pattern:**
```python
@pytest.mark.skip(reason="hits live website")
def test_download_lccc_datasets():
    ...
```

**Reason:** Both download tests are marked skipped to avoid network dependencies in CI. Manual running requires:
1. Internet connectivity
2. Upstream services (LCCC, ONS) available
3. Valid data in expected schema

## Fixture and Factory Patterns

**Test Data:**
- No fixtures or factories currently implemented
- Tests depend on real files in `data/` directory (LCCC YAML config, downloaded CSVs)
- Assumption: Data files pre-downloaded and committed or available at test time

**Location:**
- No `conftest.py` in repo root or `tests/` directory
- No shared fixtures or parametrization observed

## Mocking

**Framework:** Not used currently

**Patterns:**
- All current tests hit real data (CSV files, YAML config)
- Network operations intentionally skipped (marked `@pytest.mark.skip`)
- No unittest.mock or pytest-mock imports observed

## Assertion Patterns

**Current pattern (basic validation):**
```python
def test_load_config():
    config = load_lccc_config()
    assert len(config.datasets) > 0
    assert config.dataset("Actual CfD Generation and avoided GHG emissions").filename.endswith(".csv")

def test_load_dataset():
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    assert not df.empty
    assert "Settlement_Date" in df.columns
```

**Validation types observed:**
- Non-empty collections: `assert len(config.datasets) > 0`
- DataFrame shape: `assert not df.empty`
- Column membership: `assert "Settlement_Date" in df.columns`
- Type membership: `assert filename.endswith(".csv")`

**For planned tests (inferred from ARCHITECTURE.md):**
- Formula output pinning: `assert counterfactual_result == expected_value`
- Aggregate consistency: `assert by_year_sum == by_year_tech_sum`
- Tolerance-based benchmarks: `assert abs(our_total - ofgem_total) <= tolerance`
- Bit-identical outputs: `assert sha256(output1) == sha256(output2)`

## Coverage

**Requirements:** None enforced (no `[tool.pytest]` coverage config in `pyproject.toml`)

**Current coverage estimate:**
- Data loading/validation: ~60% of `src/cfd_payment/data/`
- Plotting, counterfactual, aggregation: 0% (no tests)

**View Coverage (if implemented):**
```bash
pytest --cov=cfd_payment --cov-report=html
pytest --cov=cfd_payment --cov-report=term-missing
```

**Target (from ARCHITECTURE.md):** Every PRODUCTION chart and critical formula must have a test, even if coverage % is not enforced. Tests are "small, boring, essential. ~300–500 lines total."

## Error Scenarios

**How to test errors (pattern to follow):**

For `LCCCAppConfig.dataset()` KeyError:
```python
def test_load_missing_dataset():
    config = load_lccc_config()
    with pytest.raises(KeyError):
        config.dataset("Nonexistent Dataset Name")
```

For network failures (when unmocked):
```python
@pytest.mark.skip(reason="requires network + valid upstream state")
def test_download_network_failure():
    # Test would verify graceful handling of RequestException
    ...
```

## Test Execution Environment

**Python version:** 3.11+ (per `pyrightconfig.json`)

**Dependencies installed:**
- pytest >=9.0.3
- All source dependencies (pandas, pydantic, pandera, plotly, etc.)

**Pre-requisites:**
- Data files in `data/` directory (LCCC CSVs, ONS Excel)
- No external services required for skipped tests to pass

## Integration Points

**Dependencies between tests:**
- `test_load_config()` must succeed before `test_load_dataset()` (config provides dataset name)
- Both assume YAML config file at `src/cfd_payment/data/lccc_datasets.yaml` exists and is valid
- Both assume CSV files have been downloaded (via `download_*` functions or manual fetch)

**Order sensitivity:**
- Tests can run in any order (no shared state, no setup/teardown dependencies)

## Planned Test Structure (from ARCHITECTURE.md §9.6)

The five required test classes and their scope:

1. **`test_counterfactual.py`** (~50 lines)
   - Pin counterfactual formula: gas cost + carbon cost + opex
   - Known inputs: gas price (p/kWh), year (carbon price lookup), efficiency assumptions
   - Verify against hardcoded expected outputs

2. **`test_schemas.py`** (~100 lines)
   - For each scheme's Parquet outputs (once Parquet generation exists)
   - Load Parquet → validate against Pydantic schema
   - Check column types, nullable constraints, enum values

3. **`test_aggregates.py`** (~80 lines)
   - For each scheme module: `sum(payment by year)` == `sum(payment by year and technology)`
   - For cross-scheme: ensure no double-counting, no row leakage
   - Parametrized by scheme module

4. **`test_benchmarks.py`** (~100 lines)
   - Compare yearly aggregates to external sources:
     - Renewable Energy Foundation (REF) reports
     - Turver/Carbon Brief analysis
     - Ofgem official totals
   - Assert within documented tolerance (e.g., ±2%)
   - Benchmark table: `external_source | our_total | tolerance | status`

5. **`test_determinism.py`** (~50 lines)
   - Run full pipeline twice on identical inputs
   - Compute SHA-256 of output Parquet files
   - Assert byte-identical: `sha256(run1) == sha256(run2)`
   - Validates no random data, consistent ordering, no timestamp embedding

---

*Testing analysis: 2026-04-21*
