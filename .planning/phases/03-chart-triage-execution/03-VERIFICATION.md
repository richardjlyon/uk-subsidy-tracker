---
phase: 03-chart-triage-execution
verified: 2026-04-22T17:10:58Z
status: passed
score: 5/5 success criteria verified (+ 5/5 requirements satisfied)
overrides_applied: 0
re_verification: null
advisory:
  - source: 03-REVIEW.md
    count: 19
    severity:
      critical: 0
      warning: 8
      info: 11
    impact: none_on_phase_3_goal
    disposition: record_as_phase_4_plus_follow_up
---

# Phase 3: Chart Triage Execution — Verification Report

**Phase Goal:** The CfD chart set is tidy and fully documented, with every PRODUCTION chart reachable from a five-theme navigation structure.

**Verified:** 2026-04-22T17:10:58Z
**Status:** passed
**Re-verification:** No — initial verification after user-approved human-verify checkpoint in Plan 03-04 Task 5.

---

## Goal Achievement

The phase goal is achieved. All five ROADMAP Success Criteria verify green against the current working tree. All five declared REQ-IDs (TRIAGE-01, TRIAGE-02, TRIAGE-03, TRIAGE-04, GOV-01) have concrete implementation evidence.

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC-1 | `scissors.py` and `bang_for_buck_old.py` are absent from the working tree; sole in-tree references are inside `tests/test_docs_structure.py` (TRIAGE-01 regression guard) | VERIFIED | `test ! -f src/uk_subsidy_tracker/plotting/subsidy/{scissors,bang_for_buck_old}.py` → exit 0. `grep -rn "scissors\|bang_for_buck_old" src/ tests/` surfaces only 3 lines inside `tests/test_docs_structure.py:40-43` (the intended exception). |
| SC-2 | All 7 PROMOTE charts (`cfd_payments_by_category`, `lorenz`, `subsidy_per_avoided_co2_tonne`, `capture_ratio`, `capacity_factor/seasonal`, `intermittency/generation_heatmap`, `intermittency/rolling_minimum`) have narrative + methodology + test reference + source-file link | VERIFIED | All 7 pages present at final theme paths with line counts 127-172. Every page carries all 6 D-01 H2 sections, a Python source permalink under `blob/main/src/uk_subsidy_tracker/plotting/...`, ≥1 `blob/main/tests/test_...py` test permalink, a `_twitter.png` PNG embed, and a methodology link. No `<Stub — ...>` placeholders remain. |
| SC-3 | `docs/themes/` contains 5 directories (`cost`, `recipients`, `efficiency`, `cannibalisation`, `reliability`), each with `index.md` + `methodology.md` | VERIFIED | All 5 theme directories exist; each has both files. Every `index.md` contains a `<div class="grid cards" markdown>` gallery block per D-02. |
| SC-4 | Every PRODUCTION chart is navigable from its theme page — no orphaned chart pages | VERIFIED | `mkdocs.yml` nav enumerates all 10 PRODUCTION chart pages across the 5 themes (3 Cost + 2 Recipients + 1 Efficiency + 1 Cannibalisation + 3 Reliability). `mkdocs build --strict` with `validation.nav.omitted_files: warn` succeeded — any nav-orphan docs page would have surfaced as an error. Homepage `docs/index.md` links to all 5 theme indices. User explicitly approved SC-4 visual check during Plan 03-04 Task 5 human-verify checkpoint. |
| SC-5 | `mkdocs build --strict` passes with the full theme structure | VERIFIED | `uv run mkdocs build --strict` exits 0 in 0.44s at verification time, zero warnings, zero errors. The `docs` CI job runs the same command on every push + PR (`.github/workflows/ci.yml:43-44`). |

