# Project State: UK Renewable Subsidy Tracker

**Last updated:** 2026-04-21
**Session:** Roadmap initialization

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

**Phase:** 1 — Foundation Tidy
**Plan:** TBD (not yet planned)
**Status:** Not started
**Focus:** Repo rename (`cfd-payment` → `uk-subsidy-tracker`), MkDocs Material theme switch, root docs committed

```
Progress: [░░░░░░░░░░░░░░░░░░░░░░░░] 0/12 phases complete
```

---

## Performance Metrics

**Phases complete:** 0/12
**Requirements delivered:** 0/61
**Test coverage:** Minimal (2 test files; none of the 5 required classes exist)

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

### Blockers

None currently.

### Todos

- [ ] Plan Phase 1 (`/gsd-plan-phase 1`)

### Notes

- Brownfield: `src/cfd_payment/` exists; Phase 1 renames to `src/uk_subsidy_tracker/`
- `scissors.py` and `bang_for_buck_old.py` still present in working tree (removed in Phase 3)
- No CI/CD yet; GitHub Actions workflows created in Phase 2
- Derived layer (`data/derived/`) does not exist yet; created in Phase 4
- Publishing layer (`site/data/`) does not exist yet; created in Phase 4

---

## Session Continuity

**To resume:** Read `.planning/STATE.md` (this file), then `.planning/ROADMAP.md` for phase structure, then `ARCHITECTURE.md §11` for authoritative exit criteria.

**Next command:** `/gsd-plan-phase 1`

---
*State initialized: 2026-04-21 after roadmap creation*
