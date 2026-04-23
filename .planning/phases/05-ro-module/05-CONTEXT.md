# Phase 5: RO Module — Context

**Gathered:** 2026-04-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the Renewables Obligation scheme as the second `schemes/<scheme>/` module conforming to ARCHITECTURE §6.1, proving the scheme-module pattern generalises beyond CfD. Raw → derived → published end-to-end; S2/S3/S4/S5 charts live on the site; RO 2011-2022 aggregate benchmarked within ±3% of Turver; `docs/schemes/ro.md` is the second scheme detail page and establishes the pattern Phase 7 (FiT) and Phases 8-12 copy.

**In scope:**

- **Ofgem scrapers.** `data/raw/ofgem/{ro-register,ro-generation,roc-prices,roc-buyout}.{csv,xlsx}` with `.meta.json` sidecars via shared `uk_subsidy_tracker.data.sidecar.write_sidecar()`. Covers the station register (XLSX), monthly ROC issuance (CSV), buy-out prices (yearly), recycle payments (yearly), and e-ROC auction clearing (quarterly).
- **`schemes/ro/` module.** Five §6.1 contract functions (`upstream_changed`, `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`) with real implementations. Internal modules: `cost_model.py`, `aggregation.py`, `forward_projection.py`, `_refresh.py` — mirroring `schemes/cfd/` verbatim.
- **Bandings YAML.** `src/uk_subsidy_tracker/data/ro_bandings.yaml` carrying ~60 (technology × commissioning-window) rows from RO Order + amendments, each with Provenance block per constant-provenance pattern.
- **Five Parquet grains.** `data/derived/ro/{station_month, annual_summary, by_technology, by_allocation_round, forward_projection}.parquet` — names locked by ROADMAP SC #5, snake_case per ARCHITECTURE §4.2.
- **Pydantic schemas.** `src/uk_subsidy_tracker/schemas/ro.py` — per-grain row models matching CfD schema pattern; used by loaders + manifest + test_schemas parametrisation.
- **Carbon-price table extension.** `counterfactual.DEFAULT_CARBON_PRICES` extended backward: EU ETS annual averages 2005-2017 (EUR→GBP contemporary rates), zero 2002-2004. `constants.yaml` gets new entries per Phase 4 D-23 pattern; `CHANGES.md [Unreleased] ## Methodology versions` logs the extension.
- **Four charts.** `plotting/subsidy/ro_{dynamics,by_technology,concentration,forward_projection}.py` mirroring CfD equivalents; PNG + interactive HTML to `docs/charts/html/`.
- **`docs/schemes/ro.md`.** Second scheme detail page. Headline figure, 2002-2037 explainer, S2-S5 embeds, methodology summary + link to shared gas-counterfactual methodology page, cross-links to Cost + Recipients theme pages.
- **Test parametrisations.** `test_schemas.py` over five RO Parquet grains, `test_aggregates.py` row-conservation on RO grains, `test_determinism.py` byte-identity on RO, `test_benchmarks.py::lccc_self` grows RO anchor entries (Turver 2011-2022).
- **`refresh_all.SCHEMES`** gets a one-line append registering the RO scheme module.

**Out of scope (belongs to later phases):**

- **X1/X2/X3/X4/X5 cross-scheme charts** — Phase 6.
- **Combined CfD+RO flagship chart** (RO-MODULE-SPEC.md calls it "chart 5") — this is X1 + X2 territory; moves to Phase 6.
- **Portal homepage (three headline cards + scheme grid)** — Phase 6 (PORTAL-01/02).
- **FiT scheme module** — Phase 7. No `fit/` stub directory; ROADMAP orders it cleanly.
- **Constraint Payments / Capacity Market / Balancing / Grid / SEG** — Phases 8-12.
- **METHODOLOGY_VERSION bump to 1.0.0** — Phase 6+ portal launch.
- **Zenodo DOI registration** — V2-COMM-01, triggers after Phase 5 lands (not during).
- **Aggressive chart-code refactor into scheme-parametric helpers** — Phase 6, when X-chart shared infrastructure actually needs it.
- **docs/data/ro.md per-scheme data page** — `docs/data/index.md` works unchanged for RO (per Phase 4 D-27); per-scheme data pages are a later polish if adoption warrants.
- **Cloudflare R2 for oversized raw files** — RO station-register XLSX is ≤100MB (per spec §4.1 estimate ~500k rows); R2 first becomes relevant in Phase 8 NESO BM data.

</domain>

<decisions>
## Implementation Decisions

### Cost-model methodology (R1 banding + R6 ROC price)

