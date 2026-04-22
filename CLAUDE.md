<!-- GSD:project-start source:PROJECT.md -->
## Project

**UK Renewable Subsidy Tracker**

An independent, open, data-driven audit of UK renewable electricity subsidy costs — every scheme, every pound, every counterfactual, every methodology exposed — published as a permanent national resource. Serves journalists, advocates, academics, policymakers, and adversarial analysts from a static MkDocs site backed by reproducible Parquet pipelines.

Currently a single-scheme prototype (`cfd-payment`) covering only Contracts for Difference. This project expands it into an eight-scheme portal (`uk-subsidy-tracker`) covering CfD, RO, FiT, SEG, Constraint Payments, Capacity Market, Balancing Services, and Grid Socialisation.

**Core Value:** **Every headline number on the site is reproducible from a single `git clone` + `uv sync` + one command, backed by a methodology page, traceable to a primary regulator source, and survives hostile reading.** Methodological bulletproofness is the constraint from which every other decision flows.

### Constraints

- **Tech stack**: Python 3.12+ only — Rust, Go, Polars-migration, non-Python frameworks rejected. Maintainability principle dominates.
- **Analytical engine**: Parquet + DuckDB — no relational database. OLAP workload with 1:1,000,000 read:write ratio.
- **Hosting**: Static files on Cloudflare Pages only — no backend, no containers, no workflow engines. GitHub Actions cron for daily refresh.
- **Charting**: Plotly 6.x — already in production; exports Twitter-ready PNG + interactive HTML.
- **Documentation**: MkDocs Material — Python-native, 10-year stable, zero JS build pipeline.
- **Provenance**: Every Parquet file carries source hash, retrieval timestamp, pipeline git SHA. Non-negotiable.
- **Reproducibility**: `git clone` + `uv sync` + one command must reproduce every published number byte-identically.
- **Adversarial-proofing**: Every PRODUCTION chart = narrative page + methodology page + test + source-file link. Four-way coverage is the quality bar.
- **Data licensing**: All sources are UK government open data; provenance documented.
- **File size**: Raw CSVs ≤100 MB stay in git; larger files push to Cloudflare R2 with manifest pointer.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.11+ - Data pipeline, analytics, visualization, testing, documentation build
- YAML - Configuration files (MkDocs, dataset configs)
- Markdown - Documentation content
- HTML/CSS - Static generated site assets
## Runtime
- Python 3.12 or later (declared in `pyproject.toml`: `requires-python = ">=3.12"`)
- Currently running on Python 3.13 (based on `.venv` structure)
- uv - Fast, modern Python package manager with lockfile support
- Lockfile: `uv.lock` - Present and maintained
- Installation: `uv sync` after cloning repository
## Frameworks
- **pandas** - DataFrame manipulation, CSV/XLSX I/O, time-series aggregation
- **numpy** - Numerical operations, array handling
- **Pydantic >= 2.13.1** - Data validation via Pydantic schemas in `src/cfd_payment/schemas/`
- **pandera >= 0.31.1** - DataFrame schema validation for ingested datasets
- **DuckDB** (embedded) - OLAP engine for analytical queries on Parquet files; declared as dependency for future use per ARCHITECTURE.md
- **openpyxl** - Excel file reading (ONS gas price dataset)
- **Plotly >= 6.x** - Interactive charting, PNG/HTML export via `kaleido`
- **kaleido >= 1.2.0** - Static image export (PNG for social media, Twitter cards)
- **mkdocs >= 1.6.1** - Static site generator
- **mkdocs-material >= 9.7.6** - Material Design theme for documentation
- **requests >= 2.33.1** - HTTP client for downloading datasets from remote APIs
- **pytest >= 9.0.3** - Test runner and assertion framework
- Run: `uv run pytest tests/`
- **pydantic-settings >= 2.13.1** - Settings management (future)
- **pyyaml >= 6.0.3** - YAML parsing (dataset config files like `lccc_datasets.yaml`)
- **scipy >= 1.17.1** - Scientific computing utilities (statistical operations)
## Build System
- hatchling - PEP 517 build backend
- Configuration: `pyproject.toml` with `[build-system]`
- Package: `src/cfd_payment/` → wheel distribution
## Key Dependencies
- pandas, openpyxl, requests - Download and parse raw datasets from LCCC, ONS, Elexon APIs
- pydantic, pandera - Strict schema validation on all ingested data
- numpy, scipy - Numerical operations
- plotly, kaleido - Chart generation with static export
- mkdocs, mkdocs-material - Build and serve docs site
- pytest - Test runner
- pydantic - Runtime validation during test execution
- PyYAML - Load dataset configuration from `lccc_datasets.yaml`
- pydantic-settings - Future configuration management
## Configuration
- No `.env` file in use currently
- Configuration via YAML for dataset locations (see `src/cfd_payment/data/lccc_datasets.yaml`)
- Package-level constants in Python modules (e.g., `CCGT_EFFICIENCY`, gas prices in `counterfactual.py`)
- `pyproject.toml` - Single source of truth for metadata, dependencies, build backend
- `uv.lock` - Locked dependency versions, reproducible installs
- `mkdocs.yml` - Complete MkDocs configuration
## Platform Requirements
- Python 3.11+ with uv installed
- 2+ GB RAM for full data pipeline (Elexon AGWS/system prices are 85+ MB CSV)
- Disk space: ~250 MB for data/ directory (raw CSVs + future Parquet)
- **Hosting:** Cloudflare Pages (free tier)
- **DNS:** Cloudflare (free tier)
- **Storage:** GitHub for source code ≤100 MB per file; Cloudflare R2 for oversized data files (>100 MB)
- **CI/CD:** GitHub Actions (free tier, ~3-5 minutes per daily refresh)
- **Data refresh:** Daily cron at 06:00 UTC via `refresh.yml` workflow (planned, not yet deployed)
## Data Layer Stack
- CSV - LCCC, Elexon, NESO data (preserves upstream schema)
- XLSX - ONS gas price data
- Git-committed where ≤100 MB; Cloudflare R2 for larger files
- Parquet - Columnar, schema-embedded, compressed ~10× vs CSV
- Parquet - Primary analytical format
- CSV - Mirror for journalist convenience
- JSON - Metadata and manifests
## Entry Points
- `src/cfd_payment/data/lccc.py` - LCCC CfD settlements download and validation
- `src/cfd_payment/data/elexon.py` - Elexon AGWS (wind/solar) and system prices
- `src/cfd_payment/data/ons_gas.py` - ONS gas price data fetch
- `src/cfd_payment/plotting/__main__.py` - Entry point for running all charts (`uv run python -m cfd_payment.plotting`)
- Outputs: PNG (Twitter) + interactive HTML to `docs/charts/html/`
- `mkdocs.yml` - Serve docs locally: `uv run mkdocs serve`
- Build: `uv run mkdocs build --strict`
- Deploy: `uv run mkdocs gh-deploy` (GitHub Pages)
- `pytest` - Run all tests in `tests/` directory
## Deployment Pipeline (Planned)
- Trigger: Daily cron 06:00 UTC or manual dispatch
- Steps:
- Trigger: Git tag push (e.g., `git tag v2026.04`)
- Creates immutable versioned snapshot in `site/data/v2026-04-21/`
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Lowercase with underscores: `counterfactual.py`, `chart_builder.py`, `ons_gas.py`
- Modules containing main entry point use `__main__.py`: `src/cfd_payment/plotting/__main__.py`
- Test files follow pattern: `test_<module>.py`, located in `tests/<category>/` directories
- Snake case throughout: `load_gas_price()`, `compute_counterfactual()`, `format_gbp_axis()`
- Verb-first pattern for operations: `download_dataset()`, `create_basic()`, `save_chart()`
- Getter methods use `load_*()` or `get_*()` conventions: `load_lccc_dataset()`, `get_allocation_round_colors()`
- Private helpers and internal utilities: minimal use observed; public API is primary pattern
- Snake case: `gas_df`, `by_unit`, `output_dir`, `non_fuel_opex_per_mwh`
- Module-level constants in UPPER_SNAKE_CASE: `CCGT_EFFICIENCY`, `GAS_CO2_INTENSITY_THERMAL`, `DEFAULT_NON_FUEL_OPEX`, `TECHNOLOGY_COLORS`
- Abbreviations used selectively: `df` for DataFrames (pandas convention), `fig` for Plotly figures, `m` for millions (unit suffix), `kwh` for kilowatt-hours
- Type hints fully present in function signatures using Python 3.11+ syntax
- Union types use `|` operator: `pd.DataFrame | None`, `dict[int, float]`
- Return types always specified: `-> pd.DataFrame`, `-> None`, `-> Path`
- Class names use PascalCase: `LCCCDatasetConfig`, `ChartBuilder`, `LCCCAppConfig`
## Code Style
- Black-compatible formatting (implicit; no linter config found in repo)
- Line wrapping observed at ~80–100 characters for code, longer for data/schemas
- Docstrings use triple-double quotes (`"""`) consistently
- Imports organized by standard library, third-party, local (observed in all modules)
- No explicit `.ruff.toml` or `.flake8` config detected; relies on Pyright configuration
- Pyright configured in `pyrightconfig.json` with basic type checking
- `reportMissingImports` set to "warning" only; most other issues disabled for flexibility
## Import Organization
- No path aliases detected in `pyrightconfig.json`
- Absolute imports from package root: `from cfd_payment import DATA_DIR`, `from cfd_payment.data import load_gas_price`
- Relative imports within modules: `from .lccc import download_lccc_datasets`
- Imports aliased to `main` consistently; allows parallel execution in orchestration
## Error Handling
- Try/except for network operations (requests): `src/cfd_payment/data/lccc.py:95–102`
- Graceful degradation on download failure (returns `output_path` even on exception)
- Pydantic validation via schema: `lccc.py:111–112` uses pandera `validate()` for CSV validation
- KeyError for missing dataset lookups: `lccc.py:32` in `LCCCAppConfig.dataset()`
- Try/except for file operations (export, PNG generation): `chart_builder.py:379–436` wraps kaleido calls
## Logging
- User-facing messages: `print(f"Saved {path}")` in `plotting/utils.py:56`
- Error messages: `print(f"An error occurred while downloading {filename}: {e}")` in `data/lccc.py:102`
- No log levels (DEBUG, INFO, WARNING, ERROR) implemented
- No structured logging or log aggregation
## Comments
- Algorithm explanation for non-obvious logic (e.g., counterfactual formula in `counterfactual.py:15–28`)
- Data transformation reasoning (e.g., efficiency conversion, carbon cost computation)
- Config/constant declarations include inline comments explaining purpose/source
- Docstrings are primary; in-line comments are minimal
- Uses reStructuredText-style docstrings (compatible with NumPy/Sphinx style)
- Function docstrings include Args, Returns patterns (inconsistent depth):
- Module-level docstrings (examples):
## Function Design
- Typical functions 10–40 lines (data processing) to 60–100 lines (chart building)
- Longest observed: `chart_builder.py` methods span up to ~80 lines (e.g., `save()` method with export logic)
- Functions accept 2–6 parameters typically
- Keyword-only arguments for optional parameters (observed in `format_currency_axis()`, `format_percentage_axis()`)
- Default parameters: widely used for optional configurations
- Type hints mandatory on all parameters
- Always typed: `-> pd.DataFrame`, `-> None`, `-> Path`, `-> dict[str, str]`
- Multiple return types expressed with `|`: `Path | None`
- Void functions explicit: `-> None` (not implicit)
## Module Design
- Modules expose functions and classes directly; no `__all__` patterns observed
- Package `__init__.py` acts as public interface: `src/cfd_payment/__init__.py` exports constants `PROJECT_ROOT`, `DATA_DIR`, `OUTPUT_DIR`
- Data module `__init__.py` exports key functions: `from .lccc import download_lccc_datasets, load_lccc_dataset`
- `src/cfd_payment/data/__init__.py` re-exports loaders: effectively a barrel file for data module
- `src/cfd_payment/plotting/__init__.py` likely re-exports `ChartBuilder` (not fully inspected)
- `src/cfd_payment/plotting/subsidy/__init__.py` exists but mostly empty (submodules imported directly)
## Type Checking Configuration
- `pythonVersion: 3.11` (targets Python 3.11+)
- `typeCheckingMode: basic` (lenient, non-strict mode)
- Most issue types disabled (`reportOperatorIssue: false`, `reportAttributeAccessIssue: false`)
- Only `reportMissingImports: "warning"` actively enforced
- Allows flexibility in type annotations while catching missing imports
## Data Processing Patterns
- Pydantic v2.13.1+ for schema definition: `LCCCDatasetConfig`, `LCCCAppConfig`
- Used for YAML config parsing: `yaml.safe_load()` → `LCCCAppConfig(**raw_config)`
- BaseModel inheritance for all config classes
- CSV schema definition and validation for LCCC datasets
- Schemas defined as module-level constants: `lccc_generation_schema`, `lccc_portfolio_schema`
- Validation on load: `schema.validate(df)`
- Standard groupby/agg patterns: `df.groupby([...]).agg({...}).reset_index()`
- Column selection and filtering: `df[df["field"] > threshold]`
- Date handling: `pd.to_datetime()`, `df.dt.year.map(dict)`
- Numeric coercion: `pd.to_numeric(..., errors="coerce")`
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Current State vs Target
## Pattern Overview
- Source → Derived → Published three-layer architecture (defined; partially implemented)
- CfD scheme only; no other scheme modules yet
- Static site generation via MkDocs (readthedocs theme)
- Plotly-based charting with custom dark theme
- DuckDB and Parquet planned but not yet implemented; using CSV + pandas currently
- Python 3.11+, uv package manager, pytest for testing
## Layers
### 4.1 Source Layer (`data/raw/` — Target state; partial current state)
- `lccc-actual-cfd-generation.csv` — LCCC daily settlement (raw)
- `lccc-cfd-contract-portfolio-status.csv` — LCCC portfolio snapshot (raw)
- `elexon_agws.csv` — Actual Generation Wind/Solar (raw)
- `elexon_system_prices.csv` — Balancing system prices (raw)
- `ons_gas_sap.xlsx` — ONS System Average Price of gas (raw)
### 4.2 Derived Layer (`data/derived/` — Not yet implemented)
### 4.3 Publishing Layer (`site/data/` — Not yet implemented)
## Data Flow
### CfD Pipeline (Current — Only Working Path)
```
```
## Key Abstractions
### ChartBuilder
```python
```
### Counterfactual Model
```
```
### Plotting Theme
- Offshore Wind: `#1f77b4`
- Onshore Wind: `#6baed6`
- Biomass (Drax/Lynemouth): `#d62728`
- Solar PV: `#ff7f0e`
## Entry Points
### Chart Generation
```
```
### Documentation Site
- Home (`docs/index.md`)
- Charts overview + 3 CfD chart pages
- Gas counterfactual methodology
## Error Handling
- Pandera schema validation on CSV ingest (`src/cfd_payment/data/lccc.py`)
- `dropna()` and null-checks in chart preparation
- Tests marked `@pytest.mark.skip` for tests that hit live services
## Cross-Cutting Concerns
- `test_counterfactual.py` (formula pinning)
- `test_schemas.py` (Parquet conformance)
- `test_aggregates.py` (row conservation)
- `test_benchmarks.py` (external cross-check)
- `test_determinism.py` (byte-identical output)
## Scheme Module Contract
```python
```
- `src/cfd_payment/counterfactual.py`
- `src/cfd_payment/plotting/subsidy/*.py` (chart-level)
- `src/cfd_payment/data/*.py` (loaders)
## Refresh Cadence
## Hosting & Deployment
## Publishing Layer Contract
```
```
## Gaps & Technical Debt (Summary)
| Gap | Impact | Target Phase |
|-----|--------|--------------|
| No derived layer (Parquet pipeline) | Each chart re-processes raw data; no caching | P3 |
| No Parquet/DuckDB | Using pandas only; slow for large datasets | P1–P3 (tech stack already decided) |
| No scheme module abstraction | CfD tightly coupled; can't replicate to RO/FiT | P1–P2 |
| Scissors chart still active | Contradicts triage; should be removed | P2 |
| MkDocs theme still `readthedocs` | Target specifies Material | P0 |
| No test coverage for counterfactual formula | Risk of silent changes | P1 |
| No repo rename (cfd-payment → uk-subsidy-tracker) | Scope has expanded; name outdated | P0 |
| No ARCHITECTURE.md in repo | Must exist per P0 | P0 |
| No RO-MODULE-SPEC.md | Template for remaining schemes | P0 |
| No CI/CD pipeline | Deploys are manual | P1–P7 |
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
