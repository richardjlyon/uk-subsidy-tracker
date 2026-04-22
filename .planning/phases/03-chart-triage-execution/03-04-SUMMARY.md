---
phase: 03-chart-triage-execution
plan: 04
subsystem: infra
tags: [mkdocs, ci, github-actions, regression-tests, chart-triage, phase-closure]

# Dependency graph
requires:
  - phase: 03-chart-triage-execution
    plan: 03
    provides: "7 PROMOTE chart pages filled with full D-01 content + GOV-01 four-way coverage (Plan 03-03); 5-theme docs tree and 22-entry nav (Plan 03-02); CUT files deleted + mkdocs.yml validation: block (Plan 03-01); `mkdocs build --strict` clean gate since end of Wave 2"
provides:
  - "`docs/charts/html/` regenerated clean — 14 twitter PNGs, zero scissors artefacts (stale pre-03-01 output purged)"
  - "`.github/workflows/ci.yml` gains a second `docs` job running `uv run --frozen python -m uk_subsidy_tracker.plotting` then `uv run --frozen mkdocs build --strict` — permanent CI gate on every push + PR"
  - "`tests/test_docs_structure.py` (60 lines, 7 invariant tests) — permanent regression guard for Phase-3 docs shape: CUT files absent, 5 themes present, 7 PROMOTE pages exist, D-01 sections present in every PROMOTE page, GOV-01 four-way coverage grep-check, mkdocs validation block intact"
  - "STATE.md Phase-3 closure recorded + OQ4 (CF-formula pin test) + OQ5 (abbreviations glossary) seeds carried forward as Phase-4+ todos"
  - "ROADMAP.md Phase 3 SC-1 + Plan 03-01 SC wording tightened to exclude the TRIAGE-01 regression guard from the CUT-file grep — resolves a self-contradiction between Plan 03-01's grep and Plan 03-04's regression test"
affects: [04-publishing-layer]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Chart regeneration as CI job step (not a local-only ritual): `uv run --frozen python -m uk_subsidy_tracker.plotting` runs on the Ubuntu runner BEFORE `mkdocs build --strict` so the runner regenerates PNGs fresh against the current code tree; catches chart-generation regressions at PR time, not at deploy time."
    - "Docs CI job as a parallel sibling to the test job (no `needs:` cross-reference): both jobs run concurrently; a failure in one does not block the other's feedback."
    - "Regression guards that name deleted files: test_docs_structure.py::test_cut_files_deleted asserts `not Path(...).exists()` for scissors.py + bang_for_buck_old.py; this means the test file MUST reference those names by string, which requires any broad 'cut file' grep to exclude the regression test explicitly."

key-files:
  created:
    - "tests/test_docs_structure.py (60 lines, 7 invariant tests — permanent regression guard for TRIAGE-01..04 + GOV-01 + mkdocs validation block)"
    - ".planning/phases/03-chart-triage-execution/03-04-SUMMARY.md (this file)"
  modified:
    - ".github/workflows/ci.yml (added `docs` job — chart regen + mkdocs --strict on push/PR; existing `test` job untouched)"
    - ".planning/STATE.md (Phase-3 closure + OQ4/OQ5 seeds + Performance Metrics 3/12 + Session Continuity advanced to Phase 4)"
    - ".planning/ROADMAP.md (Phase 3 SC-1 wording tightened to exclude the TRIAGE-01 regression guard)"
    - ".planning/phases/03-chart-triage-execution/03-01-PLAN.md (SC criterion + verify + verification block grep commands gained `--exclude-dir=__pycache__ --exclude=test_docs_structure.py` flags)"
  regenerated:
    - "docs/charts/html/ (14 twitter PNGs + 14 HTML + 14 div.html = 42 files; gitignored, not staged)"

