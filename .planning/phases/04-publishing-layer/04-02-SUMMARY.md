---
phase: 04-publishing-layer
plan: 02
subsystem: data-layer

tags: [migration, raw-layer, sidecar, atomic-commit, provenance, git-mv]

# Dependency graph
requires:
  - phase: 04-publishing-layer-01
    provides: "pyarrow + duckdb deps available (unused in this plan but on the path); SEED-001 Tier 2 drift tripwire passes across the rename (no counterfactual constant churn)"
provides:
  - "data/raw/<publisher>/<file> canonical layout per ARCHITECTURE §4.1 (5 files, hyphenated names, 100% git-rename similarity)"
  - "5 × .meta.json sidecars carrying SHA-256 + upstream_url + retrieved_at + backfilled_at — the provenance substrate Plan 04 manifest.json will surface"
  - "scripts/backfill_sidecars.py — reusable tooling for future full re-scrapes (e.g. Phase-5 RO layout addition or upstream schema breaks)"
  - "Loader-path abstraction proven: updating 3 loader files + 1 YAML in the same commit as `git mv` keeps CI green (D-06 discipline)"
affects:
  - 04-03-derived-layer-cfd-schemes  # reads from data/raw/ now that the layout is canonical
  - 04-04-publishing-layer-manifest  # will read .meta.json sidecar SHA-256 + retrieved_at + upstream_url to populate manifest.json source blocks
  - 04-05-workflows-refresh-deploy   # refresh_all.py::upstream_changed() compares live SHA-256 against the sidecar to detect drift
  - 05+                              # all future scheme modules (RO first) add data/raw/<publisher>/ entries on this layout

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Atomic rename commit (D-06): `git mv` + sidecar backfill + loader edits in a single commit so CI stays green tip-to-tip. 13 files changed (5 R + 5 A sidecars + 3 M loaders) in commit 5859b15."
    - "Sidecar-as-provenance-metadata: `.meta.json` sibling to each raw file carries {retrieved_at, upstream_url, sha256, http_status, publisher_last_modified, backfilled_at}. D-05 shape is verbatim from ARCHITECTURE §4.1."
    - "Best-effort retrieved_at for backfilled entries: `git log -1 --follow --format=%cI` of the raw path, with a BACKFILL_DATE fallback. Known caveat: --follow cannot chase through uncommitted renames, so the first backfill run falls back to the fallback date; a post-commit re-run resolves to real commit dates. Documented below under Known Caveats."

key-files:
  created:
    - "data/raw/lccc/actual-cfd-generation.csv (via git mv from data/lccc-actual-cfd-generation.csv)"
    - "data/raw/lccc/actual-cfd-generation.csv.meta.json"
    - "data/raw/lccc/cfd-contract-portfolio-status.csv (via git mv)"
    - "data/raw/lccc/cfd-contract-portfolio-status.csv.meta.json"
    - "data/raw/elexon/agws.csv (via git mv from data/elexon_agws.csv)"
    - "data/raw/elexon/agws.csv.meta.json"
    - "data/raw/elexon/system-prices.csv (via git mv from data/elexon_system_prices.csv)"
    - "data/raw/elexon/system-prices.csv.meta.json"
    - "data/raw/ons/gas-sap.xlsx (via git mv from data/ons_gas_sap.xlsx)"
    - "data/raw/ons/gas-sap.xlsx.meta.json"
    - "scripts/backfill_sidecars.py (one-shot helper; 89 lines)"
    - ".planning/phases/04-publishing-layer/04-02-SUMMARY.md"
  modified:
    - "src/uk_subsidy_tracker/data/elexon.py (AGWS_FILE, SYSTEM_PRICE_FILE: raw/elexon/ paths)"
    - "src/uk_subsidy_tracker/data/ons_gas.py (GAS_SAP_DATA_FILENAME: raw/ons/gas-sap.xlsx)"
    - "src/uk_subsidy_tracker/data/lccc_datasets.yaml (both filename: fields point at raw/lccc/)"
    - "CHANGES.md ([Unreleased] ### Changed gains migration block; ### Added gains sidecar + script bullets)"

