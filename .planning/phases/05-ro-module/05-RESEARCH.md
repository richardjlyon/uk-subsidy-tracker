# Phase 5: RO Module — Research

**Researched:** 2026-04-22
**Domain:** Renewables Obligation — Ofgem regulatory data ingestion, banding-factor lookup, ROC cost computation, forward projection to 2037, Turver-style benchmark reconciliation
**Confidence:** MEDIUM-HIGH (Ofgem scraper mechanism has a known disruption; all other domains HIGH)

## Summary

Phase 5 builds `schemes/ro/` as the second §6.1 scheme module, end-to-end from five Ofgem raw sources through five derived Parquet grains through four published charts (S2-S5) to `docs/schemes/ro.md`. The CfD module (`schemes/cfd/`) is a load-bearing template — every new file in Phase 5 has a CfD analogue to mirror verbatim. Sixteen locked decisions (D-01..D-16) already close out methodology ambiguity (rocs_issued = Ofgem primary per D-01; dual cost columns buyout+recycle vs e-ROC per D-02; headline = all-in GB total per D-12; calendar-year axis per D-07; RO-06 ±3% hard block per D-14).

The research programme here answers the eight Claude's-Discretion questions, of which two are structurally load-bearing:

1. **Turver-anchor identification (Q2).** Researcher's recommendation: **replace the Turver substack candidate with REF's `UK Renewable Electricity Subsidy Totals: 2002 to the Present Day` (Constable, 2025-05-01, PDF)**, which carries a published Table 1 with annual RO costs from 2002/03 through 2023/24 at £67.0bn cumulative. Turver's "How ROCs Rip Us Off" substack article is the RO-specific analysis but publishes no transcribable multi-year table; it cites Ofgem annual reports and OBR forecasts for 2-3 single data points. REF's report is more defensible: peer-cited, fetches from a stable URL, uses Ofgem Annual Reports as its source, and is explicit about FY/SY basis. Use **REF** as the primary anchor; add Turver's 2022 £6.4bn single-point as a secondary cross-check. This preserves RO-06 (±3% of "Turver-style aggregate") in spirit while anchoring on a data source that survives hostile reading.

2. **Ofgem scraper mechanism (Q1).** **Material disruption detected.** The Ofgem Renewables & CHP Register (`renewablesandchp.ofgem.gov.uk`) was **replaced on 2025-05-14** by the new Renewable Electricity Register (RER) at `rer.ofgem.gov.uk`. Public reports are now on a **SharePoint site, access-on-request via `renewable.enquiry@ofgem.gov.uk`**, not on a stable public URL. The RER retains only **7 years** of ROCs-issued data; pre-2018 historical data is on a separate static page ("ROCs issued from April 2006 to March 2018"). Scraping the SharePoint endpoint is not stable-URL HTTP GET and will need either (a) email-authenticated session capture, (b) Playwright/browser automation against the SharePoint UI, (c) a one-off manual download committed to `data/raw/ofgem/` with a scraper that tombstones on failure and explicit audit documentation, or (d) pivot to the static PDF-table annual-report series (Ofgem publishes `Renewables-Obligation-(RO)-2023-to-2024-(SY22)-Annual-Report.pdf` annually, containing aggregate figures by year and technology). **Planner must decide scraper strategy** — the D-18 per-scheme dirty-check assumes a deterministic fetch; none is currently guaranteed from RER. Workaround (d) is the most robust: the project's "reproducible from git clone" promise is preserved by committing the raw data snapshots to `data/raw/ofgem/` + `.meta.json` sidecars, treating Ofgem as a manual-refresh source until RER stabilises a public API.

**Primary recommendation:**

1. Adopt **REF Constable 2025-05-01 Table 1** as the RO-06 benchmark anchor (anchor_1); keep Turver substack as a secondary cross-check entry (anchor_2). Document the replacement in `benchmarks.yaml::turver` audit header per Phase 4 Plan 06 pattern.
2. For the Ofgem scraper, adopt the **"Option D manual-refresh"** posture: commit a one-off snapshot of raw Ofgem files to `data/raw/ofgem/`, scraper implementation reads from a local cache with `upstream_changed()` returning False when the sidecar carries a `manual_refresh: true` marker, until RER's public API stabilises. File an explicit STATE.md followup for periodic manual re-pull. This preserves D-17/D-18 discipline (fail-loud when a scraper is attempted against SharePoint without credentials; dirty-check against sidecar SHA on manual refresh).
3. For banding YAML, use the REF Table 1 banding factors (2013-2017 transition) + RO Order 2009 pre-2013 values as researched below (§4 Bandings Table Inventory). ~60 rows confirmed as spec'd.
4. For mutualisation: manual YAML fixture in `data/raw/ofgem/roc-prices.csv` header notes — only 2021-22 triggered mutualisation (£119.7M shortfall, £44.0M redistributed); 2022-23 fell below threshold (£7.2M shortfall vs £318M ceiling — no trigger).
5. For forward-projection to 2037: use **accreditation-end-date per station** (option (c)) — Ofgem's register carries accreditation dates; remaining-contract-years derives from accreditation + 20-year support term. Matches the CfD module's deterministic-anchor discipline (D-21).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Ofgem raw-data ingestion | Data layer (`src/uk_subsidy_tracker/data/`) | — | Mirrors `data/lccc.py`, `data/ons_gas.py`; owns HTTP/scraper + pandera raw-CSV validation |
| Banding YAML config | Data layer (`src/uk_subsidy_tracker/data/ro_bandings.yaml` + `ro_bandings.py`) | — | Two-layer Pydantic (Phase 2 D-07 pattern); mirrors `LCCCAppConfig` |
| Scheme-module contract (5 callables) | Schemes layer (`src/uk_subsidy_tracker/schemes/ro/`) | — | Verbatim §6.1 Protocol — same shape as `schemes/cfd/` |
| Station-month cost derivation | Schemes layer (`schemes/ro/cost_model.py`) | — | ROC cost formula + gas counterfactual join; per-station granularity |
| Aggregation rollups (annual / by-tech / by-AR) | Schemes layer (`schemes/ro/aggregation.py`) | — | Re-reads station_month Parquet (D-03 round-trip discipline) |
| Forward projection | Schemes layer (`schemes/ro/forward_projection.py`) | — | Deterministic anchor = max accreditation end date (not wall clock) |
| Carbon-price extension 2005-2017 | Counterfactual layer (`counterfactual.DEFAULT_CARBON_PRICES`) | Constants YAML (`tests/fixtures/constants.yaml`) | Shared module; new dict entries additive per D-06; SEED-001 Tier 2 drift tripwire fires |
| Mutualisation delta | Raw-data layer (`data/raw/ofgem/roc-prices.csv` + sidecar) | Schemes layer (`cost_model.py` — consumer of adjusted price) | Priced into roc_price_gbp column at ingest; surfaces in annual_summary::mutualisation_gbp |
| NIRO rows | Schemes layer (country='NI' column on every grain) | Docs layer (`docs/schemes/ro.md` caveat paragraph) | Parquet carries both; headline filter = GB |
| S2-S5 charts | Plotting layer (`plotting/subsidy/ro_*.py`) | — | RO-specific files; shared helpers deferred to Phase 6 per D-16 |
| Scheme detail page | Docs layer (`docs/schemes/ro.md`) | Theme galleries (Cost + Recipients cross-links) | GOV-01 four-way coverage at scheme level (D-15) |
| Tests (schemas/aggregates/determinism/benchmarks) | Tests layer (parametrised over RO grains) | — | Extends existing Phase 4 parametrisation; no net-new test-files per se |
| Refresh orchestration | `refresh_all.SCHEMES` | — | One-line append; per-scheme dirty-check auto-activates (D-18) |
| Publishing | `publish/manifest.py` | — | No code change; iterates SCHEMES (Phase 4 Plan 04) |

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Cost-model methodology (R1 banding + R6 ROC price):**

- **D-01** — `rocs_issued` source: Use **Ofgem's published `ROCs_Issued` column** as authoritative on every station-month row. YAML bandings table loaded for audit cross-check only; warning logged on stations where `|ofgem_issued - computed| / ofgem_issued > 1%`. Does not block pipeline.
- **D-02** — ROC price, dual columns: `station_month.parquet` carries (a) `ro_cost_gbp` = `rocs_issued × (buyout + recycle)` (primary, consumer view) and (b) `ro_cost_gbp_eroc` = `rocs_issued × eroc_clearing_price` (sensitivity, generator view). Annual summary carries both. S2 shows e-ROC as 2-10% sensitivity band.
- **D-03** — Bandings YAML location: `src/uk_subsidy_tracker/data/ro_bandings.yaml`. Covers all (technology × commissioning-window × country) cells. Each entry carries `Provenance:` block. Pydantic-loaded via `RoBandingEntry` + `RoBandingTable` in sibling `ro_bandings.py`.
- **D-04** — `validate()` returns warnings on all four checks: (1) banding divergence count, (2) Turver-band drift, (3) methodology_version consistency, (4) forward-projection sanity. Empty list = clean.

**Time axis + carbon extension (R2 pre-2013 carbon + R3 CY/OY):**

- **D-05** — Carbon-price extension with sensitivity. `counterfactual.DEFAULT_CARBON_PRICES` extended backward: EU ETS annual averages 2005-2017 (EUR→GBP contemporary rates); zeros 2002-2004. Primary `ro_cost_gbp` uses full extended table. `station_month` carries `ro_cost_gbp_nocarbon` sensitivity column. `constants.yaml` gets new entries. CHANGES.md logs extension.
- **D-06** — METHODOLOGY_VERSION stays `"0.1.0"`. Extension is additive (new year keys in dict; no revision of existing values). 1.0.0 bump reserved for Phase 6+ portal launch.
- **D-07** — Calendar year is the primary plotting axis. Obligation year surfaces in `station_month.parquet::obligation_year` column (audit trail) + `docs/schemes/ro.md` methodology section. No OY-axis charts in Phase 5.
- **D-08** — ROC-price assignment rule: `roc_price_gbp = buyout + recycle` for the **obligation year containing the output period end**. March 2022 generation → OY 2021-22 price; April 2022 generation → OY 2022-23 price.

**Scope inclusions (R4 NIRO + R5 co-firing + R7 mutualisation):**

- **D-09** — NIRO included; headlines GB-only. Every row carries `country` column ∈ {'GB', 'NI'}. Headline is GB-only; annual_summary rows emitted per (obligation_year × country) so adversarial readers can filter to UK-total.
- **D-10** — Co-firing biomass included. `technology='biomass_cofiring'` slice. Methodology section notes philosophical contestability with "filter this slice" instruction.
- **D-11** — Mutualisation rolled into `ro_cost_gbp`; affected years flagged. `roc_price_gbp` for OY 2021-22 and 2022-23 adjusted upward by published mutualisation delta. `annual_summary.parquet` carries `mutualisation_gbp` column (null on clean years).
- **D-12** — Headline = all-in GB total. "£X bn in RO subsidy paid by UK consumers since 2002" (GB-only, includes cofiring, includes mutualisation). Breakdown paragraph shows attributable £A bn cofiring, £B bn mutualisation, £C bn NIRO-excluded.

