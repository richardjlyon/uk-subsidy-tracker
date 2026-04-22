---
phase: 01-foundation-tidy
plan: 01
subsystem: packaging
tags: [rename, packaging, imports, brownfield, python-floor]
requires: []
provides:
  - "src/uk_subsidy_tracker/ package (renamed via git mv, history preserved)"
  - "pyproject.toml with name = uk-subsidy-tracker and requires-python >= 3.12"
  - "Regenerated uv.lock against the bumped Python floor"
  - "CLAUDE.md Runtime section aligned with Constraints on Python 3.12+"
affects:
  - "All Phase 2+ work that imports the package (now uses uk_subsidy_tracker)"
  - "mkdocs.yml header comment still references cfd_payment.plotting (swept in Plan 02)"
  - "docs/index.md and docs/charts/index.md clone/run code blocks (Plan 02)"
tech-stack:
  added: []
  patterns:
    - "git mv preserves 100% rename similarity for 34 tracked files"
    - "Absolute imports from package root (uk_subsidy_tracker.*) across 27 edited files"
    - "Relative imports within adjacent submodules (from .lccc etc.) preserved unchanged"
key-files:
  created: []
  modified:
    - "pyproject.toml"
    - "uv.lock"
    - "CLAUDE.md"
    - "src/uk_subsidy_tracker/counterfactual.py"
    - "src/uk_subsidy_tracker/data/elexon.py"
    - "src/uk_subsidy_tracker/data/lccc.py"
    - "src/uk_subsidy_tracker/data/ons_gas.py"
    - "src/uk_subsidy_tracker/plotting/__main__.py"
    - "src/uk_subsidy_tracker/plotting/chart_builder.py"
    - "src/uk_subsidy_tracker/plotting/utils.py"
    - "src/uk_subsidy_tracker/plotting/cannibalisation/capture_ratio.py"
    - "src/uk_subsidy_tracker/plotting/cannibalisation/price_vs_wind.py"
    - "src/uk_subsidy_tracker/plotting/capacity_factor/__init__.py"
    - "src/uk_subsidy_tracker/plotting/capacity_factor/monthly.py"
    - "src/uk_subsidy_tracker/plotting/capacity_factor/seasonal.py"
    - "src/uk_subsidy_tracker/plotting/intermittency/generation_heatmap.py"
    - "src/uk_subsidy_tracker/plotting/intermittency/load_duration.py"
    - "src/uk_subsidy_tracker/plotting/intermittency/rolling_minimum.py"
    - "src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck.py"
    - "src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck_old.py"
    - "src/uk_subsidy_tracker/plotting/subsidy/cfd_dynamics.py"
    - "src/uk_subsidy_tracker/plotting/subsidy/cfd_payments_by_category.py"
    - "src/uk_subsidy_tracker/plotting/subsidy/cfd_vs_gas_cost.py"
    - "src/uk_subsidy_tracker/plotting/subsidy/lorenz.py"
    - "src/uk_subsidy_tracker/plotting/subsidy/remaining_obligations.py"
    - "src/uk_subsidy_tracker/plotting/subsidy/scissors.py"
    - "src/uk_subsidy_tracker/plotting/subsidy/subsidy_per_avoided_co2_tonne.py"
    - "tests/data/test_lccc.py"
    - "tests/data/test_ons.py"
    - "demo_dark_theme.py"
  renamed:
    - "src/cfd_payment/ -> src/uk_subsidy_tracker/ (34 files, R100 similarity)"
decisions:
  - "Hard-cut package rename with no backward-compatibility alias (D-13)"
  - "git mv over copy-then-delete to preserve file history (D-14, verified R100 in commit 7b5538b)"
  - "Both tasks (rename + import rewrite) landed before Plan 01 closes so `import uk_subsidy_tracker` succeeds at plan exit (D-15)"
  - "Python floor bumped 3.11 -> 3.12 in pyproject.toml requires-python AND CLAUDE.md Runtime section (B-3 resolved)"
  - "Description updated to portal scope: 'Independent, open, data-driven audit of UK renewable electricity subsidy costs'"
  - "CLAUDE.md lines 30, 79, 126, 180, 208 ('Python 3.11+' prose) left untouched — non-authoritative descriptive bullets, deferred to Phase 3 housekeeping"
  - "Function names, class names, chart output filename prefixes (subsidy_cfd_*), and CfD-scheme narrative strings left unchanged per CONTEXT.md Claude's Discretion"
requirements:
  completed: [FND-01]
metrics:
  duration_seconds: 236
  tasks_completed: 2
  files_touched_total: 64
  files_renamed: 34
  files_modified: 30
  completed_at: "2026-04-22T02:00:39Z"
---

# Phase 1 Plan 1: Hard-Cut Package Rename and Python Floor Bump