key-decisions:
  - "Docs CI job added as a PARALLEL sibling to the test job (no `needs:` cross-reference) — matches the plan interface spec. Rationale: chart-gen + mkdocs build takes longer than pytest; running them concurrently lets the pytest failure signal surface first on fast PRs and doesn't block a docs-only change on a pytest regression (or vice versa)."
  - "Chart regeneration step runs on the Ubuntu runner at PR/push time (not only locally) — the plotting pipeline is offline-safe (reads committed `data/*.csv` files, doesn't fetch over HTTP) and `uv run --frozen` pins the Python dependency graph, so the runner's output is reproducible against the commit. If any plotting module is later made network-dependent, this job MUST be updated (documented in the 03-04 PLAN action block)."
  - "tests/test_docs_structure.py uses filesystem assertions only — no imports from `uk_subsidy_tracker.*` — so test collection remains fast (the existing `tests/__init__.py` package marker from Phase 2 still resolves it) and the test doesn't depend on the package's import graph working. The tests run in ~10ms end-to-end."
  - "SC-1 wording tightening applied AFTER user approved the human-verify checkpoint (Task 5). The user noticed that Plan 03-01's bare `grep -rn scissors src/ tests/` success criterion would flag Plan 03-04's new regression test (which MUST name the CUT files to assert their absence) — i.e. the SC criterion as originally written was self-contradictory the moment test_docs_structure.py landed. Fixed by adding `--exclude-dir=__pycache__ --exclude=test_docs_structure.py` to the grep in both places in 03-01-PLAN.md and explicitly calling out the test as the intended exception in the ROADMAP SC-1 text. Documented as a Rule-1 deviation below."

patterns-established:
  - "Wave 4 = gate-promotion + regression-guard + phase-closeout, NOT new surface area. Plan 03-04's job was to take the properties the prior three plans established (mkdocs --strict passes; docs tree has a particular shape; CUT files stay deleted) and wire them into mechanisms that make them hold forever: CI job + pytest invariants. No new docs content; no new chart code; no schema changes."
  - "Post-checkpoint reconciliation of plan self-contradictions: when a human-verify checkpoint surfaces an inconsistency between prior-plan acceptance criteria and current-plan deliverables (e.g. a grep that flags a regression test naming CUT files), the fix lands in the current plan's closeout — not as a retrospective amendment to the prior plan's SUMMARY. The ROADMAP gets the authoritative new wording; the prior plan's PLAN.md gets a grep-flag update to match; the current plan's SUMMARY documents the reconciliation as a deviation."

requirements-completed: [TRIAGE-01, TRIAGE-02, TRIAGE-03, TRIAGE-04, GOV-01]

# Metrics
duration: 5min
completed: 2026-04-22
---

# Phase 03 Plan 04: Wave 4 Phase-Closure Summary

**Regenerated `docs/charts/html/` clean (14 PNGs, zero scissors), promoted `mkdocs build --strict` to a permanent `.github/workflows/ci.yml` `docs` job, added `tests/test_docs_structure.py` (7 invariant tests) as the Phase-3 regression guard, recorded Phase-3 closure in STATE.md with OQ4/OQ5 seeds; user approved the 5 ROADMAP success criteria. Phase 3 formally closed.**

## Performance

- **Duration:** ~5 min (execution) + checkpoint wait time
- **Tasks:** 5 (4 auto + 1 human-verify checkpoint)
- **Files created:** 2 (tests/test_docs_structure.py, this SUMMARY.md)
- **Files modified:** 4 (.github/workflows/ci.yml, .planning/STATE.md, .planning/ROADMAP.md, .planning/phases/03-chart-triage-execution/03-01-PLAN.md)
- **Files regenerated (gitignored):** docs/charts/html/ (42 files)

## Accomplishments

- **Satisfied TRIAGE-04** (last Phase-3 requirement). Every PRODUCTION chart is reachable from theme nav (structural property set up by Plan 03-02); `mkdocs build --strict` is now a CI-enforced gate on every push + PR, so the navigation stays green in perpetuity.
- **Phase-3 SC-1..SC-5 all green** — user ran the 4 automated checks locally (SC-1, SC-2, SC-3, SC-5) and confirmed satisfaction with the SC-4 visual check from the Wave 2/3 mkdocs-build passes. Approved the human-verify checkpoint with "approved".
- **`docs/charts/html/` regenerated clean** — 14 twitter PNGs present; zero scissors/bang_for_buck_old artefacts remain. This purged the stale pre-Plan-03-01 output per OQ2 resolution.
- **CI `docs` job live** — `.github/workflows/ci.yml` now has two sibling jobs (`test` runs pytest, `docs` regenerates charts then runs `mkdocs build --strict`). YAML validated; both jobs will run on the next push/PR.
- **Regression guard live** — `tests/test_docs_structure.py` adds 7 structural-invariant tests (~10ms runtime) that assert: CUT files absent, 5 themes with index+methodology, 7 PROMOTE pages exist at correct paths, existing Cost pages moved, D-01 6-section template present in every PROMOTE page, GOV-01 four-way coverage grep-visible per page, mkdocs validation block intact. Any future plan that accidentally breaks these invariants fails on CI.
- **STATE.md Phase-3 closure recorded** — Phases-complete 2/12 → 3/12; Plans-complete 9/9 → 13/13 (4/4 for Phase 3); `stopped_at: Phase 3 complete`; Session Continuity advanced to Phase 4. OQ4 (CF-formula pin test) + OQ5 (abbreviations.md glossary) carried forward as Phase-4+ todos.
- **Post-checkpoint SC-1 wording reconciled** — discovered during user's local SC-1 verification that Plan 03-01's bare grep conflicted with Plan 03-04's new regression test. Fixed in both the ROADMAP (authoritative SC wording) and Plan 03-01 (grep flag update) after user approval.

