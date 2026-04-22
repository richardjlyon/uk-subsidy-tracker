---
phase: 04-publishing-layer
plan: 01
subsystem: testing

tags: [dependencies, fixtures, tests, drift, pyarrow, duckdb, seed-001, provenance]

# Dependency graph
requires:
  - phase: 02-test-benchmark-scaffolding
    provides: "BenchmarkEntry / Benchmarks / load_benchmarks two-layer Pydantic + YAML + parent-key-injection fixture pattern; METHODOLOGY_VERSION constant + DataFrame column; test_counterfactual.py parametrised-pin + remediation-hook failure-message template; Provenance: docstring discipline on counterfactual.py constants"
provides:
  - "pyarrow>=24.0.0 + duckdb>=1.5.2 declared + locked; unblocks Parquet I/O for plans 02-05 and DuckDB snippets for plan 06"
  - "tests/fixtures/constants.yaml: six regulator-sourced provenance blocks covering the entire tracked counterfactual constant set (CCGT_EFFICIENCY, GAS_CO2_INTENSITY_THERMAL, DEFAULT_NON_FUEL_OPEX, DEFAULT_CARBON_PRICES_2021/2022/2023)"
  - "tests/fixtures/__init__.py: ConstantProvenance + Constants Pydantic models + load_constants() loader — co-located with existing BenchmarkEntry/load_benchmarks"
  - "tests/test_constants_provenance.py: 13-case drift tripwire (6 name-in-yaml + 6 value-matches-live + 1 non-failing audit-overdue warning); enforces SEED-001 Tier 2"
  - "CHANGES.md [Unreleased] entry documenting the four artefacts above"
affects:
  - 04-02-raw-layer-migration  # will touch data/raw/ paths — orthogonal, but tests remain the gate
  - 04-03-derived-layer-cfd-schemes  # every Parquet writer imports pyarrow
  - 04-04-publishing-layer-manifest  # manifest.methodology_version flows from counterfactual.METHODOLOGY_VERSION which is now under drift-test enforcement
  - 04-05-workflows-refresh-deploy  # CI will run this drift test on every push/PR
  - 04-06-docs-and-benchmark-floor  # docs/data/index.md uses duckdb snippets

# Tech tracking
tech-stack:
  added:
    - "pyarrow==24.0.0 (Parquet I/O + test_determinism content-identity strip)"
    - "duckdb==1.5.2 (docs/data/index.md journalist snippets + future validate() helper)"
  patterns:
    - "Two-layer Pydantic + YAML + parent-key injection: load_constants() mirrors load_benchmarks() exactly (Constants wraps entries dict; ConstantProvenance is the row model; parent YAML key injected as `name` before validation)."
    - "Reflection-based tracked-constant discovery: _live_constants() iterates dir(counterfactual) for UPPERCASE numeric attrs, expands DEFAULT_CARBON_PRICES dict into synthetic DEFAULT_CARBON_PRICES_{year} keys, filters bools explicitly."
    - "Parametrised pin + remediation-hook test shape (already established in test_counterfactual.py) reused: exact-equality assertion with failure message citing METHODOLOGY_VERSION + constants.yaml + CHANGES.md `## Methodology versions`."
    - "Non-failing warnings for calendar-event assertions: test_audits_not_overdue uses warnings.warn rather than assert, on the principle that `next_audit < today` is a to-do item, not broken code."

key-files:
  created:
    - "tests/fixtures/constants.yaml"
    - "tests/test_constants_provenance.py"
    - ".planning/phases/04-publishing-layer/04-01-SUMMARY.md"
  modified:
    - "pyproject.toml (+ pyarrow>=24.0.0, duckdb>=1.5.2)"
    - "uv.lock (resolved pyarrow==24.0.0, duckdb==1.5.2)"
    - "tests/fixtures/__init__.py (+ ConstantProvenance + Constants + load_constants; __all__ expanded; module docstring updated)"
    - "CHANGES.md ([Unreleased] entry)"

