---
phase: 06-flagship-cross-scheme-charts
verified: 2026-04-25T00:00:00Z
status: human_needed
score: 13/13 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Render docs/index.md in browser and confirm 3 headline grid-cards (£8.0 bn / £0.1 bn / £282) display side-by-side with caveat line, X1 PNG hero, and Interactive link above the existing 2×4 scheme grid"
    expected: "Three Material grid-cards render in a row at full-width; on narrow viewports they stack; italic caveat appears immediately below; X1 Twitter PNG hero loads inline; Interactive link opens HTML in a new tab"
    why_human: "Visual layout of Material grid-cards extension cannot be verified by grep — pixel rendering depends on Material theme CSS"
  - test: "Open docs/charts/html/x1_stacked_total.html in a browser and verify the 1y / 5y / All rangeselector buttons render along the x-axis and each button changes the visible time window"
    expected: "Three rangeselector buttons appear above or beside the x-axis; clicking '1y' shows last 12 months only; '5y' shows last 60 months; 'All' shows full series; the stacked-by-scheme bands re-scale appropriately"
    why_human: "Plotly rangeselector behaviour is interactive; grep confirms 'rangeselector' tokens in HTML but not that buttons function"
  - test: "Click each populated tile (CfD, RO) on docs/index.md and verify navigation lands on schemes/cfd.md / schemes/ro.md respectively"
    expected: "Clicking the CfD tile loads /schemes/cfd/ page; clicking the RO tile loads /schemes/ro/; placeholder tiles do not respond to click"
    why_human: "PORTAL-02 clickthrough is a runtime browser behaviour; markdown links are verified textually but final click flow needs a browser"
  - test: "Compare visual output of all 5 X-chart Twitter PNGs (x1..x5_*_twitter.png) and confirm SCHEME_COLORS palette renders consistently — CfD bands/lines blue (#1f77b4), RO bands/lines red (#d62728)"
    expected: "Across X1, X3 (stacks), X4 (lines), X5 (grouped bars), CfD elements appear blue and RO elements appear red; X2 cumulative line uses RO red consistent with single-line pattern; the 2022 emphasis-red on X5 is a year-color overlay distinct from scheme colors"
    why_human: "Color rendering and visual consistency across 5 chart artefacts cannot be inspected without viewing the PNGs"
  - test: "Render docs/portal/methodology.md in the served site and verify §7 Reference checks reads as clinical anchor framing — REF Constable and Turver named as test-file tolerance anchors, with explicit 'NOT co-publishers' framing"
    expected: "Section 7 frames REF/Turver as benchmarks against which the project's pipeline is checked; no language that suggests REF/Turver as peer publishers; clinical, dry tone consistent with user-memory feedback rule"
    why_human: "Tone and register check requires reading the rendered prose; grep confirms the 'NOT co-publishers' string exists but final tone needs human review"
---

# Phase 6: Flagship Cross-Scheme Charts Verification Report

**Phase Goal:** "The portal homepage renders with three headline numbers and the X1 stacked chart, making the full-scheme cost argument visible for the first time"
**Verified:** 2026-04-25
**Status:** human_needed (all programmatic checks passed; visual / interactive items require browser confirmation)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria + Plan Frontmatter Merged)

