# Coding Conventions

**Analysis Date:** 2026-04-21

## Naming Patterns

**Files:**
- Lowercase with underscores: `counterfactual.py`, `chart_builder.py`, `ons_gas.py`
- Modules containing main entry point use `__main__.py`: `src/cfd_payment/plotting/__main__.py`
- Test files follow pattern: `test_<module>.py`, located in `tests/<category>/` directories

**Functions:**
- Snake case throughout: `load_gas_price()`, `compute_counterfactual()`, `format_gbp_axis()`
- Verb-first pattern for operations: `download_dataset()`, `create_basic()`, `save_chart()`
- Getter methods use `load_*()` or `get_*()` conventions: `load_lccc_dataset()`, `get_allocation_round_colors()`
- Private helpers and internal utilities: minimal use observed; public API is primary pattern

**Variables:**
- Snake case: `gas_df`, `by_unit`, `output_dir`, `non_fuel_opex_per_mwh`
- Module-level constants in UPPER_SNAKE_CASE: `CCGT_EFFICIENCY`, `GAS_CO2_INTENSITY_THERMAL`, `DEFAULT_NON_FUEL_OPEX`, `TECHNOLOGY_COLORS`
- Abbreviations used selectively: `df` for DataFrames (pandas convention), `fig` for Plotly figures, `m` for millions (unit suffix), `kwh` for kilowatt-hours

**Types:**
- Type hints fully present in function signatures using Python 3.11+ syntax
- Union types use `|` operator: `pd.DataFrame | None`, `dict[int, float]`
- Return types always specified: `-> pd.DataFrame`, `-> None`, `-> Path`
- Class names use PascalCase: `LCCCDatasetConfig`, `ChartBuilder`, `LCCCAppConfig`

## Code Style

**Formatting:**
- Black-compatible formatting (implicit; no linter config found in repo)
- Line wrapping observed at ~80–100 characters for code, longer for data/schemas
- Docstrings use triple-double quotes (`"""`) consistently
- Imports organized by standard library, third-party, local (observed in all modules)

**Linting:**
- No explicit `.ruff.toml` or `.flake8` config detected; relies on Pyright configuration
- Pyright configured in `pyrightconfig.json` with basic type checking
- `reportMissingImports` set to "warning" only; most other issues disabled for flexibility

## Import Organization

**Order:**
1. Standard library imports (`pathlib`, `pandas`, `requests`)
2. Third-party imports (`pandas`, `plotly`, `pydantic`, `pandera`, `pyyaml`)
3. Local imports from `cfd_payment` package

**Path Aliases:**
- No path aliases detected in `pyrightconfig.json`
- Absolute imports from package root: `from cfd_payment import DATA_DIR`, `from cfd_payment.data import load_gas_price`
- Relative imports within modules: `from .lccc import download_lccc_datasets`

**Pattern observed in `src/cfd_payment/plotting/__main__.py`:**
```python
from cfd_payment.plotting.cannibalisation.capture_ratio import main as capture_ratio
from cfd_payment.plotting.subsidy.bang_for_buck import main as bang_for_buck
```
- Imports aliased to `main` consistently; allows parallel execution in orchestration

## Error Handling

**Patterns:**
- Try/except for network operations (requests): `src/cfd_payment/data/lccc.py:95–102`
  ```python
  try:
      response = requests.get(url, headers=HEADERS, stream=True)
      response.raise_for_status()
      # write file
  except requests.exceptions.RequestException as e:
      print(f"An error occurred while downloading {filename}: {e}")
  ```
- Graceful degradation on download failure (returns `output_path` even on exception)
- Pydantic validation via schema: `lccc.py:111–112` uses pandera `validate()` for CSV validation
- KeyError for missing dataset lookups: `lccc.py:32` in `LCCCAppConfig.dataset()`
- Try/except for file operations (export, PNG generation): `chart_builder.py:379–436` wraps kaleido calls

**No explicit custom exception classes observed** — relies on standard library + third-party exceptions.

## Logging

**Framework:** `print()` only (no dedicated logging module)

**Patterns:**
- User-facing messages: `print(f"Saved {path}")` in `plotting/utils.py:56`
- Error messages: `print(f"An error occurred while downloading {filename}: {e}")` in `data/lccc.py:102`
- No log levels (DEBUG, INFO, WARNING, ERROR) implemented
- No structured logging or log aggregation

## Comments