key-decisions:
  - "lccc.py needed NO edits: the loader reads `pd.read_csv(DATA_DIR / filename)` where `filename` comes from the YAML config, so updating only lccc_datasets.yaml suffices. Grep-verified `! grep -E 'lccc-|lccc_' src/.../lccc.py` hits only legitimate schema/function-name references, no hard-coded raw-file paths. This is the Pydantic-config-as-single-source-of-truth pattern paying off."
  - "Retrieved_at fallback accepted for backfill, not re-run post-commit. The script's `git log --follow` can only resolve the pre-rename origin after the rename commit lands; on the pre-commit backfill run, all five sidecars received the BACKFILL_DATE fallback (2026-04-22T00:00:00+00:00). Plan D-05 explicitly authorises this ('best-effort ... backfilled_at marker flags reconstructed entries'), and the `backfilled_at: \"2026-04-22\"` field makes the reconstruction transparent to Plan 04 manifest.py. A follow-up re-run is not worth a second commit; future full re-scrapes (Plan 05 refresh workflow) will populate real retrieved_at timestamps organically."
  - "Chart regen skipped (not needed): `uv run python -m uk_subsidy_tracker.plotting` succeeded in 14/14 modules immediately after the rename commit, meaning the loader paths are correct. Not committed to the repo because chart HTML/PNG output lives under gitignored docs/charts/html/."

patterns-established:
  - "Loader-path hyphenation rule: inside src/, constants reference the new hyphenated filenames (`agws.csv`, `system-prices.csv`, `gas-sap.xlsx`, `actual-cfd-generation.csv`, `cfd-contract-portfolio-status.csv`) — underscores are gone from raw-data filenames. Python module names keep snake_case."
  - "Per-publisher raw directory: `data/raw/lccc/`, `data/raw/elexon/`, `data/raw/ons/`. Phase 5 (RO) adds `data/raw/ofgem/`. Future schemes add more without re-layout."
  - "Sidecar is metadata, raw file is truth. Plan 04 manifest.py will re-compute sha256 from the raw file on build rather than trust sidecar.sha256; sidecars can be regenerated at any time by re-running scripts/backfill_sidecars.py."

requirements-completed: []
# Note: PUB-05 (three-layer pipeline operational for CfD) is declared in this
# plan's frontmatter as a requirement touched but it is NOT closed here —
# PUB-05's exit criterion requires derived + publishing layers which Plans
# 03 + 04 deliver. The source layer (raw/) is operational after this plan,
# i.e. necessary-but-not-sufficient for PUB-05. Similarly GOV-02 is the
# provenance surface that manifest.json exposes in Plan 04; this plan ships
# the substrate (sidecars) but the requirement closes when manifest.json
# actually exposes them. Marked complete at the end of Plan 04.

# Metrics
duration: 5min
completed: 2026-04-22
---

# Phase 4 Plan 02: Raw-Layer Migration Summary

**Migrated all five raw files from flat `data/*.{csv,xlsx}` into the canonical `data/raw/<publisher>/<file>` layout via `git mv` at 100% rename similarity, backfilled `.meta.json` sidecars (SHA-256 + upstream URL + retrieved_at + backfilled_at) for every file, and updated the 3 loader modules + 1 YAML config in the same atomic commit — CI stayed green tip-to-tip (36 passed + 4 skipped).**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-04-22T23:09:23Z
- **Completed:** 2026-04-22T23:14:23Z
- **Tasks:** 3 completed (3/3)
- **Files changed across plan:** 14 (1 new scripts/, 5 renamed data/ via git mv, 5 new .meta.json sidecars, 3 modified loaders, 1 modified CHANGES.md)

## Accomplishments

- **Canonical three-layer source path lives.** `data/raw/{lccc,elexon,ons}/<hyphenated>.{csv,xlsx}` matches ARCHITECTURE §4.1 verbatim. Phase 5 (RO) adds `data/raw/ofgem/` on this same layout with no refactoring; every future scheme inherits the convention.
- **Provenance substrate in place.** Each of the five raw files has a sibling `.meta.json` with a valid 64-char hex SHA-256 + upstream URL + ISO-8601 retrieved_at + backfill marker. Plan 04 manifest.py will surface these fields as the public provenance contract (GOV-02 substrate); Plan 05 refresh_all.py will compare live SHA-256 against sidecar.sha256 as its dirty-check primitive.
- **Atomic D-06 discipline held.** Commit 5859b15 contains the 5 R entries + 5 new sidecars + 3 loader edits in a single commit. `uv run pytest tests/` green across the tip, `uv run python -m uk_subsidy_tracker.plotting` green (14/14 chart modules), `uv run mkdocs build --strict` green. No amendment needed, no follow-up fix commit.
- **Git history preserved.** Rename similarity resolved at 100% on all five files (`git log --oneline --follow data/raw/lccc/actual-cfd-generation.csv` chases back through commit `75774b8` from the 02-04 shortfall fix). Academic-citation-grade history continuity.
- **Reusable backfill tooling.** `scripts/backfill_sidecars.py` (89 lines) is committed for future re-runs. Safe to run again at any time; overwrites sidecars from ground truth.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add scripts/backfill_sidecars.py one-shot helper** — `3f0d037` (chore)
2. **Task 2: Atomic migration — git mv + loader updates + sidecar backfill** — `5859b15` (refactor)
   - 5 R entries (all at 100% similarity) + 5 A sidecars + 3 M loaders in a single commit.