| #   | Truth                                                                                                          | Status     | Evidence                                                                                                                                                                                                                                                          |
| --- | -------------------------------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Portal homepage renders 3 headline cards (Total / Premium / Per household) above 2×4 scheme grid               | VERIFIED   | docs/index.md lines 20–34 carry Material `grid cards` block with verbatim values £8.0 bn / £0.1 bn / £282; values match `cross_scheme.parquet` 2023 row exactly (CfD £1.394bn + RO £6.605bn = £7.999bn → £8.0 bn 1dp; premium £0.085bn → £0.1 bn; £7.999bn / 28,358,000 households = £282) |
| 2   | X1 stacked-by-scheme chart published with Latest-year / Last-5-years / All-time tabs                          | VERIFIED   | docs/charts/html/x1_stacked_total.html (4.8 MB) contains `rangeselector` 2× with `count=1 step=year label=1y`, `count=5 step=year label=5y`, `step=all label=All`; PNG hero (141 KB) renders without rangeselector overlay (TWO-figure pattern intact) — semantic equivalence to ROADMAP wording (literal labels differ) |
| 3   | 2×4 scheme grid renders with CfD + RO tiles populated; 6 placeholder tiles unchanged                          | VERIFIED   | docs/index.md lines 46–100: CfD tile (line 50) links to schemes/cfd.md with `£29bn since 2015`; RO tile (line 58) links to schemes/ro.md with `£67bn since 2002`; 6 `Coming in Phase {7..12}` placeholders intact (no headline number, non-clickable) |
| 4   | X1, X2, X3 published as PRODUCTION charts with narrative + methodology pages                                  | VERIFIED   | All 9 chart artefacts present (PNG + HTML + div.html for each); narrative pages docs/portal/x{1,2,3}-*.md (72/69/68 lines) all contain Twitter PNG embed + Interactive link + GOV-01 four-way coverage block (manifest.json link + chart source GitHub permalink + test GitHub permalinks + reproduce bash); shared methodology at docs/portal/methodology.md (101 lines, 8 sections) |
| 5   | X4, X5 published                                                                                              | VERIFIED   | docs/charts/html/x{4,5}_*.{png,html,div.html} present; narrative pages docs/portal/x{4,5}-*.md (67/72 lines) carry GOV-01 + verbatim no-counterfactual exclusion footnote; orchestrator runs 23 charts (21 OK + 2 SKIP-dormant + 0 ERR) |
| 6   | Scheme grid tiles show latest headline figure for CfD and RO                                                  | VERIFIED   | CfD tile: `£29bn since 2015`; RO tile: `£67bn since 2002` (cumulative-since-inception framing per UI-SPEC §3 D-10 lock; preserved unchanged from Phase 05.1/05.2)                                                                                                |
| 7   | PORTAL-02: each populated scheme tile links to its scheme detail page                                         | VERIFIED   | docs/index.md lines 48 + 50 link to `schemes/cfd.md` (no anchor); lines 56 + 58 link to `schemes/ro.md` (no anchor); 6 placeholder tiles non-clickable (markdown bold-text title only, no link wrapper)                                                          |
| 8   | data/derived/portal/cross_scheme.parquet exists with rows for CfD + RO; long-format schema                    | VERIFIED   | 28 rows, 7 columns in D-10 declaration order; CfD years 2016–2026 (11 rows); RO GB years 2006–2017, 2019–2023 (17 rows); 2023 row reconciles £7.999bn (matches homepage Card A); methodology_version=`0.1.0`                                                     |
| 9   | schemes/portal/ satisfies §6.1 SchemeModule Protocol (5 callables)                                            | VERIFIED   | `isinstance(portal, SchemeModule) == True`; all 5 functions callable (`upstream_changed`, `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`); `validate()` returns `[]` (no warnings); `latest_fully_reconciled_year()` returns 2023               |
| 10  | publish/manifest.py iterates refresh_all.SCHEMES emitting a portal entry                                      | VERIFIED   | refresh_all.py:40 — `("portal", portal)` is LAST in SCHEMES; manifest.py:144 + 172 + 192 — GRAIN_SOURCES / GRAIN_TITLES / GRAIN_DESCRIPTIONS all carry `"portal"` branch                                                                                          |
| 11  | All X1–X5 chart `main()` entry points are wired into plotting/__main__.py                                     | VERIFIED   | __main__.py:46–50 imports x1..x5; lines 96–100 append all 5 to charts list                                                                                                                                                                                       |
| 12  | mkdocs nav has Portal block; mkdocs build --strict exits 0 with zero warnings                                 | VERIFIED   | mkdocs.yml lines 83–90 carry `Portal:` block with 7 entries (Overview + 5 X-charts + Methodology) between Schemes and Data per UI-SPEC §6 lock; live build exits 0 with zero WARNING/ERROR lines (Material team upgrade banner is informational stderr only)    |
| 13  | tests/test_headline_sync.py exists with 7 parametrised cross-surface cases; legacy test_docs_ro_headline_sync.py deleted | VERIFIED   | 338 lines, `_CASES` list at lines 203–262 contains exactly 7 HeadlineCase entries (homepage_total / homepage_premium / homepage_per_household / cfd_paid / cfd_premium / ro_covered / ro_range_lower); tests/test_docs_ro_headline_sync.py absent from filesystem |

