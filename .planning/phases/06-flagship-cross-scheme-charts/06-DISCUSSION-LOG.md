# Phase 6: Flagship Cross-Scheme Charts — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `06-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-04-25
**Phase:** 6 — Flagship Cross-Scheme Charts
**Areas discussed:** Cross-scheme data substrate, Headline scope + X1 horizon tabs, Headline-figure binding, X4/X5 scope + placement

---

## Cross-scheme data substrate

### Where should the X-charts read their cross-scheme inputs from?

| Option | Description | Selected |
|--------|-------------|----------|
| New published cross_scheme.parquet | New `data/derived/portal/cross_scheme.parquet` joining all shipped schemes; lands in manifest.json + CSV mirror | ✓ |
| Per-chart inline reads | Each X-chart's plotting module reads each scheme's annual_summary.parquet directly, joins in-memory | |
| Hybrid: in-memory join + publish a snapshot | Charts join in memory at build time, then write to site/data/portal/ as a publishing-layer artefact | |

**User's choice:** New published cross_scheme.parquet (Recommended)

### What's the canonical row schema for the cross-scheme aggregation?

| Option | Description | Selected |
|--------|-------------|----------|
| Year × scheme × cost + premium | Long format: `year \| scheme \| cost_gbp \| premium_gbp \| generation_mwh \| households_uk \| methodology_version` | ✓ |
| Wide format: one column per scheme | `year \| cfd_cost_gbp \| ro_cost_gbp \| ...` requires schema migration each scheme phase | |
| Long-format with per-technology decomposition | Long format AND tech-slice per row | |

**User's choice:** Year × scheme × cost + premium (Recommended)

### What test discipline pins the cross-scheme totals?

| Option | Description | Selected |
|--------|-------------|----------|
| Row-conservation in test_aggregates | sum-by-scheme equals per-scheme annual totals | ✓ |
| REF £25.8bn benchmark cross-check | Total approaches REF aggregate within phase-aware tolerance | ✓ |
| Determinism: same parquets in → byte-identical out | Phase 4 D-21 discipline applied | |
| Headline-binding regression test | Belongs to area 3's binding mechanism | |

**User's choice:** Row-conservation in test_aggregates + REF £25.8bn benchmark cross-check (multiSelect)

### How should the cross_scheme dataset be exposed to journalists/academics in manifest.json?

| Option | Description | Selected |
|--------|-------------|----------|
| Single-row entry like every other scheme | manifest.json gains a `portal` scheme entry, same shape as cfd/ro | ✓ |
| New manifest section: portal-aggregates | Distinguishes per-scheme from cross-scheme | |
| Internal-only: not in manifest.json | Computation substrate only; not exposed for download | |

**User's choice:** Single-row entry like every other scheme (Recommended)

---

## Headline scope + X1 horizon tabs

### With only 2 of 8 schemes populated (CfD + RO), what do the three top headline cards show?

| Option | Description | Selected |
|--------|-------------|----------|
| Covered-only totals + 'partial coverage' caveat | CfD + RO actuals + caveat line beneath cards | ✓ |
| REF £25.8bn aggregate as headline truth + reconstruction underneath | Mixes peer publisher's number with our reconstruction | |
| Two-tier banner: reconstructed + full UK estimate side-by-side | Three cards now mean different things | |
| Defer all three cards until more schemes ship | Phase 6 ships X1 + grid only; cards row empty | |

**User's choice:** Covered-only totals + 'partial coverage' caveat (Recommended)

### What time slice do the headline cards represent?

| Option | Description | Selected |
|--------|-------------|----------|
| Latest fully-reconciled scheme year | Most recent year for which both CfD and RO have validated data | ✓ |
| Cumulative since-inception (CfD 2015 / RO 2002) | Largest-possible numbers; harder per-household reasoning | |
| Last full calendar year | Jan-Dec; requires scheme-year-to-calendar-year bridging | |

**User's choice:** Latest fully-reconciled scheme year (Recommended)

### How are the X1 chart's 'Latest year / Last 5 years / All time' tabs implemented?

| Option | Description | Selected |
|--------|-------------|----------|
| Plotly native rangeselector buttons in interactive HTML | Single Plotly figure with built-in 1y/5y/All buttons | ✓ |
| pymdownx-tabbed with 3 PNGs | 3 separate PNGs in MkDocs Material tab block | |
| Hybrid: pymdownx-tabbed wraps interactive HTML iframes | 3 tabs each embedding a different Plotly HTML via iframe | |

**User's choice:** Plotly native rangeselector buttons in interactive HTML (Recommended)

### How do unshipped schemes (FiT/Constraints/CM/Balancing/Grid/SEG) render in the X1 stacked chart?

| Option | Description | Selected |
|--------|-------------|----------|
| Omit unshipped schemes; caveat in chart subtitle | Stack only CfD + RO bands; subtitle reads "Covers 2 of 8 schemes" | ✓ |
| Reserve grey 'data pending' bands for unshipped schemes | Each placeholder gets a benchmark estimate band hatched grey | |
| Show only schemes with full reconstruction; soft fade-in line for benchmark total | Add a thin REF benchmark line for scale | |

**User's choice:** Omit unshipped schemes; caveat in chart subtitle (Recommended)

---

## Headline-figure binding

### How should headline figures (homepage cards + scheme tile numbers) stay in sync with the parquet pipeline?

| Option | Description | Selected |
|--------|-------------|----------|
| Hardcoded markdown + regression test | Plain text in markdown; test asserts prose-matches-parquet to 1dp | ✓ |
| mkdocs-macros plugin reading manifest.json at build time | Macros resolve at build; live-bound | |
| Build-time jinja/sed substitution via uv script | Pre-build script substitutes placeholder tokens | |
| Mixed: macros for portal cards, hardcoded for scheme pages | Two patterns in one project | |

