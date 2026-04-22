# Architecture

**Project:** UK Renewable Subsidy Tracker
**Status:** Draft v1 (supersedes ad-hoc decisions; pairs with `RO-MODULE-SPEC.md`)
**Owner:** Richard Lyon
**Last updated:** 2026-04-21

This document is the single source of truth for how the project is built, what
it does and does not do, and why. It captures the design decisions made
during the CfD module's first production release and the scope expansion to a
comprehensive portal covering all UK renewable subsidy schemes.

---

## 1. Mission, audience, non-goals

### 1.1 Mission

Build an independent, open, data-driven audit of UK renewable electricity
subsidy costs — every scheme, every pound, every counterfactual, every
methodology exposed — as a permanent national resource.

Every headline number on the site must be:

- reproducible from a single `git clone` + `uv sync` + one command;
- backed by a methodology page explaining the computation step by step;
- traceable to a primary data source published by a UK regulator or agency;
- versioned, citable, and adversarial-proof.

The rhetorical case the site supports: **the costs are large, the
counterfactual is unfavourable, the lock-in is decades, and the scheme design
produces structural failures (cannibalisation, intermittency) that make more
build-out worse, not better.** The portal does not make this argument — the
charts do. The portal's job is to publish the data honestly and let it speak.

### 1.2 Audiences

Four primary audiences, in order of volume:

1. **Journalists.** Want headline numbers, clean PNG charts for embedding, a
   quote-ready sentence, and a stable URL to cite. Do not want to download
   data; want to trust that the number is right.
2. **Advocates / skeptic community.** Want shareable images, Twitter-ready
   chart exports, a one-line rebuttal to renewables-lobby talking points.
   Share liberally; pass the URL around.
3. **Academics.** Want the underlying Parquet/CSV data, the methodology
   documented in detail, a citation target (DOI eventually), versioned
   snapshots so their papers can reference a specific dataset version.
4. **Policymakers / civil servants.** Want the methodology to be bulletproof
   so they can use the numbers without embarrassment. Want to know the
   assumptions and sensitivity bounds.

A fifth audience — the adversarial one — matters disproportionately:

5. **Opposing analysts (RenewableUK, Carbon Brief, academic defenders of the
   current regime).** Will attempt to discredit. The site must be
   methodologically bulletproof, because the argument's credibility depends
   on survival under hostile reading. This drives every governance decision
   in §11.

### 1.3 Non-goals

The project will not:

- **Advocate for specific policies.** Presents data; lets readers draw
  conclusions. The skeptic framing lives in essays and social media posts,
  not in the portal itself.
- **Forecast subsidy costs.** Projects forward-committed obligations from
  signed contracts only; does not model AR7+ auction outcomes, gas price
  scenarios, or NESO-style demand futures beyond citing them.
- **Be a live, real-time dashboard.** Data refreshes daily at most. Subsidy
  data is slow-moving; a live feed would be theatre.
- **Provide paid tiers, user accounts, or logged-in features.** National
  resource = free, open, anonymous.
- **Expose an API beyond stable file URLs.** Parquet and CSV files at
  predictable URLs are a better API than a REST service for analytical
  workloads.
- **Handle heat (RHI, biomethane) or transport subsidies.** Electricity
  only. A sibling project can cover heat.
- **Compete with Ofgem, DESNZ, or the Low Carbon Contracts Company on
  primary data publication.** The project consumes their data; it does not
  replicate their role.

---

## 2. Architectural principles

In order of precedence. When principles conflict, the higher-numbered one
wins.

1. **Maintainability over novelty.** A retiree-sustainable project. Every
   tool chosen must be mainstream, widely taught, and likely to exist in
   five years. Rust, Kubernetes, microservices, new frameworks — explicitly
   rejected.
2. **Static over dynamic.** Publishing operation, not a web app. Read:write
   ratio is ~1,000,000:1; static files on a CDN absorb any reasonable
   viral load.
3. **Columnar over relational.** This is OLAP data, not OLTP. Parquet +
   DuckDB is 10–100× faster than Postgres for the actual queries run.
4. **Provenance over freshness.** Every number traces to a source with
   timestamp and hash. Daily refresh is a convenience; source attribution
   is essential.
5. **Adversarial-proof over elegant.** A slightly uglier chart with a
   bulletproof methodology beats a beautiful chart that can be picked
   apart. Every chart has a methodology page. Every headline number has a
   test.
6. **Cut over defer.** Exploratory charts that don't land are deleted from
   the production path, not deferred indefinitely. Git history preserves
   them.
7. **Replication over invention.** New schemes follow the CfD template.
   No new chart patterns until the existing eight schemes are built.
8. **Composability over integration.** Each scheme is a self-contained
   module. Cross-scheme charts read the scheme-level Parquet outputs;
   they do not reach inside scheme modules.

---

## 3. Technology stack

Finalised. No further choices required.

| Layer | Tool | Why |
|---|---|---|
| Language | **Python 3.12+** | Already in use; mainstream; scientific ecosystem; maintainable long-term. |
| Package manager | **uv** | Fast, lockfile-first, unambiguous. |
| Analytical engine | **DuckDB** (embedded) | Fastest OLAP engine at this data scale; reads Parquet natively; same API in Python/CLI/browser-WASM; zero ops. |
| Secondary DataFrame API | **pandas** | Kept for light manipulation. DuckDB for heavy analytical queries. No Polars migration planned. |
| Data storage | **Parquet** | Columnar, compressed ~10× vs CSV, schema-embedded, cross-language, cloud-native. |
| Source storage | **CSV / XLSX** (raw as published) | Preserves provenance. Committed to git where ≤100 MB/file. |
| Charting | **Plotly (6.x)** | Python-native; exports Twitter-PNG + interactive HTML; already in production. |
| Documentation | **MkDocs** with **Material theme** | Python-native; ~10-year stable; used by FastAPI/Pydantic/Kubernetes; zero JS build pipeline. |
| Testing | **pytest** | Standard; simple; runs anywhere. |
| CI / scheduling | **GitHub Actions** | Free tier covers daily refresh with headroom; scheduled cron built-in. |
| Hosting | **Cloudflare Pages** | Free tier; free custom domain; CDN-backed; auto-purge on deploy; survives viral traffic. |
| Domain / DNS | Cloudflare (if not already) | Aligns with Pages. |
| Version control | **git** + **GitHub** | Standard. |

