---
phase: 02-test-benchmark-scaffolding
plan: 01
subsystem: testing
tags: [counterfactual, pin-test, methodology-versioning, pytest, semver, gov-04, test-01]

# Dependency graph
requires:
  - phase: 01-foundation-tidy
    provides: "uk_subsidy_tracker package rename; CHANGES.md with ## Methodology versions hook placeholder; pytest >= 9.0.3 in pyproject.toml"
provides:
  - "METHODOLOGY_VERSION constant in uk_subsidy_tracker.counterfactual (importable, SemVer-shaped)"
  - "compute_counterfactual() writes a methodology_version column on the returned DataFrame (propagates to any Phase-4 Parquet/manifest)"
  - "tests/test_counterfactual.py pins the gas counterfactual formula at 4dp against four cases (2019 mid/low-gas, 2022 peak, zero-gas regression)"
  - "CHANGES.md ## Methodology versions seeded with the 1.0.0 entry, unblocking all future methodology bumps"
affects: [02-02, 02-03, 02-04, 02-05, phase-03, phase-04]

# Tech tracking
tech-stack:
  added: []  # No new deps; pytest/pandas/pandera all pre-existing
  patterns:
    - "Module-level METHODOLOGY_VERSION: str = \"1.0.0\" constant with SemVer-policy docstring (patch/minor/major) immediately below other module constants in counterfactual.py"
    - "DataFrame propagation of methodology_version column — assigned after counterfactual_total, before return, so it survives into any downstream Parquet or manifest.json via GOV-02"
    - "Pin test: @pytest.mark.parametrize with hardcoded 4dp expected floats + failure message naming METHODOLOGY_VERSION and CHANGES.md explicitly so the fix path is obvious"
    - "CHANGES.md SemVer sub-section: ### X.Y.Z — YYYY-MM-DD — Short descriptor using em-dash U+2014 separators, bulleted rationale with concrete constants + sources"

key-files:
  created:
    - "tests/test_counterfactual.py"
    - ".planning/phases/02-test-benchmark-scaffolding/02-01-SUMMARY.md"
  modified:
    - "src/uk_subsidy_tracker/counterfactual.py"
    - "CHANGES.md"

key-decisions:
  - "METHODOLOGY_VERSION = 1.0.0 seeds the Phase-2 contract; future constant tweaks (new carbon-price year etc.) require PATCH bumps logged in CHANGES.md"
  - "Pin-test failure message hardcodes the remediation path — PR author is told to bump METHODOLOGY_VERSION + add a CHANGES.md entry. Silent drift impossible."
  - "methodology_version column is intentionally DROPPED by compute_counterfactual_monthly() (resample().mean(numeric_only=True) strips strings). Monthly consumers do not need it; daily is the canonical Phase-4 Parquet input."

patterns-established:
  - "Pattern 1 (GOV-04 constant + column propagation): every future methodology-carrying module follows this shape — module-level SemVer constant, docstring describing bump policy, column assigned on the output DataFrame before return"
  - "Pattern 2 (pin test): parametrized 4dp equality with failure-message remediation hook. Becomes the template for other scheme counterfactuals (RO, FiT, etc.) in later phases"
  - "Pattern 3 (CHANGES.md methodology entry): ### X.Y.Z header + bulleted formula/constants/sources, HTML hook comment preserved above for future entries"

requirements-completed: [TEST-01, GOV-04]

# Metrics
duration: 3min
completed: 2026-04-22
---

# Phase 02 Plan 01: Counterfactual Pin + Methodology Versioning Summary

**METHODOLOGY_VERSION=1.0.0 constant + DataFrame column propagation in counterfactual.py, four-case pin test at 4dp, and CHANGES.md 1.0.0 methodology seed — silent-drift-proof GOV-04 contract landed.**

## Performance

- **Duration:** ~3 min (187 s)
- **Started:** 2026-04-22T10:15:45Z
- **Completed:** 2026-04-22T10:18:52Z
- **Tasks:** 3 / 3
- **Files modified:** 2 (`counterfactual.py`, `CHANGES.md`)
- **Files created:** 1 (`tests/test_counterfactual.py`)
- **Tests added:** 6 passing (2 GOV-04 guards + 4 parametrised pin cases)