Renamed the Python package from `cfd_payment` to `uk_subsidy_tracker` in a single atomic wave (two commits), bumped the Python floor from 3.11 to 3.12 to match the CLAUDE.md Constraints declaration, and rewrote all 24 `from cfd_payment` import statements across sources, tests, and the repo-root demo script so `uv run python -c 'import uk_subsidy_tracker'` succeeds at plan exit.

## What Shipped

### Commit 1 — `7b5538b` (Task 1)

**`refactor(01-01): rename package cfd_payment -> uk_subsidy_tracker; bump Python floor to 3.12`**

- `git mv src/cfd_payment src/uk_subsidy_tracker` — 34 tracked files, every entry shows as `R100` (100% similarity rename) in git log. History preserved for all files including the baseline-committed pre-phase drafts (`cfd_dynamics.py`, modified `__main__.py`, modified `cfd_vs_gas_cost.py`).
- `pyproject.toml`:
  - `name = "cfd-payment"` → `name = "uk-subsidy-tracker"`
  - `description` updated to portal scope
  - `requires-python = ">=3.11"` → `requires-python = ">=3.12"`
  - `packages = ["src/cfd_payment"]` → `packages = ["src/uk_subsidy_tracker"]`
  - `kaleido>=1.2.0` dependency (pre-existing from baseline) preserved.
- `uv.lock` regenerated (`uv lock` → 58 packages resolved; `Removed cfd-payment v0.1.0 / Added uk-subsidy-tracker v0.1.0`).
- `uv sync` → built `uk-subsidy-tracker@0.1.0`, replaced installed `cfd-payment`.
- `CLAUDE.md` line 35: `Python 3.11 or later (declared in \`pyproject.toml\`: \`requires-python = ">=3.11"\`)` → `Python 3.12 or later (declared in \`pyproject.toml\`: \`requires-python = ">=3.12"\`)`. No other `Python 3.11+` mentions touched (deferred to Phase 3 housekeeping, out of scope for this plan per PLAN.md).

### Commit 2 — `596594c` (Task 2)

**`refactor(01-01): rewrite all cfd_payment imports to uk_subsidy_tracker`**

- 27 files modified — every `from cfd_payment` rewritten to `from uk_subsidy_tracker`, preserving the rest of each import line verbatim.
- Relative imports within adjacent submodules (e.g., `from .lccc import ...`, `from .chart_builder import ChartBuilder`) left unchanged, confirming per-CLAUDE.md import convention.
- Coverage:
  - `src/uk_subsidy_tracker/` — 24 Python files (including the 3 baseline-committed pre-phase drafts that had to carry through the rename: `cfd_dynamics.py`, modified `__main__.py`, modified `cfd_vs_gas_cost.py`).
  - `tests/data/test_lccc.py`, `tests/data/test_ons.py`.
  - `demo_dark_theme.py` at repo root (3 imports: `ChartBuilder`, `GENERATION_COLORS`, `register_cfd_dark_theme`).
- Function/class names, constants, docstring prose describing the CfD scheme, and the chart-output filename prefix `subsidy_cfd_payments_by_category` all left unchanged per CONTEXT.md Claude's Discretion ("leave narrative text describing the 'CfD' scheme untouched").

## Python-Floor Bump Verification (B-3 resolution)

| Artefact | Before | After |
|----------|--------|-------|
| `pyproject.toml` L5 | `requires-python = ">=3.11"` | `requires-python = ">=3.12"` |
| `CLAUDE.md` L35 | `Python 3.11 or later (declared in \`pyproject.toml\`: \`requires-python = ">=3.11"\`)` | `Python 3.12 or later (declared in \`pyproject.toml\`: \`requires-python = ">=3.12"\`)` |
| `CLAUDE.md` L14 Constraints | `Python 3.12+ only` (already correct) | `Python 3.12+ only` (unchanged — this was the anchor) |

**Lockfile regeneration:**
- `uv lock` — exit 0, `Resolved 58 packages in 1.01s`.
- `uv sync` — exit 0, built and installed `uk-subsidy-tracker@0.1.0`.

## Verification Gates

All seven plan-level acceptance gates pass:

```
1. test -d src/uk_subsidy_tracker && test ! -d src/cfd_payment       -> OK
2. grep -r "from cfd_payment" src/ tests/ demo_dark_theme.py          -> zero matches (exit 1)
3. uv run python -c 'import uk_subsidy_tracker'                       -> OK (ROADMAP success criterion 1)
4. uv run python -c 'from uk_subsidy_tracker.plotting import ChartBuilder' -> OK
5. grep -c 'name = "uk-subsidy-tracker"' pyproject.toml               -> 1
6. grep -c 'requires-python = ">=3.12"' pyproject.toml                -> 1
   grep -c 'requires-python = ">=3.12"' CLAUDE.md                     -> 1  (B-3 resolved)
7. uv sync                                                            -> OK
```

Import-level gates (additional smoke tests run during Task 2 verification):

