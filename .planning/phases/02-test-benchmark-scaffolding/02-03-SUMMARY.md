---
phase: 02-test-benchmark-scaffolding
plan: 03
subsystem: testing
tags: [benchmarks, reconciliation, lccc-floor, pydantic, yaml, pytest-parametrize]

# Dependency graph
requires:
  - phase: 02-test-benchmark-scaffolding
    provides: "Plan 02-02 pandera schemas + test_schemas.py + test_aggregates.py scaffolding (load_lccc_dataset validated at read-time)"
  - phase: 01-foundation-tidy
    provides: "`src/uk_subsidy_tracker.data.load_lccc_dataset` (post-rename package path) + CHANGES.md Keep-a-Changelog scaffolding"
provides:
  - "Pydantic-validated benchmarks fixture loader (`tests/fixtures/__init__.py`)"
  - "Structured benchmark provenance store (`tests/fixtures/benchmarks.yaml`)"
  - "LCCC self-reconciliation floor test (CONTEXT D-10, mandatory 0.1% red-line) — skips cleanly per D-11 fallback"
  - "Parametrised external-anchor benchmark test (OBR / Ofgem / DESNZ / HoC / NAO) with per-source named tolerance constants + CHANGES.md-bump discipline per D-07"
  - "`tests/__init__.py` — makes tests/ a package so `from tests.fixtures import ...` resolves under pytest collection"
affects: [phase-02-04-ci-workflow, phase-04-publishing-layer, phase-05-ro-module, future-scheme-benchmarks]

# Tech tracking
tech-stack:
  added: []  # All dependencies already in pyproject.toml (pydantic, pyyaml, pytest)
  patterns:
    - "Two-layer Pydantic loader for YAML fixtures: `BenchmarkEntry` + `Benchmarks` mirrors `LCCCDatasetConfig` + `LCCCAppConfig` from `src/uk_subsidy_tracker/data/lccc.py`"
    - "Source-key injection: parent YAML key set as `source` field on each entry before Pydantic validation, so test-side failure messages can cite the source"
    - "Tolerance constants as module-level named constants with docstring rationale (CONTEXT D-06); tolerance bumps require CHANGES.md `## Methodology versions` entry (D-07)"
    - "Parametrised test iterating over an optionally-empty provenance list (D-11 fallback posture) — zero parametrisations is not a failure"
    - "Collection-time parametrisation (`@pytest.mark.parametrize(..., _collect_external_entries(), ids=lambda e: f'{e.source}-{e.year}')`) gives human-readable test IDs and graceful zero-entry handling"

key-files:
  created:
    - "tests/fixtures/__init__.py"
    - "tests/fixtures/benchmarks.yaml"
    - "tests/test_benchmarks.py"
    - "tests/__init__.py"
  modified:
    - "CHANGES.md"

key-decisions:
  - "Shipped D-11 fallback posture: `lccc_self: []` in benchmarks.yaml. The LCCC ARA 2024/25 PDF aggregate was not transcribed in this pass — a wrong floor is worse than no floor per D-10. Follow-up filed for Phase 3/4 to transcribe the calendar-year figure and activate the mandatory floor check."
  - "All external-anchor sections (ofgem_transparency, obr_efo, desnz_energy_trends, hoc_library, nao_audit) also ship empty per D-11. OBR EFO November 2025 figure (CfD 2024/25 = £2.3bn FY) needs calendar-year translation via quarterly breakdown from supplementary fiscal tables — deferred to a future phase."
  - "Added `tests/__init__.py` (Rule 3 — blocking fix). Pytest collection could not resolve `from tests.fixtures import ...` without tests being a package. No pytest config change required; `tests/` was not previously a package (RESEARCH.md pattern 5 assumed it already was)."
  - "Tolerance lookup via `_TOLERANCE_BY_SOURCE: dict[str, float]` dispatches named module-level constants by source key. Missing source falls back to `entry.tolerance_pct` (per-entry YAML field) for forward compatibility with as-yet-unnamed sources."
  - "Single `test(02-03)` commit for Task 2 (test file + CHANGES.md + tests/__init__.py) rather than separate test→feat commits — the plan's TDD RED/GREEN cycle degenerates under D-11 fallback (tests skip on empty data, never fail-then-pass), so RED/GREEN commit separation is not meaningful here."

