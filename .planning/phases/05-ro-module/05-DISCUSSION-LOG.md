# Phase 5: RO Module — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-22
**Phase:** 05-ro-module
**Areas discussed:** Cost-model methodology, Time + carbon extension, Scope inclusions, Benchmark + docs structure

---

## Cost-model methodology (R1 banding + R6 ROC price)

### Q1: How should ro_cost_gbp compute rocs_issued per station-month?

| Option | Description | Selected |
|--------|-------------|----------|
| Ofgem rocs_issued primary | Ofgem's published `ROCs_Issued` column is authoritative; YAML bandings table used only for audit cross-check. Short-circuits R1 methodology risk. | ✓ |
| YAML bandings primary | Compute `generation_mwh × banding_factor` from our `ro_bandings.yaml`; Ofgem column used only as validation check. | |
| Hybrid | Ofgem where present; YAML fallback where missing or implausible. Each row carries `roc_source` audit column. | |

**User's choice:** Ofgem rocs_issued primary (Recommended).
**Notes:** Largest methodology risk (R1) deflects to the regulator's own certification. YAML retained as audit cross-check with >1% divergence warning.

---

### Q2: What is the primary ROC price feeding ro_cost_gbp?

| Option | Description | Selected |
|--------|-------------|----------|
| buyout + recycle | Consumer-cost view; what suppliers charge customers via bills. Ofgem-published, stable. | |
| e-ROC market clearing | Generator-revenue view; what stations actually received. 2-10% divergent from buyout+recycle. | |
| Dual: primary buyout+recycle, sensitivity e-ROC | `ro_cost_gbp` = buyout+recycle; additional `ro_cost_gbp_eroc` column holds e-ROC variant. Dynamics chart shows both as band. | ✓ |

**User's choice:** Dual: primary buyout+recycle, sensitivity e-ROC.
**Notes:** Lets adversarial readers see the 2-10% convention-choice sensitivity without re-running the pipeline. Two cost columns on station_month.parquet.

---

### Q3: Where does ro_bandings.yaml live and what is its scope?

| Option | Description | Selected |
|--------|-------------|----------|
| src/uk_subsidy_tracker/data/ro_bandings.yaml | Alongside `lccc_datasets.yaml` pattern; ~60 (technology × commissioning-window × country) cells with Provenance blocks; Pydantic-loaded. | ✓ |
| tests/fixtures/ro_bandings.yaml | Treat bandings as validation-test fixture; cost model uses Ofgem column directly. Simpler if Option 1 was chosen for Q1. | |
| static Python dict in cost_model.py | Inline ~60 rows as module-level constant. Simpler but harder to audit and breaks established YAML pattern. | |

**User's choice:** src/uk_subsidy_tracker/data/ro_bandings.yaml (Recommended).
**Notes:** Follows constant-provenance pattern (`grep -rn "^Provenance:" src/`) so RO bandings are grep-discoverable for audit.

---

### Q4: What does `validate()` for the RO scheme check?

| Option | Description | Selected |
|--------|-------------|----------|
| Banding divergence | Count stations where `|generation_mwh × banding_factor - rocs_issued| / rocs_issued > 1%`. Warn if >10 stations. | ✓ |
| Aggregate drift vs Turver band | Compute 2011-2022 aggregate; warn if outside Turver ±3%. Runtime validator, not just a test. | ✓ |
| Methodology version consistency | Mirrors CfD validate() Check 3; warn on methodology_version column drift. | ✓ |
| Forward projection sanity | Warn on negative costs or MWh jumps >50% between years in forward_projection.parquet. | ✓ |

**User's choice:** All four.
**Notes:** `validate()` returns warnings (empty list = clean). All four are cheap post-rebuild checks.

---

## Time + carbon extension (R2 pre-2013 carbon + R3 CY/OY)

### Q1: How do we handle carbon-price coverage for RO pre-2018?

| Option | Description | Selected |
|--------|-------------|----------|
| Extend table; publish sensitivity | Extend DEFAULT_CARBON_PRICES with EU ETS 2005-2017 (EUR→GBP) + zero 2002-2004; emit ro_cost_gbp_nocarbon sensitivity column. | ✓ |
| Extend table only (no sensitivity) | Extend DEFAULT_CARBON_PRICES; primary cost only, no-carbon via kwarg but not persisted. | |
| Dual publish (with-carbon + without-carbon equally prominent) | Every chart shows paired lines. Heaviest, most transparent. | |
| Skip carbon entirely pre-2018 | Hard-code zero pre-2018; methodologically wrong for 2013-2017 UK-in-EU-ETS window. | |

**User's choice:** Extend table; publish sensitivity (Recommended).
**Notes:** Primary uses extended table; ro_cost_gbp_nocarbon column available for adversarial readers to see the pure-subsidy portion.

---

### Q2: METHODOLOGY_VERSION policy with carbon extension?

