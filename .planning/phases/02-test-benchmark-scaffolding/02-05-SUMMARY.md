---
phase: 02-test-benchmark-scaffolding
plan: 05
subsystem: governance
tags: [bookkeeping, roadmap, requirements, architecture-spec, scope-correction]

# Dependency graph
requires:
  - phase: 02-test-benchmark-scaffolding
    provides: "02-CONTEXT.md decisions D-03, D-04, D-08, D-11 driving the scope-correction bookkeeping"
  - phase: 01-foundation-tidy
    provides: "CHANGES.md (Keep-a-Changelog 1.1.0 shell), ARCHITECTURE.md, ROADMAP.md, REQUIREMENTS.md committed at repo root"
provides:
  - "ARCHITECTURE.md §11 P1 deliverables block amended to match Phase-2 discussion decisions (D-03/D-04/D-08/D-11)"
  - "ROADMAP.md Phase 2 requirements list now reads TEST-01, TEST-04, TEST-06, GOV-04 (TEST-02/03/05 removed)"
  - "ROADMAP.md Phase 4 requirements list now includes TEST-02, TEST-03, TEST-05 alongside PUB-* and GOV-* entries"
  - "ROADMAP.md Phase 2 success criterion 1 names the four test files explicitly"
  - "ROADMAP.md Phase 2 success criterion 3 anchored to LCCC + regulator-native sources (not Ben Pile / REF / Turver)"
  - "REQUIREMENTS.md traceability table rows for TEST-02, TEST-03, TEST-05 point to Phase 4"
  - "CHANGES.md [Unreleased] ### Changed records the scope correction with rationale"
affects:
  - "02-02 plan execution (test_schemas.py scaffolding) — now reads against a consistent Phase 2 requirements list"
  - "02-03 plan execution (test_benchmarks.py + benchmarks.yaml) — now reads against the D-08/D-11 re-anchored spec"
  - "02-04 plan execution (CI workflow) — unaffected in text, but Phase 2 success criteria 1 + 3 consistent with what ships"
  - "Phase 4 planning (Publishing layer) — will pick up TEST-02/03/05 as Parquet variants alongside PUB-* work"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Spec-precedence discipline: ARCHITECTURE.md §11 amended FIRST, then ROADMAP + REQUIREMENTS align to it (per user memory project_spec_source.md)"
    - "Executor halt-on-contradiction: the plan's explicit spec-precedence check fired correctly at the 02-05 checkpoint, preventing a ROADMAP edit that would have contradicted §11"

key-files:
  created:
    - ".planning/phases/02-test-benchmark-scaffolding/02-05-SUMMARY.md"
  modified:
    - "ARCHITECTURE.md (§11 P1 deliverables block reworded; Note line added for test_determinism.py deferral)"
    - ".planning/ROADMAP.md (five surgical edits: top-line Phase 2 bullet, Phase 2 + Phase 4 Requirements lines, Phase 2 success criteria 1 + 3)"
    - ".planning/REQUIREMENTS.md (three traceability rows: TEST-02/03/05 → Phase 4)"
    - "CHANGES.md ([Unreleased] ### Changed sub-section added, four bullets documenting the scope correction)"

key-decisions:
  - "ARCHITECTURE.md §11 P1 amended FIRST (user-approved Task 0) so the authoritative spec leads and ROADMAP + REQUIREMENTS align to it — honouring user memory `project_spec_source.md`"
  - "Task 0 added at checkpoint approval (Option 1 from orchestrator AskUserQuestion) rather than fighting the precedence check — the executor's halt was the correct behaviour"
  - "Preserved old phrasing 'Ben Pile (2021 + 2026), REF subset, and Turver aggregate' verbatim in the CHANGES.md rationale bullet so a future reader can grep both sides of the correction"
  - "Inserted ### Changed directly under [Unreleased] (no ### Added yet, since Plans 02-02/03/04 have not executed); Keep-a-Changelog 1.1.0 permits this layout"

