# UK Renewable Subsidy Tracker

## What This Is

An independent, open, data-driven audit of UK renewable electricity subsidy costs — every scheme, every pound, every counterfactual, every methodology exposed — published as a permanent national resource. Serves journalists, advocates, academics, policymakers, and adversarial analysts from a static MkDocs site backed by reproducible Parquet pipelines.

Currently a single-scheme prototype (`cfd-payment`) covering only Contracts for Difference. This project expands it into an eight-scheme portal (`uk-subsidy-tracker`) covering CfD, RO, FiT, SEG, Constraint Payments, Capacity Market, Balancing Services, and Grid Socialisation.

## Core Value

**Every headline number on the site is reproducible from a single `git clone` + `uv sync` + one command, backed by a methodology page, traceable to a primary regulator source, and survives hostile reading.** Methodological bulletproofness is the constraint from which every other decision flows.

## Requirements

### Validated

<!-- Inferred from existing codebase; locked as shipped CfD module. -->

- ✓ **CFD-01**: CfD cost dynamics chart (4-panel volume × price gap × premium × cumulative) — existing
- ✓ **CFD-02**: CfD vs gas counterfactual chart — existing
- ✓ **CFD-03**: CfD remaining obligations forward projection — existing
- ✓ **CFD-04**: CfD payments by technology category — existing (needs docs page)
- ✓ **CFD-05**: CfD Lorenz / concentration chart — existing (needs docs page)
- ✓ **CFD-06**: CfD bang-for-buck scatter — existing (documented)
- ✓ **CFD-07**: Subsidy per avoided CO₂ tonne — existing (needs docs page)
- ✓ **CFD-08**: Cannibalisation capture-ratio chart — existing (needs docs page)
- ✓ **CFD-09**: Price vs wind correlation — existing (documented)
- ✓ **CFD-10**: Capacity factor monthly + seasonal — existing (seasonal needs docs page)
- ✓ **CFD-11**: Generation heatmap — existing (needs docs page)
- ✓ **CFD-12**: Load-duration curve — existing (documented)
- ✓ **CFD-13**: Rolling-minimum drought chart — existing (needs docs page)
- ✓ **CFD-14**: MkDocs documentation site with readthedocs theme — existing (target: material)
- ✓ **CFD-15**: Raw data loading from LCCC, ONS, Elexon CSVs — existing (no provenance metadata)

### Active

<!-- v1 target scope derived from ARCHITECTURE.md §11 phased plan (P0-P11). -->

**Foundation (P0-P3):**
- [ ] **FND-01**: Repo renamed `cfd-payment` → `uk-subsidy-tracker`
- [ ] **FND-02**: MkDocs theme switched from `readthedocs` to `material`
- [ ] **FND-03**: `ARCHITECTURE.md`, `RO-MODULE-SPEC.md`, `CHANGES.md`, `CITATION.cff` committed at repo root
- [ ] **TEST-01**: `tests/test_counterfactual.py` pins the gas counterfactual formula (fuel + carbon + O&M)
- [ ] **TEST-02**: `tests/test_schemas.py` validates every Parquet file against Pydantic schemas
- [ ] **TEST-03**: `tests/test_aggregates.py` proves no row leakage across grains
- [ ] **TEST-04**: `tests/test_benchmarks.py` reconciles totals against REF, Turver, Ofgem, Ben Pile
- [ ] **TEST-05**: `tests/test_determinism.py` proves rebuilds are byte-identical
- [ ] **TEST-06**: GitHub Actions CI runs pytest on every push
- [ ] **TRIAGE-01**: `bang_for_buck_old.py` and `scissors.py` deleted (CUT verdict from §5.2)
- [ ] **TRIAGE-02**: Docs pages written for all seven PROMOTE charts
- [ ] **TRIAGE-03**: `docs/` restructured into five theme pages (cost, recipients, efficiency, cannibalisation, reliability)
- [ ] **PUB-01**: `src/uk_subsidy_tracker/publish/manifest.py` builds `site/data/manifest.json`
- [ ] **PUB-02**: `publish/csv_mirror.py` writes CSV alongside every Parquet
- [ ] **PUB-03**: `publish/snapshot.py` writes versioned snapshot on tag
- [ ] **PUB-04**: `docs/data/index.md` — how-to-use-our-data page
- [ ] **PUB-05**: Three-layer data pipeline (`data/raw/` → `data/derived/` → `site/data/`) operational for CfD

**Scheme expansion (P4-P11):**
- [ ] **RO-01**: RO scheme module conforms to §6.1 contract (5 standard functions)
- [ ] **RO-02**: RO scraper for Ofgem register, generation, ROC prices
- [ ] **RO-03**: RO S2 dynamics, S3 by-tech, S4 concentration, S5 forward charts
- [ ] **RO-04**: RO scheme docs page + benchmark within 3% of Turver 2011-2022 aggregate
- [ ] **FIT-01**: FiT scheme module (Ofgem scraper, S2/S3/S5 charts, docs page)
- [ ] **CON-01**: Constraint payments module (NESO BM scraper, all five slots, "£X bn paid to switch off" headline)
- [ ] **CM-01**: Capacity Market module (EMR scraper, modified S2 without gas counterfactual, S3/S4/S5, attribution caveat)
- [ ] **BAL-01**: Balancing services delta (pre/post-renewables comparison)
- [ ] **GRID-01**: Grid socialisation with low/central/high sensitivity bounds
- [ ] **SEG-01**: SEG + REGOs aggregate-only pages
- [ ] **X1**: Cross-scheme stacked total by scheme, annual (portal flagship)
- [ ] **X2**: Combined premium over gas, cumulative (portal flagship)
- [ ] **X3**: Cost per household decomposed by scheme (portal flagship)
- [ ] **X4**: Cost per MWh of subsidised generation by scheme
- [ ] **X5**: 2022 crisis comparison across schemes
- [ ] **PORTAL-01**: Portal homepage — three headline cards + X1 chart with time-horizon tabs + 2×4 scheme grid + theme nav (iamkate.com/grid pattern)

