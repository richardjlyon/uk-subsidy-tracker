---
phase: 05-ro-module
plan: 6
subsystem: publishing
tags: [manifest, scheme-parametric, multi-scheme, pydantic, publishing-layer]

# Dependency graph
requires:
  - phase: 04-publishing-layer
    provides: "`publish/manifest.py` single-scheme CfD implementation (Plan 04-04); `refresh_all.SCHEMES` tuple; Dataset/Manifest Pydantic contracts; 8 CfD-parity tests"
provides:
  - "Scheme-parametric manifest.build() iterating an Iterable[tuple[str, Any]] of schemes"
  - "derived_root: Path parent + per-scheme subdir discovery (derived_root/<scheme>/*.parquet)"
  - "Nested GRAIN_SOURCES/TITLES/DESCRIPTIONS dicts keyed by scheme (outer) × grain (inner)"
  - "URL pattern /data/{latest,<version>}/<scheme>/<grain>.<ext> — CfD unchanged, RO slots in at Plan 05-07"
  - "Empty-scheme-dir skip semantics (valid pre-first-rebuild state)"
  - "3 new test_manifest tests proving multi-scheme iteration (11 total, was 8)"
affects: [05-07-ro-registration, 07-fit-module, 08-10-remaining-schemes, manifest-json-consumers]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Scheme-parametric manifest.build() — all future scheme modules auto-publish with a one-line SCHEMES append"
    - "Filesystem-driven grain discovery — derived_root/<scheme>/*.parquet globbed sorted; no per-scheme grain registry needed"
    - "Per-(scheme, grain) provenance via nested GRAIN_SOURCES dict — preserves B-02 mitigation at scheme granularity"
    - "Empty scheme_derived silently skipped — registered-but-not-yet-built schemes do not crash manifest.build"

key-files:
  created: []
  modified:
    - "src/uk_subsidy_tracker/publish/manifest.py — refactored build() to iterate schemes iterable; nested GRAIN_SOURCES/TITLES/DESCRIPTIONS; _build_dataset_entry + _grain_title/_grain_description/_grain_sources helpers"
    - "src/uk_subsidy_tracker/refresh_all.py — publish_latest() passes SCHEMES + DERIVED_DIR (formerly DERIVED_DIR / 'cfd')"
    - "tests/test_manifest.py — fixture uses new signature; 3 new multi-scheme iteration tests (test_manifest_build_handles_two_schemes, test_manifest_urls_include_scheme_segment, test_manifest_empty_scheme_derived_is_skipped)"

key-decisions:
  - "Refactor Option 3 (scheme-awareness inside one manifest) — single manifest.json with datasets[] containing every scheme × every grain; matches ARCHITECTURE §4.3 one-manifest contract; rejects per-scheme manifest files (breaks contract) and @scheme_name= kwarg (doesn't scale past 2 schemes)"
  - "Filesystem-driven grain discovery over explicit per-scheme grain registry — scheme_derived.glob('*.parquet') sorted; schemes register grains via GRAIN_SOURCES nested dict only (B-02 preserved)"
  - "test_manifest.py fixture updated to new signature rather than keeping back-compat overload — fixture is test infrastructure not a public contract; 8 test bodies assert behaviour on manifest output, not call signature"
  - "Monkeypatch GRAIN_SOURCES/TITLES/DESCRIPTIONS in multi-scheme tests — avoids polluting module-level dicts with test-only RO entries; real RO registration lands via src/ in Plan 05-07 alongside the schemes/ro/ module"

patterns-established:
  - "Per-(scheme, grain) lookup via scheme-keyed-outer nested dicts — replaces grain-only dicts; scales to arbitrary scheme count"
  - "build() is keyword-only (PEP 3102): `def build(*, version, schemes, derived_root, raw_dir, output_path)` — prevents positional-arg bugs as signature evolves"
  - "Iterable[tuple[str, Any]] instead of tuple of (name, SchemeModule) — Protocol isn't enforced in build() because manifest uses only the scheme name and derived_root/<name> lookup; keeps the contract loose for tests and future schemes"

requirements-completed: [RO-03]

# Metrics
duration: 5min
completed: 2026-04-23
---

# Phase 5 Plan 6: Manifest.py SCHEMES-parametric refactor Summary

**Multi-scheme manifest.build() iterating `schemes: Iterable[tuple[str, Any]]` + `derived_root: Path` — RO Parquet grains will surface in site/data/manifest.json as soon as Plan 05-07 registers `("ro", ro)` in `refresh_all.SCHEMES`; CfD path preserved byte-identical (8 existing tests pass unchanged).**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-23T05:18:21Z
- **Completed:** 2026-04-23T05:23:36Z
- **Tasks:** 2 / 2
- **Files modified:** 3 (manifest.py, refresh_all.py, test_manifest.py)

## Accomplishments