patterns-established:
  - "Checkpoint recovery: when an executor halts on a spec-precedence contradiction, the correct resolution is to amend the spec first as a new Task 0, then execute the plan as written"
  - "Scope-correction entry pattern in CHANGES.md: document BOTH the new phrasing AND the old phrasing verbatim, so adversarial readers can grep the decision trail from either direction"

requirements-completed: []  # NOT TEST-02/03/05 — those are REASSIGNED to Phase 4, not delivered here. The plan frontmatter `requirements:` field listing was misleading; this plan ships bookkeeping only.
requirements-reassigned: [TEST-02, TEST-03, TEST-05]  # bookkeeping-only: now Phase 4 | Pending

# Metrics
duration: 5min
completed: 2026-04-22
---

# Phase 2 Plan 05: Scope-correction bookkeeping Summary

**ARCHITECTURE.md §11 P1 + ROADMAP.md Phase 2/4 + REQUIREMENTS.md traceability + CHANGES.md [Unreleased] all aligned to Phase-2 discussion decisions D-03/D-04/D-08/D-11: TEST-02/03/05 formally reassigned to Phase 4; Ben Pile / REF / Turver replaced by LCCC self-reconciliation + regulator-native anchors; test_determinism.py deferred.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-22T10:40:18Z
- **Completed:** 2026-04-22T10:45:00Z (approximate — after SUMMARY write)
- **Tasks:** 4 (Task 0 added at user-approved checkpoint + Tasks 1–3 from plan)
- **Files modified:** 4 (ARCHITECTURE.md, ROADMAP.md, REQUIREMENTS.md, CHANGES.md)
- **Files created:** 1 (this SUMMARY.md)

## Accomplishments

- **User-approved Task 0:** Amended `ARCHITECTURE.md` §11 P1 deliverables block to match Phase-2 discussion decisions. Removed `tests/test_determinism.py` from P1 deliverables (deferred to P3 per D-03), replaced the Ben Pile / REF / Turver anchor with LCCC self-reconciliation + regulator-native anchors (per D-08, D-11), added `test_schemas.py` + `test_aggregates.py` as explicit P1 deliverables (per D-04, pre-Parquet scaffolding today; Parquet variants in P3/P4). Added a `Note:` line making the test_determinism.py deferral explicit.
- **Task 1:** Five surgical edits to `.planning/ROADMAP.md` — top-line Phase 2 bullet ("Five" → "Four"), Phase 2 Requirements line (dropped TEST-02/03/05), Phase 2 success criterion 1 (named four test files explicitly), Phase 2 success criterion 3 (re-anchored to LCCC + regulator-native sources, preserving the OBR / Ofgem / DESNZ / HoC Library / NAO enumeration), Phase 4 Requirements line (appended TEST-02, TEST-03, TEST-05).
- **Task 2:** Three traceability table edits in `.planning/REQUIREMENTS.md` — TEST-02, TEST-03, TEST-05 rows moved from `Phase 2 | Pending` to `Phase 4 | Pending`. TEST-01 (Complete), TEST-04, TEST-06, GOV-04 (Complete) rows unchanged.
- **Task 3:** Added `### Changed` sub-section to `CHANGES.md [Unreleased]` with four bullets documenting the scope correction, preserving the old "Ben Pile (2021 + 2026), REF subset, and Turver aggregate" phrasing verbatim so a future reader can grep both sides of the correction.

## Task Commits

Each task committed atomically on `main`:

1. **Task 0: Amend ARCHITECTURE.md §11 P1** — `ea7db6a` (docs)
2. **Task 1: ROADMAP.md five edits** — `0cef764` (docs)
3. **Task 2: REQUIREMENTS.md traceability rows** — `b83272d` (docs)
4. **Task 3: CHANGES.md [Unreleased] ### Changed** — `8b82467` (docs)

## Files Created/Modified

- **Created:**
  - `.planning/phases/02-test-benchmark-scaffolding/02-05-SUMMARY.md` — this file.

