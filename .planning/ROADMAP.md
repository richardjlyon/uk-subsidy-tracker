# Roadmap: UK Renewable Subsidy Tracker

**Milestone:** v1 — Eight-scheme portal
**Defined:** 2026-04-21
**Granularity:** Fine (12 phases matching ARCHITECTURE.md §11 P0–P11)
**Coverage:** 61/61 v1 requirements mapped

## Phases

- [x] **Phase 1: Foundation Tidy** — Repo rename, theme switch, root docs committed; brownfield import paths updated
- [x] **Phase 2: Test & Benchmark Scaffolding** — Four test classes, CI green on main; counterfactual formula pinned
- [ ] **Phase 3: Chart Triage Execution** — CUT files deleted, seven PROMOTE charts documented, five-theme docs structure built
- [x] **Phase 4: Publishing Layer** — manifest.json, CSV mirror, snapshot, data how-to; three-layer pipeline operational for CfD (completed 2026-04-23)
- [ ] **Phase 5: RO Module** — Full Renewables Obligation scheme module, S2–S5 charts, benchmarks within 3% of Turver
- [ ] **Phase 6: Flagship Cross-Scheme Charts** — X1/X2/X3 portal charts, portal homepage with scheme grid
- [ ] **Phase 7: FiT Module** — Feed-in Tariff scheme module, S2/S3/S5 charts, scheme grid tile
- [ ] **Phase 8: Constraint Payments Module** — NESO BM scraper, all five diagnostic slots, switch-off headline
- [ ] **Phase 9: Capacity Market Module** — EMR scraper, modified S2 (no gas counterfactual), S3/S4/S5, attribution caveat
- [ ] **Phase 10: Balancing Services Module** — NESO balancing costs scraper, pre/post-renewables delta analysis
- [ ] **Phase 11: Grid Socialisation Module** — Best-efforts TNUoS attribution with low/central/high sensitivity bounds
- [ ] **Phase 12: SEG + REGOs Completion** — Aggregate-only scheme pages, all eight scheme grid tiles populated

## Phase Details

### Phase 1: Foundation Tidy
**Goal**: The repository is correctly named, typed, and documented so all subsequent scheme work begins from a clean, publishable baseline
**Depends on**: Nothing (first phase)
**Requirements**: FND-01, FND-02, FND-03, GOV-05, GOV-06 (CITATION.cff portion)
**Success Criteria** (what must be TRUE):
  1. `uv run python -c 'import uk_subsidy_tracker'` succeeds — all existing imports updated to post-rename package path
  2. `uv run mkdocs build --strict` passes with the Material theme (readthedocs theme removed)
  3. `ARCHITECTURE.md`, `RO-MODULE-SPEC.md`, `CHANGES.md`, `CITATION.cff` are committed at repo root and visible in `git log`
  4. `docs/about/corrections.md` page exists and is reachable from site navigation
  5. `CITATION.cff` contains correct author, repository URL, and version metadata
**Plans:** 4 plans
Plans:
- [x] 01-01-PLAN.md — Package rename sweep: git mv src/cfd_payment → src/uk_subsidy_tracker, pyproject.toml, 24 Python files + 2 tests + demo_dark_theme.py imports
- [x] 01-02-PLAN.md — MkDocs Material theme + palette toggle + nav wiring, move docs/technical-details/gas-counterfactual.md → docs/methodology/, sweep docs/index.md + docs/charts/index.md
- [x] 01-03-PLAN.md — Commit ARCHITECTURE.md + RO-MODULE-SPEC.md, create CHANGES.md (Keep-a-Changelog) + CITATION.cff (CFF 1.2.0) + README.md + docs/about/{corrections,citation}.md; licence decision checkpoint
- [x] 01-04-PLAN.md — Create GitHub `correction` label, run mkdocs build --strict, phase-exit verification checkpoint
**UI hint**: yes

### Phase 2: Test & Benchmark Scaffolding
**Goal**: The test suite is complete and CI is green, with the gas counterfactual formula pinned and all external benchmark deltas documented
**Depends on**: Phase 1
**Requirements**: TEST-01, TEST-04, TEST-06, GOV-04
**Success Criteria** (what must be TRUE):
  1. `uv run pytest` passes green on `main` — four test classes present and passing: `test_counterfactual.py`, `test_schemas.py`, `test_aggregates.py`, `test_benchmarks.py`
  2. `tests/test_counterfactual.py` fails if the gas formula (fuel + carbon + O&M) constants are changed — formula is pinned
  3. `tests/test_benchmarks.py` documents divergence from LCCC self-reconciliation and any regulator-native external sources the researcher located (OBR, Ofgem, DESNZ, HoC Library, NAO) explicitly in the fixture notes or test docstring
  4. GitHub Actions CI workflow triggers on every push to `main` and reports pass/fail
  5. `counterfactual.py` carries a `methodology_version` string; `CHANGES.md` logs the initial version
