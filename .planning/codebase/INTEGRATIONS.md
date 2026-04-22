# External Integrations

**Analysis Date:** 2026-04-21

## APIs & External Data Sources

**LCCC (Low Carbon Contracts Company) - CfD Settlements:**
- **What it's used for:** Daily CfD generation, strike prices, payments, avoided GHG emissions
- **Endpoint:** `https://dp.lowcarboncontracts.uk/datastore/dump/{uuid}`
- **Data:** Two datasets via UUID-based API
  1. "Actual CfD Generation and avoided GHG emissions" - Daily settlement data
  2. "CfD Contract Portfolio Status" - Contract metadata (capacity, technology, status, expected start)
- **Update cadence:** Daily (weekdays), T+3 to T+7 lag from settlement
- **Our refresh:** Daily via `download_lccc_dataset()` in `src/cfd_payment/data/lccc.py`
- **Authentication:** None required
- **Configuration:** `src/cfd_payment/data/lccc_datasets.yaml` (dataset UUIDs and filenames)
- **Client:** Python `requests` library with User-Agent header
- **Local cache:** `data/raw/lccc-actual-cfd-generation.csv`, `data/raw/lccc-cfd-contract-portfolio-status.csv` (~18 MB and 76 KB)
- **Schema validation:** Pandera schemas in `src/cfd_payment/data/lccc.py` enforce column types and presence

**Elexon (National Grid ESO) - BMRS (Balancing Mechanism Real-time Settlement):**
- **What it's used for:** Actual Generation Wind/Solar (AGWS) and system balancing prices
- **Endpoints:**
  - AGWS: `https://data.elexon.co.uk/bmrs/api/v1/datasets/AGWS`
  - System prices: `https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices`
- **Data:** Half-hourly settlement periods (48 per day)
- **Update cadence:** Daily
- **Our refresh:** Daily, parallelized via ThreadPoolExecutor (7-day chunks for AGWS, 1-day chunks for prices)
- **Authentication:** None required
- **Client:** Python `requests` with `concurrent.futures.ThreadPoolExecutor` (10 workers max)
- **Local cache:** `data/raw/elexon_agws.csv` (~58 MB), `data/raw/elexon_system_prices.csv` (~27 MB)
- **Implementation:** `src/cfd_payment/data/elexon.py`
  - `_fetch_agws()` - Download AGWS in 7-day chunks
  - `_fetch_system_prices()` - Download system prices day-by-day
  - `load_elexon_wind_daily()` - Aggregate to daily average wind (MW)
  - `load_elexon_prices_daily()` - Aggregate to daily average system price (£/MWh)

**ONS (Office for National Statistics) - Gas Prices:**
- **What it's used for:** System Average Price (SAP) of gas — fuel cost basis for gas counterfactual
- **Endpoint:** `https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/output/datasets/systemaveragepricesapofgas/2026/systemaveragepriceofgasdataset160426.xlsx`
- **Data:** Daily gas price (pence/kWh thermal)
- **Update cadence:** Weekly, ~5 day lag
- **Our refresh:** Daily (cheap HTTP recheck)
- **Authentication:** None required
- **Format:** XLSX with date indexed by sheet "1.Daily SAP Gas"
- **Client:** Python `openpyxl` for reading Excel
- **Local cache:** `data/raw/ons_gas_sap.xlsx` (~125 KB)
- **Implementation:** `src/cfd_payment/data/ons_gas.py`
  - `download_dataset()` - HTTP fetch and save
  - `load_gas_price()` - Parse Excel, extract date + gas price columns

**UK ETS (Emissions Trading Scheme) - Carbon Prices:**
- **What it's used for:** Daily carbon cost component of gas counterfactual (£/tCO2)
- **Data:** Secondary market auction prices
- **Hardcoded mapping:** `src/cfd_payment/counterfactual.py` has annual carbon prices by year
  - 2018–2020: EU ETS (converted EUR→GBP)
  - 2021+: UK ETS official (GOV.UK published)
- **Current values:** 2018: £13, 2019: £22, ..., 2026: £40 per tCO2
- **Implementation:** Static dictionary updated manually on annual ETS price announcements
- **Note:** Planned future integration to scrape GOV.UK or Elexon ETS API

**NESO (National Energy System Operator):**
- **What it's used for:** Balancing Mechanism half-hourly data, balancing services costs
- **Planned sources:** `data/raw/neso/balancing-mechanism.csv`, `data/raw/neso/balancing-costs.csv`
- **Status:** Declared in ARCHITECTURE.md §4.1; implementation planned for P7–P9
- **Update cadence:** Daily (BM), Monthly (balancing costs, ~6 week lag)
- **Implementation planned:** `src/cfd_payment/data/neso.py` (not yet created)

**Ofgem - Renewables Obligation (RO) & Feed-in Tariff (FiT):**
- **What it's used for:** RO register, RO generation (ROCs issued), FiT register, FiT generation, ROC buyout/recycle prices
- **Planned sources:**
  - `data/raw/ofgem/ro-register.csv` - RO accredited stations
  - `data/raw/ofgem/ro-generation.csv` - RO ROCs issued monthly
  - `data/raw/ofgem/roc-prices.csv` - Buyout + recycle annual
  - `data/raw/ofgem/fit-register.csv` - FiT accredited installations
  - `data/raw/ofgem/fit-generation.csv` - FiT quarterly generation
- **Status:** Declared in ARCHITECTURE.md §4.1; implementation planned for P4–P6
- **Update cadence:** Monthly (RO register, FiT), Quarterly (FiT generation), Annual (ROC prices)
- **Implementation planned:** `src/cfd_payment/data/ofgem_ro.py`, `src/cfd_payment/data/ofgem_fit.py`

