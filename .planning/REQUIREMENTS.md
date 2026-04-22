# Requirements: UK Renewable Subsidy Tracker

**Defined:** 2026-04-21
**Core Value:** Every headline number on the site is reproducible, traceable to a primary regulator source, methodologically bulletproof, and survives hostile reading.

## v1 Requirements

Requirements for the portal's first public release: expansion from single-scheme CfD prototype to eight-scheme portal with adversarial-proof methodology infrastructure. Derived from ARCHITECTURE.md §11 phased plan (P0-P11) and §5.2 chart triage.

### Foundation

- [ ] **FND-01**: Repo renamed `cfd-payment` → `uk-subsidy-tracker` (Python package path, GitHub repo, pyproject.toml, imports)
- [ ] **FND-02**: MkDocs theme switched from `readthedocs` to `material`; `mkdocs build --strict` passes
- [ ] **FND-03**: `ARCHITECTURE.md`, `RO-MODULE-SPEC.md`, `CHANGES.md`, `CITATION.cff` committed at repo root

### Test & Benchmark Scaffolding

- [ ] **TEST-01**: `tests/test_counterfactual.py` pins the gas counterfactual formula (fuel + carbon + O&M) against known inputs
- [ ] **TEST-02**: `tests/test_schemas.py` validates every derived Parquet file against Pydantic schemas
- [ ] **TEST-03**: `tests/test_aggregates.py` proves `sum by year` = `sum by year × technology`; no row leakage
- [ ] **TEST-04**: `tests/test_benchmarks.py` reconciles totals against Ben Pile (2021 + 2026), REF subset, Turver aggregate; documents divergences
- [ ] **TEST-05**: `tests/test_determinism.py` proves rebuilds produce byte-identical Parquet output on unchanged sources
- [ ] **TEST-06**: GitHub Actions CI workflow runs pytest on every push to `main`

### Chart Triage & Theme Pages

- [ ] **TRIAGE-01**: `bang_for_buck_old.py` deleted and `scissors.py` removed (CUT verdict from §5.2) — preserved in git history only
- [ ] **TRIAGE-02**: Docs pages written for seven PROMOTE charts: `cfd_payments_by_category`, `lorenz`, `subsidy_per_avoided_co2_tonne`, `capture_ratio`, `capacity_factor/seasonal`, `intermittency/generation_heatmap`, `intermittency/rolling_minimum`
- [ ] **TRIAGE-03**: `docs/` restructured into five theme directories (`cost/`, `recipients/`, `efficiency/`, `cannibalisation/`, `reliability/`) with narrative index, methodology, and per-chart pages
- [ ] **TRIAGE-04**: Every PRODUCTION chart on the site is reachable from its theme page navigation

### Publishing Layer

- [ ] **PUB-01**: `src/uk_subsidy_tracker/publish/manifest.py` builds `site/data/manifest.json` with provenance (retrieval timestamp, SHA-256, upstream URL, pipeline version) per dataset
- [ ] **PUB-02**: `publish/csv_mirror.py` writes CSV alongside every published Parquet (journalist convenience)
- [ ] **PUB-03**: `publish/snapshot.py` creates versioned snapshot (`site/data/v<date>/`) on tagged release; immutable
- [ ] **PUB-04**: `docs/data/index.md` documents how journalists and academics use the published datasets
- [ ] **PUB-05**: Three-layer data pipeline (`data/raw/` → `data/derived/` → `site/data/`) operational end-to-end for CfD scheme
- [ ] **PUB-06**: External consumer can fetch `manifest.json`, follow a URL, and retrieve Parquet/CSV with provenance metadata

### Renewables Obligation (RO) Module

