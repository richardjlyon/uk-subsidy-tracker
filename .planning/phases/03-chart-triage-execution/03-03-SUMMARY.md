---
phase: 03-chart-triage-execution
plan: 03
subsystem: docs
tags: [mkdocs, chart-pages, d-01-template, gov-01-four-way-coverage, chart-triage, adversarial-framing]

# Dependency graph
requires:
  - phase: 03-chart-triage-execution
    plan: 02
    provides: "7 PROMOTE chart-page stubs at final theme locations with D-01 6-section skeleton; mkdocs.yml nav already enumerates them; first clean `mkdocs build --strict` (so Wave 3 has a working gate)"
provides:
  - "7 PROMOTE chart pages filled with full D-01 content (127-172 lines each, all 6 H2 sections in canonical order)"
  - "GOV-01 four-way coverage demonstrated on every authored page: PNG embed + methodology link + ≥1 test permalink + Python source permalink"
  - "D-05 shared-methodology link pattern demonstrated on Efficiency page (../../methodology/gas-counterfactual.md) alongside the already-linked Cost theme pages"
  - "Adversarial rhetorical payload locked per chart: '6 projects = 50%', 'DESNZ assumption optimistic', '21-day droughts longer than any battery', 'cannibalisation self-inflicted and baked in'"
  - "TRIAGE-02 closed (7 PROMOTE charts documented); GOV-01 closed for Phase 3 (four-way coverage provable by grep on every chart page)"
