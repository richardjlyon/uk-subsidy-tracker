---
phase: 04-publishing-layer
verified: 2026-04-23T02:00:00Z
status: passed
score: 5/5 success criteria verified
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 4/5
  previous_verified_at: 2026-04-22T21:00:00Z
  gap_closure_plan: 04-07-refresh-loop-closure
  gap_closure_commits:
    - "29b5524 — feat(04-07): add sidecar.write_sidecar() atomic helper"
    - "ac9675a — fix(04-07): ons_gas download error-path + timeout=60 (gap #2)"
    - "42c8c3e — fix(04-07): wire Elexon + ONS + sidecar rewrites into cfd refresh (gap #1)"
    - "3497296 — test(04-07): refresh-loop invariant test (gap #1)"
    - "14e2138 — docs(04-07): CHANGES entries + backfill script refactor to shared sidecar helper"
  gaps_closed:
    - "GitHub Actions daily refresh workflow is committed AND functional"
    - "External consumers can follow a URL from manifest.json and retrieve a Parquet file and its CSV mirror — including when the publisher is temporarily unavailable"
  gaps_remaining: []
  regressions: []
human_verification:
  - test: "Trigger .github/workflows/refresh.yml manually via workflow_dispatch after user completes the two dashboard-only prerequisites (enable 'Allow GitHub Actions to create and approve pull requests'; create labels `daily-refresh` + `refresh-failure`)"
    expected: "Workflow runs to completion; on unchanged state, refresh_all short-circuits ('upstream unchanged'); all test gates green; no PR opens; no refresh-failure issue opens."
    why_human: "Requires GitHub UI authentication (label creation + repo settings toggle) and a live GitHub Actions run — cannot be verified from a local checkout."

  - test: "Push a test tag matching the D-14 pattern (e.g. `v2026.04-rc1`) and confirm deploy.yml fires, uploads release assets, and that downloading the release asset URL resolves to the same Parquet byte-for-byte as the snapshot CLI produces locally."
    expected: "Release page at https://github.com/<user>/uk-subsidy-tracker/releases/tag/v2026.04-rc1 contains manifest.json + 5 parquet + 5 csv + 5 schema.json files. Downloading manifest.json and following any parquet_url resolves to the file whose SHA-256 matches the manifest entry."
    why_human: "Tag push is an intentional user action (never automated). Release-asset publication and HTTPS retrieval depend on GitHub's infrastructure; cannot be simulated locally."

  - test: "Visual inspection of docs/data/index.md rendered via `uv run mkdocs serve` — verify the pandas/DuckDB/R snippets are copy-pasteable and the cross-links to methodology/gas-counterfactual.md and about/corrections.md resolve."
    expected: "All three language snippets render as highlighted code blocks without markdown leaks; every internal link clicks through without 404."
    why_human: "Visual layout, code-block rendering fidelity, and link discoverability are quality concerns that grep cannot verify."
---

# Phase 4: Publishing Layer Verification Report

**Phase Goal:** External consumers can discover, fetch, and cite any dataset via a machine-readable manifest with full provenance, and the three-layer pipeline is operational end-to-end for CfD.

**Verified:** 2026-04-23T02:00:00Z
**Status:** passed (re-verified after gap closure)
**Re-verification:** Yes — after Plan 04-07 gap closure. Previous verification at 2026-04-22T21:00:00Z returned `gaps_found` with SC #5 partial (two structural/code gaps). Plan 04-07 delivered both closures in five atomic commits; this re-run confirms both gaps are structurally and behaviourally closed.

## Goal Achievement

