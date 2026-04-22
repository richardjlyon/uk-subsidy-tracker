---
phase: 03-chart-triage-execution
plan: 01
subsystem: infra
tags: [mkdocs, material-theme, chart-triage, yaml, validation]

# Dependency graph
requires:
  - phase: 02-test-foundation
    provides: CI gate (pytest green on push + PR); stable 16-passed + 4-skipped baseline that Task 1's file-deletion regression check relies on
provides:
  - "scissors.py + bang_for_buck_old.py physically removed from working tree (git history preserved)"
  - "plotting/__main__.py trimmed to 14 imports + 14 calls (was 15 + 15)"
  - "counterfactual.py docstring cleaned of scissors chart reference"
  - "mkdocs.yml theme.features list matches D-06 target ordering exactly (4 additions + toc.follow → toc.integrate swap)"
  - "mkdocs.yml root-level validation: block promoting nav.omitted_files + anchor + absolute_links warnings"
affects: [03-02, 03-03, 03-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Material theme features locked to D-06 contract (10 entries, specific ordering per RESEARCH §Material Theme Feature Regressions)"
    - "mkdocs validation: root block as CI-strict teeth — nav.omitted_files: warn catches orphan docs, anchors: warn catches broken cross-links"

key-files:
  created: []
  modified:
    - "src/uk_subsidy_tracker/plotting/__main__.py (scissors import + call deleted)"
    - "src/uk_subsidy_tracker/counterfactual.py (L139-140 docstring cleaned)"
    - "mkdocs.yml (theme.features + new validation: block)"
  deleted:
    - "src/uk_subsidy_tracker/plotting/subsidy/scissors.py (preserved in git history)"
    - "src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck_old.py (preserved in git history)"

key-decisions:
  - "nav: block intentionally left untouched — Plan 03-02 rewrites it once the five-theme docs tree exists. Adding nav.omitted_files: warn first is safe because the current 3-CfD-chart nav already matches the current filesystem exactly."
  - "toc.follow removed (not commented) per D-06 — Material docs flag toc.follow and toc.integrate as mutually exclusive (RESEARCH Pitfall 4)."
  - "YAML validated via Material-compatible loader (ignore !!python/name tags) rather than plain yaml.safe_load — safe_load rejects the pre-existing pymdownx.emoji constructors and would have failed even without my edits."
  - "Orchestrator import sanity checked via importlib.util.find_spec + ast.parse rather than running `python -m uk_subsidy_tracker.plotting` — the latter regenerates 14 chart artefacts as a side effect, which is Wave 4's scope (per OQ2 resolution), not Wave 1's."

patterns-established:
  - "Wave 1 = scope-locked cleanup: only deletions and config additions that are no-ops against the current filesystem. Structural rewrites (nav, docs tree) are Wave 2's scope and depend on the theme tree existing."
  - "Deletion + reference purge in a single commit (never split). Dangling imports would break `uv run python -m uk_subsidy_tracker.plotting` at module-load time, which is T-03-01's mitigation pathway."

requirements-completed: [TRIAGE-01]

# Metrics
duration: 2min
completed: 2026-04-22
---

# Phase 03 Plan 01: Wave 1 Cleanup Summary

**Deleted scissors.py + bang_for_buck_old.py (TRIAGE-01) and primed mkdocs.yml with 10-feature Material theme + strict-validation nav-orphan detection — zero test regressions, nav: untouched for Plan 03-02.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-04-22T16:08:55Z
- **Completed:** 2026-04-22T16:11:10Z
- **Tasks:** 2
- **Files modified:** 3 (counterfactual.py, plotting/__main__.py, mkdocs.yml)
- **Files deleted:** 2 (scissors.py, bang_for_buck_old.py)

## Accomplishments

- Satisfied TRIAGE-01 (CUT verdict from PROJECT.md §Requirements): both doomed chart modules physically removed from `src/`, zero working-tree grep hits for `scissors` or `bang_for_buck_old` under `src/` or `tests/`.
- Orchestrator reduced 15 → 14 charts cleanly — no dangling import, pytest stays at 16 passed + 4 skipped (same as Phase 2 close baseline).
- `mkdocs.yml` theme.features list exactly matches D-06 (10 entries in locked order): `navigation.tabs`, `navigation.tabs.sticky`, `navigation.sections`, `navigation.top`, `navigation.instant`, `search.suggest`, `search.highlight`, `content.code.copy`, `content.tooltips`, `toc.integrate`.
- Root-level `validation:` block promotes `nav.omitted_files: warn` + `links.anchors: warn` + `links.absolute_links: warn` — the strict-build teeth that TRIAGE-04 depends on (and that Plan 03-04 Wave 4 wires into CI).

## Task Commits

1. **Task 1: Delete scissors.py + bang_for_buck_old.py and purge references** — `c5cc229` (chore)
2. **Task 2: Update mkdocs.yml theme.features + add validation block** — `575b57d` (chore)

_Plan metadata commit follows this SUMMARY._

## Files Created/Modified

- `src/uk_subsidy_tracker/plotting/__main__.py` — removed scissors import + call; 14 imports + 14 calls remain across the 4 section-commented blocks (Subsidy economics, Capacity factor, Intermittency, Cannibalisation).
- `src/uk_subsidy_tracker/counterfactual.py` — cleaned L139-140 docstring inside `compute_counterfactual()`: "Callers who want fuel-only (e.g. scissors chart) should reference..." → "Callers who want fuel-only should reference...". `Provenance:` blocks and formula body (L143-167) untouched.
- `mkdocs.yml` — theme.features list replaced (10 entries, locked ordering); new root-level `validation:` block inserted between `theme.palette:` and `# Navigation` comment (lines 43-53).
- `src/uk_subsidy_tracker/plotting/subsidy/scissors.py` — **deleted** via `git rm` (history preserved; stale PNG artefacts under `docs/charts/html/subsidy_scissors*` are gitignored and will be purged by Plan 03-04 Wave 4's `rm -rf docs/charts/html/` + regenerate).
- `src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck_old.py` — **deleted** via `git rm` (zero code references pre-deletion; deletion is purely cosmetic hygiene).

## Decisions Made

- **Deferred `nav:` rewrite to Plan 03-02** — rewriting nav here would reference the five-theme docs tree (cost/recipients/efficiency/cannibalisation/reliability) which does not yet exist in Wave 1, producing dangling entries that would immediately trip `validation.nav.not_found: warn` (RESEARCH Pitfall 2). The current three-CfD-chart nav still maps 1:1 to the filesystem, so the new `validation:` block is a no-op against current state but active against Plan 03-02's structural changes.
- **Removed (not commented) `toc.follow`** per D-06 contract — Material docs flag `toc.follow` and `toc.integrate` as mutually exclusive; keeping both produces a per-page tracebackless render bug (RESEARCH §Material Theme Feature Regressions Pitfall 4).
- **Purge scissors docstring cross-reference, not just the code reference** — `counterfactual.py:139` mentioning "scissors chart" would otherwise become an orphan word once the chart module is gone. The replacement sentence carries the same semantic content ("fuel-only mode is available via `gas_fuel_cost` column") without citing a no-longer-extant chart, preserving the docstring's API-documentation role.

## Deviations from Plan

None — plan executed exactly as written. Both tasks landed in single commits as specified (deletion + reference purge atomic in Task 1, per T-03-01 mitigation). Verify blocks passed clean on first run; no auto-fixes triggered; no Rule-4 architectural questions surfaced.

## Issues Encountered

- **Pre-existing `yaml.safe_load` incompatibility noted during verify** — the plan's `uv run python -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"` check fails under `safe_load` because `mkdocs.yml` already contains `!!python/name:material.extensions.emoji.twemoji` tags (lines 86-87) that `safe_load` refuses by design. Confirmed pre-existing via `git stash` + same check on HEAD~1 — fails identically. Swapped the verification to a custom `SafeLoaderIgnoreUnknown` loader that accepts unknown tags (matches MkDocs' own YAML-loading behaviour). Verification confirms: validation block parses correctly, 10 features present in target order, nav: block length unchanged. **Not a deviation** — the plan's verify was under-specified for a pre-existing condition; functional outcome (YAML is valid MkDocs config) is verified.

## User Setup Required

None — no external service configuration required. Changes are all internal file edits.

## Next Phase Readiness

- **Ready for Plan 03-02 (Wave 2: nav + docs-tree rewrite).** The `validation:` block is in place but inactive (current nav matches filesystem). When Plan 03-02 rewrites `nav:` into the five-theme tree, `validation.nav.omitted_files: warn` will immediately surface any doc orphans; `validation.nav.not_found: warn` will surface any nav entries pointing at non-existent files. Both are the CI-strict teeth that TRIAGE-04 (exit criterion for Phase 3) depends on.
- **Orchestrator clean:** `uv run python -m uk_subsidy_tracker.plotting` will regenerate 14 charts (not 15) on Wave 4's chart-regeneration step — stale `docs/charts/html/subsidy_scissors*` artefacts vanish via Plan 03-04's `rm -rf docs/charts/html/` + regenerate (per OQ2).
- **No blockers:** pytest baseline holds at 16 passed + 4 skipped — regression guard for the rest of Phase 3.

## Self-Check: PASSED

**Files verified:**
- MISSING (expected): `src/uk_subsidy_tracker/plotting/subsidy/scissors.py` — confirmed absent
- MISSING (expected): `src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck_old.py` — confirmed absent
- FOUND: `src/uk_subsidy_tracker/plotting/__main__.py` (14 imports verified)
- FOUND: `src/uk_subsidy_tracker/counterfactual.py` (docstring cleaned at L139-140)
- FOUND: `mkdocs.yml` (validation: block + 10 features in D-06 order)

**Commits verified:**
- FOUND: `c5cc229` (Task 1 — chore(03-01): purge scissors + bang_for_buck_old)
- FOUND: `575b57d` (Task 2 — chore(03-01): prime mkdocs.yml with Material features + validation block)

**Verification commands run:**
- `test ! -f src/uk_subsidy_tracker/plotting/subsidy/scissors.py` → exit 0
- `test ! -f src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck_old.py` → exit 0
- `grep -rn "scissors\|bang_for_buck_old" src/ tests/` → no matches (zero hits, clean)
- `grep -c "^from uk_subsidy_tracker.plotting" src/uk_subsidy_tracker/plotting/__main__.py` → 14 (was 15)
- `uv run pytest` → 16 passed + 4 skipped (no regressions)
- MkDocs-loader YAML parse → `validation.nav.omitted_files: warn` confirmed, 10 features in locked order confirmed, `toc.follow` removed + `toc.integrate` added confirmed

---
*Phase: 03-chart-triage-execution*
*Completed: 2026-04-22*