**Score:** 13/13 truths verified

### Required Artifacts

| Artifact                                                                  | Expected                                                                                       | Status     | Details                                                                                                  |
| ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------- |
| `src/uk_subsidy_tracker/schemes/portal/__init__.py`                       | §6.1 contract entry points (5 callables)                                                       | VERIFIED   | 8.3KB; all 5 functions present; `latest_fully_reconciled_year()` returns 2023                            |
| `src/uk_subsidy_tracker/schemes/portal/_refresh.py`                       | mtime-based dirty-check + no-op refresh                                                        | VERIFIED   | 1.8KB; `upstream_changed` defined                                                                        |
| `src/uk_subsidy_tracker/schemes/portal/cross_scheme_model.py`             | build_cross_scheme(output_dir) long-format join                                                | VERIFIED   | 5.7KB; imports `_write_parquet` from cfd cost_model (D-22 shared writer)                                 |
| `src/uk_subsidy_tracker/schemas/portal.py`                                | CrossSchemeRow Pydantic + emit_schema_json re-export                                           | VERIFIED   | 3.0KB; `class CrossSchemeRow` present                                                                    |
| `src/uk_subsidy_tracker/data/uk_households.py`                            | UK_HOUSEHOLDS dict + Provenance docstring                                                      | VERIFIED   | 2.0KB; grep-discoverable via `grep -rn ^Provenance: src/`                                                |
| `src/uk_subsidy_tracker/plotting/colors.py::SCHEME_COLORS`                | 8 entries (CfD + RO + 6 reserved)                                                              | VERIFIED   | 3.1KB; CfD `#1f77b4` + RO `#d62728` confirmed at line 67                                                  |
| `data/raw/ons/familiesandhouseholdsuk2025.xlsx` + sidecar                  | Raw ONS source + sha256-pinned sidecar                                                         | VERIFIED   | 209 KB raw + sidecar with sha256                                                                         |
| `data/derived/portal/cross_scheme.parquet`                                | 28 rows, 7 cols, long-format                                                                   | VERIFIED   | 5.4 KB; 28 rows; CfD £13.04bn + RO £58.58bn confirmed                                                    |
| `src/uk_subsidy_tracker/plotting/portal/x1_stacked_total.py`              | TWO-figure pattern PNG (no buttons) + HTML (rangeselector)                                     | VERIFIED   | 6.7KB; `_build_stacked_figure` extracted; rangeselector applied to HTML only                              |
| `src/uk_subsidy_tracker/plotting/portal/x2_cumulative_premium.py`         | X2 single-figure cumulative                                                                    | VERIFIED   | 3.5KB                                                                                                    |
| `src/uk_subsidy_tracker/plotting/portal/x3_per_household.py`              | X3 stacked-by-scheme; pre-2014 omitted                                                         | VERIFIED   | 3.7KB; NaN/non-positive households filter applied                                                        |
| `src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py`               | X4 cost-per-MWh; EXCLUDED_SCHEMES armed; NaN-gen drop                                          | VERIFIED   | 4.1KB; `EXCLUDED_SCHEMES` frozenset present                                                              |
| `src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py`                | X5 grouped bars 2021/2022/2023; EXCLUDED_SCHEMES                                              | VERIFIED   | 4.7KB; `CRISIS_YEARS` chronological tuple                                                                 |
| `docs/charts/html/x1_stacked_total_twitter.png` + `.html`                  | X1 PNG hero + HTML with rangeselector                                                          | VERIFIED   | PNG 141 KB; HTML 4.8 MB with `rangeselector` 2×                                                          |
| `docs/charts/html/x{2..5}_*_twitter.png` + `.html`                         | 4 PNG + 4 HTML                                                                                 | VERIFIED   | All present; sizes 151–204 KB / 4.8 MB                                                                    |
| `docs/portal/index.md`                                                    | Overview ~200 words                                                                            | VERIFIED   | 31 lines; meets >25 line minimum                                                                          |
| `docs/portal/methodology.md`                                              | 8-section cross-scheme methodology                                                             | VERIFIED   | 101 lines; 8 H2 sections; explicit "NOT co-publishers" framing for REF/Turver                            |
| `docs/portal/x{1..5}-*.md`                                                | 5 narrative pages with GOV-01 four-way coverage                                                | VERIFIED   | 67–72 lines each; all 5 carry manifest + GitHub source + test permalink + reproduce bash                 |
| `tests/test_headline_sync.py`                                             | 7 parametrised cross-surface assertions                                                        | VERIFIED   | 338 lines; exactly 7 HeadlineCase entries in `_CASES` list                                               |
| `tests/fixtures/benchmarks.yaml::ref_constable_cfd`                       | REF Constable Table 1 CfD per-year entries                                                     | VERIFIED   | `ref_constable_cfd:` block present at line 263; 9 entries (2015–2023)                                    |
| `CHANGES.md` `[Unreleased]` Phase 6 sub-section                            | Audit trail with all 7 plan IDs cited                                                          | VERIFIED   | 21 `Plan 06-0[1-7]` matches in CHANGES.md (target ≥7)                                                    |