## Accomplishments

- `METHODOLOGY_VERSION: str = "1.0.0"` is importable from `uk_subsidy_tracker.counterfactual` with a docstring spelling out the SemVer bump policy (PATCH / MINOR / MAJOR).
- `compute_counterfactual()` now writes a `methodology_version` column on its returned DataFrame — the mechanical handshake that lets Phase-4 Parquet writes propagate the version into `site/data/manifest.json` via GOV-02.
- `tests/test_counterfactual.py` pins the formula at 4 decimal places against four curated inputs (2019-01-01 @ 1.5 p/kWh → 39.6327; 2019-06-01 @ 1.2 → 34.1782; 2022-10-01 @ 8.0 → 168.1855; 2019-01-01 @ 0.0 → 12.3600). Any change to `CCGT_EFFICIENCY`, `GAS_CO2_INTENSITY_THERMAL`, `DEFAULT_NON_FUEL_OPEX`, or `DEFAULT_CARBON_PRICES` breaks four tests with a failure message that explicitly instructs the PR author to bump `METHODOLOGY_VERSION` and add a CHANGES.md entry.
- Regression-verified: temporarily toggling `CCGT_EFFICIENCY` from 0.55 to 0.56 produced four red parametrised failures; revert restored green.
- `CHANGES.md` `## Methodology versions` now has its first versioned entry (`### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)`) listing the pinned constants, BEIS Electricity Generation Costs 2023 + GOV.UK UK ETS as sources, and pointing at the pin-test file.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add METHODOLOGY_VERSION + DataFrame column propagation** — `9e991e8` (feat)
2. **Task 2: Create tests/test_counterfactual.py with pin + GOV-04 checks** — `d15bd28` (test)
3. **Task 3: Seed CHANGES.md `## Methodology versions` with 1.0.0 entry** — `3f434ad` (docs)

_Note: TDD was declared `tdd="true"` at task granularity on Tasks 1 and 2, but the plan structure places the RED test in Task 2 after the GREEN implementation in Task 1. Task 1's verification ran the importable-constant + column-present check directly via `uv run python -c ...`; Task 2 then layered the full parametrised pin suite on top. The gate sequence is therefore `feat → test → docs` rather than the canonical `test → feat`. This is a plan-authoring choice (the test freezes a constant that must exist first), not a TDD-compliance issue — the pin test WAS regression-verified to fail when the pinned constant changes, which is the actual guarantee the RED phase is meant to provide._

## Files Created/Modified

- `src/uk_subsidy_tracker/counterfactual.py` — added `METHODOLOGY_VERSION` module-level constant (line 15) with SemVer-policy docstring; added `df["methodology_version"] = METHODOLOGY_VERSION` assignment (line 92) inside `compute_counterfactual()` immediately before `return df`. No other lines changed; diff is two pure-insertion hunks totalling +11 lines.
- `tests/test_counterfactual.py` — new file, 66 lines. Two GOV-04 guard tests (`test_methodology_version_present`, `test_methodology_version_in_output`) + one parametrised pin test with four cases (`test_counterfactual_pin`). Imports from `uk_subsidy_tracker.counterfactual`; follows `tests/data/test_lccc.py` idioms (flat functions, module-level docstring, no classes).
- `CHANGES.md` — appended `### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)` sub-section beneath the existing GOV-04 HTML hook comment. `[Unreleased]` and `## [0.1.0] — 2026-04-21` blocks untouched (those land in plans 02-02 / 02-03 / 02-05).

## Decisions Made