- Hard-coded `"cfd."` prefix and `/cfd/` URL literals removed from manifest.py. `id=f"{scheme_name}.{grain}"`; URLs route via `/data/latest/<scheme>/<grain>.*`.
- `build()` signature now `(*, version, schemes, derived_root, raw_dir, output_path)` — keyword-only, scheme-parametric, derived_root is the parent of per-scheme dirs.
- `GRAIN_SOURCES`, `GRAIN_TITLES`, `GRAIN_DESCRIPTIONS` converted to nested `dict[scheme, dict[grain, ...]]` — every scheme registers its per-grain provenance explicitly (B-02 mitigation preserved at scheme granularity).
- `refresh_all.publish_latest()` passes `schemes=SCHEMES` and `derived_root=DERIVED_DIR`. Plan 05-07 now only needs the one-line `("ro", ro)` append to `SCHEMES`.
- 3 new tests pin the refactor contract: 2-scheme × 5-grain → exactly 10 datasets (ids match `<scheme>.<grain>`); all URLs carry the scheme segment; missing scheme_derived dir is a silent skip.
- CfD path preserved byte-identical — 8 existing tests/test_manifest.py tests (round-trip identity, absolute URLs, sha256 match, methodology_version D-12 chain, generated_at stability Pitfall 3) pass unchanged.
- Test coverage: 145 passed + 4 skipped (was 142 + 4; +3 new).

## Hard-Coded CfD References Removed

Phase 7+ code review reference (per plan `<output>` directive). Each reference was on a URL-assignment line in `_assemble_dataset_entries()` (removed) → now in `_build_dataset_entry()`:

| Line (pre) | Before                                                                 | After                                                                                  |
| ---------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| 307        | `id=f"cfd.{grain}",`                                                   | `id=f"{scheme_name}.{grain}",`                                                         |
| 311        | `schema_url=f"{base}/data/latest/cfd/{grain}.schema.json",`            | `schema_url=f"{base}/data/latest/{scheme_name}/{grain}.schema.json",`                  |
| 312        | `parquet_url=f"{base}/data/latest/cfd/{grain}.parquet",`               | `parquet_url=f"{base}/data/latest/{scheme_name}/{grain}.parquet",`                     |
| 313        | `csv_url=f"{base}/data/latest/cfd/{grain}.csv",`                       | `csv_url=f"{base}/data/latest/{scheme_name}/{grain}.csv",`                             |
| 314        | `versioned_url=f"{base}/data/{vseg}/cfd/{grain}.parquet",`             | `versioned_url=f"{base}/data/{vseg}/{scheme_name}/{grain}.parquet",`                   |

In `refresh_all.py::publish_latest()`:

| Line (pre) | Before                                | After                              |
| ---------- | ------------------------------------- | ---------------------------------- |
| 84         | `derived_dir=DERIVED_DIR / "cfd",`    | `schemes=SCHEMES,`                 |
| —          | (implicit — no schemes kwarg)         | `derived_root=DERIVED_DIR,`        |

Remaining `"cfd"` string literals in manifest.py are (a) module docstring references to `schemes/cfd/__init__.py` for the D-12 chain explanation (lines 20, 44 — documentation only) and (b) outer-dict registration keys in `GRAIN_SOURCES/TITLES/DESCRIPTIONS` (lines 75, 105, 115 — these are data, not code-path branches). None are on URL-assignment lines or id-construction lines. Grep -E verification: `grep -E '^\s*(id=|parquet_url=|schema_url=|csv_url=|versioned_url=).*("cfd\.|/cfd/)' src/uk_subsidy_tracker/publish/manifest.py` returns zero hits.

## Task Commits

Each task was committed atomically:

1. **Task 1: Refactor manifest.build() to iterate schemes iterable** — `757ac4e` (refactor)
2. **Task 2: Add test_manifest_iterates_multiple_schemes (3 new tests)** — `7d94884` (test)

## Files Created/Modified

- `src/uk_subsidy_tracker/publish/manifest.py` — scheme-parametric build(); nested GRAIN_SOURCES/TITLES/DESCRIPTIONS; 3 new helpers (_grain_title, _grain_description, _grain_sources); _build_dataset_entry keyed by (scheme, grain); _assemble_dataset_entries iterates schemes iterable (Task 1).
- `src/uk_subsidy_tracker/refresh_all.py` — publish_latest() passes schemes=SCHEMES + derived_root=DERIVED_DIR (Task 1).
- `tests/test_manifest.py` — fixture migrated to new signature; 3 new tests for multi-scheme iteration (Tasks 1 + 2).

## Decisions Made