**Plans:** 5/5 plans executed
Plans:
- [x] 02-01-PLAN.md — Counterfactual pin test + METHODOLOGY_VERSION + CHANGES.md 1.0.0 entry (TEST-01, GOV-04)
- [x] 02-02-PLAN.md — Pandera schemas on Elexon/ONS loaders + test_schemas.py + test_aggregates.py pre-Parquet scaffolding (TEST-02, TEST-03)
- [x] 02-03-PLAN.md — Benchmarks fixture (Pydantic + YAML) + test_benchmarks.py with LCCC floor + external anchors (TEST-04)
- [x] 02-04-PLAN.md — GitHub Actions CI workflow running uv + pytest on push/PR (TEST-06)
- [x] 02-05-PLAN.md — REQ-ID bookkeeping: reassign TEST-02/03/05 to Phase 4 in ROADMAP + REQUIREMENTS + CHANGES

### Phase 3: Chart Triage Execution
**Goal**: The CfD chart set is tidy and fully documented, with every PRODUCTION chart reachable from a five-theme navigation structure
**Depends on**: Phase 2
**Requirements**: TRIAGE-01, TRIAGE-02, TRIAGE-03, TRIAGE-04, GOV-01
**Success Criteria** (what must be TRUE):
  1. `scissors.py` and `bang_for_buck_old.py` are absent from the working tree (preserved only in git history); the sole in-tree references are inside `tests/test_docs_structure.py`, which asserts their absence as the permanent TRIAGE-01 regression guard
  2. All seven PROMOTE charts (`cfd_payments_by_category`, `lorenz`, `subsidy_per_avoided_co2_tonne`, `capture_ratio`, `capacity_factor/seasonal`, `intermittency/generation_heatmap`, `intermittency/rolling_minimum`) have a narrative docs page, a methodology section, a test reference, and a source-file link
  3. `docs/themes/` contains five directories (`cost/`, `recipients/`, `efficiency/`, `cannibalisation/`, `reliability/`), each with an `index.md` and `methodology.md`
  4. Every PRODUCTION chart is navigable from its theme page — no orphaned chart pages
  5. `mkdocs build --strict` passes with the full theme structure
**Plans:** 4 plans
Plans:
- [x] 03-01-PLAN.md — Triage cleanup: delete scissors.py + bang_for_buck_old.py; mkdocs.yml feature + validation deltas (Wave 1 prep)
- [x] 03-02-PLAN.md — 5-theme scaffolding: git mv 3 CfD pages, create theme index/methodology + PROMOTE stubs, rewrite nav, fix homepage link-rot
- [x] 03-03-PLAN.md — 7 PROMOTE chart pages filled (D-01 template, GOV-01 four-way coverage; parallelisable per chart)
- [x] 03-04-PLAN.md — Chart regen + mkdocs --strict CI gate + test_docs_structure.py + phase-exit checkpoint
**UI hint**: yes

### Phase 4: Publishing Layer
**Goal**: External consumers can discover, fetch, and cite any dataset via a machine-readable manifest with full provenance, and the three-layer pipeline is operational end-to-end for CfD
**Depends on**: Phase 3
**Requirements**: PUB-01, PUB-02, PUB-03, PUB-04, PUB-05, PUB-06, GOV-02, GOV-03, GOV-06 (snapshot URL portion), TEST-02, TEST-03, TEST-05
**Success Criteria** (what must be TRUE):
  1. `site/data/manifest.json` is present after build and contains source URL, retrieval timestamp, SHA-256, pipeline git SHA, and `methodology_version` per dataset
  2. External consumer can follow a URL from `manifest.json` and retrieve a Parquet file and its CSV mirror
  3. `publish/snapshot.py` creates an immutable `site/data/v<date>/` directory on tagged release
  4. `docs/data/index.md` explains how journalists and academics use the datasets, including citation via versioned snapshot URL
  5. GitHub Actions daily refresh workflow (06:00 UTC cron) with per-scheme dirty-check is committed and functional