key-decisions:
  - "Tracked DEFAULT_NON_FUEL_OPEX (the canonical, policy-answering alias) rather than the underlying CCGT_EXISTING_FLEET_OPEX_PER_MWH in _TRACKED. Both live on the module at value 5.0; both surface in _live_constants(); only the alias is enforced. If the alias is redefined to point elsewhere (or the underlying changes while the alias is hand-rewritten), the drift test fires. CCGT_NEW_BUILD_CAPEX_OPEX_PER_MWH (sensitivity-only, value 20.0) is not in _TRACKED per plan scope."
  - "Explicit bool exclusion in _live_constants(): isinstance(value, bool) check before isinstance(value, (int, float)) — Python bools are an int subclass, and leaking a future FLAG_FOO = True into tracked numerics would produce a confusing drift failure."
  - "YAML entries carry `unit` field (plan-specified) AND `notes` field (free-form audit-trail). GAS_CO2_INTENSITY_THERMAL.notes records the 2026-04-22 correction from 0.184 as the tripwire origin, giving future maintainers the story without needing git blame."

patterns-established:
  - "Provenance YAML co-location: tests/fixtures/*.yaml is now the project's machine-queryable audit trail — two families (benchmarks.yaml from Phase 2, constants.yaml from Phase 4). Future schemes add more families; same loader shape applies."
  - "Test-first execution for new tripwires: the test file was authored before the loader + YAML, verified RED (ImportError on load_constants), then each step turned the test progressively GREEN. The RED evidence is captured in the task commit story."
  - "Drift-proof manual verification in acceptance criteria: edit a tracked constant → observe remediation message → revert → re-verify green. Documents the tripwire's user experience so future reviewers know what a genuine drift looks like."

requirements-completed:
  - GOV-04

# Metrics
duration: 5min
completed: 2026-04-22
---

# Phase 4 Plan 01: Wave 0 — Deps + Constants Drift Test Summary

**Added pyarrow==24.0.0 + duckdb==1.5.2 dependencies and shipped the SEED-001 Tier 2 drift tripwire (6 tracked counterfactual constants, 13 test cases, remediation-hook failure message) — the enforcement layer that would have caught the Phase-2 `0.184` vs `0.18290` incident.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-04-22T22:58:11Z
- **Completed:** 2026-04-22T23:03:00Z (approx)
- **Tasks:** 3 completed (3/3)
- **Files modified:** 6 (2 new test/fixture, 1 extended fixture, 1 new YAML, 2 dep-config: pyproject.toml + uv.lock, 1 docs: CHANGES.md)

## Accomplishments

- **pyarrow + duckdb unblocked all downstream Phase-4 plans.** pyarrow is required by every Parquet writer in plans 02-05 and by the `test_determinism.py` content-identity strip. duckdb is referenced in the `docs/data/index.md` journalist-how-to snippets (plan 06) and is declared in ARCHITECTURE §3 alongside Parquet as the project's canonical OLAP engine.
- **SEED-001 Tier 2 scaffold shipped: the tripwire now exists.** The Phase-2 constant-drift incident (`GAS_CO2_INTENSITY_THERMAL = 0.184` wrong vs `0.18290` correct) was caught by user inspection only; Tier-1 `Provenance:` grep-discipline missed it. `tests/test_constants_provenance.py` is the enforcement layer that makes the "bump METHODOLOGY_VERSION + update constants.yaml + add CHANGES.md entry" discipline machine-checkable on every push/PR. Manual drift-verification (edit `CCGT_EFFICIENCY` 0.55 → 0.56, observe remediation message, revert) confirmed the tripwire fires with the full three-step remediation message.
- **Pydantic + YAML fixture pattern extended, not duplicated.** `ConstantProvenance`/`Constants`/`load_constants()` co-locate with `BenchmarkEntry`/`Benchmarks`/`load_benchmarks()` in `tests/fixtures/__init__.py` — same two-layer Pydantic model, same `yaml.safe_load` + parent-key-injection idiom. Future `tests/fixtures/*.yaml` families (Phase 5+ schemes) follow this template.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add pyarrow + duckdb to pyproject.toml; refresh uv.lock** — `b9c8233` (chore)
2. **Task 2: Create tests/fixtures/constants.yaml + extend fixtures loader + ship drift test** — `f2548df` (test)
   - Single atomic commit for TDD cycle: test file (RED) + loader extension (GREEN step 1) + YAML (GREEN step 2) shipped together per plan's sub-steps 2A/2B/2C. Plan authorised single task-commit containing all three sub-step artefacts.