### Explicitly rejected

| Rejected | Why |
|---|---|
| Rust | Maintainability cost > performance benefit at this scale. |
| Polars (migration) | Pandas is sufficient; DuckDB covers performance needs. |
| MySQL / Postgres | Wrong shape for analytical workload; adds ops burden. |
| MongoDB / document stores | Data is tabular and schema-stable. |
| Redis / caching layer | CDN edge caching handles this; no need for a second layer. |
| Docker / Kubernetes | Single-process application; containerisation is overhead. |
| Airflow / Prefect / Dagster | Pipeline runs daily; a cron + Python script is correct-sized. |
| Quarto / Observable Framework / Astro | MkDocs Material is already working; migration cost > benefit. |
| Leptos / Dioxus / any WASM frontend | Fails maintainability principle; fails "static over dynamic". |
| Tableau / Metabase / PowerBI | Vendor lock-in, subscription cost, charts already in Plotly. |

---

## 4. Data architecture

Three layers. Each has a single, clear purpose. The layers are
unidirectional — source → derived → published.

### 4.1 Source layer (`data/raw/`)

Preserves primary data exactly as published. CSV and XLSX files from
regulators. No transformation. No cleaning. Read-only except when the
relevant scraper refreshes.

```
data/raw/
├── lccc/
│   ├── actual-cfd-generation.csv           # LCCC daily settlement
│   └── cfd-contract-portfolio-status.csv   # LCCC portfolio snapshot
├── ons/
│   └── gas-sap.xlsx                        # ONS System Average Price of gas
├── elexon/
│   ├── agws.csv                            # Actual Generation Wind/Solar
│   └── system-prices.csv                   # Balancing system prices
├── ofgem/
│   ├── ro-register.csv                     # RO accredited stations
│   ├── ro-generation.csv                   # RO ROCs issued monthly
│   ├── roc-prices.csv                      # Buyout + recycle annual
│   ├── fit-register.csv                    # FiT accredited installations
│   └── fit-generation.csv                  # FiT quarterly generation
├── neso/
│   ├── balancing-mechanism.csv             # Half-hourly BM data
│   └── balancing-costs.csv                 # Monthly balancing services
├── emr/
│   └── capacity-market-auctions.csv        # EMR Delivery Body data
├── gov-uk/
│   └── uk-ets-carbon.csv                   # UK ETS auction prices
└── e-roc/
    └── auction-clearing-prices.csv         # Secondary ROC market
```

**Rules for the source layer:**

- Files match the upstream publisher's schema exactly.
- Filename encodes the source; path encodes the publisher.
- Each source scraper writes a sidecar `<filename>.meta.json` with retrieval
  timestamp, upstream URL, SHA-256 of the file, HTTP status, and (where
  available) the publisher's own "last modified" timestamp.
- Files are committed to git where ≤100 MB. Above that threshold, pushed to
  Cloudflare R2 with a manifest in the repo pointing to the R2 object.
- Never edited by hand. Corrections go upstream.

### 4.2 Derived layer (`data/derived/`)

Analytical tables produced by scheme modules. Parquet only. Columnar,
compressed, schema-embedded.

```
data/derived/
├── cfd/
│   ├── station_month.parquet              # grain: station × month
│   ├── annual_summary.parquet             # grain: year
│   ├── by_technology.parquet              # grain: year × technology
│   ├── by_allocation_round.parquet        # grain: year × round
│   └── forward_projection.parquet         # grain: station × future-year
├── ro/
│   └── (same grains)
├── fit/
│   └── (same grains)
├── constraints/
│   └── (same grains)
├── capacity_market/
│   └── (same grains)
├── balancing/
│   └── (delta-only rollups)
├── grid/
│   └── (attribution estimates with bounds)
└── combined/
    ├── all_schemes_annual.parquet         # cross-scheme rollup
    ├── all_schemes_vs_gas.parquet
    └── total_per_household.parquet
```

**Rules for the derived layer:**

- One table per grain. No wide tables serving multiple charts.
- Each table's schema is documented in a Pydantic model in `src/.../schemas/`.
- Tables are deterministic functions of the source layer. Re-running the
  pipeline on unchanged sources produces byte-identical Parquet files
  (modulo Parquet metadata timestamps).
- Columns that join across schemes (date, technology, country) use the
  same name and dtype everywhere. Enforced by schema tests.
- Cross-scheme tables (`combined/`) are built from per-scheme Parquet
  outputs. They do not re-read raw data.

### 4.3 Publishing layer (`site/data/`)

What the portal serves. Public URLs. Versioned. Journalist/academic-facing.

```
site/data/
├── manifest.json                          # machine-readable index
├── latest/
│   ├── cfd/station_month.parquet
│   ├── cfd/station_month.csv              # CSV mirror for journalists
│   ├── cfd/station_month.schema.json      # column types + descriptions
│   ├── ro/...
│   ├── ...
│   └── combined/all_schemes_annual.parquet
└── v2026-04-21/                           # pinned snapshot
    └── (same structure as latest/)
```

`manifest.json` shape:

```json
{
  "version": "2026-04-21",
  "generated_at": "2026-04-21T06:12:00Z",
  "methodology_version": "1.3",
  "datasets": [
    {
      "id": "cfd.station_month",
      "title": "CfD payments, station × month, 2016-present",
      "grain": "station × month",
      "row_count": 29847,
      "schema_url": "/data/latest/cfd/station_month.schema.json",
      "parquet_url": "/data/latest/cfd/station_month.parquet",
      "csv_url": "/data/latest/cfd/station_month.csv",
      "versioned_url": "/data/v2026-04-21/cfd/station_month.parquet",
      "sha256": "...",
      "sources": [
        {
          "name": "LCCC Actual CfD Generation",
          "upstream_url": "https://dp.lowcarboncontracts.uk/...",
          "retrieved_at": "2026-04-21T05:58:00Z",
          "source_sha256": "..."
        }
      ],
      "methodology_page": "/charts/cfd/methodology/"
    }
  ]
}
```