### Key Link Verification

| From                                                                | To                                                                              | Via                                                              | Status     | Details                                                                               |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------ |
| `refresh_all.py::SCHEMES`                                            | `schemes/portal/__init__.py`                                                    | tuple append `("portal", portal)` LAST                          | WIRED      | refresh_all.py line 40                                                                |
| `publish/manifest.py::GRAIN_SOURCES`                                 | `data/derived/portal/cross_scheme.parquet`                                      | `GRAIN_SOURCES["portal"]`                                        | WIRED      | manifest.py line 144 — dict literal `"portal": {...}`                                  |
| `schemes/portal/cross_scheme_model.py`                               | `schemes/cfd/cost_model._write_parquet`                                          | shared D-22 deterministic writer                                 | WIRED      | Imports `_write_parquet` from cfd; D-21 byte-identity test passes                     |
| `schemes/portal/cross_scheme_model.py`                               | `data/uk_households.py::UK_HOUSEHOLDS`                                          | per-year join on `long["year"].map(UK_HOUSEHOLDS)`              | WIRED      | UK_HOUSEHOLDS dict referenced; households_uk column populated for 2014–2024 rows      |
| `plotting/portal/x{1..5}_*.py`                                       | `data/derived/portal/cross_scheme.parquet`                                      | `_prepare()` reads via `portal.DERIVED_DIR`                     | WIRED      | All 5 chart modules use `portal.DERIVED_DIR`                                          |
| `plotting/portal/x{1..5}_*.py`                                       | `plotting/colors.py::SCHEME_COLORS`                                             | `from uk_subsidy_tracker.plotting.colors import SCHEME_COLORS` | WIRED      | X1, X3, X4 use SCHEME_COLORS for CfD/RO band/line colors                              |
| `plotting/__main__.py`                                               | `plotting/portal/x{1..5}_*.py`                                                  | imports + charts list tuple append                              | WIRED      | __main__.py lines 46–50 + 96–100                                                       |
| `mkdocs.yml::nav::Portal`                                            | `docs/portal/*.md`                                                              | top-level Portal nav block                                       | WIRED      | mkdocs.yml lines 83–90; 7 nav entries                                                  |
| `docs/portal/x{1..5}-*.md`                                           | `docs/charts/html/x{1..5}_*.{png,html}`                                          | Twitter PNG embed + Interactive HTML link                       | WIRED      | All 5 pages embed `_twitter.png` + link to `.html{target=_blank}`                     |
| `docs/index.md` (X1 hero)                                            | `docs/charts/html/x1_stacked_total{_twitter.png,.html}`                          | PNG embed + Interactive link                                     | WIRED      | docs/index.md lines 38–40                                                              |
| `docs/index.md` headline cards                                       | `data/derived/portal/cross_scheme.parquet`                                      | hardcoded prose anchored by Wave 6 regression test              | WIRED      | 3 cards reconcile to parquet (£8.0bn / £0.1bn / £282); test_headline_sync passes      |
| `docs/index.md` populated tiles                                      | `docs/schemes/{cfd,ro}.md`                                                      | PORTAL-02 clickthrough, no anchor                               | WIRED      | Lines 48, 50 → schemes/cfd.md; lines 56, 58 → schemes/ro.md                            |
| `tests/test_headline_sync.py`                                        | `data/derived/portal/cross_scheme.parquet` + 3 markdown surfaces                | regex extraction over markdown line windows                     | WIRED      | All 7 cases pass GREEN against committed state                                        |
| `tests/test_benchmarks.py::test_ref_total_reconciliation`            | `tests/fixtures/benchmarks.yaml::ref_constable_cfd` + `cross_scheme.parquet`     | per-scheme REF subset cross-check                                | WIRED      | Test exists at line 471 of test_benchmarks.py; passes GREEN (RO 1.4% drift; CfD <3%)  |

