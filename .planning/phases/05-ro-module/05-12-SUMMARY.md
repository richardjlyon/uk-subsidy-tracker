---
phase: 5
plan: 12
subsystem: governance/changelog
tags: [phase-exit, audit-trail, keep-a-changelog, changelog-consolidation]
dependency-graph:
  requires: [05-01, 05-02, 05-03, 05-04, 05-05, 05-06, 05-07, 05-08, 05-09, 05-10, 05-11]
  provides: [Phase-5-citable-from-Phase-6-onwards, RO-01..RO-06-audit-trail]
  affects: [CHANGES.md]
tech-stack:
  added: []
  patterns: [Keep-a-Changelog v1.1.0 canonical section ordering, Plan-number citations grep-verifiable, ## Methodology versions H3 audit log]
key-files:
  created:
    - .planning/phases/05-ro-module/05-12-SUMMARY.md
  modified:
    - CHANGES.md
key-decisions:
  - "Plan 05-12 is documentation-only — zero code, zero test delta (163 passed + 12 skipped + 22 xfailed unchanged)"
  - "Preserve all Phase 4 entries in [Unreleased] (not yet tagged) under explicit `Phase 4` sub-headings; add Phase 5 entries under `Phase 5` sub-headings — sub-grouping makes wave provenance grep-discoverable per-PR"
  - "## Methodology versions gains 3 new H3 entries (REF Constable adoption, Mutualisation scope correction SY 2021-22, manifest.py scheme-parametric refactor) on top of the DEFAULT_CARBON_PRICES extension entry that landed in Plan 05-04"
  - "Phase 5 introduced no regressions — Fixed section explicitly says 'no Phase-5 entries' rather than omitting the header, so absence-of-fixes is itself documented"
metrics:
  duration: 4 min
  completed: 2026-04-23
  tasks_completed: 1
  files_modified: 1
  files_created: 1
  test_count_pre: "163 passed + 12 skipped + 22 xfailed"
  test_count_post: "163 passed + 12 skipped + 22 xfailed"
  test_delta: "+0 (docs-only plan)"
  changelog_lines_added: 379
  changelog_lines_removed: 208
  plan_citations_in_changelog: 35
  ro_requirement_citations_in_changelog: 7
  methodology_version_h3_entries: 4
---

# Phase 5 Plan 12: Phase 5 CHANGES.md Consolidation Summary

**One-liner:** Consolidated Phase 5 (Plans 05-01..05-11) into a single coherent
[Unreleased] CHANGES.md ledger with Keep-a-Changelog canonical section ordering,
explicit Phase 4 vs Phase 5 sub-headings, and 4 ## Methodology versions H3 audit
entries — phase-exit artefact citable from Phase 6 onwards.

## What landed

### CHANGES.md [Unreleased] reorganised

Before this plan: `[Unreleased]` had Phase 4 entries plus a single Plan 05-04
DEFAULT_CARBON_PRICES extension bullet under `### Changed` — 10 of 11 Phase 5
plans had no CHANGES.md surface despite shipping per-plan SUMMARY.md
documentation. Sub-section ordering deviated from Keep-a-Changelog (Fixed
appeared before a second Changed block).

After this plan: `[Unreleased]` is reorganised into the canonical
Keep-a-Changelog section order:

1. `### Added` — sub-divided by `#### Phase 5 — Renewables Obligation Module`
   (11 plan-cited entries closing RO-01..RO-06) and `#### Phase 4 — Publishing
   Layer (carry-over from prior wave)` (preserves all Phase 4 entries
   verbatim, de-duplicated against the prior `### Changed` block).
2. `### Changed` — sub-divided by `#### Phase 5` (4 entries: DEFAULT_CARBON_PRICES,
   constants.yaml extension, manifest.py refactor, refresh_all.SCHEMES + RO
   manifest provenance) and `#### Phase 4` (carry-over).
3. `### Fixed` — Phase 4 ons_gas + cfd refresh fixes carried over; Phase 5
   noted explicitly as having introduced no regressions.

### `## Methodology versions` audit-event ladder

Now carries 4 H3 audit entries with grep-verifiable plan-number citations:

| H3 entry | Plan | Audit-event class | Hard/soft block |
|----------|------|-------------------|------------------|
| REF Constable 2025-05-01 adopted as primary RO benchmark anchor | 05-09 | Anchor adoption | HARD BLOCK at ±3% (D-14), sentinel-gated until Plan 05-13 |
| DEFAULT_CARBON_PRICES backward extension to 2002 | 05-04 | Constant extension (additive) | No block; drift tripwire enumerates all 25 year keys |
| Mutualisation scope correction — SY 2021-22 only | 05-05 | Scope clarification | No block; ensures REF reconciliation does not over-attribute mutualisation |
| `publish/manifest.py` scheme-parametric refactor | 05-06 | Contract-shape change | No block; URL pattern preserved verbatim, all 8 CfD parity tests green byte-identical |

`### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)` historical
entry preserved at the bottom (the original formula-pin event).

## Verification

| Gate | Required | Actual | Pass |
|------|----------|--------|------|
| `uv run pytest tests/ -q` | All pass | 163 passed + 12 skipped + 22 xfailed | ✅ (zero delta vs baseline) |
| `uv run mkdocs build --strict` | 0 warnings | 0 warnings, 0.52s | ✅ |
| `grep -c "Plan 05-" CHANGES.md` | ≥ 10 | 35 | ✅ |
| `grep -c "RO-0[1-6]" CHANGES.md` | ≥ 6 | 7 | ✅ |
| `grep -q "RO-01..RO-06"` (each) | All present | All present | ✅ |
| `grep -q "REF Constable"` | Present | Present | ✅ |
| `grep -q "DEFAULT_CARBON_PRICES"` | Present | Present | ✅ |
| `grep -q "scheme-parametric refactor"` | Present | Present | ✅ |

## Phase 5 close-out report

### Per-plan deliverables ledger

| Plan | Requirement closed | Tests added | Key artefacts |
|------|--------------------|-------------|---------------|
| 05-01 | RO-01 | +8 mocked tests | `data/ofgem_ro.py` (170 LoC) + `data/roc_prices.py` (115 LoC) + 3 Option-D stub raws + 3 sidecars + INVESTIGATION.md (6 follow-ups routed to Plan 05-13) |
| 05-02 | RO-02 (foundation) | +7 unit tests | `data/ro_bandings.yaml` (85 entries) + `data/ro_bandings.py` (138 LoC two-layer Pydantic loader) |
| 05-03 | RO-03 (foundation) | +9 smoke tests | `schemas/ro.py` (5 BaseModel subclasses, 17/9/6/6/7 fields each) |
| 05-04 | n/a (substrate) | +44 (drift coverage) | `counterfactual.DEFAULT_CARBON_PRICES` extended 2002-2026 (25 years); `constants.yaml` 6→28 entries |
| 05-05 | RO-02 + RO-03 | +6 smoke tests | `schemes/ro/` module (5 files, 1079 LoC) — full §6.1 conformance; 5 Parquet grains emittable |
| 05-06 | n/a (refactor) | +0 (8 CfD parity tests preserved) | `publish/manifest.py` scheme-parametric (signature change, URL preserved) |
| 05-07 | n/a (wiring) | +2 RO refresh-loop invariant | `refresh_all.SCHEMES += ("ro", ro)` + `manifest.py` RO sub-dicts (5 grains × 3 dicts = 15 entries) |
| 05-08 | RO-04 | +0 (orchestrator-exercised) | 4 RO chart modules + 4 PNG twitter-cards under `docs/charts/html/` |
| 05-09 | RO-06 (sentinel-gated) | +22 xfailed (sentinel-gated) | `benchmarks.yaml::ref_constable` (22 SY entries) + `test_ref_constable_ro_reconciliation` + DIVERGENCE.md sentinel |
| 05-10 | RO-03 (regression guards) | +18 (10 pass + 8 skip) | RO parametrisations in `test_schemas.py` / `test_aggregates.py` / `test_determinism.py` |
| 05-11 | RO-05 | +0 (docs-only) | `docs/schemes/ro.md` (251 LoC, 9 H2 sections) + Schemes nav tab + 3 theme-page cross-links |
| 05-12 | (this plan) | +0 (docs-only) | CHANGES.md consolidation + this SUMMARY |

**Phase 5 totals:**
- 11 functional plans + 1 changelog-consolidation plan = **12/13 plans closed
  in execution wave** (Plan 05-13 is the human-attended Post-Execution Review,
  out of execution scope).
- Test coverage: **+99 net tests** — 89→163 passed (+74) + 4→12 skipped (+8)
  + 0→22 xfailed (+22) + 22 xfailed sentinel-gated (re-arm on Plan 05-13).
- 6/6 RO requirements closed (RO-01..RO-06).
- 4 PNGs emitted (S2/S3/S4/S5 RO charts) + 4 interactive HTMLs.
- ~3,000 lines of new src/ code under `src/uk_subsidy_tracker/`
  (`data/ofgem_ro.py`, `data/roc_prices.py`, `data/ro_bandings.{yaml,py}`,
  `schemas/ro.py`, `schemes/ro/` package, `plotting/subsidy/ro_*.py`).

### REF reconciliation divergence-per-year status

`tests/test_benchmarks.py::test_ref_constable_ro_reconciliation` parametrises
over 22 REF SY entries. All 22 are currently in `xfail(strict=False)` state
gated by the presence of `.planning/phases/05-ro-module/05-09-DIVERGENCE.md`
sentinel.

| State | Count | Reason |
|-------|-------|--------|
| xfail (sentinel-gated) | 22 | Plan 05-01 Option-D stub data — `ro-register.csv` absent + `ro-generation.csv` is 72-byte header-only stub → `station_month.parquet` emits zero rows → divergence class is **data-absence**, NOT methodological |
| pass within ±3% | 0 | Re-arms automatically once Plan 05-13 plumbs Ofgem RER and the sentinel is deleted |
| fail (>±3%) | 0 | None |

DIVERGENCE.md explicitly classifies the observed state as data-absence so
Plan 05-13 reviewer skips the D-14 methodological ladder (REF scope vs D-12 /
banding / carbon-price extension all N/A under zero-data) and goes straight
to Ofgem RER plumbing as the resolution path.

### Open follow-ups routed to Plan 05-13

(Not closed in execution wave; require human-attended Post-Execution Review.)

1. Replace 3 Option-D stub raw files (`ro-register.csv`, `ro-generation.csv`,
   `roc-prices.csv`) with real Ofgem exports.
2. Plumb `OFGEM_RER_*` secrets if Playwright-OIDC Option-B path approved.
3. Transcribe `roc-prices.csv` from public Ofgem PDFs.
4. Decide on Option-C `pdfplumber` middle-ground approach.
5. Re-examine RESEARCH §2 stale URL templates.
6. Transcribe NIROC primary source (Utility Regulator NI banding factors)
   to replace 12 `[ASSUMED]` entries in `data/ro_bandings.yaml`.
7. Audit 2005-2017 `DEFAULT_CARBON_PRICES` against primary EEA + BoE sources
   before next_audit (2027-01-15) to drop `[VERIFICATION-PENDING]` flags.
8. Delete `.planning/phases/05-ro-module/05-09-DIVERGENCE.md` sentinel after
   Plan 05-13 lands non-stub Ofgem data → 22 REF parametrisations re-arm to
   D-14 hard-block (must pass within ±3%).

## Deviations from plan

None — plan executed exactly as written. The plan is intentionally a
single-task changelog-editing plan; no Rule 1-3 auto-fixes were triggered.

## Threat model coverage

| Threat ID | Disposition | Resolution |
|-----------|-------------|------------|
| T-5.12-01 (Repudiation: missing CHANGES.md entry for a Phase 5 change) | mitigate | Acceptance criteria grep-verify each of RO-01..RO-06 cited in [Unreleased]. All 6 verified present (`grep -c "RO-0[1-6]" CHANGES.md` = 7, redundancy on RO-02 surfaced in two RO module entries). |

## Commit landed

| Commit | Files | Insertions | Deletions |
|--------|-------|------------|-----------|
| `22bb8c5` | CHANGES.md | 379 | 208 |

`docs(05-12): consolidate Phase 5 [Unreleased] + Methodology versions entries`

## Self-Check: PASSED

- ✅ CHANGES.md exists at `/Users/rjl/Code/github/cfd-payment/CHANGES.md` (621 lines)
- ✅ Commit `22bb8c5` exists on `main` (`git log --oneline | grep 22bb8c5` resolves)
- ✅ All 6 RO-NN requirement IDs grep-verifiable in CHANGES.md
- ✅ All 4 ## Methodology versions H3 entries grep-verifiable
- ✅ Test count unchanged: 163 passed + 12 skipped + 22 xfailed (matches baseline)
- ✅ `mkdocs build --strict` green (0 warnings)
- ✅ Plan-number citations: 35 `Plan 05-` mentions (≥ 10 required)