**User's choice:** Hardcoded markdown + regression test (Recommended)

### How are the 6 placeholder scheme tiles handled until each scheme module ships?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep current 'Coming in Phase N' label, no headline figure | Match current 05.1 homepage state; non-clickable text | ✓ |
| Add caveated REF-derived estimate | Each placeholder gets a number with REF caveat | |
| Link placeholder tiles to ROADMAP.md / a 'coming soon' page | Each placeholder is clickable; 6 stub pages | |

**User's choice:** Keep current 'Coming in Phase N' label, no headline figure (Recommended)

### What discipline keeps scheme-page headline figures (cfd.md, ro.md) consistent with the homepage cards?

| Option | Description | Selected |
|--------|-------------|----------|
| Single regression test covers all surfaces | One test asserts homepage + cfd.md + ro.md + parquets all consistent | ✓ |
| Per-page regression tests | Separate test files per page | |
| No cross-page sync test — manual review only | mkdocs --strict + visual review at each refresh | |

**User's choice:** Single regression test covers all surfaces (Recommended)

### What's the binding cadence — when do headline numbers update?

| Option | Description | Selected |
|--------|-------------|----------|
| Every refresh + manual prose update via PR | Daily cron updates parquets; prose updates in human-reviewed PR | ✓ |
| Live binding via macros — prose updates each build | Zero lag; risk of silent methodology drift | |
| Quarterly batch update | Headline prose locked between releases | |

**User's choice:** Every refresh + manual prose update via PR (Recommended)

---

## X4/X5 scope + placement

### Resolve the spec discrepancy: ARCH §11 P5 lists X1/X2/X3 only; ROADMAP Phase 6 SC#3 also requires X4 + X5. Ship all five in Phase 6, or carve X4/X5 out?

| Option | Description | Selected |
|--------|-------------|----------|
| Ship all five in Phase 6 | Honour ROADMAP SC#3; X1-X5 land together | ✓ |
| Carve X4/X5 to Phase 06.1 (insert) | Phase 6 ships X1/X2/X3 + portal; 06.1 ships X4/X5 | |
| Defer X4/X5 to Phase 8 (Constraints) or later | Wait for richer cross-scheme coverage | |

**User's choice:** Ship all five in Phase 6 (Recommended)

### Where do X-chart narrative + methodology pages live in the docs tree?

| Option | Description | Selected |
|--------|-------------|----------|
| New docs/portal/ directory with one page per X-chart | Cross-scheme analysis as the sixth implicit theme | ✓ |
| Existing docs/themes/cost/ directory | Slot X-charts under appropriate theme; no new IA tier | |
| Embed all X-chart narrative inline on docs/index.md | Homepage hero + scrollable narrative | |
| Mixed: X1/X2/X3 in docs/portal/; X4/X5 in themes | Reflects priority distinction; inconsistent IA | |

**User's choice:** New docs/portal/ directory with one page per X-chart (Recommended)

### What shape does X5 (2022 crisis comparison across schemes) take?

| Option | Description | Selected |
|--------|-------------|----------|
| Bar chart: per-scheme premium 2022 vs adjacent years | Vertical bars; x-axis = scheme; 3 grouped bars per scheme for 2021/2022/2023 | ✓ |
| Evolution panels with 2022 highlighted | Multi-panel time series; one panel per scheme | |
| Single combined evolution chart with shaded 2022 band | All schemes on one chart with 2022 vertical band | |

**User's choice:** Bar chart: per-scheme premium 2022 vs adjacent years (Recommended)

### How do X4 + X5 handle schemes without a gas counterfactual (Capacity Market, Balancing, Grid)?

| Option | Description | Selected |
|--------|-------------|----------|
| Omit + footnote | Charts include only schemes with gas counterfactual; footnote points to methodology | ✓ |
| Include with 'no counterfactual' marker | Hatched bars / 'n/a' markers in the chart | |
| Defer X4/X5 entirely to a later phase | Couple to Q1 above | |

**User's choice:** Omit + footnote (Recommended)

---

## Claude's Discretion

Captured in `06-CONTEXT.md` `<decisions>` section under Claude's Discretion:
- Portal scheme module shape (§6.1 contract conformance details)
- `docs/portal/methodology.md` depth (5-10 paragraphs covering 6 enumerated topics)
- Households-count constant source (ONS published table; planner picks canonical URL)
- `latest_fully_reconciled_year` precise definition (intersection rule)
- REF benchmark tolerance for partial-coverage phase (recommend lower-bound REF subset cross-check)
- mkdocs.yml nav placement of Portal tier (top-level vs sub-section)
- Atomic-commit slicing (suggested 7-wave decomposition)
- METHODOLOGY_VERSION 0.1.0 → 1.0.0 bump (planner judges at phase close)

---

## Deferred Ideas

Captured in `06-CONTEXT.md` `<deferred>` section. Highlights:
- mkdocs-macros plugin / live-binding via macros (revisit threshold defined)
- Calendar-year vs scheme-year normalisation as project-wide axis convention
- Three-tier headline display
- REF benchmark line on X1 chart
- `@pytest.mark.skip` on `test_ref_total_reconciliation`
- Per-technology decomposition on cross_scheme.parquet
- mkdocs nav placement of Portal tier
- METHODOLOGY_VERSION 0.1.0 → 1.0.0 bump
- External URL redirects
- Methodology page split (per-X-chart vs shared)
- Headline-sync test parametrisation

---

*Discussion completed: 2026-04-25*
*Total decisions: 16 across 4 areas (4 + 4 + 4 + 4)*
*All recommended options selected; no scope-creep moments; no user-cited external docs introduced during discussion.*