**Plans:** 7 plans
Plans:
- [x] 04-01-wave0-deps-and-constants-drift-test-PLAN.md — Add pyarrow + duckdb deps; ship SEED-001 Tier 2 constants drift test (constants.yaml + fixtures loader + test_constants_provenance.py)
- [x] 04-02-raw-layer-migration-PLAN.md — Atomic git mv of 5 raw files to data/raw/<publisher>/<file>; backfill 5 .meta.json sidecars; update loaders + YAML paths (D-04/05/06)
- [x] 04-03-derived-layer-cfd-schemes-PLAN.md — schemas/cfd.py Pydantic + schemes/ Protocol + schemes/cfd/ contract + rebuild_derived; Parquet variants for test_schemas + test_aggregates; new test_determinism (D-01/03/19/20/21/22)
- [x] 04-04-publishing-layer-manifest-PLAN.md — publish/{manifest,csv_mirror,snapshot}.py + refresh_all.py + test_manifest + test_csv_mirror (D-07/08/09/10/11/13/18; PUB-01/02/03/06; GOV-02)
- [x] 04-05-workflows-refresh-deploy-PLAN.md — refresh.yml cron + deploy.yml tag; refresh-failure-template.md (D-13/14/16/17; GOV-03; GOV-06)
- [x] 04-06-docs-and-benchmark-floor-PLAN.md — docs/data/index.md + mkdocs nav + citation versioned-URL + LCCC ARA 2024/25 floor disposition (PUB-04; GOV-06; TEST-04; D-26/27)
- [x] 04-07-refresh-loop-closure-PLAN.md — Gap closure from 04-VERIFICATION.md: sidecar.write_sidecar() atomic helper + ons_gas UnboundLocalError fix + refresh() wires LCCC+Elexon+ONS + refresh-loop invariant test (GOV-03; PUB-05 robustness)

### Phase 5: RO Module
**Goal**: The Renewables Obligation scheme is fully tracked from raw Ofgem data through to published charts, benchmarked against REF Constable 2025 Table 1 (Turver retained as peer cross-check), and integrated into the site as the second scheme module
**Depends on**: Phase 4
**Requirements**: RO-01, RO-02, RO-03, RO-04, RO-05, RO-06
**Success Criteria** (what must be TRUE):
  1. `schemes/ro/` module exposes all five §6.1 contract functions (`upstream_changed`, `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`)
  2. RO S2 dynamics, S3 cost-by-technology, S4 concentration/Lorenz, and S5 forward-commitment charts are published and reachable from the site
  3. `tests/test_benchmarks.py` passes with RO 2011–2022 aggregate within 3% of REF Constable 2025 Table 1 per-year figures; any divergence is documented (per CONTEXT D-13 post-research amendment)
  4. `docs/schemes/ro.md` scheme page exists with S2–S5 chart embeds and links to Cost and Recipients theme pages
  5. RO derived Parquet tables (`station_month`, `annual_summary`, `by_technology`, `by_allocation_round`, `forward_projection`) are present in `data/derived/ro/` after a build
**Plans:** 5/13 plans executed
Plans:
- [x] 05-01-PLAN.md — Ofgem RER scraper investigation + ofgem_ro.py + roc_prices.py + seed raw/ofgem/ tree + sidecars + mocked scraper tests (RO-01)
- [x] 05-02-PLAN.md — ro_bandings.yaml ~60-row table + Pydantic RoBandingEntry/RoBandingTable loader + unit tests (RO-02)
- [x] 05-03-PLAN.md — schemas/ro.py 5 Pydantic row models + emit_schema_json import from schemas.cfd + smoke tests (RO-03)
- [x] 05-04-PLAN.md — counterfactual.DEFAULT_CARBON_PRICES backward extension 2005-2017 + 22 new constants.yaml entries + _TRACKED completion + CHANGES.md (RO-02)
- [x] 05-05-PLAN.md — schemes/ro/ module (__init__ + _refresh + cost_model + aggregation + forward_projection) + smoke rebuild tests + §6.1 Protocol conformance (RO-02, RO-03)
- [x] 05-06-PLAN.md — publish/manifest.py scheme-parametric refactor + refresh_all.publish_latest update + multi-scheme manifest tests (RO-03)
- [x] 05-07-PLAN.md — refresh_all.SCHEMES RO registration (one-line append) + test_refresh_loop RO invariant tests (RO-02, RO-03)
- [x] 05-08-PLAN.md — 4 RO charts ro_dynamics + ro_by_technology + ro_concentration + ro_forward_projection + plotting/__main__ wiring (RO-04)
- [x] 05-09-PLAN.md — REF Constable 2025 Table 1 → benchmarks.yaml + Benchmarks.ref_constable Pydantic field + test_benchmarks.py::test_ref_constable_ro_reconciliation parametrised D-14 hard-block test (RO-06)
- [x] 05-10-PLAN.md — test_schemas + test_aggregates + test_determinism RO grain parametrisations (RO-03)
- [x] 05-11-PLAN.md — docs/schemes/ro.md + schemes/index.md + mkdocs.yml Schemes nav + theme-page cross-links + homepage entry + mkdocs --strict gate (RO-05)
- [x] 05-12-PLAN.md — CHANGES.md [Unreleased] + ## Methodology versions consolidation; phase-exit verify (RO-01..RO-06)