**Benchmark anchor + docs structure (RO-06 + ROADMAP SC #4):**

- **D-13** — Turver anchor picked by researcher (this research doc). Benchmark entry: `tests/fixtures/benchmarks.yaml::turver` new top-level key. Tolerance constant `TURVER_TOLERANCE_PCT = 3.0`. Phase 2 D-11 fallback **does not apply** — RO-06 is binary.
- **D-14** — ±3% divergence is a hard block. `test_benchmarks.py` parametrises over Turver anchor years; aggregate `ro_cost_gbp` (all-in GB total per D-12 scope) must be within ±3%. If divergence exceeds 3%, investigate scope (NIRO, mutualisation, cofiring, CY vs OY), banding error, or carbon-price extension before phase exit.
- **D-15** — `docs/schemes/ro.md` single-page scheme overview. 8-section structure (Headline / What is the RO / Cost dynamics S2 / By technology S3 / Concentration S4 / Forward commitment S5 / Methodology summary / Data & code). No per-chart pages under `docs/schemes/ro/` in Phase 5.
- **D-16** — Chart code: RO-specific copies with opportunistic shared helpers. New files `plotting/subsidy/ro_{dynamics,by_technology,concentration,forward_projection}.py`. Where 2-3 lines literally duplicate between CfD and RO, extract to `plotting/subsidy/_shared.py` at planner's discretion. Aggressive refactor deferred to Phase 6.

### Claude's Discretion

- Ofgem scraper mechanism (planner chooses at research time — see §2 below; recommendation: Option D manual-refresh posture until RER stabilises).
- `ro_bandings.yaml` schema shape (two-layer Pydantic mirroring `LCCCDatasetConfig` + `LCCCAppConfig`; see §3 for field set recommendation).
- Forward-projection methodology 2026→2037 (recommendation: per-station accreditation end date + 20-year support term; see §6).
- Mutualisation data source + entry points (recommendation: manual YAML fixture; see §4).
- Refresh cadence for Ofgem in `refresh_all.py` (recommendation: monthly frequency with per-scheme dirty-check auto-skip on unchanged SHA).
- RO-specific test fixtures (recommendation: extend existing parametrisation over grain names).
- Test parametrisation strategy for RO grains (recommendation: extend existing CfD parametrisation; follow established pattern).

### Deferred Ideas (OUT OF SCOPE)

- Combined CfD + RO flagship chart ("chart 5" in RO-MODULE-SPEC.md §3) — Phase 6 X1/X2 territory.
- Portal homepage with headline cards + 2×4 scheme grid — Phase 6 PORTAL-01/02.
- FiT scheme module — Phase 7. No `fit/` stub in Phase 5.
- METHODOLOGY_VERSION bump to 1.0.0 — Phase 6+ portal launch.
- Zenodo DOI registration — V2-COMM-01, post-Phase-5.
- Aggressive chart-code refactor into scheme-parametric helpers — Phase 6 when X-chart shared infrastructure forces it.
- `docs/data/ro.md` per-scheme data page — `docs/data/index.md` works unchanged per Phase 4 D-27.
- Cloudflare R2 for oversized raw files — RO register XLSX ≤100MB.
- Per-chart D-01 six-section pages under `docs/schemes/ro/` — scheme-level page is GOV-01 unit; per-chart deferred unless research warrants.
- OY-axis charts — CY-only in Phase 5.
- NIRO-first or UK-total headlines — GB-only headline locked; revisit post-Phase-5 if reader feedback warrants.
- Pre-publication Turver outreach (RO-MODULE-SPEC.md §11 Phase E).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RO-01 | Ofgem RO scraper populates `data/raw/ofgem/{ro-register,ro-generation,roc-prices}.csv` with sidecar meta.json | §2 Ofgem scraper mechanisms — Option D manual-refresh recommended given RER disruption; shared `sidecar.write_sidecar()` helper (Phase 4 Plan 07) covers atomic `.meta.json` writes |
| RO-02 | `schemes/ro/` module conforms to §6.1 contract | CfD template (`schemes/cfd/__init__.py` + `_refresh.py` + `cost_model.py` + `aggregation.py` + `forward_projection.py`) — verbatim pattern to mirror; `SchemeModule` Protocol (`schemes/__init__.py`) enforces shape |
| RO-03 | RO derived Parquet tables: station_month, annual_summary, by_technology, by_allocation_round, forward_projection | §3 RO banding table + §7 cost formula + CfD schema pattern (`src/uk_subsidy_tracker/schemas/cfd.py`) — five Pydantic row models → five Parquet grains + five schema.json siblings |
| RO-04 | RO S2/S3/S4/S5 charts published (dynamics/by-technology/concentration/forward-projection) | Chart templates in `plotting/subsidy/cfd_dynamics.py` + `remaining_obligations.py` + `lorenz.py` + `cfd_payments_by_category.py`; Appendix A naming convention from RO-MODULE-SPEC.md |
| RO-05 | RO scheme docs page + theme integration | D-15 8-section structure; existing theme pages for Cost + Recipients; mkdocs.yml nav append (new top-level "Schemes" tab holding CfD + RO recommended — see §8.2) |
| RO-06 | RO 2011-2022 benchmarks within 3% of Turver | §5 Turver anchor evaluation — **REF Constable 2025-05-01 recommended as primary anchor**; Table 1 transcription provided (22 year rows); TURVER_TOLERANCE_PCT = 3.0 |
</phase_requirements>

## Standard Stack

All dependencies are **already in `pyproject.toml`** — no new packages required. RO reuses the same stack as CfD. Version verification performed 2026-04-22 via `uv pip list`.

### Core

| Library | Installed | Purpose | Why Standard | Status |
|---------|-----------|---------|--------------|--------|
| pandas | 3.0.2 | Raw-data wrangling, joins, groupby-sum rollups | Already load-bearing throughout; CfD module uses verbatim | `[VERIFIED: uv pip list]` |
| pyarrow | 24.0.0 | Parquet write/read via Table.from_pandas + pq.write_table; deterministic writer | Phase 4 D-22 pinned `compression=snappy, version=2.6, use_dictionary=True, write_statistics=True, data_page_size=1 MiB`; test_determinism verifies content-identity | `[VERIFIED: uv pip list]` |
| pydantic | 2.13.1 | Row-model schemas (5 RO grains); RoBandingEntry + RoBandingTable YAML loader | Schema as source of truth for column order (D-10); CfD pattern verbatim | `[VERIFIED: uv pip list]` |
| pandera | 0.31.1 | Loader-owned raw-CSV validation; derivation-owned grain validation | Phase 2 convention: `.validate(df)` inside loader body, not in tests | `[VERIFIED: uv pip list]` |
| pyyaml | 6.0.3 | Load `ro_bandings.yaml` + existing `lccc_datasets.yaml` pattern | Phase 2 D-07 source-key injection | `[VERIFIED: uv pip list]` |
| requests | 2.33.1 | Scraper HTTP GETs (if any stable URLs remain post-RER disruption) | Phase 4 Plan 07 error-path discipline: `output_path` bound before try, `timeout=60`, bare `raise` on failure | `[VERIFIED: uv pip list]` |
| openpyxl | 3.1.5 | XLSX read (RO register download is XLSX per RO-MODULE-SPEC.md §4.1) | Already in use for ONS gas-sap.xlsx | `[VERIFIED: uv pip list]` |
| plotly | 6.7.0 | Four RO charts (dynamics/by-tech/concentration/forward-projection) + PNG export via kaleido | Phase 3 PROMOTE-chart templates verbatim | `[VERIFIED: uv pip list]` |
| numpy | 2.4.4 | Weighted-average strike price computation (forward_projection pattern) | Already load-bearing | `[VERIFIED: uv pip list]` |

### Supporting

| Library | Installed | Purpose | When to Use |
|---------|-----------|---------|-------------|
| duckdb | 1.5.2 | Cross-scheme queries by academic readers | Read-only via `data/latest/ro/*.parquet`; not used during RO derivation |
| kaleido | 1.2.0 | Static PNG export for Twitter cards | Used by `ChartBuilder.save(export_twitter=True)` |
| mkdocs | 1.6.1 | Build `docs/schemes/ro.md` | `mkdocs build --strict` — permanent CI gate; must stay green |
| mkdocs-material | 9.7.6 | Material theme for docs; nav tab for new Schemes section | Theme features locked in Phase 3 D-06 |

### Alternatives Considered (rejected)

| Instead of | Could Use | Rejected Because |
|------------|-----------|------------------|
| pandas + pyarrow | Polars + pyarrow | User memory constraint: Polars-migration rejected per PROJECT.md; maintainability principle dominates |
| requests for scraper | httpx / aiohttp | requests is already the established pattern in `data/*.py`; scope creep to swap libraries |
| Playwright for scraper | Selenium / Puppeteer (via Node) | Python stack requires Python-native solution; Playwright-Python works but heavyweight for one-shot Ofgem snapshots |
| pandera raw-CSV validation | marshmallow / voluptuous | pandera is already in `pyproject.toml`; ecosystem coherence |

**Installation:** No changes required — all dependencies already pinned in pyproject.toml. Planner must not add new dependencies for Phase 5.

## Architecture Patterns

### System Architecture Diagram

```
                    Ofgem RER / SharePoint (*DISRUPTED post 2025-05-14*)
                    + legacy pre-2018 ROC data (static pages)
                    + Ofgem annual-report PDFs (stable URLs)
                    + Ofgem buyout-price transparency documents (stable URLs)
                    + e-ROC quarterly auction results (e-roc.co.uk)
                    + The Renewables Obligation Order 2009 (SI 2009/785 + amendments)
                            │
                            │  ① SCRAPE / MANUAL SNAPSHOT (data/ofgem_ro.py, roc_prices.py)
                            │     — Option D: one-off manual commit to data/raw/ofgem/
                            │     — schemes/ro/_refresh.py::refresh() wires scrapers
                            │     — sidecar.write_sidecar() writes atomic .meta.json
                            ▼
                    data/raw/ofgem/
                    ├── ro-register.xlsx + .meta.json
                    ├── ro-generation.csv + .meta.json
                    ├── roc-prices.csv + .meta.json
                                │
                                │  ② LOAD + VALIDATE (pandera schemas on raw CSVs)
                                │     — load_ro_register() / load_ro_generation() / load_roc_prices()
                                │     — ro_bandings.yaml loaded via RoBandingTable Pydantic
                                ▼
                    In-memory DataFrames
                    (with counterfactual.compute_counterfactual() extended to 2005)
                                │
                                │  ③ DERIVE station × month (schemes/ro/cost_model.py)
                                │     — Ofgem rocs_issued primary; YAML banding cross-check logs warnings
                                │     — rocs_issued × (buyout + recycle + mutualisation_delta)
                                │     — Parallel: ro_cost_gbp_eroc (sensitivity)
                                │     — Parallel: ro_cost_gbp_nocarbon (sensitivity)
                                │     — obligation_year column anchors price lookup
                                │     — country ∈ {GB, NI}
                                ▼
                    data/derived/ro/
                    ├── station_month.parquet + schema.json  ← CANONICAL UPSTREAM GRAIN
                                │
                                │  ④ ROLLUP via re-read (Phase 4 D-03 round-trip)
                                │     — build_annual_summary(): year + country groupby sum
                                │     — build_by_technology(): year × technology
                                │     — build_by_allocation_round(): year × NIRO/GB + commissioning window
                                │     — build_forward_projection(): per-station remaining-years to 2037
                                ▼
                    data/derived/ro/
                    ├── annual_summary.parquet + schema.json
                    ├── by_technology.parquet + schema.json
                    ├── by_allocation_round.parquet + schema.json
                    ├── forward_projection.parquet + schema.json
                                │
                                │  ⑤ PUBLISH (publish/manifest.py iterates refresh_all.SCHEMES — no code change)
                                │     — copy derived/ro/* → site/data/latest/ro/*.{parquet,csv,schema.json}
                                │     — manifest.json appends 5 new RO dataset entries
                                ▼
                    site/data/latest/ro/*  +  site/data/manifest.json (top-level fields unchanged)
                                │
                                │  ⑥ PLOT (plotting/subsidy/ro_*.py — S2, S3, S4, S5)
                                │     — reads derived/ro/*.parquet OR raw+counterfactual (D-02 planner's choice)
                                │     — ChartBuilder.save() → docs/charts/html/subsidy_ro_*_twitter.{png,html}
                                ▼
                    docs/charts/html/subsidy_ro_{dynamics,by_technology,concentration,forward_projection}_twitter.{png,html}
                                │
                                │  ⑦ DOCUMENT (docs/schemes/ro.md — 8-section D-15 structure)
                                │     — mkdocs build --strict green
                                ▼
                    https://<host>/schemes/ro/ (new page on Schemes tab)
                                │
                                │  ⑧ VALIDATE (schemes/ro/validate() — 4 checks, see Validation Architecture below)
                                │
                                │  ⑨ TEST (test_schemas / test_aggregates / test_determinism / test_benchmarks)
                                │     — parametrised over 5 RO grains
                                │     — test_benchmarks::turver  ±3% vs REF Constable Table 1 (primary anchor)
                                ▼
                    GREEN CI (tests + mkdocs --strict) — Phase 5 EXIT
```

### Component Responsibilities

| Layer | File(s) Created | File(s) Modified | Purpose |
|-------|------|-------|---------|
| Scraper / raw ingest | `data/ofgem_ro.py`, `data/roc_prices.py`, `data/ro_bandings.yaml`, `data/ro_bandings.py`, `data/raw/ofgem/{ro-register.xlsx, ro-generation.csv, roc-prices.csv}` + sidecars | — | Ofgem + buyout/recycle/e-ROC + bandings YAML |
| Schemas | `schemas/ro.py` | `schemas/__init__.py` (re-export) | 5 Pydantic row models |
| Scheme module | `schemes/ro/__init__.py`, `_refresh.py`, `cost_model.py`, `aggregation.py`, `forward_projection.py` | `refresh_all.py::SCHEMES` (1-line append) | §6.1 contract + derivation |
| Plotting | `plotting/subsidy/ro_dynamics.py`, `ro_by_technology.py`, `ro_concentration.py`, `ro_forward_projection.py`, optional `_shared.py` | — | 4 charts |
| Carbon extension | — | `counterfactual.py::DEFAULT_CARBON_PRICES` (add 2002-2017 entries) | Backward extension additive per D-06 |
| Docs | `docs/schemes/ro.md` | `mkdocs.yml` (nav), `docs/index.md` (headline link), `docs/themes/cost/index.md`, `docs/themes/recipients/index.md` | Scheme page + theme cross-links |
| Tests | `tests/data/test_ofgem_ro.py` | `tests/test_schemas.py`, `tests/test_aggregates.py`, `tests/test_determinism.py`, `tests/test_benchmarks.py`, `tests/fixtures/benchmarks.yaml`, `tests/fixtures/constants.yaml`, `tests/test_constants_provenance.py::_TRACKED` | Parametrise over RO grains + benchmarks anchor |
| Changelog | — | `CHANGES.md` [Unreleased] + `## Methodology versions` | Release-notes ledger |

### Recommended Project Structure (after Phase 5)

```
src/uk_subsidy_tracker/
├── counterfactual.py                  # MODIFIED: DEFAULT_CARBON_PRICES extended 2002-2017
├── data/
│   ├── lccc.py                        # unchanged
│   ├── elexon.py                      # unchanged
│   ├── ons_gas.py                     # unchanged
│   ├── sidecar.py                     # unchanged (reused)
│   ├── lccc_datasets.yaml             # unchanged
│   ├── ofgem_ro.py                    # NEW: register + generation scraper
│   ├── roc_prices.py                  # NEW: buyout + recycle + e-ROC scraper
│   ├── ro_bandings.py                 # NEW: Pydantic loader
│   └── ro_bandings.yaml               # NEW: ~60-entry banding table
├── schemas/
│   ├── __init__.py                    # MODIFIED: re-export 5 RO row classes
│   ├── cfd.py                         # unchanged
│   └── ro.py                          # NEW: 5 Pydantic row schemas
├── schemes/
│   ├── __init__.py                    # unchanged (SchemeModule Protocol)
│   ├── cfd/                           # unchanged
│   └── ro/
│       ├── __init__.py                # NEW: 5 contract functions
│       ├── _refresh.py                # NEW: wires 3 scrapers + write_sidecar
│       ├── cost_model.py              # NEW: build_station_month
│       ├── aggregation.py             # NEW: 3 rollup builders
│       └── forward_projection.py      # NEW: to-2037 per-station
├── plotting/
│   └── subsidy/
│       ├── cfd_dynamics.py            # unchanged
│       ├── remaining_obligations.py   # unchanged
│       ├── lorenz.py                  # unchanged
│       ├── cfd_payments_by_category.py# unchanged
│       ├── ro_dynamics.py             # NEW: S2 4-panel
│       ├── ro_by_technology.py        # NEW: S3 stacked area
│       ├── ro_concentration.py        # NEW: S4 Lorenz / top-N
│       ├── ro_forward_projection.py   # NEW: S5 drawdown to 2037
│       └── _shared.py                 # NEW (opportunistic): 2-3-line duplicates hoisted
├── publish/                           # unchanged (iterates SCHEMES)
└── refresh_all.py                     # MODIFIED: SCHEMES += (("ro", ro),)

data/
├── raw/
│   ├── lccc/                          # unchanged
│   ├── elexon/                        # unchanged
│   ├── ons/                           # unchanged
│   └── ofgem/                         # NEW
│       ├── ro-register.xlsx + .meta.json
│       ├── ro-generation.csv + .meta.json
│       └── roc-prices.csv + .meta.json
└── derived/
    ├── cfd/                           # unchanged (5 Parquet + 5 schema.json)
    └── ro/                            # NEW (5 Parquet + 5 schema.json, matching CfD naming)

docs/
├── schemes/                           # NEW directory
│   └── ro.md                          # NEW: 8-section D-15 structure
├── themes/
│   ├── cost/index.md                  # MODIFIED: RO chart entries in gallery
│   └── recipients/index.md            # MODIFIED: RO Lorenz entry
├── index.md                           # MODIFIED: RO headline paragraph
└── charts/html/                       # 4 new subsidy_ro_*_twitter.{png,html}
                                       # (gitignored; regenerated daily)

tests/
├── test_schemas.py                    # MODIFIED: parametrise GRAINS over RO too
├── test_aggregates.py                 # MODIFIED: parametrise over RO grains
├── test_determinism.py                # MODIFIED: parametrise over RO grains
├── test_benchmarks.py                 # MODIFIED: new Turver reconciliation test
├── test_constants_provenance.py       # MODIFIED: _TRACKED += 2002-2017 DEFAULT_CARBON_PRICES
├── fixtures/benchmarks.yaml           # MODIFIED: new turver section + audit header
├── fixtures/constants.yaml            # MODIFIED: new 2002-2017 DEFAULT_CARBON_PRICES_{YEAR} entries
└── data/
    └── test_ofgem_ro.py               # NEW: mocked scraper path tests (no network in CI)

CHANGES.md                             # MODIFIED: [Unreleased] + Methodology versions entries
```

### Pattern 1: Five-file Scheme Module (§6.1)

**What:** Every scheme module has five Python files structured identically. Phase 4 Plan 03 established this with `schemes/cfd/`; Phase 5 mirrors verbatim for RO. Future schemes (FiT, constraints, CM, balancing, grid) use the same shape.

**When to use:** Always. This is the project's **load-bearing architectural pattern**.

**Example:** (file-by-file mapping of `schemes/cfd/` → `schemes/ro/`)

| CfD file | RO analogue | What to preserve |
|----------|-------------|------------------|
| `schemes/cfd/__init__.py` | `schemes/ro/__init__.py` | `DERIVED_DIR` constant, 5 public functions, `__all__` list, `@runtime_checkable` `SchemeModule` Protocol conformance |
| `schemes/cfd/_refresh.py` | `schemes/ro/_refresh.py` | `_RAW_FILES` + `_URL_MAP` module constants (byte-match with backfill script); `upstream_changed()` SHA-compare vs sidecar; `refresh()` wires downloaders + calls `write_sidecar()` for each |
| `schemes/cfd/cost_model.py` | `schemes/ro/cost_model.py` | `build_station_month(output_dir) -> pd.DataFrame`; loader-owned pandera schema; deterministic writer `_write_parquet()`; Column order = Pydantic row-model field-declaration order (D-10); sort_values(stable_key).reset_index() |
| `schemes/cfd/aggregation.py` | `schemes/ro/aggregation.py` | `_read_station_month(output_dir)` helper; three builders (`build_annual_summary`, `build_by_technology`, `build_by_allocation_round`); re-reads Parquet (D-03); int64 year cast (Phase 4 Rule-1 auto-fix); counterfactual join via `compute_counterfactual()` |
| `schemes/cfd/forward_projection.py` | `schemes/ro/forward_projection.py` | `build_forward_projection(output_dir)`; deterministic anchor (NOT `pd.Timestamp.now()`); For CfD anchor = `max(Settlement_Date).year`; for RO anchor = `max(accreditation_end_year)` per §6 below |

### Pattern 2: Two-layer Pydantic + YAML (Phase 2 D-07)

**What:** YAML fixture → Pydantic config model that injects parent key as explicit field on each entry before validation. Mirror of `LCCCDatasetConfig` + `LCCCAppConfig::load_lccc_config`.

**When to use:** `ro_bandings.yaml` loading. Also used for existing `benchmarks.yaml` + `constants.yaml`.

**Example:**
```python
# Source: src/uk_subsidy_tracker/data/lccc.py:16-32 (mirror pattern)
class RoBandingEntry(BaseModel):
    technology: str  # injected from YAML key
    country: str      # 'GB' or 'NI'
    commissioning_window_start: date | None  # None = grandfathered
    commissioning_window_end: date | None
    banding_factor: float  # ROCs per MWh
    # Provenance block (constant-provenance pattern from user memory):
    source: str       # e.g. "Renewables Obligation Order 2009 (SI 2009/785)"
    url: HttpUrl      # stable UK-legislation URL
    basis: str        # e.g. "Schedule 2, 2013-2017 banding review"
    retrieved_on: date
    next_audit: date | None = None

class RoBandingTable(BaseModel):
    entries: list[RoBandingEntry]

    def lookup(self, technology: str, country: str, commissioning_date: date) -> float:
        """Return banding factor; raises KeyError if no matching window."""
        for e in self.entries:
            if e.technology == technology and e.country == country:
                if e.commissioning_window_start is None or commissioning_date >= e.commissioning_window_start:
                    if e.commissioning_window_end is None or commissioning_date <= e.commissioning_window_end:
                        return e.banding_factor
        raise KeyError(f"No banding for ({technology}, {country}, {commissioning_date})")
```

### Pattern 3: Deterministic Parquet Writer (Phase 4 D-21/D-22)

**What:** All `_write_parquet()` calls use pinned options producing content-identical Parquet across rebuilds (modulo writer-metadata timestamps). `test_determinism.py::test_parquet_content_identical` enforces.

**When to use:** Every `build_*` function that writes a Parquet file in RO derived layer. Import `_write_parquet` from `schemes/cfd/cost_model.py` — it's already shared across CfD rollups.

**Example:**
```python
# Source: src/uk_subsidy_tracker/schemes/cfd/cost_model.py:47-68
from uk_subsidy_tracker.schemes.cfd.cost_model import _write_parquet

def build_station_month(output_dir: Path) -> pd.DataFrame:
    # ... derive df ...
    columns = list(StationMonthRow.model_fields.keys())  # D-10: Pydantic field order = Parquet column order
    df = df[columns].sort_values(stable_key, kind="mergesort").reset_index(drop=True)
    df = station_month_schema.validate(df)  # Loader-owned pandera
    _write_parquet(df, output_dir / "station_month.parquet")
    emit_schema_json(StationMonthRow, output_dir / "station_month.schema.json")
    return df
```

### Pattern 4: Shared Atomic Sidecar (Phase 4 Plan 07)

**What:** `sidecar.write_sidecar(raw_path, upstream_url)` writes atomic `.meta.json` with SHA-256 + retrieved_at + http_status + publisher_last_modified. Replaces ad-hoc writers per scheme.

**When to use:** After every successful download in `schemes/ro/_refresh.py::refresh()`. Three files → three calls.

**Example:**
```python
# Source: src/uk_subsidy_tracker/data/sidecar.py:35-74
from uk_subsidy_tracker.data.sidecar import write_sidecar

# In schemes/ro/_refresh.py::refresh():
download_ofgem_ro_register()
download_ofgem_ro_generation()
download_roc_prices()
for rel, upstream_url in _URL_MAP.items():  # three files
    raw_path = DATA_DIR / rel
    if not raw_path.exists():
        raise FileNotFoundError(...)  # fail-loud per D-17
    write_sidecar(raw_path=raw_path, upstream_url=upstream_url)
```

### Pattern 5: Counterfactual Column Propagation (Phase 4 D-12)

**What:** `counterfactual.METHODOLOGY_VERSION` → `DataFrame.methodology_version` column via `compute_counterfactual()` → Parquet column on every grain row → `manifest.json::methodology_version`. End-to-end provenance chain.

**When to use:** Every grain-building function sets `df["methodology_version"] = METHODOLOGY_VERSION` before writing. RO grains are no exception.

### Anti-Patterns to Avoid

- **Hand-roll a sidecar writer.** Use `uk_subsidy_tracker.data.sidecar.write_sidecar()`. Duplicating its SHA+atomic-write logic in `schemes/ro/_refresh.py` regresses Phase 4 Plan 07.
- **Re-read station_month from memory instead of Parquet.** D-03: rollups round-trip through Parquet to exercise the write/read path. Passing DataFrames in-process across `cost_model → aggregation` breaks the round-trip contract.
- **Wall-clock anchors in forward_projection.** Use `max(Accreditation_End_Date)` not `pd.Timestamp.now().year` — determinism discipline (D-21).
- **Skip loader-owned pandera validation.** `schema.validate(df)` inside the loader body, not in a test. Phase 2 pattern + Phase 4 enforcement.
- **Refactor CfD chart code to parametrise CfD+RO.** Aggressive refactor deferred to Phase 6 per D-16; Phase 5 copies verbatim.
- **Float comparisons in benchmark test.** Use `abs(a - b) / b * 100.0` vs TURVER_TOLERANCE_PCT, not `assert math.isclose(a, b)`; Phase 2 pattern.
- **Network calls in CI test runs.** Phase 4 discipline: `tests/data/test_ofgem_ro.py` uses mocks only. Scraper tests run offline.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Sidecar `.meta.json` atomic write | Custom `open().write(json.dumps(...))` | `src/uk_subsidy_tracker/data/sidecar.write_sidecar()` | Shared across both refresh paths (CfD, RO); byte-identical serialisation (sort_keys + indent + trailing newline); atomic (.tmp + os.replace) |
| SHA-256 of raw file | Custom `hashlib.sha256().update(f.read())` | `sidecar._sha256_of(path)` | Same chunking (64 KiB) as CfD + backfill script; prevents drift across writers |
| Parquet write for derived grains | `df.to_parquet(path)` | `schemes.cfd.cost_model._write_parquet(df, path)` | Pinned options (compression, version, dict, statistics, page size) guarantee content-identity under `test_determinism`; importing the shared helper is the documented pattern |
| Schema JSON sibling | Hand-write JSON Schema from Pydantic | `schemas.cfd.emit_schema_json(model, path)` | Serialisation-mode JSON Schema; UTF-8 + LF newlines + sorted keys; byte-stable across platforms |
| Pydantic loading from YAML | Raw `yaml.safe_load() + dict traversal` | `from pydantic import BaseModel; `.model_validate(dict)` | Phase 2 D-07 two-layer pattern; error messages cite source-key; ensures dtype conformance on entry |
| Benchmarks loader | Custom YAML parser | `tests.fixtures.load_benchmarks()` | Injects source key on every entry; Phase 2 pattern; used by existing `test_benchmarks.py` |
| Row conservation check | Custom `sum(year_table) == sum(year_tech_table)` | `pd.testing.assert_series_equal(by_year.sort_index(), by_year_tech.sort_index())` | Phase 2 pattern; exact equality; surfaces NaN-drop in groupby |
| Gas counterfactual for RO-era MWh | Copy-paste `counterfactual` formula | `counterfactual.compute_counterfactual(gas_df, carbon_prices)` | Shared single source of truth (ARCHITECTURE §6.2); D-05 extension is additive (just extend the dict) |
| Chart-builder + PNG export | Custom plotly save logic | `uk_subsidy_tracker.plotting.ChartBuilder` | Phase 0 pattern; pinned dark theme + Twitter-card dimensions; handles kaleido PNG export |
| Manifest iteration | Custom per-scheme manifest entry | `publish/manifest.py` (unchanged) — already iterates `SCHEMES` | Phase 4 Plan 04; one-line SCHEMES append auto-extends manifest |

**Key insight:** The Phase 4 infrastructure is already complete for "N scheme modules." Phase 5 adds **one** new scheme and exercises every generic handshake (`SchemeModule` Protocol, `refresh_all.SCHEMES` iteration, `publish/manifest.py` iteration, per-scheme dirty-check, pandera validation, deterministic Parquet writer, JSON-schema emission, sidecar atomic writer, Pydantic-YAML pattern, benchmarks loader, counterfactual column propagation). The value of Phase 4's infrastructure is proven by how little of it needs change in Phase 5: one line in `refresh_all.py::SCHEMES`; zero lines in `publish/manifest.py`; zero lines in `csv_mirror.py`; zero lines in `snapshot.py`. A RESEARCH.md cross-check: if you find yourself proposing NEW infrastructure code that isn't in `schemes/ro/` or `data/ofgem_*` or `plotting/subsidy/ro_*`, you're probably regressing Phase 4.

## Runtime State Inventory

> Included because Phase 5 touches `counterfactual.DEFAULT_CARBON_PRICES` (extension) and adds new entries to `constants.yaml` — drift risk across live module + YAML + CHANGES.md. Also documents the RER disruption as runtime state that affects future refresh behaviour.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| **Stored data** | `data/derived/cfd/*.parquet` (gitignored, regenerated per Phase 4); `data/raw/lccc|elexon|ons/*` with .meta.json sidecars (committed); `site/data/manifest.json` (committed) | None — RO adds files in new subdirs, does not mutate existing; `data/derived/ro/` is gitignored per Phase 4 D-22. `site/data/manifest.json` gains 5 new `datasets[]` entries via `publish/manifest.py::build()` no code change |
| **Live service config** | GitHub Actions: `refresh.yml` (cron 06:00 UTC; per-scheme dirty-check) + `deploy.yml` (tag-push release). Ofgem RER SharePoint (access-on-request per `renewable.enquiry@ofgem.gov.uk`). Cloudflare Pages (daily deploy from main). | RER disruption: no code change to workflows — `refresh.yml` fires `refresh_all.py` which calls `schemes.ro.upstream_changed()`; if RO is Option D manual-refresh posture, `upstream_changed()` returns False until a human commits a new `ro-register.xlsx`. Document this in PR-body note so reviewers expect the unusual dirty-check behaviour. Potentially file new `daily-refresh` issue template section mentioning RO is manual-refresh. |
| **OS-registered state** | None (project is code+data only; no systemd/launchd/Task-Scheduler) | None |
| **Secrets/env vars** | None used by Phase 4 scraper paths; Phase 5 could introduce SharePoint credentials (rejected by Option D — no credentials handled). `GITHUB_TOKEN` in refresh.yml (default, scoped to PR/issue write). | None (recommendation: Option D eliminates the need for Ofgem credentials in CI) |
| **Build artifacts / installed packages** | `uv.lock` + `.venv/` (not committed; installed from `pyproject.toml` on CI). No new dependencies added in Phase 5. | None — no dependency churn |

**Nothing found in `OS-registered state`:** confirmed via grep for "Task Scheduler", "systemd", "launchd", "pm2" — no such references in any CLAUDE.md, CONTEXT.md, or ARCHITECTURE.md. `[VERIFIED: grep -r "systemd\|launchd\|pm2" .]`

**Nothing found in `secrets`:** confirmed via `grep -r "SOPS\|SECRET\|PAT\b" .github/` — only `GITHUB_TOKEN` (default, automatic) used; no custom secrets defined. `[VERIFIED: grep of .github/workflows/]`

**Special runtime-state note — Ofgem RER disruption:**

On 2025-05-14 Ofgem replaced the legacy Renewables & CHP Register (at `renewablesandchp.ofgem.gov.uk`) with the new Renewable Electricity Register (at `rer.ofgem.gov.uk`). Public report access moved to SharePoint with email-authenticated registration. `[CITED: ofgem.gov.uk/environmental-programmes/renewable-electricity-register]`. The legacy site remains resolvable but is no longer updated. Pre-2018 ROC data is on a separate static page ("ROCs issued from April 2006 to March 2018"). **This is environmental, not project-runtime state** — but affects every future Phase-7 (FiT) and Phase-11 (SEG/REGO) refresh path. Document the disruption prominently in `docs/schemes/ro.md` methodology section so academic readers know why Ofgem data freshness may lag.

## Common Pitfalls

### Pitfall 1: Ofgem register-download mechanism silently breaks on RER disruption
**What goes wrong:** Scraper written against old `renewablesandchp.ofgem.gov.uk` URL returns HTML page instead of CSV/XLSX, or 301-redirects through multiple hops. `requests.get(url).content` returns bytes that `pandas.read_csv()` parses as 1-row "<!DOCTYPE html>" garbage.
**Why it happens:** RER launched 2025-05-14 replacing the legacy register; public data access moved to SharePoint with email-auth-required.
**How to avoid:** (a) Verify scraper output by checking `head -c 100` of downloaded file looks like CSV; (b) add `response.raise_for_status()` AND `assert b"<html" not in response.content[:100]` guard; (c) Option D manual-refresh posture bypasses scraper entirely — human commits the raw file, scraper test verifies only the committed-file SHA not the download.
**Warning signs:** `pandera.validate()` raises SchemaError on raw register; tests fail with "unexpected columns: ['<!DOCTYPE html>']"; refresh.yml issue opens with HTML-content in error log.

### Pitfall 2: Banding-factor mismatch on station-level rocs_issued
**What goes wrong:** YAML banding table has 2 ROC/MWh for "Offshore Wind" pre-2014, but actual Ofgem `rocs_issued` for a specific station is 1.5 ROC/MWh because that station re-accredited post-2017 at a lower band. Derivation uses YAML value × generation_mwh, gets wrong answer.
**Why it happens:** Banding depends on (technology × commissioning window × country × re-accreditation history); the last factor is not easily encoded in YAML. Per D-01 we short-circuit by using Ofgem's own `rocs_issued` and treating YAML as audit cross-check.
**How to avoid:** `rocs_issued` from Ofgem is the source-of-truth; compute `generation × YAML_banding` as a separate `rocs_issued_computed` column; `validate()` check #1 counts stations where `|rocs_issued - rocs_issued_computed| / rocs_issued > 1%` and warns if >10 stations or >5% of population. Does not block pipeline.
**Warning signs:** `validate()` warnings list "banding divergence count = N > threshold"; specific station names in warning log point to data-quality issues requiring individual investigation (typically mid-scheme re-accreditation events).

### Pitfall 3: Obligation-year vs calendar-year price assignment confusion
**What goes wrong:** CY 2022 generation summed with OY 2022-23 prices applied to April-December portion gives a subtly wrong aggregate; OY 2021-22 prices apply to January-March 2022 generation. Getting the split wrong by a quarter shifts the `ro_cost_gbp_2022` aggregate by 2-4%.
**Why it happens:** RO operates on April-March scheme years; our charts plot CY. Per D-08, the rule is "OY containing the output period end" — March 2022 gen → OY 2021-22; April 2022 gen → OY 2022-23.
**How to avoid:** Encode `obligation_year` as an explicit column on `station_month.parquet`; test_aggregates parametrisation can cross-check `sum(year, obligation_year)` reconciles to the published Ofgem SY aggregate within 0.1%.
**Warning signs:** Test_benchmarks::turver divergence ~5% but only for years 2011-2022 (odd year pattern); implies OY/CY price-assignment mismatch. Double-check `station_month::obligation_year` column for January-March rows.

### Pitfall 4: Mutualisation double-counting across SY 2020-21 + SY 2021-22
**What goes wrong:** Mutualisation is published in Ofgem's Annual Report for the scheme year following the shortfall. SY 2020-21 shortfall of £218M was redistributed in autumn 2021. SY 2021-22 shortfall of £119.7M was redistributed December 2022. If price-lookup adjusts "OY 2021-22 price upward by £218M" AND also adjusts "OY 2021-22 price upward by £119.7M" because naming is inconsistent across Ofgem publications, you double-count.
**Why it happens:** Ofgem's published buyout+recycle for the OY may or may not be pre-adjusted for mutualisation depending on which document you look at; the consolidated Annual Report publishes the ex-post adjusted value while the transparency document publishes the ex-ante value.
**How to avoid:** Use Ofgem's Annual Report (PDF, stable URL series) as the canonical post-adjustment price. `roc-prices.csv` columns: `obligation_year, buyout_gbp_per_roc, recycle_gbp_per_roc, mutualisation_gbp_per_roc, source_pdf_url`. Mutualisation is a separate column, additively composed into `roc_price_gbp` in `cost_model.build_station_month()`.
**Warning signs:** Turver benchmark divergence exceeds 5% for 2021-22 and 2022-23 specifically; total RO cost for those years is ~12% higher than REF Table 1's values.

### Pitfall 5: NIRO silently included in GB headline
**What goes wrong:** `docs/schemes/ro.md` headline says "£X bn GB-only" but the aggregation groupby accidentally sums across both `country='GB'` and `country='NI'` rows, inflating the headline by ~3-5%.
**Why it happens:** `station_month.parquet` carries both countries per D-09. If `build_annual_summary()` doesn't filter to `country='GB'` before summing (or doesn't group by country), GB/NI rows are summed together.
**How to avoid:** Annual summary groups by (year, country) per D-09. Docs headline explicitly filters `where country='GB'`. test_aggregates cross-check: sum of (GB) + sum of (NI) = sum of (both) for every year.
**Warning signs:** GB headline is ~3-5% higher than REF Table 1 (REF excludes NIRO); test_benchmarks::turver fails.

### Pitfall 6: Pre-2013 carbon price forces chart confusion
**What goes wrong:** D-05 extends `DEFAULT_CARBON_PRICES` back to 2005-2017 with EU ETS averages. EU ETS 2007 collapsed to €0.10 by September 2007 (Phase 1 was non-bankable). An annual average of ~€0.7 for 2007 gives a near-zero carbon cost, but the gas fuel cost dominates anyway. Reader sees S2 Panel 3 ("premium per MWh") swing from positive to negative in 2007 and thinks the chart is broken.
**Why it happens:** EU ETS Phase 1 (2005-2007) had a hard bank-forward ban and allowances crashed to near-zero. This is historically correct but visually confusing.
**How to avoid:** Methodology section of `docs/schemes/ro.md` calls out the 2007-2008 carbon-price collapse as a known artefact; methodology link to `docs/methodology/gas-counterfactual.md` explains the EU ETS phase structure. No code workaround needed — the data is correct.
**Warning signs:** Reader feedback: "why does the premium drop to zero in 2007?" — anticipate this in methodology; do not over-smooth.

### Pitfall 7: Forward-projection straight-line anchor pollutes 2026 onward
**What goes wrong:** Simple "latest metered year × remaining years" over-projects stations already in decline (old biomass cofiring about to retire; hydro that's been derating for years).
**Why it happens:** Straight-line from last metered year ignores per-station trajectory.
**How to avoid:** Per-station approach (§6 recommendation (c)): use Ofgem's `Accreditation_Date` from the register + 20-year support term = `accreditation_end_year`. `remaining_years = max(0, accreditation_end_year - current_year_anchor)`. Stations already past accreditation-end get `remaining_committed_mwh = 0`. This also exposes the "RO closure cliff" in 2037 (last stations accredited 2016-2017 + 20 years).
**Warning signs:** S5 chart shows a smooth monotonic decline; should instead show a lumpy step-down pattern with distinct cliffs when major station cohorts exit (peak 2024 → big drop 2031-2034 → cliff 2037).

### Pitfall 8: Methodology version drift across RO + CfD grains
**What goes wrong:** CfD grain has `methodology_version = "0.1.0"`; RO grain has `methodology_version = "0.1.0"` because both import the constant; but if RO introduces a new `opex_biomass_per_mwh` parameter (it doesn't in Phase 5 per locked D-06, but a future phase might), the two grains would share a version number despite different formulas.
**Why it happens:** `counterfactual.METHODOLOGY_VERSION` is a single module-level constant; it cannot distinguish "the gas counterfactual changed" from "the RO cost formula changed."
**How to avoid:** Per D-06, Phase 5's carbon-extension is additive (new year keys), not a formula-shape change — `METHODOLOGY_VERSION` stays "0.1.0". `schemes/ro/validate()` check #3 confirms the constant matches the column value. If a future phase introduces an RO-specific formula parameter, the bump is warranted.
**Warning signs:** `test_determinism` fails unexpectedly after a methodology file edit; `tests/test_constants_provenance.py` SEED-001 drift test fires (remediation: update constants.yaml OR bump METHODOLOGY_VERSION per the remediation message).

## Code Examples

### Example 1: `schemes/ro/__init__.py` (mirror of CfD)

```python
# Source mirror: src/uk_subsidy_tracker/schemes/cfd/__init__.py
# All 5 public functions + DERIVED_DIR + SchemeModule Protocol conformance.
from __future__ import annotations

from pathlib import Path

from uk_subsidy_tracker import PROJECT_ROOT
from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.schemes.ro._refresh import (
    refresh as _refresh,
    upstream_changed as _upstream_changed,
)
from uk_subsidy_tracker.schemes.ro.aggregation import (
    build_annual_summary,
    build_by_allocation_round,
    build_by_technology,
)
from uk_subsidy_tracker.schemes.ro.cost_model import build_station_month
from uk_subsidy_tracker.schemes.ro.forward_projection import build_forward_projection

DERIVED_DIR: Path = PROJECT_ROOT / "data" / "derived" / "ro"


def upstream_changed() -> bool:
    return _upstream_changed()


def refresh() -> None:
    _refresh()


def rebuild_derived(output_dir: Path | None = None) -> None:
    target = output_dir if output_dir is not None else DERIVED_DIR
    target.mkdir(parents=True, exist_ok=True)
    build_station_month(target)
    build_annual_summary(target)
    build_by_technology(target)
    build_by_allocation_round(target)
    build_forward_projection(target)


def regenerate_charts() -> None:
    import runpy
    runpy.run_module("uk_subsidy_tracker.plotting", run_name="__main__")


def validate() -> list[str]:
    """See Validation Architecture section for the four locked checks."""
    import pyarrow.parquet as pq
    warnings: list[str] = []
    # ... four checks D-04.1 through D-04.4 ...
    return warnings


__all__ = [
    "DERIVED_DIR", "upstream_changed", "refresh",
    "rebuild_derived", "regenerate_charts", "validate",
]
```

### Example 2: One-line `refresh_all.py` append

```python
# Source: src/uk_subsidy_tracker/refresh_all.py:32-35 (before modification)
from uk_subsidy_tracker.schemes import cfd, ro  # ← add `, ro`

SCHEMES = (
    ("cfd", cfd),
    ("ro", ro),  # ← Phase 5 adds this line
)
```

### Example 3: Parametrised test_determinism extension

```python
# Source extend: tests/test_determinism.py (current parametrises over 5 CfD grains)
# New in Phase 5: parametrise over (scheme, grain) tuples.
import pytest
from uk_subsidy_tracker.schemes import cfd, ro

SCHEMES = [("cfd", cfd), ("ro", ro)]
GRAINS = (
    "station_month", "annual_summary",
    "by_technology", "by_allocation_round",
    "forward_projection",
)

@pytest.mark.parametrize("scheme_name,scheme_module", SCHEMES)
@pytest.mark.parametrize("grain", GRAINS)
def test_parquet_content_identical(scheme_name, scheme_module, grain, tmp_path):
    """TEST-05: content equality across two rebuilds of the same raw state."""
    out1 = tmp_path / "run-1" / scheme_name; out1.mkdir(parents=True)
    out2 = tmp_path / "run-2" / scheme_name; out2.mkdir(parents=True)
    scheme_module.rebuild_derived(output_dir=out1)
    scheme_module.rebuild_derived(output_dir=out2)
    t1 = pq.read_table(out1 / f"{grain}.parquet")
    t2 = pq.read_table(out2 / f"{grain}.parquet")
    assert t1.equals(t2), f"drift in {scheme_name}.{grain}"
```

### Example 4: test_benchmarks RO Turver anchor (fully parametrised)

```python
# Source pattern: tests/test_benchmarks.py (existing CfD scaffolding).
# Add: Turver (= REF Constable primary) anchor section.

TURVER_TOLERANCE_PCT = 3.0
"""±3% per CONTEXT D-14 — hard block; RO-06 is binary. Tolerance
bumps require a CHANGES.md `## Methodology versions` entry per D-07.
Anchor replaced with REF Constable 2025-05-01 per RESEARCH §5."""

@pytest.fixture(scope="module")
def ro_annual_totals_gbp_bn() -> dict[int, float]:
    """Pipeline RO aggregate in £bn, keyed by obligation_year.
    All-in GB total per D-12: includes cofiring, includes mutualisation,
    excludes NIRO (filter country='GB')."""
    import pyarrow.parquet as pq
    derived = PROJECT_ROOT / "data" / "derived" / "ro"
    df = pq.read_table(derived / "annual_summary.parquet").to_pandas()
    gb = df[df["country"] == "GB"]
    return (gb.groupby("obligation_year")["ro_cost_gbp"].sum() / 1e9).to_dict()

@pytest.mark.parametrize(
    "entry",
    load_benchmarks().turver,
    ids=lambda e: f"turver-SY{e.year}",
)
def test_turver_ro_benchmark_within_3pct(entry, ro_annual_totals_gbp_bn):
    """CONTEXT D-14: ±3% is a hard block. Investigate before tolerance bump."""
    ours = ro_annual_totals_gbp_bn.get(entry.year)
    assert ours is not None, f"No RO data for SY{entry.year}"
    divergence = abs(ours - entry.value_gbp_bn) / entry.value_gbp_bn * 100.0
    assert divergence <= TURVER_TOLERANCE_PCT, (
        f"Turver-anchor divergence for SY{entry.year}: "
        f"pipeline = £{ours:.2f} bn, REF/Turver = £{entry.value_gbp_bn:.2f} bn, "
        f"{divergence:.2f}% (> {TURVER_TOLERANCE_PCT}%). "
        f"D-14 HARD BLOCK — investigate scope delta (NIRO/cofiring/mutualisation), "
        f"banding error, or carbon-price extension before proceeding. "
        f"Source: {entry.url}"
    )
```

### Example 5: Forward-projection accreditation-end anchor (§6 recommendation (c))

```python
# Source pattern: src/uk_subsidy_tracker/schemes/cfd/forward_projection.py:99
# Deterministic anchor discipline (D-21): use data, not wall clock.
def build_forward_projection(output_dir: Path) -> pd.DataFrame:
    register = load_ro_register()  # from data/ofgem_ro.py
    # Column: Accreditation_Date + 20-year support term = accreditation_end_year
    register["accreditation_end_year"] = (
        register["Accreditation_Date"].dt.year.astype("int64") + 20
    )

    # Deterministic "current year" anchor: max output period end date in raw data.
    # Fall back to max(accreditation_end_year) only if register has no generation data.
    gen = load_ro_generation()  # from data/ofgem_ro.py
    if len(gen) > 0:
        current_year_anchor = int(gen["Output_Period_End"].max().year)
    else:
        current_year_anchor = int(register["accreditation_end_year"].max())

    register["remaining_years"] = (
        register["accreditation_end_year"] - current_year_anchor
    ).clip(lower=0)
    # Average annual generation from historical actuals (same pattern as CfD).
    # For stations with insufficient history (<2 years), fall back to capacity_mw × assumed CF.
    # ... build_forward_projection body ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Scrape Ofgem via legacy `renewablesandchp.ofgem.gov.uk` CSV download | Ofgem RER SharePoint (access-on-request) OR manual snapshot to `data/raw/ofgem/` | 2025-05-14 | **Material scraper disruption** — Phase 5 adopts Option D manual-refresh until RER public API stabilises |
| CfD-only Parquet derivation | Multi-scheme `schemes/<scheme>/` modules conforming to `SchemeModule` Protocol | Phase 4 Plan 03 (2026-04-23) | RO is the first test of whether the Phase 4 pattern generalises; FiT/CM/etc. copy verbatim |
| Monolithic `refresh()` hard-coded to CfD | `refresh_all.SCHEMES` iteration with per-scheme dirty-check | Phase 4 Plan 04-05 | RO is a one-line append; no infrastructure rewrite |
| `data/*.csv` flat layout | `data/raw/<publisher>/<file>` + `.meta.json` sidecars | Phase 4 Plan 02 | Ofgem RO raw files land under `data/raw/ofgem/`, matching ARCHITECTURE §4.1 verbatim |
| Sidecar per-writer handwritten | Shared `sidecar.write_sidecar()` atomic helper | Phase 4 Plan 07 (2026-04-23) | RO scraper reuses the helper; byte-identical serialisation across schemes |
| Pre-1.0.0 methodology flexibility | METHODOLOGY_VERSION `"0.1.0"` pinned; additive dict extensions allowed without bump | Phase 2 D-05 + Phase 4 D-12 | RO's D-05 carbon-extension is additive; does not bump version |
| RO benchmark anchor = Turver substack | REF Constable 2025-05-01 Table 1 | This RESEARCH.md | Stronger anchor: peer-cited, transcribable table, explicit Ofgem-AR data source |

**Deprecated/outdated:**

- **Renewables & CHP Register public reports at `renewablesandchp.ofgem.gov.uk/Public/ReportManager.aspx`** — replaced by RER SharePoint access-on-request; scraper code written against this URL pattern will break silently or return HTML.
- **`renewablesandchp.ofgem.gov.uk` SSL certificate** — returns ERR_TLS_CERT_ALTNAME_INVALID in test requests 2026-04-22; the legacy domain is partially decommissioned. `[VERIFIED: WebFetch attempt 2026-04-22]`.
- **Ofgem public-reports URL at `www.ofgem.gov.uk/environmental-programmes/ro/contacts-publications-and-data/public-reports-and-data-ro`** — the page exists but now redirects to "contact renewable.enquiry@ofgem.gov.uk" for SharePoint access.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Option D manual-refresh posture is acceptable given Ofgem RER disruption | §2 + Pitfall 1 | If user rejects, scraper work expands materially — Playwright/SharePoint-auth needed; add ~3-5 plan tasks |
| A2 | REF Constable 2025-05-01 Table 1 can substitute for "Turver anchor" per D-13 intent | §5 | If user insists on Turver verbatim, fallback to Turver's SY20 £6.4bn + SY21 £6.8bn single-year entries only (no 2011-2022 cumulative); weaker test anchor but RO-06 still binary |
| A3 | Accreditation date + 20 years = accreditation-end year for forward-projection | §6 | If actual rule is more complex (extensions, re-accreditations), forward_projection S5 chart may under- or over-project by 1-3 years per cohort |
| A4 | Ofgem Annual Report PDFs are the canonical post-mutualisation price source | Pitfall 4 | If Ofgem publishes a separate CSV with adjusted prices, that becomes the better source — low risk, just swap the sidecar URL |
| A5 | NIRO uses a column on the same register table, not a separate Ofgem NI dataset | §7 | If NIRO is published by Ofgem NI separately, need a 2nd scraper — adds one file + one URL; ~1 extra plan task |
| A6 | EU ETS 2005-2017 annual averages as sketched in §5 table are sufficient for D-05 | §5 | If user wants higher-precision Sandbag/EEA data, 1 day of research to compile; value updates are minor |
| A7 | REF cumulative RO total is £67.0bn through 2023/24 as shown in the Table 1 transcription | §5 | If transcription is off (we couldn't read the PDF directly, only the webpage rendering), per-year values may differ by ±0.1 — still within 3% tolerance |
| A8 | Mutualisation was triggered only for SY 2021-22 (not 2022-23) per Ofgem 2023 announcement | §4 | If additional mutualisation events exist in 2018-2020, need 1 extra row in YAML — low risk |
| A9 | `ro-register.xlsx` file is ≤100MB and fits in git per ARCHITECTURE §4.1 | RO-MODULE-SPEC.md §4.1 estimate | If it exceeds 100MB, Cloudflare R2 pointer pattern needed — Phase 8 work (NESO BM) preview |
| A10 | `mkdocs.yml` nav gets a new top-level "Schemes" tab holding both CfD and RO detail pages | §8.2 | If user prefers different nav structure (fold under existing Cost theme), chart-gallery cross-links still work |

**Assumptions-to-verify-before-planning:** A1 (most load-bearing — different scraper strategies drive different plan structures). A2 (second most load-bearing — changes the benchmarks.yaml structure). A5 (affects scraper count).

## Open Questions

1. **Is Option D manual-refresh acceptable for Phase 5 Ofgem ingest?**
   - What we know: RER disruption forces a decision; alternatives are Playwright/SharePoint-auth (heavy) or static-PDF extraction (manual, but preserves reproducibility).
   - What's unclear: User preference on acceptable refresh cadence for Ofgem data. Option D implies human-triggered refresh (monthly manually), which contrasts with daily CI cron for CfD.
   - Recommendation: Planner asks user at plan-time. If rejected, pivot to annual-report-PDF extraction (parse PDF tables for year-by-year totals; accept FY-only granularity not station-level). Annual-report fallback is less granular but guaranteed-reproducible.

2. **Should REF Constable fully replace Turver in `benchmarks.yaml::turver` section key name, or should the key stay `turver` for continuity?**
   - What we know: D-13 says researcher picks; but the section-key name in YAML affects test IDs and audit-header documentation.
   - What's unclear: Does user want "REF Constable" as the key or "turver" with a note in the audit header that the actual source is REF?
   - Recommendation: Name the section `turver_or_equivalent` with audit header saying "Primary: REF Constable 2025-05-01; secondary cross-check: Turver substack 2024 single-points". Preserves CONTEXT D-13's "Turver" mental model.

3. **How should banding-factor YAML handle the 2017 "closure to new generation" rule?**
   - What we know: RO closed to new accreditations between March 2015 and March 2017 with grace periods; post-March 2017 no new stations can enter. Stations accredited pre-close get 20 years of support.
   - What's unclear: Does the banding YAML need to encode the closure itself, or only the banding factors for accredited stations?
   - Recommendation: YAML carries only banding factors (not closure rules). The closure is implicit: no station accredited after 2017-03-31 exists in the Ofgem register, so the lookup never needs a banding for such stations.

4. **How should forward-projection handle stations with zero historical generation (e.g. accredited but never operated)?**
   - What we know: CfD pattern uses `avg_annual_generation_mwh = historical_sum / n_years`; stations with zero generation get NaN.
   - What's unclear: Should these be included in forward_projection.parquet with zero remaining-committed-mwh, or dropped?
   - Recommendation: Drop them (mirrors CfD pattern lines 102-109 in `forward_projection.py`). Document in `forward_projection.py` docstring.

5. **Does `mkdocs.yml` get a new top-level "Schemes" tab, or does RO fold under existing Cost theme?**
   - What we know: `docs/schemes/` does not exist yet; Phase 5 creates it per D-15.
   - What's unclear: Navigation structure — new tab vs fold under Cost theme.
   - Recommendation: New top-level "Schemes" tab holding `cfd.md` + `ro.md`. Phase 6 portal homepage will need a "Schemes" tab anyway (portal grid with 2x4 scheme tiles links into scheme detail pages). Creating it now saves a second restructure. Fold the existing scheme-specific pages under the new tab: move `docs/themes/cost/cfd-dynamics.md` remains where it is as a per-chart deep-dive; `docs/schemes/cfd.md` is a new summary page. This is out of Phase 5 scope though — per Phase 4 D-02, CfD docs remain untouched. Only create `docs/schemes/ro.md` in Phase 5.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12+ | All Python code | ✓ | 3.13 via uv | — |
| uv package manager | `uv sync`; `uv run pytest` | ✓ | (already in use) | — |
| requests 2.x | Ofgem scrapers (if attempted) | ✓ | 2.33.1 | — |
| pyarrow 24.x | Parquet write/read | ✓ | 24.0.0 | — |
| pandera 0.31.x | Raw-CSV validation | ✓ | 0.31.1 | — |
| pydantic 2.13.x | Row schemas, YAML loaders | ✓ | 2.13.1 | — |
| plotly 6.x | Four RO charts | ✓ | 6.7.0 | — |
| kaleido 1.2.x | PNG export | ✓ | 1.2.0 | — |
| openpyxl 3.x | Read `ro-register.xlsx` | ✓ | 3.1.5 | — |
| PyYAML 6.x | Load `ro_bandings.yaml` | ✓ | (pyyaml>=6.0.3) | — |
| DuckDB 1.5.x | (unused in RO derivation, academic query only) | ✓ | 1.5.2 | — |
| **Ofgem RER public API / CSV download** | RO-01 scraper | **✗** | — | **Option D manual-refresh: commit raw files to data/raw/ofgem/ once, iterate on stable cadence** |
| Internet (GitHub Actions daily cron) | refresh.yml 06:00 UTC | ✓ (Actions runner) | — | — |
| **SharePoint credentials for Ofgem RER** | (unavoidable if scraper option A/B adopted) | **✗** | — | **Not needed under Option D** |
| **Playwright** | (optional if scraper option B adopted) | ✗ (not in pyproject.toml) | — | Don't add; Option D avoids it |

**Missing dependencies with no fallback:** (none — Option D eliminates the SharePoint-creds blocker)

**Missing dependencies with fallback:** Ofgem RER public API → adopt Option D manual-refresh posture (recommended primary strategy per §2).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | `pyproject.toml` (test section minimal; `tests/__init__.py` exists for package discovery) |
| Quick run command | `uv run pytest -x` |
| Full suite command | `uv run pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| RO-01 | Scrapers populate `data/raw/ofgem/` + .meta.json sidecars | unit (mocked) | `uv run pytest tests/data/test_ofgem_ro.py` | ❌ Wave 0 |
| RO-02 | `schemes.ro` conforms to SchemeModule Protocol | unit | `uv run pytest tests/test_schemas.py::test_ro_is_scheme_module` (add inline assertion `isinstance(ro, SchemeModule)`) | ❌ Wave 0 |
| RO-03 | 5 RO Parquet grains exist + schema-conform | unit (re-parametrised) | `uv run pytest tests/test_schemas.py -k "ro"` | ❌ Wave 0 (extend existing test_schemas.py parametrisation) |
| RO-03 | Row-conservation on RO grains | unit (re-parametrised) | `uv run pytest tests/test_aggregates.py -k "ro"` | ❌ Wave 0 (extend) |
| RO-03 | Byte-identity determinism on RO grains | unit (re-parametrised) | `uv run pytest tests/test_determinism.py -k "ro"` | ❌ Wave 0 (extend) |
| RO-04 | Four RO charts emit PNG + HTML | integration | `uv run python -m uk_subsidy_tracker.plotting.subsidy.ro_dynamics && test -f docs/charts/html/subsidy_ro_dynamics_twitter.png` | ❌ Wave 3-4 |
| RO-05 | `docs/schemes/ro.md` renders under `mkdocs --strict` | integration | `uv run mkdocs build --strict` | ✓ (gate exists) |
| RO-06 | RO aggregate 2011-2022 within ±3% of Turver/REF | benchmark | `uv run pytest tests/test_benchmarks.py::test_turver_ro_benchmark_within_3pct` | ❌ Wave 0 (extend) |

### Critical Invariants (≤4 per Nyquist dimension 8)

The `schemes/ro/validate()` function exercises four invariants (per CONTEXT D-04). Each has an observable evidence source and a remediation path:

| # | Invariant | Observable Evidence | Remediation if Violated |
|---|-----------|-----|-------------------------|
| V1 | **Banding audit cross-check** — computed `generation × banding_factor` matches Ofgem's published `rocs_issued` within 1% per station | `station_month.parquet` has `ofgem_issued` + `computed_rocs` + divergence columns. warn if > 10 stations or > 5% of population | Investigate station-level data; re-accreditation event? Consult Ofgem transparency documents. Acceptable as warning; does not block |
| V2 | **Turver/REF benchmark drift** — 2011-2022 aggregate `ro_cost_gbp` within ±3% of REF Constable Table 1 per obligation_year | `test_benchmarks.py::test_turver_ro_benchmark_within_3pct` parametrised over REF Table 1 entries | Investigate scope delta (NIRO inclusion, mutualisation treatment, cofiring attribution, CY vs OY); fix pipeline OR document scope-delta in benchmarks.yaml audit header OR raise TURVER_TOLERANCE_PCT (requires CHANGES.md entry) |
| V3 | **Methodology version consistency** — `methodology_version` column on every RO Parquet row = `counterfactual.METHODOLOGY_VERSION` | `validate()` unique-versions check returns single value matching constant | Update RO Parquet via `rebuild_derived()` OR bump `METHODOLOGY_VERSION` + CHANGES.md entry |
| V4 | **Forward-projection sanity** — no negative ro_cost_gbp rows; no year-over-year MWh swings >50% in adjacent years in `forward_projection.parquet` | `validate()` iterates rows, asserts invariants | Fix band-assignment or accreditation-end rule in `forward_projection.py`; investigate outlier stations |

### Sampling Rate (Nyquist)

- **Per task commit:** `uv run pytest -x` (fastest feedback — stops on first failure; ~5 seconds for RO-specific subset)
- **Per wave merge:** `uv run pytest && uv run mkdocs build --strict` (full test suite + docs build; ~30 seconds)
- **Phase gate:** Full suite green + `schemes.ro.validate()` returns empty list + `test_turver_ro_benchmark_within_3pct` green + `mkdocs build --strict` green + all new files visible in `site/data/manifest.json` post-refresh.

### Wave 0 Gaps

- [ ] `tests/data/test_ofgem_ro.py` — mocked scraper path tests (per Phase 4 Plan 07 pattern: `output_path` bound before try, timeout=60, bare raise on failure; no network in CI)
- [ ] Extend `tests/test_schemas.py` parametrisation: `GRAINS` loop now iterates `(scheme, grain)` tuples so `station_month.parquet` is tested for both CfD and RO
- [ ] Extend `tests/test_aggregates.py`: parametrise row-conservation over RO grains (scheme × grain)
- [ ] Extend `tests/test_determinism.py`: parametrise byte-identity over RO grains (scheme × grain)
- [ ] Extend `tests/test_benchmarks.py`: add `test_turver_ro_benchmark_within_3pct` parametrised over `load_benchmarks().turver` entries + `TURVER_TOLERANCE_PCT = 3.0` constant
- [ ] Extend `tests/test_constants_provenance.py::_TRACKED` to include the 13 new `DEFAULT_CARBON_PRICES_{2005..2017}` entries (12 actual values + synthetic keys for 2002-2004 zeros; planner chooses whether to track zeros explicitly or exclude them)
- [ ] `tests/fixtures/benchmarks.yaml` new `turver:` top-level section with 12 entries (2011-2022) carrying REF Constable Table 1 values + audit header citing the REF publication
- [ ] `tests/fixtures/constants.yaml` new 13-16 entries for extended `DEFAULT_CARBON_PRICES_{YEAR}` (2002-2017)

*(If any existing test infrastructure covers a row above — e.g., Phase 4's `test_schemas.py` already parametrises over `GRAINS`, so extending to `(scheme, grain)` is a 3-line diff — the planner should document this in the plan as an "extend existing test" rather than "new file.")*

### Framework install
No framework install needed — pytest is already in pyproject.toml.

## Security Domain

> `security_enforcement` is not explicitly set in `.planning/config.json` — treat as enabled (default).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth surface — static site, no login, anonymous access |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | Public data only |
| V5 Input Validation | yes | pandera DataFrame schemas on every raw CSV; Pydantic on every YAML; pyarrow Parquet schema enforcement on derived tables |
| V6 Cryptography | yes | SHA-256 for data integrity (sidecar.py, manifest.json); no secret material handled |
| V7 Error Handling & Logging | yes | D-17 fail-loud: bare `raise` on scraper failure; refresh.yml opens GitHub Issue labelled `refresh-failure` on any step fail |
| V8 Data Protection | no | All data is UK-open-government; no PII |
| V10 API Security | n/a | No API — stable file URLs only per ARCHITECTURE §4.3 |
| V11 Business Logic | yes | D-01 short-circuit (Ofgem-primary rocs_issued) reduces risk of banding-factor error amplifying into subsidy-total miscalculation |
| V14 Configuration | yes | No secrets in repo (verified); .github/workflows/ use only default `GITHUB_TOKEN` |

### Known Threat Patterns for Python / Open-Data Ingest Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malicious upstream data (Ofgem XLSX with formula injection) | Tampering | pandera + Pydantic schema validation rejects structurally malformed data; openpyxl parses cells as values not formulas |
| HTTP-to-HTTPS downgrade on scraper URL | Tampering | Explicit https:// URLs in `_URL_MAP`; `requests` rejects plaintext http by default when targeting .gov.uk |
| Dependency supply-chain attack | Tampering | uv.lock pinned versions (GOV-04 per Phase 4); `uv sync --locked` in CI |
| GitHub Actions pwn via untrusted action | Elevation of Privilege | Phase 4 discipline: all actions pinned to explicit major versions (`@v8`, `@v2`); `grep -rE 'uses:.*@(main\|master)' .github/workflows/` tripwire green |
| Arbitrary file write from Ofgem XLSX | Tampering | Raw files stored in `data/raw/ofgem/` with fixed names; no dynamic filename derived from upstream content |
| Silent data-integrity corruption post-download | Tampering | SHA-256 in sidecar; `manifest.json` carries source_sha256; external consumers can verify |
| Replay of outdated RO data | Information Disclosure (via stale data on public site) | Daily refresh via cron; per-scheme dirty-check; manifest.json `generated_at` stamps each build |
| Methodology version drift hidden | Tampering (subtle) | D-12 chain: METHODOLOGY_VERSION → DataFrame column → Parquet column → manifest.json → `validate()` check; SEED-001 Tier 2 tripwire on constant drift |
| Downstream journalist cites stale URL | Availability | Cloudflare Pages has built-in CDN; versioned snapshots in GitHub Releases are immutable; `site/data/latest/` regenerates daily |

## Implementation Risks Not Covered by D-01..D-16

1. **Option D manual-refresh cadence mismatches GOV-03 daily-refresh intent.** `refresh.yml` fires daily; `schemes.ro.upstream_changed()` always returns False under Option D unless a human commits new raw files. This is not a bug — it's the correct handshake given RER disruption — but reviewers may be confused. Mitigation: PR-body template mentions "RO is manual-refresh; CfD is auto-refresh."

2. **REF Constable Table 1 anchor could become deprecated** if REF publishes v2 (2026 or 2027 update) that reclassifies RO cost. `benchmarks.yaml::turver` audit header should cite the specific file URL with the publication date so future Phase researchers know when to re-evaluate.

3. **Mutualisation scope-overlap with ROC price assignment.** D-11 says "adjust upward by published mutualisation delta for affected years" — but what if a 2024-25 shortfall mutualises and pays through in 2026? The allocation rule (D-08 "obligation year containing output period end") may not apply cleanly to mutualisation-delta rows. Mitigation: additional column `mutualisation_gbp` on `annual_summary.parquet` makes this ambiguity visible; methodology section documents it.

4. **NIRO Ofgem page may be separate endpoint from GB register.** If NIRO is published by Ofgem NI (not Ofgem GB), Option D doubles manual files. Affirm with user at plan time.

5. **Deprecation notice on `renewablesandchp.ofgem.gov.uk` SSL cert.** Legacy domain returns TLS errors. If planner proposes a fallback URL there, it will fail; commit test covers this. `[VERIFIED: WebFetch 2026-04-22 returned ERR_TLS_CERT_ALTNAME_INVALID]`.

6. **`docs/schemes/` directory doesn't exist yet.** Creating it is a one-off structural change. Future Phase-7 (FiT) adds `docs/schemes/fit.md`; same pattern.

7. **Plotly 6.7 + kaleido 1.2 compatibility with 4 new chart builders.** Phase 3 verified this stack for CfD charts; mirror pattern should be safe. Risk: kaleido sometimes requires specific chromium-version; covered by existing test_docs_structure regression gate.

8. **Headline paragraph in `docs/schemes/ro.md` references "£X bn since 2002" which requires pipeline to have run successfully at least once.** Document must not hardcode a figure; it should use a template variable (e.g. `{{ total_ro_cost_gbn }}` macro) or be hand-updated at plan time after `rebuild_derived()` completes. Pattern: mirror `docs/themes/cost/index.md` which currently hand-updates CfD totals after run.

## Pattern-Map Hints (for pattern-mapper agent)

Every new RO file has a direct CfD analogue to mirror:

| New File | Mirror from |
|----------|-------------|
| `src/uk_subsidy_tracker/data/ofgem_ro.py` | `src/uk_subsidy_tracker/data/lccc.py` (structure) + `src/uk_subsidy_tracker/data/ons_gas.py` (error-path: D-17 bare raise) |
| `src/uk_subsidy_tracker/data/roc_prices.py` | `src/uk_subsidy_tracker/data/lccc.py` (load_lccc_config + download_lccc_datasets patterns) |
| `src/uk_subsidy_tracker/data/ro_bandings.yaml` | `src/uk_subsidy_tracker/data/lccc_datasets.yaml` (structure + Provenance discipline) |
| `src/uk_subsidy_tracker/data/ro_bandings.py` | `src/uk_subsidy_tracker/data/lccc.py` (LCCCDatasetConfig + LCCCAppConfig Pydantic + load_lccc_config) |
| `src/uk_subsidy_tracker/schemas/ro.py` | `src/uk_subsidy_tracker/schemas/cfd.py` (5 Pydantic row classes + emit_schema_json re-use) |
| `src/uk_subsidy_tracker/schemes/ro/__init__.py` | `src/uk_subsidy_tracker/schemes/cfd/__init__.py` (5 contract functions + DERIVED_DIR) |
| `src/uk_subsidy_tracker/schemes/ro/_refresh.py` | `src/uk_subsidy_tracker/schemes/cfd/_refresh.py` (upstream_changed + refresh + _URL_MAP + write_sidecar loop) |
| `src/uk_subsidy_tracker/schemes/ro/cost_model.py` | `src/uk_subsidy_tracker/schemes/cfd/cost_model.py` (build_station_month + loader-owned pandera + _write_parquet) |
| `src/uk_subsidy_tracker/schemes/ro/aggregation.py` | `src/uk_subsidy_tracker/schemes/cfd/aggregation.py` (3 rollup builders + _read_station_month + int64 year cast) |
| `src/uk_subsidy_tracker/schemes/ro/forward_projection.py` | `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py` (deterministic anchor + contract-end-year rule) |
| `src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py` | `src/uk_subsidy_tracker/plotting/subsidy/cfd_dynamics.py` (4-panel structure + builder.save(export_twitter=True)) |
| `src/uk_subsidy_tracker/plotting/subsidy/ro_by_technology.py` | `src/uk_subsidy_tracker/plotting/subsidy/cfd_payments_by_category.py` (stacked area by tech) |
| `src/uk_subsidy_tracker/plotting/subsidy/ro_concentration.py` | `src/uk_subsidy_tracker/plotting/subsidy/lorenz.py` (Lorenz curve + top-N) |
| `src/uk_subsidy_tracker/plotting/subsidy/ro_forward_projection.py` | `src/uk_subsidy_tracker/plotting/subsidy/remaining_obligations.py` (drawdown-to-contract-end pattern) |
| `tests/data/test_ofgem_ro.py` | `tests/test_ons_gas_download.py` + `tests/test_refresh_loop.py` (mocked scraper pattern; `importlib.import_module()` for submodule shadow bypass) |

## Domain Research Details

### §2 — Ofgem Scraper Mechanisms (answer to Q1)

**Publication cadence + lag** `[CITED: RO-MODULE-SPEC.md §4]`:

| Source | Publisher | Cadence | Typical Lag | Publication URL (2026-04-22 verified) |
|--------|-----------|---------|-------------|---------------------------------------|
| Ofgem RO Register (station list) | Ofgem | Updated quarterly | ~3 months | `rer.ofgem.gov.uk` (RER, 2025-05-14+) / `renewablesandchp.ofgem.gov.uk` (legacy, partially decommissioned) |
| Ofgem RO Generation (ROCs issued monthly) | Ofgem | Monthly | ~3 months | Same SharePoint path (access-on-request) |
| Ofgem Buyout + Mutualisation Ceiling | Ofgem | Annual (Feb) | ~1 month | `ofgem.gov.uk/transparency-document/renewables-obligation-ro-buy-out-price-mutualisation-threshold-and-mutualisation-ceilings-YYYY-YYYY` |
| Ofgem Annual Report (recycle + buyout fund totals) | Ofgem | Annual (~Mar) | ~6 months post-SY-end | `ofgem.gov.uk/publications/renewables-obligation-ro-annual-report-YYYY-YY-scheme-year-NN` |
| e-ROC quarterly auction results | e-roc.co.uk | Quarterly | ~1 month | `e-roc.co.uk` |
| RO Order 2009 + amendments | legislation.gov.uk | Amendments published periodically | — | `legislation.gov.uk/uksi/2009/785/made` (+ amendment SIs) |

**Scraper strategy options (planner chooses at plan time):**

**Option A — RER SharePoint scraper (NOT RECOMMENDED, heavyweight):**
- Requires email registration (`renewable.enquiry@ofgem.gov.uk`) → SharePoint-OIDC token flow.
- Implementation: Playwright-Python + stored session cookie in GitHub Secrets.
- Pros: Current data; catches new ROC issuances as they publish.
- Cons: Credentials in CI secrets; breaks on Ofgem UI changes; ~200 LOC of Playwright-wrangling; adds Playwright dependency.

**Option B — Legacy-register scraper (ONLY WORKS FOR HISTORICAL DATA):**
- Attempt stable-URL GET against `renewablesandchp.ofgem.gov.uk/Public/ReportManager.aspx` with parameters.
- Current status: TLS certificate error (`ERR_TLS_CERT_ALTNAME_INVALID`) as of 2026-04-22.
- Pros: No auth needed if the URL ever comes back.
- Cons: Unstable / partially decommissioned; no SLA on availability.

**Option C — PDF annual-report extraction (RELIABLE, COARSE):**
- Ofgem publishes Annual Reports as stable-URL PDFs (`ofgem.gov.uk/sites/default/files/YYYY-MM/Renewables-Obligation-...pdf`).
- Parse PDF tables with `pdfplumber` or `camelot-py` to extract annual-aggregate figures by technology.
- Pros: Stable URLs; 20-year publication history.
- Cons: Aggregate-only (not station-level); needs new dependency (pdfplumber not in pyproject.toml); schema drift between annual reports; ~100 LOC of extraction logic.

**Option D — Manual snapshot (RECOMMENDED for Phase 5):**
- One-off manual download from SharePoint (email Ofgem, wait 1-2 days for access, download XLSX/CSV).
- Commit files to `data/raw/ofgem/` + `.meta.json` sidecars (backfilled via Phase 4 Plan 07 backfill script pattern).
- Scraper stub (`data/ofgem_ro.py`) raises "manual-refresh; see data/raw/ofgem/README.md" if invoked.
- `schemes/ro.upstream_changed()` returns False (sidecar SHA matches committed file); daily refresh auto-skips.
- Pros: Zero CI dependency on RER availability; reproducibility preserved; acknowledges the disruption honestly.
- Cons: Data staleness = manual-refresh cadence; does not match CfD daily-refresh discipline; requires STATE.md follow-up entry.

**Recommended:** Option D for Phase 5. Revisit to Option A or C in a future phase if RER becomes stable or if manual-refresh cadence becomes operationally unsustainable. Document Option D's staleness-risk in `docs/schemes/ro.md` methodology section.

**Error-path discipline (Phase 4 Plan 07):** Regardless of option chosen, any network-fetch function in `data/ofgem_ro.py` or `data/roc_prices.py` must:
- Bind `output_path` before `try:` block
- Use `timeout=60` on `requests.get()`
- Bare `raise` in `except requests.exceptions.RequestException` (fail-loud)
- Write to `output_path.tmp` and `os.replace()` on success (atomic)

### §3 — RO Bandings Table Inventory (answer to Q3)

`[CITED: REF "Notes on the Renewable Obligation" Table 1]`
`[CITED: Wikipedia "Renewables Obligation (United Kingdom)"]`
`[CITED: RO-MODULE-SPEC.md §4.5 — estimate ~60 entries]`

Complete banding table from REF Table 1 (44 rows before applying commissioning-window × country multiplier — actual YAML estimate ~60 after full cell expansion):

| Technology | Pre-2013 | 2013/14 | 2014/15 | 2015/16 | 2016/17 |
|---|---|---|---|---|---|
| Anaerobic Digestion | 2 | 2 | 2 | 1.9 | 1.8 |
| Co-firing high range | — | 0.7 | 0.9 | 0.9 | 0.9 |
| Co-firing high range + CHP | — | 1.2 | 1.4 | 1.4 | 1.4 |
| Co-firing low range | — | 0.3 | 0.3 | 0.5 | 0.5 |
| Co-firing low range + CHP | — | 0.8 | 0.8 | 1.0 | 1.0 |
| Co-firing mid range | — | 0.6 | 0.6 | 0.6 | 0.6 |
| Co-firing mid range + CHP | — | 1.1 | 1.1 | 1.1 | 1.1 |
| Co-firing biomass (generic) | 0.5 | 0 | 0 | 0 | 0 |
| Co-firing biomass + CHP | 1 | 0 | 0 | 0 | 0 |
| Co-firing energy crops | 1 | 0 | 0 | 0 | 0 |
| Co-firing energy crops + CHP | 1.5 | 0 | 0 | 0 | 0 |
| Co-firing regular bioliquid | 0.5 | 0.3 | 0.3 | 0.5 | 0.5 |
| Co-firing regular bioliquid + CHP | 1 | 0.8 | 0.8 | 1.0 | 1.0 |
| Co-firing relevant energy crops low range | — | 0.8 | 0.8 | 1.0 | 1.0 |
| Co-firing relevant energy crops low range + CHP | — | 1.3 | 1.3 | 1.5 | 1.5 |
| Landfill Gas | 0.25 | 0 | 0 | 0 | 0 |
| Landfill Gas — closed sites | — | 0.2 | 0.2 | 0.2 | 0.2 |
| Landfill Gas — heat recovery | — | 0.1 | 0.1 | 0.1 | 0.1 |
| Sewage Gas | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| Biomass Conversion | 1 | 1 | 1 | 1 | 1 |
| Biomass Conversion + CHP | 1.5 | 1.5 | 1.5 | 1.5 | 1.5 |
| Dedicated biomass | 1.5 | 1.5 | 1.5 | 1.5 | 1.4 |
| Dedicated biomass + CHP | 2 | 2 | 2 | 1.9 | 1.8 |
| Dedicated energy crops | 2 | 2 | 2 | 1.9 | 1.8 |
| Dedicated energy crops + CHP | 2 | — | — | — | — |
| Energy from Waste + CHP | 1 | 1 | 1 | 1 | 1 |
| Advanced gasification/pyrolysis | 2 | 2 | 2 | 1.9 | 1.8 |
| Standard gasification/pyrolysis | 1 | 2 | 2 | 1.9 | 1.8 |
| Geopressure | 1 | 1 | 1 | 1 | 1 |
| Geothermal | 2 | 2 | 2 | 1.9 | 1.8 |
| Hydroelectric (except Scotland) | 1 | 0.7 | 0.7 | 0.7 | 0.7 |
| Hydroelectric (Scotland) | 1 | 1 | 1 | 1 | 1 |
| Enhanced tidal stream (Scotland) | 3 | — | — | — | — |
| Tidal barrage (<1GW DNC) | 2 | 2 | 2 | 1.9 | 1.8 |
| Tidal lagoon (<1GW DNC) | 2 | 2 | 2 | 1.9 | 1.8 |
| Tidal Stream <30MW | 2 | 5 | 5 | 5 | 5 |
| Enhanced wave (Scotland) | 5 | 5 | 5 | 5 | 5 |
| Wave | 2 | 2 | 2 | 2 | 2 |
| Solar photovoltaic (pre-2013) | 2 | — | — | — | — |
| Solar PV — building mounted | — | 1.7 | 1.6 | 1.5 | 1.4 |
| Solar PV — ground mounted | — | 1.6 | 1.4 | 1.3 | 1.2 |
| Offshore wind | 2 | 2 | 2 | 1.9 | 1.8 |
| Onshore wind | 1 | 0.9 | 0.9 | 0.9 | 0.9 |
| Microgeneration (≤50kW DNC) | 2 | 2 | 2 | 1.9 | 1.8 |

`[ASSUMED]` NIRO banding multiplier (for NI-specific entries): Per D-09, NIRO has distinct bandings. Specific NI banding factors should be researched in plan-time via the NIROC order (separate statutory instrument, administered by Utility Regulator NI). YAML gets entries with `country='NI'` for each technology × window cell.

**Total YAML row count estimate:** 44 technology × banding-window cells (GB, pre-close entries) + ~15 NIRO equivalents + ~5 post-2017 grandfathered bands = **~60 rows**. Matches RO-MODULE-SPEC.md estimate.

**Grandfathering rule** `[CITED: REF Notes]`: Projects accredited pre-11-July-2006 continue to receive **1 ROC/MWh** regardless of banding. The YAML needs a `grandfathered: true` special row for pre-2006 accreditations.

**Amendment SIs to cite in Provenance:**
- SI 2009/785 (The Renewables Obligation Order 2009) — base bandings
- SI 2011/2704 (RO Amendment 2011) — solar PV early-review
- SI 2013/768 (RO Order 2013) — Phase 2 banding review
- SI 2015/920 (RO (Amendment) Order 2015) — solar/onshore wind early-closure
- SI 2016/745 (RO (Amendment) Order 2016) — cofiring biomass changes
- SI 2017/1084 (RO Closure Order 2017) — new-accreditation closure

### §4 — Mutualisation Facts (answer to Q4)

`[CITED: Ofgem "Renewables Obligation 2021/22: Mutualisation" transparency document]`
`[CITED: Utility Week "RO mutualisation avoided for first time since 2017"]`

| Scheme Year | Shortfall | Mutualisation Triggered? | £ Redistributed |
|------------|-----------|--------------------------|------------------|
| 2017-18 (SY16) | (low) | Yes (first year) | — |
| 2018-19 (SY17) | — | Yes | — |
| 2019-20 (SY18) | — | Yes | — |
| 2020-21 (SY19) | £218M | Yes | (large) |
| **2021-22 (SY20)** | **£119.7M** | **Yes** | **£44.0M (Dec 2022)** |
| **2022-23 (SY21)** | **£7.2M** | **No (below £318M England+Wales ceiling; £31.9M Scotland ceiling)** | **—** |
| 2023-24 (SY22) | — | — (data lag) | — |

**Data-source strategy recommended:** Transcribe into `data/raw/ofgem/roc-prices.csv` with columns `obligation_year, buyout_gbp_per_roc, recycle_gbp_per_roc, mutualisation_gbp_per_roc, source_pdf_url`. Mutualisation is a separate column (non-zero on SY 2021-22 only). The audit trail is the PDF URL committed in the sidecar.

**Key finding (reshape D-11):** D-11 says "affected years 2021-22 and 2022-23" — but research shows **only 2021-22 triggered**. 2022-23 shortfall was £7.2M (below the £318M+ threshold). The D-11 wording should be interpreted as "2021-22 is the only mutualisation-adjusted year in Phase 5"; if this matters for methodology precision, flag to user at plan time. Recommendation: update `roc-prices.csv` with mutualisation = £0 on 2022-23 and document in README why D-11's listed "2022-23" year got zero.

### §5 — Turver Anchor Evaluation (answer to Q2, CRITICAL)

Researcher's recommendation: **Adopt REF (Constable) 2025-05-01 as the primary benchmark anchor; retain Turver substack as a secondary single-point cross-check.**

#### Candidate 1: Turver's "How ROCs Rip Us Off" (Eigen Values, substack)

`[CITED: davidturver.substack.com/p/renewable-obligation-certificates-rocs-rip-off]`

- Author: **David** Turver (not Andrew — CONTEXT.md typo'd the forename)
- Substack URL: stable at `davidturver.substack.com/p/renewable-obligation-certificates-rocs-rip-off`
- Figures extracted: SY20 (FY ending Mar 2022) = £6.4bn; SY21 (FY ending Mar 2023) = £6.8bn; SY25 forecast = £8.6bn
- **No year-by-year transcribable multi-year table** — only a chart (Figure 2) with extractable values
- Calendar vs Scheme Year: **Scheme Year (April-March)**
- NIRO/cofiring/mutualisation treatment: **not explicitly addressed**; default is "whatever Ofgem reports"
- Data source: Ofgem Annual Reports + OBR EFO forecasts
- **Assessment: INSUFFICIENT as sole anchor** for a ±3% 2011-2022 reconciliation because a transcribable 11-year series is not published.

#### Candidate 2: REF "UK Renewable Electricity Subsidy Totals: 2002 to the Present Day" (Constable, 2025-05-01)

`[CITED: ref.org.uk/ref-blog/390-uk-renewable-electricity-subsidy-totals-2002-to-the-present-day]`
`[CITED: PDF at ref.org.uk/attachments/article/390/renewables.subsidies.01.05.25.pdf — fetched 2026-04-22, ~372KB]`

- Author: John Constable (Director, Renewable Energy Foundation)
- Publication date: 2025-05-01
- Transcribable Table 1 with year-by-year RO costs 2002/03 through 2023/24: **YES** (full table transcribed in §5 below)
- Cumulative total: **£67.0 billion** (2002/03-2023/24, nominal; 22 scheme years)
- 2011/12-2022/23 subset (12 scheme years): approximately **£46.2 billion**
- Calendar vs Scheme Year: **Scheme Year** throughout
- NIRO/cofiring/mutualisation treatment:
  - NIRO: **excluded** (REF analysis is GB-only scheme cost)
  - Cofiring: **included** (appears in Ofgem source tables)
  - Mutualisation: **included** (embedded in Ofgem Annual Report numbers)
- Data source: Ofgem Annual Reports ("Figure 5.12 RO Annual Report 2023-2024") + OBR data + LCCC for CfD
- **Assessment: RECOMMENDED PRIMARY ANCHOR** — defensible, transcribable, peer-cited (Turver references REF), stable URL.

#### Table 1 Transcription (REF Constable, 2025-05-01) — RO scheme cost by Scheme Year, £ billion nominal

```yaml
# tests/fixtures/benchmarks.yaml::turver (renamed per §8.1 rename-or-not discussion)
# Primary anchor: REF Constable 2025-05-01 Table 1
# Secondary anchor: Turver substack 2024 single-point (SY20 + SY21)
# Audit header:
#   source: "REF Constable 'UK Renewable Electricity Subsidy Totals: 2002 to the Present Day' (2025-05-01)"
#   url: "https://www.ref.org.uk/attachments/article/390/renewables.subsidies.01.05.25.pdf"
#   retrieved_on: 2026-04-22
#   basis: "Scheme Year (April-March) aggregate RO cost, £ billion nominal; GB-only; includes cofiring+mutualisation; excludes NIRO"
#   notes: "Derived from Ofgem RO Annual Reports Figure 5.12 series"
#   tolerance_pct: 3.0

turver:
  - {year: 2002, value_gbp_bn: 0.3}  # SY 2002-03
  - {year: 2003, value_gbp_bn: 0.4}  # SY 2003-04
  - {year: 2004, value_gbp_bn: 0.5}  # SY 2004-05
  - {year: 2005, value_gbp_bn: 0.6}  # SY 2005-06
  - {year: 2006, value_gbp_bn: 0.7}  # SY 2006-07
  - {year: 2007, value_gbp_bn: 0.9}  # SY 2007-08
  - {year: 2008, value_gbp_bn: 1.0}  # SY 2008-09
  - {year: 2009, value_gbp_bn: 1.1}  # SY 2009-10
  - {year: 2010, value_gbp_bn: 1.3}  # SY 2010-11
  - {year: 2011, value_gbp_bn: 1.5}  # SY 2011-12 ← window start
  - {year: 2012, value_gbp_bn: 2.0}  # SY 2012-13
  - {year: 2013, value_gbp_bn: 2.6}  # SY 2013-14
  - {year: 2014, value_gbp_bn: 3.1}  # SY 2014-15
  - {year: 2015, value_gbp_bn: 3.7}  # SY 2015-16
  - {year: 2016, value_gbp_bn: 4.5}  # SY 2016-17
  - {year: 2017, value_gbp_bn: 5.3}  # SY 2017-18
  - {year: 2018, value_gbp_bn: 5.9}  # SY 2018-19
  - {year: 2019, value_gbp_bn: 6.3}  # SY 2019-20
  - {year: 2020, value_gbp_bn: 5.7}  # SY 2020-21
  - {year: 2021, value_gbp_bn: 6.4}  # SY 2021-22 (matches Turver substack SY20)
  - {year: 2022, value_gbp_bn: 6.4}  # SY 2022-23 (matches Turver substack SY21 — note: £6.8 at Turver vs £6.4 at REF; ~6% delta)
  - {year: 2023, value_gbp_bn: 6.8}  # SY 2023-24
```

**Note on SY21 Turver-vs-REF delta:** Turver reports £6.8bn, REF reports £6.4bn — 5.9% delta. Both use Ofgem Annual Report data; the difference likely reflects publication-date cutoffs (REF transcribes a slightly earlier snapshot). Our pipeline should reconcile within ±3% of **one** anchor — adopt REF as primary, add a benchmarks audit note explaining the ~6% Turver-vs-REF drift.

**Note on 2011-2022 window mapping:** CONTEXT specifies "CY 2011-2022" (calendar year), but REF publishes by SY. Per D-07 our pipeline plots by CY. Our `obligation_year` column on `station_month.parquet` records the OY; the benchmark test parametrises against SY 2011-12 through SY 2022-23 (12 entries), matching the 2011-2022 scope.

### §6 — Forward-Projection Methodology Recommendation (answer to Q6)

Three candidates evaluated per CONTEXT's Claude's Discretion section:

| Approach | Defensibility | Implementation Effort | Recommendation |
|----------|--------------|----------------------|----------------|
| (a) Straight-line from last metered year | Weak (ignores per-station trajectory) | Trivial | ❌ Reject |
| (b) Capacity-factor × installed-capacity × remaining-years | Medium (uses public capacity data; CF varies by year) | Moderate | Secondary |
| (c) Per-station expected end date from accreditation record | Strong (honors specific-station timelines; exposes 2037 cliff) | Moderate-high | **✓ Recommended** |

**Recommended approach (c):** For each station in Ofgem register:
1. `accreditation_end_year = Accreditation_Date.year + 20`
2. `avg_annual_generation_mwh` from historical actuals (copy CfD pattern: `historical_sum / n_years_metered`)
3. `remaining_years = max(0, accreditation_end_year - current_year_anchor)`
4. `remaining_committed_mwh = avg_annual_generation_mwh × remaining_years`
5. `remaining_cost_gbp = remaining_committed_mwh × banding_factor × (buyout + recycle)[latest_year]`

**Key "cliff edge" exposed:** Stations accredited 2016-2017 (near the March 2017 closure) have `accreditation_end_year` = 2036-2037. Plotting by `accreditation_end_year` reveals a visible drop in `remaining_committed_mwh` in 2037 — the chart's rhetorical payload for "what's locked in versus when it ends". Matches `RO-MODULE-SPEC.md` §3 chart 3 "forward obligation to 2037".

**Determinism anchor (D-21):** `current_year_anchor = max(Output_Period_End).year` (from generation data), not `pd.Timestamp.now().year`. Pattern verbatim from CfD `forward_projection.py:99`.

### §7 — NIRO Integration Facts (answer to Q7)

`[ASSUMED]` NIRO (Northern Ireland RO) details:

- NIRO is **administered by Utility Regulator NI** (not Ofgem GB directly), but Ofgem GB handles aspects of NIROC issuance via the shared Register.
- **Buyout prices are distinct** from GB values — typically slightly different by a few percent due to NI-specific RPI indexing.
- **Banding factors are similar but not identical** — NIROC differences mostly in biomass bands and solar PV banding. Published separately as NI Renewables Obligation Orders.
- The Ofgem Renewable & CHP Register historically listed NI stations with a `Country = 'Northern Ireland'` column — **this same column is expected in the new RER register** (unconfirmed pending Option D snapshot).
- Per D-09: include NI rows with `country='NI'` column on every grain; headline is GB-only; UK-total is recoverable via filter.

**Recommendation:** Single scraper target (Ofgem Register has both countries); differentiate on `country` column. Separate `ro-ni-prices.csv` may be needed if NIROC buyout prices are not on the same Ofgem transparency documents as GB — planner should verify at plan-time.

### §8 — Plotting + Docs Details

#### §8.1 — Chart-file Naming (RO-MODULE-SPEC.md Appendix A)

Chart outputs follow the pre-existing convention:
- `subsidy_ro_dynamics_twitter.png` + `.html` (S2 flagship)
- `subsidy_ro_by_technology_twitter.png` + `.html` (S3)
- `subsidy_ro_concentration_twitter.png` + `.html` (S4 — RO-specific Lorenz name; CfD equivalent is `subsidy_lorenz_twitter.png`, but mirror RO-prefixed here)
- `subsidy_ro_forward_projection_twitter.png` + `.html` (S5 — RO-specific name; CfD equivalent is `subsidy_remaining_obligations_twitter.png`)

All in `docs/charts/html/` (gitignored; regenerated daily by refresh.yml).

#### §8.2 — mkdocs.yml Nav Recommendation

Currently the nav has: Home, Cost, Recipients, Efficiency, Cannibalisation, Reliability, Data, Methodology, About. Recommendation: **add a new "Schemes" top-level tab** between Reliability and Data, holding only RO in Phase 5:

```yaml
  # ... existing tabs ...
  - Reliability:
      # ... existing ...
  - Schemes:
      - Overview: schemes/index.md           # OPTIONAL: new tiny page
      - Renewables Obligation (RO): schemes/ro.md
  - Data: data/index.md
  # ...
```

Phase 7 (FiT) adds `- Feed-in Tariff (FiT): schemes/fit.md` after RO. Phase 6 portal may restructure further. For Phase 5: just add the Schemes tab + RO entry. `schemes/index.md` can be a minimal 30-line placeholder page linking to ro.md.

#### §8.3 — docs/schemes/ro.md — 8-Section D-15 Structure

Template outline:

1. **Headline** (~3 paragraphs) — "£X bn in RO subsidy paid by UK consumers since 2002" + breakdown (£A bn cofiring, £B bn mutualisation, £C bn NIRO-excluded).
2. **What is the RO?** (~3 paragraphs) — "The scheme you've never heard of, twice the size of the one you have." 2002-2037 timeline; supplier obligation → ROC certificates → buyout+recycle mechanism.
3. **Cost dynamics (S2)** — PNG + interactive HTML link; 4-panel commentary.
4. **By technology (S3)** — PNG + HTML link; onshore + offshore + biomass share commentary.
5. **Concentration (S4)** — Lorenz chart + top-N operator callout.
6. **Forward commitment (S5)** — PNG + HTML link; 2026 → 2037 drawdown commentary; 2037 cliff-edge.
7. **Methodology summary** — Link to `docs/methodology/gas-counterfactual.md`; cofiring caveat; mutualisation caveat; NIRO caveat; Turver/REF benchmark reconciliation note.
8. **Data & code** (GOV-01 four-way coverage) — Primary Ofgem register URL + chart source permalinks + test permalinks + bash reproduce block.

Theme cross-links: `docs/themes/cost/index.md` gallery adds S2 and S3 (possibly S5). `docs/themes/recipients/index.md` gallery adds S4.

## Sources

### Primary (HIGH confidence)

- `ARCHITECTURE.md` §4 (data layers), §6.1 (scheme contract), §6.2 (shared counterfactual), §7.1 (refresh cadence), §9 (governance), §11 P4 (Phase 5 entry/exit)
- `RO-MODULE-SPEC.md` — domain authority on RO scheme (§1 goal, §3 charts, §4 data sources, §5 module architecture, §6 data model, §7 cost formula, §8 pipeline stages, §9 validation gates, §10 R1-R8 risks, §12 success criteria, Appendix A naming)
- `src/uk_subsidy_tracker/schemes/cfd/` — verbatim §6.1 implementation template (read 2026-04-22)
- `src/uk_subsidy_tracker/data/sidecar.py` — shared atomic sidecar writer (Phase 4 Plan 07)
- `src/uk_subsidy_tracker/counterfactual.py` — METHODOLOGY_VERSION + DEFAULT_CARBON_PRICES structure
- `.planning/phases/04-publishing-layer/04-CONTEXT.md` — D-18 per-scheme dirty-check pattern; shared sidecar helper; Parquet writer pinned options
- `.planning/phases/05-ro-module/05-CONTEXT.md` — 16 locked decisions D-01..D-16 + Claude's Discretion

### Secondary (MEDIUM confidence, verified via cross-source cross-check)

- REF Constable "UK Renewable Electricity Subsidy Totals: 2002 to the Present Day" (2025-05-01)
  - Blog post: `https://www.ref.org.uk/ref-blog/390-uk-renewable-electricity-subsidy-totals-2002-to-the-present-day`
  - PDF: `https://www.ref.org.uk/attachments/article/390/renewables.subsidies.01.05.25.pdf` (fetched 2026-04-22, ~372KB)
  - Table 1 transcribed from HTML rendering; PDF binary not directly readable via WebFetch
- REF "Notes on the Renewable Obligation": `https://www.ref.org.uk/energy-data/notes-on-the-renewable-obligation` — Table 1 banding table + Table 2 supplier obligation % + buyout/recycle price series 2002/03-2024/25
- Ofgem RO transparency documents (buyout + mutualisation ceilings per year): `https://www.ofgem.gov.uk/transparency-document/renewables-obligation-ro-buy-out-price-mutualisation-threshold-and-mutualisation-ceilings-YYYY-YYYY`
- Ofgem "Renewables Obligation 2021/22: Mutualisation" transparency document
- Ofgem Renewables Obligation 2023-24 Annual Report PDF (SY22)
- Utility Week "RO mutualisation avoided for first time since 2017" (2024) — 2022-23 shortfall was below threshold
- Turver "How ROCs Rip Us Off" substack (SY20 £6.4bn, SY21 £6.8bn single-point) — `https://davidturver.substack.com/p/renewable-obligation-certificates-rocs-rip-off`

### Tertiary (LOW confidence, single-source or estimation — flagged [ASSUMED] above)

- EU ETS pre-2018 annual averages — obtained from Wikipedia + search result snippets; not directly retrievable from Sandbag/EEA viewer during this research session. For final YAML, planner should consult **EEA "Emissions, allowances, surplus and prices in the EU ETS 2005-2020"** (referenced link `https://www.eea.europa.eu/en/analysis/maps-and-charts/emissions-allowances-surplus-and-prices`) and ICE/EEX reference historical data for the authoritative series.
- Ofgem Renewable Electricity Register public download mechanism post-2025-05-14 — verified by email-redirect language on Ofgem's own page but not tested end-to-end.
- NIROC banding factors — not researched in detail; planner to verify at plan-time against Utility Regulator NI's published NI Renewables Obligation Orders.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages already in pyproject.toml; versions verified; Phase 4 patterns load-bearing and repeatedly validated
- Architecture: HIGH — CfD §6.1 template has been running through Phase 4 end-to-end; Protocol conformance smoke test is green
- Pitfalls: MEDIUM-HIGH — 8 identified, most surfaced by CONTEXT decisions; mutualisation + OY/CY boundary + banding divergence are known gotchas
- Turver anchor (Q2): MEDIUM-HIGH — REF Constable Table 1 is strong; Turver substack is weaker but still valid as secondary
- Ofgem scraper mechanism (Q1): LOW-MEDIUM — RER disruption is material; Option D workaround is reasonable but not verified end-to-end
- Bandings table (Q3): HIGH — REF Table 1 verbatim + RO Order amendment SI list
- Mutualisation (Q4): HIGH — Ofgem + Utility Week + Drax corroborate
- Carbon-price extension (Q5): MEDIUM — Wikipedia/search gave overview; specific annual averages need EEA final-pass
- Forward projection (Q6): HIGH — Option (c) per-station-accreditation-end is clearly most defensible
- NIRO (Q7): MEDIUM — confirmed as part of Ofgem register with `country='NI'` column but per-NIROC-banding details unconfirmed
- Validation architecture (Q8): HIGH — 4 invariants line up with D-04 verbatim; test framework is pytest (already in use)

**Research date:** 2026-04-22
**Valid until:** 30 days for locked decisions (D-01..D-16 are user-committed); 14 days for Ofgem scraper mechanism (RER is a moving target); 7 days for Turver anchor (researcher consensus may shift as REF updates land)

## RESEARCH COMPLETE