**Governance (cross-cutting):**
- [ ] **GOV-01**: Every PRODUCTION chart has narrative page, methodology page, test, and linked source file
- [ ] **GOV-02**: `manifest.json` exposes provenance (retrieval timestamp, source SHA-256, pipeline git SHA) per dataset
- [ ] **GOV-03**: Daily refresh CI workflow (06:00 UTC cron, dirty-check per scheme)
- [ ] **GOV-04**: Methodology versioning — counterfactual formula is append-only; changes bump `methodology_version`
- [ ] **GOV-05**: Public `corrections.md` page + GitHub Issues `correction` label triage
- [ ] **GOV-06**: CITATION.cff + versioned snapshot URLs for academic citability

### Out of Scope

<!-- From ARCHITECTURE.md §1.3 and §10 — explicit non-goals. -->

- **Policy advocacy in the portal** — Data speaks; argumentation lives in essays/social, not the site itself.
- **Forecasting beyond signed contracts** — No AR7+ auction modelling, no gas-price scenarios, no NESO demand futures.
- **Real-time dashboard** — Subsidy data is slow-moving; daily refresh maximum.
- **User accounts, authentication, paid tiers** — National resource = anonymous, open, free.
- **REST API** — Parquet + CSV files at stable URLs via `manifest.json` is a better API for analytical workloads.
- **Heat subsidies (RHI, biomethane)** — Sibling project future scope.
- **Transport subsidies (EV plug-in grant etc.)** — Different analytical frame; different project.
- **Non-UK data** — Scope is UK renewables only.
- **Rust / Go / any non-Python** — Maintainability principle (retirement-sustainable project).
- **Polars migration** — Pandas + DuckDB sufficient.
- **Relational database (Postgres, MySQL)** — OLAP workload, wrong shape; Parquet is canonical.
- **Docker / Kubernetes** — Single-process CLI; containers are overhead.
- **Airflow / Prefect / Dagster** — GitHub Actions cron is right-sized.
- **Quarto / Observable / Astro / WASM frontend** — MkDocs Material is working; migration cost > benefit.
- **Second frontend framework / Tableau / Metabase** — Vendor lock-in, subscription cost, wrong fit.
- **Live chat, comments on site** — GitHub Issues channel only.
- **Replicating Ofgem / DESNZ / LCCC's publication role** — This project consumes their data, not replaces them.

## Context

**Existing codebase state (from `.planning/codebase/`):**
- Early-stage prototype focused exclusively on CfD scheme
- CSV-only data loading via pandas; no derived Parquet layer yet
- Scattered plotting logic under `src/cfd_payment/plotting/` (subsidy/, cannibalisation/, capacity_factor/, intermittency/)
- MkDocs site on `readthedocs` theme with ad-hoc docs structure
- Minimal test coverage (~2 files); none of §9.6's required test classes exist
- No CI/CD workflows; no scheme-module abstraction; no publishing layer
- `scissors.py` and `bang_for_buck_old.py` still present despite CUT/DELETE verdicts
- `docs/technical-details/*` pages recently deleted; site restructure in flight

**Domain context:**
- UK renewable subsidies are concentrated in eight schemes with ~£25.8bn/year total (REF aggregate)
- Primary data comes from LCCC, Ofgem, Elexon, NESO, ONS, UK ETS Authority, and EMR Delivery Body — all UK-regulator-published open data
- Prior work exists (Ben Pile 2021/2026, Turver, REF aggregates) — used as benchmark anchors
- Audience includes RenewableUK / Carbon Brief as adversarial readers; methodology survival under hostile inspection is first-class

**Maintainer context:**
- Solo maintainer (Richard Lyon)
- Retirement-adjacent project horizon; maintainability discipline over novelty
- Static-file hosting on Cloudflare Pages (free tier) — no servers to manage

## Constraints

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

## Key Decisions

<!-- From ARCHITECTURE.md §14 decision log. Append-only. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Parquet + DuckDB, no relational DB | OLAP workload; 1:1,000,000 read:write; zero-ops | — Pending (P3) |
| MkDocs Material over Quarto/Observable/Astro | Avoid migration cost; Material is 10-year stable | — Pending (P0) |
| Python-only; Rust abandoned | Maintainability principle; retirement-adjacent | ✓ Good |
| Static files on Cloudflare Pages, no backend | Publishing operation, not web app; free tier survives viral load | — Pending |
| Five-theme IA (Cost / Recipients / Efficiency / Cannibalisation / Reliability) | Charts cluster naturally into five argumentative families | — Pending (P2) |
| iamkate.com/grid layout adapted | Proven design; 3 headlines + flagship + scheme grid | — Pending (P5) |
| Per-scheme 5-slot diagnostic set (S1-S5) | Consistency across 8 schemes; CfD establishes the pattern | ✓ Good (CfD) |
| `scissors.py` CUT | Strictly dominated by `cfd_dynamics` | — Pending (P2) |
| Seven PROMOTE charts to PRODUCTION | Documented triage outcome (§5.2) | — Pending (P2) |
| Repo rename to `uk-subsidy-tracker` | `cfd-payment` no longer accurate scope | — Pending (P0) |
| Daily refresh cadence | LCCC/Elexon/ETS/NESO daily; others monthly under dirty-check | — Pending (P3+) |
| Adversarial-proofing as first-class concern | Hostile audience; methodology + tests + reproducible code essential | — Pending (cross-cutting) |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-21 after initialization*