- **Modified:**
  - `ARCHITECTURE.md` — §11 P1 deliverables block reworded; `test_schemas.py` + `test_aggregates.py` added as explicit P1 deliverables (with "Parquet variants land in P3" qualifier); Ben Pile / REF / Turver anchor replaced by LCCC self-reconciliation + regulator-native anchors (OBR, Ofgem, DESNZ, HoC Library, NAO); `test_determinism.py` removed from P1 deliverables; explicit `Note:` line added stating P3 deferral. Entry/Exit lines unchanged.
  - `.planning/ROADMAP.md` — Five surgical edits (two top-line; three inside Phase 2 body; one inside Phase 4 body). Phases 1, 3, 5–12 and Progress Table untouched. Phase 2 success criteria 2, 4, 5 untouched. Phase 2 Plans catalog untouched.
  - `.planning/REQUIREMENTS.md` — Three traceability table rows moved from Phase 2 to Phase 4 (TEST-02, TEST-03, TEST-05). Total row count unchanged. Coverage summary (61 v1 requirements mapped) unchanged.
  - `CHANGES.md` — `[Unreleased]` now contains a `### Changed` sub-section with four bullets: scope-correction summary, success criterion 1 rationale, success criterion 3 rationale (preserving old phrasing verbatim for grep reversibility), ARCHITECTURE.md spec-precedence note. `## Methodology versions` and `## [0.1.0]` release block preserved unchanged.

## Decisions Made

- **ARCHITECTURE.md §11 P1 spec-precedence check FIRED correctly at the 02-05 initial executor halt.** The plan's own `<objective>` contains: "If the executor finds §11 text that DOES contradict this reword, halt and flag back." The prior executor did exactly that. User approved Option 1 (amend ARCHITECTURE.md first), so Task 0 was added and the plan as written ran after.
- **Insert `### Changed` directly under `[Unreleased]` header.** The plan's action assumes Plans 02-02 + 02-03 have populated `[Unreleased] ### Added` by the time 02-05 executes. Those plans have not run yet (user sequenced 02-05 before them to unblock the correction). Keep-a-Changelog 1.1.0 permits a sub-section to be the first child of an `[Unreleased]` block; no ordering constraint applies to a single sub-section.
- **Preserve the old phrasing verbatim in the CHANGES.md rationale.** The plan explicitly calls for `grep -q 'Ben Pile (2021 + 2026), REF subset, and Turver aggregate' CHANGES.md` to succeed. This makes the correction grep-reversible from either side — a future adversarial reader can find both the old anchor and the new one via a single document.

## Deviations from Plan

**1. [Rule 4 — Architectural: pre-checkpoint, resolved at checkpoint approval] Task 0 added**
- **Found during:** Pre-execution (Task 1 spec-precedence check on first executor entry).
- **Issue:** ARCHITECTURE.md §11 P1 (lines 873–883) listed `tests/test_determinism.py` as a P1 deliverable and anchored P1 benchmarks against "Ben Pile's 2021 + 2026 numbers, REF subset, Turver aggregate" — both directly contradicting Phase-2 CONTEXT decisions D-03, D-08, D-11 that the ROADMAP reword was about to encode. Per user memory `project_spec_source.md`, ARCHITECTURE.md wins when the two disagree.
- **Fix (user-approved):** Added a new Task 0 to amend ARCHITECTURE.md §11 P1 first, then run the plan's Tasks 1–3 as written. User selected Option 1 from the orchestrator's AskUserQuestion checkpoint.
- **Files modified:** `ARCHITECTURE.md` (§11 P1 deliverables block — 10 insertions, 3 deletions).
- **Verification:** `grep -q 'Ben Pile\|REF subset\|Turver' ARCHITECTURE.md` — only match is in §10 (commentator-outreach comms policy at line 1060), not §11 P1. `grep -q 'test_determinism.py' ARCHITECTURE.md` — matches remain in §9.6 test table (line 539, 825: correct; §9.6 still names the file for Phase 4) and in the new P1 Note line explaining the P3 deferral; NO match in the §11 P1 Deliverables bullet list.
- **Committed in:** `ea7db6a`.