### Observable Truths (from ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `site/data/manifest.json` is present after build and contains source URL, retrieval timestamp, SHA-256, pipeline git SHA, and `methodology_version` per dataset | VERIFIED | Prior run confirmed `snapshot.py --dry-run` emits manifest with 5 datasets; each carries `sources[]` with `upstream_url`/`retrieved_at`/`source_sha256`; top-level `pipeline_git_sha` is 40-char hex; `methodology_version: "0.1.0"` matches `counterfactual.METHODOLOGY_VERSION`. No regression this cycle. |
| 2 | External consumer can follow a URL from `manifest.json` and retrieve a Parquet file and its CSV mirror | **VERIFIED (upgraded from partial)** | Happy-path unchanged: 5 Parquet + 5 CSV + 5 schema.json; all URLs absolute https; CSV mirror 7/7 quality tests pass. **Gap #2 closed:** `ons_gas.download_dataset()` (lines 36/39/41/45-47) now binds `output_path` BEFORE the `try` block, passes `timeout=60`, and `except` block bare-`raise`s per D-17 (fail-loud). Regression test `tests/test_ons_gas_download.py` (3 tests) locks all three invariants — all pass. The reliability promise underpinning the fetch truth is now testable and tested. |
| 3 | `publish/snapshot.py` creates an immutable `site/data/v<date>/` directory on tagged release | VERIFIED | Prior `python -m uk_subsidy_tracker.publish.snapshot --version v2026.04-rc1 --output /tmp/snap --dry-run` exit 0 with 16 artefacts. No regression. |
| 4 | `docs/data/index.md` explains how journalists and academics use the datasets, including citation via versioned snapshot URL | VERIFIED | 144 lines, 9 H2s, six-section template + three-language snippets, absolute manifest URL, BibTeX template. `mkdocs build --strict` exit 0. No regression. |
| 5 | GitHub Actions daily refresh workflow (06:00 UTC cron) with per-scheme dirty-check is committed and functional | **VERIFIED (upgraded from FAILED-partial)** | `.github/workflows/refresh.yml` unchanged — still valid YAML, pinned actions, least-privilege permissions. **Gap #1 closed:** `schemes/cfd/_refresh.py::refresh()` (lines 83-111) now invokes all three downloaders (`download_lccc_datasets` + `download_elexon_data` + `download_ons_gas`) and calls `write_sidecar()` for every one of the five raw files after download. `_URL_MAP` dict byte-matches `scripts/backfill_sidecars.py::URL_MAP`. Invariant test `tests/test_refresh_loop.py::test_refresh_loop_generated_at_advances_once_then_stable` (and its companion `test_refresh_loop_converges_on_unchanged_upstream`) lock the algebraic property: after refresh rewrites sidecars with fresh bytes, `upstream_changed()` returns False on the next call (no perpetual dirty-check loop) and `max(sidecar.retrieved_at)` advances once then stays stable. Both tests pass. |