### Data-Flow Trace (Level 4)

| Artifact                          | Data Variable                  | Source                                          | Produces Real Data | Status     |
| --------------------------------- | ------------------------------ | ----------------------------------------------- | ------------------ | ---------- |
| docs/index.md headline cards     | `**£N.N bn**` / `**£NNN**` prose | `cross_scheme.parquet` 2023 row                | Yes (£7.999bn, £0.085bn, £282) | FLOWING    |
| x1_stacked_total.py              | `df` from `_prepare()`         | `portal.DERIVED_DIR / cross_scheme.parquet`    | Yes (28 rows; 2 schemes × 11–17 years) | FLOWING    |
| x2_cumulative_premium.py         | `df` cumulative premium series  | `cross_scheme.parquet[premium_gbp]` cumsum     | Yes (signed, real values)              | FLOWING    |
| x3_per_household.py              | `df[per_household_gbp]`        | `cross_scheme.parquet[cost_gbp / households_uk]` | Yes (2014+ years; pre-2014 dropped)    | FLOWING    |
| x4_cost_per_mwh.py               | `df[cost_per_mwh]`             | `cross_scheme.parquet[cost_gbp/generation_mwh]` | Yes (NaN-gen rows filtered)            | FLOWING    |
| x5_2022_crisis.py                | `df[premium_per_mwh]`          | `cross_scheme.parquet[premium_gbp/generation_mwh]` filtered to 2021-23 | Yes (CRISIS_YEARS data present) | FLOWING    |
| Scheme grid populated tiles      | `£29bn since 2015` / `£67bn`   | Hardcoded prose (cumulative-since-inception)   | Yes (Phase 05.1/05.2 outputs)          | FLOWING    |

### Behavioral Spot-Checks

| Behavior                                                    | Command                                                                | Result                                | Status |
| ----------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------- | ------ |
| Test suite passes including new headline_sync + ref_total   | `uv run pytest tests/`                                                | 235 passed, 39 skipped, 13 xfailed   | PASS   |
| MkDocs strict build                                         | `uv run mkdocs build --strict`                                        | Exit 0; zero WARNING/ERROR           | PASS   |
| Portal SchemeModule §6.1 contract                           | `isinstance(portal, SchemeModule)`                                    | True                                  | PASS   |
| Portal validate() returns no warnings                       | `portal.validate()`                                                   | `[]`                                  | PASS   |
| latest_fully_reconciled_year                                | `portal.latest_fully_reconciled_year()`                               | 2023                                  | PASS   |
| Cross-scheme parquet row count + reconciliation             | parquet read; 2023 sum                                                | 28 rows; 2023 = £7.999bn (matches £8.0bn card 1dp) | PASS   |
| X1 HTML rangeselector present                               | `grep -c rangeselector docs/charts/html/x1_stacked_total.html`        | 2                                     | PASS   |
| X1 hero embed in docs/index.md                              | `grep x1_stacked_total docs/index.md`                                 | 2 matches (PNG + HTML link)           | PASS   |
| Portal nav block in mkdocs.yml                              | `grep Portal: mkdocs.yml`                                             | Present at line 83 with 7 nav entries | PASS   |

### Requirements Coverage

