---
phase: 05-ro-module
fixed_at: 2026-04-23T00:00:00Z
review_path: .planning/phases/05-ro-module/05-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 5: Code Review Fix Report

**Fixed at:** 2026-04-23T00:00:00Z
**Source review:** .planning/phases/05-ro-module/05-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope (critical + warning): 3
- Fixed: 3
- Skipped: 0
- Test baseline preserved: 163 passed + 12 skipped + 22 xfailed (unchanged)
- `uv run mkdocs build --strict`: green

## Fixed Issues

### WR-01: REF-drift check in `validate()` reads a non-existent path

**Files modified:** `src/uk_subsidy_tracker/schemes/ro/__init__.py`
**Commit:** 5f479c6
**Applied fix:**
- Changed `ref_path` from the non-existent `src/uk_subsidy_tracker/data/benchmarks.yaml`
  to the real fixture location `tests/fixtures/benchmarks.yaml`. The Check 2 REF-drift
  warner is now live rather than dead code.
- Tightened the bare `except Exception:` to `except (FileNotFoundError, KeyError, yaml.YAMLError):`
  so only the three expected best-effort failure modes are swallowed (fresh-clone
  fixture absence, missing `ref_constable` / `annual_gbp` block, malformed YAML).
  Any other exception now propagates — real bugs (schema drift, attribute errors,
  OSError) will no longer be silently masked.
- Added an explanatory comment block documenting why each expected exception is
  tolerated and which exceptions deliberately propagate.

### WR-02: `mutualisation_gbp` dtype drifts between empty and non-empty rebuilds

**Files modified:** `src/uk_subsidy_tracker/schemes/ro/aggregation.py`
**Commit:** 4b02013
**Applied fix:**
- In the non-empty branch of `build_annual_summary`, cast the post-groupby
  `mutualisation_gbp` column to the nullable extension dtype `Float64`
  immediately after `.reset_index()`, matching the empty-frame branch.
- Changed the subsequent null-setting assignment from `= None` to `= pd.NA`
  to match the `Float64` dtype semantics (the previous `None` worked only
  because the column was `float64`; on `Float64` the idiomatic sentinel is
  `pd.NA`).
- The Parquet column logical type for `mutualisation_gbp` is now stable
  across empty-input (stub / Wave-2 smoke) and non-empty (real-data) rebuilds,
  eliminating the silent dtype-drift hazard when real Ofgem data lands.
- Added a WR-02 reference comment so future readers understand the cast's purpose.

### WR-03: Blanket `except Exception:` in `_annual_counterfactual_gbp_per_mwh`

**Files modified:** `src/uk_subsidy_tracker/schemes/ro/cost_model.py`
**Commit:** a5d3881
**Applied fix:**
- Narrowed `except Exception:` to `except FileNotFoundError:` in
  `_annual_counterfactual_gbp_per_mwh()`. The one expected failure mode
  (ONS gas SAP XLSX absent during Wave-2 bootstrap) is still tolerated and
  returns an empty lookup; all other exceptions (pandera schema drift,
  missing columns, arithmetic errors) now propagate as real bugs rather
  than silently producing zero `gas_counterfactual_gbp` rows that would
  inflate the subsidy-premium headline.
- Expanded the inline comment to explain why only `FileNotFoundError` is
  caught, pointing future maintainers at the validate() Check 2 backstop
  (now also correctly live per WR-01).

## Verification

For each fix:
1. Tier 1: Re-read the modified file section and confirmed the fix text is present
   and surrounding code is intact.
2. Tier 2: `python -c "import ast; ast.parse(...)"` passed on each modified file.
3. Regression guard: `uv run pytest tests/ -q --tb=line` run after each fix; baseline
   of 163 passed + 12 skipped + 22 xfailed held throughout.
4. Final confirmation: `uv run mkdocs build --strict` green after all fixes applied.

Note: All three fixes are defensive / error-handling narrow-downs on Option-D
stub-only code paths. The WR-02 dtype pin is the only one whose behaviour
actually changes under the current test fixtures (empty-frame rebuilds), and
it changes nothing observable because both the source (NumPy float64 on
empty groupby output) and target (pandas Float64) roundtrip identically
through Parquet when zero rows are present. The real value of all three fixes
lands when real Ofgem data arrives in Wave-2; until then, tests confirm no
regression.

---

_Fixed: 2026-04-23T00:00:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