- **Refactor Option 3 (scheme-awareness inside one manifest)** over Option 1 (scheme_name kwarg) and Option 2 (per-scheme manifest files). Option 3 preserves ARCHITECTURE §4.3 one-manifest contract; Option 1 forces N invocations and wouldn't surface multi-scheme datasets in a single file; Option 2 breaks the external-consumer contract.
- **Filesystem-driven grain discovery** over explicit per-scheme grain list. `scheme_derived.glob("*.parquet")` sorted is deterministic; adding a new grain to a scheme requires zero manifest.py changes (only a GRAIN_SOURCES entry for the B-02 provenance contract). Matches the principle that the Parquet files on disk are the source of truth.
- **Keyword-only build() signature** (`*, version, schemes, derived_root, raw_dir, output_path`). Prevents positional-arg bugs as the signature evolves across schemes; mirrors the ARCHITECTURE §4.3 "always call by name" convention.
- **Monkeypatch in multi-scheme tests** rather than permanent RO entries in module-level GRAIN_SOURCES. Real RO entries will land via src/ alongside the schemes/ro/ module in Plan 05-07; landing them here would be ahead-of-order and would require faking grain output in the same PR.
- **Fixture migrated to new signature** rather than preserving a back-compat wrapper for `derived_dir=`. The fixture is test infrastructure (not a public contract); the 8 CfD tests assert behaviour on manifest output (URLs, sha256s, methodology_version, generated_at stability) — not call-signature. All 8 pass unchanged.

## Deviations from Plan

None — plan executed exactly as written. All 11 tests pass, including the 8 pre-existing CfD-parity tests; no deviation rules invoked.

One minor implementation adjustment: the plan's `<action>` Step 2 code sketch used `base_url: str = "https://richardjlyon.github.io/uk-subsidy-tracker"` as a keyword default. The existing HEAD code uses `_site_url()` which reads from `SITE_URL` env var or falls back to `mkdocs.yml::site_url` line-scan. I preserved the existing `_site_url()` pattern (it's the Plan 04-04 contract — SITE_URL override in deploy.yml) rather than introducing a hard-coded default. Functionally equivalent to the plan intent; keeps the env-var override working.

## Issues Encountered

One test-side regex issue during Task 2 RED run: the URL-pattern regex `^https?://[^/]+/data/latest/...` failed against `https://richardjlyon.github.io/uk-subsidy-tracker/data/latest/cfd/...` because `mkdocs.yml::site_url` carries a repo-subpath (`/uk-subsidy-tracker`) between the host and `/data/latest/`. Fixed by relaxing the host-matching component to `\S+` (arbitrary path prefix tolerated). Pre-commit; no extra commit needed.

## Verification Results

- `uv run pytest tests/test_manifest.py -x -q` → 11 passed (was 8; +3 new multi-scheme tests)
- `grep -E '^\s*(id=|parquet_url=|schema_url=|csv_url=|versioned_url=).*("cfd\.|/cfd/)' src/uk_subsidy_tracker/publish/manifest.py` → 0 hits ✓
- `grep "schemes=" src/uk_subsidy_tracker/refresh_all.py` → 1 match at line 84 ✓
- `uv run pytest tests/ -q` → 145 passed, 4 skipped (was 142 + 4; +3 from Plan 05-06)
- CfD regression check: 8 pre-existing test_manifest.py tests pass byte-identical assertions (round-trip identity, absolute URLs, sha256, methodology_version D-12, generated_at Pitfall 3) ✓

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 05-07 (Wave 3) can now append `("ro", ro)` to `refresh_all.SCHEMES` in a single line; manifest.py auto-surfaces every `data/derived/ro/*.parquet` grain as a `Dataset` entry with `id="ro.<grain>"` and `/data/latest/ro/<grain>.*` URLs, provided (a) the RO grain is registered in `GRAIN_SOURCES["ro"]` with its raw-file references (for B-02 provenance), and (b) `schemes/ro/__init__.py::rebuild_derived()` has written the Parquet.
- Phase 7 (FiT) + Phases 8-12 inherit the same hookup: one-line `SCHEMES` append + `GRAIN_SOURCES[<scheme>]` registration.
- No blockers. Wave 1 complete once this plan's final metadata commit lands.

## Self-Check: PASSED

Verified on disk:

- `src/uk_subsidy_tracker/publish/manifest.py` — FOUND (modified; 451 lines)
- `src/uk_subsidy_tracker/refresh_all.py` — FOUND (modified; 124 lines)
- `tests/test_manifest.py` — FOUND (modified; 530 lines)
- `.planning/phases/05-ro-module/05-06-SUMMARY.md` — FOUND (this file)

Verified in git log:

- `757ac4e refactor(05-06): manifest.py iterates SCHEMES; prepares RO multi-scheme publishing` — FOUND
- `7d94884 test(05-06): add multi-scheme manifest iteration tests` — FOUND

Verification matches all SUMMARY.md claims (file paths, commit hashes, test counts).

---
*Phase: 05-ro-module*
*Completed: 2026-04-23*