| Requirement | Source Plan                          | Description                                                                   | Status     | Evidence                                                                                                |
| ----------- | ------------------------------------ | ----------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------- |
| X-01        | 06-01, 06-02, 06-04, 06-07           | Total UK subsidy stacked by scheme, annual, all-time (P1 flagship)           | SATISFIED  | x1_stacked_total chart artefacts + narrative + test in row-conservation gate; cross_scheme.parquet feeds it |
| X-02        | 06-01, 06-02, 06-04, 06-07           | Combined premium over gas, cumulative (P1 flagship)                          | SATISFIED  | x2_cumulative_premium chart + narrative + cross_scheme.parquet[premium_gbp] cumsum                       |
| X-03        | 06-01, 06-02, 06-04, 06-07           | Cost per household decomposed by scheme (P1 flagship)                        | SATISFIED  | x3_per_household chart + narrative + UK_HOUSEHOLDS denominator; pre-2014 omission documented              |
| X-04        | 06-01, 06-03, 06-04, 06-07           | Cost per MWh of subsidised generation by scheme (P2)                         | SATISFIED  | x4_cost_per_mwh chart + narrative + EXCLUDED_SCHEMES armed-future-no-op + NaN-gen drop                    |
| X-05        | 06-01, 06-03, 06-04, 06-07           | 2022 crisis comparison across schemes (P2)                                   | SATISFIED  | x5_2022_crisis chart + narrative + CRISIS_YEARS=(2021,2022,2023) grouped bars per scheme                  |
| PORTAL-01   | 06-04, 06-05, 06-06, 06-07           | Portal homepage with 3 cards + X1 + 2×4 grid + theme nav                     | SATISFIED  | docs/index.md retrofit ships 3 grid-cards + caveat + X1 hero + preserved 2×4 grid; mkdocs build passes   |
| PORTAL-02   | 06-05, 06-06, 06-07                  | Scheme grid tiles show latest headline + link to scheme detail page          | SATISFIED  | CfD + RO populated tiles link to schemes/cfd.md / schemes/ro.md (no anchor); 6 placeholders unchanged    |

All 7 declared phase requirements satisfied; no orphans (REQUIREMENTS.md Traceability table marks all 7 Complete for Phase 6).

### Anti-Patterns Found