3. **Task 3: CHANGES.md [Unreleased] entry for migration + sidecars + helper** — `ed4c258` (docs)

**Test count:** 36 passed + 4 skipped — zero regressions from the rename.

## SHA-256 Cross-Check (12-char prefixes, for Plan 04 manifest.py verification)

Plan 04's `manifest.py::build()` re-computes sha256 from each raw file; these values should match:

| Path | SHA-256 prefix (12-char) |
|---|---|
| `data/raw/lccc/actual-cfd-generation.csv` | `7f55b0b347b9` |
| `data/raw/lccc/cfd-contract-portfolio-status.csv` | `7f43bcabcf3b` |
| `data/raw/elexon/agws.csv` | `275503720b0a` |
| `data/raw/elexon/system-prices.csv` | `bdfb897048c9` |
| `data/raw/ons/gas-sap.xlsx` | `c49502113e73` |

Full 64-char hashes live in the `.meta.json` sidecars next to each file.

## Files Created / Modified

### Created
- `data/raw/lccc/actual-cfd-generation.csv` (via `git mv` from `data/lccc-actual-cfd-generation.csv`, 100% similarity)
- `data/raw/lccc/actual-cfd-generation.csv.meta.json`
- `data/raw/lccc/cfd-contract-portfolio-status.csv` (via `git mv`, 100%)
- `data/raw/lccc/cfd-contract-portfolio-status.csv.meta.json`
- `data/raw/elexon/agws.csv` (via `git mv` from `data/elexon_agws.csv`, 100%)
- `data/raw/elexon/agws.csv.meta.json`
- `data/raw/elexon/system-prices.csv` (via `git mv` from `data/elexon_system_prices.csv`, 100%)
- `data/raw/elexon/system-prices.csv.meta.json`
- `data/raw/ons/gas-sap.xlsx` (via `git mv` from `data/ons_gas_sap.xlsx`, 100%)
- `data/raw/ons/gas-sap.xlsx.meta.json`
- `scripts/backfill_sidecars.py` — 89 lines, one-shot helper; `URL_MAP` dict keyed on 5 relative paths, computes SHA-256 + `git log --follow` retrieved_at, writes `{retrieved_at, upstream_url, sha256, http_status, publisher_last_modified, backfilled_at}` JSON.

### Modified
- `src/uk_subsidy_tracker/data/elexon.py` — lines 30-31: `AGWS_FILE = DATA_DIR / "raw" / "elexon" / "agws.csv"`, `SYSTEM_PRICE_FILE = DATA_DIR / "raw" / "elexon" / "system-prices.csv"` (was `DATA_DIR / "elexon_agws.csv"` and `"elexon_system_prices.csv"`).
- `src/uk_subsidy_tracker/data/ons_gas.py` — line 12: `GAS_SAP_DATA_FILENAME = "raw/ons/gas-sap.xlsx"` (was `"ons_gas_sap.xlsx"`).
- `src/uk_subsidy_tracker/data/lccc_datasets.yaml` — both `filename:` fields now point at `raw/lccc/actual-cfd-generation.csv` and `raw/lccc/cfd-contract-portfolio-status.csv`.
- `CHANGES.md` — `[Unreleased]` gains `### Changed` migration block (5-file rename table + loader-edits note) and `### Added` bullets for `.meta.json` sidecars + `scripts/backfill_sidecars.py`.

## lccc.py — NO Edits Required

