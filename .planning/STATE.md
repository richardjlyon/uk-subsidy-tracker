---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: planning
stopped_at: Phase 3 context gathered
last_updated: "2026-04-22T15:02:39.654Z"
progress:
  total_phases: 12
  completed_phases: 2
  total_plans: 9
  completed_plans: 9
  percent: 100
---

# Project State: UK Renewable Subsidy Tracker

**Last updated:** 2026-04-22
**Session:** Phase 02 Plan 04 — complete (GitHub Actions CI workflow green on push + pull_request; Phase 2 all 5 plans complete; 3 retrospective Phase-1 shortfalls surfaced and resolved)

---

## Project Reference

**Core value:** Every headline number on the site is reproducible from a single `git clone` + `uv sync` + one command, backed by a methodology page, traceable to a primary regulator source, and survives hostile reading.

**Project docs:**

- `.planning/PROJECT.md` — scope, constraints, key decisions
- `.planning/REQUIREMENTS.md` — v1 requirements with REQ-IDs
- `.planning/ROADMAP.md` — 12-phase plan (P0–P11 mapping)
- `ARCHITECTURE.md` — authoritative design document (§11 has phase plan)
- `RO-MODULE-SPEC.md` — per-scheme module template

**Brownfield note:** Package currently named `cfd_payment`. Phase 1 renames it to `uk_subsidy_tracker`. All scheme modules in phases 5+ use the post-rename package path.

---

## Current Position

Phase: 02 (test-benchmark-scaffolding) — COMPLETE (5/5 plans)
Plan: all 5 complete (Plans 02-01, 02-02, 02-03, 02-04, 02-05)
**Phase:** 3
**Plan:** Not started
**Status:** Ready to plan
**Focus:** CUT file deletion, seven PROMOTE chart documentation, five-theme docs structure

```
Progress: [████░░░░░░░░░░░░░░░░░░░░] 2/12 phases complete (Phase 2: 5/5 plans)
```

---

## Performance Metrics

**Phases complete:** 2/12
**Plans complete:** 9/9 (Phase 1 closed 4/4; Phase 2 closed 5/5)
**Requirements delivered:** FND-01, FND-02, FND-03, GOV-05, GOV-06 (CITATION.cff portion), TEST-01, TEST-04, TEST-06, GOV-04 (+ TEST-02/03/05 formally reassigned to Phase 4 by 02-05 bookkeeping; pre-Parquet scaffolding for TEST-02/03 shipped by 02-02)
**Test coverage:** 16 passing + 4 skipped. `test_counterfactual.py` (6), `test_schemas.py` (5, pre-Parquet scaffolding), `test_aggregates.py` (2, pre-Parquet scaffolding), `test_benchmarks.py` (2 skipped per D-11 fallback — no lccc_self entries, no external anchors transcribed), plus legacy `tests/data/*` (3 passing + 2 skipped). All four §9.6 Phase-2 test classes now present. `test_determinism.py` deferred to Phase 4 per 02-CONTEXT D-03 (confirmed by 02-05 bookkeeping).

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| 02-01 Counterfactual pin + GOV-04 | 3 min | 3 | 3 |
| 02-05 Scope-correction bookkeeping | 5 min | 4 (incl. Task 0 user-approved) | 4 |
| 02-02 Pandera schemas + test_schemas.py + test_aggregates.py scaffolding | 2 min | 3 | 5 |
| Phase 02 P03 | 8min | 2 tasks | 5 files |
| Phase 02 P04 | 30min | 2 tasks | 2 files |

## Accumulated Context

### Key Decisions Made