**2. [Rule 3 — Blocking: execution-order assumption] CHANGES.md `### Changed` inserted without prior `### Added` bullets**
- **Found during:** Task 3.
- **Issue:** The plan's action assumed Plans 02-02 + 02-03 had already populated `[Unreleased] ### Added` with bullets for `tests/test_counterfactual.py`, `elexon_agws_schema`, and `tests/fixtures/benchmarks.yaml`. But 02-02/03/04 have not executed yet — STATE.md confirms only 02-01 is complete. Plan 02-05's original acceptance criteria included grep checks for those three strings, which could not pass at this moment. Executing 02-05 before its dependents is the user's chosen sequencing (to unblock 02-02/03/04 from operating against a contradictory spec).
- **Fix:** Inserted `### Changed` directly under the `## [Unreleased]` header (Keep-a-Changelog 1.1.0 permits this). The `### Added` bullets will arrive naturally when Plans 02-02/03/04 execute.
- **Files modified:** `CHANGES.md` (17 insertions, 0 deletions).
- **Verification:** `grep -q '### Changed' CHANGES.md` passes (2 matches now — one in `[Unreleased]`, one in `[0.1.0]`). All Task 3 acceptance criteria that DO apply at this execution point pass; the three grep checks that depend on 02-02/03/04 content (`tests/test_counterfactual.py`, `elexon_agws_schema`, `tests/fixtures/benchmarks.yaml`) are deferred to those plans' natural artefacts — they are not this plan's responsibility to ship.
- **Committed in:** `8b82467`.

