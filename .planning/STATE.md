---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
last_updated: "2026-04-22T10:21:15.201Z"
progress:
  total_phases: 12
  completed_phases: 1
  total_plans: 9
  completed_plans: 5
  percent: 56
---

# Project State: UK Renewable Subsidy Tracker

**Last updated:** 2026-04-22
**Session:** Phase 02 Plan 01 — complete (METHODOLOGY_VERSION + pin test + CHANGES.md seed)

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

Phase: 02 (test-benchmark-scaffolding) — EXECUTING
Plan: 2 of 5 (Plan 02-01 complete)
**Phase:** 2 — Test & Benchmark Scaffolding
**Plan:** 02-02 (next)
**Status:** Executing Phase 02
**Focus:** Formula pinning tests, schema conformance, row conservation, external benchmarks, determinism

```
Progress: [██░░░░░░░░░░░░░░░░░░░░░░] 1/12 phases complete (Phase 2: 1/5 plans)
```

---

## Performance Metrics

**Phases complete:** 1/12
**Plans complete:** 5/9 (Phase 1 closed 4/4; Phase 2 now 1/5)
**Requirements delivered:** FND-01, FND-02, FND-03, GOV-05, GOV-06 (CITATION.cff portion), TEST-01, GOV-04
**Test coverage:** `test_counterfactual.py` passing (6 new tests: 2 GOV-04 guards + 4 parametrised pin cases). Still 4 of §9.6's required test classes outstanding (`test_schemas.py`, `test_aggregates.py`, `test_benchmarks.py` land in Phase 2 plans 02-02/03/04; `test_determinism.py` deferred to Phase 4 per 02-CONTEXT D-03).

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| 02-01 Counterfactual pin + GOV-04 | 3 min | 3 | 3 |

---

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

### Blockers

None currently.

### Todos

- [x] Plan Phase 1 (`/gsd-plan-phase 1`)
- [x] Execute Phase 1 (`/gsd-execute-phase 1`) — 4/4 plans, 5/5 success criteria, MIT licence
- [ ] Rename GitHub repo `cfd-payment` → `uk-subsidy-tracker` (manual UI step; `correction` label already created and will travel on rename)
- [x] Plan Phase 2 (`/gsd-plan-phase 2`)
- [x] Execute Phase 2 Plan 01 — counterfactual pin + GOV-04 seed
- [ ] Execute Phase 2 Plan 02 — `tests/test_schemas.py` (pandera scaffolding)
- [ ] Execute Phase 2 Plans 03–05 — aggregates, benchmarks, CI workflow

### Notes

- Brownfield rename COMPLETE: `src/cfd_payment/` → `src/uk_subsidy_tracker/` via `git mv` (commits 7b5538b, 596594c)
- Python floor bumped 3.11 → 3.12 in pyproject.toml + CLAUDE.md (B-3 resolved)
- MkDocs theme swapped `readthedocs` → `material` with palette toggle; `docs/methodology/gas-counterfactual.md` now canonical (was `docs/technical-details/`)
- Root docs committed: ARCHITECTURE.md, RO-MODULE-SPEC.md, CHANGES.md, CITATION.cff, LICENSE (MIT), README.md
- `scissors.py` and `bang_for_buck_old.py` still present in working tree (removed in Phase 3)
- No CI/CD yet; GitHub Actions workflows created in Phase 2
- Derived layer (`data/derived/`) does not exist yet; created in Phase 4
- Publishing layer (`site/data/`) does not exist yet; created in Phase 4

---

## Session Continuity

**To resume:** Read `.planning/STATE.md` (this file), then `.planning/ROADMAP.md` for phase structure, then `ARCHITECTURE.md §11` for authoritative exit criteria.

**Next command:** Execute next plan in Phase 2 (Plan 02-02 — `tests/test_schemas.py` pandera scaffolding).

**Stopped at:** Completed 02-01-PLAN.md (3 tasks, 3 commits: `9e991e8`, `d15bd28`, `3f434ad`; 6 new tests passing).

---
*State initialized: 2026-04-21 after roadmap creation*