**Rules for the publishing layer:**

- Every table is published as both Parquet (canonical) and CSV (journalist
  convenience).
- `latest/` is overwritten on each refresh.
- Versioned snapshots (`v2026-04-21/`) are written on tagged releases, never
  overwritten.
- `manifest.json` is the contract. External consumers (academic citations,
  journalist scripts, third-party dashboards) should read the manifest and
  follow the URLs. URLs in the manifest are stable.

---

## 5. The chart catalogue

**This section is the content spine of the project.** Everything the
pipeline produces flows from here. If a chart is not listed here, the
pipeline does not build it.

Charts are grouped by **theme** (argumentative family), not by scheme. Each
theme is a page. Within a theme, charts are labelled PRODUCTION,
DOCUMENTED, DEFER, or CUT.

### 5.1 Theme definitions

Five themes form the portal's argumentative structure:

| Theme | Slug | The argument |
|---|---|---|
| **A. Cost mechanics** | `cost` | *Here's what the scheme cost, here's what gas would have cost, here's what's locked in.* Per-scheme cost dynamics, gas counterfactual, forward obligations. |
| **B. Where the money goes** | `recipients` | *Most of this spending goes to a handful of offshore wind farms and Drax.* Breakdowns by technology, by allocation round, by project. Concentration analysis. |
| **C. Value for money** | `efficiency` | *Even if you accept the climate premise, this is not a cost-effective way to decarbonise.* £/tCO₂ avoided, subsidy-per-avoided-tonne time series, bang-for-buck scatter. |
| **D. Cannibalisation** | `cannibalisation` | *The more we build, the worse the economics get. The scheme is self-defeating.* Capture ratio, wind-price correlation. |
| **E. Reliability** | `reliability` | *What we're paying for doesn't deliver what's claimed.* Capacity factor, intermittency, drought analysis. |

Plus a sixth layer, the portal integration:

| **X. Cross-scheme portal** | `index` | *Total cost across all UK renewable subsidy schemes, on one canvas.* Top-strip headlines + stacked totals + scheme grid. |

### 5.2 Existing chart triage

Outcome of the 2026-04 review. Every file under `src/cfd_payment/plotting/`
has a verdict.

| File | Theme | Verdict | Action |
|---|---|---|---|
| `subsidy/cfd_dynamics.py` | A (CfD) | **PRODUCTION** | Documented. Keep. |
| `subsidy/cfd_vs_gas_cost.py` | A (CfD) | **PRODUCTION** | Documented. Keep. |
| `subsidy/remaining_obligations.py` | A (CfD) | **PRODUCTION** | Documented. Keep. |
| `subsidy/cfd_payments_by_category.py` | B | **PROMOTE → PRODUCTION** | Write docs page. |
| `subsidy/lorenz.py` | B | **PROMOTE → PRODUCTION** | Write docs page. "6 projects = 50%" headline. |
| `subsidy/bang_for_buck.py` | C | **DOCUMENTED** | Keep, secondary on theme C page. |
| `subsidy/subsidy_per_avoided_co2_tonne.py` | C | **PROMOTE → PRODUCTION** | Write docs page. Flagship on theme C. |
| `subsidy/scissors.py` | — | **CUT** | Strictly dominated by `cfd_dynamics`. Preserved in git history. |
| `subsidy/bang_for_buck_old.py` | — | **DELETE** | Obsolete version. |
| `cannibalisation/capture_ratio.py` | D | **PROMOTE → PRODUCTION** | Write docs page. Flagship on theme D. |
| `cannibalisation/price_vs_wind.py` | D | **DOCUMENTED** | Keep, secondary on theme D page. |
| `capacity_factor/monthly.py` | E | **DOCUMENTED** | Keep, secondary. |
| `capacity_factor/seasonal.py` | E | **PROMOTE → PRODUCTION** | Write docs page. DESNZ-assumption challenge. |
| `intermittency/generation_heatmap.py` | E | **PROMOTE → PRODUCTION** | Write docs page. Visual hook. |
| `intermittency/load_duration.py` | E | **DOCUMENTED** | Keep, secondary. Academics will want it. |
| `intermittency/rolling_minimum.py` | E | **PROMOTE → PRODUCTION** | Write docs page. Drought/"longer than any battery" argument. |

**Post-triage counts:** 9 PRODUCTION, 4 DOCUMENTED, 1 CUT, 1 DELETE. From
15 working files to 13 kept, all with defined roles.

### 5.3 Minimum diagnostic set per scheme

Each subsidy scheme has a standard five-slot diagnostic set. The pattern
was established by CfD and replicates across schemes.

| Slot | Purpose | CfD reference |
|---|---|---|
| **S1** — Headline card | Scheme size, premium over gas, end year | (portal top strip) |
| **S2** — Dynamics (4-panel) | Volume × price gap × premium × cumulative | `cfd_dynamics.py` |
| **S3** — Cost breakdown by technology | Where the money goes within the scheme | `cfd_payments_by_category.py` |
| **S4** — Concentration | Lorenz / top-N recipients | `lorenz.py` |
| **S5** — Forward commitment | What's locked in from today | `remaining_obligations.py` |

Applied across all planned schemes:

| Scheme | S1 card | S2 dynamics | S3 by-tech | S4 concentration | S5 forward | Notes |
|---|:-:|:-:|:-:|:-:|:-:|---|
| CfD | ✓ | ✓ | ✓ | ✓ | ✓ | Reference implementation. Done. |
| RO | **new** | **new** | **new** | **new** | **new** | Per `RO-MODULE-SPEC.md`. |
| FiT | **new** | **new** | **new** | n/a | **new** | Concentration trivial (800k domestic installs). |
| SEG | **new** | n/a | n/a | n/a | n/a | Aggregate only (no station-level data). |
| Constraint payments | **new** | **new** | **new** (by wind farm) | **new** (top-N paid to switch off) | trend projection | |
| Capacity Market | **new** | modified | **new** | **new** | **new** (to 2040) | No gas counterfactual. |
| Balancing services | **new** | **new** (delta view) | — | — | — | Pre/post-renewables delta. |
| Grid socialisation | **new** | n/a | — | — | — | Aggregate with bounds. |

