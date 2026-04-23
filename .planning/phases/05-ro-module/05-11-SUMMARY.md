---
phase: 05-ro-module
plan: 11
subsystem: docs
tags: [mkdocs, ro, scheme-page, gov-01, theme-cross-links, material-grid-cards]

# Dependency graph
requires:
  - phase: 05-ro-module
    provides: "Plan 05-08 4 RO chart modules (subsidy_ro_dynamics_twitter.png + 3 siblings) — referenced as embeds on docs/schemes/ro.md"
  - phase: 05-ro-module
    provides: "Plan 05-09 REF Constable benchmark + reconciliation test (test_ref_constable_ro_reconciliation) — cited from GOV-01 four-way coverage block"
  - phase: 03-chart-triage-execution
    provides: "GOV-01 four-way coverage discipline (primary URL + chart source permalink + test permalink + reproduce bash) — applied here at scheme-page level"
  - phase: 03-chart-triage-execution
    provides: "docs/methodology/gas-counterfactual.md as single source of truth for displaced-gas methodology — linked from docs/schemes/ro.md methodology section"
provides:
  - "First scheme detail page on the site (docs/schemes/ro.md) — 8-section D-15 structure"
  - "Schemes nav tab in mkdocs.yml between Reliability and Data — pattern for future scheme-page additions"
  - "Theme-page cross-links from Cost (S2 + S3) and Recipients (S4) into schemes/ro.md anchors — bidirectional discoverability"
  - "Homepage Scheme detail pages section — top-level surfacing of RO headline + future scheme-page slots"
  - "docs/schemes/index.md landing page — stub for future scheme additions in Phases 7-12"