patterns-established:
  - "Benchmark provenance shape (CONTEXT D-05): every entry carries source, year, value_gbp_bn, url (HttpUrl validated), retrieved_on (date), notes, tolerance_pct. Future scheme benchmarks (RO, FiT, Constraints...) reuse this shape under new top-level YAML keys (`ro_self`, `turver_ro_aggregate`, etc.)."
  - "Failure-message-as-documentation: tolerance-exceedance failures instruct the PR author through the three allowed resolution paths (fix pipeline / document divergence in CHANGES.md / bump tolerance with rationale). Silent tolerance creep is structurally forbidden."
  - "Collection-time parametrisation with try/except fallback: `_collect_external_entries()` returns `[]` if the loader raises, so fixture-loading errors degrade gracefully at collection time instead of blocking the entire test module."

requirements-completed: [TEST-04]

# Metrics
duration: 8min
completed: 2026-04-22
---

# Phase 02 Plan 03: Benchmarks fixture + reconciliation tests Summary

**Pydantic-validated benchmarks fixture + LCCC self-reconciliation floor (CONTEXT D-10) + parametrised external-anchor tolerance tests shipped in D-11 fallback posture.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-04-22T11:08:00Z (approx)
- **Completed:** 2026-04-22T11:16:00Z (approx)
- **Tasks:** 2
- **Files modified:** 5 (4 created, 1 modified)

## Accomplishments

- Two-layer Pydantic benchmarks loader (`BenchmarkEntry`, `Benchmarks`, `load_benchmarks()`) mirroring the `LCCCDatasetConfig` / `LCCCAppConfig` idiom from `src/uk_subsidy_tracker/data/lccc.py`. HttpUrl + date types auto-validate upstream provenance; source-key injection gives each entry a `source` field for failure-message citation.
- `tests/fixtures/benchmarks.yaml` ships with the D-10 / D-11 fallback posture: `lccc_self: []` plus all external anchor sections empty. When regulator-native figures are transcribed in Phase 3/4, the floor + external-anchor tests activate automatically.
- `tests/test_benchmarks.py` ships both test types per TEST-04: (a) mandatory `test_lccc_self_reconciliation_floor` that skips cleanly with a D-11-citing reason when `lccc_self` is empty, and tolerance-checks at 0.1% when populated; (b) parametrised `test_external_benchmark_within_tolerance` with per-source tolerance dispatch (`_TOLERANCE_BY_SOURCE`) and failure messages that cite the three D-06/D-07 resolution paths.
- Tolerance constants (`LCCC_SELF_TOLERANCE_PCT`, `OBR_EFO_TOLERANCE_PCT`, `OFGEM_TOLERANCE_PCT`, `DESNZ_TOLERANCE_PCT`, `HOC_LIBRARY_TOLERANCE_PCT`, `NAO_TOLERANCE_PCT`) are module-level, named, and docstring-documented per CONTEXT D-06.
- `CHANGES.md [Unreleased] ### Added` extended with two bullets covering the benchmark artefacts.

## Task Commits

1. **Task 1: Pydantic loader + seeded benchmarks YAML** — `396fed2` (feat)
2. **Task 2: LCCC floor + external-anchor tests + CHANGES.md extension** — `09e6621` (test)

**Plan metadata:** (this SUMMARY commit — to be made)

## Files Created/Modified

- `tests/fixtures/__init__.py` — `BenchmarkEntry`, `Benchmarks`, `load_benchmarks()`. Two-layer Pydantic model + `yaml.safe_load` loader with parent-key → `source` injection.
- `tests/fixtures/benchmarks.yaml` — D-11 fallback seed: `lccc_self: []` + all external anchor sections empty. Inline comments document the D-10/D-11 rationale.
- `tests/test_benchmarks.py` — Mandatory LCCC floor (0.1%, skips cleanly under D-11) + parametrised external anchors (per-source tolerance dispatch, empty parametrise handled gracefully).
- `tests/__init__.py` — Empty; makes `tests/` a package so `from tests.fixtures import ...` resolves under pytest collection.
- `CHANGES.md` — `[Unreleased] ### Added` extended with `tests/test_benchmarks.py` and `tests/fixtures/benchmarks.yaml` bullets.

## Decisions Made

