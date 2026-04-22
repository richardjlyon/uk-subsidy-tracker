# Codebase Structure

**Analysis Date:** 2026-04-21

## Directory Layout

```
cfd-payment/                                    # Repo root (to be renamed uk-subsidy-tracker)
├── README.md                                   # Project overview
├── ARCHITECTURE.md                             # [Exists but is UNTRACKED; should be committed per P0]
├── RO-MODULE-SPEC.md                           # [UNTRACKED; needed per P0]
├── pyproject.toml                              # Python project metadata
├── uv.lock                                     # uv lockfile
├── mkdocs.yml                                  # MkDocs config (theme: readthedocs → material per P0)
├── pyrightconfig.json                          # Type checking config (optional)
│
├── .github/
│   └── workflows/                              # [NOT YET CREATED]
│       ├── refresh.yml                         # Daily scrape + rebuild + publish (P1)
│       └── deploy.yml                          # On tag: versioned snapshot (P1)
│
├── data/                                       # Data files (three-layer architecture)
│   ├── raw/                                    # Source layer (§4.1) — files as published
│   │   ├── lccc-actual-cfd-generation.csv     # LCCC daily settlement
│   │   ├── lccc-cfd-contract-portfolio-status.csv
│   │   ├── elexon_agws.csv                    # Actual Generation Wind/Solar
│   │   ├── elexon_system_prices.csv
│   │   └── ons_gas_sap.xlsx
│   │   # Missing: ofgem_ro_register.csv, ofgem_fit_register.csv, etc. (added in P4–P11)
│   │   # Missing: .meta.json sidecars for source tracking
│   │
│   └── derived/                                # Derived layer (§4.2) — NOT YET CREATED
│       # Target: Parquet files per scheme
│       # cfd/station_month.parquet, annual_summary.parquet, etc.
│       # ro/, fit/, seg/, constraints/, capacity_market/, balancing/, grid/
│
├── src/
│   └── cfd_payment/                            # Main Python package (to be renamed uk_subsidy_tracker)
│       ├── __init__.py                         # PROJECT_ROOT, DATA_DIR, OUTPUT_DIR constants
│       ├── counterfactual.py                   # Gas counterfactual formula (shared across schemes)
│       │                                        # compute_counterfactual() + constants
│       │
│       ├── data/                               # Data loading and scraping utilities
│       │   ├── __init__.py                     # Exports load_lccc_dataset, load_gas_price, load_elexon_*
│       │   ├── lccc.py                         # LCCC dataset config + loader
│       │   │                                    # Pandera schema for LCCC generation/portfolio
│       │   ├── lccc_datasets.yaml              # LCCC dataset URLs and UUIDs
│       │   ├── elexon.py                       # Elexon AGWS + system prices loaders
│       │   ├── ons_gas.py                      # ONS gas SAP loader
│       │   └── utils.py                        # Shared headers + download utilities
│       │   # Missing: scrapers/ subdir per target (lccc.py, ofgem_ro.py, ofgem_fit.py, etc.)
│       │   # Missing: refresh logic, hash tracking, .meta.json creation
│       │
│       ├── schemes/                            # [NOT YET CREATED per P1]
│       │   # Target structure (§6):
│       │   ├── cfd/
│       │   │   ├── __init__.py                 # DERIVED_DIR, upstream_changed(), refresh(), etc.
│       │   │   ├── cost_model.py               # Station-month build
│       │   │   ├── aggregation.py              # Rollups to annual/by-tech/by-round
│       │   │   └── forward_projection.py
│       │   ├── ro/
│       │   ├── fit/
│       │   ├── seg/
│       │   ├── constraints/
│       │   ├── capacity_market/
│       │   ├── balancing/
│       │   └── grid/
│       │   # Consistency enforced by base class or protocol in __init__.py
│       │
│       ├── plotting/                           # Chart generation (currently only CfD)
│       │   ├── __init__.py                     # Exports ChartBuilder, theme, colors
│       │   ├── __main__.py                     # Entry point: python -m cfd_payment.plotting
│       │   │                                    # Calls main() on all 15 chart files (11 + scissors + old files)
│       │   ├── __pycache__/
│       │   ├── chart_builder.py                # ChartBuilder class: create_basic(), format_axes(), save()
│       │   ├── colors.py                       # Color palettes (TECHNOLOGY_COLORS, GENERATION_COLORS, etc.)
│       │   ├── theme.py                        # Plotly dark theme registration
│       │   ├── utils.py                        # Axis formatting, dual-axis patterns, save_chart()
│       │   │
│       │   ├── subsidy/                        # CfD-specific charts (§5.2 verdict column)
│       │   │   ├── __init__.py
│       │   │   ├── cfd_dynamics.py             # PRODUCTION: 4-panel volume×price×premium×cumulative
│       │   │   ├── cfd_vs_gas_cost.py          # PRODUCTION: two cash-flow channels
│       │   │   ├── remaining_obligations.py    # PRODUCTION: forward locked-in cost
│       │   │   ├── cfd_payments_by_category.py # PROMOTE → PRODUCTION: where money goes
│       │   │   ├── lorenz.py                   # PROMOTE → PRODUCTION: concentration analysis (6 projects = 50%)
│       │   │   ├── subsidy_per_avoided_co2_tonne.py # PROMOTE → PRODUCTION: flagship on theme C
│       │   │   ├── bang_for_buck.py            # DOCUMENTED: secondary on theme C
│       │   │   ├── scissors.py                 # CUT: strictly dominated by cfd_dynamics (remove in P2)
│       │   │   └── bang_for_buck_old.py        # DELETE: obsolete (remove in P2)
│       │   │
│       │   ├── capacity_factor/                # Reliability theme charts
│       │   │   ├── __init__.py
│       │   │   ├── monthly.py                  # DOCUMENTED: secondary
│       │   │   └── seasonal.py                 # PROMOTE → PRODUCTION: DESNZ assumption challenge
│       │   │
│       │   ├── intermittency/                  # Reliability theme charts
│       │   │   ├── __init__.py
│       │   │   ├── generation_heatmap.py       # PROMOTE → PRODUCTION: visual hook
│       │   │   ├── load_duration.py            # DOCUMENTED: academics want this
│       │   │   └── rolling_minimum.py          # PROMOTE → PRODUCTION: drought/"longer than battery" argument
│       │   │
│       │   └── cannibalisation/                # Cannibalisation theme charts
│       │       ├── __init__.py
│       │       ├── capture_ratio.py            # PROMOTE → PRODUCTION: flagship on theme D
│       │       └── price_vs_wind.py            # DOCUMENTED: secondary on theme D
│       │
│       ├── publish/                            # [NOT YET CREATED per P3]
│       │   ├── __init__.py
│       │   ├── manifest.py                     # Builds site/data/manifest.json
│       │   ├── snapshot.py                     # Versioned snapshot on release tag
│       │   └── csv_mirror.py                   # Writes CSV alongside Parquet
│       │
│       └── refresh_all.py                      # [NOT YET CREATED per P1] CI entry point
│                                                # Dirty-check each scheme, rebuild only if changed
│
├── tests/
│   ├── conftest.py                             # [MISSING] pytest fixtures
│   ├── test_counterfactual.py                  # [MISSING per P1] Pin the formula
│   ├── test_schemas.py                         # [MISSING per P1] Parquet schema conformance
│   ├── test_aggregates.py                      # [MISSING per P1] Row conservation
│   ├── test_benchmarks.py                      # [MISSING per P1] Benchmark against external (REF, Turver, Ofgem)
│   ├── test_determinism.py                     # [MISSING per P1] Byte-identical output
│   └── data/
│       ├── __init__.py
│       ├── test_lccc.py                        # Load LCCC config; skip live download test
│       └── test_ons.py                         # [Minimal]
│
├── docs/                                       # MkDocs source (for static site generation)
│   ├── index.md                                # Homepage: 3 headline numbers + embedded CfD dynamics chart
│   │                                            # [Gap: target specifies portal top strip with scheme grid]
│   │
│   ├── charts/
│   │   ├── index.md                            # Charts overview (mentions 3 PRODUCTION CfD charts)
│   │   ├── html/                               # Generated chart assets (PNGs + HTMLs) [.gitignore]
│   │   │   ├── subsidy_cfd_dynamics_twitter.png
│   │   │   ├── subsidy_cfd_vs_gas_cost_twitter.png
│   │   │   ├── subsidy_remaining_obligations_twitter.png
│   │   │   └── [11 more HTML + PNG pairs]
│   │   │
│   │   └── subsidy/
│   │       ├── cfd-dynamics.md                 # PRODUCTION: 4-panel methodology
│   │       ├── cfd-vs-gas-cost.md              # PRODUCTION: cash-flow decomposition
│   │       ├── remaining-obligations.md        # PRODUCTION: forward cost
│       │       ├── cfd-dynamics.md             # [Renamed from cfd_dynamics.md]
│       │       ├── cfd-vs-gas-cost.md
│       │       └── remaining-obligations.md
│       │
│       └── [MISSING per target §5.5]
│           ├── themes/                         # [NOT YET CREATED]
│           │   ├── cost/
│           │   ├── recipients/
│           │   ├── efficiency/
│           │   ├── cannibalisation/
│           │   └── reliability/
│           ├── schemes/                        # [NOT YET CREATED]
│           │   ├── cfd.md
│           │   ├── ro.md
│           │   └── ...
│           └── data/                           # [NOT YET CREATED]
│               ├── index.md
│               ├── schema.md
│               └── citation.md
│
│   └── technical-details/
│       ├── index.md                            # [UNTRACKED per git status]
│       └── gas-counterfactual.md               # [UNTRACKED] Detailed methodology + formula
│
├── site/                                       # MkDocs build output (generated) [.gitignore]
│   ├── index.html
│   ├── charts/
│   ├── (other static files)
│   └── data/                                   # [NOT YET CREATED per P3]
│       └── manifest.json
│
├── .planning/
│   └── codebase/                               # [Newly created for this analysis]
│       ├── ARCHITECTURE.md                     # This file
│       └── STRUCTURE.md                        # Current file
│
├── .gitignore
├── .git/
├── .venv/                                      # Python virtual environment [.gitignore]
└── .claude/                                    # Claude Code metadata [.gitignore]
```