### Phase 05.1: CfD Scheme Page Retrofit (INSERTED)

**Goal**: Ship `docs/schemes/cfd.md` mirroring the `docs/schemes/ro.md` shape (adversarial-headline lead + 4 charts embedded + GOV-01 four-way coverage manifest + citation block); migrate the homepage "Module in focus: Contracts for Difference" section into it; convert the homepage to a scheme-grid listing CfD and RO as equal tiles. Phase-6 scheme-grid prerequisite — restores symmetry between CfD (historical prototype) and RO (first portal-pattern scheme).
**Depends on**: Phase 5
**Requirements**: SCHEMEPAGE-01
**Plans:** 4 plans

Plans:
- [ ] 05.1-01-PLAN.md — Create docs/schemes/cfd.md with migrated prose + 4 chart embeds + GOV-01 + Headline FAQ (SCHEMEPAGE-01)
- [ ] 05.1-02-PLAN.md — Delete 4 overlap theme pages + migrate inbound links + update mkdocs.yml nav + update schemes/index.md + retarget ro.md and rolling-minimum.md cross-links (SCHEMEPAGE-01)
- [ ] 05.1-03-PLAN.md — Pivot docs/index.md to hero + 2×4 scheme grid (SCHEMEPAGE-01)
- [ ] 05.1-04-PLAN.md — CHANGES.md [Unreleased] entry + REQUIREMENTS.md SCHEMEPAGE-01 + ROADMAP.md bookkeeping (SCHEMEPAGE-01)

### Phase 6: Flagship Cross-Scheme Charts
**Goal**: The portal homepage renders with three headline numbers and the X1 stacked chart, making the full-scheme cost argument visible for the first time
**Depends on**: Phase 5
**Requirements**: X-01, X-02, X-03, X-04, X-05, PORTAL-01, PORTAL-02
**Success Criteria** (what must be TRUE):
  1. Portal homepage (`docs/index.md`) renders three headline cards (total subsidy / premium over gas / per household), the X1 stacked-by-scheme chart with Latest-year / Last-5-years / All-time tabs, and a 2×4 scheme grid
  2. X1 (stacked total), X2 (cumulative premium over gas), and X3 (cost per household by scheme) charts are published as PRODUCTION charts with narrative and methodology pages
  3. X4 (cost per MWh by scheme) and X5 (2022 crisis comparison) charts are published
  4. Scheme grid tiles show latest headline figure for CfD and RO; remaining tiles show placeholder figures
  5. `PORTAL-02`: Each populated scheme tile links to its scheme detail page
**Plans**: TBD
**UI hint**: yes

### Phase 7: FiT Module
**Goal**: The Feed-in Tariff scheme is tracked with S2/S3/S5 diagnostics and integrated into the portal scheme grid as the third populated tile
**Depends on**: Phase 6
**Requirements**: FIT-01, FIT-02, FIT-03, FIT-04
**Success Criteria** (what must be TRUE):
  1. `schemes/fit/` module exposes all five §6.1 contract functions and populates `data/derived/fit/` after a build
  2. FiT S2 dynamics, S3 cost-by-technology, and S5 forward-commitment charts are published (S4 concentration omitted — 800k domestic installs makes concentration trivial)
  3. `docs/schemes/fit.md` scheme page exists with chart embeds and links to relevant theme pages
  4. FiT scheme grid tile on portal homepage shows latest FiT headline figure and links to scheme page
**Plans**: TBD

### Phase 8: Constraint Payments Module
**Goal**: Constraint payments — the growing cost of paying wind farms to switch off — are tracked, charted, and visible as a line item in the cross-scheme X1 chart
**Depends on**: Phase 7
**Requirements**: CON-01, CON-02, CON-03, CON-04, CON-05
**Success Criteria** (what must be TRUE):
  1. `schemes/constraints/` module exposes all five §6.1 contract functions, with NESO BM half-hourly data rolled up to station-month grain
  2. Constraint S2 dynamics, S3 by-wind-farm, S4 top-N concentration, and S5 forward-trend charts are published
  3. The "£X bn paid to switch off" headline figure appears prominently on the constraint payments scheme page
  4. Constraint payments appear as a growing line item in the X1 stacked-by-scheme chart
  5. Scheme grid has five populated tiles (CfD, RO, FiT, Constraints, and one more placeholder)