3. **Task 3: CHANGES.md [Unreleased] entry for Wave 0** — `a2704df` (docs)

**Test count:** 23 passed + 4 skipped → 36 passed + 4 skipped (+13 new cases, zero regressions).

## Files Created/Modified

### Created
- `tests/fixtures/constants.yaml` — Six provenance entries (CCGT_EFFICIENCY, GAS_CO2_INTENSITY_THERMAL, DEFAULT_NON_FUEL_OPEX, DEFAULT_CARBON_PRICES_2021/2022/2023). Each block mirrors the live `Provenance:` docstring field-for-field: source, url, basis, retrieved_on, next_audit, value, unit, notes.
- `tests/test_constants_provenance.py` — 13 test cases: 6 × parametrised `test_every_tracked_constant_in_yaml`, 6 × parametrised `test_yaml_value_matches_live` (exact-equality drift detector), 1 × non-failing `test_audits_not_overdue` (calendar-event warning). Module docstring cites the `0.184`-vs-`0.18290` incident as the tripwire's motivation.

### Modified
- `pyproject.toml` — Added `duckdb>=1.5.2` and `pyarrow>=24.0.0` via `uv add` (alphabetical placement inside `[project.dependencies]`).
- `uv.lock` — Resolved pyarrow==24.0.0, duckdb==1.5.2, plus transitive resolution delta. Wheels available for Python 3.12 + 3.13 on macOS-arm64; linux-x86_64 wheels standard.
- `tests/fixtures/__init__.py` — Module docstring updated to describe both fixture families. Added `ConstantProvenance` (per-entry), `Constants` (container with `entries: dict`), `load_constants()` (yaml.safe_load + parent-key-injection via `name` field). `__all__` expanded to six names.
- `CHANGES.md` — `[Unreleased] ### Added` section gains three bullets (pyarrow/duckdb dep add; constants.yaml scaffold; fixtures loader extension; test_constants_provenance.py drift tripwire). No `## Methodology versions` entry (METHODOLOGY_VERSION stays `"0.1.0"` per CONTEXT D-12 + pre-existing condition).

## Resolved Versions

From `uv pip show`:
```
pyarrow: 24.0.0
duckdb:  1.5.2
```

Python runtime: 3.13.11 (project floor: 3.12). Both packages resolved wheel-directly for the target platform; no build-from-source step required.

## Decisions Made

- **DEFAULT_NON_FUEL_OPEX tracked instead of CCGT_EXISTING_FLEET_OPEX_PER_MWH.** Both constants reside on the module at value `5.0` (Python-level alias: `DEFAULT_NON_FUEL_OPEX = CCGT_EXISTING_FLEET_OPEX_PER_MWH`). The plan's `_TRACKED` template suggested "DEFAULT_NON_FUEL_OPEX (or CCGT_EXISTING_FLEET_OPEX_PER_MWH — match the actual live constant name)". Chose the alias because its docstring is the policy-answering one ("what if we'd stuck with the gas fleet we already had instead of building renewables?") and it is the name used as a default kwarg in `compute_counterfactual()`. If the alias gets hand-rewritten to a different value while the underlying constant stays at 5.0 (a realistic refactor hazard), the drift test fires.
- **Bool exclusion in `_live_constants()`.** Python bools are an `int` subclass, so a future `FLAG_FOO = True` would satisfy `isinstance(value, (int, float))`. An explicit `isinstance(value, bool)` early-exit keeps the tracked numeric set semantically clean and avoids mysterious `test_yaml_value_matches_live[FLAG_FOO]` failures in hypothetical future refactors.
- **CCGT_NEW_BUILD_CAPEX_OPEX_PER_MWH NOT in `_TRACKED`.** This is the sensitivity-analysis-only constant (value 20.0, new-build counterfactual). Plan scope listed six tracked constants only; adding this one would require a seventh YAML entry with no plan authorisation. Future plan may promote it if the sensitivity chart becomes production.

## Deviations from Plan

None - plan executed exactly as written.