- [ ] **RO-01**: Ofgem RO scraper populates `data/raw/ofgem/{ro-register,ro-generation,roc-prices}.csv` with sidecar meta.json
- [ ] **RO-02**: `src/uk_subsidy_tracker/schemes/ro/` module conforms to §6.1 contract (`upstream_changed`, `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`)
- [ ] **RO-03**: RO derived Parquet tables: `station_month`, `annual_summary`, `by_technology`, `by_allocation_round`, `forward_projection`
- [ ] **RO-04**: RO S2 dynamics chart (4-panel), S3 cost by technology, S4 concentration/Lorenz, S5 forward commitment published
- [ ] **RO-05**: RO scheme docs page (`docs/schemes/ro.md`) + theme-page integration for Cost and Recipients themes
- [ ] **RO-06**: RO aggregate 2011-2022 benchmarks within 3% of Turver's published totals

### Feed-in Tariff (FiT) Module

- [ ] **FIT-01**: Ofgem FiT scraper populates `data/raw/ofgem/{fit-register,fit-generation}.csv` with sidecar meta.json
- [ ] **FIT-02**: `schemes/fit/` module conforming to §6.1 contract
- [ ] **FIT-03**: FiT S2 dynamics, S3 cost by technology, S5 forward commitment charts (S4 n/a — 800k domestic installs)
- [ ] **FIT-04**: FiT scheme docs page + scheme-grid tile

### Constraint Payments Module

- [ ] **CON-01**: NESO Balancing Mechanism scraper populates `data/raw/neso/balancing-mechanism.csv`
- [ ] **CON-02**: `schemes/constraints/` module conforming to §6.1 contract (half-hourly data rolled up to station-month)
- [ ] **CON-03**: Constraint S2-S5 charts published
- [ ] **CON-04**: "£X bn paid to switch off" headline figure on constraint scheme page
- [ ] **CON-05**: Constraint payments appear as growing line-item in cross-scheme X1 chart

### Capacity Market (CM) Module

- [ ] **CM-01**: EMR Delivery Body scraper populates `data/raw/emr/capacity-market-auctions.csv`
- [ ] **CM-02**: `schemes/capacity_market/` module conforming to §6.1 contract
- [ ] **CM-03**: CM modified S2 (no gas counterfactual), S3, S4, S5 charts published
- [ ] **CM-04**: Attribution caveat (how much CM cost is "caused by renewables") documented prominently
- [ ] **CM-05**: CM forward commitment projected to 2040

### Balancing Services Module

- [ ] **BAL-01**: NESO monthly balancing costs scraper populates `data/raw/neso/balancing-costs.csv`
- [ ] **BAL-02**: `schemes/balancing/` module conforming to §6.1 contract (delta-only rollups)
- [ ] **BAL-03**: Pre/post-renewables delta chart published (baseline before wind build-out vs today)

### Grid Socialisation Module

- [ ] **GRID-01**: `schemes/grid/` module producing best-efforts TNUoS attribution with low/central/high sensitivity bounds
- [ ] **GRID-02**: Grid costs presented as range with prominent confidence caveat, not as point estimate
- [ ] **GRID-03**: Combined total across all nine modules approaches REF's £25.8bn within ±15%

### SEG + REGOs Completion

- [ ] **SEG-01**: SEG aggregate-only scheme page (no station-level data available)
- [ ] **SEG-02**: REGOs aggregate page for completeness
- [ ] **SEG-03**: All eight scheme grid tiles populated on portal homepage

### Cross-Scheme / Portal Integration

- [ ] **X-01**: Total UK subsidy stacked by scheme, annual, all-time (portal P1 flagship)
- [ ] **X-02**: Combined premium over gas, cumulative (portal P1 flagship)
- [ ] **X-03**: Cost per household decomposed by scheme (portal P1 flagship)
- [ ] **X-04**: Cost per MWh of subsidised generation by scheme (P2)
- [ ] **X-05**: 2022 crisis comparison across schemes (P2)
- [ ] **PORTAL-01**: Portal homepage (`docs/index.md`) renders three headline cards (total / premium / per-household) + X1 chart with Latest-year / Last-5-years / All-time tabs + 2×4 scheme grid + theme navigation (iamkate.com/grid pattern adapted)
- [ ] **PORTAL-02**: Scheme grid tiles show latest headline figure per scheme and link to scheme detail page

### Governance & Adversarial-Proofing