| Decision | Rationale |
|----------|-----------|
| 12 GSD phases mapping 1:1 to ARCHITECTURE.md §11 (P0–P11) | User explicitly chose to preserve §11's plan rather than re-bucket |
| GOV requirements distributed across earliest applicable phase | Cross-cutting governance belongs where the mechanism is first built |
| GOV-06 split: CITATION.cff → Phase 1, snapshot URLs → Phase 4 | CITATION.cff is a static doc file; snapshot mechanism is a publishing-layer concern |
| X-04 and X-05 included in Phase 6 | Both are cross-scheme portal charts; Phase 6 already builds X1/X2/X3 cross-scheme infrastructure |
| TRIAGE-04 assigned to Phase 3 | "Every PRODUCTION chart reachable from theme nav" is the exit criterion for Phase 3 triage work |
| Package rename is Phase 1 gate | All subsequent Python code assumes `uk_subsidy_tracker`; rename must land before any new module work |
| GOV-04: METHODOLOGY_VERSION = 1.0.0 + DataFrame column (02-01) | SemVer-shaped module constant (PATCH/MINOR/MAJOR policy); column on `compute_counterfactual()` output propagates the version into any Phase-4 Parquet/manifest — structural handshake, not convention |
| TEST-01: 4-parametrised pin test + remediation-hook failure message (02-01) | `round(actual, 4) == expected` at 4dp across 2019/2022 + zero-gas regression; failure message tells the PR author to bump METHODOLOGY_VERSION + add CHANGES.md entry, making silent constant drift structurally impossible |
| ARCHITECTURE.md §11 P1 amended before ROADMAP edits (02-05 Task 0, user-approved) | Per user memory project_spec_source.md: when ARCHITECTURE.md and ROADMAP disagree, the spec wins. Executor halted correctly on spec-precedence check; user approved Option 1 (amend spec first). test_determinism.py removed from P1 Deliverables (deferred to P3); Ben Pile / REF / Turver anchor replaced by LCCC + regulator-native sources; test_schemas.py + test_aggregates.py added as P1 deliverables with "Parquet variants in P3" qualifier. |
| TEST-02/03/05 formally reassigned Phase 2 → Phase 4 (02-05) | Phase 2 ships pre-Parquet scaffolding variants of test_schemas.py + test_aggregates.py today (useful-today scaffolding, not formal satisfaction); Phase 4 adds Parquet variants + test_determinism.py to close the three formal requirements. ROADMAP.md + REQUIREMENTS.md + CHANGES.md all aligned. |
| Loader-owned pandera validation (02-02) | `.validate()` inside the loader body (not in the test) means every caller benefits — charts, ad-hoc notebooks, future scheme modules — not only the pytest run. Matches the pre-existing `load_lccc_dataset` idiom verbatim. Schema drift fails at read-time, not silently downstream. |
| Row-conservation via `pd.testing.assert_series_equal` (02-02) | Decomposed-then-collapsed groupby sums are algebraically identical under pandas; exact equality is the correct assertion. Tolerance-based comparison would mask the actual failure mode (groupby drops rows on NaN keys). |
| TEST-04: D-11 fallback shipped, not D-10 floor activation (02-03) | `lccc_self: []` in benchmarks.yaml, all external sections empty. LCCC ARA 2024/25 PDF transcription deferred to Phase 3/4 — per plan's own guidance, a wrong floor is worse than no floor. Floor test skips cleanly with D-11-citing reason string; external test parametrises over zero entries (not a failure). |
| TEST-04: Two-layer Pydantic model + source-key injection (02-03) | `BenchmarkEntry` + `Benchmarks` mirrors `LCCCDatasetConfig` + `LCCCAppConfig` from `src/uk_subsidy_tracker/data/lccc.py`. Loader injects parent YAML key as `source` field on each entry before Pydantic validation so test-side failure messages can cite the source by name. |
| TEST-04: Tolerance constants named per-source, not per-entry (02-03) | `LCCC_SELF_TOLERANCE_PCT`, `OBR_EFO_TOLERANCE_PCT` etc. are module-level constants with docstring rationale (D-06). `_TOLERANCE_BY_SOURCE` dict dispatches by source key; `entry.tolerance_pct` YAML field is only a fallback for unnamed sources. Tolerance bumps require CHANGES.md `## Methodology versions` entry (D-07), which means a code PR, which is grep-visible in review. |
| `tests/__init__.py` added as Rule 3 blocking fix (02-03) | Pytest 9.0.3 could not resolve `from tests.fixtures import ...` at collection time without `tests/` being a package. Minimal empty `__init__.py` fixes this without pytest/pyproject config changes; existing `tests/data/*` still collects and passes. |

### Blockers

None currently.

### Todos