- **D-11 fallback shipped, not D-10 floor activation.** The LCCC ARA 2024/25 PDF was not opened/transcribed during this plan's execution window. Per the plan's own guidance ("a wrong floor is worse than no floor"), `lccc_self: []` ships as the safe landing. Follow-up filed for Phase 3/4 to transcribe the calendar-year aggregate and activate the mandatory floor check.
- **All external anchors empty.** OBR EFO, DESNZ Energy Trends, HoC Library, NAO — none transcribed in this pass. The parametrised external test handles zero entries as zero parametrisations (pytest skips with "got empty parameter set"), which is not a failure. External anchors land as follow-ups.
- **Tolerance constants named per source, not per entry.** `_TOLERANCE_BY_SOURCE` dispatches module-level named constants; `entry.tolerance_pct` from YAML is only used as a fallback for sources not in the dict. This matches CONTEXT D-06 (tolerance is a versioned decision-in-source, not a YAML knob) and D-07 (bumps require CHANGES.md entry, which means a code PR, which is grep-visible).
- **`tests/__init__.py` added as a Rule 3 blocking fix.** See Deviations section.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added `tests/__init__.py` for pytest import resolution**

- **Found during:** Task 2 verification (`uv run pytest tests/test_benchmarks.py -v`)
- **Issue:** The plan mandates `from tests.fixtures import BenchmarkEntry, load_benchmarks`. Under pytest 9.0.3 default collection (no `pythonpath` config in `pyproject.toml`, no conftest.py), `tests/` was not importable as a package — pytest raised `ModuleNotFoundError: No module named 'tests.fixtures'` at collection time. Worked via `uv run python -c ...` (CWD on sys.path) but not via pytest (uses rootdir-relative collection).
- **Fix:** Created empty `tests/__init__.py`. Minimal, idiomatic pytest practice; no pytest/pyproject config changes needed; no impact on existing tests (verified 16 pass + 4 skipped, up from 16 + 2 — the two new skips are the intentional D-11 skips of the benchmarks tests, not regressions).
- **Files modified:** `tests/__init__.py` (created).
- **Verification:** `uv run pytest tests/` exit 0; `uv run pytest tests/test_benchmarks.py -v` shows both tests skipped with D-11/empty-parametrise reasons; all existing `tests/data/*.py` still collect and pass.
- **Committed in:** `09e6621` (with Task 2).

---

**Total deviations:** 1 auto-fixed (1 Rule 3 blocking).
**Impact on plan:** Auto-fix essential for pytest import resolution. No scope creep; no pytest config changes; no impact on existing test collection.

## Issues Encountered

- None. Plan executed cleanly once the `tests/__init__.py` blocker was resolved.

## Deferred Follow-ups

1. **Phase 3/4 — Transcribe LCCC ARA 2024/25 calendar-year CfD aggregate** into `tests/fixtures/benchmarks.yaml::lccc_self`. Activates the mandatory D-10 floor check. URL: `https://www.lowcarboncontracts.uk/documents/293/LCCC_ARA_24-25_11.pdf`. Tolerance pinned at 0.1%.
2. **Phase 3/4 — Populate OBR EFO anchor** with calendar-year translation of the November 2025 EFO supplementary fiscal tables. Secondary reporting cites FY 2024/25 CfD = £2.3bn — calendar-year figure requires quarterly breakdown. Tolerance 5%.
3. **Later scheme phases — RO benchmark anchors.** Under Phase 5, add `ro_self` + Turver-aggregate (flagged `non_canonical: true` if ever added per CONTEXT D-08) to the same `tests/fixtures/benchmarks.yaml` file. Same shape; no loader changes required.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `uv run pytest` is green on `main` (16 passed + 4 skipped) ahead of Plan 02-04 (GitHub Actions CI workflow).
- The benchmarks test is compatible with CI — it skips under D-11 rather than failing, so CI does not block on missing external anchors.
- Phase 2 is 4/5 complete. Only Plan 02-04 (CI workflow, TEST-06) remains.
- `TEST-04` is formally complete per this plan's `requirements` frontmatter — the four-test-class Phase 2 deliverable per ROADMAP Phase 2 criterion 1 (counterfactual + schemas + aggregates + benchmarks) is now met.

## Self-Check: PASSED

Files verified to exist on disk:
- `tests/fixtures/__init__.py` — FOUND
- `tests/fixtures/benchmarks.yaml` — FOUND
- `tests/test_benchmarks.py` — FOUND
- `tests/__init__.py` — FOUND
- `CHANGES.md` — FOUND (modified)

Commits verified to exist in `git log`:
- `396fed2` — FOUND (Task 1: feat Pydantic loader)
- `09e6621` — FOUND (Task 2: test LCCC floor + external anchors)

Test suite verified green:
- `uv run pytest tests/` → 16 passed, 4 skipped, exit 0

---
*Phase: 02-test-benchmark-scaffolding*
*Completed: 2026-04-22*