- **D-01 rocs_issued source.** Use **Ofgem's published `ROCs_Issued` column** as the authoritative value on every station-month row. YAML bandings table is loaded but used only as an **audit cross-check**: compute `generation_mwh × banding_factor` via `ro_bandings.yaml` lookup and **log warning** on stations where `|ofgem_issued - computed| / ofgem_issued > 1%`. Short-circuits R1 (banding-assignment risk) by deferring to the regulator's own certification. Warning log surfaces station-level data-quality issues; does not block the pipeline.
- **D-02 ROC price — dual columns.** `station_month.parquet` carries **two cost columns**: `ro_cost_gbp` = `rocs_issued × (buyout_gbp_per_roc + recycle_gbp_per_roc)` for the obligation year (**primary**, consumer-cost view); `ro_cost_gbp_eroc` = `rocs_issued × eroc_clearing_gbp_per_roc` (**sensitivity**, generator-revenue view). Annual summary carries both aggregates. S2 dynamics chart shows them as a 2-10% sensitivity band so readers see the convention-choice's numerical weight.
- **D-03 Bandings YAML location + scope.** `src/uk_subsidy_tracker/data/ro_bandings.yaml` alongside `lccc_datasets.yaml` pattern. Covers all (technology × commissioning-window × country) cells from RO Order + amendments. Each entry carries full `Provenance:` block (source: specific RO Order SI number + amendment SIs, URL, basis, retrieved_on, next_audit) per constant-provenance pattern. Pydantic-loaded via a `RoBandingEntry` + `RoBandingTable` pair in a sibling `ro_bandings.py` helper (mirroring `LCCCDatasetConfig` pattern).
- **D-04 `schemes/ro/validate()` returns warnings on all four checks.**
  1. **Banding divergence** — count stations with >1% `ofgem_vs_computed` delta; warn if >10 stations or >5% of station population.
  2. **Turver-band drift** — recompute 2011-2022 `ro_cost_gbp` aggregate; warn if outside `±3%` of Turver anchor.
  3. **Methodology version consistency** — warn if any RO Parquet's `methodology_version` column differs from the live `counterfactual.METHODOLOGY_VERSION`.
  4. **Forward projection sanity** — warn on negative costs or MWh jumps >50% between adjacent years in `forward_projection.parquet`.
  All four are cheap post-rebuild checks; empty return = clean.

### Time axis + carbon extension (R2 pre-2013 carbon + R3 CY/OY)

- **D-05 Carbon-price extension with sensitivity.** `counterfactual.DEFAULT_CARBON_PRICES` extended backward to cover RO's 2002-present span: EU ETS annual averages 2005-2017 (EUR→GBP at contemporary average rates; ICE/EEX as provenance), zeros 2002-2004 (no carbon scheme). Primary `ro_cost_gbp` flows the full extended table through `compute_counterfactual()`. Additionally, `station_month.parquet` carries `ro_cost_gbp_nocarbon` column (sensitivity — how much of RO premium is pure subsidy vs carbon). `constants.yaml` gets new entries for each added year with Provenance block (SEED-001 Tier 2 discipline). `CHANGES.md [Unreleased] ## Methodology versions` logs the 2002-2017 coverage extension.
- **D-06 METHODOLOGY_VERSION stays `"0.1.0"`.** Per Phase 2 D-05 + `counterfactual.py` module docstring: pre-1.0.0 is prototype phase; constants may change without version ceremony. The 2005-2017 extension is **additive** (new year keys in `DEFAULT_CARBON_PRICES`; no revision of existing 2018-2026 values) and is not a formula-shape change. Bump to 1.0.0 is reserved for Phase 6+ portal launch and is a deliberate milestone event. `CHANGES.md ## Methodology versions` records the extension as a noteworthy audit event without bumping the version string.
- **D-07 Calendar year is the primary plotting axis.** Every RO chart S2-S5 plots by calendar year. Obligation year (Apr-Mar) surfaces in:
  - `station_month.parquet::obligation_year` column (audit trail + price-lookup source of truth).
  - `docs/schemes/ro.md` methodology section explaining the CY-axis + OY-price convention.
  - No OY-axis charts published in Phase 5; future phases may add if research warrants.
  Rationale: gas counterfactual is CY-anchored; CfD is CY; Phase 6 cross-scheme X1/X2/X3 demands a single axis. Consistent axis is an adversarial-proofing concern.
- **D-08 ROC-price assignment rule.** For each station-month row, `roc_price_gbp = buyout + recycle` for the **obligation year containing the output period end**. March 2022 generation → OY 2021-22 price; April 2022 generation → OY 2022-23 price. Encoded as `obligation_year` column on `station_month.parquet` for auditability. Rejected alternatives: weighted-average across OYs intersecting the CY (obscures mechanism); OY-ending-in-CY (assigns prices from OYs that covered only 3 months of the CY).

### Scope inclusions (R4 NIRO + R5 co-firing + R7 mutualisation)