**Score:** 5/5 truths verified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/uk_subsidy_tracker/plotting/subsidy/scissors.py` | Deleted | VERIFIED | Absent from working tree; preserved in git history (deletion commit `c5cc229`). |
| `src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck_old.py` | Deleted | VERIFIED | Absent from working tree; preserved in git history (same commit). |
| `src/uk_subsidy_tracker/plotting/__main__.py` | 14 imports + 14 calls, no scissors reference | VERIFIED | `grep -c "^from uk_subsidy_tracker.plotting"` returns 14 (was 15). No `scissors` grep match. |
| `src/uk_subsidy_tracker/counterfactual.py` | Docstring freed of scissors reference | VERIFIED | No `scissors` grep match anywhere in module. |
| `mkdocs.yml` (theme.features) | 10-entry D-06 target ordering, `toc.integrate` replaces `toc.follow` | VERIFIED | 10 features in locked order. `navigation.tabs.sticky`, `navigation.top`, `navigation.instant`, `content.tooltips`, `toc.integrate` present. `toc.follow` absent. |
| `mkdocs.yml` (validation block) | Root-level `validation:` with `nav.omitted_files: warn` | VERIFIED | Present at lines 43-53. |
| `mkdocs.yml` (nav block) | 22-entry 5-theme structure | VERIFIED | `grep -cE "themes/(cost\|recipients\|efficiency\|cannibalisation\|reliability)/.*\.md"` returns 20 theme-scoped entries + Home + Methodology + About = 22-entry structure. No `charts/subsidy/` or `charts/index.md` references remain. |
| `docs/themes/cost/{index,methodology}.md` | Present with D-02 / D-05 structure | VERIFIED | 51 + 26 lines. Methodology links to `../../methodology/gas-counterfactual.md` (D-05). |
| `docs/themes/recipients/{index,methodology}.md` | Present with D-02 / D-05a structure | VERIFIED | 31 + 21 lines. Methodology stands alone (D-05a — no gas-counterfactual link by design). |
| `docs/themes/efficiency/{index,methodology}.md` | Present; methodology links to shared gas-counterfactual | VERIFIED | 25 + 24 lines. Methodology cites DEFRA SCC + UK ETS benchmarks + links to `../../methodology/gas-counterfactual.md`. |
| `docs/themes/cannibalisation/{index,methodology}.md` | Present with D-05a (no gas-counterfactual link) | VERIFIED | 25 + 21 lines. Methodology stands alone. |
| `docs/themes/reliability/{index,methodology}.md` | Present; methodology includes OQ4 pin-test seed | VERIFIED | 43 + 31 lines. Methodology contains "A note on pin tests" paragraph (OQ4 seed). |
| `docs/themes/cost/{cfd-dynamics,cfd-vs-gas-cost,remaining-obligations}.md` | `git mv`'d from `docs/charts/subsidy/`, PNG paths rewritten | VERIFIED | All 3 present at new paths (105, 169, 114 lines). PNG paths use `../../charts/html/...`. `docs/charts/subsidy/` directory and `docs/charts/index.md` both deleted. |
| `docs/themes/recipients/lorenz.md` | D-01 6-section + GOV-01 four-way | VERIFIED | 127 lines, 6 D-01 H2 sections, PNG + source + test permalinks + methodology link all present. |
| `docs/themes/recipients/cfd-payments-by-category.md` | D-01 6-section + GOV-01 four-way | VERIFIED | 140 lines, all 6 sections, four-way coverage. |
| `docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md` | D-01 + D-05 shared-methodology link | VERIFIED | 172 lines, all 6 sections, shared `../../methodology/gas-counterfactual.md` link + theme methodology link, two test permalinks (`test_schemas.py`, `test_aggregates.py`), PNG embed uses `subsidy_cost_per_avoided_co2_tonne_twitter.png`. |
| `docs/themes/cannibalisation/capture-ratio.md` | D-01 + GOV-01 | VERIFIED | 152 lines, all 6 sections, four-way coverage. |
| `docs/themes/reliability/capacity-factor-seasonal.md` | D-01 + DESNZ challenge + OQ4 Phase-4 seed | VERIFIED | 154 lines, all 6 sections, DESNZ references present, OQ4 Phase-4 pin-test seed recorded in Caveats. |
| `docs/themes/reliability/generation-heatmap.md` | D-01 + GOV-01 | VERIFIED | 143 lines, all 6 sections, four-way coverage. |
| `docs/themes/reliability/rolling-minimum.md` | D-01 + "21-day" drought framing | VERIFIED | 154 lines, "21-day" string present in argument, four-way coverage. |
| `docs/charts/html/` (regenerated) | 14 `_twitter.png` files, zero scissors artefacts | VERIFIED | `ls docs/charts/html/*_twitter.png \| wc -l` returns 14; `grep -c scissors` on directory listing returns 0. All 14 expected PNGs present: 7 subsidy + 2 capacity_factor + 3 intermittency + 2 cannibalisation. |
| `.github/workflows/ci.yml` | Two sibling jobs `test` + `docs`; docs runs chart regen then `mkdocs build --strict` | VERIFIED | YAML parses. `docs` job at lines 26-44 contains both `Regenerate charts` step and `Build docs --strict` step. Existing `test` job untouched. |
| `tests/test_docs_structure.py` | 7 invariant tests | VERIFIED | 60 lines, 7 `test_*` functions. `uv run pytest tests/test_docs_structure.py` → 7 passed in 0.01s. |
| `.planning/STATE.md` | Phase-3 closure + OQ4/OQ5 seeds | VERIFIED | Frontmatter: `completed_phases: 3`, `stopped_at: Phase 3 complete`. Progress bar 3/12. Both Phase-4+ seeds present (`Author docs/abbreviations.md glossary` + `Add CF-formula pin test`). Next-command advanced to `/gsd-plan-phase 4`. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/uk_subsidy_tracker/plotting/__main__.py` | 14 chart modules | `from uk_subsidy_tracker.plotting.*` imports | WIRED | 14 imports + 14 calls; `uv run python -m uk_subsidy_tracker.plotting` regenerated all 14 PNGs cleanly at Plan 03-04 time; `uv run pytest` remains green. |
| `mkdocs.yml` nav | 22-entry theme tree | Material navigation | WIRED | Every nav entry resolves to an existing `.md` file (confirmed by `mkdocs --strict` exit 0 under `validation.nav.not_found: warn`). |
| `docs/index.md` | 5 theme indices | "Explore by theme" section | WIRED | All 5 theme links (`themes/{cost,recipients,efficiency,cannibalisation,reliability}/index.md`) present; no stale `charts/subsidy/*` or `charts/index.md` refs. |
| `docs/themes/cost/methodology.md` | `docs/methodology/gas-counterfactual.md` | `../../methodology/gas-counterfactual.md` | WIRED | D-05 shared-methodology link present. |
| `docs/themes/efficiency/methodology.md` | `docs/methodology/gas-counterfactual.md` | `../../methodology/gas-counterfactual.md` | WIRED | D-05 shared-methodology link present. |
| `docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md` | `docs/methodology/gas-counterfactual.md` | `../../methodology/gas-counterfactual.md` | WIRED | Efficiency flagship chart page links to shared methodology (per D-05). |
| Every PROMOTE chart page | GitHub source permalink | `blob/main/src/uk_subsidy_tracker/plotting/<module>.py` | WIRED | Grep-verified on all 7 pages. |
| Every PROMOTE chart page | GitHub test permalink | `blob/main/tests/test_<name>.py` | WIRED | Grep-verified on all 7 pages (`test_schemas.py` everywhere; `test_aggregates.py` on Recipients + Efficiency + Seasonal-CF). |
| `.github/workflows/ci.yml docs` job | mkdocs + plotting orchestrator | `uv run --frozen python -m uk_subsidy_tracker.plotting` → `uv run --frozen mkdocs build --strict` | WIRED | Sequential steps in the `docs` job will run on every push/PR. Existing `test` job untouched. |
| `tests/test_docs_structure.py` | Phase-3 invariants | Filesystem + grep assertions | WIRED | 7 tests pass in 0.01s. No import from `uk_subsidy_tracker.*` — tests act on filesystem only. |

### Data-Flow Trace (Level 4)

Phase 3 produces documentation and configuration artefacts, not runtime dynamic data. The closest analogue to dynamic data is the chart PNG/HTML tree under `docs/charts/html/`, which is a build output, not a runtime state. It was regenerated clean at Plan 03-04 Task 1 and will be regenerated on every CI run by the `docs` job. Level 4 trace is not applicable to any component in this phase — all artefacts are static files.

### Behavioural Spot-Checks

| Behaviour | Command | Result | Status |
|-----------|---------|--------|--------|
| `mkdocs build --strict` produces clean build | `uv run mkdocs build --strict` | `INFO - Documentation built in 0.44 seconds`; exit 0; zero WARNING lines | PASS |
| Phase-3 structural regression guard passes | `uv run pytest tests/test_docs_structure.py -v` | `7 passed in 0.01s` | PASS |
| Full pytest baseline preserved | `uv run pytest` | `23 passed, 4 skipped in 1.98s` (16 pre-existing + 7 new test_docs_structure) | PASS |
| CI workflow YAML parses + has expected jobs | `python -c "import yaml; ..."` | `OK` — both `test` and `docs` jobs present; docs job has `mkdocs build --strict` step | PASS |
| Chart orchestrator produces 14 PNGs, zero scissors | `ls docs/charts/html/*_twitter.png \| wc -l` ; `grep -c scissors` | `14` ; `0` | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| TRIAGE-01 | 03-01, 03-04 | CUT files deleted (scissors.py, bang_for_buck_old.py); preserved in git history only | SATISFIED | Files absent; test_cut_files_deleted passing; regression guard in `tests/test_docs_structure.py`. |
| TRIAGE-02 | 03-03 | Docs pages for 7 PROMOTE charts | SATISFIED | All 7 pages filled with full D-01 content (127-172 lines); stubs gone. |
| TRIAGE-03 | 03-02 | 5-theme docs tree with narrative index + methodology + per-chart pages | SATISFIED | All 5 theme directories with index + methodology + chart pages; 3 existing CfD pages relocated via `git mv`. |
| TRIAGE-04 | 03-02, 03-04 | Every PRODUCTION chart reachable from its theme page navigation | SATISFIED | 22-entry mkdocs nav; `validation.nav.omitted_files: warn`; `mkdocs build --strict` green as CI gate. |
| GOV-01 | 03-03 | Every PRODUCTION chart carries narrative + methodology + test + source-file link | SATISFIED | Four-way coverage grep-verified on all 7 PROMOTE pages + existing 3 Cost pages (verified via `test_gov01_four_way_coverage`). |

No requirements mapped to Phase 3 in `.planning/REQUIREMENTS.md` are orphaned — all 5 declared IDs (TRIAGE-01..04 + GOV-01) appear in at least one plan's `requirements:` frontmatter field and all 5 have concrete implementation evidence in the codebase.

### Anti-Patterns Found

Scan executed on every file listed across the 4 plan SUMMARY `key-files` sections plus the regenerated `docs/charts/html/` manifest.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| _none_ | — | No `TODO`, `FIXME`, `XXX`, `HACK`, `PLACEHOLDER`, empty-handler, or stub patterns found in Phase-3 modified files. | — | — |

All 7 PROMOTE chart pages contain zero `<Stub — ...>` placeholders. `grep -l "Stub —" docs/themes/` returns empty. No in-tree references to the CUT modules beyond the intended regression guard.

### Data-Flow / Rendering (Sub-Level Spot Check)

The 7 PROMOTE chart pages each embed a PNG whose file stem maps to a generator module listed in `src/uk_subsidy_tracker/plotting/__main__.py`:

| Page | Embedded PNG | Generator Module | PNG Regenerated |
|------|--------------|------------------|-----------------|
| lorenz.md | `subsidy_lorenz_twitter.png` | `plotting/subsidy/lorenz.py` | YES |
| cfd-payments-by-category.md | `subsidy_cfd_payments_by_category_twitter.png` | `plotting/subsidy/cfd_payments_by_category.py` | YES |
| subsidy-per-avoided-co2-tonne.md | `subsidy_cost_per_avoided_co2_tonne_twitter.png` | `plotting/subsidy/subsidy_per_avoided_co2_tonne.py` | YES |
| capture-ratio.md | `cannibalisation_capture_ratio_twitter.png` | `plotting/cannibalisation/capture_ratio.py` | YES |
| capacity-factor-seasonal.md | `capacity_factor_seasonal_twitter.png` | `plotting/capacity_factor/seasonal.py` | YES |
| generation-heatmap.md | `intermittency_generation_heatmap_twitter.png` | `plotting/intermittency/generation_heatmap.py` | YES |
| rolling-minimum.md | `intermittency_rolling_minimum_twitter.png` | `plotting/intermittency/rolling_minimum.py` | YES |

All 7 PNG paths resolve to files present on disk in `docs/charts/html/` (verified by `test -f`). No broken image links.

### Human Verification Required

None remaining. Plan 03-04 Task 5 executed the phase-exit human-verify checkpoint during execution; the user responded "approved" after running all 4 automated SC checks (SC-1, SC-2, SC-3, SC-5) locally and declaring SC-4 visually satisfied from the mkdocs-serve check in Wave 2/3 iterations plus the post-reconciliation strict-build confirmation. Automated re-run of all 5 SC checks at verification time reproduces those results with zero deviation. No remaining visual, real-time, or external-service checks are required to confirm the Phase-3 goal.

### Gaps Summary

No gaps blocking goal achievement.

---

## Code-Review Findings (Advisory — Non-Blocking)

`.planning/phases/03-chart-triage-execution/03-REVIEW.md` was produced after Plan 03-04 and catalogues 19 findings (0 critical, 8 warning, 11 info). None of these invalidate the Phase-3 structural goal. They are all prose-level correctness issues or minor code-polish items worth tracking forward, not gaps against the ROADMAP Success Criteria.

**Most consequential review findings (WR-01, WR-02, WR-03) — worth explicit tracking:**

| Finding | Files | Description | Recommended Disposition |
|---------|-------|-------------|-------------------------|
| WR-01 | `docs/themes/cost/cfd-vs-gas-cost.md:26,117` | Headline table reports £14.2bn premium; narrative on L117 cites £14.9bn for the same quantity. | Track as Phase-4 todo in STATE.md — "numeric-claim consistency pass across Cost theme pages". |
| WR-02 | `cfd-dynamics.md:33`, `cfd-vs-gas-cost.md:26`, `methodology/gas-counterfactual.md:67` | Same cumulative premium reported as £14.1bn / £14.2bn / £14.9bn across three pages. | Same Phase-4 todo — consider introducing a `HEADLINE_FIGURES.md` generated from a pin test (Phase-4 "golden numbers" seed). |
| WR-03 | `docs/themes/efficiency/{index,subsidy-per-avoided-co2-tonne}.md` | Claim that "AR3 is already above UK ETS" but the chart omits AR3. | Track as Phase-4 todo — either remove the AR3 claim pending sufficient generation history, or cite an external projection source. |
| WR-04 | `docs/themes/cannibalisation/{capture-ratio,methodology}.md` | Colour labelling for 2022 clawback contradicts between the two files (blue vs red). | Phase-4 todo — reconcile against the rendered PNG. |
| WR-05 | `docs/index.md:73-76` | Homepage "Status" paragraph is stale post-Phase-3 — mentions "three charts" (only one embedded above) and "capacity factor not yet documented" (now documented). | Phase-4 todo — rewrite Status paragraph to reflect the 5-theme structure. |
| WR-06, WR-07, WR-08 | `counterfactual.py`, `plotting/__main__.py`, `ci.yml` | Minor code / CI polish (missing parameter in monthly wrapper; no `__main__` guard in plotting entry point; docs CI job doesn't depend on test job). | Phase-4 todo or individual fix PRs. |

**Why these are NOT gaps for Phase 3:**

- The Phase-3 goal is **structural** ("tidy and fully documented, with every PRODUCTION chart reachable from a five-theme navigation structure"). Every structural artefact exists and is wired correctly.
- The REVIEW findings are **content correctness** issues (numbers disagreeing across pages, stale prose, colour mismatches). They would block a Phase-4 "publishing layer quality" goal but do not block Phase-3's structural goal.
- The user **explicitly approved** the Phase-3 exit checkpoint after running all 5 SC checks locally. The REVIEW was generated after that approval, so the findings are correctly framed as forward-looking polish items.

**Recommended follow-up:** Add two Phase-4+ todos to `STATE.md`:

1. `[ ] Phase 4+: Numeric-claim consistency pass — reconcile £14.1bn / £14.2bn / £14.9bn cumulative-premium figure across Cost theme + gas-counterfactual methodology (WR-01, WR-02) — consider a HEADLINE_FIGURES.md pin test`.
2. `[ ] Phase 4+: Prose hygiene pass on docs/themes/ — resolve AR3-claim / chart-exclusion contradiction (WR-03), colour-labelling contradiction in Cannibalisation (WR-04), stale "Status" paragraph on homepage (WR-05)`.

These can be folded into Phase 4's Publishing Layer planning as they touch the same docs surface area.

---

## Verification Commands (Reproducible)

All commands below were run at verification time and produced the results cited in the tables above:

```bash
# SC-1
test ! -f src/uk_subsidy_tracker/plotting/subsidy/scissors.py
test ! -f src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck_old.py
grep -rn "scissors\|bang_for_buck_old" src/ tests/   # only tests/test_docs_structure.py:40-43

# SC-2
for f in docs/themes/recipients/{lorenz,cfd-payments-by-category}.md docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md docs/themes/cannibalisation/capture-ratio.md docs/themes/reliability/{capacity-factor-seasonal,generation-heatmap,rolling-minimum}.md; do
  test -f "$f" && wc -l "$f"
done
# All 7 present at 127-172 lines

uv run pytest tests/test_docs_structure.py -v   # 7 passed in 0.01s

# SC-3
for d in cost recipients efficiency cannibalisation reliability; do
  test -d "docs/themes/$d" && test -f "docs/themes/$d/index.md" && test -f "docs/themes/$d/methodology.md"
done

# SC-4 (structural proxy)
grep -cE "themes/(cost|recipients|efficiency|cannibalisation|reliability)/.*\.md" mkdocs.yml   # 20 theme-scoped entries
# Plus mkdocs --strict under validation.nav.omitted_files: warn — see SC-5

# SC-5
uv run mkdocs build --strict   # Documentation built in 0.44 seconds; 0 warnings

# Full suite
uv run pytest   # 23 passed, 4 skipped

# Chart regen
ls docs/charts/html/*_twitter.png | wc -l   # 14
ls docs/charts/html/ | grep -c scissors     # 0
```

---

_Verified: 2026-04-22T17:10:58Z_
_Verifier: Claude (gsd-verifier)_