**EMR Delivery Body (Capacity Market):**
- **What it's used for:** Capacity Market auction clearing prices and volumes
- **Planned source:** `data/raw/emr/capacity-market-auctions.csv`
- **Status:** Declared; implementation planned for P8
- **Update cadence:** Event-driven, ~6 month auction cycles + annual CM rules
- **Implementation planned:** `src/cfd_payment/data/emr_cm.py`

**e-ROC Secondary Market:**
- **What it's used for:** ROC clearing prices on secondary market
- **Planned source:** `data/raw/e-roc/auction-clearing-prices.csv`
- **Status:** Declared; implementation planned for P11 (SEG/REGOs)
- **Update cadence:** Quarterly
- **Implementation planned:** `src/cfd_payment/data/e_roc.py`

## Data Storage

**Databases:**
- **None** - By design. OLAP workload on static Parquet files; no relational database.
- **Planned:** DuckDB (embedded, zero-ops) for analytical queries on Parquet files

**File Storage:**
- **Local filesystem (development):** `data/raw/`, `data/derived/`
- **GitHub:** All source code and data ≤100 MB per file (raw CSV/XLSX)
- **Cloudflare R2 (production):** Future storage for files >100 MB (e.g., NESO BM half-hourly history ~500 MB)
  - Expected threshold breaches: NESO BM data, possibly FiT station-month data

**Cache:**
- **None active** - Data files cached locally as CSV/XLSX, but no in-memory or Redis cache

## Authentication & Identity

**Auth Provider:**
- **None** - All data sources are public, no authentication required
- All APIs are open-access government/regulator data

## Monitoring & Observability

**Error Tracking:**
- **None** - By design, focuses on observability in code
- Tests validate data completeness: `src/cfd_payment/data/lccc.py`, `src/cfd_payment/data/elexon.py`

**Logs:**
- **Console output** - Data scrapers print download progress
  - Example: `"Downloading Elexon AGWS (wind/solar generation)..."` and chunk count
  - Example: `"Saved 29,847 rows to data/raw/elexon_agws.csv"`
- **Test logs** - Pytest output with validation errors on schema failures
- **CI logs** - GitHub Actions workflow logs (planned, not yet active)

**Validation:**
- **Pandera schemas** - Enforce column presence, type, and nullability on ingested data
  - `src/cfd_payment/data/lccc.py`: `lccc_generation_schema`, `lccc_portfolio_schema`
  - Test: `tests/data/test_lccc.py::test_load_dataset()` validates schema on real data
- **Manual benchmarks** - `tests/test_benchmarks.py` (planned) will cross-check totals vs. external sources

## CI/CD & Deployment

**Hosting:**
- **Primary:** Cloudflare Pages (free tier, auto-deploy on push to main)
- **Fallback:** GitHub Pages (if Cloudflare changes terms)
- **Custom domain:** Pending (planned: `uksubsidytracker.org` or `renewablescost.uk`)

**CI Pipeline:**
- **Provider:** GitHub Actions (free tier)
- **Refresh workflow:** `refresh.yml` (planned, not yet deployed)
  - Trigger: Daily cron 06:00 UTC + manual dispatch
  - Steps: sync deps → scrape data → rebuild Parquet → regenerate charts → build docs → auto-commit → deploy
  - Runtime: ~3–5 minutes typical, <30 minute timeout
- **Deploy workflow:** `deploy.yml` (planned)
  - Trigger: Tag push (e.g., `git tag v2026.04`)
  - Action: Creates immutable versioned snapshot in `site/data/v2026-04-21/`

**Version Control:**
- **Git + GitHub** - Standard; no special integrations

## Environment Configuration

**Required env vars:**
- **None currently** - All configuration hardcoded or in YAML/Python modules
- **Future (pydantic-settings):** May add for API keys if auth is needed

**Secrets location:**
- **None in use** - Public data sources only
- `.env` not present and not required

**Lockfile:**
- `uv.lock` - Maintained, includes all transitive dependencies

## Webhooks & Callbacks

**Incoming:**
- **None** - Static generation pipeline, no webhooks

**Outgoing:**
- **None** - Data is published to Cloudflare Pages and GitHub, no push callbacks
- **Planned:** Cross-post essays to Substack (manual, not automated)

## Data Refresh Orchestration

**Dirty-check implementation:**
- `src/cfd_payment/refresh_all.py` (planned, sketch in ARCHITECTURE.md §7.3)
- Each scraper writes sidecar `<filename>.meta.json` with:
  - Retrieval timestamp
  - Upstream HTTP status
  - Source file SHA-256
  - Publisher's "last modified" timestamp
- On daily refresh: compare upstream SHA against cached SHA; only rebuild downstream if changed
- Benefit: ~95% of days skip expensive Parquet regeneration when sources unchanged

**Provenance tracking (planned):**
- `site/data/manifest.json` - Machine-readable index of all published datasets
  - Schema: `version`, `generated_at`, `methodology_version`, `datasets[]` with `sources[]`
  - Each dataset source includes: name, upstream_url, retrieved_at, source_sha256
  - Implementation: `src/cfd_payment/publish/manifest.py` (planned for P3)

**Data publication (planned):**
- `site/data/latest/` - Overwritten daily
- `site/data/v2026-04-21/` - Immutable versioned snapshots on tagged release
- Both serve Parquet (canonical) + CSV (journalist convenience) + schema.json (column metadata)

---

*Integration audit: 2026-04-21*