---

## Directory Purposes

### `data/` — Three-layer data pipeline

**Purpose:** Source → Derived → Published lifecycle.

**Current:** Only raw CSV files present (source layer partial).

**Contains:** CSVs from LCCC, Elexon, ONS.

**Key files:**
- `lccc-actual-cfd-generation.csv`: 18 MB, daily settlement data
- `elexon_agws.csv`: 58 MB, wind/solar generation
- `elexon_system_prices.csv`: 27 MB, system prices
- `ons_gas_sap.xlsx`: 125 KB, gas prices

**Missing:** Ofgem RO/FiT register, NESO balancing, EMR capacity market. No .meta.json. No derived/ directory.

### `src/cfd_payment/` — Main package

**Purpose:** All business logic and chart generation.

**Contains:** Data loaders, counterfactual model, plotting utilities, chart generators.

**Key structure:**
- `counterfactual.py`: Shared formula (gas fuel cost + carbon + O&M)
- `data/`: CSV loaders with Pandera schema validation
- `plotting/`: ChartBuilder abstraction + theme + all 15 chart files
- `schemes/`: [NOT YET CREATED] Will contain per-scheme modules (cfd, ro, fit, etc.)

### `src/cfd_payment/plotting/` — Chart generation

**Purpose:** Generate production charts (PNG for Twitter, HTML for embedding).