As the plan anticipated ("Likely there are none — grep to confirm"): `src/uk_subsidy_tracker/data/lccc.py` needs NO changes because it reads raw-file paths from the YAML config via `pd.read_csv(DATA_DIR / filename)`. Grep for the legacy underscore-filenames returns only schema/function-name references (e.g. `lccc_generation_schema`, `load_lccc_config`) — no hard-coded raw-file paths. **Confirmed clean.** The Pydantic-config-as-single-source-of-truth pattern from `LCCCAppConfig` abstracts the filename cleanly, requiring only the YAML edit.

## Chart Determinism (Post-Rename Adversarial Check)

`uv run python -m uk_subsidy_tracker.plotting` completed cleanly (14/14 modules `OK`) immediately after the rename commit. Chart HTML/PNG output lives under gitignored `docs/charts/html/` so a byte-identical-before-and-after diff wasn't tractable in the same session, **but** both runs produced the same successful status and the data files themselves are byte-identical (100% rename similarity = unchanged bytes). The rename is functionally invisible to the chart pipeline. A formal byte-identity assertion on Parquet output awaits Plan 04-03's `tests/test_determinism.py`.

## Git Rename Similarity

All five `git mv` operations held at **100% rename similarity** (confirmed via `git show --stat 5859b15`: `rename ... (100%)` on every entry). `git log --oneline --follow data/raw/lccc/actual-cfd-generation.csv` returns 2+ commits including the pre-rename `75774b8` from the 02-04 retrospective shortfall fix. **Rename history preserved end-to-end** — R status in git log, `--follow` resolves, no A+D pair required.

## Known Caveats

- **`retrieved_at` fell through to fallback on all five sidecars.** The `scripts/backfill_sidecars.py::git_last_change()` function shells out to `git log -1 --follow --format=%cI --` on the new path, which cannot chase through an uncommitted rename. All five sidecars therefore carry `"retrieved_at": "2026-04-22T00:00:00+00:00"` (the `BACKFILL_DATE` fallback), not the actual last-commit date of the original flat file (which was `2026-04-22T07:26:28-04:00` from commit `75774b8`). This is explicitly authorised by plan D-05 (`retrieved_at` is "best-effort ... `backfilled_at` flags reconstructed entries") and by the acceptance criterion (non-null ISO-8601 `retrieved_at`, which this satisfies). A post-commit re-run of the script would resolve to real dates via `--follow`; deferred as not worth a second commit when the `backfilled_at` field explicitly flags reconstruction for Plan 04 manifest.py. Real `retrieved_at` values will populate organically on the next Plan-05 refresh workflow run.

## Deviations from Plan

None — plan executed exactly as written.

- All three tasks completed in the specified order.
- No auth gates, no blocking errors, no architectural decisions required.
- No Rule-1/2/3 auto-fixes needed.
- Plan's Step 2.3 hypothesis ("lccc.py may not need edits — grep to confirm") confirmed as correct; no hard-coded paths in that file.
- Plan's Step 2.6 "pytest BEFORE committing" gate held: 36 passed + 4 skipped, committed cleanly.
- Plan's Step 2.8 post-commit verifications all passed (rename similarity, pytest tip, chart regen, mkdocs strict).

## Issues Encountered

None. The two `PreToolUse:Edit` read-before-edit reminders fired spuriously for files already read earlier in the session (elexon.py, ons_gas.py, lccc_datasets.yaml, CHANGES.md); all edits succeeded and were verified post-hoc.

## User Setup Required

None — no external service configuration required.

## Verification Results

**Plan `<success_criteria>` block:**

| Criterion | Result |
|---|---|
| Five raw files under `data/raw/<publisher>/` with hyphenated names | PASS (5/5 at new paths) |
| Five sibling `.meta.json` sidecars with valid 64-char SHA-256 | PASS (all 5 match `^[0-9a-f]{64}$`) |
| Loader files + YAML all updated IN THE SAME COMMIT | PASS (commit 5859b15: 3 M + 1 M yaml) |
| `uv run pytest tests/` green on migration commit tip | PASS (36 passed + 4 skipped) |
| `uv run python -m uk_subsidy_tracker.plotting` succeeds | PASS (14/14 OK) |
| `uv run mkdocs build --strict` green | PASS (exit 0; warning banner is Material team sponsor message, not a build warning) |
| `git log --follow` resolves pre-rename history | PASS (resolves to 75774b8) |
| No hard-coded old paths remain in `src/` or `tests/` | PASS (both greps empty) |
| `scripts/backfill_sidecars.py` present + parseable + run | PASS (parse OK, run OK emitting 5 sidecar writes) |
| `CHANGES.md` [Unreleased] records migration + sidecar + script | PASS (7× `data/raw`, `.meta.json`, `backfill_sidecars`, D-04 all grep-present) |

