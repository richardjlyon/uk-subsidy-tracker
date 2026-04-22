# Technology Stack

**Analysis Date:** 2026-04-21

## Languages

**Primary:**
- Python 3.11+ - Data pipeline, analytics, visualization, testing, documentation build

**Secondary:**
- YAML - Configuration files (MkDocs, dataset configs)
- Markdown - Documentation content
- HTML/CSS - Static generated site assets

## Runtime

**Environment:**
- Python 3.11 or later (declared in `pyproject.toml`: `requires-python = ">=3.11"`)
- Currently running on Python 3.13 (based on `.venv` structure)

**Package Manager:**
- uv - Fast, modern Python package manager with lockfile support
- Lockfile: `uv.lock` - Present and maintained
- Installation: `uv sync` after cloning repository

## Frameworks

**Core Data Processing:**
- **pandas** - DataFrame manipulation, CSV/XLSX I/O, time-series aggregation
- **numpy** - Numerical operations, array handling
- **Pydantic >= 2.13.1** - Data validation via Pydantic schemas in `src/cfd_payment/schemas/`
- **pandera >= 0.31.1** - DataFrame schema validation for ingested datasets

**Analytical Engine:**
- **DuckDB** (embedded) - OLAP engine for analytical queries on Parquet files; declared as dependency for future use per ARCHITECTURE.md

**Data Storage:**
- **openpyxl** - Excel file reading (ONS gas price dataset)

**Visualization:**
- **Plotly >= 6.x** - Interactive charting, PNG/HTML export via `kaleido`
- **kaleido >= 1.2.0** - Static image export (PNG for social media, Twitter cards)

**Documentation:**
- **mkdocs >= 1.6.1** - Static site generator
- **mkdocs-material >= 9.7.6** - Material Design theme for documentation

**HTTP & Data Fetch:**
- **requests >= 2.33.1** - HTTP client for downloading datasets from remote APIs

**Testing:**
- **pytest >= 9.0.3** - Test runner and assertion framework
- Run: `uv run pytest tests/`

**Utilities:**
- **pydantic-settings >= 2.13.1** - Settings management (future)
- **pyyaml >= 6.0.3** - YAML parsing (dataset config files like `lccc_datasets.yaml`)
- **scipy >= 1.17.1** - Scientific computing utilities (statistical operations)

## Build System

**Build Tool:**
- hatchling - PEP 517 build backend
- Configuration: `pyproject.toml` with `[build-system]`
- Package: `src/cfd_payment/` → wheel distribution

## Key Dependencies

**Critical — Data Ingest:**
- pandas, openpyxl, requests - Download and parse raw datasets from LCCC, ONS, Elexon APIs
- pydantic, pandera - Strict schema validation on all ingested data

**Critical — Analysis:**
- numpy, scipy - Numerical operations
- plotly, kaleido - Chart generation with static export

**Critical — Documentation:**
- mkdocs, mkdocs-material - Build and serve docs site

**Testing & Quality:**
- pytest - Test runner
- pydantic - Runtime validation during test execution

**Infrastructure:**
- PyYAML - Load dataset configuration from `lccc_datasets.yaml`
- pydantic-settings - Future configuration management

## Configuration

**Environment:**
- No `.env` file in use currently
- Configuration via YAML for dataset locations (see `src/cfd_payment/data/lccc_datasets.yaml`)
- Package-level constants in Python modules (e.g., `CCGT_EFFICIENCY`, gas prices in `counterfactual.py`)

**Build:**
- `pyproject.toml` - Single source of truth for metadata, dependencies, build backend
- `uv.lock` - Locked dependency versions, reproducible installs

**Documentation Build:**
- `mkdocs.yml` - Complete MkDocs configuration
  - Theme: readthedocs (to be switched to material in P0)
  - Extensions: pymdownx, abbr, admonition, tables, footnotes, emoji, code highlighting
  - Plugins: search
  - Site URL: `https://richardjlyon.github.io/cfd-payment/`

## Platform Requirements

**Development:**
- Python 3.11+ with uv installed
- 2+ GB RAM for full data pipeline (Elexon AGWS/system prices are 85+ MB CSV)
- Disk space: ~250 MB for data/ directory (raw CSVs + future Parquet)

**Production:**
- **Hosting:** Cloudflare Pages (free tier)
- **DNS:** Cloudflare (free tier)
- **Storage:** GitHub for source code ≤100 MB per file; Cloudflare R2 for oversized data files (>100 MB)
- **CI/CD:** GitHub Actions (free tier, ~3-5 minutes per daily refresh)
- **Data refresh:** Daily cron at 06:00 UTC via `refresh.yml` workflow (planned, not yet deployed)

## Data Layer Stack

**Source Format (data/raw/):**
- CSV - LCCC, Elexon, NESO data (preserves upstream schema)
- XLSX - ONS gas price data
- Git-committed where ≤100 MB; Cloudflare R2 for larger files

**Derived Format (data/derived/):**
- Parquet - Columnar, schema-embedded, compressed ~10× vs CSV

**Publishing Format (site/data/):**
- Parquet - Primary analytical format
- CSV - Mirror for journalist convenience
- JSON - Metadata and manifests

## Entry Points

**Data Pipeline:**
- `src/cfd_payment/data/lccc.py` - LCCC CfD settlements download and validation
- `src/cfd_payment/data/elexon.py` - Elexon AGWS (wind/solar) and system prices
- `src/cfd_payment/data/ons_gas.py` - ONS gas price data fetch

**Charting:**
- `src/cfd_payment/plotting/__main__.py` - Entry point for running all charts (`uv run python -m cfd_payment.plotting`)
- Outputs: PNG (Twitter) + interactive HTML to `docs/charts/html/`

**Documentation:**
- `mkdocs.yml` - Serve docs locally: `uv run mkdocs serve`
- Build: `uv run mkdocs build --strict`
- Deploy: `uv run mkdocs gh-deploy` (GitHub Pages)

**Testing:**
- `pytest` - Run all tests in `tests/` directory

## Deployment Pipeline (Planned)

**Refresh Workflow (`refresh.yml`):**
- Trigger: Daily cron 06:00 UTC or manual dispatch
- Steps:
  1. Checkout code
  2. Setup uv and sync dependencies
  3. Run `uv run python -m cfd_payment.refresh_all` (dirty-check pipeline)
  4. Run benchmarks: `uv run pytest tests/test_benchmarks.py`
  5. Build docs: `uv run mkdocs build --strict`
  6. Auto-commit derived data and charts via EndBug/add-and-commit
  7. Deploy to Cloudflare Pages (auto on push to main)

**Release Workflow (`deploy.yml`, planned):**
- Trigger: Git tag push (e.g., `git tag v2026.04`)
- Creates immutable versioned snapshot in `site/data/v2026-04-21/`

---

*Stack analysis: 2026-04-21*