**Contains:** 15 chart files across 4 subdirectories.

**Entry point:** `__main__.py` calls `main()` on each chart.

**Output:** `docs/charts/html/{chart_name}_twitter.png` + `.html`

**Current chart count:** 11 production + scissors + bang_for_buck_old = 13 files.
- Subsidy: 9 files
- Capacity factor: 2 files
- Intermittency: 3 files
- Cannibalisation: 2 files

**Gap:** Target lists 15 production charts (after triage). Scissors is marked CUT but still active.

### `docs/` — Static site source (MkDocs)

**Purpose:** Human-readable documentation for all charts and methodology.

**Contains:** Markdown files that become the static site.

**Key files:**
- `index.md`: Homepage (currently just "CfD Payment Analysis" heading + 3 charts)
- `charts/index.md`: Overview
- `charts/subsidy/*.md`: Individual chart pages (3 PRODUCTION CfD pages)
- `technical-details/gas-counterfactual.md`: Methodology

**Generated assets:** `charts/html/` (PNGs + interactive HTMLs) [.gitignore]

**Gap:** No theme pages (Cost, Recipients, Efficiency, Cannibalisation, Reliability per §5). No scheme detail pages. No per-chart deep-dive for PROMOTE → PRODUCTION charts. Portal top strip not yet designed (target §5.6).