```
from uk_subsidy_tracker import DATA_DIR, OUTPUT_DIR, PROJECT_ROOT           -> OK
from uk_subsidy_tracker.counterfactual import compute_counterfactual        -> OK
from uk_subsidy_tracker.plotting.chart_builder import ChartBuilder          -> OK
from uk_subsidy_tracker.data import load_gas_price                          -> OK
from uk_subsidy_tracker.plotting.subsidy.cfd_dynamics import main           -> OK   # baseline draft
from uk_subsidy_tracker.plotting.subsidy.remaining_obligations import main  -> OK
```

`git log --name-status` confirms 34 rename entries appear as `R100` (not parallel `D` + `A` pairs) — file history is preserved.

## Deviations from Plan

None — plan executed exactly as written across both tasks. No auto-fixed bugs, no missing functionality added, no architectural questions raised. Mechanical rename + single-line config bumps went through cleanly.

## Skipped / Out-of-Scope Items

The following references to `cfd_payment`/`cfd-payment` remain in the tree after Plan 01 closes — all are intentionally deferred per the phase wave structure:

- `mkdocs.yml` — header comment still shows `uv run python -m cfd_payment.plotting`; `site_name`, `site_url`, `repo_name`, `repo_url` still reference `cfd-payment`. **Plan 02 scope.**
- `docs/index.md` — clone/run code block (`git clone .../cfd-payment`, `cfd_payment.plotting`) and link text. **Plan 02 scope.**
- `docs/charts/index.md` — reproduce-command code fences and GitHub URL. **Plan 02 scope.**
- `docs/technical-details/gas-counterfactual.md` — source-code links reference `cfd_payment.counterfactual` + a pre-existing broken `richlyon` (vs `richardjlyon`) handle typo. **Plan 02 scope.**
- `CLAUDE.md` lines 30, 79, 126, 180, 208 — descriptive `Python 3.11+` / `cfd_payment` prose in non-authoritative sections. **Phase 3 housekeeping.**

## Hand-off Notes

**To Plan 02 (Wave 2 — docs + mkdocs rewrite):**
- `mkdocs.yml` header comment (`uv run python -m cfd_payment.plotting`) and site identity block (`site_name`, `site_url`, `repo_name`, `repo_url`) still reference the old name. Plan 02 sweeps these along with the theme swap.
- `docs/index.md` line 59 `technical-details/gas-counterfactual.md` link and clone-and-run code block at lines 65–73 need updating.
- `docs/charts/index.md` lines 52, 59, 65, 68 need URL and module-path updates.

**To Plan 03 (Wave 3 — root docs):**
- `README.md` creation is deferred to Plan 03 (it didn't exist before this phase).
- `CHANGES.md` `0.1.0 — 2026-04-21` seed entry MUST record the Python-floor bump from `>=3.11` to `>=3.12` under `### Changed`, as the B-3 resolution is a public/reproducibility-relevant change that hostile readers will want an audit trail for.
- `CITATION.cff` should list `version: "0.1.0"` matching the unchanged `pyproject.toml` version field.

## TDD Gate Compliance

Not applicable — this plan is `type: execute` with `tdd="false"` on both tasks. No test coverage was added; `tests/data/test_lccc.py` and `tests/data/test_ons.py` imports were mechanically rewritten so the existing (skipped-by-default) tests remain runnable under the new package name.

## Self-Check: PASSED

Verified against the objective and success_criteria in the executor prompt:

- **File exists: `.planning/phases/01-foundation-tidy/01-01-SUMMARY.md`** — FOUND (this file).
- **Commit `7b5538b` (Task 1)** — `git log --oneline | grep 7b5538b` → FOUND: `refactor(01-01): rename package cfd_payment -> uk_subsidy_tracker; bump Python floor to 3.12`.
- **Commit `596594c` (Task 2)** — `git log --oneline | grep 596594c` → FOUND: `refactor(01-01): rewrite all cfd_payment imports to uk_subsidy_tracker`.
- **Package dir `src/uk_subsidy_tracker/`** — FOUND.
- **Package dir `src/cfd_payment/`** — GONE (removed by git mv).
- **Zero residual `from cfd_payment` in src/ tests/ demo_dark_theme.py** — confirmed (grep exit 1).
- **`uv run python -c 'import uk_subsidy_tracker'` exits 0** — confirmed.
- **`uv run python -c 'from uk_subsidy_tracker.plotting.subsidy.cfd_dynamics import main'` exits 0** — confirmed (baseline draft carried through rename).
- **`pyproject.toml` declares `name = "uk-subsidy-tracker"`, `requires-python = ">=3.12"`, `packages = ["src/uk_subsidy_tracker"]`** — confirmed.
- **`CLAUDE.md` Runtime section declares `>=3.12`** — confirmed.
- **STATE.md and ROADMAP.md untouched by this agent** — confirmed (only `.planning/STATE.md` and `.planning/config.json` show as modified in `git status`, both carrying orchestrator-owned changes present before this plan started).