**Plans**: TBD

### Phase 9: Capacity Market Module
**Goal**: The Capacity Market scheme is tracked with its specific methodological treatment (no gas counterfactual, attribution caveat) and published as the fifth scheme
**Depends on**: Phase 8
**Requirements**: CM-01, CM-02, CM-03, CM-04, CM-05
**Success Criteria** (what must be TRUE):
  1. `schemes/capacity_market/` module exposes all five §6.1 contract functions; EMR auction data populates `data/derived/capacity_market/`
  2. CM modified S2 (no gas counterfactual), S3 cost breakdown, S4 concentration, and S5 forward-commitment-to-2040 charts are published
  3. Attribution caveat — explaining which portion of CM cost is "caused by renewables" — is documented prominently on the CM scheme page with include/exclude views
  4. Scheme grid has five populated tiles (CfD, RO, FiT, Constraints, CM)
**Plans**: TBD

### Phase 10: Balancing Services Module
**Goal**: The incremental balancing services cost attributable to high renewable penetration is quantified, charted as a pre/post-renewables delta, and the running total approaches REF's £25.8bn within tolerance
**Depends on**: Phase 9
**Requirements**: BAL-01, BAL-02, BAL-03
**Success Criteria** (what must be TRUE):
  1. `schemes/balancing/` module exposes all five §6.1 contract functions; NESO monthly balancing costs populate `data/derived/balancing/` with delta-only rollups
  2. Pre/post-renewables baseline delta chart is published — showing the difference in balancing costs before and after significant wind build-out
  3. Combined total across CfD + RO + FiT + Constraints + CM + Balancing approaches REF's £25.8bn within ±15%
**Plans**: TBD

### Phase 11: Grid Socialisation Module
**Goal**: TNUoS grid socialisation costs attributable to renewable siting are estimated with explicit uncertainty bounds, completing the cost picture with prominent confidence caveats
**Depends on**: Phase 10
**Requirements**: GRID-01, GRID-02, GRID-03
**Success Criteria** (what must be TRUE):
  1. `schemes/grid/` module produces best-efforts TNUoS attribution in `data/derived/grid/` with low/central/high sensitivity bounds
  2. Grid costs are presented as a range (not a point estimate) on the grid scheme page, with a prominent confidence caveat explaining the attribution methodology
  3. Combined total across all scheme modules approaches REF's £25.8bn within ±15% using the central estimate
**Plans**: TBD

### Phase 12: SEG + REGOs Completion
**Goal**: All eight scheme tiles on the portal homepage are populated, completing the portal's coverage of UK renewable subsidy schemes
**Depends on**: Phase 11
**Requirements**: SEG-01, SEG-02, SEG-03
**Success Criteria** (what must be TRUE):
  1. `docs/schemes/seg.md` aggregate-only scheme page exists with headline cost figure and caveat that no station-level data is available
  2. `docs/schemes/regos.md` aggregate page exists for completeness
  3. All eight scheme grid tiles on the portal homepage are populated with a headline figure and link to their scheme detail page
**Plans**: TBD
**UI hint**: yes

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation Tidy | 0/4 | Not started | - |
| 2. Test & Benchmark Scaffolding | 5/5 | Complete | 2026-04-22 |
| 3. Chart Triage Execution | 4/4 | Complete | 2026-04-22 |
| 4. Publishing Layer | 0/6 | Not started | - |
| 5. RO Module | 5/13 | In Progress|  |
| 05.1. CfD Scheme Page Retrofit | 0/4 | Planned | - |
| 6. Flagship Cross-Scheme Charts | 0/0 | Not started | - |
| 7. FiT Module | 0/0 | Not started | - |
| 8. Constraint Payments Module | 0/0 | Not started | - |
| 9. Capacity Market Module | 0/0 | Not started | - |
| 10. Balancing Services Module | 0/0 | Not started | - |
| 11. Grid Socialisation Module | 0/0 | Not started | - |
| 12. SEG + REGOs Completion | 0/0 | Not started | - |

---
*Roadmap defined: 2026-04-21*
*Maps 1:1 to ARCHITECTURE.md §11 phases P0–P11*