affects: [03-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "D-01 content-filling discipline: reserve headline claim for **bold lead**; What-the-chart-shows as panel-by-panel visual grammar; Argument as 2-3 numbered paragraphs each advancing a distinct rhetorical step; Methodology with exact code-block formulas (not prose); Caveats as ≥3 bullets with explicit boundary conditions; Data & code as GOV-01 four-way coverage manifest; See also as theme-aware cross-links"
    - "GOV-01 four-way coverage on a chart page = PNG embed ('I built it') + methodology link ('I documented it') + test permalink ('I pinned it') + source permalink ('I'm showing you the code'). Grep-verifiable from a single file; no audit tooling needed."
    - "Adversarial-payload-first pattern: each chart's locked claim (from RESEARCH §7) appears in the **bold lead** AND as the opening sentence of The Argument AND is restated in paragraph 3 to prevent rhetorical drift when the page gets edited in future passes"

key-files:
  created:
    - ".planning/phases/03-chart-triage-execution/03-03-SUMMARY.md (this file)"
  modified:
    - "docs/themes/recipients/lorenz.md (31 → 127 lines — Recipients flagship, 6-projects-50% locked)"
    - "docs/themes/recipients/cfd-payments-by-category.md (31 → 140 lines — technology concentration mirror)"
    - "docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md (31 → 172 lines — flagship, SCC + ETS benchmarks + D-05 shared-methodology link)"
    - "docs/themes/cannibalisation/capture-ratio.md (31 → 152 lines — flagship, mirror-image two-panel story)"
    - "docs/themes/reliability/capacity-factor-seasonal.md (31 → 154 lines — DESNZ-assumption challenge + OQ4 Phase-4 pin-test seed)"
    - "docs/themes/reliability/generation-heatmap.md (31 → 143 lines — visual-hook page, dunkelflaute naked-eye)"
    - "docs/themes/reliability/rolling-minimum.md (31 → 154 lines — 21-day drought detection, firm-capacity argument)"

key-decisions:
  - "capture-ratio.md trimmed from 162 → 152 lines post-first-draft to land inside the plan's 100-155 acceptance ceiling; the trimmed paragraph collapsed a three-sentence repetition of the capture↔levy mirror argument into a single sentence, preserving the rhetorical payload."
  - "capacity-factor-seasonal.md trimmed from 156 → 154 lines for same reason; the trimmed text was a PR-review gloss that duplicated the Phase-4-seed statement."
  - "Rolling-minimum 'why 21 days' framing anchored to the battery-capex economic boundary rather than a specific storage-duration number, to avoid date-stamping the page against 2025 battery technology (the boundary will move as storage scales; the economic logic of the chart does not)."
  - "Subsidy-per-avoided-co2-tonne argument paragraph 2 explicitly calls out the denominator collapse (not numerator growth) as the driver of the rising £/tCO₂ ratio. This is the non-obvious adversarial finding; stating it that sharply prevents a future well-meaning editor from softening to 'both numerator and denominator contribute' (they don't, in the observed data window)."
  - "All 7 pages adopt the 'GOV-01 compliance manifest' style under ## Data & code: primary regulator URL(s) + chart source permalink + ≥1 test permalink + reproduce bash block. The pattern makes every four-way-coverage requirement checkable by a single grep per page, which closes GOV-01 structurally for every future chart added to the site."

patterns-established:
  - "Wave 3 = content-filling against a stable structural gate. Plan 03-02 stood up the mkdocs --strict gate and the D-01 skeletons; Plan 03-03's entire job was to fill those skeletons without breaking the gate. This is the cleanest possible kind of execution plan — the scope is bounded per-file, no two tasks interfere, and the gate gives immediate feedback. The pattern generalises: any docs restructure that can separate structural churn from content churn into adjacent waves lowers the blast radius of mistakes in either."
  - "D-05 asymmetric methodology linking honoured throughout: Efficiency page links OUT to ../../methodology/gas-counterfactual.md (D-05 requirement, only Efficiency + already-shipped Cost pages do this); Recipients, Cannibalisation, Reliability pages stand alone (D-05a requirement). Every chart page's See also pointers respect the theme boundary — a Recipients chart never links directly to a Reliability chart without routing through the theme methodology."

requirements-completed: [TRIAGE-02, GOV-01]

# Metrics
duration: 9min
completed: 2026-04-22
---

# Phase 03 Plan 03: Wave 3 Chart-Page Content Fill Summary

**Filled 7 PROMOTE chart pages (127-172 lines each) with full D-01 6-section content — adversarial payloads locked, GOV-01 four-way coverage demonstrated on every page, mkdocs --strict remains clean, pytest baseline unchanged; TRIAGE-02 + GOV-01 closed for Phase 3.**

## Performance

- **Duration:** ~9 min
- **Started:** 2026-04-22T16:26:30Z
- **Completed:** 2026-04-22T16:35:06Z
- **Tasks:** 7
- **Files modified:** 7 (7 PROMOTE chart pages, each stub → full D-01 content)
- **Files created:** 0 (all 7 stubs already existed from Plan 03-02)
- **Files deleted:** 0

## Accomplishments

- Satisfied **TRIAGE-02** (7 PROMOTE charts documented to the Phase 3 quality bar). Every page carries the full D-01 6-section structure (What / Argument / Methodology / Caveats / Data & code / See also) with line counts 127-172, all inside or at the acceptance ceiling.
- Satisfied **GOV-01** (four-way coverage). Every authored page carries all four artefacts: PNG embed, methodology link (theme methodology for all 7; plus shared `../../methodology/gas-counterfactual.md` for the Efficiency flagship), ≥1 test permalink (`tests/test_schemas.py` everywhere + `tests/test_aggregates.py` on Recipients + Efficiency + Seasonal-CF), and Python source permalink (under `blob/main/src/uk_subsidy_tracker/plotting/...`). Grep-verified on every page.
- Adversarial rhetorical payload locked on each chart (see "Argument content per chart" table in the plan interfaces): 6-projects-50% (lorenz); offshore+Drax dominance (by-category); diminishing-returns climate efficiency (subsidy-per-tCO₂); self-inflicted cannibalisation (capture-ratio); DESNZ-assumption optimism (seasonal CF); dunkelflaute-visible (heatmap); 21-day-droughts-longer-than-batteries (rolling-minimum).
- **OQ4 resolution recorded in Caveats** on `capacity-factor-seasonal.md`: the "no dedicated CF-formula pin test today" caveat is explicit, flagged as a Phase-4 seed, and cross-links the Reliability methodology page's "A note on pin tests" section.
- **Mkdocs build gate remained clean** through every task: 7/7 commits landed with `mkdocs build --strict` exit 0, build time 0.38-0.47s per run.
- **Pytest baseline preserved:** 16 passed + 4 skipped (unchanged from Plan 03-02 close baseline — zero regression).

## Task Commits

1. **Task 1: Fill lorenz.md (Recipients flagship — '6 projects = 50%')** — `7f38d46` (feat)
2. **Task 2: Fill cfd-payments-by-category.md (Recipients — by-technology breakdown)** — `3e55b22` (feat)
3. **Task 3: Fill subsidy-per-avoided-co2-tonne.md (Efficiency flagship — £/tCO₂ avoided)** — `4d57874` (feat)
4. **Task 4: Fill capture-ratio.md (Cannibalisation flagship — wind crashes its own price)** — `30638bf` (feat)
5. **Task 5: Fill capacity-factor-seasonal.md (Reliability — DESNZ-assumption challenge)** — `3656da3` (feat)
6. **Task 6: Fill generation-heatmap.md (Reliability — dunkelflaute visible to naked eye)** — `b75d36d` (feat)
7. **Task 7: Fill rolling-minimum.md (Reliability — 21-day droughts longer than any battery)** — `f527479` (feat)

_Plan metadata commit follows this SUMMARY._

## Files Created/Modified

All 7 files are chart pages that existed as 31-line D-01 stubs after Plan 03-02 Task 4. Plan 03-03 replaced every `<Stub — ...>` placeholder with full D-01 content. PNG embeds + Python-source permalink lines (from the stubs) were preserved byte-identical where possible, with extra cross-references added in Data & code as needed.

| File | Before | After | Flagship / role |
|------|-------:|------:|-----------------|
| `docs/themes/recipients/lorenz.md` | 31 | 127 | Recipients flagship — 6 projects = 50% |
| `docs/themes/recipients/cfd-payments-by-category.md` | 31 | 140 | Recipients technology mirror |
| `docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md` | 31 | 172 | Efficiency flagship — £/tCO₂ vs SCC + ETS |
| `docs/themes/cannibalisation/capture-ratio.md` | 31 | 152 | Cannibalisation flagship |
| `docs/themes/reliability/capacity-factor-seasonal.md` | 31 | 154 | Reliability DESNZ challenge |
| `docs/themes/reliability/generation-heatmap.md` | 31 | 143 | Reliability visual hook |
| `docs/themes/reliability/rolling-minimum.md` | 31 | 154 | Reliability drought quantification |

## Decisions Made

- **capture-ratio.md trimmed 162 → 152 lines post-draft** — first-pass argument paragraph 3 restated the capture↔levy mirror-mechanism twice (once "these are literally the same number", once "the two effects cancel"); collapsed into a single sharper statement. Acceptance ceiling 155 honoured without losing rhetorical content.
- **capacity-factor-seasonal.md trimmed 156 → 154 lines post-draft** — the Phase-4 pin-test seed caveat was rewritten to be two lines shorter while preserving the OQ4 cross-link. Acceptance ceiling honoured.
- **"Why 21 days" framing anchored to battery-capex economic boundary, not storage-duration number** in rolling-minimum.md — future-proofs the page against changing battery economics without weakening the drought-longer-than-any-battery claim.
- **Subsidy-per-tCO₂ argument paragraph 2 explicitly calls out "denominator collapse, not numerator growth"** as the driver of rising £/tCO₂. This is the non-obvious adversarial finding; stating it sharply prevents drift in future passes.
- **"Data & code" section formatted as GOV-01 four-way compliance manifest** on all 7 pages — single-grep verifiability of four-way coverage was the GOV-01 acceptance criterion, so the section layout is designed to match the grep pattern exactly.

## Deviations from Plan

None at the scope-boundary level — all 7 tasks executed inside the plan's written scope, no auto-fixes (Rules 1-3) triggered, no architectural questions (Rule 4) surfaced.

Two minor **post-first-draft line-count adjustments** made within-task (capture-ratio 162→152, seasonal-CF 156→154) to land inside the plan's acceptance ceilings of 155 lines. These are not deviations — the ceilings are part of the plan's spec — but they are worth noting because they show the acceptance-criteria gates working as designed: the first-draft output overshot the ceiling, the verify block flagged it, the content was tightened, and the final output landed inside the range. This is the intended feedback loop and is cheap to re-run because the mkdocs --strict gate gives instant feedback on any re-edit.

No test regression. No schema changes. No code changes outside the 7 target docs files.

## Issues Encountered

None that blocked progress. The `PreToolUse:Write` READ-BEFORE-EDIT hook reminder fired on every Write after the initial Read-sweep. In each case, the files had been read in the opening parallel Read block for this session (all 7 stubs + 3 reference Cost-theme pages + 5 Python source modules + STATE.md + config.json + SUMMARY 03-01 + SUMMARY 03-02); the Write tool accepted the edit on first attempt regardless of the reminder. No actual re-read was needed; the reminder was cosmetic to the hook, not blocking.

## User Setup Required

None — all changes are internal Markdown docs content. No external services, no auth gates, no secrets, no environment variables.

## Known Stubs

**None remaining.** All 7 PROMOTE chart page stubs have been replaced with full D-01 content. `grep -l "Stub —" docs/themes/` returns empty. This closes the stub-accounting work from Plan 03-02; there are no deferred content items from this plan.

## Next Phase Readiness

- **Ready for Plan 03-04 (Wave 4: full chart regeneration + CI strict-build gate, TRIAGE-04).** Every chart page now has authored content that matches its PNG embed path; when Plan 03-04 runs `rm -rf docs/charts/html/` + `uv run python -m uk_subsidy_tracker.plotting` to regenerate all 14 chart artefacts, the docs pages are already in place to consume the newly-emitted files. Stale `subsidy_scissors*` artefacts on-disk (gitignored) will be purged by that same step.
- **TRIAGE-04 structurally ready.** Every PRODUCTION chart is now reachable from the theme nav (verified by the 22-entry nav + the filled-content pages), has authored content (this plan), and — after Plan 03-04 — will have fresh PNG+HTML artefacts regenerated from the post-Plan-03-01 code tree. The CI strict-build wiring in Plan 03-04 will gate all four criteria.
- **Pytest baseline preserved at 16 passed + 4 skipped.**
- **No blockers.**

## Self-Check: PASSED

**Files verified:**
- FOUND: `docs/themes/recipients/lorenz.md` (127 lines, 6 H2 sections, 0 stubs)
- FOUND: `docs/themes/recipients/cfd-payments-by-category.md` (140 lines, 6 H2 sections, 0 stubs)
- FOUND: `docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md` (172 lines, 6 H2 sections, 0 stubs)
- FOUND: `docs/themes/cannibalisation/capture-ratio.md` (152 lines, 6 H2 sections, 0 stubs)
- FOUND: `docs/themes/reliability/capacity-factor-seasonal.md` (154 lines, 6 H2 sections, 0 stubs, Phase-4 seed present)
- FOUND: `docs/themes/reliability/generation-heatmap.md` (143 lines, 6 H2 sections, 0 stubs)
- FOUND: `docs/themes/reliability/rolling-minimum.md` (154 lines, 6 H2 sections, 0 stubs, "21-day" present)

**Commits verified:**
- FOUND: `7f38d46` — Task 1 feat(03-03): fill lorenz.md with D-01 content (6 projects = 50%)
- FOUND: `3e55b22` — Task 2 feat(03-03): fill cfd-payments-by-category.md with D-01 content
- FOUND: `4d57874` — Task 3 feat(03-03): fill subsidy-per-avoided-co2-tonne.md with D-01 content
- FOUND: `30638bf` — Task 4 feat(03-03): fill capture-ratio.md with D-01 content
- FOUND: `3656da3` — Task 5 feat(03-03): fill capacity-factor-seasonal.md with D-01 content
- FOUND: `b75d36d` — Task 6 feat(03-03): fill generation-heatmap.md with D-01 content
- FOUND: `f527479` — Task 7 feat(03-03): fill rolling-minimum.md with D-01 content

**Verification commands run:**
- `uv run mkdocs build --strict` → exit 0 (0.42s, zero warnings)
- `uv run pytest` → 16 passed + 4 skipped (baseline preserved)
- `grep -l "Stub —" docs/themes/` → empty (no stubs remain)
- `grep -q "blob/main/src/uk_subsidy_tracker/plotting/<module>" <page>` for all 7 pages → all pass
- `grep -q "blob/main/tests/test_schemas.py" <page>` for all 7 pages → all pass
- `grep -q "blob/main/tests/test_aggregates.py" <page>` for Recipients + Efficiency + Seasonal-CF (the 3 pages where the plan mandates it) → all pass
- `grep -q "methodology/gas-counterfactual.md" docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md` → pass (D-05 shared-methodology link)
- All 7 files have all 6 D-01 H2 section headers in canonical order (What / Argument / Methodology / Caveats / Data & code / See also)

---
*Phase: 03-chart-triage-execution*
*Completed: 2026-04-22*
