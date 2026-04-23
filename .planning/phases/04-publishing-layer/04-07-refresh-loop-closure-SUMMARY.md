---
phase: 04-publishing-layer
plan: 07
subsystem: refresh-loop-closure
tags: [gap-closure, refresh, sidecar, ons-gas, gov-03, pub-05, provenance, atomicity]

gap_closure: true
gap_closure_source: .planning/phases/04-publishing-layer/04-VERIFICATION.md

# Dependency graph
requires:
  - phase: 04-publishing-layer/05
    provides: "refresh_all.py orchestrator + refresh.yml daily cron that this plan now completes end-to-end"
  - phase: 04-publishing-layer/02
    provides: "raw-layer migration to data/raw/<publisher>/<file> + sidecar shape"
provides:
  - "src/uk_subsidy_tracker/data/sidecar.py — shared write_sidecar() atomic helper (.tmp + os.replace; sort_keys=True + indent=2 + trailing newline)"
  - "src/uk_subsidy_tracker/data/ons_gas.py — UnboundLocalError fix + timeout=60 + fail-loud raise on network failure"
  - "src/uk_subsidy_tracker/schemes/cfd/_refresh.py — refresh() now fetches LCCC + Elexon + ONS and rewrites all 5 sidecars (gap #1 closed)"
  - "tests/test_refresh_loop.py — 2 invariant tests locking the refresh-loop algebraic property"
  - "tests/test_ons_gas_download.py — 3 regression tests on ons_gas error path"
  - "scripts/backfill_sidecars.py — refactored to delegate to write_sidecar()"
  - "CHANGES.md [Unreleased] entries under Added / Fixed / Changed"