### `tests/` — Test suite

**Purpose:** Validate data integrity, formulas, and output consistency.

**Current:** 2 minimal test files.

**Missing:**
- `test_counterfactual.py`: Pin the formula against known inputs
- `test_schemas.py`: Parquet file schema conformance
- `test_aggregates.py`: Sum conservation (no row leakage)
- `test_benchmarks.py`: Match external benchmarks (REF, Turver, Ofgem) within tolerance
- `test_determinism.py`: Same input → byte-identical Parquet output
- `conftest.py`: pytest fixtures

---

## Key File Locations

### Entry Points

- **Chart generation:** `src/cfd_payment/plotting/__main__.py`
  - Invoked by: `uv run python -m cfd_payment.plotting`
  - Calls all 15 chart generators sequentially
  - Outputs to `docs/charts/html/`

- **Site build:** `mkdocs.yml` + `docs/index.md`
  - Invoked by: `uv run mkdocs build` or `mkdocs serve`
  - Reads from `docs/` tree
  - Outputs to `site/` (generated)

- **CI entry point (future):** `src/cfd_payment/refresh_all.py` (not yet created per P1)
  - Will orchestrate daily refresh: scrape → derive → charts → publish

### Configuration

- `pyproject.toml`: Python dependencies, project metadata
- `mkdocs.yml`: MkDocs config (theme, nav structure, plugins)
- `pyrightconfig.json`: Type checking (optional)
- `uv.lock`: Exact pinned versions (generated by uv)

### Core Logic

- **Counterfactual formula:** `src/cfd_payment/counterfactual.py` (source of truth for gas cost)
- **Chart builder abstraction:** `src/cfd_payment/plotting/chart_builder.py` (standardizes all charts)
- **Color palette:** `src/cfd_payment/plotting/colors.py` (TECHNOLOGY_COLORS, etc.)
- **Data loaders:** `src/cfd_payment/data/lccc.py`, `ons_gas.py`, `elexon.py`

### Testing

- **Data tests:** `tests/data/test_lccc.py`, `test_ons.py`
- **Missing test suite:** §9.6 of ARCHITECTURE.md specifies 5 essential test classes (300–500 lines total)

---

## Naming Conventions

### Files

**Pattern: snake_case with descriptive names**

Examples:
- `cfd_dynamics.py`: Chart file; chart ID would be `cost_cfd_dynamics` (§13.1)
- `lccc-actual-cfd-generation.csv`: Raw CSV filename matches upstream publisher's schema
- `station_month.parquet`: Derived table grain in snake_case (target §13.1)

**Current:** Mostly consistent. One exception: `bang_for_buck_old.py` (to be deleted per P2).

### Directories

**Pattern: snake_case, grouped by function**

Examples:
- `plotting/subsidy/` — subsidy economics charts
- `plotting/capacity_factor/` — reliability charts
- `data/` → `data/raw/` and `data/derived/` (target structure)
- `schemes/cfd/`, `schemes/ro/` (target structure)

**Current:** Mostly follows this. Missing: top-level scheme module directory.

### Functions/Classes

**Pattern: snake_case functions, PascalCase classes**

Examples:
- `ChartBuilder` (class in chart_builder.py)
- `compute_counterfactual()` (function)
- `load_lccc_dataset()` (function)

### Variables

**Pattern: snake_case**

Examples:
- `cfd_generation_mwh` (from LCCC CSV)
- `strike_price_gbp_per_mwh`

---

## Where to Add New Code

### New Chart

1. **Pick a theme/scheme:** e.g., "recipients / RO scheme"
2. **Create file:** `src/cfd_payment/plotting/per_scheme/ro/recipients.py` (target structure)
   - Or current: `src/cfd_payment/plotting/<theme>/` if theme-level