- [x] Plan Phase 1 (`/gsd-plan-phase 1`)
- [x] Execute Phase 1 (`/gsd-execute-phase 1`) — 4/4 plans, 5/5 success criteria, MIT licence
- [ ] Rename GitHub repo `cfd-payment` → `uk-subsidy-tracker` (manual UI step; `correction` label already created and will travel on rename)
- [x] Plan Phase 2 (`/gsd-plan-phase 2`)
- [x] Execute Phase 2 Plan 01 — counterfactual pin + GOV-04 seed
- [x] Execute Phase 2 Plan 05 — scope-correction bookkeeping (ROADMAP + REQUIREMENTS + CHANGES + ARCHITECTURE §11 P1 amendment)
- [x] Execute Phase 2 Plan 02 — pandera schemas on elexon/ons_gas + `tests/test_schemas.py` + `tests/test_aggregates.py` pre-Parquet scaffolding
- [x] Execute Phase 2 Plan 03 — `tests/test_benchmarks.py` + `tests/fixtures/benchmarks.yaml` (D-11 fallback shipped)
- [x] Execute Phase 2 Plan 04 — GitHub Actions CI workflow green on push + pull_request (TEST-06; runs 24775720044 + 24775750701)
- [x] Rename GitHub repo (resolved via fresh `richardjlyon/uk-subsidy-tracker` + archive of `cfd-payment`; retrospective Phase-1 shortfall surfaced and closed in Plan 02-04)
- [ ] Plan Phase 3 (`/gsd-plan-phase 3`) — Chart Triage Execution (CUT files, seven PROMOTE charts, five-theme docs)
- [ ] Execute Phase 3
- [ ] Phase 3/4: transcribe LCCC ARA 2024/25 calendar-year CfD aggregate into `tests/fixtures/benchmarks.yaml::lccc_self` to activate the mandatory D-10 floor check
- [ ] Phase 3/4: populate external benchmark anchors (OBR EFO calendar-year translation, DESNZ, HoC, NAO) as transcribable figures surface

### Notes

- Brownfield rename COMPLETE: `src/cfd_payment/` → `src/uk_subsidy_tracker/` via `git mv` (commits 7b5538b, 596594c)
- Python floor bumped 3.11 → 3.12 in pyproject.toml + CLAUDE.md (B-3 resolved)
- MkDocs theme swapped `readthedocs` → `material` with palette toggle; `docs/methodology/gas-counterfactual.md` now canonical (was `docs/technical-details/`)
- Root docs committed: ARCHITECTURE.md, RO-MODULE-SPEC.md, CHANGES.md, CITATION.cff, LICENSE (MIT), README.md
- `scissors.py` and `bang_for_buck_old.py` still present in working tree (removed in Phase 3)
- CI is now live: `.github/workflows/ci.yml` single-job pytest on push/PR, pinned `astral-sh/setup-uv@v8.1.0` + `actions/checkout@v5`, green on both trigger paths
- GitHub repo lives at `github.com/richardjlyon/uk-subsidy-tracker` (old `cfd-payment` repo archived; origin URL updated locally)
- Raw data files (5 files, each ≤100MB) now committed under `data/` per CLAUDE.md reproducibility policy (retrospective Phase-1 shortfall fixed in commit 75774b8)
- Derived layer (`data/derived/`) does not exist yet; created in Phase 4
- Publishing layer (`site/data/`) does not exist yet; created in Phase 4

---

## Session Continuity

**To resume:** Read `.planning/STATE.md` (this file), then `.planning/ROADMAP.md` for phase structure, then `ARCHITECTURE.md §11` for authoritative exit criteria.

**Next command:** `/gsd-plan-phase 3` — begin planning Phase 3 (Chart Triage Execution). Phase 2 is formally closed: all 5 plans complete, TEST-01 / TEST-04 / TEST-06 / GOV-04 delivered, `.github/workflows/ci.yml` is live and green on both push + pull_request triggers (runs 24775720044, 24775750701). Full suite: 16 passing + 4 skipped on CI, enforced on every PR. Phase 2 CI validation also surfaced and closed three retrospective Phase-1 shortfalls (GitHub repo rename, ARCHITECTURE.md §11 P1 sync, `.gitignore` vs CLAUDE.md data-files policy); see `02-04-SUMMARY.md` for the canonical record.

**Stopped at:** Phase 3 context gathered

---
*State initialized: 2026-04-21 after roadmap creation*