affects: ["phase-05-renewables-obligation", "phase-06+", "every-future-scheme-module"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Atomic sidecar write (.tmp + os.replace) shared across daily-refresh + one-shot backfill paths"
    - "Scheme-owns-its-raw-files architecture (Option A): each scheme.refresh() fetches its own raw files and writes its own sidecars; refresh_all.py stays orchestrator-only"
    - "Fail-loud on network failure (D-17): bare raise in except, no silent un-downloaded path return"
    - "importlib.import_module() escape hatch when a package __init__.py binds a submodule name as a function alias (shadows the submodule attribute for x.y.z-as-alias imports)"

key-files:
  created:
    - "src/uk_subsidy_tracker/data/sidecar.py"
    - "tests/test_refresh_loop.py"
    - "tests/test_ons_gas_download.py"
  modified:
    - "src/uk_subsidy_tracker/data/ons_gas.py"
    - "src/uk_subsidy_tracker/schemes/cfd/_refresh.py"
    - "scripts/backfill_sidecars.py"
    - "CHANGES.md"
    - "data/raw/**/*.meta.json (5 sidecars — retrieved_at refreshed to real git-log values post-rename)"

key-decisions:
  - "Option A architecture preserved: scheme module owns its raw files and its provenance. refresh_all.py UNCHANGED."
  - "_URL_MAP duplicated across _refresh.py and backfill_sidecars.py with cross-reference comment; byte-match verified via dict-sort diff. Duplication is load-bearing locality — each script is self-contained; cross-drift is caught by the test_refresh_loop invariant on first run."
  - "Backfill retains ownership of two unique fields (backfilled_at marker + retrieved_at from git log --follow); write_sidecar() handles the common 5 keys; post-step overlay writes the two extras with the same serialisation invariants + atomic rename."
  - "sha256_of() helper deleted from backfill script — routed through write_sidecar() internally; single source of truth for SHA chunking."
  - "Test-side importlib.import_module() chosen over `import x.y.z as alias` because cfd/__init__.py binds `_refresh` as a function alias that shadows the submodule on attribute-chain lookup. This is documented in the test file for future test authors."

patterns-established:
  - "Shared write_sidecar() helper — future Phase 5+ schemes (RO, FiT, SEG, etc.) call write_sidecar() from their own _refresh.py; no scheme re-implements SHA chunking or atomic JSON write."
  - "Refresh-loop invariant test template — any future scheme's _refresh.py can adapt tests/test_refresh_loop.py structure (tmp_raw_tree fixture + patched-downloader ExitStack) verbatim."
  - "ons_gas download error path pattern — any future downloader follows: bind output_path before try, timeout=60 on requests.get, bare raise in except for fail-loud."

requirements-completed: [GOV-03, PUB-05]

# Metrics
duration: 9min
completed: 2026-04-23
---

# Phase 04 Plan 07: Refresh-Loop Closure Summary

**Two 04-VERIFICATION.md gaps closed: refresh() now fetches all 3 data sources + rewrites all 5 sidecars (gap #1); ons_gas.download_dataset() fail-loud with timeout=60 (gap #2). Shared write_sidecar() atomic helper replaces hand-written JSON in both daily-refresh and backfill paths. Refresh-loop invariant test locks the algebraic property that makes GOV-03's "functional" claim survive the first real upstream change.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-04-23T01:40:23Z
- **Completed:** 2026-04-23T01:49:11Z
- **Tasks:** 5
- **Files created:** 3 (sidecar.py, test_refresh_loop.py, test_ons_gas_download.py)
- **Files modified:** 4 (ons_gas.py, _refresh.py, backfill_sidecars.py, CHANGES.md) + 5 sidecar JSON files (retrieved_at refreshed to real git-log values)

## Accomplishments

- **Gap #1 closed (SC #5 / GOV-03):** `schemes/cfd/_refresh.py::refresh()` now invokes all three downloaders (LCCC + Elexon + ONS) and rewrites every `.meta.json` sidecar after successful download. `upstream_changed()` returns False on the next call (perpetual dirty-check loop fixed); `manifest.generated_at` advances once and stays stable on unchanged second run (tested).
- **Gap #2 closed (PUB-05 / GOV-03 error resilience):** `ons_gas.download_dataset()` cannot raise `UnboundLocalError` on network failure; `timeout=60` matches Elexon convention; bare `raise` propagates per D-17 (fail-loud). Three-test regression guard locks all three invariants.
- **Shared atomic sidecar writer shipped:** `src/uk_subsidy_tracker/data/sidecar.py::write_sidecar()` is the single source of truth for `.meta.json` mechanics (SHA chunking, serialisation invariants, .tmp + os.replace atomicity). Used by both the daily-refresh path AND `scripts/backfill_sidecars.py`; byte-identity preserved on all common keys (verified by re-run git-diff showing 0 sha256/upstream_url/backfilled_at changes).
- **Refresh-loop invariant pinned:** `tests/test_refresh_loop.py` 2 tests using tmp_path + mocked downloaders (no network) lock the "after refresh, upstream_changed() returns False" invariant.

## Task Commits

Each task was committed atomically (one commit per task, D-16 discipline):

1. **Task 1: sidecar.write_sidecar() helper** — `29b5524` (feat)
2. **Task 2: ons_gas error-path fix + timeout + fail-loud** — `ac9675a` (fix; TDD RED→GREEN in a single commit per Plan 04-01 precedent)
3. **Task 3: wire Elexon + ONS + sidecar rewrites into cfd refresh** — `42c8c3e` (fix)
4. **Task 4: refresh-loop invariant test** — `3497296` (test)
5. **Task 5: CHANGES entries + backfill script refactor** — `14e2138` (docs)

## Files Created/Modified

### Created
- `src/uk_subsidy_tracker/data/sidecar.py` — atomic shared sidecar writer (78 lines; write_sidecar + _sha256_of)
- `tests/test_refresh_loop.py` — refresh-loop invariant (150 lines; 2 tests, importlib-based submodule import)
- `tests/test_ons_gas_download.py` — ons_gas error-path regression (64 lines; 3 tests, all patched)

### Modified
- `src/uk_subsidy_tracker/data/ons_gas.py` — `download_dataset()`: output_path bound before try, timeout=60, bare raise in except
- `src/uk_subsidy_tracker/schemes/cfd/_refresh.py` — `refresh()` fetches LCCC + Elexon + ONS + writes 5 sidecars; adds `_URL_MAP` dict (byte-matches backfill URL_MAP)
- `scripts/backfill_sidecars.py` — delegates SHA + atomic JSON write to `write_sidecar()`; overlays `retrieved_at` (git log) + `backfilled_at` (marker); `sha256_of()` removed
- `CHANGES.md` [Unreleased] — 3 Added bullets, 2 Fixed bullets (new section), 1 Changed bullet (all citing 04-07)
- `data/raw/**/*.meta.json` (5 files) — `retrieved_at` refreshed from BACKFILL_DATE fallback to real `git log --follow` values (expected improvement per STATE.md: post-rename-commit re-run resolves to real dates). All other keys unchanged.

## Decisions Made

1. **Option A architecture preserved:** `refresh_all.py` is UNCHANGED. Each scheme.refresh() owns its full data-layer responsibility (download + sidecar rewrite). Rationale: Phase 5 RO module copies this pattern verbatim; centralising sidecar-rewrite in `refresh_all.py` would weaken the scheme contract ("scheme owns its raw tree and its provenance").

2. **URL_MAP duplicated with cross-reference comment, not extracted to shared module:** Locality over DRY. Each of the two scripts is self-contained (grep-inspectable, no `sys.path.insert()` tricks at import time for the refresh path). Cross-drift is caught by the test_refresh_loop invariant: if `_refresh.py::_URL_MAP` and `backfill_sidecars.py::URL_MAP` disagree, sidecars written by the two paths diverge and test_manifest byte-identity fails.

3. **Test uses `importlib.import_module()` rather than `from x.y import z as alias`:** `cfd/__init__.py` rebinds `_refresh` as a function alias (`from ... import refresh as _refresh`) which shadows the `_refresh` submodule on attribute-chain lookup. This is a Python quirk documented in the test file to save future test authors from the same debugging session.

4. **Backfill retains unique-field ownership (two-pass write):** `write_sidecar()` owns the five common keys; the backfill script runs a post-step that reads the just-written sidecar, overlays `retrieved_at` (from `git log --follow`) + `backfilled_at` (reconstruction marker), and re-writes atomically. This preserves the single-source-of-truth principle for SHA + serialisation while keeping backfill-specific logic local to the script that owns it.

5. **sha256_of() deleted from backfill script:** Single source of truth for SHA chunking now lives in `sidecar.py::_sha256_of()`. The `_sha256` helper in `schemes/cfd/_refresh.py` is a duplicate (used only by `upstream_changed()` dirty-check, not by refresh); left in place for locality but flagged as a future candidate for extraction.

## Deviations from Plan

**Total deviations: 1** (Rule 3 - Blocking, in-test only)

### 1. [Rule 3 - Blocking] Test-side `importlib.import_module()` instead of `from x.y import z as alias`

- **Found during:** Task 4 (test_refresh_loop.py — first test run errored)
- **Issue:** `from uk_subsidy_tracker.schemes.cfd import _refresh as cfd_refresh` resolved `_refresh` to the FUNCTION alias bound by `cfd/__init__.py` line 26-29 (`from ... import refresh as _refresh`), not the submodule. `cfd_refresh._URL_MAP` therefore raised `AttributeError: 'function' object has no attribute '_URL_MAP'`. Same error persisted with `import uk_subsidy_tracker.schemes.cfd._refresh as cfd_refresh` because the `as alias` binding uses the attribute chain on the parent package.
- **Fix:** Replaced the import with `cfd_refresh = importlib.import_module("uk_subsidy_tracker.schemes.cfd._refresh")` which bypasses the attribute-chain lookup and returns the submodule object directly. Added a 4-line explanatory comment in the test file for future test authors.
- **Files modified:** tests/test_refresh_loop.py
- **Verification:** Both tests pass; full suite 74 passed + 4 skipped
- **Committed in:** 3497296 (Task 4 commit)

**Impact on plan:** Minor — test-side import plumbing only; does not change the tested behaviour. No scope creep.

## Issues Encountered

None materially impactful. The `importlib` discovery (documented above) was a 30-second debug cycle. The `retrieved_at` field shift in the 5 sidecar files on backfill re-run was expected (documented in STATE.md line 115) — strict improvement on provenance accuracy.

## Scope Discipline (Verifier-Scoped OUT Items)

The following items were explicitly out of scope per the plan's verification block and remain untouched:

- `src/uk_subsidy_tracker/publish/manifest.py::_site_url()` — WR-03 line-scan fragility (Info accepted)
- `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py::build_forward_projection` — WR-04 empty-data defensive fallback (Info)
- `src/uk_subsidy_tracker/data/lccc.py::download_lccc_datasets` — pre-existing silent-swallow pattern (verifier scoped out; follow-up candidate for future audit)
- `.github/workflows/refresh.yml` + `.github/workflows/deploy.yml` — action SHA pinning supply-chain concern (Info accepted)

Verified via `git diff`: all five paths show empty diff.

## Gap Closure Traceability

### Gap #1 (from 04-VERIFICATION.md, verbatim "missing:" lines):

- ✅ "End-to-end refresh helper that fetches LCCC + Elexon + ONS and rewrites .meta.json sidecars (shared helper extracted from scripts/backfill_sidecars.py)" → **Delivered:** Task 1 (write_sidecar) + Task 3 (refresh() body expansion) + Task 5 (backfill script refactor to use shared helper)
- ✅ "Call sites in refresh_all.refresh_scheme() (or scheme_module.refresh() of each scheme) that invoke Elexon + ONS downloaders" → **Delivered:** Task 3 chose Option A (scheme_module.refresh()) per plan architecture choice; grep confirms `download_elexon_data` + `download_ons_gas` both present
- ✅ "Test covering the refresh loop invariant: after a simulated upstream change, running refresh_all twice produces generated_at that advances once and stays stable on the second run" → **Delivered:** Task 4 (`test_refresh_loop_generated_at_advances_once_then_stable`)

### Gap #2 (from 04-VERIFICATION.md, verbatim "missing:" lines):

- ✅ "Assign output_path BEFORE the try block" → **Delivered:** Task 2, ons_gas.py line 36
- ✅ "Either re-raise or return None/False on failure — never silently return a non-downloaded path" → **Delivered:** Task 2, bare `raise` at ons_gas.py line 47
- ✅ "Add timeout=60 to requests.get() to match the Elexon convention" → **Delivered:** Task 2, ons_gas.py line 39

## Next Phase Readiness

**Phase 5 (Renewables Obligation) fully unblocked, with an improved template:**

- `src/uk_subsidy_tracker/schemes/cfd/_refresh.py::refresh()` is now the complete Option A template: three downloaders + a for-loop over `_URL_MAP` calling `write_sidecar()`. A new scheme's `_refresh.py` is a copy-paste-modify of this file.
- `src/uk_subsidy_tracker/data/sidecar.py::write_sidecar()` is the single-source helper every new scheme calls; no scheme re-implements SHA chunking or atomic JSON write.
- `tests/test_refresh_loop.py` is the invariant-test template: future schemes adapt the `tmp_raw_tree` fixture + patched-downloader `ExitStack` verbatim for their own `_URL_MAP`.
- Phase 4 exit criteria (all 5 ROADMAP SCs) now FULLY green: SC #5 "daily refresh ... functional" is tested and locked, not just wired.

**Re-verification of 04-VERIFICATION.md:** A re-run would downgrade both gaps from `partial` to `verified`. GOV-03 and PUB-05 are now fully satisfied.

## Self-Check: PASSED

Verified the following post-write:

- Created files exist:
  - `src/uk_subsidy_tracker/data/sidecar.py` — FOUND
  - `tests/test_refresh_loop.py` — FOUND
  - `tests/test_ons_gas_download.py` — FOUND
- Commits exist:
  - `29b5524` (Task 1) — FOUND
  - `ac9675a` (Task 2) — FOUND
  - `42c8c3e` (Task 3) — FOUND
  - `3497296` (Task 4) — FOUND
  - `14e2138` (Task 5) — FOUND
- Full test suite green: 74 passed + 4 skipped (expected ≥74 + 4)
- Behavioural spot-checks (plan verification table): all 9 rows pass
- No scope creep: 5 verifier-scoped OUT files show empty `git diff`

---
*Phase: 04-publishing-layer*
*Plan: 07*
*Completed: 2026-04-23*