3. **Implement:** `def main(): ...` function that builds and saves figure
4. **Register:** Add call to `__main__.py` if production-ready
5. **Document:** Add `.md` page under `docs/themes/<theme>/` (target §5.5)

### New Scheme Module

1. **Create directory:** `src/cfd_payment/schemes/ro/`
2. **Implement protocol (from §6.1):**
   ```python
   DERIVED_DIR = Path("data/derived/ro")
   
   def upstream_changed() -> bool: ...
   def refresh() -> None: ...
   def rebuild_derived() -> None: ...
   def regenerate_charts() -> None: ...
   def validate() -> list[str]: ...
   ```
3. **Data models:** Add Pydantic schemas for all Parquet tables to `src/cfd_payment/schemas/ro.py` (target structure)
4. **Aggregation:** Build `cost_model.py` (station-month), `aggregation.py` (rollups), `forward_projection.py`
5. **Charts:** Create S1–S5 diagnostic set under `plotting/per_scheme/ro/` (target §5.3)
6. **Tests:** Add `tests/test_ro.py` with benchmarks

### New Shared Utility

- **Plotting helper:** Add to `src/cfd_payment/plotting/utils.py` or `chart_builder.py`
- **Data loader:** Add to `src/cfd_payment/data/<source>.py` (e.g., `ofgem_ro.py`)
- **Common model:** Add to `src/cfd_payment/counterfactual.py` or create new module

### Updating Counterfactual

- **File:** `src/cfd_payment/counterfactual.py`
- **Affects:** All charts using premium; every deployment triggers test_benchmarks.py
- **Governance:** Changes documented in `CHANGES.md`, methodology_version bumped in manifest.json (target §9.4)

---

## Special Directories

### `docs/charts/html/` (Generated, .gitignore)

**Purpose:** Plotly export outputs (PNGs + interactive HTMLs).

**Generated by:** `src/cfd_payment/plotting/__main__.py`

**Contains:**
- `subsidy_cfd_dynamics_twitter.png` (1200×675 px)
- `subsidy_cfd_dynamics.html` (interactive, responsive)
- [Similar pairs for 14 other charts]

**Committed:** No (in .gitignore). Regenerated on every build.

### `site/` (Generated, .gitignore)

**Purpose:** MkDocs build output.

**Generated by:** `mkdocs build`

**Contains:** Static HTML site (browsable via local server or deployed to Cloudflare Pages).

**Committed:** No (in .gitignore).

### `.planning/codebase/` (New)

**Purpose:** Mapping documents for GSD orchestration.

**Contains:**
- `ARCHITECTURE.md`: Pattern, layers, abstractions, entry points (this document)
- `STRUCTURE.md`: File layout, naming, where to add code (current file)

**Committed:** Yes. Supports downstream planning/execution phases.

---

## Project Layout Gaps vs Target

| Item | Current | Target | Phase |
|------|---------|--------|-------|
| Repo name | `cfd-payment` | `uk-subsidy-tracker` | P0 |
| MkDocs theme | `readthedocs` | `material` | P0 |
| ARCHITECTURE.md committed | No (untracked) | Yes | P0 |
| RO-MODULE-SPEC.md | No | Yes | P0 |
| Scheme modules | None (cfd scattered) | 8 modules (cfd, ro, fit, seg, constraints, cm, balancing, grid) | P1–P11 |
| Derived layer (Parquet) | Missing | data/derived/{scheme}/ | P3 |
| Publishing layer | Missing | site/data/{latest,v*}/ + manifest.json | P3 |
| Theme pages | Missing | docs/themes/{cost,recipients,efficiency,cannibalisation,reliability}/ | P2 |
| Scheme detail pages | Missing | docs/schemes/{cfd,ro,fit,...}.md | P4+ |
| Portal top strip | Missing | Portal homepage per iamkate pattern (§5.6) | P5 |
| CI/CD workflows | Missing | .github/workflows/{refresh,deploy}.yml | P1 |
| Test suite | 2 files (minimal) | 5 classes (300–500 LOC) | P1 |
| Data publication | Missing | Parquet + CSV + schema.json + manifest.json | P3 |

---

*Structure analysis: 2026-04-21*