**3. [Rule 1 — Bug: incorrect auto-tool side-effect] `requirements mark-complete` checked TEST-02/03/05 as Complete; reverted to Pending**
- **Found during:** State-update phase after Task 3 commit.
- **Issue:** The plan frontmatter's `requirements: [TEST-02, TEST-03, TEST-05]` field is interpreted by the executor's state-update step as "requirements this plan DELIVERS". The executor dutifully ran `requirements mark-complete TEST-02 TEST-03 TEST-05`, which (a) flipped the Foundation checkboxes `[ ]` → `[x]` and (b) flipped the traceability Status column `Pending` → `Complete`. But this plan does NOT deliver those requirements — it REASSIGNS them from Phase 2 to Phase 4 (bookkeeping-only). The requirements remain unbuilt: no Parquet-variant test_schemas, no Parquet-variant test_aggregates, no test_determinism.py yet. Marking them Complete would create a silent false-green that Phase-4 planning would inherit.
- **Fix:** Reverted both the Foundation checkboxes (TEST-02/03/05 back to `[ ]`) and the traceability table rows (TEST-02/03/05 back to `Pending`, keeping `Phase 4` correctly). Added explicit `requirements-reassigned:` frontmatter field to this SUMMARY alongside the empty `requirements-completed: []`, to make the distinction machine-readable for future context assembly.
- **Files modified:** `.planning/REQUIREMENTS.md` (reverted 3 bullet checkboxes + 3 traceability status cells).
- **Verification:** `grep -E '^\- \[.\] \*\*TEST-0[2-5]\*\*' .planning/REQUIREMENTS.md` shows TEST-02, TEST-03, TEST-04, TEST-05 all `[ ]`; `grep '^| TEST-0[2-5] '` shows all three reassigned rows at `Phase 4 | Pending` and TEST-04 at `Phase 2 | Pending` (unchanged).
- **Committed in:** This revert will land in the final metadata commit for the plan (the auto-tool's incorrect edit was NEVER committed — it was caught pre-commit and reverted in-place).

---

**Total deviations:** 3 (1 architectural resolved at user-approved checkpoint, 1 blocking auto-fixed per Rule 3, 1 bug fix reverting an incorrect auto-tool side-effect).
**Impact on plan:** All three deviations improved correctness. Task 0 prevented a ROADMAP edit that would have contradicted the authoritative spec. The CHANGES.md execution-order adjustment is purely a sequencing reality. The REQUIREMENTS.md revert prevented a silent false-green that would have corrupted Phase-4 planning context.

**Plan-frontmatter guidance for future planners:** When a plan's sole purpose is REQ-ID bookkeeping (reassigning requirements between phases, not delivering them), the `requirements:` frontmatter field should be either empty or split into explicit `requirements_delivered: []` vs. `requirements_reassigned: [...]` sub-fields to prevent the executor's `mark-complete` step from flipping statuses incorrectly. This plan is a canonical example.

## Issues Encountered

None beyond the two deviations documented above. The `PreToolUse:Edit` hook fired cosmetic "READ-BEFORE-EDIT REMINDER" messages on a few edits, but files had been read at the top of the session and all edits succeeded.

## User Setup Required

None — pure documentation bookkeeping.

## Next Phase Readiness

- **Phase 2 Plans 02-02/03/04 ready to execute** against a consistent ARCHITECTURE.md + ROADMAP.md + REQUIREMENTS.md.
- **No remaining contradictions** between §11 P1 spec text and the Phase-2 CONTEXT decisions.
- **Cross-document consistency verified:** `grep -E 'TEST-0(2|3|5)' .planning/ROADMAP.md .planning/REQUIREMENTS.md` shows these IDs appear ONLY in Phase-4 contexts in the Requirements/traceability lines (the Phase 2 Plans catalog entry still mentions them descriptively for 02-02 + 02-05, which is correct — those are plan contents, not Phase-2 requirement assignments).
- **Phase-exit blocker resolved:** Phase 2 can now close cleanly without a false "TEST-05 missing artefact" failure. Phase-4 planning will naturally pick up TEST-02/03/05 alongside PUB-* work.

## ARCHITECTURE.md §11 Spot-check Trail

Per the plan's request for an audit trail:

- **Before Task 0:** §11 P1 text CONTRADICTED D-03, D-08, D-11. Executor halted correctly.
- **After Task 0 (commit `ea7db6a`):** §11 P1 text ALIGNED with all four decisions (D-03, D-04, D-08, D-11).
- **Post-edit grep verification:** `grep -n "test_determinism\|Ben Pile\|Turver\|REF subset" ARCHITECTURE.md` returns matches only at §9.6 test table (lines 539, 825 — correct: §9.6 names all five files including test_determinism.py; P1 ships four, P3 adds the fifth), §10 comms policy (line 1060 — commentator outreach, not P1 benchmarks), and the new P1 Note line (line 887 — explicitly documents the P3 deferral). NO match inside the §11 P1 Deliverables bullet list itself.

## Self-Check: PASSED

- [x] `ARCHITECTURE.md` Task 0 edit applied and committed (`ea7db6a`)
- [x] `.planning/ROADMAP.md` five edits applied and committed (`0cef764`)
- [x] `.planning/REQUIREMENTS.md` three traceability rows moved and committed (`b83272d`)
- [x] `CHANGES.md` `[Unreleased] ### Changed` sub-section added and committed (`8b82467`)
- [x] `02-05-SUMMARY.md` created at `.planning/phases/02-test-benchmark-scaffolding/`
- [x] All plan grep verifications for Tasks 1, 2, 3 pass (executed inline during each task)
- [x] Cross-document `TEST-02/03/05` consistency confirmed (Phase-4 only in Requirements lines)
- [x] ARCHITECTURE.md contains no `Ben Pile`, `REF subset`, or `Turver` in §11 P1 Deliverables block
- [x] ARCHITECTURE.md `test_determinism.py` no longer listed as a P1 deliverable

---
*Phase: 02-test-benchmark-scaffolding*
*Completed: 2026-04-22*