- **4-decimal-place tolerance chosen for the pin** — strict enough to catch meaningful constant drift (0.01 change in `CCGT_EFFICIENCY` produces a visible divergence) without being so strict that legitimate floating-point rounding triggers false failures. Verified against the RESEARCH.md pre-computed table.
- **Zero-gas regression case included** — guards the NaN / divide-by-zero path and pins the carbon + O&M floor (£12.36/MWh for 2019). Gives an adversarial reader a clear sanity check independent of gas-price assumptions.
- **Monthly resample drops the column intentionally** — `compute_counterfactual_monthly()` uses `.resample("ME").mean(numeric_only=True)` which strips string columns. Left alone; daily is the Parquet-canonical input per CONTEXT specifics.
- **No `tests/conftest.py` created** — the plan only needs `pd.DataFrame` fixtures constructed in-test. A shared conftest would premature-abstract given subsequent plans in this phase may introduce their own fixture patterns (e.g., 02-02's YAML loader).

## Deviations from Plan

None — plan executed exactly as written. All three tasks completed on the first pass; all acceptance-criteria grep checks passed; full test suite (`uv run pytest tests/`) is green (9 passed, 2 skipped by design).

**One operational hiccup resolved silently during verification:** during the regression-check step (temporarily bumping `CCGT_EFFICIENCY` to 0.56, then reverting), a stale `src/uk_subsidy_tracker/__pycache__/counterfactual.cpython-313.pyc` bytecode cache masked the restored source. `find src -name '*.pyc' -path '*counterfactual*' -delete` cleared it. No committed artefact was affected — this was purely an interactive-verification artefact. Recording here so future regression-check scripts know to bust the pyc cache after `git checkout` on a source file.

## Issues Encountered

- **Stale `.pyc` bytecode cache during regression check** — resolved inline with `find … -delete`. Not a code issue; a local-dev cache coherence artefact. See Deviations above.

## User Setup Required

None — no external service configuration required.

## Threat Flags

None — plan does not introduce new trust boundaries. The T-02-04 mitigation (silent-drift-proof pin test + failure-message remediation hook) landed as specified. T-02-01/02/03/05 are N/A for this plan (no CI/workflows/benchmarks.yaml/branch-protection changes).

## Known Stubs

None — every line of new code is wired end-to-end:

- `METHODOLOGY_VERSION` is imported by real tests
- `methodology_version` DataFrame column is produced by live `compute_counterfactual()` calls
- `CHANGES.md` 1.0.0 entry cites real constants + real sources with real URLs in Phase-1 context

## Next Phase Readiness

**Plan 02-02 (test_schemas.py) unblocked.** Required handshake with this plan:

- Pandera schema file will sit next to the counterfactual pin test — same `tests/` directory — and reuse the `import pandera.pandas as pa` idiom (Pattern A in 02-PATTERNS.md).
- No shared fixtures between 02-01 and 02-02 yet; if 02-03 (`test_aggregates.py`) introduces a module-scoped LCCC fixture that 02-04 (`test_benchmarks.py`) also needs, the planner will hoist it to `tests/conftest.py` at that point.

**Plan 02-05 (CI workflow `.github/workflows/ci.yml`) unblocked for pytest-on-push.** The full test suite (9 passing, 2 skipped) runs in <1 s locally; expected CI wall-clock remains the `uv sync --frozen` step (~60 s), not the tests.

**Downstream (Phase 4) handshake confirmed:** `methodology_version` is live as a DataFrame column today. When Phase 4's `publish/manifest.py` writes Parquet derivations, the column will flow automatically into `manifest.json` — no additional wiring required in the counterfactual module. This is the exact GOV-04 ↔ GOV-02 link the ARCHITECTURE.md §9.4 contract specifies.

---
*Phase: 02-test-benchmark-scaffolding*
*Completed: 2026-04-22*

## Self-Check: PASSED

- All 4 declared files exist on disk (`counterfactual.py`, `test_counterfactual.py`, `CHANGES.md`, `02-01-SUMMARY.md`).
- All 3 task commits present in `git log` (`9e991e8`, `d15bd28`, `3f434ad`).
- `uv run pytest tests/` → 9 passed, 2 skipped by design (0.68 s).
- All acceptance-criteria grep checks returned `PASS`.
- Regression check: toggling `CCGT_EFFICIENCY` → 4 pin tests fail; revert → green. Confirmed.