**Per-scheme target: ~20 new charts across seven schemes, following the CfD
template.** Most are direct ports of the CfD code with data source swapped.

### 5.4 Cross-scheme / portal integration charts

New. The payoff for having all schemes in one place.

| ID | Chart | Theme | Audience | Priority |
|---|---|---|---|---|
| **X1** | Total UK subsidy, stacked by scheme, annual | Portal | Everyone | P1 flagship |
| **X2** | Combined premium over gas, cumulative | Portal | Everyone | P1 flagship |
| **X3** | Cost per household, decomposed by scheme | Portal | Public/journalists | P1 flagship |
| **X4** | Cost per MWh of subsidised generation, by scheme | A | Academics | P2 |
| **X5** | 2022 crisis comparison across schemes | A | Rhetorical | P2 |

### 5.5 Theme page structure

Each theme page has a consistent layout:

```
docs/themes/<theme>/
├── index.md                   # theme narrative + embedded flagship charts
├── methodology.md             # how every number on the theme page was computed
└── <chart>.md                 # optional per-chart deep-dive for PRODUCTION charts
```

Per-chart documentation pages exist for every PRODUCTION chart. DOCUMENTED
charts are embedded in the theme index page without their own dedicated
page.

### 5.6 Portal top strip (iamkate pattern)