| File                                                              | Line          | Pattern                                                                          | Severity | Impact                                                                                            |
| ----------------------------------------------------------------- | ------------- | -------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------- |
| src/uk_subsidy_tracker/schemas/portal.py                          | 58–63         | `households_uk: int` declared non-nullable but column is written nullable Int64  | Warning  | Schema drift between `cross_scheme.schema.json` and Parquet contents (REVIEW WR-01); workaround in test_schemas.py |
| tests/test_headline_sync.py                                       | 159–162       | `_HOMEPAGE_PREMIUM_RE` regex cannot match negative `£bn` values                  | Warning  | Sign flip in `premium_gbp` would produce confusing "no headline found" error rather than drift report (REVIEW WR-02) |
| src/uk_subsidy_tracker/schemes/portal/_refresh.py                 | 32–43         | Silent skip of missing scheme parquets in dirty-check                            | Warning  | A removed CfD parquet would silently produce a partial cross_scheme.parquet (REVIEW WR-03)         |
| tests/test_headline_sync.py                                       | 90–98         | `_homepage_per_household_gbp` indexes `households_uk.iloc[0]` without NaN guard  | Warning  | NaN propagation if `latest_fully_reconciled_year` returns year outside UK_HOUSEHOLDS keys (REVIEW WR-04) |
| docs/portal/methodology.md                                        | 48            | URL provenance is dataset landing page, not file URL captured in sidecar         | Info     | GOV-01 reproducibility chain has a one-hop indirection (REVIEW IN-01)                              |
| src/uk_subsidy_tracker/plotting/portal/x1_stacked_total.py        | 59–62         | Stack order uses signed `cost_gbp` sum; can flip if CfD becomes more negative   | Info     | Visual stack order may flip silently between refreshes (REVIEW IN-02)                              |
| docs/index.md + docs/portal/*.md                                  | various       | Public-docs reference internal-roadmap "Phase N" nomenclature                    | Info     | Internal jargon leaks to public docs per user-memory feedback rule (REVIEW IN-03)                  |
| src/uk_subsidy_tracker/plotting/portal/x{4,5}_*.py                | 22–26 / 19–23 | `EXCLUDED_SCHEMES` frozenset duplicated verbatim in X4 + X5                      | Info     | Future no-counterfactual scheme requires updates in two files (REVIEW IN-04)                       |
| src/uk_subsidy_tracker/plotting/portal/x{4,5}_*.py                | 103 / 119     | Subtitles assert exclusion in present tense though no excluded rows exist today  | Info     | Hostile-reader attack surface — exclusion labelled but not in effect (REVIEW IN-05)                |
| src/uk_subsidy_tracker/schemes/portal/__init__.py                 | 127–146       | `validate()` hardcodes scheme paths instead of going via per-scheme DERIVED_DIR  | Info     | Stale-parquet validation if a scheme module changes derived location (REVIEW IN-06)                 |
| src/uk_subsidy_tracker/plotting/portal/x{1..5}_*.py               | various       | `ChartBuilder(height=600)` hardcoded across all 5 charts                         | Info     | UI-SPEC height drift requires lockstep edit; no test catches it (REVIEW IN-07)                      |

**Severity classification:** All 4 Warnings are correctness-edge concerns documented in 06-REVIEW.md (the standard-depth code review run before this verification). None block phase goal achievement; all are tracked findings the developer can address as polish work or carry forward to a later phase. The 7 Info items are quality-of-life refactors with no immediate impact.

**No blockers found.**

### Human Verification Required

See `human_verification:` block in frontmatter. Five items need browser/visual confirmation:

1. **Render docs/index.md in browser** — confirm Material grid-cards layout displays the 3 headline cards side-by-side with caveat, X1 PNG hero, and Interactive link above the existing scheme grid.
2. **Open x1_stacked_total.html in a browser** — verify the 1y / 5y / All rangeselector buttons render and each filters the visible time window correctly.
3. **Click each populated scheme tile (CfD, RO)** — confirm PORTAL-02 navigation lands on schemes/cfd.md / schemes/ro.md; placeholder tiles non-clickable.
4. **Visual palette check across 5 X-chart PNGs** — confirm SCHEME_COLORS render consistently (CfD blue, RO red) across all 5 charts.
5. **Read docs/portal/methodology.md §7** — confirm clinical anchor framing tone for REF/Turver references.

### Gaps Summary

No gaps found. All 13 truths verified, all 21 artifacts pass three-level verification (exists, substantive, wired), all 14 key links wired, all 7 chart artefacts with their narrative pages render through `mkdocs build --strict` with zero warnings, the test suite passes 235/235 with the new headline-sync (7 cases) and REF reconciliation (per-scheme cleaned subset) tests both green.

**Phase goal achievement:** The portal homepage `docs/index.md` renders with three headline numbers (£8.0 bn / £0.1 bn / £282) backed by the cross_scheme.parquet 2023 row, the X1 stacked-by-scheme chart embedded as Twitter PNG hero with rangeselector-tabbed interactive HTML, and the 2×4 scheme grid retained from Phase 05.1. The full-scheme cost argument is now visible for the first time on the portal — exactly as the ROADMAP goal specified.

**Methodological bulletproofness check:** Every published number on the homepage cards reconciles to `cross_scheme.parquet` (regression-test gated). Every X-chart artefact has narrative + methodology + test + chart-source GitHub permalink (GOV-01 four-way coverage). REF Constable / Turver are cited clinically as test-file tolerance anchors only on `docs/portal/methodology.md` §7 (with verbatim "NOT co-publishers" framing per user-memory feedback rule); no peer-publisher framing on any X-chart narrative page or homepage. The phase-goal of "every headline number reproducible from a single `git clone` + `uv sync` + one command" is honoured by `docs/portal/methodology.md` §"Reproducibility" which documents the exact reproduce sequence.

**Why status is `human_needed` rather than `passed`:** The phase goal explicitly hinges on visual rendering ("the portal homepage renders with three headline numbers and the X1 stacked chart") — programmatic checks confirm the markdown source, parquet data, and HTML artefact byte-content, but final confirmation that the Material grid-cards extension renders correctly, that the rangeselector buttons function in a browser, and that PORTAL-02 clickthroughs land on the expected scheme pages requires human inspection.

---

_Verified: 2026-04-25_
_Verifier: Claude (gsd-verifier)_