- [ ] **GOV-01**: Every PRODUCTION chart carries four artefacts — narrative page, methodology page, test (in test_benchmarks or scheme-specific), source-file link — all cross-referenced
- [ ] **GOV-02**: `manifest.json` exposes full provenance per dataset (source URL, retrieval timestamp, source SHA-256, pipeline git SHA, methodology version)
- [ ] **GOV-03**: Daily refresh CI workflow (06:00 UTC cron) with per-scheme dirty-check rebuilds only what changed upstream
- [ ] **GOV-04**: Methodology versioning — `counterfactual.py` formula carries version number; changes bump `methodology_version` in manifest; `CHANGES.md` logs rationale
- [ ] **GOV-05**: Public `docs/about/corrections.md` lists every correction with date, reason, affected charts; GitHub Issues `correction` label triages
- [ ] **GOV-06**: `CITATION.cff` + versioned snapshot URLs enable academic citation; per-release tag publishes immutable `site/data/v<date>/`

## v2 Requirements

Deferred to a future release. Acknowledged but not in the P0-P11 roadmap.

### Client-side Analytics

- **V2-WASM-01**: DuckDB-WASM client-side queries for custom journalist filters — deferred until concrete use case emerges

### Content / Communications

- **V2-COMM-01**: Zenodo DOI registration for dataset citability — triggered after P5 (CfD + RO + portal) lands
- **V2-COMM-02**: Substack essay output cadence — published as material warrants, not tied to P-phases

### Adjacent Domains

- **V2-ADJ-01**: Heat subsidy tracker (RHI, biomethane) — separate sibling project, not this repo
- **V2-ADJ-02**: Transport subsidy tracker (EV plug-in grant etc.) — separate sibling project
- **V2-ADJ-03**: Non-UK equivalent (Ireland, Germany, etc.) — separate sibling project

## Out of Scope

Explicitly excluded from both v1 and v2. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Policy advocacy in the portal | Portal presents data; argumentation lives in essays and social media. |
| Forecasting subsidy costs beyond signed contracts | Project forward-committed obligations only; no AR7+ auction modelling, no gas-price scenarios. |
| Real-time dashboard | Subsidy data is slow-moving; daily refresh is the correct cadence. |
| User accounts, authentication, paid tiers | National resource = anonymous, open, free. |
| REST API | `manifest.json` + stable file URLs is a better API for analytical workloads. |
| SQL query endpoint | Parquet + DuckDB (local or WASM) covers this without server. |
| Relational database (Postgres, MySQL) | OLAP workload; wrong shape; adds ops burden. |
| MongoDB or document stores | Data is tabular and schema-stable. |
| Redis / caching layer | Cloudflare CDN handles this. |
| Docker / Kubernetes | Single-process CLI; containerisation is overhead. |
| Airflow / Prefect / Dagster | GitHub Actions cron is right-sized. |
| Rust, Go, non-Python runtimes | Maintainability principle — retirement-sustainable project. |
| Polars migration | Pandas + DuckDB sufficient; migration cost > benefit. |
| Quarto / Observable / Astro / WASM frontend | MkDocs Material is working. |
| Tableau, Metabase, PowerBI | Vendor lock-in, subscription cost, wrong fit. |
| Live chat or comments on site | Moderation burden; off-topic risk. GitHub Issues only. |
| Heat subsidies (RHI, biomethane) | Sibling project scope. |
| Transport subsidies (EV plug-in grant) | Sibling project scope. |
| Non-UK data | UK renewables only. |
| Competing with Ofgem/DESNZ/LCCC on primary data publication | Consume upstream, don't replicate. |

## Traceability

Populated during roadmap creation. Each requirement maps to exactly one phase.

| Requirement | Phase | Status |
|-------------|-------|--------|
| _(filled by roadmapper)_ | | |

**Coverage:**
- v1 requirements: TBD
- Mapped to phases: TBD
- Unmapped: TBD

---
*Requirements defined: 2026-04-21*
*Last updated: 2026-04-21 after initialization*