**Score:** 5/5 ROADMAP success criteria verified (was 4/5; SC #2 and SC #5 both flipped to VERIFIED).

### Required Artifacts

New artifacts delivered in this cycle (04-07) — three files created + four modified + five sidecars re-emitted:

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/uk_subsidy_tracker/data/sidecar.py` | Shared atomic `write_sidecar()` helper | VERIFIED | 78 lines (exists; substantive). Functions: `_sha256_of()` (64-KiB-chunked, matches `_refresh.py::_sha256` byte-for-byte) + `write_sidecar()` (writes `.meta.json.tmp` then `os.replace` — atomic on POSIX + Windows). `json.dumps(meta, sort_keys=True, indent=2) + "\n"` byte-parity with backfill script. Correctly raises `FileNotFoundError` when `raw_path` is missing (pre-condition). Imported by both `schemes/cfd/_refresh.py` (daily refresh path) and `scripts/backfill_sidecars.py` (backfill path). |
| `src/uk_subsidy_tracker/data/ons_gas.py` (modified) | Gap #2 fixed | VERIFIED | `output_path` bound on line 36 BEFORE `try:` on line 38 (was: line 35 inside try); `timeout=60` added on `requests.get` line 39; `except` block line 45-47 now bare-`raise`s instead of silently returning un-downloaded path. Docstring line 29-31 documents the D-17 fail-loud contract. |
| `src/uk_subsidy_tracker/schemes/cfd/_refresh.py` (modified) | Gap #1 fixed | VERIFIED | `refresh()` body (lines 83-111) now: (1) calls `download_lccc_datasets` + `download_elexon_data` + `download_ons_gas` in sequence, (2) iterates `_URL_MAP` and calls `write_sidecar(raw_path, upstream_url)` for each of the five files, (3) raises `FileNotFoundError` if any downloader returned but raw file is missing (fail-loud). Added `_URL_MAP` dict (lines 31-42) — cross-reference comment on line 28-30 notes it MUST match `backfill_sidecars.py::URL_MAP`. Byte-match verified by re-running backfill: `git diff data/raw/` shows zero bytes changed. |
| `scripts/backfill_sidecars.py` (modified) | Delegate to shared helper | VERIFIED | 108 lines; now imports `write_sidecar` from the new shared module (line 76) and calls it for the five common keys (line 84-89) with `http_status=None` + `publisher_last_modified=None` (backfill marker). Post-step overlays the two backfill-exclusive fields (`retrieved_at` from `git log --follow` + `backfilled_at` marker) via the same atomicity discipline (`.tmp` + `os.replace`, `sort_keys=True`, `indent=2`, trailing newline). `sha256_of` helper removed — single source of truth now in `sidecar.py::_sha256_of`. |
| `tests/test_refresh_loop.py` | Refresh-loop invariant test | VERIFIED | 150 lines, 2 tests, both pass in 0.34s. Uses `importlib.import_module` to bypass `cfd/__init__.py`'s `_refresh` function-alias shadow (documented in test file lines 25-28 — good future-reader discipline). `tmp_raw_tree` fixture seeds 5 raw files + matching sidecars. `_patched_refresh_downloaders()` ExitStack patches all three downloaders with synthetic bytes — no network. Test 1 (`test_refresh_loop_converges_on_unchanged_upstream`) locks the core invariant; test 2 (`test_refresh_loop_generated_at_advances_once_then_stable`) corrupts one sidecar's sha256, asserts detection, runs refresh, asserts `retrieved_at` advanced within 5s of wall clock, asserts second call reports clean. |
| `tests/test_ons_gas_download.py` | Regression guard on ons_gas error path | VERIFIED | 62 lines, 3 tests, all pass in 0.32s. Test 1: network failure raises `RequestException` (not `UnboundLocalError`). Test 2: `requests.get` call kwargs contain `timeout == 60`. Test 3: happy path returns `tmp_path / GAS_SAP_DATA_FILENAME` with correct bytes written. All three patched via `unittest.mock` — no network. |
| `data/raw/**/*.meta.json` (5 files) | Re-emitted with real `git log --follow` values | VERIFIED | All 5 files present with 64-char sha256, 200/null http_status, full upstream_url, and `retrieved_at` values now sourced from real git log (not BACKFILL_DATE fallback). Byte-identity preserved: a fresh `uv run python scripts/backfill_sidecars.py` run produces zero bytes of diff against the committed sidecars. |
| `CHANGES.md` [Unreleased] | 04-07 entries under Added / Fixed / Changed | VERIFIED | Three Added bullets (sidecar.py, test_refresh_loop.py, test_ons_gas_download.py); two Fixed bullets (ons_gas.py error path, _refresh.py gap #1 + duplicate URL_MAP note); one Changed bullet (backfill_sidecars.py delegate-to-helper refactor). Every entry cites "Plan 04-07" and its gap number where applicable. |

### Key Link Verification

Gap-closure wiring (links that were broken or absent pre-04-07 and are now present and exercised):

| From | To | Via | Status | Details |
|------|------|------|--------|---------|
| `schemes/cfd/_refresh.py::refresh` | `data.elexon::download_elexon_data` | Inline import + call | VERIFIED | Line 84, 97. Previously absent (gap #1 — deferred to refresh_all.py which never picked it up). |
| `schemes/cfd/_refresh.py::refresh` | `data.ons_gas::download_dataset` | Inline import (aliased) + call | VERIFIED | Line 89, 100. Previously absent. |
| `schemes/cfd/_refresh.py::refresh` | `data.sidecar::write_sidecar` | Inline import + loop-call 5× | VERIFIED | Line 90, 111. Previously absent entirely — sidecars only written by one-shot backfill. Now called for every raw file after download. |
| `scripts/backfill_sidecars.py::main` | `data.sidecar::write_sidecar` | `sys.path.insert` + import + call | VERIFIED | Line 75-76, 84-89. Previously backfill owned its own SHA + JSON-write code (duplicated logic); now delegates. |
| `tests/test_refresh_loop.py` | `schemes.cfd._refresh` submodule | `importlib.import_module` | VERIFIED | Line 29. Required because `cfd/__init__.py` binds `_refresh` as a function alias (shadowing the submodule on attribute-chain lookup); documented in-file for future test authors. |

All other Phase 4 key links remain VERIFIED from the prior run — no regression touched `publish/manifest.py`, `publish/csv_mirror.py`, `publish/snapshot.py`, `refresh_all.py`, `schemes/cfd/__init__.py`, or any derived-layer builder.

### Data-Flow Trace (Level 4)

Updated for the two artifacts whose data flow was partial/disconnected pre-04-07:

| Artifact | Data variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `schemes/cfd/_refresh.py::refresh()` | (side effects — downloads + sidecar writes) | `download_lccc_datasets(config)` + `download_elexon_data()` + `download_ons_gas()` + `write_sidecar()` for each of 5 raw paths | **Yes — all 3 publishers fetched; all 5 sidecars rewritten** | **FLOWING** (was: STATIC/DISCONNECTED for Elexon + ONS) |
| `refresh_all.py::refresh_scheme()` | bool | Delegates to `scheme.refresh()` (which now closes the loop) | Yes — full data path flows end-to-end, sidecars advance `retrieved_at` | **FLOWING** (was: DISCONNECTED for sidecar-advance path) |
| `data.sidecar.write_sidecar()` | `.meta.json` bytes | Computes sha256 of live raw file + stamps `retrieved_at=now(UTC)` + echoes `upstream_url` from caller | Yes — every successful call overwrites the sidecar atomically | FLOWING |

All other data flows remain FLOWING from the prior run.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full test suite is green | `uv run pytest tests/ -q` | `74 passed, 4 skipped in 6.38s` (was 69+4 pre-04-07) | PASS |
| Refresh-loop invariant locked | `uv run pytest tests/test_refresh_loop.py -v` | 2 passed in 0.34s | PASS |
| ons_gas error-path regression guard | `uv run pytest tests/test_ons_gas_download.py -v` | 3 passed in 0.32s | PASS |
| Refresh invokes all 3 publishers | `grep -n download_* src/uk_subsidy_tracker/schemes/cfd/_refresh.py` | `download_lccc_datasets` @ line 86/94; `download_elexon_data` @ line 84/97; `download_ons_gas` @ line 89/100 | PASS |
| Refresh writes sidecars for all 5 files | `grep -n write_sidecar src/uk_subsidy_tracker/schemes/cfd/_refresh.py` | `from … import write_sidecar` @ line 90; `write_sidecar(raw_path=raw_path, upstream_url=upstream_url)` @ line 111 (inside 5-iteration loop over `_URL_MAP`) | PASS |
| ons_gas output_path bound before try | `grep -n -E 'output_path\|try:\|except' src/.../ons_gas.py` | `output_path = DATA_DIR / …` @ line 36; `try:` @ line 38; `except` @ line 45 | PASS |
| ons_gas uses timeout=60 | `grep -n timeout src/.../ons_gas.py` | `timeout=60` on `requests.get` @ line 39 | PASS |
| ons_gas fail-loud on network failure | `grep -n -E 'raise\|except' src/.../ons_gas.py` | Bare `raise` @ line 47 (fail-loud per D-17) | PASS |
| Backfill byte-identity preserved | `uv run python scripts/backfill_sidecars.py && git diff data/raw/` | 5 sidecars written; `git diff data/raw/` shows **zero bytes changed** | PASS |
| No scope creep (5 forbidden files untouched) | `git log --oneline -- <5 files>` since `61ac424` (pre-04-07) | All 5 files' last commit predates 04-07 (manifest.py @ 2e90d11; forward_projection.py @ e00a4f6; lccc.py @ 596594c; refresh.yml @ f3b9e33; deploy.yml @ bbb421d) | PASS |
| Shared SHA helper single source of truth | `grep sha256_of scripts/backfill_sidecars.py` | No match — helper removed (now lives only in `sidecar.py::_sha256_of`) | PASS |
| CHANGES.md 04-07 entries | `grep -c "04-07" CHANGES.md` | Multiple entries under Added / Fixed / Changed with "Plan 04-07" citation | PASS |

Every prior spot-check (manifest contract, snapshot CLI, mkdocs build --strict, determinism, csv mirror quality, workflow YAML parse) re-runs green. No regressions.

### Requirements Coverage

Delta against the prior verification — only two requirements moved from PARTIAL to SATISFIED; the remainder stay SATISFIED:

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|----------------|-------------|--------|----------|
| PUB-01 | 04-04 | `publish/manifest.py` builds `site/data/manifest.json` with provenance | SATISFIED | Unchanged |
| PUB-02 | 04-04 | `publish/csv_mirror.py` writes CSV alongside every Parquet | SATISFIED | Unchanged |
| PUB-03 | 04-04, 04-05 | `publish/snapshot.py` creates versioned snapshot on tag release | SATISFIED | Unchanged |
| PUB-04 | 04-06 | `docs/data/index.md` explains journalist/academic use | SATISFIED | Unchanged |
| PUB-05 | 04-02, 04-03, 04-04, **04-07** | Three-layer pipeline operational end-to-end for CfD | SATISFIED (**upgraded** — structural concern resolved) | Refresh loop now closes the raw→derived→published cycle on a real upstream change. `ons_gas` error path no longer undermines end-to-end reliability. |
| PUB-06 | 04-04, 04-06 | External consumer fetches manifest + follows URL + retrieves Parquet/CSV | SATISFIED | Unchanged |
| GOV-02 | 04-02, 04-03, 04-04 | manifest.json exposes full provenance per dataset | SATISFIED | Unchanged |
| GOV-03 | 04-05, **04-07** | Daily refresh CI workflow with per-scheme dirty-check | SATISFIED (**upgraded from PARTIAL**) | Refresh loop now functional end-to-end on real upstream change (gap #1 closed). Error-path fail-loud posture on ONS downloader (gap #2 closed). Invariant test (`test_refresh_loop.py`) pins the algebraic property locally so the workflow's "functional" claim is reproducible without a live GitHub Actions run. |
| GOV-04 | (seed) | Methodology versioning | SATISFIED | Unchanged |
| GOV-06 | 04-04, 04-05, 04-06 | Versioned-snapshot URL citability | SATISFIED | Unchanged |
| TEST-02 | 04-03 | Pydantic schema validation on derived Parquet | SATISFIED | Unchanged |
| TEST-03 | 04-03 | Row-conservation across grain rollups | SATISFIED | Unchanged |
| TEST-05 | 04-03 | Byte-identical Parquet rebuild determinism | SATISFIED | Unchanged |

**No orphaned requirements.** REQUIREMENTS.md already tags PUB-05 and GOV-03 as "Complete" in the traceability table (lines 183, 186).

### Anti-Patterns Found

Delta against prior run:

| File | Line | Pattern | Severity | Impact | Delta |
|------|------|---------|----------|--------|-------|
| `src/uk_subsidy_tracker/data/ons_gas.py` | 31-44 | ~~`output_path` bound inside `try`; `except` returns unbound variable~~ | ~~Blocker~~ | ~~UnboundLocalError on network failure~~ | **RESOLVED 04-07** |
| `src/uk_subsidy_tracker/schemes/cfd/_refresh.py` | 53-67 | ~~Elexon + ONS refresh "delegated" to refresh_all.py but not picked up~~ | ~~Warning~~ | ~~Structural incompleteness~~ | **RESOLVED 04-07** — refresh() now invokes all 3 downloaders in-line |
| `src/uk_subsidy_tracker/refresh_all.py` | 42-87 | ~~No sidecar-rewrite code path~~ | ~~Warning~~ | ~~Sidecar SHA + retrieved_at stale after refresh~~ | **RESOLVED 04-07** — sidecar-rewrite lives in `scheme.refresh()`, which refresh_all delegates to (Option A architecture: scheme owns its raw tree + provenance) |
| `src/uk_subsidy_tracker/schemes/cfd/_refresh.py` | 31-42 (new) | Duplicated `_URL_MAP` with `scripts/backfill_sidecars.py::URL_MAP` | Info (accepted) | Two scripts both carry the same 5 URLs. Trade-off documented in plan key-decision #2: locality over DRY; cross-drift would be caught by `test_refresh_loop` invariant on first divergent write. Acceptable. |
| `src/uk_subsidy_tracker/schemes/cfd/_refresh.py::_sha256` | 45-51 | Duplicate of `data/sidecar.py::_sha256_of` | Info (accepted) | Used only by `upstream_changed()` dirty-check, not by `refresh()`. Flagged in plan-summary as a future-extraction candidate; not blocking. |
| `.github/workflows/{refresh,deploy}.yml` | multiple | Actions pinned to floating majors | Info (accepted) | Unchanged; out of 04-07 scope per plan rationale. |
| `src/uk_subsidy_tracker/publish/manifest.py` | 172-199 | `_site_url()` line-scan fragility | Info | Unchanged; WR-03 out of 04-07 scope. |
| `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py` | 99 | `int(gen["Settlement_Date"].max().year)` no defensive fallback | Info | Unchanged; WR-04 out of 04-07 scope. |

Two blockers + two warnings from the prior run all resolved. No new blockers or warnings introduced. No TODO/FIXME/PLACEHOLDER comments added.

### Human Verification Required

The same three items carry forward unchanged from the prior verification — all three are dashboard / GitHub-Actions / visual-rendering checks that cannot be verified from a local checkout. They are not blockers for the "passed" status: every locally-verifiable truth is VERIFIED; the human items exercise GitHub-integration behaviour that the daily-refresh workflow and release-asset pipeline depend on but that has no bearing on the code's correctness.

1. `workflow_dispatch` trigger of `refresh.yml` (user-dashboard prerequisites: enable PR-approval toggle + create labels).
2. Tag-push trigger of `deploy.yml` + HTTPS retrieval of release-asset Parquet matches manifest SHA-256.
3. Visual inspection of `docs/data/index.md` rendered via `uv run mkdocs serve`.

### Gaps Summary

**Gap #1 (SC #5 / GOV-03 structural incompleteness):** **RESOLVED in plan 04-07 — see commits `29b5524`, `ac9675a`, `42c8c3e`, `3497296`, `14e2138`.** The refresh flow is now wired end-to-end at the data layer. `schemes/cfd/_refresh.py::refresh()` invokes all three publisher downloaders (LCCC + Elexon + ONS) and writes `.meta.json` sidecars for every one of the five raw files via the new shared `write_sidecar()` helper. The algebraic invariant that the phase goal's "functional" clause depends on — after refresh, `upstream_changed()` reports False on the next call; `max(sidecar.retrieved_at)` advances once then stays stable on unchanged second runs — is pinned by `tests/test_refresh_loop.py` (2 tests, both pass locally without network). `manifest.generated_at` will advance on real upstream change and stay stable otherwise.

**Gap #2 (PUB-05 / GOV-03 error resilience):** **RESOLVED in plan 04-07 — see commit `ac9675a`.** `ons_gas.download_dataset()` cannot raise `UnboundLocalError` on network failure (`output_path` bound before `try:`), carries `timeout=60` matching the Elexon convention, and fail-loud-raises on `RequestException` per D-17. Regression test `tests/test_ons_gas_download.py` (3 tests, all pass) locks all three invariants so future edits cannot silently regress the error path.

Both gaps closed without scope creep: the five files explicitly out-of-scope per the prior verifier's recommendation (`publish/manifest.py`, `schemes/cfd/forward_projection.py`, `data/lccc.py`, `.github/workflows/refresh.yml`, `.github/workflows/deploy.yml`) show empty `git diff` since commit `61ac424` (last commit before 04-07 started). The `Info`-tagged concerns surfaced pre-04-07 (WR-03 line-scan fragility, WR-04 empty-data fallback, action-SHA pinning) remain as documented future-candidate items; they do not block Phase 4 closure.

### Deferred Items

None. All phase-scoped work — including the two 04-07 gap-closure deliverables — is either delivered-and-verified or surfaces only in the three human-verification items (which were always expected to need a live GitHub Actions / mkdocs-serve session).

---

## VERIFICATION PASSED

**Phase 4 (Publishing Layer) goal achieved.** All five ROADMAP success criteria are VERIFIED; SC #2 and SC #5 both flipped from partial/failed to VERIFIED via plan 04-07 gap closure. Full test suite 74 passed + 4 skipped (up from 69+4 pre-04-07). No scope creep. Byte-identity on existing sidecars preserved. Ready to proceed to Phase 5 (Renewables Obligation), which copies the now-complete scheme-module template verbatim.

Three human verification items remain as originally identified — all require GitHub-infrastructure or visual inspection and are informational rather than blocking. They should be completed opportunistically when the user next touches the GitHub repo settings or the docs site.

---

*Verified: 2026-04-23T02:00:00Z*
*Verifier: Claude (gsd-verifier) — re-verification after plan 04-07*
