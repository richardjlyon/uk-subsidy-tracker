# Phase 6: Flagship Cross-Scheme Charts — Context

**Gathered:** 2026-04-25
**Status:** Ready for planning

---

<domain>
## Phase Boundary

Ship the portal homepage and the cross-scheme aggregation layer that drives it. Phase 6 makes the full-scheme cost argument visible for the first time on the portal, with two of eight schemes fully reconstructed (CfD + RO) and the remaining six tiles preserved as `Coming in Phase N` placeholders inherited from Phase 05.1.

**In scope:**

- **New cross-scheme derived layer.** `data/derived/portal/cross_scheme.parquet` — long-format `year | scheme | cost_gbp | premium_gbp | generation_mwh | households_uk | methodology_version`. One row per scheme-year. Joins all shipped scheme `annual_summary.parquet` files into a single canonical cross-scheme table. CSV mirror published alongside; `manifest.json` gains a `portal` scheme entry with full provenance (source URL, retrieval timestamp, sha256, pipeline git SHA, methodology version) — same shape as `cfd` + `ro` entries.
- **Five flagship cross-scheme charts** (X-01 through X-05 per REQUIREMENTS.md):
  - **X1** — Total UK subsidy stacked by scheme, annual. Plotly native `rangeselector` buttons (1y / 5y / All) on the interactive HTML; Twitter-PNG hero shows All-time view. Stacks only schemes with full reconstruction (CfD + RO today); chart subtitle reads "Covers 2 of 8 schemes — see scheme grid for coverage status."
  - **X2** — Combined premium over gas, cumulative.
  - **X3** — Cost per household, decomposed by scheme. Per-household division uses ONS UK-households count (planner sources via `constants.yaml`).
  - **X4** — Cost per MWh of subsidised generation by scheme. Schemes without a gas counterfactual (Capacity Market, Balancing, Grid Socialisation) are omitted with explicit footnote pointing to `docs/portal/methodology.md`.
  - **X5** — 2022 crisis comparison: vertical bar chart, x-axis = scheme, three grouped bars per scheme for 2021 / 2022 / 2023 premium-per-MWh. Schemes without gas counterfactual omitted with the same footnote.
  - All five follow the Twitter-PNG hero + `[Interactive version](path.html){target="_blank"}` embed pattern.
- **New `docs/portal/` documentation tier** with one D-01 six-section narrative page per X-chart (`x1-stacked-total.md`, `x2-cumulative-premium.md`, `x3-per-household.md`, `x4-cost-per-mwh.md`, `x5-2022-crisis.md`) plus a shared `docs/portal/methodology.md` covering cross-scheme aggregation rules, scheme-year vs calendar-year reconciliation, no-counterfactual exclusions, and the partial-coverage caveat. Each X-chart page carries full GOV-01 four-way coverage (narrative + methodology + test + chart-source-file link).
- **Portal homepage retrofit (`docs/index.md`)** — three new headline cards above the existing scheme grid:
  - `[GBPN.NN bn] Total subsidy (latest scheme year)` — covered-only total (CfD + RO) for the latest fully-reconciled scheme year.
  - `[GBPN.NN bn] Premium over gas (latest scheme year)` — covered-only premium total.
  - `[GBPNN] Per household (latest scheme year)` — covered-only per-household figure (cost / ONS UK households).
  - Caveat line beneath the cards: "Covers 2 of 8 schemes; full coverage in Phases 7-12."
  - X1 hero embed (Twitter PNG + Interactive HTML link with native rangeselector tabs) sits between the headline cards and the existing 2×4 scheme grid.
  - 2×4 scheme grid carries forward from 05.1: CfD + RO tiles populated with hardcoded headline figures (regression-test-anchored); six placeholder tiles unchanged ("Coming in Phase 7" through "Coming in Phase 12" with brief description, no headline number, non-clickable text).
- **PORTAL-02 tile clickthrough.** Populated tiles (CfD, RO) link to `schemes/cfd.md` / `schemes/ro.md` via the 05.1 D-03 anchor convention. No clickthrough on placeholder tiles.
- **Headline-sync regression test.** `tests/test_headline_sync.py` (single test file covering all surfaces) asserts that prose figures in `docs/index.md`, `docs/schemes/cfd.md`, and `docs/schemes/ro.md` match `cross_scheme.parquet` and per-scheme `annual_summary.parquet` totals to 1 decimal place. Failing test = update prose, run mkdocs --strict, commit. Generalises the Phase 05.2 ro.md headline-sync precedent across all surfaces.
- **Test discipline for the cross-scheme substrate:**
  - `tests/test_aggregates.py::test_cross_scheme_row_conservation` — sum of `cross_scheme.parquet[cost_gbp]` filtered by scheme-year equals each scheme's `annual_summary.parquet[year, total]` to fixed tolerance.
  - `tests/test_benchmarks.py::test_ref_total_reconciliation` — total UK subsidy approaches REF Constable's GBP25.8bn aggregate within phase-appropriate tolerance. With only 2 of 8 schemes populated, this cannot fire as a hard-block; documented tolerance covers the coverage gap and re-arms automatically as Phase 7-12 schemes ship.
  - Determinism (Phase 4 D-21 discipline) inherited: same scheme parquets in → byte-identical `cross_scheme.parquet` out.
