# Architecture

**Analysis Date:** 2026-04-21

## Current State vs Target

This document maps the **existing architecture** against the target defined in `/ARCHITECTURE.md` (the authoritative design document). Major gaps between current and target state are flagged.

---

## Pattern Overview

**Overall:** Three-layer data pipeline feeding into a single-scheme plotting and documentation system.

**Current State:** Early-stage prototype focused on CfD scheme only.

**Key Characteristics:**
- Source → Derived → Published three-layer architecture (defined; partially implemented)
- CfD scheme only; no other scheme modules yet
- Static site generation via MkDocs (readthedocs theme)
- Plotly-based charting with custom dark theme
- DuckDB and Parquet planned but not yet implemented; using CSV + pandas currently
- Python 3.11+, uv package manager, pytest for testing

---

## Layers

### 4.1 Source Layer (`data/raw/` — Target state; partial current state)

**Purpose:** Preserve primary data exactly as published.

**Location:** `/Users/rjl/Code/github/cfd-payment/data/`

**Current Contents:**
- `lccc-actual-cfd-generation.csv` — LCCC daily settlement (raw)
- `lccc-cfd-contract-portfolio-status.csv` — LCCC portfolio snapshot (raw)
- `elexon_agws.csv` — Actual Generation Wind/Solar (raw)
- `elexon_system_prices.csv` — Balancing system prices (raw)
- `ons_gas_sap.xlsx` — ONS System Average Price of gas (raw)

**Status:** Only LCCC, Elexon, and ONS data present. Missing Ofgem RO/FiT, NESO balancing, EMR capacity market, UK ETS, e-ROC. No meta.json sidecars yet.

**Gap:** Target specifies source scrapers (`src/cfd_payment/data/scrapers/`) — currently only basic loaders exist in `src/cfd_payment/data/lccc.py`, `elexon.py`, `ons_gas.py`. No download/refresh logic. No hash tracking or versioning.

### 4.2 Derived Layer (`data/derived/` — Not yet implemented)

**Purpose:** Analytical tables produced by scheme modules, in Parquet format.

**Current State:** Directory does not exist. No Parquet pipeline.

**Gap:** Target calls for per-scheme derived tables (`data/derived/cfd/station_month.parquet`, `annual_summary.parquet`, etc.). Current codebase loads raw CSVs directly into pandas DataFrames at chart time; no persistent derived layer.

### 4.3 Publishing Layer (`site/data/` — Not yet implemented)

**Purpose:** Public URLs for data, versioned snapshots.

**Current State:** Directory does not exist. No manifest.json.

**Gap:** Target specifies CSV mirrors, schema.json, manifest.json. Not yet built.

---

## Data Flow

### CfD Pipeline (Current — Only Working Path)

```
1. Load raw LCCC data
   src/cfd_payment/data/lccc.py → load_lccc_dataset()
   ↓
2. Load counterfactual components
   src/cfd_payment/data/ons_gas.py → load_gas_price()
   src/cfd_payment/data/elexon.py → load_elexon_wind_daily()
   ↓
3. Compute counterfactual
   src/cfd_payment/counterfactual.py → compute_counterfactual()
   (Gas fuel cost + carbon cost + O&M)
   ↓
4. Build chart-specific aggregations (in-memory pandas)
   src/cfd_payment/plotting/subsidy/*.py
   Each chart._prepare() aggregates raw data to grain needed
   ↓
5. Generate Plotly figure
   ChartBuilder.create_*() + traces
   ↓
6. Export to PNG (Twitter) + HTML
   src/cfd_payment/plotting/utils.py → save_chart()
   Outputs: docs/charts/html/{chart_name}_twitter.png
```

**State Management:** None persistent. Each chart run reloads raw CSV from disk, re-aggregates, re-renders. No caching.

**Target vs Current:** Target specifies a derived layer that sits between raw and charts. Currently missing entirely.

---

## Key Abstractions

### ChartBuilder

**Purpose:** Standardized chart creation with dark theme, formatting, export.

**Location:** `src/cfd_payment/plotting/chart_builder.py`

**Pattern:** Class with methods for creating figures, formatting axes, and saving outputs.

```python
builder = ChartBuilder(title="My Chart", height=600)
fig = builder.create_basic()
# Add traces...
builder.save(fig, "my_chart", export_twitter=True)
```

**Used by:** Every chart in `src/cfd_payment/plotting/*/`.

### Counterfactual Model

**Purpose:** Single source of truth for gas-only electricity cost.

**Location:** `src/cfd_payment/counterfactual.py`

**Formula (from §6.2 of ARCHITECTURE.md):**
```
counterfactual £/MWh =
  fuel cost (ONS gas SAP / 0.55 CCGT efficiency)
  + carbon cost (UK ETS £/tCO2 × 0.184 tCO2/MWh thermal / 0.55)
  + O&M £5/MWh (existing fleet, capex sunk)
```

**Used by:** All CfD charts that compute premium.