- All three tasks completed in the order specified.
- TDD sequence followed for Task 2 (RED → GREEN): test file authored first, collection confirmed failing with `ImportError: cannot import name 'load_constants'`, then loader extended, then YAML authored; final run showed 13 passed in 0.50s.
- No auth gates, no blocking errors, no architectural decisions required.
- No Rule-1/2/3 auto-fixes needed.
- `METHODOLOGY_VERSION` left at `"0.1.0"` per CONTEXT D-12 + Task 3's explicit "do NOT bump" instruction.

## Issues Encountered

- **Stale Python bytecode cache during drift-proof manual test.** After `sed`-editing `CCGT_EFFICIENCY = 0.55` → `0.56` and reverting with `mv .bak`, pytest reported the constant as `0.56` despite the file showing `0.55`. Root cause: Python imported the `.pyc` from `__pycache__/` rather than re-compiling the restored source. Cleared both `src/uk_subsidy_tracker/__pycache__` and `tests/__pycache__`, reran — 13 passed. This is an interpreter-level artefact, not a test or plan bug; documented here so the next person attempting a drift-proof dry-run clears caches first.

## User Setup Required

None - no external service configuration required.

## Verification Results

**Success criteria (from plan):**

| Criterion | Result |
|---|---|
| `uv sync --frozen` installs pyarrow≥24.0.0 and duckdb≥1.5.2 | PASS (24.0.0 + 1.5.2) |
| `uv run pytest tests/test_constants_provenance.py -v` reports 13 passed | PASS (13 passed, 0 failed) |
| `tests/fixtures/constants.yaml` has entries for 6 counterfactual constants | PASS (6 top-level keys) |
| `tests/fixtures/__init__.py` exports `ConstantProvenance`, `Constants`, `load_constants` via `__all__` | PASS |
| `CHANGES.md` [Unreleased] section mentions pyarrow + duckdb + constants.yaml + test_constants_provenance | PASS (all four greps green) |
| All pre-existing tests still pass (23 + 4) plus 13 new passes | PASS (36 passed + 4 skipped) |
| `METHODOLOGY_VERSION` in `counterfactual.py` is unchanged (still `"0.1.0"`) | PASS (line 38 grep: `METHODOLOGY_VERSION: str = "0.1.0"`) |

**Plan verifications (from plan's `<verification>` block):**

| Check | Result |
|---|---|
| `uv run pytest tests/test_constants_provenance.py -v` — 13 passes | PASS |
| `uv run pytest tests/` — full suite green | PASS (36 passed + 4 skipped) |
| `uv run python -c "import pyarrow, duckdb"` — both import cleanly | PASS |
| `grep -q "class ConstantProvenance" tests/fixtures/__init__.py` | PASS |
| Drift-proof manual verification (edit → fails with "Drift detected" → revert → passes) | PASS (remediation message cites METHODOLOGY_VERSION `'0.1.0'` + YAML URL) |
| `uv run mkdocs build --strict` — docs build clean | PASS (built in 0.44s, 0 warnings) |

## Next Plan Readiness

**Plan 04-02 (raw-layer migration) is unblocked.** It can now:
- Import `pyarrow` for any Parquet-related work (not strictly needed in 04-02 but available for follow-ups).
- Run the drift test on every commit — if 04-02 touches `counterfactual.py` constants unintentionally, CI catches it before merge.

**Plans 04-03 through 04-06 are unblocked.** All downstream Parquet I/O + DuckDB snippet work has its dependency foundation.

**No known blockers** for the remaining five Phase-4 plans from this Wave-0 base.

## Self-Check: PASSED

- [x] `tests/fixtures/constants.yaml` exists
- [x] `tests/test_constants_provenance.py` exists
- [x] `tests/fixtures/__init__.py` modified (contains `class ConstantProvenance`, `def load_constants`)
- [x] `pyproject.toml` modified (pyarrow + duckdb present)
- [x] `uv.lock` modified
- [x] `CHANGES.md` modified
- [x] Commit `b9c8233` in git log (Task 1: chore deps)
- [x] Commit `f2548df` in git log (Task 2: test drift tripwire)
- [x] Commit `a2704df` in git log (Task 3: docs CHANGES entry)

---
*Phase: 04-publishing-layer*
*Plan: 01 (Wave 0)*
*Completed: 2026-04-22*