- **Portal scheme module conforming to ARCH §6.1.** `src/uk_subsidy_tracker/schemes/portal/` exposes the five-function contract (`upstream_changed`, `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`) — `refresh()` is a no-op (downstream of all scheme refreshes), `rebuild_derived()` reads each scheme's `annual_summary.parquet` and emits `cross_scheme.parquet`, `regenerate_charts()` produces all five X-chart PNG/HTML artefacts. `refresh_all.SCHEMES` registers the portal module; runs after all scheme modules complete in cron order.
- **CHANGES.md `[Unreleased]`.** Full audit trail: Added (cross-scheme parquet, X-charts, portal homepage cards, docs/portal/ tier, headline-sync test); Changed (homepage layout). `## Methodology versions` entry only if METHODOLOGY_VERSION bumps.
- **`mkdocs build --strict`** passes with zero warnings post-commit. New `docs/portal/` nav entry added under MkDocs Schemes/Themes-adjacent position (planner picks ordering).

**Out of scope (belongs elsewhere):**

- **New scheme modules** (FiT, Constraints, Capacity Market, Balancing, Grid Socialisation, SEG) — Phases 7-12.
- **Updating placeholder scheme tiles with REF/Turver external estimates** — explicitly rejected; tiles stay "Coming in Phase N" until the scheme module ships and produces its own reproducible figure.
- **mkdocs-macros plugin / live binding** — explicitly rejected. Hardcoded prose + regression test is the discipline.
- **Quarterly batch update cadence** — explicitly rejected. Daily refresh + manual prose update via PR is the cadence.
- **Backend API, dynamic site features, JS build pipeline.**
- **Calendar-year to scheme-year normalisation as a project-wide axis.** Phase 6 reconciles CfD calendar-year and RO scheme-year (Apr-Mar) at the cross-scheme aggregation layer for the `latest fully-reconciled scheme year` headline; deeper axis-convention rationalisation across all eight schemes is deferred. `docs/portal/methodology.md` documents the current convention.
- **METHODOLOGY_VERSION bump 0.1.0 → 1.0.0.** Reserved for portal-launch milestone (Phase 5 D-06). Phase 6 plans may bump it as part of "portal launch" but the bump itself is a planner-level decision once headline numbers stabilise; not a gray area for this discussion.
- **Hard URL redirects for prior layouts** — `mkdocs build --strict` catches internal links; external redirects out of scope.
- **Three-headline-card auto-sourcing of REF GBP25.8bn full-UK aggregate as a co-display** — explicitly rejected (mixes our reconstruction with peer publisher's number; conflicts with Phase 05.2 D-15/D-16 clinical-anchor discipline).
- **Two-tier banner displaying 'reconstructed so far' + 'full UK estimate' side-by-side** — rejected for the same reason.
- **Live-binding via macros that update prose at every build** — rejected for risk of silent methodology drift without CHANGES.md audit (against Phase 2 D-07 + GOV-04).

</domain>

<decisions>
## Implementation Decisions

### Cross-scheme data substrate

- **D-01 New published `data/derived/portal/cross_scheme.parquet`.** Single canonical cross-scheme aggregation table joining all shipped scheme `annual_summary.parquet` files. All five X-charts read from this single file. Lands in `manifest.json` + CSV mirror. Phase-1 outcome: journalists download one table to do their own cross-scheme analysis; X-chart code becomes a thin plotting layer over the canonical join.
- **D-02 Long-format row schema.** `year | scheme | cost_gbp | premium_gbp | generation_mwh | households_uk | methodology_version`. One row per scheme-year. X1 sums by year; X2 takes cumulative premium; X3 divides cost by households; X4 divides cost by generation. Future-scheme additions (Phases 7-12) are append-only rows — no schema migration. `households_uk` carried per-row so X3's per-household figure is reproducible from the parquet alone. `methodology_version` per-row inherits Phase 4 D-08 / GOV-04 discipline.
- **D-03 Test discipline = row-conservation + REF benchmark cross-check (with phase-6 caveat).** `tests/test_aggregates.py::test_cross_scheme_row_conservation` asserts sum of `cross_scheme.parquet[cost_gbp]` filtered by scheme-year equals each scheme's `annual_summary.parquet[year, total]` to a fixed GBP-tolerance. `tests/test_benchmarks.py::test_ref_total_reconciliation` asserts total UK subsidy approaches REF Constable's GBP25.8bn aggregate within a coverage-gap-aware tolerance. With 2 of 8 schemes populated the REF test cannot fire as a hard-block; documented tolerance covers the gap and re-arms automatically as Phase 7-12 schemes ship. Determinism (Phase 4 D-21) inherited: same scheme parquets in → byte-identical `cross_scheme.parquet` out.
- **D-04 Single-row manifest entry.** `manifest.json` gains a `portal` scheme entry with `cross_scheme.parquet` + CSV mirror, source URL, retrieval timestamp, sha256, pipeline git SHA, methodology_version — same shape as `cfd` and `ro` entries. `publish/manifest.py` already iterates SCHEMES so registering `portal` as a scheme module via `refresh_all.SCHEMES` is low-friction. Cross-scheme totals are first-class downloadable artefacts; the principle "every number traceable to a downloadable file with provenance" extends to the cross-scheme layer.

### Headline scope + X1 horizon tabs

- **D-05 Three top headline cards show covered-only totals + 'partial coverage' caveat.** Cards display CfD + RO actual totals for the latest fully-reconciled scheme year, with a small caveat line beneath: "Covers 2 of 8 schemes; full coverage in Phases 7-12." Every number on the page is reproducible from the parquet pipeline. No mixing of REF aggregate or external estimates with our reconstruction. Coverage gap is visible feature, not hidden flaw — adversarial-proof posture.
- **D-06 Time slice = latest fully-reconciled scheme year.** Per ARCH §5.6 'this year' framing. `latest_fully_reconciled_year` is the most recent year for which both CfD and RO have validated `annual_summary.parquet` rows. Apr-Mar (RO) vs calendar-year (CfD) mismatch reconciled in `docs/portal/methodology.md` with a footnote on the cards. Phase-6 starting state: latest reconciled SY = 2022-23 (RO SY21) intersected with CfD CY 2023 — planner verifies as part of substrate work.
- **D-07 Plotly native rangeselector buttons in interactive HTML.** Single Plotly figure with `rangeselector` buttons (`1y` / `5y` / `All`) built into the chart. Twitter-PNG hero shows All-time view. Interactive HTML link carries the tabs natively. Zero MkDocs config; matches existing PNG-hero + Interactive-link embed pattern from RO/CfD pages; no JS build pipeline. Tabs only function in the interactive view — accepted tradeoff (Twitter PNG = static hero; interactive HTML = full functionality).
- **D-08 Unshipped schemes omitted from X1 stack with caveat in chart subtitle.** X1 stacked chart shows only CfD + RO bands today; chart subtitle reads "Covers 2 of 8 schemes — see scheme grid for coverage status." As Phases 7-12 ship, new bands appear automatically (cross_scheme.parquet append-only; chart re-renders on regenerate_charts). Every visible band is real reconstructed data; no greyed-out 'data pending' bands; no REF benchmark line on the chart.

### Headline-figure binding

- **D-09 Hardcoded markdown + regression test.** Headline figures live as plain text in `docs/index.md`, `docs/schemes/cfd.md`, and `docs/schemes/ro.md`. `tests/test_headline_sync.py` reads the parquet pipeline and asserts each prose figure matches to 1 decimal place. Failing test = update prose, run mkdocs --strict, commit. Generalises the Phase 05.2 ro.md headline-sync precedent. No mkdocs-macros plugin; no build-time substitution; no jinja templating layer. Cheap, test-anchored, debuggable.
- **D-10 Six placeholder scheme tiles keep current 'Coming in Phase N' labels, no headline figure.** Tiles show scheme name + `Coming in Phase 7` (FiT), 8 (Constraints), 9 (Capacity Market), 10 (Balancing), 11 (Grid), 12 (SEG) + brief description. No headline number on placeholder tiles. Tiles are non-clickable text. Phase 6 carries the 05.1 D-10 pattern forward unchanged for placeholders. Zero adversarial-proof exposure; no estimates from external sources sit on our page; conforms to Phase 05.2 D-15/D-16 clinical-anchor discipline.
- **D-11 Single regression test covers all surfaces.** `tests/test_headline_sync.py` asserts: (a) homepage card numbers, (b) cfd.md headline numbers (`GBP29bn` paid + `GBP14bn` premium), (c) ro.md headline numbers (`GBP58.6bn` covered + `GBP65-70bn` range), (d) `cross_scheme.parquet` totals, (e) per-scheme `annual_summary.parquet` totals — all consistent to 1 decimal place. Single source of truth; one test; one place to diagnose drift. Failures localise to "which prose surface drifted from which parquet". Future-scheme docs add a parametrised entry, not a new test file.
- **D-12 Cadence = every refresh + manual prose update via PR.** Daily `refresh.yml` cron updates parquets + `manifest.json` automatically. Prose headline updates happen in a separate human-reviewed PR triggered by the regression test going red. Humans review each headline change; supports CHANGES.md `## Methodology versions` discipline; no surprise prose changes under cron. Small lag between data refresh and prose refresh accepted as the cost of audit-anchored prose.

### X4/X5 scope + placement

- **D-13 Ship all five X-charts in Phase 6.** Honour ROADMAP Phase 6 SC#3 — X1, X2, X3, X4, X5 all land in Phase 6. ARCH §11 P5's 'X1/X2/X3 only' wording predates the ROADMAP refinement; ROADMAP is the active phase contract. Phase boundary stays clean: 'flagship cross-scheme charts' delivered as a complete set; REQUIREMENTS.md X-04/X-05 don't bleed into Phase 7+. Bigger phase scope accepted; X4/X5 polish degrees of freedom captured in Claude's Discretion below.
- **D-14 New `docs/portal/` directory with one page per X-chart.** Files: `docs/portal/x1-stacked-total.md`, `x2-cumulative-premium.md`, `x3-per-household.md`, `x4-cost-per-mwh.md`, `x5-2022-crisis.md`. Each follows D-01 six-section template (per Phase 3 D-01) with full GOV-01 four-way coverage. Shared `docs/portal/methodology.md` documents cross-scheme aggregation rules, scheme-year vs calendar-year reconciliation, no-counterfactual scheme exclusions, and the partial-coverage caveat. New IA tier matches ARCH §5.4's 'cross-scheme portal' bucket (the implicit sixth theme). Nav: planner adds `Portal` (or `Cross-scheme analysis`) section to `mkdocs.yml`, position planner-decided.
- **D-15 X5 shape = vertical bar chart, per-scheme premium 2022 vs adjacent years.** X-axis = scheme (CfD, RO, [+ later schemes as they ship]); each scheme has 3 grouped bars for 2021 / 2022 / 2023 premium-per-MWh. Visualises "did the scheme work in the crisis year?" per scheme at a glance. Reproduces the cfd.md "7% more in 2022" insight cross-scheme. Schemes without gas counterfactual omitted with footnote (D-16).
- **D-16 X4 + X5 omit schemes without gas counterfactual + footnote.** Capacity Market, Balancing, Grid Socialisation excluded from X4 + X5 visualisations once those modules ship (Phases 9-11). Footnote on each chart: "Schemes without a gas counterfactual (CM, Balancing, Grid) are excluded from this view; see methodology." Methodologically clean; matches ARCH §5.3 'modified S2 for CM' treatment. Risk of incomplete cross-scheme picture for those visualisations accepted in exchange for clean methodology. Re-evaluate in Phase 9-11 if the exclusion creates reader confusion.

### Claude's Discretion

- **Portal scheme module shape.** ARCH §6.1 contract demands five functions — `upstream_changed`, `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`. `src/uk_subsidy_tracker/schemes/portal/` planner-decided shape: `__init__.py` (contract entry points) + `cross_scheme_model.py` (the join logic) + module-level constants for households-count + scheme order. `refresh()` is effectively a no-op (the portal module is downstream of all scheme refreshes); `upstream_changed()` returns true when any scheme's `annual_summary.parquet` mtime is newer than `cross_scheme.parquet`. Planner verifies fit with existing `refresh_all.SCHEMES` registration order — portal module runs **after** all scheme modules complete.
- **`docs/portal/methodology.md` depth.** Matches `docs/methodology/gas-counterfactual.md` precedent — 5-10 paragraphs covering: (i) cross-scheme aggregation join semantics; (ii) scheme-year vs calendar-year reconciliation rule; (iii) the no-gas-counterfactual exclusion list (CM, Balancing, Grid) and why; (iv) per-household division convention (ONS households-count source + which year's count for which scheme-year); (v) partial-coverage caveat language and how the regression test re-arms as new schemes ship; (vi) clinical reference to REF Constable / Turver as test-file tolerance anchors only (per Phase 05.2 D-15/D-16). Length and section structure planner-decided.
- **Households-count constant source.** `constants.yaml` entry `uk_households` populated from ONS published table (planner sources URL + sha256 + retrieved_on per Phase 4 SEED-001 Tier 2 constants drift discipline). Likely ONS Annual Population Survey or census; planner picks the canonical source. Either single-value (latest) or per-year time series — planner picks. Per-year preferred for X3 historical accuracy.
- **`latest_fully_reconciled_year` precise definition.** Planner-decided: most recent `year` for which both CfD and RO `annual_summary.parquet` rows pass schema validation AND the value is a "complete" year (not a partial-current-year settlement). Edge case: if CfD has 2024 partial data and RO has 2023 final, latest reconciled = 2023. Planner specifies the rule in `docs/portal/methodology.md`.
- **REF benchmark tolerance for partial-coverage phase.** D-03 says `test_ref_total_reconciliation` runs with a coverage-gap-aware tolerance during Phase 6 (2 of 8 schemes). Planner picks the tolerance shape: (a) document expected_ratio = 2/8 with ±N% headroom, (b) compute lower-bound = sum of REF entries for CfD + RO only, (c) skip the test entirely until coverage > 70% with `@pytest.mark.skip(reason="partial coverage; re-arms in Phase N")`. Recommend (b) — REF Constable Table 1 transcribes per-scheme; cross-checking CfD + RO subsets against REF's CfD + RO entries is methodologically cleaner than a coverage-fraction estimate.
- **mkdocs.yml nav placement of the Portal tier.** Planner decides where the new `docs/portal/` section sits in nav: top-level `Portal` tab, sub-section under existing `Schemes` tab, or sub-section under existing `Themes` tab. ARCH §5.4 puts cross-scheme charts in their own bucket which suggests top-level. Cross-scheme symmetry principle: readers learn the X-chart reading pattern once, same as scheme pages.
- **Atomic-commit slicing.** Planner decomposes Phase 6 into waves per Phase 1 D-16 discipline. Suggested grouping: (W1) `schemes/portal/` module + cross_scheme_model.py + cross_scheme.parquet emission + manifest registration + test_aggregates row-conservation; (W2) X1/X2/X3 plotting modules + Twitter PNG + interactive HTML (Plotly rangeselector for X1); (W3) X4/X5 plotting modules; (W4) `docs/portal/` directory + 5 X-chart narrative pages + methodology.md; (W5) `docs/index.md` retrofit (3 headline cards + X1 hero + caveat) + scheme tile headline figures hardcoded; (W6) `tests/test_headline_sync.py` + cross-page sync; (W7) REF reconciliation test + tolerance + CHANGES.md + mkdocs --strict gate.
- **Methodology version bump.** Planner decides whether Phase 6 portal-launch warrants a `METHODOLOGY_VERSION` bump 0.1.0 → 1.0.0 (per Phase 5 D-06 deferral). If bumped, full audit trail in CHANGES.md `## Methodology versions` per Phase 2 D-07 + GOV-04. Recommend bump iff the cross-scheme aggregation join introduces any methodology rule not already captured in per-scheme `counterfactual.METHODOLOGY_VERSION`. If pure substrate-and-presentation, hold at 0.1.0.

### Folded Todos

No pending todos from STATE.md matched Phase 6 (`gsd-tools todo match-phase 6` returned 0 matches).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Authoritative spec

- `ARCHITECTURE.md` §5.4 — Cross-scheme / portal integration charts (X1-X5 catalogue with theme + audience + priority). Substrate for scope decision D-13.
- `ARCHITECTURE.md` §5.6 — Portal top strip (iamkate pattern). ASCII layout for 3 headline cards + X1 hero + 2×4 scheme grid + theme nav. Substrate for D-05 / D-06 / D-07 / D-10.
- `ARCHITECTURE.md` §6.1 — Scheme-module contract (5 functions: `upstream_changed`, `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`). Load-bearing template for `schemes/portal/` per D-Claude's Discretion.
- `ARCHITECTURE.md` §11 P5 — Original Phase 6 deliverables (X1/X2/X3 + portal strip + scheme grid). Wording predates ROADMAP refinement; ROADMAP supersedes per D-13.
- `ARCHITECTURE.md` §4.2 — Derived layer discipline (Pydantic schemas + Parquet + per-row provenance). Substrate for `cross_scheme.parquet` schema decision D-02.
- `ARCHITECTURE.md` §4.3 — Publishing layer discipline (manifest.json provenance, CSV mirror). Substrate for D-04.
- `ARCHITECTURE.md` §9.4 — Methodology versioning (`methodology_version` column + CHANGES.md ## Methodology versions). Substrate for D-02 + D-Claude's Discretion (version bump).

### Roadmap + requirements

- `.planning/ROADMAP.md` Phase 6 (lines 167-178) — 5 success criteria. SC#1 portal homepage (3 cards + X1 + scheme grid); SC#2 X1/X2/X3 PRODUCTION with narrative + methodology; SC#3 X4/X5 published; SC#4 scheme grid CfD + RO populated; SC#5 PORTAL-02 tile clickthroughs.
- `.planning/REQUIREMENTS.md` — X-01 through X-05 (cross-scheme charts), PORTAL-01 (homepage shape), PORTAL-02 (tile clickthroughs). All 7 requirements scoped to Phase 6 per Traceability table.
- `.planning/PROJECT.md` — Core value: every headline number reproducible from `git clone + uv sync + one command`. Adversarial-proofing as first-class concern. The cross-scheme aggregation table is now the largest single example of this principle in the project.

### Prior-phase context (locked decisions apply)

- `.planning/phases/05.1-cfd-scheme-page/05.1-CONTEXT.md` — **D-10 homepage 2×4 scheme grid is the substrate** Phase 6 builds on. D-03 H2 anchor convention (`#cost-dynamics-chart-s2` etc.) defines PORTAL-02 tile clickthrough targets. D-Claude's Discretion explicitly punts headline-figure data-binding to Phase 6 — D-09 of this phase resolves it.
- `.planning/phases/05.2-ro-data-reconstruction-aggregate-grain/05.2-CONTEXT.md` — **D-15/D-16 clinical-anchor discipline drives D-10 placeholder-tile decision** (no REF estimates on placeholders) and the explicit rejection of the "REF aggregate as headline truth" homepage-card variant. RO is aggregate-grain only (annual_summary + by_technology); cross_scheme aggregation reads RO at this grain. The ro.md headline-sync regression test is the **precedent for D-09/D-11**; Phase 6 generalises it.
- `.planning/phases/05-ro-module/05-CONTEXT.md` — D-12 "every component visible, no component hidden" headline strategy. Applied at homepage scope: covered totals + caveat, never partial figure that obscures the gap. D-15 8-section scheme page + GOV-01 4-way coverage discipline carries to `docs/portal/` X-chart pages.
- `.planning/phases/04-publishing-layer/04-CONTEXT.md` — Three-layer pipeline (raw → derived → site/data). `cross_scheme.parquet` lands in `data/derived/portal/`; published via existing `publish/manifest.py` + `publish/csv_mirror.py`. D-21 deterministic-rebuild discipline applies. SEED-001 constants drift test pattern (Plan 04-01) is the template for adding `uk_households` to `constants.yaml`.
- `.planning/phases/03-chart-triage-execution/03-CONTEXT.md` — **D-01 six-section chart page template** applies to each X-chart's narrative page in `docs/portal/`. GOV-01 four-way coverage is the per-X-chart quality bar.
- `.planning/phases/02-test-benchmark-scaffolding/02-CONTEXT.md` — `_TOLERANCE_BY_SOURCE` dispatch pattern in `test_benchmarks.py`. REF reconciliation tolerance shape per D-Claude's Discretion. TDD RED → GREEN discipline applies.
- `.planning/phases/01-foundation-tidy/01-CONTEXT.md` — Material theme + `mkdocs build --strict` permanent CI gate + Keep-a-Changelog `CHANGES.md` with `## Methodology versions` section + atomic-commit discipline (D-16).

### Pattern-setting documents (read before planning)

- `docs/schemes/ro.md` + `docs/schemes/cfd.md` — Scheme-page templates. Headline-figure prose patterns + 4-chart embed convention + GOV-01 four-way coverage block + Headline FAQ section. The `docs/portal/` X-chart pages mirror the per-chart 6-section template (Phase 3 D-01) rather than the scheme-page 8-section template (Phase 05.1 D-02).
- `docs/index.md` — Current homepage. 2×4 scheme grid + theme nav + journalist card + status section already in place from Phase 05.1. Phase 6 adds 3 headline cards + X1 hero above the scheme grid; preserves the rest.
- `docs/methodology/gas-counterfactual.md` — Methodology-page depth + structure precedent for `docs/portal/methodology.md`.
- `docs/data/index.md` — Journalist/academic entry point (Phase 4 PUB-04). Updates incidentally — `manifest.json` gains a `portal` entry; the page documents how to download `cross_scheme.parquet`.

### External references (clinical anchors only)

- **REF Constable 2025 "Renewable Subsidies"** — `tests/fixtures/benchmarks.yaml::ref_constable` already carries the per-scheme entries. `test_ref_total_reconciliation` cross-checks the CfD + RO subset against REF's matching entries during Phase 6. Cited clinically as a tolerance anchor only per Phase 05.2 D-15/D-16; **not linked from `docs/index.md` or `docs/portal/*.md` as peer publisher**. URL: `https://ref.org.uk/attachments/article/390/renewables.subsidies.01.05.25.pdf`.
- **ONS UK households-count** — Planner sources canonical URL + sha256 + retrieved_on as part of `constants.yaml` `uk_households` entry. Likely ONS Annual Population Survey or census tables.
- **iamkate.com/grid** — `https://grid.iamkate.com/` — Design-pattern reference cited in ARCH §5.6. Already linked from `ARCHITECTURE.md`; Phase 6 implementation faithful to the adapted pattern.

### Files to modify

- `docs/index.md` — Insert 3 headline cards + caveat + X1 hero (Twitter-PNG + interactive-HTML link with rangeselector tabs) above the existing 2×4 scheme grid. Scheme tile headline figures (CfD + RO) updated to reflect `latest fully-reconciled scheme year` figures from `cross_scheme.parquet`. 6 placeholder tiles unchanged.
- `mkdocs.yml` — Add `Portal` (or `Cross-scheme analysis`) nav section with 5 X-chart pages + methodology page. Position planner-decided.
- `CHANGES.md` `[Unreleased]` — Audit trail per the in-scope list above.
- `.planning/REQUIREMENTS.md` — Mark X-01..X-05, PORTAL-01, PORTAL-02 as Complete on phase close. Traceability table updates.

### Files to create

- `src/uk_subsidy_tracker/schemes/portal/__init__.py` — §6.1 contract entry points (no-op refresh; `rebuild_derived` calls cross-scheme model; `regenerate_charts` produces all five X-charts; `validate` checks row-conservation).
- `src/uk_subsidy_tracker/schemes/portal/cross_scheme_model.py` — Long-format join logic over each shipped scheme's `annual_summary.parquet`.
- `src/uk_subsidy_tracker/schemas/portal.py` (or extend existing schemas) — Pydantic row model for `cross_scheme.parquet` per D-02.
- `src/uk_subsidy_tracker/plotting/portal/x1_stacked_total.py`, `x2_cumulative_premium.py`, `x3_per_household.py`, `x4_cost_per_mwh.py`, `x5_2022_crisis.py` — Plotting modules. X1 uses Plotly `rangeselector` per D-07.
- `src/uk_subsidy_tracker/data/constants.yaml` — Extend with `uk_households` entry (planner sources from ONS).
- `data/derived/portal/cross_scheme.parquet` + `cross_scheme.schema.json` + sidecar — Emitted by `rebuild_derived()`.
- `docs/portal/x1-stacked-total.md`, `x2-cumulative-premium.md`, `x3-per-household.md`, `x4-cost-per-mwh.md`, `x5-2022-crisis.md` — D-01 six-section narrative pages with full GOV-01 coverage.
- `docs/portal/methodology.md` — Cross-scheme aggregation methodology per D-Claude's Discretion.
- `tests/test_headline_sync.py` — Single test file covering homepage + scheme-page + parquet consistency per D-11.
- `tests/test_aggregates.py` — Add `test_cross_scheme_row_conservation` parametrisation.
- `tests/test_benchmarks.py` — Add `test_ref_total_reconciliation` with phase-6 coverage-gap tolerance per D-Claude's Discretion.
- `tests/test_determinism.py` — Add `cross_scheme.parquet` parametrisation.
- `tests/test_schemas.py` — Add `cross_scheme.parquet` schema validation parametrisation.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`src/uk_subsidy_tracker/schemes/cfd/` + `schemes/ro/`** — §6.1 contract templates. `schemes/portal/` mirrors their shape with `refresh()` as a no-op (downstream of all scheme refreshes) and `rebuild_derived()` reading each scheme's `annual_summary.parquet` rather than scraping upstream sources. The pattern of returning early when upstream is unchanged (Phase 5 `upstream_changed` discipline) carries over: portal `upstream_changed()` returns true when any scheme `annual_summary.parquet` mtime is newer than `cross_scheme.parquet`.
- **`src/uk_subsidy_tracker/plotting/subsidy/` chart modules** — 11 chart modules already follow the Plotly `figure → ChartBuilder.save() → Twitter-PNG + interactive HTML + .div.html` pattern. X-chart modules in `plotting/portal/` (new directory) inherit this discipline. Plotly's `rangeselector` is a feature of `update_xaxes()` / `update_layout()` — no new infrastructure for X1's tabs (D-07).
- **`src/uk_subsidy_tracker/counterfactual.py`** — `compute_counterfactual()` + `DEFAULT_CARBON_PRICES` + `METHODOLOGY_VERSION` unchanged. Cross-scheme aggregation reads scheme parquets (which already carry `methodology_version`); `cross_scheme.parquet` propagates the field per-row.
- **`src/uk_subsidy_tracker/data/sidecar.py::write_sidecar()`** — Atomic sidecar writer. `cross_scheme.parquet` gets a sidecar on emission; `sources[]` field (introduced in Phase 05.2 D-03) optionally carries the per-scheme source chain — planner decides whether to use this or single `upstream_url` pointing back to scheme parquets.
- **`src/uk_subsidy_tracker/publish/manifest.py`** — Already iterates `refresh_all.SCHEMES` (Phase 05.2 multi-scheme refactor). Registering `portal` in `SCHEMES` auto-publishes the cross-scheme entry. Zero refactor needed.
- **`src/uk_subsidy_tracker/publish/csv_mirror.py`** — Auto-mirrors every published Parquet to CSV. Cross-scheme parquet inherits.
- **`src/uk_subsidy_tracker/publish/snapshot.py`** — On tag push, snapshots `site/data/v<date>/`. Cross-scheme parquet inherits.
- **`tests/fixtures/benchmarks.yaml::ref_constable`** — 22 RO entries already transcribed (Phase 5 Plan 05-09). REF Table 1 covers all 8 schemes — planner verifies which scheme entries beyond CfD + RO are present and uses the CfD + RO subset for `test_ref_total_reconciliation` per D-Claude's Discretion.
- **`tests/fixtures/benchmarks.yaml`** — General fixture-loader infrastructure (Pydantic) supports per-source tolerance dispatch (Phase 02 D-07 `_TOLERANCE_BY_SOURCE`).
- **`tests/test_benchmarks.py`** — Already runs `test_ref_constable_ro_reconciliation` as a hard CI block (post-Phase 05.2 sentinel delete). New `test_ref_total_reconciliation` joins it as a sibling, with phase-6-aware tolerance.
- **`tests/test_aggregates.py`** — Row-conservation discipline already in place for per-scheme grains (Phase 4). Cross-scheme parametrisation extends the same pattern.
- **`docs/schemes/ro.md` + `docs/schemes/cfd.md`** — Headline-prose precedent for D-09/D-11 regression test. Phase 05.2 ro.md already has a headline-sync test; D-11 generalises.
- **`docs/themes/cost/index.md` lines 9-59** — Material `grid cards` extension demonstration. The 3 headline cards on the homepage reuse this pattern (matching Phase 05.1 D-10).

### Established Patterns

- **Atomic commits per concern** (Phase 1 D-16). Suggested wave structure per D-Claude's Discretion.
- **TDD RED → GREEN** where pragmatic (Phase 4 Plans 01/03/07). Cross-scheme model + headline-sync test land RED first.
- **Twitter-PNG hero + Interactive HTML link embed pattern** (Phase 05.1 D-05, RO/CfD pages). All five X-charts follow it.
- **Loader-owned pandera validation** — Cross-scheme model carries `.validate()` inside the rebuild path.
- **Provenance: docstring discipline** (user memory `constant_provenance_pattern.md`) — `uk_households` constant in `constants.yaml` carries a per-row Provenance: block + sidecar `sources[]` entry.
- **Deterministic rebuild discipline** (Phase 4 D-21). Same scheme parquets in → byte-identical `cross_scheme.parquet` out. Sort order is canonical (`year` ASC, `scheme` ASC).
- **Internal artefacts off public docs** (user memory `feedback_internal_artefacts_off_public_docs.md`). REF / Turver named clinically as test-file tolerance anchors only; no peer-publisher framing on `docs/index.md` or `docs/portal/*.md` (D-10 + D-Claude's Discretion methodology depth).
- **Headline-sync regression discipline** (Phase 05.2 ro.md precedent). Generalised to all surfaces in D-11.

### Integration Points

- **`refresh_all.SCHEMES`** — Add `schemes.portal` after all per-scheme entries. Run-order: scheme refreshes → scheme rebuilds → portal rebuild → publish. Planner verifies the `refresh_all` orchestration handles this dependency cleanly.
- **`manifest.json`** — Auto-extends with `portal` entry via `publish/manifest.py` iteration over SCHEMES (Phase 05.2 multi-scheme refactor). No code change needed.
- **`CSV mirror`** — `publish/csv_mirror.py` writes `cross_scheme.csv` alongside `cross_scheme.parquet`.
- **`mkdocs build --strict`** — Permanent CI gate. New `docs/portal/` directory + 5 X-chart pages + methodology page + nav entries must pass without warnings.
- **`.github/workflows/refresh.yml`** — Daily 06:00 UTC cron. After D-04, RO + CfD + portal rebuilds chain in registered order. Per-scheme dirty-check still applies; portal rebuild fires only if any upstream `annual_summary.parquet` changed.
- **`.github/workflows/deploy.yml`** — On tag push, `snapshot.py` emits `site/data/v<date>/portal/cross_scheme.parquet` alongside scheme parquets. No workflow change.
- **`docs/data/index.md`** — Journalist/academic entry point. Phase 6 adds a paragraph documenting the new `portal` scheme entry in `manifest.json` and how to download `cross_scheme.parquet`.
- **`docs/about/corrections.md` + `correction` label** — Cross-scheme corrections inherit the existing channel.

### Known pre-existing considerations

- **Apr-Mar (RO) vs calendar-year (CfD) scheme-year mismatch.** D-06 `latest fully-reconciled scheme year` reconciles at the cross-scheme aggregation layer; planner picks the precise rule (likely intersection of latest validated row in each scheme parquet) and documents in `docs/portal/methodology.md`.
- **RO covered total ≈ GBP58.6 bn (2006-17 + 2019-23); full 2002-2024 range ≈ GBP65-70 bn with SY1-SY4 + SY17 deferred per Phase 05.2.** D-09 headline-sync test handles both figures across `ro.md` + cross_scheme.parquet (the parquet rows for SY1-SY4 + SY17 are absent or null per Phase 05.2 dormancy discipline; cross-scheme aggregation respects this).
- **CfD GBP29 bn paid + GBP14 bn premium since 2015.** Carries forward unchanged from Phase 05.1.
- **`refresh.yml` workflow already handles per-scheme dirty-check** (Phase 4 GOV-03). Portal scheme module adds one more entry; the dirty-check generalises naturally.
- **Phase 05.2 deferred SY1-SY4 + SY17 + ROC e-roc clearing prices** — Surfacing in cross-scheme totals as missing rows. `cross_scheme.parquet` either omits (D-08 chart-level posture) or carries `null` `cost_gbp` for those years (planner picks). Either way, the headline-sync regression test must handle the gaps without false failures.
- **`docs/index.md` 'Status' section currently mentions "Two scheme modules are shipped"** — Phase 6 may update this language to reflect cross-scheme aggregation now exists; planner verifies.
- **No mkdocs-macros plugin in current `pyproject.toml`** — D-09 commits to NOT adding it. Confirm during planning.

</code_context>

<specifics>
## Specific Ideas

- **"Three big numbers, not one, not six"** (ARCH §5.6 iamkate adaptation). Three headline cards is the limit of human glance-comprehension. D-05 honours this; D-06 picks `latest fully-reconciled scheme year` as the time slice that gives all three cards meaning together.
- **"Every visible band is real"** (D-08). The X1 stacked chart never carries placeholder/grey/estimate bands. As Phases 7-12 ship, the chart literally grows — the visible chart-state IS the project's coverage state. Reader trust: what they see is what we reconstructed.
- **"Coverage gap as visible feature, not hidden flaw"** (D-05 caveat line). Adversarial-proofing: hostile readers can't accuse us of obscuring incomplete coverage when the homepage explicitly says so under each headline. The 6 placeholder tiles + caveat are the page's honesty signal.
- **"Hardcoded prose + regression test"** (D-09 / D-11). The Phase 05.2 ro.md headline-sync precedent generalises to a single test covering all surfaces. Cheap, debuggable, no plugin sprawl. Each refresh's prose update goes through human PR review — no silent number changes.
- **"Portal is the sixth implicit theme"** (D-14). ARCH §5.4 tags X-charts as 'Portal' bucket. `docs/portal/` directory makes this explicit in the IA. Readers learn 5 themes + 1 cross-scheme tier.
- **"Cross-scheme symmetry inherits from scheme symmetry"** (Phase 05.1 D-02). Each X-chart page mirrors the others; readers learn the X-chart reading pattern once. Same principle the scheme pages established.
- **"REF is a test-file tolerance anchor, not a co-publisher"** (Phase 05.2 D-15/D-16, user-memory `feedback_internal_artefacts_off_public_docs.md`). D-10 (no REF estimates on placeholder tiles) and D-Claude's Discretion (`docs/portal/methodology.md` clinical citation only) carry this discipline forward to the cross-scheme tier.
- **"Plotly natively supports range buttons"** (D-07). Static MkDocs deployment doesn't need a JS build pipeline for X1's tabs — Plotly's `rangeselector` already produces them in the interactive HTML. The Twitter-PNG hero is static (no tabs); accepting that tradeoff keeps the embed pattern consistent with every other chart on the site.

</specifics>

<deferred>
## Deferred Ideas

- **mkdocs-macros plugin / live-binding via macros** — Explicitly rejected in D-09. Revisit if hardcoded prose + regression test discipline becomes operationally painful (e.g., 8 schemes shipped with quarterly methodology refinements driving constant prose churn). Threshold: if 3+ separate refreshes within a month require coordinated prose updates across 8+ surfaces, reconsider macros.
- **Calendar-year vs scheme-year normalisation as a project-wide axis convention** — Phase 6 reconciles at the cross-scheme aggregation layer for the headline cards (D-06). Project-wide rationalisation across all 8 schemes deferred. Revisit when a scheme adopts an axis that doesn't fit either pattern (unlikely; Constraints + CM + Balancing are calendar-year by construction; FiT mirrors RO on Apr-Mar).
- **Live-binding via macros** — Revisit per the threshold above.
- **Three-tier headline display ('reconstructed' + 'full UK estimate' + 'gap')** — Rejected in D-05. Revisit when coverage > 70% and the gap becomes a footnote rather than a major feature of the page.
- **REF benchmark line on X1 chart** — Considered and rejected (D-08). Revisit only if the coverage-gap caveat in the chart subtitle proves insufficient — e.g., if reader feedback reports confusion about scale.
- **`@pytest.mark.skip` on `test_ref_total_reconciliation` until coverage > 70%** — Recommended option (b) in D-Claude's Discretion (lower-bound REF subset cross-check) is preferred. Skip only if the subset cross-check produces noisy false positives that aren't worth the test's signal value.
- **Per-technology decomposition on cross_scheme.parquet rows** — Rejected in D-02 (long-format with per-tech adds work for 4 of 5 X-charts that don't need it). Revisit if a Phase 7+ X-chart specifically requires cross-scheme tech comparisons (unlikely for X4/X5 shape decisions in D-15 / D-16).
- **mkdocs nav placement of Portal tier** — Planner-decided in Claude's Discretion. Revisit if user feedback suggests the placement obscures the cross-scheme charts' flagship framing.
- **METHODOLOGY_VERSION 0.1.0 → 1.0.0 bump** — Planner-decided in Claude's Discretion. Revisit at end of Phase 6 if cross-scheme methodology rules introduce anything not captured per-scheme.
- **External URL redirects** — Out of scope per Phase 05.1 D-09 precedent. Revisit if external referrers warrant.
- **Methodology page split** (one per X-chart vs one shared) — D-14 picks one shared `docs/portal/methodology.md`. Revisit if methodology depth grows beyond 10 paragraphs.
- **Headline-sync test parametrisation** — D-11 picks single test file. Revisit if test-fixture growth (Phase 7-12 schemes) makes the single file unwieldy; parametrise rather than splitting if growth is per-scheme rather than per-surface.

### Reviewed Todos (not folded)

No pending todos from STATE.md matched Phase 6 — `gsd-tools todo match-phase 6` returned 0 matches.

</deferred>

---

*Phase: 06-flagship-cross-scheme-charts*
*Context gathered: 2026-04-25*