**When to Comment:**
- Algorithm explanation for non-obvious logic (e.g., counterfactual formula in `counterfactual.py:15–28`)
- Data transformation reasoning (e.g., efficiency conversion, carbon cost computation)
- Config/constant declarations include inline comments explaining purpose/source
- Docstrings are primary; in-line comments are minimal

**JSDoc/TSDoc:**
- Uses reStructuredText-style docstrings (compatible with NumPy/Sphinx style)
- Function docstrings include Args, Returns patterns (inconsistent depth):
  ```python
  def format_currency_axis(
      self,
      fig: go.Figure,
      *,
      axis: Literal["x", "y"] = "y",
      suffix: str = "",
      prefix: str = "£",
      tickformat: str = "~g",
      secondary_y: bool = False,
      title: str = "",
      row: int | None = None,
      col: int | None = None,
  ) -> None:
      """Apply currency formatting to an axis.

      Args:
          fig: The figure to modify
          axis: Which axis to format ("x" or "y")
          suffix: Tick suffix (default "m" for millions)
          prefix: Tick prefix (default "£")
          tickformat: D3 format string (default "~g" for compact)
          secondary_y: Whether this is a secondary y-axis
          title: Axis title
          row: Subplot row (for subplots)
          col: Subplot column (for subplots)
      """
  ```
- Module-level docstrings (examples):
  - `counterfactual.py`: Domain-specific explanation of the counterfactual formula
  - `chart_builder.py`: Purpose, attributes, usage example in class docstring
  - `data/lccc.py`: Purpose of each schema and loading function

## Function Design

**Size:**
- Typical functions 10–40 lines (data processing) to 60–100 lines (chart building)
- Longest observed: `chart_builder.py` methods span up to ~80 lines (e.g., `save()` method with export logic)

**Parameters:**
- Functions accept 2–6 parameters typically
- Keyword-only arguments for optional parameters (observed in `format_currency_axis()`, `format_percentage_axis()`)
  - Pattern: `def func(required_arg, *, kwarg1=default, kwarg2=default)`
- Default parameters: widely used for optional configurations
- Type hints mandatory on all parameters

**Return Values:**
- Always typed: `-> pd.DataFrame`, `-> None`, `-> Path`, `-> dict[str, str]`
- Multiple return types expressed with `|`: `Path | None`
- Void functions explicit: `-> None` (not implicit)

## Module Design

**Exports:**
- Modules expose functions and classes directly; no `__all__` patterns observed
- Package `__init__.py` acts as public interface: `src/cfd_payment/__init__.py` exports constants `PROJECT_ROOT`, `DATA_DIR`, `OUTPUT_DIR`
- Data module `__init__.py` exports key functions: `from .lccc import download_lccc_datasets, load_lccc_dataset`

**Barrel Files:**
- `src/cfd_payment/data/__init__.py` re-exports loaders: effectively a barrel file for data module
- `src/cfd_payment/plotting/__init__.py` likely re-exports `ChartBuilder` (not fully inspected)
- `src/cfd_payment/plotting/subsidy/__init__.py` exists but mostly empty (submodules imported directly)

## Type Checking Configuration

**Tool:** Pyright

**Config file:** `pyrightconfig.json`
- `pythonVersion: 3.11` (targets Python 3.11+)
- `typeCheckingMode: basic` (lenient, non-strict mode)
- Most issue types disabled (`reportOperatorIssue: false`, `reportAttributeAccessIssue: false`)
- Only `reportMissingImports: "warning"` actively enforced
- Allows flexibility in type annotations while catching missing imports

**Implication:** Type hints are present but not strictly enforced; mypy-style strictness not required.

## Data Processing Patterns

**Pydantic Usage:**
- Pydantic v2.13.1+ for schema definition: `LCCCDatasetConfig`, `LCCCAppConfig`
- Used for YAML config parsing: `yaml.safe_load()` → `LCCCAppConfig(**raw_config)`
- BaseModel inheritance for all config classes

**Pandera Validation:**
- CSV schema definition and validation for LCCC datasets
- Schemas defined as module-level constants: `lccc_generation_schema`, `lccc_portfolio_schema`
- Validation on load: `schema.validate(df)`

**Pandas Operations:**
- Standard groupby/agg patterns: `df.groupby([...]).agg({...}).reset_index()`
- Column selection and filtering: `df[df["field"] > threshold]`
- Date handling: `pd.to_datetime()`, `df.dt.year.map(dict)`
- Numeric coercion: `pd.to_numeric(..., errors="coerce")`

---

*Convention analysis: 2026-04-21*