## Task Commits

1. **Task 1: Regenerate docs/charts/html/** — no commit (gitignored path; regeneration is a filesystem side-effect that CI re-runs per build)
2. **Task 2: Add `docs` job to .github/workflows/ci.yml** — `934941a` (ci)
3. **Task 3: Create tests/test_docs_structure.py** — `c52af81` (test)
4. **Task 4: Update STATE.md (Phase-3 closure + OQ4/OQ5 seeds)** — `97ab810` (docs)
5. **Task 5: Human-verify checkpoint** — APPROVED by user (no commit; checkpoint reconciliation followed)
6. **Post-checkpoint: Tighten SC-1 wording in ROADMAP.md + 03-01-PLAN.md** — `77fbcbb` (docs)

_Plan metadata commit follows this SUMMARY._

## Files Created/Modified

### Created (2)

- `tests/test_docs_structure.py` (60 lines) — 7 pytest functions: test_cut_files_deleted, test_all_themes_have_index_and_methodology, test_promote_chart_pages_exist, test_existing_cost_pages_moved, test_six_section_template_present_in_promote_pages, test_gov01_four_way_coverage, test_mkdocs_validation_block_present. No imports from `uk_subsidy_tracker`; filesystem assertions only.
- `.planning/phases/03-chart-triage-execution/03-04-SUMMARY.md` — this file.

### Modified (4)

- `.github/workflows/ci.yml` — added `docs` job (sibling to `test`). Steps: checkout, install uv (v8.1.0), `uv sync --frozen`, regenerate charts, `mkdocs build --strict`. Existing `test` job untouched; trigger block untouched.
- `.planning/STATE.md` — 3 edits per the plan: (1) Performance Metrics + progress bar bumped to 3/12 phases / 13/13 plans with Phase-3 requirements appended; (2) Current Position + Session Continuity advanced to Phase 4 with next-command string; (3) Todos marked + OQ4/OQ5 seeds appended; frontmatter bumped to `completed_phases: 3`, `stopped_at: Phase 3 complete`.
- `.planning/ROADMAP.md` — Phase 3 Success Criteria #1 wording tightened (post-checkpoint, user-approved) to clarify that the sole in-tree references to `scissors.py` / `bang_for_buck_old.py` live inside `tests/test_docs_structure.py`, the permanent TRIAGE-01 regression guard.
- `.planning/phases/03-chart-triage-execution/03-01-PLAN.md` — 3 localised edits to match the ROADMAP rewording: (a) success_criteria truths line appended with the regression-test exclusion clause; (b) Task 1 verify block grep gained `--exclude-dir=__pycache__ --exclude=test_docs_structure.py` flags; (c) end-of-plan verification block got the same grep flags plus a one-line explanatory note.

### Regenerated (gitignored, not staged)

- `docs/charts/html/` — 14 `_twitter.png` files + 14 `.html` interactive charts + 14 `.div.html` embeds (42 files total). Purged stale `subsidy_scissors*` artefacts from the pre-Plan-03-01 working tree.

## Decisions Made

- **Docs CI job is parallel (no `needs:` on the test job)** — per plan interface spec. Rationale: chart-gen + mkdocs build takes longer than pytest; running them concurrently surfaces pytest failures first on fast PRs and doesn't block a docs-only change on a pytest regression (or vice versa).
- **Chart regeneration runs on the Ubuntu runner, not cached** — the plotting pipeline is offline-safe (reads committed `data/*.csv`, no HTTP), and `uv run --frozen` pins Python deps, so the runner's regen output is reproducible against the commit. If any plotting module is later made network-dependent, this job must be updated (flagged in the PLAN action block).
- **test_docs_structure.py uses filesystem assertions only** — no imports from `uk_subsidy_tracker.*`. Tests run in ~10ms total; collection doesn't depend on the package's import graph working. The 7 tests pass in 0.01s per pytest timing.
- **SC-1 wording fix landed in the current plan's closeout** — the inconsistency between Plan 03-01's bare grep and Plan 03-04's regression test was discovered during user's SC-1 check (human-verify checkpoint). Per standard GSD practice, the fix lands in the current plan's commits (this plan is where the new test was added that created the grep conflict); the ROADMAP gets the authoritative new SC-1 wording; Plan 03-01's PLAN.md gets a grep-flag update to stay internally consistent; Plan 03-01's SUMMARY stays frozen as a historical record of what was shipped at that time.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan 03-01 SC-1 self-contradicts Plan 03-04 regression test**
- **Found during:** Task 5 (human-verify checkpoint — user ran SC-1 grep locally)
- **Issue:** Plan 03-01's success criterion #1 (and the corresponding verify + end-of-plan verification blocks) uses a bare `grep -rn "scissors\|bang_for_buck_old" src/ tests/` to assert that no in-tree references to the CUT files remain. Plan 03-04 Task 3 adds `tests/test_docs_structure.py::test_cut_files_deleted`, which MUST reference the CUT filenames by string literal to assert their filesystem absence. As written, Plan 03-01's SC criterion would flag Plan 03-04's regression guard as a failure — a self-contradiction that only surfaces once both plans have landed.
- **Fix:** (a) Tightened the ROADMAP Phase 3 SC-1 wording to explicitly carve out `tests/test_docs_structure.py` as the permanent TRIAGE-01 regression guard. (b) Added `--exclude-dir=__pycache__ --exclude=test_docs_structure.py` to the grep in Plan 03-01's Task 1 verify block + end-of-plan verification block. (c) Appended the exclusion clause to Plan 03-01's `success_criteria.truths[...]` line. The `__pycache__` exclusion is a belt-and-braces addition — it prevents stale `.pyc` bytecode files from tripping the grep if they happen to contain the string (a separate, stray `__pycache__/scissors.cpython-313.pyc` file was removed from the working tree during user diagnosis; not committed because the path is gitignored).
- **Files modified:** `.planning/ROADMAP.md` (1 line), `.planning/phases/03-chart-triage-execution/03-01-PLAN.md` (3 lines)
- **Verification:** All 4 automated SC checks pass clean post-fix — SC-1 `SC-1 OK`; SC-2 `7 passed in 0.01s`; SC-3 `SC-3 OK`; SC-5 `mkdocs build --strict` exit 0, 0 warnings, 0.45s build
- **Commit:** `77fbcbb` (post-checkpoint, user-approved in-checkpoint)

---

**Total deviations:** 1 auto-fixed (Rule 1 bug — plan self-contradiction surfaced at checkpoint)
**Impact on plan:** The auto-fix was a hygiene reconciliation of a latent inconsistency between two plans in the same phase; no scope creep; no code paths changed; the SC-1 intent (no production code references scissors/bang_for_buck_old) is preserved, and the regression-guard exception is now explicit. User explicitly approved the reconciliation during the human-verify checkpoint.

## Authentication Gates

None — all work was local filesystem + YAML edits. No external services, no secrets, no logins.

## Issues Encountered

- **Stray `__pycache__/scissors.cpython-313.pyc` surfaced during user's SC-1 grep** — a leftover bytecode file from a pre-Plan-03-01 checkout still contained the word "scissors" as a symbol reference. Removed from the working tree during diagnosis (no commit — the path is inside a `__pycache__/` directory which is gitignored project-wide). The SC-1 grep exclusion flag `--exclude-dir=__pycache__` added in the post-checkpoint fix means this class of stale-bytecode ghost cannot trip the SC-1 gate again.

## User Setup Required

None — all changes are repository-internal (CI workflow file, test file, state+plan docs). No environment variables, no external dashboards, no secrets.

## Known Stubs

None. The 7 PROMOTE chart page stubs from Plan 03-02 were filled with full D-01 content in Plan 03-03; this plan added no new stubs.

## Out-of-Scope Uncommitted Items (deferred)

The following working-tree changes existed before this plan began executing and are NOT within Plan 03-04's scope. They are intentionally left uncommitted for a future plan or workflow to address:

- `.gitignore` modification adding `.private/` exclusion (off-record notes dir; unrelated to Phase 3)
- `.planning/config.json` modification flipping `_auto_chain_active: false` (GSD tooling auto-managed)
- `test` (empty file at repo root, 0 bytes — stray; safe to delete in any subsequent hygiene pass)

The plan-metadata closeout commit below picks up only `03-04-SUMMARY.md` + `03-04-PLAN.md` + the previously uncommitted `03-02-PLAN.md` + `03-03-PLAN.md` (hygiene fix — these 3 PLAN files were never committed by the planner) + `ROADMAP.md` + `REQUIREMENTS.md` so the Phase-3 planning artefacts are versioned. It does NOT touch `.gitignore`, `.planning/config.json`, or the stray `test` file.

## Next Phase Readiness

- **Phase 3 formally closed.** All 5 ROADMAP success criteria met; user approved the human-verify checkpoint; all 4 automated SC checks green post-reconciliation.
- **CI gate live.** The next push/PR will exercise both the `test` job (pytest — 23 passed + 4 skipped expected) and the `docs` job (chart regen + mkdocs build --strict — 0 warnings expected).
- **Regression guards in place.** `tests/test_docs_structure.py` will fail-fast on any future plan that accidentally breaks Phase-3 invariants (theme tree shape, CUT-file absence, D-01 template presence, GOV-01 coverage, mkdocs validation block).
- **Phase 4 seeds recorded.** OQ4 (CF-formula pin test for the capacity-factor-seasonal chart's methodology) and OQ5 (abbreviations.md glossary to populate the Material `content.tooltips` feature enabled in Plan 03-01) are carried forward as Phase-4+ todos in STATE.md.
- **No blockers.**
- **Next command:** `/gsd-plan-phase 4` — begin planning Phase 4 (Publishing Layer: manifest.json, CSV mirror, snapshot, Parquet migration for CfD scheme). The orchestrator will run the Phase-3 verifier before kicking off Phase 4 planning.

## Self-Check: PASSED

**Files verified:**
- FOUND: `tests/test_docs_structure.py` — 7 tests pass in 0.01s
- FOUND: `.github/workflows/ci.yml` — `docs:` job present with `mkdocs build --strict` step (grep-verified)
- FOUND: `.planning/STATE.md` — Phase 3 closure strings present (`Phase 3 closed`, `gsd-plan-phase 4`, `stopped_at: Phase 3 complete`, `Phases complete:** 3/12`)
- FOUND: `.planning/ROADMAP.md` — Phase 3 SC-1 tightened wording present (`tests/test_docs_structure.py`, which is the TRIAGE-01 regression guard)
- FOUND: `.planning/phases/03-chart-triage-execution/03-01-PLAN.md` — grep exclusion flags present in 2 places; success-criteria truths line extended
- FOUND: `docs/charts/html/subsidy_lorenz_twitter.png` (sample PNG from Task 1 regen; path is gitignored but exists on disk)

**Commits verified:**
- FOUND: `934941a` — ci(03-04): add docs job running mkdocs --strict on push/PR (Task 2)
- FOUND: `c52af81` — test(03-04): add tests/test_docs_structure.py regression guard (Task 3)
- FOUND: `97ab810` — docs(03-04): record Phase 3 closure + OQ4/OQ5 seeds in STATE.md (Task 4)
- FOUND: `77fbcbb` — docs(03-04): tighten SC-1 wording to exclude TRIAGE-01 regression test (post-checkpoint reconciliation)

**Verification commands run (final, post-reconciliation):**
- SC-1: `test ! -f src/uk_subsidy_tracker/plotting/subsidy/scissors.py && test ! -f src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck_old.py && ! grep -rn --exclude-dir=__pycache__ --exclude=test_docs_structure.py "scissors\|bang_for_buck_old" src/ tests/` → exit 0 (`SC-1 OK`)
- SC-2: `uv run pytest tests/test_docs_structure.py -v` → 7 passed in 0.01s
- SC-3: 5-theme tree test (loop over cost/recipients/efficiency/cannibalisation/reliability) → exit 0 (`SC-3 OK`)
- SC-4: mkdocs serve visual check — NOT re-run by the executor; user declared satisfaction from Wave-2/3 strict-build passes + the Wave-4 strict-build reconfirmation below
- SC-5: `uv run mkdocs build --strict` → exit 0, 0.45s, 0 warnings (`Exit: 0`)
- Git status post-commits: `03-04-SUMMARY.md` present; `03-04-PLAN.md`, `03-02-PLAN.md`, `03-03-PLAN.md` still untracked (will be swept into the plan-metadata closeout commit below as a hygiene fix — not introduced by this plan, but the closeout is the right place to bring them into git)

---
*Phase: 03-chart-triage-execution*
*Completed: 2026-04-22*