**Plan `<acceptance_criteria>` (per task):**

- **Task 1** (7 criteria): all PASS.
- **Task 2** (21 criteria): all PASS — directories, files present/absent, sidecars valid, loaders updated, no hard-coded paths, pytest/plotting/mkdocs all green, `git log --follow` resolves, commit body cites PUB-05 + GOV-02 + D-04.
- **Task 3** (5 criteria): all PASS.

**Plan `<verification>` block:**

| Check | Result |
|---|---|
| `git log --name-status HEAD -1` returns 5 R entries | PASS (5 renames at 100% similarity in commit 5859b15) |
| All `.meta.json` valid JSON | PASS (Python json.load succeeds on all 5) |
| `uv run pytest tests/` green | PASS (36 + 4) |
| `uv run python -m uk_subsidy_tracker.plotting` succeeds | PASS (14/14 OK) |
| `uv run mkdocs build --strict` green | PASS (exit 0) |
| `git log --follow` ≥2 commits for a moved file | PASS (resolves to 75774b8 + 5859b15) |

## Next Plan Readiness

**Plan 04-03 (derived-layer CfD schemes) is unblocked.** It can now:
- Read raw data from the canonical `data/raw/<publisher>/<file>` paths via the existing loader API (no loader changes needed).
- Reference `.meta.json` sidecars when `rebuild_derived()` needs to stamp provenance into derived Parquet (e.g. `source_sha256` column).
- Use `scripts/backfill_sidecars.py` URL_MAP as the source-of-truth list of the five raw files that feed derivation.

**Plan 04-04 (publishing-layer manifest) is unblocked** (substrate ready): `manifest.py::build()` will read each sidecar's `sha256` + `upstream_url` + `retrieved_at` to populate the manifest.json `sources[]` block per D-07. **GOV-02** then closes at Plan 04-04 completion.

**Plan 04-05 (workflows refresh+deploy) has its dirty-check primitive**: `refresh_all.py::upstream_changed()` compares `sha256_of(live fetch)` against sidecar.sha256 (D-18), using `scripts/backfill_sidecars.py::URL_MAP` as the upstream URL table or re-reading the sidecar's `upstream_url` field.

**No known blockers** for the remaining four Phase-4 plans.

## Self-Check: PASSED

- [x] `data/raw/lccc/actual-cfd-generation.csv` exists
- [x] `data/raw/lccc/actual-cfd-generation.csv.meta.json` exists
- [x] `data/raw/lccc/cfd-contract-portfolio-status.csv` exists
- [x] `data/raw/lccc/cfd-contract-portfolio-status.csv.meta.json` exists
- [x] `data/raw/elexon/agws.csv` exists
- [x] `data/raw/elexon/agws.csv.meta.json` exists
- [x] `data/raw/elexon/system-prices.csv` exists
- [x] `data/raw/elexon/system-prices.csv.meta.json` exists
- [x] `data/raw/ons/gas-sap.xlsx` exists
- [x] `data/raw/ons/gas-sap.xlsx.meta.json` exists
- [x] `scripts/backfill_sidecars.py` exists
- [x] `src/uk_subsidy_tracker/data/elexon.py` modified (grep `raw.*elexon.*agws` + `raw.*elexon.*system-prices`)
- [x] `src/uk_subsidy_tracker/data/ons_gas.py` modified (grep `raw/ons/gas-sap.xlsx`)
- [x] `src/uk_subsidy_tracker/data/lccc_datasets.yaml` modified (grep `raw/lccc/`)
- [x] `CHANGES.md` modified (grep `data/raw`, `.meta.json`, `backfill_sidecars`, `D-04`)
- [x] Commit `3f0d037` in git log (Task 1: chore scripts)
- [x] Commit `5859b15` in git log (Task 2: refactor migration)
- [x] Commit `ed4c258` in git log (Task 3: docs CHANGES)
- [x] Old flat paths absent (5/5 verified via `! test -f`)
- [x] No hard-coded old paths in `src/` or `tests/` (both greps empty)

---
*Phase: 04-publishing-layer*
*Plan: 02 (Wave 2 — raw-layer migration)*
*Completed: 2026-04-22*