| Option | Description | Selected |
|--------|-------------|----------|
| Stay at 0.1.0 | Pre-1.0.0 prototype policy; additive year extension, no existing-value revision, not a formula-shape change. CHANGES.md ## Methodology versions still logs it. | ✓ |
| Bump to 0.2.0 | Treat extension as meaningful methodology change. | |
| Bump to 1.0.0 now | Formal SemVer start; SemVer-locks before portal launch (Phase 6). Contradicts Phase 4 carry-forward. | |

**User's choice:** Stay at 0.1.0 (Recommended).
**Notes:** Bump reserved for Phase 6+ portal launch per Phase 2 D-05 + counterfactual.py module docstring.

---

### Q3: Primary plotting axis for RO charts?

| Option | Description | Selected |
|--------|-------------|----------|
| Calendar year throughout | Every RO chart plots by CY; obligation year as methodology caveat only. Matches gas counterfactual + CfD + future cross-scheme axis. | ✓ |
| Obligation year for RO-only; CY for cross-scheme | Faithful to RO mechanics; readers must reason about axis changes when navigating. | |
| Both axes with a toggle | Maximum flexibility; more work; derived Parquet carries both columns. | |

**User's choice:** Calendar year throughout (Recommended).
**Notes:** Single-axis cross-scheme comparability is an adversarial-proofing concern.

---

### Q4: ROC-price assignment rule for CY-axis plotting?

| Option | Description | Selected |
|--------|-------------|----------|
| ROC price of OY containing the output period | March 2022 generation → OY 2021-22 price. Each row carries `obligation_year` audit column. | ✓ |
| Weighted average of OYs intersecting the CY | Weight OY-portions by month-count. Obscures mechanism. | |
| ROC price of OY ending in the CY | Convention choice; less defensible (OY covers only 3 months of CY). | |

**User's choice:** ROC price of OY containing the output period (Recommended).
**Notes:** Simple, defensible, spec-recommended. Matches how consumers were actually billed.

---

## Scope inclusions (R4 NIRO + R5 co-firing + R7 mutualisation)

### Q1: NIRO (Northern Ireland) — include?

| Option | Description | Selected |
|--------|-------------|----------|
| Include as country='NI' rows; GB-only headlines | Scraper fetches NI stations + NI-specific buyout/recycle; headline totals on docs/schemes/ro.md are GB-only; methodology notes NI-inclusion option. | ✓ |
| GB-only, exclude NIRO entirely | Filter at ingest; simpler but hides ~£100m/year of NI subsidy. | |
| Include; headline quotes UK total (GB+NI) | Comprehensive headline; may complicate CfD comparison. | |

**User's choice:** Include as country='NI' rows; GB-only headlines (Recommended).
**Notes:** Data in Parquet for adversarial-reader filter; headline matches CfD GB-only convention.

---

### Q2: Co-firing biomass — include?

| Option | Description | Selected |
|--------|-------------|----------|
| Include with technology='biomass_cofiring' slice | Spec recommendation. Co-firing received Ofgem-certified ROCs; part of consumer cost. Methodology flags contestability with filter instructions. | ✓ |
| Exclude co-firing entirely | Cleaner 'renewables' framing but excludes several £bn historical cost (Drax 2003-2016). Breaks Turver/REF/Ofgem reconciliation. | |
| Include; publish with/without-cofiring headline variants | Maximally transparent; docs complexity. | |

**User's choice:** Include with technology='biomass_cofiring' slice (Recommended).
**Notes:** Slice filter lets readers regenerate cofiring-excluded totals if they object.

---

### Q3: Mutualisation payments — treatment?

| Option | Description | Selected |
|--------|-------------|----------|
| Roll into ro_cost_gbp + flag years | Mutualisation increments 2021-22 + 2022-23 effective ROC cost; annual_summary carries mutualisation_gbp column. S2 chart shows visible spike. | ✓ |
| Separate line in cost stack, not in ro_cost_gbp | Keeps ro_cost_gbp as pure buyout+recycle; two lines to explain. | |
| Exclude mutualisation entirely | Underestimates 2021-22 by ~£200m; breaks Turver reconciliation. | |

**User's choice:** Roll into ro_cost_gbp + flag years (Recommended).
**Notes:** Consumers paid it; it's in the consumer-cost total. Methodology page explains the event.

---

### Q4: Headline figure scope?

| Option | Description | Selected |
|--------|-------------|----------|
| All-in GB total incl. cofiring + mutualisation | Methodology lists component parts: 'of which £A from cofiring, £B from mutualisation, £C NIRO excluded'. Every component visible; adversarial-proof. | ✓ |
| Narrow: GB excl. cofiring + mutualisation | Conservative headline; invites 'why did you exclude?' critique. | |
| Publish two headlines prominently | Lead with both; less crisp messaging. | |

**User's choice:** All-in GB total incl. cofiring + mutualisation (Recommended).
**Notes:** Adversarial-proofing made concrete on the scheme page.

---

## Benchmark + docs structure

### Q1: Turver anchor source?