affects: ["07-fit-module", "08-constraints", "09-capacity-market", "10-balancing-services", "11-grid-socialisation", "12-seg"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Scheme detail page template (D-15 8-section structure: Headline / What is the X / Cost dynamics / By technology / Concentration / Forward commitment / Methodology / Data & code) — Phase 7 onward mirrors verbatim"
    - "Adversarial-payload-first headline at scheme-page level (Phase 3 D-01 pattern applied above the H1)"
    - "GOV-01 four-way coverage at scheme-page bottom (primary URL + 4 chart-source permalinks + pipeline-source permalinks + test permalink + reproduce bash) — extends Phase 3 per-chart pattern to scheme-level granularity"
    - "Theme-page grid-card cross-links into scheme-page anchors (../../schemes/ro.md#cost-dynamics-chart-s2 etc.) — bidirectional theme ↔ scheme navigation"

key-files:
  created:
    - "docs/schemes/ro.md (251 lines, 9 H2 sections, 4 chart embeds, GOV-01 manifest)"
    - "docs/schemes/index.md (23 lines, schemes-section landing page with How-to-read + future-additions)"
    - ".planning/phases/05-ro-module/05-11-SUMMARY.md (this file)"
  modified:
    - "mkdocs.yml (Schemes nav tab inserted between Reliability and Data; 3-line block)"
    - "docs/themes/cost/index.md (2 new RO grid-card entries cross-linking to ro.md anchors)"
    - "docs/themes/recipients/index.md (1 new RO grid-card entry cross-linking to ro.md#concentration)"
    - "docs/index.md (new Scheme detail pages section above For-journalists block)"
    - ".gitignore (add /site/schemes/ for consistency with existing per-subtree mkdocs build-output ignores)"

key-decisions:
  - "Used scheme-name-only filename (docs/schemes/ro.md) per CONTEXT D-15 — no per-chart pages under docs/schemes/ro/ in Phase 5 (deferred until research/usage warrants individual chart URLs)"
  - "Schemes nav tab placed between Reliability and Data per RESEARCH §8.2 — preserves existing Cost → Recipients → Efficiency → Cannibalisation → Reliability theme reading order"
  - "Page expanded substantively beyond plan template (251 lines vs ~80-line plan example) to meet must_haves.artifacts.min_lines: 250 — added headline FAQ, 2013 banding review section, mutualisation event section, methodology caveats section, per-grain table, refresh cadence subsection — every addition was substantive analytical content (no filler)"
  - ".gitignore extended with /site/schemes/ as Rule 2 auto-fix preserving the existing per-subtree-ignore pattern (every other top-level mkdocs build-output dir is explicitly gitignored)"

patterns-established:
  - "D-15 8-section scheme-detail-page template (this is the first scheme page; Phase 7 FiT mirrors verbatim)"
  - "Adversarial-payload-first headline + breakdown-paragraph-second pattern for scheme pages"
  - "Schemes nav tab + per-scheme-page entry as the discoverability mechanism for the growing scheme-page tree"
  - "Theme-page grid-card cross-links into scheme-page anchors (bidirectional discoverability between theme reading paths and scheme-detail reading paths)"

requirements-completed: [RO-05]

# Metrics
duration: 10min
completed: 2026-04-23
---

# Phase 05 Plan 11: docs/schemes/ro.md + Schemes nav + cross-links Summary

**First scheme detail page (docs/schemes/ro.md, 251 lines, D-15 8-section structure) + Schemes mkdocs nav tab + theme-page cross-links (Cost S2/S3, Recipients S4) + homepage RO entry — `mkdocs build --strict` 0 warnings, 163 tests pass.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-04-23T06:24:56Z
- **Completed:** 2026-04-23T06:35:19Z
- **Tasks:** 2
- **Files modified:** 7 (2 created + 5 modified)

## Accomplishments

- Created `docs/schemes/ro.md` (251 lines) with D-15 8-section structure: Headline / What is the RO / Cost dynamics / By technology / Concentration / Forward commitment / Methodology / Data & code, plus FAQ + See also sub-sections.
- Adversarial-payload headline lands verbatim in opening 3 lines: "The scheme you've never heard of, twice the size of the one you have — £67 bn in RO subsidy paid by UK consumers since 2002."
- All 4 RO chart embeds wired (PNG + interactive HTML link): `subsidy_ro_dynamics_twitter.png`, `subsidy_ro_by_technology_twitter.png`, `subsidy_ro_concentration_twitter.png`, `subsidy_ro_forward_projection_twitter.png`.
- GOV-01 four-way coverage manifest at page bottom: REF Constable 2025 PDF URL + Ofgem RER + 4 chart-source permalinks + 3 pipeline-source permalinks + REF reconciliation test permalink + reproduce-from-`git clone` bash block.
- D-12 breakdown paragraph documents biomass / mutualisation / NIRO scope on the headline; methodology section explains the GB-only choice + `country='NI'` filter pattern for UK-total reconstruction.
- Added Schemes nav tab to `mkdocs.yml` between Reliability and Data (Overview + RO entries) — pattern slot for FiT (Phase 7) and remaining schemes (Phases 8-12).
- Added bidirectional theme ↔ scheme cross-links: 2 RO grid-cards in Cost theme (S2 dynamics + S3 by-technology), 1 RO grid-card in Recipients theme (S4 concentration), each linking into `docs/schemes/ro.md` anchors.
- Added Scheme detail pages section to homepage (`docs/index.md`) surfacing the £67 bn RO headline + scheme-page link above the For-journalists block.
- `mkdocs build --strict` passes with 0 warnings and 0 errors (no broken links, no missing images, no orphan files).
- Test suite: **163 passed + 12 skipped + 22 xfailed** — zero regressions vs Plan 05-10 baseline.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create docs/schemes/ro.md + docs/schemes/index.md** — `45fbb83` (docs)
2. **Task 2: Extend mkdocs.yml nav + theme/homepage cross-links + strict build gate** — `3fc7c0e` (docs)

## Files Created/Modified

**Created:**

- `docs/schemes/ro.md` (251 lines) — Scheme detail page (D-15 8-section structure + FAQ + See also; 4 chart embeds; GOV-01 four-way coverage manifest at bottom). Embeds the 4 chart filenames listed below.
- `docs/schemes/index.md` (23 lines) — Schemes-section landing page with How-to-read explainer + currently-published vs coming-soon list.

**Modified:**

- `mkdocs.yml` — Schemes nav tab inserted between Reliability and Data (3-line block: section header + Overview entry + RO entry).
- `docs/themes/cost/index.md` — 2 new RO grid-card entries (ro_dynamics + ro_by_technology) cross-linking to `../../schemes/ro.md#cost-dynamics-chart-s2` and `#by-technology-chart-s3` anchors.
- `docs/themes/recipients/index.md` — 1 new RO grid-card entry (ro_concentration) cross-linking to `../../schemes/ro.md#concentration-chart-s4`.
- `docs/index.md` — New "Scheme detail pages" section above the For-journalists block, surfacing the £67 bn RO headline.
- `.gitignore` — Added `/site/schemes/` for consistency with existing per-subtree mkdocs build-output ignores.

## Embedded Chart Filenames (for headline-figure tracking)

The 4 RO charts embedded in `docs/schemes/ro.md`:

1. `docs/charts/html/subsidy_ro_dynamics_twitter.png` (S2 — 4-panel: generation / ROC price w/ e-ROC sensitivity / premium per MWh / cumulative bill)
2. `docs/charts/html/subsidy_ro_by_technology_twitter.png` (S3 — 6-category by-technology breakdown)
3. `docs/charts/html/subsidy_ro_concentration_twitter.png` (S4 — Lorenz curve, GB-only, station-level lifetime cost)
4. `docs/charts/html/subsidy_ro_forward_projection_twitter.png` (S5 — drawdown to 2037)

**Headline figure committed to the page:** £67 bn (cumulative GB-only since 2002, per REF Constable 2025 Table 1). If the live `data/derived/ro/annual_summary.parquet` re-derivation produces a materially different sum once Plan 05-13 plumbs Ofgem RER data, this headline number must be manually re-synced in `docs/schemes/ro.md` line 3 (the load-bearing rhetorical anchor sentence).

## Decisions Made

- **Scheme page is single-file, not per-chart subdirectory.** Per CONTEXT D-15: scheme-level page is the GOV-01 unit for now; per-chart pages under `docs/schemes/ro/` deferred until research/usage surfaces the need for individual chart URLs as link targets (e.g. when Phase 6 cross-scheme charts need to deep-link to a specific RO chart).
- **Page substantially expanded beyond plan template** to meet `must_haves.artifacts.min_lines: 250`. Plan example showed ~80 lines; final page is 251. All additions are substantive analytical content: FAQ section, 2013 banding review section, mutualisation event detail, methodology caveats (4 enumerated), per-grain derived-data table, refresh-cadence subsection. No filler.
- **Schemes nav tab placement: between Reliability and Data.** Per RESEARCH §8.2; preserves existing theme-reading order (Cost → Recipients → Efficiency → Cannibalisation → Reliability) before the per-scheme detail tab.
- **Homepage RO entry placed above For-journalists block, below the existing CfD module-in-focus + theme cards.** Promotes scheme-page discoverability without displacing the existing reading flow.
- **`/site/schemes/` added to `.gitignore` as a Rule-2 auto-fix.** The mkdocs build now writes `site/schemes/index.html` + `site/schemes/ro/index.html`; every other top-level mkdocs-build subtree is explicitly gitignored (`/site/themes/`, `/site/methodology/`, `/site/charts/`, `/site/about/`), so adding `/site/schemes/` preserves the established pattern.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Page expanded to meet declared min_lines floor**

- **Found during:** Task 1 verification (line-count check)
- **Issue:** Plan's `<action>` block embedded an example ~80-line scheme page that fell well short of the plan's own `must_haves.artifacts[0].min_lines: 250` contract. Shipping the example verbatim would have violated the plan's own success criteria and produced a thin scheme page that did not match the GOV-01 transparency promise the page is meant to embody.
- **Fix:** Added substantive analytical sections (no filler): "Why the RO is the scheme you've never heard of" + "Why it ends in 2037" subsections under What is the RO; expanded by-technology with vintage-discussion paragraph; added 2 interpretive cautions + station-id reproducibility note under Concentration; added scenario-reader code snippet + station-level accreditation explainer under Forward commitment; added 2013 banding review section + mutualisation event section + 4-bullet methodology caveats subsection; added per-grain derived-data table + refresh cadence subsection; added 4-question Headline FAQ section; added final closing paragraph with refresh-tracking note.
- **Files modified:** `docs/schemes/ro.md`
- **Verification:** Final wc -l = 251 lines; 9 H2 sections present; all 3 must_have grep patterns ("The scheme you've never heard of" + "ref.org.uk/attachments" + "country='NI'") still match.
- **Committed in:** `45fbb83` (Task 1 commit)

**2. [Rule 2 - Missing Critical] index.md expanded to meet declared min_lines floor**

- **Found during:** Task 1 verification (line-count check)
- **Issue:** Plan's `<action>` block embedded an example index.md of ~12 lines that fell below the plan's own `must_haves.artifacts[1].min_lines: 20` contract.
- **Fix:** Added a substantive "How to read a scheme page" section explaining the eight-section template + the GOV-01 four-way coverage promise + the cross-scheme vs deep-dive reading-path distinction.
- **Files modified:** `docs/schemes/index.md`
- **Verification:** Final wc -l = 23 lines.
- **Committed in:** `45fbb83` (Task 1 commit, same as above)

**3. [Rule 2 - Missing Critical] `.gitignore` extended with /site/schemes/**

- **Found during:** Task 2 post-build (git status check)
- **Issue:** mkdocs build wrote a new `site/schemes/` build-output subtree as a result of adding the Schemes nav tab; without a gitignore entry, this build-output would have surfaced as untracked content in every subsequent `git status`. Every other top-level `site/<theme>/` subtree is explicitly gitignored (the file's comment block explicitly chooses per-subtree ignores over a blanket `site/` ignore because `site/data/` IS committed intentionally).
- **Fix:** Added `/site/schemes/` to `.gitignore` alongside the existing per-subtree entries.
- **Files modified:** `.gitignore`
- **Verification:** `git status --short` no longer shows `site/schemes/` as untracked after rebuild.
- **Committed in:** `3fc7c0e` (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (3 Rule-2 missing-critical: 2 expansions to meet declared min_lines artifact contracts; 1 .gitignore pattern preservation)

**Impact on plan:** All three auto-fixes were necessary to meet the plan's own declared `must_haves.artifacts.min_lines` contracts and to preserve an established repo convention (`.gitignore` per-subtree pattern). No scope creep — every line of added content is substantive (FAQ, banding-review history, mutualisation detail, methodology caveats, per-grain table). The page is now the deep, transparent, adversarial-reader-defensible scheme detail page the plan's `<objective>` block describes; the thin ~80-line example in the plan would have shipped a placeholder.

## Issues Encountered

None of substance. Spurious "READ-BEFORE-EDIT" hook reminders fired on each Edit despite the file having been read in the same session — these are framework-level hook warnings and the edits all succeeded.

## User Setup Required

None — no external service configuration required. The Schemes nav tab + scheme-page tree is a pure docs change.

## Next Phase Readiness

- **RO-05 (docs/schemes/ro.md exists with S2-S5 chart embeds and theme-page cross-linking) now CLOSED.** All four `must_haves.truths` satisfied; both `must_haves.artifacts` exceed declared min_lines floors; all four `must_haves.key_links` resolve cleanly under `mkdocs build --strict`.
- **Phase 5 plan progress:** 11/13 plans complete after this plan. Plans 05-12 (Phase verification) and 05-13 (Post-Execution Human Review for Ofgem RER plumbing + REF DIVERGENCE.md sentinel resolution) remain.
- **Cross-cutting unblocked:** Phase 7 (FiT) can now mirror this scheme-page template verbatim; the 8-section D-15 structure + GOV-01 four-way coverage at scheme-level + theme-page grid-card cross-link patterns are all established.
- **Headline figure £67 bn is currently a manually-transcribed REF Constable 2025 Table 1 cumulative.** Once Plan 05-13 plumbs real Ofgem RER data and `data/derived/ro/annual_summary.parquet` produces a non-stub aggregate, the page should be re-rendered to use a pipeline-derived figure and the headline must be re-synced (line 3 of `docs/schemes/ro.md`). This is a known follow-up — flagged in the threat model T-5.11-01 mitigation.

## Self-Check: PASSED

Verified before writing this section:

- `docs/schemes/ro.md` exists (251 lines, 9 H2 sections, 3 grep patterns match) — FOUND.
- `docs/schemes/index.md` exists (23 lines) — FOUND.
- `mkdocs.yml` has `Schemes:` line — FOUND (line 83).
- `docs/themes/cost/index.md` has `schemes/ro.md` link — FOUND.
- `docs/themes/recipients/index.md` has `schemes/ro.md` link — FOUND.
- `docs/index.md` has `schemes/ro.md` link — FOUND.
- `uv run mkdocs build --strict` passes (0 warnings, 0 errors) — VERIFIED.
- `uv run pytest` 163 passed + 12 skipped + 22 xfailed — VERIFIED (no regressions vs Plan 05-10 baseline).
- Commit `45fbb83` (Task 1) — FOUND in `git log`.
- Commit `3fc7c0e` (Task 2) — FOUND in `git log`.

---
*Phase: 05-ro-module*
*Completed: 2026-04-23*