**Gap:** No test coverage pinning this formula (target specifies `tests/test_counterfactual.py`).

### Plotting Theme

**Purpose:** Unified dark theme for all charts.

**Location:** `src/cfd_payment/plotting/theme.py`, `colors.py`

**Implementation:** Plotly template registered via `register_cfd_dark_theme()`.

**Color Conventions (from ARCHITECTURE.md §13.3):**
- Offshore Wind: `#1f77b4`
- Onshore Wind: `#6baed6`
- Biomass (Drax/Lynemouth): `#d62728`
- Solar PV: `#ff7f0e`

---

## Entry Points

### Chart Generation

**Location:** `src/cfd_payment/plotting/__main__.py`

**Triggers:** `uv run python -m cfd_payment.plotting` (manual) or CI workflow.

**Responsibilities:**
1. Import all chart generators from `plotting/*/`
2. Call each chart's `main()` function
3. Write PNG + HTML to `docs/charts/html/`

**Current Calls (11 charts):**
```
cfd_vs_gas_total()      # cfd_vs_gas_cost.py
cfd_dynamics()          # cfd_dynamics.py
cfd_payments_by_category()
scissors()              # [CUT per ARCHITECTURE.md]
subsidy_per_avoided_co2_tonne()
bang_for_buck()
remaining_obligations()
lorenz()

cf_monthly(), cf_seasonal()
heatmap(), load_duration(), rolling_minimum()
capture_ratio(), price_vs_wind()
```

**Gap:** Scissors is still called (§5.2 marks it CUT). No scheme module protocol yet.

### Documentation Site

**Location:** `mkdocs.yml`, `docs/index.md`

**Build:** `uv run mkdocs build` (or `mkdocs serve` locally)

**Theme:** `readthedocs` (target specifies migration to `material`)

**Current Sections:**
- Home (`docs/index.md`)
- Charts overview + 3 CfD chart pages
- Gas counterfactual methodology

**Gap:** No theme pages (Cost, Recipients, Efficiency, Cannibalisation, Reliability). No scheme detail pages. No per-chart deep-dive pages for PRODUCTION charts.

---

## Error Handling

**Strategy:** Minimal.

**Patterns:**
- Pandera schema validation on CSV ingest (`src/cfd_payment/data/lccc.py`)
- `dropna()` and null-checks in chart preparation
- Tests marked `@pytest.mark.skip` for tests that hit live services

**Gap:** No systematic error handling strategy. No validation pipeline. No test for schema conformance across all tables (target specifies `tests/test_schemas.py`).

---

## Cross-Cutting Concerns

**Logging:** `print()` statements in some data loaders. No structured logging framework.

**Validation:** Pandera used selectively in data layer; not systematic across pipeline.

**Authentication:** None required (public data sources).

**Testing:** 2 test files (`test_lccc.py`, `test_ons.py`), both minimal. Target specifies:
- `test_counterfactual.py` (formula pinning)
- `test_schemas.py` (Parquet conformance)
- `test_aggregates.py` (row conservation)
- `test_benchmarks.py` (external cross-check)
- `test_determinism.py` (byte-identical output)

---

## Scheme Module Contract

**Target (§6.1):** Every `schemes/<scheme>/` exposes:
```python
DERIVED_DIR = Path("data/derived/<scheme>")

def upstream_changed() -> bool:
def refresh() -> None:
def rebuild_derived() -> None:
def regenerate_charts() -> None:
def validate() -> list[str]:
```

**Current State:** No scheme modules exist. CfD logic is scattered across:
- `src/cfd_payment/counterfactual.py`
- `src/cfd_payment/plotting/subsidy/*.py` (chart-level)
- `src/cfd_payment/data/*.py` (loaders)

**Gap:** RO, FiT, SEG, Constraints, Capacity Market, Balancing, Grid modules all missing (target: deliver across P4–P11).

---

## Refresh Cadence

**Current:** Manual. Run `uv run python -m cfd_payment.plotting` to regenerate charts.

**Target:** GitHub Actions daily refresh at 06:00 UTC (§7.2). Dirty-check logic (§7.3) skips schemes whose sources haven't changed.

**Gap:** No CI/CD pipeline. No source hash tracking. No automated deployment.

---

## Hosting & Deployment

**Current:** Repo is on GitHub; docs site built manually or via legacy GitHub Pages setup. No Cloudflare Pages.

**Target:** Cloudflare Pages for static hosting. Daily automated deploys.

**Gap:** No continuous deployment configured.

---

## Publishing Layer Contract

**Target (§4.3):** Every scheme output:
```
site/data/latest/<scheme>/<grain>.{parquet,csv}
site/data/latest/<scheme>/<grain>.schema.json
site/data/manifest.json
site/data/v<YYYY-MM-DD>/...  (versioned snapshots)
```

**Current State:** Not implemented. Outputs go directly to `docs/charts/html/`.

**Gap:** No data publication for external consumers. No manifest. No schema.json sidecars.

---

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

---

*Architecture mapping: 2026-04-21*