The portal homepage (`docs/index.md`) follows the [iamkate.com/grid](https://grid.iamkate.com/)
design pattern, adapted to slow-moving subsidy data.

Layout:

```
┌─────────────────────────────────────────────────────────────────┐
│ UK Renewable Subsidy Tracker     [data] [methodology] [about]   │
├─────────────────────────────────────────────────────────────────┤
│ Three headline cards:                                           │
│   [£25.8bn] Total subsidy (this year)                           │
│   [£14.0bn] Premium over gas (this year)                        │
│   [£285]    Per household (this year)                           │
├─────────────────────────────────────────────────────────────────┤
│ X1 — Total subsidy, stacked by scheme                           │
│ [Latest year] [Last 5 years] [All time]   ← time-horizon tabs   │
├─────────────────────────────────────────────────────────────────┤
│ Scheme grid (2 × 4):                                            │
│   CfD £2.5bn    RO £7bn      FiT £1.7bn     CM £1.5bn           │
│   Constr £2.5bn Balanc £2.5bn Grid £1–2bn   SEG £0.05bn         │
├─────────────────────────────────────────────────────────────────┤
│ Themes:  Cost • Recipients • Efficiency                         │
│          Cannibalisation • Reliability • Methodology            │
└─────────────────────────────────────────────────────────────────┘
```

**Design decisions translated from iamkate:**

- Three big numbers, not one, not six. Three is the limit of human
  glance-comprehension.
- One flagship chart with time-horizon tabs, not a wall of charts.
- Scheme grid equivalent to iamkate's "source mix" tiles. Each tile links
  to the scheme detail page.
- Theme navigation bottom-row, not a traditional hamburger.

**What does not translate:**

- iamkate's "past hour / past day" tabs. Subsidy data is slow-moving.
  Relevant tabs are **Latest year / Last 5 years / All time.** Optionally
  add "Latest quarter" when data plumbing supports it.
- Dark/light toggle. MkDocs Material handles this natively.

---

## 6. Module layout

Mirrors the theme and scheme structure. Each scheme is self-contained and
isolated from the others, consuming only shared utilities.

```
uk-subsidy-tracker/                          # renamed from cfd-payment
├── README.md
├── ARCHITECTURE.md                          # this file
├── RO-MODULE-SPEC.md                        # per-scheme spec, template for others
├── CHANGES.md                               # release-by-release diff log
├── CITATION.cff                             # academic citation metadata
├── pyproject.toml
├── uv.lock
├── .github/
│   └── workflows/
│       ├── refresh.yml                      # daily cron: scrape + rebuild + publish
│       └── deploy.yml                       # on tag: publish versioned snapshot
├── data/
│   ├── raw/                                 # §4.1 source layer
│   └── derived/                             # §4.2 derived layer (Parquet)
├── src/
│   └── uk_subsidy_tracker/
│       ├── __init__.py
│       ├── counterfactual.py                # shared gas counterfactual
│       ├── schemas/                         # Pydantic models for every table
│       ├── data/                            # shared ingestion utilities
│       │   ├── scrapers/
│       │   │   ├── lccc.py
│       │   │   ├── ofgem_ro.py
│       │   │   ├── ofgem_fit.py
│       │   │   ├── ons_gas.py
│       │   │   ├── neso_bm.py
│       │   │   ├── emr_cm.py
│       │   │   └── e_roc.py
│       │   └── utils.py
│       ├── schemes/
│       │   ├── cfd/
│       │   │   ├── __init__.py
│       │   │   ├── cost_model.py            # station-month build
│       │   │   ├── aggregation.py           # rollups
│       │   │   └── forward_projection.py
│       │   ├── ro/
│       │   ├── fit/
│       │   ├── seg/
│       │   ├── constraints/
│       │   ├── capacity_market/
│       │   ├── balancing/
│       │   └── grid/
│       ├── plotting/
│       │   ├── theme.py                     # shared Plotly theme
│       │   ├── colors.py                    # shared palette
│       │   ├── chart_builder.py
│       │   ├── per_scheme/                  # S2-S5 charts, one subdir per scheme
│       │   │   ├── cfd/
│       │   │   ├── ro/
│       │   │   └── ...
│       │   ├── themes/                      # theme-page flagship charts
│       │   │   ├── cost/
│       │   │   ├── recipients/
│       │   │   ├── efficiency/
│       │   │   ├── cannibalisation/
│       │   │   └── reliability/
│       │   └── combined/                    # X1-X5 cross-scheme charts
│       ├── publish/
│       │   ├── manifest.py                  # builds site/data/manifest.json
│       │   ├── snapshot.py                  # versioned snapshot on release
│       │   └── csv_mirror.py                # writes CSV alongside Parquet
│       └── refresh_all.py                   # CI entry point
├── tests/
│   ├── test_counterfactual.py
│   ├── test_schemas.py
│   ├── test_aggregates.py
│   ├── test_benchmarks.py                   # totals vs REF/Turver/Ofgem
│   └── test_determinism.py                  # same input → byte-identical output
├── docs/                                    # MkDocs content
│   ├── index.md                             # portal homepage (§5.6)
│   ├── schemes/                             # one page per scheme
│   │   ├── cfd.md
│   │   ├── ro.md
│   │   └── ...
│   ├── themes/                              # one directory per theme (§5.5)
│   │   ├── cost/
│   │   ├── recipients/
│   │   ├── efficiency/
│   │   ├── cannibalisation/
│   │   └── reliability/
│   ├── data/                                # how to use our datasets
│   │   ├── index.md
│   │   ├── schema.md
│   │   └── citation.md
│   ├── about/
│   │   ├── methodology.md
│   │   ├── corrections.md
│   │   └── contributing.md
│   ├── changelog.md
│   └── charts/
│       └── html/                            # generated PNG + HTML assets
├── site/                                    # MkDocs build output (generated)
│   ├── (html from MkDocs)
│   └── data/                                # §4.3 publishing layer
├── mkdocs.yml
└── pyrightconfig.json
```

### 6.1 Scheme module contract

Every `schemes/<scheme>/` module exposes the same interface:

```python
# schemes/cfd/__init__.py

from pathlib import Path

DERIVED_DIR = Path("data/derived/cfd")

def upstream_changed() -> bool:
    """Return True if any source file has changed since last build."""

def refresh() -> None:
    """Re-scrape upstream sources. Idempotent. Writes to data/raw/."""

def rebuild_derived() -> None:
    """Rebuild all derived tables from raw sources. Writes Parquet to
    data/derived/cfd/."""

def regenerate_charts() -> None:
    """Regenerate all PRODUCTION charts for this scheme."""

def validate() -> list[str]:
    """Run scheme-level validation. Returns list of warnings; empty list
    means healthy."""
```

Consistency across schemes is enforced by a base class or protocol in
`schemes/__init__.py`.

### 6.2 Shared counterfactual

`src/uk_subsidy_tracker/counterfactual.py` is the single definition of the
gas counterfactual. Every scheme calls it. Test coverage must pin the
formula exactly:

```
counterfactual £/MWh =
    fuel cost (ONS gas SAP / 0.55 CCGT efficiency)
  + carbon cost (UK ETS £/tCO₂ × 0.184 tCO₂/MWh thermal / 0.55)
  + O&M £5/MWh (existing fleet, capex sunk)
```

Changes to this formula are a versioned methodology event (§11.4).

---

## 7. Refresh cadence and CI

### 7.1 Per-source cadence

| Source | Upstream update cadence | Our refresh |
|---|---|---|
| LCCC CfD settlements | daily (weekdays), T+3 to T+7 lag | **daily** |
| ONS gas SAP | weekly, ~5 day lag | **daily** (cheap; just re-fetch) |
| UK ETS carbon | daily secondary market | **daily** |
| Elexon AGWS + system prices | daily | **daily** |
| Ofgem RO register + generation | monthly, ~3 month lag | **monthly** |
| Ofgem FiT | quarterly | **monthly** (catches publication) |
| Ofgem ROC buyout | annual (Feb) | **monthly** (catches publication) |
| NESO Balancing Mechanism | daily | **daily** |
| NESO balancing costs monthly | monthly, ~6 week lag | **monthly** |
| EMR Capacity Market auctions | event-driven | **on-event** + weekly check |
| e-ROC auction | quarterly | **monthly** check |

### 7.2 Daily pipeline

Single `refresh.yml` workflow. Cron at 06:00 UTC (after LCCC's overnight
publication window).

```yaml
on:
  schedule: [{cron: '0 6 * * *'}]
  workflow_dispatch:

jobs:
  refresh:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run python -m uk_subsidy_tracker.refresh_all
      - run: uv run pytest tests/test_benchmarks.py
      - run: uv run mkdocs build --strict
      - uses: EndBug/add-and-commit@v9
        with:
          add: 'data/derived site docs/charts/html'
          message: 'Daily refresh ${{ github.run_id }}'
```

### 7.3 Dirty-check: rebuild only what changed

`refresh_all.py` compares upstream source hashes against their last-seen
values (stored in `data/raw/*/meta.json`). If a source hasn't changed, the
downstream scheme is not rebuilt.

```python
# refresh_all.py (sketch)
from uk_subsidy_tracker.schemes import cfd, ro, fit, constraints, capacity_market

schemes = [cfd, ro, fit, constraints, capacity_market]

any_changed = False
for scheme in schemes:
    if scheme.upstream_changed():
        scheme.refresh()
        scheme.rebuild_derived()
        scheme.regenerate_charts()
        any_changed = True

if any_changed:
    from uk_subsidy_tracker.plotting import combined
    combined.regenerate_all()               # only if any scheme changed
    from uk_subsidy_tracker.publish import manifest, csv_mirror
    manifest.build()
    csv_mirror.build()
```

This keeps the daily build under 5 minutes in typical cases and keeps git
history clean (no noisy Parquet reflow when nothing upstream changed).

### 7.4 Release tagging

On a meaningful change — new scheme lands, methodology revision, major
chart change — tag a release:

```bash
git tag -a v2026.04 -m "April 2026 release: RO module lands"
git push --tags
```

The `deploy.yml` workflow fires on tag push and publishes a versioned
snapshot to `site/data/v2026-04-XX/`. `latest/` is overwritten daily;
versioned snapshots are immutable.

---

## 8. Hosting and deployment

### 8.1 Primary host: Cloudflare Pages

- Free tier: unlimited bandwidth, unlimited requests, automatic HTTPS,
  custom domain.
- Deploys on every push to `main`.
- Cache purged automatically on deploy.
- CDN backed by Cloudflare's global edge. Survives any realistic viral
  load (HN front page, Daily Mail pickup, Substack feature) without
  configuration.

### 8.2 Object storage for oversized files

If any raw CSV exceeds ~100 MB, push to Cloudflare R2 (free egress to
Cloudflare Pages). The repo keeps a manifest pointer; the scraper downloads
from R2 instead of git.

Expected threshold breaches:

- NESO Balancing Mechanism half-hourly data (likely ~500 MB over ten years).
- FiT station-month data (possibly ~50 MB; probably fits in git).
- Everything else stays in git.

### 8.3 Domain

Proposed: `uksubsidytracker.org` or `renewablescost.uk` (whichever is
available and reads well). Pointed at Cloudflare Pages. Short URL helps
citation.

### 8.4 Backup and continuity

- All code and data (≤100 MB) in GitHub.
- R2-hosted files mirrored nightly to a second R2 bucket (cheap).
- Internet Archive auto-archives public URLs; sufficient for continuity.
- No separate backup infrastructure required.

---

## 9. National-resource governance

What makes this "a national resource" rather than "a skeptic's spreadsheet."
These are process, not infrastructure.

### 9.1 Provenance

Every Parquet file in `data/derived/` carries:

- a `sources` column or sidecar JSON listing the raw source files it was
  built from;
- the timestamp those sources were retrieved;
- the SHA-256 of each source;
- the pipeline version (git SHA) that built it.

Expressed in `manifest.json` for public consumption. Any downstream user
can audit a published number back to the primary data.

### 9.2 Citability

- **CITATION.cff** at repo root — machine-readable citation metadata.
- **Versioned snapshots** — every tagged release has an immutable URL.
  Academics cite `/data/v2026-04-21/cfd/station_month.parquet`, not
  `/data/latest/`.
- **DOI** (future) — register with Zenodo on a stable release cadence
  (annual?) so the dataset has a permanent identifier.
- **Stable URLs** — structure defined by `manifest.json`. Breaking changes
  are major-version events, not accidental.

### 9.3 Adversarial-proofing

Every PRODUCTION chart has:

1. **A narrative page** (`docs/themes/<theme>/<chart>.md`) — what the chart
   shows and why it matters, in plain English.
2. **A methodology page** (`docs/themes/<theme>/methodology.md` or
   `<chart>-method.md`) — every formula, every assumption, every filter,
   every source cited.
3. **A test** (`tests/test_benchmarks.py`) — totals reproduce known
   external benchmarks (REF aggregates, Turver's totals, Ofgem annual
   reports) within documented tolerance.
4. **A Python source file** — linked from both the chart page and the
   methodology page. A journalist or adversary can read the actual code
   that produced the number.

### 9.4 Methodology versioning

The gas counterfactual and any cross-cutting formula has a version number
in `src/uk_subsidy_tracker/counterfactual.py`. Methodology changes are:

- announced in `CHANGES.md` with the rationale;
- applied to the whole time series (no mixing of methodology versions
  within a chart);
- captured in `manifest.json` as the `methodology_version` field so
  external users can distinguish pre/post-change numbers.

### 9.5 Corrections

- Public `corrections.md` page listing every correction ever applied,
  with date, reason, and affected charts/numbers.
- GitHub Issues are the channel. Label `correction` triages to priority.
- Substantive corrections (change a headline number by >1%) trigger a
  release-note entry in `CHANGES.md` and a methodology-version bump if
  formula-related.

### 9.6 Testing

Small, boring, essential. ~300–500 lines total.

| Test class | Purpose | Runs |
|---|---|---|
| `test_counterfactual.py` | Pin the gas counterfactual formula against known inputs. | Every commit |
| `test_schemas.py` | Every Parquet file conforms to its Pydantic schema. | Every commit |
| `test_aggregates.py` | `sum by (year)` = `sum by (year × technology)`; no row leakage. | Every commit |
| `test_benchmarks.py` | Aggregates match REF/Turver/Ofgem within documented tolerance. | Every commit + daily |
| `test_determinism.py` | Identical input → byte-identical Parquet output. | Every commit |

A failing benchmark test in daily CI does not block the deploy (upstream
may have revised data); it raises an issue and flags the affected chart.

---

## 10. Scope boundaries (explicit non-commitments)

Things the project will not become, to make future scope creep decisions
trivial.

| Will not add | Replaced by | Reason |
|---|---|---|
| User accounts | — | National resource = anonymous, open. |
| Authentication | — | Nothing to authenticate. |
| Payment / paid tiers | Ko-fi / GitHub Sponsors | Not a business. |
| Real-time dashboard | Daily refresh | Source data is slow-moving. |
| Live chat / comments | GitHub Issues | Moderation burden; off-topic risk. |
| REST API | `manifest.json` + stable file URLs | Better shape for analytical workloads. |
| SQL query endpoint | Parquet + DuckDB-WASM (if demand) | No server to maintain. |
| Database (Postgres, MySQL) | Parquet files | OLAP workload, wrong shape. |
| Containers (Docker, K8s) | `uv run` | Single process. |
| Workflow engine (Airflow) | GitHub Actions cron | Right-sized. |
| Rust / Go / anything non-Python | Python | Maintainability principle. |
| Second frontend framework | MkDocs Material | Maintainability principle. |
| Heat subsidies (RHI) | Separate project (future) | Different regulator, different data. |
| Transport subsidies (EV plug-in grant etc.) | Separate project (future) | Different analytical frame. |
| Non-UK data | — | Scope is UK renewables. |

---

## 11. Phased delivery plan

Strict priority order. Each phase has an entry criterion, deliverables, and
an exit criterion. Do not advance until exit is met.

### P0 — Foundation tidy (½ day)

**Entry:** Now.
**Deliverables:**
- Rename repo `cfd-payment` → `uk-subsidy-tracker`.
- Switch MkDocs theme from `readthedocs` to `material`.
- Commit `ARCHITECTURE.md` (this file) and `RO-MODULE-SPEC.md`.
- Add `CHANGES.md`, `CITATION.cff`.

**Exit:** Repo renamed, theme switched, `mkdocs build --strict` passes.

### P1 — Test + benchmark scaffolding (1 day)

**Entry:** P0 complete.
**Deliverables:**
- `tests/test_counterfactual.py` pinning the formula.
- `tests/test_benchmarks.py` with CfD-only benchmarks against Ben Pile's
  2021 + 2026 numbers (documented divergence), REF subset, Turver aggregate.
- `tests/test_determinism.py` proving rebuilds are byte-identical.
- CI workflow runs pytest on every push.

**Exit:** Green CI on `main`; benchmark deltas explicitly documented.

### P2 — Chart triage execution (1 day)

**Entry:** P1 complete.
**Deliverables:**
- Delete `bang_for_buck_old.py` and `scissors.py`.
- Write docs pages for the seven PROMOTE charts (§5.2):
  `cfd_payments_by_category`, `lorenz`, `subsidy_per_avoided_co2_tonne`,
  `capture_ratio`, `capacity_factor/seasonal`,
  `intermittency/generation_heatmap`, `intermittency/rolling_minimum`.
- Restructure `docs/` into theme pages (§5.5).

**Exit:** `mkdocs build --strict` passes; every PRODUCTION chart has a
docs page; theme pages render.

### P3 — Publishing layer (1 day)

**Entry:** P2 complete.
**Deliverables:**
- `src/uk_subsidy_tracker/publish/manifest.py` — builds `manifest.json`.
- `publish/csv_mirror.py` — writes CSV alongside every Parquet.
- `publish/snapshot.py` — versioned snapshot on tag.
- `docs/data/index.md` — "how to use our data" page for
  journalists/academics.
- `site/data/manifest.json` present and valid after build.

**Exit:** External consumer can fetch `manifest.json`, follow a URL, and
retrieve a Parquet/CSV with provenance metadata.

### P4 — RO module (5–6 days)

**Entry:** P3 complete.
**Deliverables:** Per `RO-MODULE-SPEC.md`:
- Stage 1–5 pipeline.
- `schemes/ro/` module conforming to §6.1 contract.
- S2, S3, S4, S5 charts for RO.
- Docs pages mirroring the CfD set.
- Benchmarks: RO aggregate 2011–2022 within 3% of Turver.

**Exit:** RO scheme page live; benchmarks green; headline updated to
include RO.

### P5 — Flagship cross-scheme charts (2 days)

**Entry:** P4 complete. Two schemes (CfD + RO) now have production data.
**Deliverables:**
- X1 (stacked total by scheme, annual).
- X2 (combined premium over gas).
- X3 (cost per household).
- Portal top strip (§5.6).
- Scheme grid on homepage with CfD + RO tiles populated, others as
  placeholders.

**Exit:** Portal homepage renders with three headline numbers and X1 chart.

### P6 — FiT module (4–5 days)

**Entry:** P5 complete.
**Deliverables:**
- Ofgem FiT scraper.
- `schemes/fit/` conforming to §6.1 contract.
- S2, S3, S5 charts (S4 n/a).
- Docs pages + scheme grid tile.

**Exit:** FiT scheme page live; scheme grid has three populated tiles.

### P7 — Constraint payments module (4 days)

**Entry:** P6 complete.
**Deliverables:**
- NESO Balancing Mechanism scraper.
- `schemes/constraints/` module.
- All five slots.
- The "£X bn paid to switch off" headline.

**Exit:** Constraint page live; the growing-fastest line item is visible
in X1 stacked chart.

### P8 — Capacity Market module (3 days)

**Entry:** P7 complete.
**Deliverables:**
- EMR Delivery Body scraper.
- `schemes/capacity_market/` module.
- Modified S2 (no gas counterfactual), S3, S4, S5.
- Attribution caveat clearly documented.

**Exit:** CM page live; scheme grid has five populated tiles.

### P9 — Balancing services delta (3 days)

**Entry:** P8 complete.
**Deliverables:**
- NESO balancing costs scraper.
- `schemes/balancing/` module.
- Pre/post-renewables delta analysis.

**Exit:** Balancing page live; full renewable cost attributed within ±15%
of REF's £25.8bn headline.

### P10 — Grid socialisation (4 days)

**Entry:** P9 complete. Explicitly lower confidence than other modules.
**Deliverables:**
- Best-efforts TNUoS attribution with sensitivity bounds.
- Low/central/high estimates presented as a range, not a point.

**Exit:** Grid page live with caveats prominent; totals approach REF.

### P11 — SEG + REGOs completion (1 day)

**Entry:** P10 complete.
**Deliverables:** Aggregate-only scheme pages for the remaining two small
schemes. Completeness.

**Exit:** All eight scheme tiles populated.

### Post-P11 — steady state

Maintenance mode:
- Daily refresh CI (automatic).
- Monthly scheme audit: revisit benchmarks, check Ofgem publication cadence.
- Quarterly release tag: versioned snapshot for academics.
- Annual methodology review.
- Essay output: Substack + cross-post as material warrants.

**Total build effort: ~30 working days spread across 4–6 calendar months.**

---

## 12. Risks and open questions

### 12.1 Technical risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Ofgem RO banding table errors | Med | High | Cross-check `gen × banding` against Ofgem's own `ROCs_issued` per station. |
| Upstream schema changes | Med | Med | Pydantic validation on ingest; CI fails loudly; manual fix. |
| Constraint payments data volume | Low | Low | Push to R2 if exceeds 100 MB. |
| `mkdocs build --strict` breaks on scale | Low | Low | Works today with 3 pages; will work with 30. |
| DuckDB version incompatibility | Very low | Low | Pin major version in `pyproject.toml`. |

### 12.2 Data/methodology risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Pre-2013 carbon price ambiguity | High | Med | Publish "with carbon" headline + "without carbon" sensitivity. |
| Obligation year vs calendar year mix-up | High | Low | Plot everything in calendar years; document convention. |
| Capacity Market attribution disputed | Certain | Med | Flag as attribution choice; include + exclude views. |
| Grid socialisation attribution weak | Certain | Med | Range estimate; prominent caveat; lower confidence tier. |
| Adversarial attack on headline number | Certain | High | Methodology pages, test suite, reproducible code. |

### 12.3 Operational risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Solo maintainer unavailable | Certain at some point | High | No critical infra; repo + GitHub Pages fallback survive indefinitely. |
| GitHub Actions free tier exceeded | Low | Low | Daily build ~3 min; well within 2000 min/month. |
| Cloudflare Pages free tier exceeded | Very low | Low | Free tier is unlimited; would need actual abuse to trigger a limit. |
| Legal challenge (data licensing) | Low | High | All sources are government open data; provenance is documented. |

### 12.4 Open questions (for future decisions)

1. **Domain name.** `uksubsidytracker.org`? `renewablescost.uk`?
   Something else?
2. **Citation / DOI.** When does the dataset warrant Zenodo registration?
   After P5 (CfD + RO + portal) feels right.
3. **Substack cadence.** One essay per P-phase release? Or when data
   warrants? Probably the latter.
4. **Collaboration with Turver / REF / Ben Pile.** Pre-announce RO release
   to Turver; invite cross-link. But not a formal partnership.
5. **When to enable DuckDB-WASM client-side queries.** Defer until a
   concrete use case emerges (e.g. a journalist asking for custom
   filters). Not P1–P11.
6. **Internationalisation.** Stay UK-only; a sibling project for
   Ireland/Germany is out of scope.

---

## 13. Appendices

### 13.1 Naming conventions

**Files / paths:**
- Source raw data: `data/raw/<publisher>/<dataset>.<ext>`
- Derived Parquet: `data/derived/<scheme>/<grain>.parquet`
- Published: `site/data/latest/<scheme>/<grain>.{parquet,csv}`
- Python modules: `uk_subsidy_tracker.schemes.<scheme>.<role>`
- Chart files: `plotting/per_scheme/<scheme>/<chart_id>.py`
- Chart outputs: `docs/charts/html/<scheme>_<chart>_twitter.png` (plus
  `.html` for interactive version)
- Docs pages: `docs/themes/<theme>/<chart>.md`

**Chart IDs:** `<theme>_<scheme>_<slot>` (e.g. `cost_cfd_dynamics`,
`recipients_cfd_by_tech`). Stable for URLs.

**Database-free schema names:** singular, snake_case
(`station_month`, `annual_summary`, `forward_projection`).

### 13.2 URL conventions

Stable URLs the project commits to:

| Path | Content | Stability |
|---|---|---|
| `/` | Portal homepage | Stable forever |
| `/schemes/<scheme>/` | Scheme detail page | Stable per scheme |
| `/themes/<theme>/` | Theme narrative page | Stable per theme |
| `/themes/<theme>/<chart>/` | Per-chart deep-dive | Stable per chart |
| `/about/methodology/` | Top-level methodology | Stable |
| `/about/citation/` | How to cite | Stable |
| `/data/manifest.json` | Machine index | Stable contract |
| `/data/latest/<scheme>/<grain>.parquet` | Latest data | Content changes; URL stable |
| `/data/v<YYYY-MM-DD>/...` | Versioned snapshot | Immutable |

Breaking changes (renames, restructures) are major-version events
documented in `CHANGES.md` with 301 redirects maintained for at least 12
months.

### 13.3 Chart colour conventions

From existing `plotting/colors.py`. Do not change without an overall review.

- Offshore Wind: `#1f77b4`
- Onshore Wind: `#6baed6`
- Biomass (Drax/Lynemouth): `#d62728`
- Solar PV: `#ff7f0e`
- Investment Contracts: `#d62728`
- Allocation Round 1: `#1f77b4`
- Allocation Round 2: `#2ca02c`
- CfD strike / subsidised price: blue
- Gas counterfactual: orange
- Premium / cost highlight: red

### 13.4 Chart size conventions

- Twitter card: 1200 × 675 px (standard Plotly export)
- Interactive HTML: responsive; min-width 800px
- Mobile: charts stack to single column; long titles wrap

### 13.5 Citation template

```
Lyon, Richard (2026). UK Renewable Subsidy Tracker, v2026-04-21.
https://<domain>/data/v2026-04-21/
```

Machine-readable form in `CITATION.cff`.

### 13.6 Cross-references

- `RO-MODULE-SPEC.md` — per-scheme module specification template.
- `CHANGES.md` — release-by-release changelog.
- `CITATION.cff` — academic citation metadata.
- `docs/about/methodology.md` — top-level methodology.
- `docs/about/corrections.md` — correction log.
- `pyproject.toml` — package metadata and dependency pins.

---

## 14. Decision log

Key architectural decisions, dated, with rationale. Append-only.

| Date | Decision | Rationale |
|---|---|---|
| 2026-04-21 | Parquet + DuckDB, no relational database | OLAP workload; 1:1,000,000 read:write ratio; maintainability. |
| 2026-04-21 | MkDocs Material over Quarto/Observable/Astro | Avoid migration cost; Material is 10-year stable; drop-in from readthedocs theme. |
| 2026-04-21 | Python-only; Rust abandoned | Maintainability principle; retirement-adjacent project. |
| 2026-04-21 | Static files on Cloudflare Pages, no backend | Publishing operation, not web app; survives viral load free tier. |
| 2026-04-21 | Five-theme information architecture (Cost / Recipients / Efficiency / Cannibalisation / Reliability) | Chart portfolio clusters naturally into five argumentative families. |
| 2026-04-21 | iamkate.com/grid layout translated for subsidy data (3 headline numbers + flagship chart + scheme grid + themes) | Proven design pattern; scale appropriate to audiences; time tabs adapted for slow-moving data. |
| 2026-04-21 | Per-scheme 5-slot diagnostic set (S1–S5) | Consistency across eight schemes; CfD establishes the pattern. |
| 2026-04-21 | Scissors chart CUT | Strictly dominated by `cfd_dynamics`. |
| 2026-04-21 | Seven PROMOTE charts to PRODUCTION | Documented triage outcome. |
| 2026-04-21 | Repo rename to `uk-subsidy-tracker` | `cfd-payment` no longer accurate scope; rename before scheme expansion. |
| 2026-04-21 | Daily refresh cadence | LCCC/Elexon/ETS/NESO are daily; all others override to monthly under dirty-check. |
| 2026-04-21 | Adversarial-proofing as a first-class concern | Audience includes hostile analysts; methodology pages + tests + reproducible code are essential. |

---

**End of document.**