- **D-09 NIRO included; headlines GB-only.** Scraper fetches both GB and NI station registers + NI-specific buyout/recycle price series. Every row in `station_month.parquet` carries a `country` column with values `'GB'` or `'NI'`. `docs/schemes/ro.md` headline figure is **GB-only** (most readers' mental model; matches CfD scope); `annual_summary.parquet` rows are emitted per (obligation_year × country) so adversarial readers can filter to UK-wide via DuckDB. Methodology section documents: "NIRO is a separate scheme administered by Ofgem NI with distinct buyout prices and bandings; we include NI rows in `data/derived/ro/*.parquet` and quote GB-only headline totals — UK total reconstructable via filter."
- **D-10 Co-firing biomass included.** Co-fired biomass MWh receives Ofgem-certified ROCs and was paid by consumers; it is part of the consumer-cost total. Derived tables carry a distinct `technology='biomass_cofiring'` slice. Methodology section on `docs/schemes/ro.md` notes the philosophical contestability of counting co-firing as "renewable" (attribution debate around Drax's 2003-2016 coal/biomass blend) with a "filter this slice" instruction. No dual headline — the all-in figure is primary; breakdown available via Parquet technology column.
- **D-11 Mutualisation rolled into `ro_cost_gbp`; affected years flagged.** `roc_price_gbp` for obligation years 2021-22 and 2022-23 is adjusted upward by the published mutualisation delta (Ofgem publishes this in the Annual Report following the shortfall). `annual_summary.parquet` carries an additional `mutualisation_gbp` column showing the additive component on mutualisation-affected years (null on clean years). S2 dynamics chart visibly spikes on affected years; methodology section documents the event ("Suppliers defaulted on their ROC obligations in the 2021 energy-price crisis; Ofgem redistributed the shortfall across remaining suppliers, who passed the cost to consumers"). Mutualisation is included in Turver-benchmark reconciliation (D-14); if Turver excluded mutualisation, that's a scope-delta entry in benchmarks.yaml audit header.
- **D-12 Headline = all-in GB total.** `docs/schemes/ro.md` lead figure: "**£X bn in RO subsidy paid by UK consumers since 2002**" (GB-only, includes cofiring, includes mutualisation). Immediately below, a breakdown paragraph: "of which £A bn attributable to cofiring; £B bn from mutualisation events in 2021-22; NIRO (£C bn) excluded from headline, available via `country='NI'` filter in the Parquet." Maximally adversarial-proof: every component is visible; adjustments are audit-accessible. No second prominent headline.

### Benchmark anchor + docs structure (RO-06 + ROADMAP SC #4)

- **D-13 Turver anchor picked by researcher.** Exact Turver publication deferred to `gsd-phase-researcher` at Phase 5 research time. Researcher identifies most-defensible Turver source with a cleanly transcribable CY 2011-2022 RO aggregate total (candidates include Net Zero Watch 2023 paper "The Hidden Cost of Net Zero"; researcher verifies the paper's Table X figure is CY not OY, includes or excludes cofiring/mutualisation/NIRO, and carries a retrievable PDF URL). Benchmark entry: `tests/fixtures/benchmarks.yaml::turver` gets a new top-level key with entries per transcribed year. Tolerance constant: `TURVER_TOLERANCE_PCT = 3.0` in `tests/fixtures/__init__.py` or equivalent tolerance dispatch per Phase 2 D-07. Phase 2 D-11 fallback (skip-if-unavailable) **does not apply** here — ROADMAP SC #3 is binary.
- **D-14 ±3% divergence is a hard block.** `test_benchmarks.py` parametrises over the Turver anchor years; aggregate `ro_cost_gbp` (all-in GB total per D-12 scope) must be within ±3% of Turver's figure. If divergence exceeds 3%, investigate root cause before phase exit:
  - Is Turver's scope different? (NIRO inclusion, mutualisation treatment, cofiring attribution, CY vs OY) → document scope-delta in benchmarks.yaml audit header; adjust tolerance only if scope difference is documented and legitimate.
  - Is a banding error surfacing? (R1 regression) → fix bandings YAML; re-derive.
  - Is the carbon-price extension wrong? (D-05 regression) → revisit DEFAULT_CARBON_PRICES pre-2018 values.
  Phase does not ship with failing test_benchmarks. Matches Phase 3/4 "strict gate" discipline.
- **D-15 `docs/schemes/ro.md` single-page scheme overview.** Structure:
  1. **Headline** — £X bn all-in GB total (per D-12).
  2. **What is the RO?** — 2-3 paragraph explainer: 2002-2037 timeline, how consumers pay (supplier obligation → ROC certificates → buyout + recycle), why it's the "scheme you've never heard of twice the size of the one you have".
  3. **Cost dynamics** — S2 4-panel chart embed (PNG + interactive HTML link), prose commentary.
  4. **By technology** — S3 stacked chart embed, prose noting onshore wind + offshore wind + biomass shares.
  5. **Concentration** — S4 Lorenz-style chart embed, top-N operator callout.
  6. **Forward commitment** — S5 chart embed, 2026 → 2037 drawdown.
  7. **Methodology summary** — link to `docs/methodology/gas-counterfactual.md` + co-firing/mutualisation/NIRO caveats + Turver benchmark reconciliation.
  8. **Data & code** — GOV-01 four-way coverage at scheme level: primary Ofgem register URL + chart source permalinks + test permalinks + reproduce bash block.
  Cross-links: `docs/themes/cost/index.md` (RO rows in Cost theme chart gallery) + `docs/themes/recipients/index.md` (RO concentration surfaces on Recipients theme). **No per-chart pages under `docs/schemes/ro/`** in Phase 5 — scheme-level page is the GOV-01 unit; per-chart expansion deferred if research/usage warrants.
- **D-16 Chart code — RO-specific copies with opportunistic shared helpers.** New files: `plotting/subsidy/ro_dynamics.py`, `ro_by_technology.py`, `ro_concentration.py`, `ro_forward_projection.py`. Structure mirrors `cfd_dynamics.py`, `remaining_obligations.py`, etc. Where 2-3 lines literally duplicate between CfD and RO (e.g., title formatting, PNG `save()` call, axis-formatting helpers), extract to `plotting/subsidy/_shared.py` at planner's discretion. **Aggressive refactor to scheme-parametric helpers is deferred to Phase 6** when X1/X2/X3 cross-scheme charts force shared infrastructure; a refactor in Phase 5 risks regressing Phase 3's 7 PROMOTE CfD charts and blows up scope. Matches Phase 4 D-02 "charts untouched" discipline.

### Claude's Discretion

- **Ofgem scraper mechanism.** HTTP GET with `requests` against stable URLs if available; Playwright/browser automation only if Ofgem's register requires form interaction. Planner chooses at research time. Error-path discipline follows Phase 4 Plan 07 pattern (output_path bound before try, timeout=60, bare raise on failure).
- **`ro_bandings.yaml` schema shape.** Two-layer Pydantic model (`RoBandingEntry` + `RoBandingTable`) mirroring `LCCCDatasetConfig` + `LCCCAppConfig` from Phase 2 D-07 source-key injection pattern. Exact field set planner-decided; must include technology, commissioning window start, commissioning window end, country, banding factor, RO-Order SI citation per Provenance block.
- **Forward projection methodology for 2026 → 2037.** Extrapolation approach (straight-line from last metered year? capacity-factor × installed capacity × remaining accreditation years? per-station expected end date from accreditation record?) is a planner decision. Must be deterministic (D-21 content-identity invariant from Phase 4); must document the chosen extrapolation in `ro_forward_projection.py` docstring + methodology page.
- **Mutualisation data source + entry points.** Ofgem publishes mutualisation per Annual Report; planner picks extraction approach (manual YAML fixture vs scraped table). Either way: `roc_prices.csv` carries the adjusted price; mutualisation delta exposed as separate `annual_summary` column.
- **Refresh cadence for Ofgem in `refresh_all.py`.** ARCHITECTURE §7.1 suggests monthly for Ofgem RO register (monthly publication with ~3-month lag). Planner may choose daily (with dirty-check short-circuit on unchanged SHA) vs conditional-skip-if-month-boundary. Matches Phase 4 D-18 per-scheme dirty-check philosophy.
- **RO-specific test fixtures.** Planner decides whether `tests/data/test_ofgem_ro.py` gets its own fixture file or piggybacks on existing test patterns. Must not add network calls to CI test runs (Phase 4 discipline).
- **Test parametrisation strategy for RO grains.** Existing CfD `test_schemas` / `test_aggregates` / `test_determinism` structure parametrises over grain name; RO planner decides whether to extend the same parametrisation or add RO-specific test files. Former is the established pattern.

### Folded Todos

No pending todos from STATE.md matched Phase 5 (per `gsd-tools todo match-phase 5`).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Authoritative spec

- `ARCHITECTURE.md` §4 — Three-layer data architecture. Verbatim substrate for `data/raw/ofgem/*`, `data/derived/ro/*`, `site/data/latest/ro/*`.
- `ARCHITECTURE.md` §6.1 — Scheme-module contract (five functions + `DERIVED_DIR`). **Load-bearing template** for `schemes/ro/` — must isomorphically conform.
- `ARCHITECTURE.md` §6.2 — Shared counterfactual — `counterfactual.compute_counterfactual` reused unchanged; D-05 extends its `DEFAULT_CARBON_PRICES` table backward.
- `ARCHITECTURE.md` §7.1 — Per-source refresh cadence; Ofgem RO register is monthly (~3-month lag) per table.
- `ARCHITECTURE.md` §9.1 + §9.4 — Provenance + methodology-versioning chain; RO Parquet rows carry `methodology_version` column.
- `ARCHITECTURE.md` §11 P4 — Phase 5 entry/exit criteria (lines ~918-935). Exit: RO module + 4 charts + Turver benchmark + docs page.
- `RO-MODULE-SPEC.md` — **Single authoritative source on RO domain**. §1 goal, §3 chart set, §4 data sources (5 scrapers), §5 module architecture, §6 data model (grain schemas), §7 cost-computation formula, §8 pipeline stages, §9 validation gates, **§10 R1-R7 risks** (every D-01..D-12 decision references one of these), §12 success criteria, Appendix A naming cross-reference.

### Roadmap + requirements

- `.planning/ROADMAP.md` Phase 5 (lines ~99-109) — Five success criteria. SC #1 five-function contract, SC #2 four charts published, SC #3 Turver ±3%, SC #4 `docs/schemes/ro.md`, SC #5 five derived Parquet grains.
- `.planning/REQUIREMENTS.md` — RO-01 Ofgem scraper, RO-02 §6.1 conformance, RO-03 five Parquet grains, RO-04 four charts, RO-05 docs page + theme integration, RO-06 Turver ±3%.
- `.planning/PROJECT.md` — Core-value "reproducible from single git clone + uv sync + one command"; adversarial-proofing as first-class concern; Parquet + DuckDB; Cloudflare Pages static hosting.
- `.planning/STATE.md` — Current position: Phase 5 starting, all Phase 4 exit criteria delivered incl. refresh-loop closure; 74 passed + 4 skipped; `mkdocs --strict` clean; METHODOLOGY_VERSION at `"0.1.0"`.

### Prior-phase context (locked decisions apply)

- `.planning/phases/01-foundation-tidy/01-CONTEXT.md` — Atomic-commit discipline; Material theme; `CHANGES.md` Keep-a-Changelog with `## Methodology versions` section.
- `.planning/phases/02-test-benchmark-scaffolding/02-CONTEXT.md` — Methodology-versioning discipline; loader-owned pandera validation; Pydantic + YAML fixture pattern with source-key injection (D-07); benchmark tolerance constants per-source with `_TOLERANCE_BY_SOURCE` dispatch; D-11 fallback posture for external anchors (but D-14 here makes RO-06 binary).
- `.planning/phases/03-chart-triage-execution/03-CONTEXT.md` — D-01 six-section chart page template; GOV-01 four-way coverage as the quality bar; `docs/methodology/gas-counterfactual.md` as single source of truth for counterfactual methodology; adversarial-payload-first pattern for chart pages.
- `.planning/phases/04-publishing-layer/04-CONTEXT.md` — Three-layer pipeline operational; `schemes/cfd/` as the §6.1 template; `sidecar.write_sidecar()` shared atomic helper; `refresh_all.SCHEMES` registration; `manifest.py` iterates `SCHEMES` so RO auto-publishes; `constants.yaml` + drift test (Phase 5 adds extended-carbon entries).

### Files to modify

- `src/uk_subsidy_tracker/counterfactual.py` — Extend `DEFAULT_CARBON_PRICES` backward 2005-2017 (EU ETS averages; EUR→GBP); zeros 2002-2004. `METHODOLOGY_VERSION` unchanged at `"0.1.0"`.
- `src/uk_subsidy_tracker/refresh_all.py` — Append `schemes.ro` to `SCHEMES` list; one line. Per-scheme dirty-check (D-18 from Phase 4) automatically applies.
- `src/uk_subsidy_tracker/publish/manifest.py` — No code change; already iterates `SCHEMES`. Verify RO grains surface in manifest.json after registration.
- `tests/fixtures/constants.yaml` — Add entries for extended `DEFAULT_CARBON_PRICES` years (2002-2017) with Provenance blocks (EU ETS source + URL + basis: CY annual average + retrieved_on + next_audit).
- `tests/fixtures/benchmarks.yaml` — Add `turver` section with CY 2011-2022 annual totals (researcher-transcribed at Phase 5 research time) + audit-header note citing publication.
- `tests/test_schemas.py` — Parametrise over RO grains (mirror CfD parametrisation).
- `tests/test_aggregates.py` — Parametrise row-conservation invariants over RO grains.
- `tests/test_determinism.py` — Parametrise byte-identity checks over RO grains.
- `tests/test_benchmarks.py` — Add Turver reconciliation test over RO aggregate with `TURVER_TOLERANCE_PCT = 3.0`.
- `tests/test_constants_provenance.py::_TRACKED` — Ensure new 2002-2017 `DEFAULT_CARBON_PRICES` year entries fire the drift tripwire.
- `mkdocs.yml` — Add RO scheme-page nav entry (where under the nav — TBD — probably a new top-level "Schemes" tab holding CfD + RO detail pages, or fold RO under existing structure; planner decides).
- `docs/index.md` — Update portal-homepage link with RO headline figure once computed.
- `docs/themes/cost/index.md` + `docs/themes/recipients/index.md` — Add RO chart entries to the theme galleries (S2 + S3 in Cost; S4 in Recipients; S5 Cost or standalone — planner picks).
- `CHANGES.md` — `[Unreleased]` entries: RO scraper + module + Parquet grains + charts + docs page; `## Methodology versions` entry for DEFAULT_CARBON_PRICES 2002-2017 extension.

### Files to create

- `src/uk_subsidy_tracker/data/ofgem_ro.py` — Ofgem RO register + generation scraper (mirror `data/lccc.py` pattern).
- `src/uk_subsidy_tracker/data/roc_prices.py` — Buyout + recycle + e-ROC scrapers → `data/raw/ofgem/roc-prices.csv`.
- `src/uk_subsidy_tracker/data/ro_bandings.yaml` — Technology × commissioning-window × country banding factors with Provenance blocks.
- `src/uk_subsidy_tracker/data/ro_bandings.py` — Pydantic loader for the YAML (mirror `LCCCAppConfig` pattern).
- `src/uk_subsidy_tracker/schemas/ro.py` — Pydantic schemas for the five RO grains.
- `src/uk_subsidy_tracker/schemes/ro/__init__.py` — `DERIVED_DIR` + five §6.1 contract functions.
- `src/uk_subsidy_tracker/schemes/ro/_refresh.py` — `refresh()` wires the three Ofgem scrapers + writes sidecars via `sidecar.write_sidecar()` (mirror `schemes/cfd/_refresh.py` pattern from 04-07).
- `src/uk_subsidy_tracker/schemes/ro/cost_model.py` — `build_station_month()` — Ofgem rocs_issued join + YAML bandings cross-check + buyout+recycle pricing + e-ROC sensitivity + gas counterfactual + mutualisation adjustment.
- `src/uk_subsidy_tracker/schemes/ro/aggregation.py` — Annual, by_technology, by_allocation_round rollups (re-reads `station_month.parquet` per Phase 4 D-03).
- `src/uk_subsidy_tracker/schemes/ro/forward_projection.py` — 2026 → 2037 per-station remaining-obligations extrapolation.
- `src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py` — S2 4-panel (generation / ROC price vs gas counterfactual / premium per MWh / cumulative bill) with e-ROC sensitivity band.
- `src/uk_subsidy_tracker/plotting/subsidy/ro_by_technology.py` — S3 stacked area £/yr by technology.
- `src/uk_subsidy_tracker/plotting/subsidy/ro_concentration.py` — S4 Lorenz / top-N operator concentration.
- `src/uk_subsidy_tracker/plotting/subsidy/ro_forward_projection.py` — S5 forward-commitment drawdown to 2037.
- `src/uk_subsidy_tracker/plotting/subsidy/_shared.py` — (opportunistic) CfD+RO shared helpers where 2-3 lines literally duplicate.
- `docs/schemes/ro.md` — Second scheme detail page (structure per D-15).
- `data/raw/ofgem/{ro-register.xlsx, ro-generation.csv, roc-prices.csv}` + sibling `.meta.json` sidecars via `sidecar.write_sidecar()`.
- `tests/data/test_ofgem_ro.py` — Scraper-path tests (mocked; no network) per Phase 4 Plan 07 pattern.

### External references

- Ofgem Renewables and CHP Register: https://renewablesandchp.ofgem.gov.uk/ — accredited stations + monthly ROC issuance.
- Ofgem buy-out publications: https://www.ofgem.gov.uk/publications-and-updates/renewables-obligation-buy-out-price-and-mutualisation-ceilings — annual buyout + mutualisation ceilings.
- Ofgem Annual Report on the Renewables Obligation — recycle payments + ROCs presented + buy-out fund total; publication cadence ~6 months post year-end.
- e-ROC quarterly auction results: https://www.e-roc.co.uk/ — market-clearing ROC price; sensitivity anchor only.
- The Renewables Obligation Order 2009 (SI 2009/785) + amendments — bandings source (feeds `ro_bandings.yaml`).
- EU ETS historical spot prices (ICE/EEX reference) — pre-2021 carbon-price extension source (D-05).
- UK ETS historical prices via OBR Economic & Fiscal Outlook — post-2021 reference already in `counterfactual.py`.
- Turver 2023 Net Zero Watch paper "The Hidden Cost of Net Zero" (researcher to confirm at research time) — RO-06 benchmark anchor candidate.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`src/uk_subsidy_tracker/schemes/cfd/`** — The §6.1 template end-to-end. `__init__.py` (5 contract functions), `_refresh.py` (3 downloader wires + `sidecar.write_sidecar()` pattern), `cost_model.py` (raw → station_month), `aggregation.py` (3 rollup builders re-reading station_month Parquet per D-03), `forward_projection.py` (deterministic `pd.Timestamp.max().year` anchor per Phase 4). RO mirrors every file verbatim with RO-specific logic.
- **`src/uk_subsidy_tracker/data/sidecar.py::write_sidecar()`** — Shared atomic sidecar writer (`.tmp` + `os.replace`; `sort_keys=True` + `indent=2` + trailing newline). `schemes/ro/_refresh.py::refresh()` calls it for each of the 3 raw files exactly as `schemes/cfd/_refresh.py::refresh()` does. Guarantees byte-identical sidecars across refreshes.
- **`src/uk_subsidy_tracker/counterfactual.py::compute_counterfactual()`** — Reused unchanged. Accepts a full `DEFAULT_CARBON_PRICES` dict via `carbon_prices` kwarg; D-05's backward extension just adds new year keys. `methodology_version` column propagates automatically.
- **`src/uk_subsidy_tracker/data/lccc.py::LCCCAppConfig`** — Pydantic + PyYAML loader pattern. Direct analogue for `ro_bandings.py + ro_bandings.yaml` (D-03). Two-layer Pydantic + source-key injection (Phase 2 D-07).
- **`src/uk_subsidy_tracker/refresh_all.py::SCHEMES`** — One-line append (D-18 per-scheme dirty-check auto-activates).
- **`src/uk_subsidy_tracker/publish/manifest.py`** — Already iterates `SCHEMES`; no code change needed for RO. Verify it auto-discovers the new grains.
- **`tests/fixtures/benchmarks.yaml`** + `tests/fixtures/__init__.py::load_benchmarks` + `_TOLERANCE_BY_SOURCE` dispatch — Pattern for adding Turver section with `TURVER_TOLERANCE_PCT` constant.
- **`tests/fixtures/constants.yaml`** + `tests/test_constants_provenance.py::_TRACKED` — SEED-001 Tier 2 drift test. New `DEFAULT_CARBON_PRICES` year entries must appear in both places or the drift test fires.
- **`tests/test_determinism.py`** — pyarrow-strip determinism check; parametrise over RO grains (D-21 invariant from Phase 4).
- **`src/uk_subsidy_tracker/plotting/subsidy/cfd_dynamics.py`** + `remaining_obligations.py` — Chart structure templates for RO analogues. Preserved per Phase 4 D-02 "charts untouched" discipline; RO plotting is new files alongside, not refactors of CfD.
- **`docs/methodology/gas-counterfactual.md`** — Single source of truth for the counterfactual methodology (Phase 3 D-05a). `docs/schemes/ro.md` links OUT to this.

### Established Patterns

- **Atomic commits per concern** (Phase 1 D-16; reinforced every phase). Scrapers commit, bandings YAML commit, schemes/ro/ commit, charts commit, docs commit — each distinct.
- **Loader-owned pandera validation** — Every `.validate()` lives inside loader body, not in tests. `schemes/ro/cost_model.py` + `aggregation.py` loaders follow suit.
- **Two-layer Pydantic + source-key injection** (Phase 2 D-07). `ro_bandings.yaml` + `RoBandingEntry` + `RoBandingTable`; `benchmarks.yaml::turver` + existing `BenchmarkEntry` model (source key injected for tolerance dispatch).
- **Provenance docstring discipline** (Phase 3 commit `efdfbbc`). Every regulator-sourced constant in `src/` carries `Provenance:` block. RO bandings YAML rows carry equivalent blocks.
- **Deterministic current-year anchors** (Phase 4 Plan 03 decision). `ro_forward_projection.py` anchors on `gen['output_period_end'].max().year`, not `pd.Timestamp.now().year`. Prevents non-determinism on daily rebuilds.
- **int64 year cast in rollup builders** (Phase 4 Plan 03 Rule-1 auto-fix). `pandas dt.year` returns int32; Pydantic row models declare int64. Cast explicitly in RO rollups.
- **TDD RED → GREEN commit discipline** (Phase 4 Plans 01/03/07). Scraper tests land in RED first where pragmatic.
- **importlib.import_module() bypass** for cross-module attribute shadowing (Phase 4 Plan 07). If RO tests need to import `schemes.ro._refresh` alongside `schemes.ro.refresh` alias, use `importlib.import_module()`.
- **Spec-precedence discipline** (Phase 2 Plan 05 Task 0 + `project_spec_source.md` user memory). ARCHITECTURE.md + RO-MODULE-SPEC.md win where they conflict with ROADMAP. Relevant because RO-MODULE-SPEC.md §10 risks pre-date the portal-scope decisions.

### Integration Points

- **`counterfactual.METHODOLOGY_VERSION` → RO Parquet column → `manifest.json::methodology_version`** — Phase 4 D-12 chain completes for a second scheme. RO Parquet rows inherit the column automatically through `compute_counterfactual()`.
- **`mkdocs build --strict`** — Permanent CI gate (Phase 3). New `docs/schemes/ro.md` + nav entry must produce zero warnings.
- **`.github/workflows/refresh.yml`** — Daily cron at 06:00 UTC; runs `refresh_all.py`. After RO registration, daily refresh includes Ofgem dirty-check. Per-scheme SHA short-circuit (D-18) keeps noisy commits away when Ofgem hasn't published.
- **`.github/workflows/deploy.yml`** — On tag push, `snapshot.py` emits RO grains alongside CfD; all uploaded as release assets. No workflow change needed.
- **`docs/data/index.md`** — Journalist/academic entry point; works unchanged for RO (per Phase 4 D-27 — snippets iterate on manifest.json, not scheme-specific).
- **`docs/about/corrections.md` + `correction` label** — RO scheme correction channel inherits automatically.
- **`CHANGES.md ## Methodology versions`** — Continues to be the log where `DEFAULT_CARBON_PRICES` extension is recorded (D-05).

### Known pre-existing considerations

- **`METHODOLOGY_VERSION` is `"0.1.0"`** in `counterfactual.py`. D-06 preserves this; extension of `DEFAULT_CARBON_PRICES` is additive and does not bump the string. Phase 6+ is when 1.0.0 lands.
- **`schemes/` namespace exists** (Phase 4 Plan 03). RO is the second entry.
- **`schemas/` namespace exists** (Phase 4 Plan 03). `schemas/ro.py` is new.
- **`data/raw/ofgem/` does not exist yet.** `data/raw/lccc/`, `data/raw/elexon/`, `data/raw/ons/` do (Phase 4 D-04 migration). Creating `data/raw/ofgem/` + sidecars for the 3 new files is an atomic commit per D-04 discipline.
- **No `docs/schemes/` directory exists yet.** RO is the pattern establisher; Phase 7 (FiT) follows verbatim.
- **No `docs/charts/ro/` directory exists.** Per D-15, not creating one in Phase 5 (scheme-level page is GOV-01 unit).
- **Plotly chart HTML + PNG are gitignored** in `docs/charts/html/`; regenerated by the daily refresh. RO outputs follow same rule.
- **`refresh.yml` has no RO PR-failure context yet.** Plan may need a PR-body note that cron includes RO from Phase 5 onward so reviewers expect the extra diff columns in `manifest.json`.

</code_context>

<specifics>
## Specific Ideas

- **"The scheme you've never heard of, twice the size of the one you have"** — RO-MODULE-SPEC.md §11 Phase E publication quote. The rhetorical payload for `docs/schemes/ro.md`'s headline paragraph (Phase 3 D-01 "adversarial-payload-first" pattern applied at scheme-page level). Land this verbatim (or close) in the first 3 lines of `docs/schemes/ro.md`.
- **"Short-circuit R1 by deferring to the regulator"** — D-01's Ofgem-primary rocs_issued strategy is the most adversarial-proof option available; it means the biggest methodology risk in RO-MODULE-SPEC.md §10 lands on Ofgem's certification rather than on our YAML. The YAML still exists (for audit cross-check) so we haven't hollowed out the transparency story.
- **"Every component visible, no component hidden"** — D-12 headline strategy. £X bn all-in, with breakdown bullets (cofiring, mutualisation, NIRO-excluded) in the same paragraph. Readers who disagree with any component can filter the Parquet and regenerate their own total — the adversarial-proofing principle made concrete on the scheme page.
- **"Parquet is the audit trail"** — station_month.parquet carries ~500k rows × ~18 columns covering country, technology, obligation_year, rocs_issued, banding_factor (computed), ofgem_rocs_issued (published), ro_cost_gbp (buyout+recycle), ro_cost_gbp_eroc (sensitivity), ro_cost_gbp_nocarbon (sensitivity), gas_counterfactual_gbp, premium_gbp, mutualisation_gbp. Researcher can pivot the all-in figure any way they want in <5 SQL lines.
- **"Turver defines the acceptance test"** — RO-06's 3% tolerance is our public commitment to numerical accuracy. If we can't replicate Turver's published totals within 3%, the project's core value ("every headline number reproducible") is unproven for RO. Hence D-14's hard block.
- **Chart file naming convention** — RO-MODULE-SPEC.md Appendix A already specifies: `subsidy_ro_dynamics_twitter.png`, `subsidy_ro_by_technology_twitter.png`, etc. Preserve verbatim; enables Phase 3's Cost/Recipients theme gallery grids to treat RO equivalents consistently with CfD.
- **Grain naming is snake_case, one table per grain** (ARCHITECTURE §4.2 + Phase 4 D-07). `station_month.parquet`, `annual_summary.parquet`, `by_technology.parquet`, `by_allocation_round.parquet`, `forward_projection.parquet`. Cross-scheme consistency matters from Phase 6 onward when X1/X2/X3 read multi-scheme grains side-by-side.

</specifics>

<deferred>
## Deferred Ideas

- **Combined CfD + RO flagship chart** (RO-MODULE-SPEC.md §3 "chart 5" — `subsidy_combined_cfd_ro_twitter.png`). This IS the X1 + X2 cross-scheme stacked chart; belongs in Phase 6 per ROADMAP. **Explicit scope guardrail applied** — Phase 5 ships single-scheme RO; Phase 6 ships the cross-scheme combined view.
- **Portal homepage with three headline cards + 2×4 scheme grid** — Phase 6 (PORTAL-01/02).
- **FiT (Feed-in Tariff) module** — Phase 7. No `fit/` stub in Phase 5.
- **Per-chart D-01 six-section pages under `docs/schemes/ro/`** — Scheme-level page is GOV-01 unit for now (D-15). Per-chart pages added if research surfaces need OR if scheme grid in Phase 6 requires individual chart URLs as link targets.
- **Aggressive chart-code refactor** into scheme-parametric shared helpers — D-16 defers this to Phase 6 when X-charts force shared infrastructure.
- **METHODOLOGY_VERSION bump to 1.0.0** — Phase 6+ portal launch milestone event (D-06).
- **Zenodo DOI registration** — V2-COMM-01, triggers after Phase 5 lands (post-phase operational step, not scoped in Phase 5).
- **Pre-publication email to Turver** (RO-MODULE-SPEC.md §11 Phase E) — Courtesy outreach after publication; out of Phase 5 scope.
- **`docs/data/ro.md` per-scheme data page** — `docs/data/index.md` snippets work unchanged for RO (Phase 4 D-27 design). Add only if reader feedback warrants.
- **NIRO-first or UK-total headlines** — D-09 picks GB-only headline; NIRO data in Parquet available for filter. Revisit after Phase 5 ships if readers demand the UK-wide framing.
- **`fit/` stub directory** — RO-MODULE-SPEC.md §10 R8 suggested a stub now for future FiT; superseded by Phase 7's full FiT module.
- **OY-axis charts** (obligation year rather than calendar year) — D-07 picks CY throughout. OY-axis chart added only if reader feedback demands.
- **Cloudflare R2 for oversized raw files** — RO register XLSX estimated ≤100MB; first becomes relevant in Phase 8 NESO BM half-hourly data.

### Reviewed Todos (not folded)

No pending todos from STATE.md matched Phase 5 — `todo match-phase 5` returned zero matches. STATE.md todos left unclosed (LCCC ARA CY transcription, GitHub PR permission, `daily-refresh`/`refresh-failure` label creation) remain deferred to their originating phases or user setup.

</deferred>

---

*Phase: 05-ro-module*
*Context gathered: 2026-04-22*