| Option | Description | Selected |
|--------|-------------|----------|
| Andrew Turver NZW 2023 paper | 'The Hidden Cost of Net Zero'; widely-cited; researcher transcribes 2011-2022 annual total. | |
| Turver's Substack aggregates | Moving target; less paper-of-record-ish. | |
| Researcher identifies best available at research time | gsd-phase-researcher picks most-defensible Turver publication with clean CY 2011-2022 RO aggregate. Defers decision with low cost; matches Phase 2 D-11 pattern. | ✓ |

**User's choice:** Researcher identifies best available at research time.
**Notes:** Defers to gsd-phase-researcher at Phase 5 research time. Planner confirms figure + PDF URL + scope (CY/OY, NIRO/cofiring/mutualisation inclusion).

---

### Q2: What if RO 2011-2022 aggregate diverges beyond 3% from Turver?

| Option | Description | Selected |
|--------|-------------|----------|
| Block phase exit; investigate | ROADMAP SC #3 is binary. Investigate root cause (banding, scope, mutualisation) before merging. | ✓ |
| Ship with divergence documented + widen tolerance | Pragmatic but weakens adversarial-proof quality bar. | |
| D-11 fallback posture — skip the check | Spec rejects; ROADMAP SC #3 is hard. | |

**User's choice:** Block phase exit; investigate (Recommended).
**Notes:** Phase 2 D-11 fallback does NOT apply for RO-06. Matches adversarial-proofing principle.

---

### Q3: docs/schemes/ro.md structure?

| Option | Description | Selected |
|--------|-------------|----------|
| Scheme overview + S2-S5 embeds + theme links | Single-page: headline, explainer, chart embeds, methodology summary, cross-links to Cost/Recipients theme pages. | ✓ |
| Scheme page + per-chart pages under docs/schemes/ro/ | Four child pages with D-01 six-section GOV-01 coverage. Double docs work. | |
| Scheme page + per-chart pages under docs/themes/ | Per-chart pages live with their argumentative theme. Mixes scheme-axis and theme-axis navigation. | |

**User's choice:** Scheme overview + S2-S5 embeds + theme links (Recommended).
**Notes:** Scheme-level page is the GOV-01 unit for RO; per-chart expansion deferred if research warrants.

---

### Q4: Chart code shared with CfD?

| Option | Description | Selected |
|--------|-------------|----------|
| RO-specific copies, extract shared helpers opportunistically | New RO chart files mirror CfD structure; 2-3 line duplicates extracted to plotting/subsidy/_shared.py. Aggressive refactor deferred to Phase 6. | ✓ |
| Aggressive refactor: shared cfd_dynamics.py parametrised over scheme | Maximises DRY; risks regressing Phase 3's 7 PROMOTE CfD charts. | |
| Full duplicate (no shared helpers) | Simplest; most duplication. | |

**User's choice:** RO-specific copies, extract shared helpers opportunistically (Recommended).
**Notes:** Matches Phase 4 D-02 "charts untouched" discipline. Phase 6 X-charts will force shared refactor.

---

## Claude's Discretion

Areas deferred to planner / research agent at Phase 5 planning time:

- **Ofgem scraper mechanism** — HTTP GET vs Playwright; planner chooses at research time.
- **`ro_bandings.yaml` exact field schema** — Two-layer Pydantic pattern established; field set planner-decided.
- **Forward projection methodology for 2026→2037** — Extrapolation approach (straight-line, capacity-factor × installed capacity, per-station accreditation-end) is planner decision. Must be deterministic (D-21).
- **Mutualisation data source + extraction** — Planner picks manual YAML fixture vs scraped table.
- **Refresh cadence for Ofgem in `refresh_all.py`** — Monthly vs daily-with-dirty-check; planner picks.
- **RO-specific test fixtures** — Own file vs piggyback on existing patterns; no network in CI.
- **Test parametrisation strategy** — Extend existing CfD parametrisation vs new RO-specific test files (former is established pattern).

## Deferred Ideas

- Combined CfD + RO flagship chart (X1/X2 territory) — Phase 6.
- Portal homepage + scheme grid — Phase 6.
- FiT module — Phase 7.
- Per-chart D-01 pages under docs/schemes/ro/ — deferred if research warrants.
- Aggressive chart-code refactor — Phase 6 when X-charts need it.
- METHODOLOGY_VERSION bump to 1.0.0 — Phase 6+ portal launch.
- Zenodo DOI registration — V2-COMM-01 after Phase 5 lands.
- Pre-publication email to Turver — post-Phase-5 courtesy step.
- docs/data/ro.md per-scheme data page — unneeded per Phase 4 D-27.
- UK-total (GB+NI) headline framing — D-09 picks GB-only; revisit after ship.
- `fit/` stub directory — superseded by Phase 7's full module.
- OY-axis charts — D-07 picks CY; add only if reader feedback demands.
- Cloudflare R2 for oversized raw files — first relevant Phase 8.
