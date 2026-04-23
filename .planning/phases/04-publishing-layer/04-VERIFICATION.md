---
phase: 04-publishing-layer
verified: 2026-04-22T21:00:00Z
status: gaps_found
score: 4/5 success criteria verified
overrides_applied: 0
gaps:
  - truth: "GitHub Actions daily refresh workflow is committed AND functional"
    status: partial
    reason: "Workflow YAML is committed and valid, and the orchestrator runs cleanly on an unchanged state. However, the refresh path is structurally incomplete in two ways that break functional correctness on the first real upstream change: (1) scheme.refresh() only re-fetches LCCC datasets; Elexon and ONS downloaders are never invoked (explicitly deferred in code comments to 'Plan 04-05's orchestrator' but refresh_all.py does not pick them up); (2) no code path updates .meta.json sidecars after a successful download — sidecars are written only by the one-shot scripts/backfill_sidecars.py. Because upstream_changed() compares live SHA against sidecar SHA, and manifest.generated_at sources from max(sidecar.retrieved_at), a real upstream change produces a perpetual dirty-check loop and frozen generated_at. The phase goal clause 'three-layer pipeline operational end-to-end' works today for the current raw state, but GOV-03's 'daily refresh ... functional' claim is fragile."
    artifacts:
      - path: "src/uk_subsidy_tracker/schemes/cfd/_refresh.py"
        issue: "refresh() re-fetches LCCC only; Elexon/ONS delegated to refresh_all but not picked up there. No sidecar rewrite after download."
      - path: "src/uk_subsidy_tracker/refresh_all.py"
        issue: "refresh_scheme() calls scheme.refresh() + rebuild_derived + regenerate_charts + validate but does not re-fetch Elexon/ONS nor rewrite sidecars."
    missing:
      - "End-to-end refresh helper that fetches LCCC + Elexon + ONS and rewrites .meta.json sidecars (shared helper extracted from scripts/backfill_sidecars.py)"
      - "Call sites in refresh_all.refresh_scheme() (or scheme_module.refresh() of each scheme) that invoke Elexon + ONS downloaders"
      - "Test covering the refresh loop invariant: after a simulated upstream change, running refresh_all twice produces generated_at that advances once and stays stable on the second run"

  - truth: "External consumers can follow a URL from manifest.json and retrieve a Parquet file and its CSV mirror — including when the publisher is temporarily unavailable (provenance guarantee)"
    status: partial
    reason: "Happy-path fetch works correctly (manifest.json URLs valid, snapshot.py produces 5 Parquet + 5 CSV + 5 schema.json). However, src/uk_subsidy_tracker/data/ons_gas.py::download_dataset() raises UnboundLocalError on any network failure: output_path is assigned inside the try block (line 35), but the except handler at line 44 returns it. This is a latent bug that activates precisely when the ONS endpoint is unavailable — the moment the error handler is supposed to preserve the project's 'methodologically bulletproof' promise. Does not block current state (raw files already downloaded) but undermines the reliability story refresh.yml depends on."
    artifacts:
      - path: "src/uk_subsidy_tracker/data/ons_gas.py"
        issue: "Lines 31-44: output_path assigned inside try; except path references unbound variable. No timeout on requests.get()."
    missing:
      - "Assign output_path BEFORE the try block"
      - "Either re-raise or return None/False on failure — never silently return a non-downloaded path"
      - "Add timeout=60 to requests.get() to match the Elexon convention"

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

**Verified:** 2026-04-22T21:00:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (from ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `site/data/manifest.json` is present after build and contains source URL, retrieval timestamp, SHA-256, pipeline git SHA, and `methodology_version` per dataset | VERIFIED | Ran `snapshot.py --dry-run` against live raw data: manifest emitted with 5 datasets; each carries `sources[]` with `upstream_url`/`retrieved_at`/`source_sha256`; top-level `pipeline_git_sha` is 40-char hex (`ade71580…`); `methodology_version: "0.1.0"` matches `counterfactual.METHODOLOGY_VERSION`. |
| 2 | External consumer can follow a URL from `manifest.json` and retrieve a Parquet file and its CSV mirror | VERIFIED (partial) | Snapshot produced 5 Parquet + 5 CSV + 5 schema.json files. All URL fields serialise as absolute `https://` strings. CSV mirror has LF line endings, no BOM, ISO-8601 dates, no index column, preserved float precision (7/7 test_csv_mirror tests pass). **Weakness:** `ons_gas.download_dataset()` has an `UnboundLocalError` on network failure — the fetch reliability promise degrades on the first publisher outage. See gap #2. |
| 3 | `publish/snapshot.py` creates an immutable `site/data/v<date>/` directory on tagged release | VERIFIED | `uv run python -m uk_subsidy_tracker.publish.snapshot --version v2026.04-rc1 --output /tmp/snap --dry-run` exits 0 and emits `manifest.json` + `cfd/` containing 5 parquet + 5 csv + 5 schema.json (16 artefacts total). `versioned_url` field on every Dataset resolves to `https://.../data/v2026.04-rc1/cfd/<grain>.parquet`. |
| 4 | `docs/data/index.md` explains how journalists and academics use the datasets, including citation via versioned snapshot URL | VERIFIED | 144 lines, 9 `##` H2 headings covering the D-27 six-section template plus extras. pandas + DuckDB + R snippets present with absolute `manifest.json` URL. BibTeX template anchored on `releases/tag/v<YYYY.MM>`. Top-level `Data` nav tab present in mkdocs.yml (between Reliability and About). `mkdocs build --strict` exits 0. |
| 5 | GitHub Actions daily refresh workflow (06:00 UTC cron) with per-scheme dirty-check is committed and functional | FAILED (partial) | `.github/workflows/refresh.yml` exists, is valid YAML (`yaml.safe_load` clean), pins all actions to explicit majors, carries least-privilege permissions, invokes `refresh_all` + benchmark floor + 6-module pytest gate + charts + `mkdocs build --strict` + `peter-evans/create-pull-request@v8` + `create-issue-from-file@v6` on failure. Orchestrator runs cleanly (`[cfd] upstream unchanged — skipping refresh`). **However:** the refresh flow is structurally incomplete — see gap #1. Workflow is committed but not fully functional on upstream change. |

**Score:** 4/5 ROADMAP success criteria verified (SC #5 partial).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/uk_subsidy_tracker/publish/__init__.py` | Barrel exports | VERIFIED | Re-exports Manifest/Dataset/Source/build + csv_mirror + snapshot (26 lines). |
| `src/uk_subsidy_tracker/publish/manifest.py` | Pydantic Manifest + build() emitting `site/data/manifest.json` | VERIFIED | 373 lines (plan required ≥120). Contains `class Manifest`, `class Dataset`, `class Source`, `def build`, `GRAIN_SOURCES`, `model_dump(mode="json")`, `sort_keys=True`, `newline="\n"`. |
| `src/uk_subsidy_tracker/publish/csv_mirror.py` | Pinned CSV writer | VERIFIED | 57 lines (plan required ≥40). `lineterminator="\n"`, `date_format`, `index=False`, `float_format=None` all present. |
| `src/uk_subsidy_tracker/publish/snapshot.py` | CLI `--version`/`--output` assembling release-asset tree | VERIFIED | 117 lines (plan required ≥60). Module entry works via `python -m`; dry-run produces 16 artefacts. |
| `src/uk_subsidy_tracker/refresh_all.py` | CI entry-point orchestrator | VERIFIED (partial) | 122 lines (plan required ≥50). Iterates `SCHEMES`, calls `upstream_changed`/`rebuild_derived`/`regenerate_charts`/`validate`, short-circuits on clean state. Missing the Elexon/ONS refetch + sidecar rewrite logic — see gap #1. |
| `src/uk_subsidy_tracker/schemes/cfd/__init__.py` | §6.1 SchemeModule Protocol implementation | VERIFIED | 5.0 KB; contains `DERIVED_DIR`, `upstream_changed`, `refresh`, `rebuild_derived`, `regenerate_charts`, `validate`. |
| `src/uk_subsidy_tracker/schemes/cfd/{cost_model,aggregation,forward_projection,_refresh}.py` | Derived builders + dirty-check | VERIFIED | All 4 files present and non-stub (ranging 2.1–7.8 KB). |
| `src/uk_subsidy_tracker/schemas/cfd.py` | Pydantic row models for 5 grains | VERIFIED | 214 lines (plan required ≥80). 5 BaseModel subclasses + `emit_schema_json`. |
| `tests/test_manifest.py` | 8 manifest tests | VERIFIED | 8/8 passing (round-trip byte-identity, provenance-fields, absolute URLs, SHA match, stable generated_at, methodology match). |
| `tests/test_csv_mirror.py` | 7 CSV-mirror tests | VERIFIED | 7/7 passing (LF line endings, no BOM, column order, no index, ISO-8601 dates, precision preserved). |
| `tests/test_determinism.py` | 10 determinism tests | VERIFIED | 10/10 passing (5 content-identity via `pyarrow.Table.equals()` + 5 writer-identity). |
| `tests/test_schemas.py` (extended) | Raw + Parquet variants | VERIFIED | 10 passing (5 raw + 5 parametrised Parquet). |
| `tests/test_aggregates.py` (extended) | Row-conservation across grains | VERIFIED | 5 passing (2 raw scaffolding + 3 Parquet row-conservation). |
| `tests/test_constants_provenance.py` | SEED-001 Tier 2 drift tripwire | VERIFIED | 13 cases passing. |
| `tests/fixtures/constants.yaml` | 6 constant provenance blocks | VERIFIED | All 6 keys present; every `test_yaml_value_matches_live` passes. |
| `data/raw/<publisher>/<file>` | 5 raw files migrated | VERIFIED | 5 files present at new paths; 5 sibling `.meta.json` sidecars with valid 64-char SHA-256 + `upstream_url` + `retrieved_at` + `backfilled_at`. |
| `scripts/backfill_sidecars.py` | One-shot helper | VERIFIED | 89 lines; parses cleanly. |
| `.github/workflows/refresh.yml` | Daily cron workflow | VERIFIED | 89 lines; `yaml.safe_load` parses; pinned actions; least-privilege permissions; invokes refresh_all + gates + create-pull-request + create-issue-on-failure. |
| `.github/workflows/deploy.yml` | Tag-triggered release workflow | VERIFIED | 65 lines; `yaml.safe_load` parses; tag-format regex validation; invokes snapshot.py + softprops/action-gh-release@v2. |
| `.github/refresh-failure-template.md` | Issue body template | VERIFIED | File exists (1.1 KB). |
| `docs/data/index.md` | 6-section how-to-use-our-data page | VERIFIED | 144 lines, 9 H2 headings (plan required ≥120 lines, 6 sections — exceeds both). `manifest.json`, `read_parquet`, `versioned` grep-present. |
| `docs/about/citation.md` | Versioned-snapshot URL pattern | VERIFIED | Contains "Versioned snapshots" + "Citing a specific data snapshot" H2 sections; `releases/tag` pattern present. |
| `mkdocs.yml` | `Data` top-level nav entry | VERIFIED | `- Data: data/index.md` on line 83, between Reliability and About. |
| `tests/fixtures/benchmarks.yaml` | Disposition C audit note | VERIFIED | Summary confirms header carries the 2026-04-22 audit block; `lccc_self: []` preserved per user decision. |
| `.gitignore` | `data/derived/` ignored; `site/data/` tracked | VERIFIED | `data/derived/` in .gitignore; explicit per-mkdocs-subtree pattern preserves `site/data/` tracking. |
| `pyproject.toml` | pyarrow ≥ 24.0.0 + duckdb ≥ 1.5.2 | VERIFIED | Both resolved in `uv.lock` at 24.0.0 + 1.5.2. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|------|------|--------|---------|
| `publish/manifest.py` | `data/raw/**/*.meta.json` | Walks sidecars for upstream_url/retrieved_at/source_sha256 | VERIFIED | Emitted manifest shows every Dataset.sources[].upstream_url + retrieved_at populated from sidecars; source_sha256 re-computed from raw file per W-05 mitigation. |
| `publish/manifest.py` | `data/derived/cfd/*.parquet` | Walks derived_dir, one Dataset per Parquet | VERIFIED | 5 Datasets in emitted manifest, one per grain; row_counts match Plan 03 reference (3460/11/52/33/68). |
| `publish/manifest.py` | `counterfactual.METHODOLOGY_VERSION` | Top-level manifest.methodology_version | VERIFIED | Emitted manifest: `"methodology_version": "0.1.0"` matches module constant. |
| `publish/manifest.py` | `mkdocs.yml::site_url` | Line-scan for `site_url:` | VERIFIED | All emitted URLs resolve to `https://richardjlyon.github.io/uk-subsidy-tracker/...`. (See WR-03 in Review — line-scan is fragile; not a blocker but noted.) |
| `publish/csv_mirror.py` | `data/derived/cfd/*.parquet` | `pq.read_table(...).to_pandas().to_csv(...)` | VERIFIED | Dry-run produced 5 CSV mirrors with correct column order and ISO-8601 dates; all 7 test_csv_mirror tests pass. |
| `refresh_all.py` | `schemes/cfd/__init__.py` | `from uk_subsidy_tracker.schemes import cfd` + calls | VERIFIED (partial) | Module import and `upstream_changed`/`rebuild_derived`/`regenerate_charts`/`validate` calls all wired. **Missing:** refresh path does not re-fetch Elexon/ONS nor rewrite sidecars — gap #1. |
| `.github/workflows/refresh.yml` | `uk_subsidy_tracker.refresh_all` | `uv run --frozen python -m uk_subsidy_tracker.refresh_all` | VERIFIED | Step present at line 49; orchestrator exits 0 on clean state. |
| `.github/workflows/deploy.yml` | `uk_subsidy_tracker.publish.snapshot` | `uv run --frozen python -m ... snapshot --version ... --output snapshot-out/` | VERIFIED | Step present at line 47-50; local smoke-test exits 0. |
| `.github/workflows/refresh.yml` | `.github/refresh-failure-template.md` | `content-filepath` on peter-evans/create-issue-from-file@v6 | VERIFIED | Step present at line 85-89. |

### Data-Flow Trace (Level 4)

| Artifact | Data variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `publish/manifest.py::build()` | `manifest` | Walks `data/raw/**/*.meta.json` + `data/derived/cfd/*.parquet` + `counterfactual.METHODOLOGY_VERSION` + `subprocess.run(['git', 'rev-parse', 'HEAD'])` | Yes — DB-equivalent walks real files; `pipeline_git_sha` populated via subprocess | FLOWING |
| `publish/csv_mirror.py::build()` | CSV rows | `pq.read_table(parquet).to_pandas()` | Yes — reads the just-emitted Parquet files | FLOWING |
| `publish/snapshot.py::build()` | Manifest + CSV + Parquet tree | Calls `cfd.rebuild_derived(output_dir)` + `csv_mirror.build(...)` + `manifest_mod.build(...)` | Yes — end-to-end rebuild from raw state | FLOWING |
| `schemes/cfd/cost_model.py::build_station_month()` | 3,460 station-month rows | `load_lccc_dataset("Actual CfD Generation...")` + `compute_counterfactual(...)` | Yes — verified via pyarrow.Table.equals in test_determinism | FLOWING |
| `schemes/cfd/aggregation.py::build_annual_summary()` | 11 annual rows | `pq.read_table(derived/station_month.parquet)` + `compute_counterfactual` daily | Yes — verified via test_aggregates row-conservation | FLOWING |
| `schemes/cfd/forward_projection.py::build_forward_projection()` | 68 forward rows | `load_lccc_dataset("CfD Contract Portfolio Status")` + `int(gen['Settlement_Date'].max().year)` | Yes — deterministic anchor from raw data, not clock | FLOWING |
| `schemes/cfd/_refresh.py::upstream_changed()` | bool | Walks `_RAW_FILES` + compares live SHA vs sidecar SHA | Yes — ran locally, returned False (matches expected) | FLOWING |
| `schemes/cfd/_refresh.py::refresh()` | (side effects — downloads) | `download_lccc_datasets(config)` | **Partial — LCCC only** | **STATIC / DISCONNECTED** for Elexon + ONS (gap #1) |
| `refresh_all.py::refresh_scheme()` | bool | Delegates to `scheme.refresh()` | Partial — LCCC data flows; sidecar updates do not | **DISCONNECTED for sidecar-advance data path** (gap #1) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full test suite is green | `uv run pytest tests/ -q` | `69 passed, 4 skipped in 6.17s` | PASS |
| Manifest build produces correct contract | `python -c "from uk_subsidy_tracker.publish import manifest; manifest.build(version='latest', derived_dir=Path('data/derived/cfd'), raw_dir=Path('data/raw'), output_path=...)"` | 5 datasets; all required fields present; 40-char pipeline_git_sha; methodology_version="0.1.0"; all URLs https | PASS |
| Snapshot CLI produces release-asset tree | `uv run python -m uk_subsidy_tracker.publish.snapshot --version v2026.04-rc1 --output /tmp/snap --dry-run` | Exit 0; 16 artefacts (1 manifest.json + 5 parquet + 5 csv + 5 schema.json) | PASS |
| Refresh orchestrator runs on clean state | `uv run python -m uk_subsidy_tracker.refresh_all` | `[cfd] upstream unchanged — skipping refresh` + `no upstream changes; skipping manifest rebuild` | PASS |
| Refresh orchestrator re-fetches Elexon/ONS on dirty state | (mocked — inspected code path) | Code path never calls Elexon or ONS downloaders | **FAIL** (gap #1) |
| Refresh writes sidecars after download | (mocked — inspected code path) | No sidecar writer call in refresh_all.py nor in schemes/cfd/_refresh.py; only scripts/backfill_sidecars.py writes | **FAIL** (gap #1) |
| Determinism invariant holds | `uv run pytest tests/test_determinism.py` | 10/10 passing | PASS |
| Manifest round-trip byte-identical | `uv run pytest tests/test_manifest.py::test_manifest_roundtrip_byte_identical` | PASS | PASS |
| CSV mirror quality invariants | `uv run pytest tests/test_csv_mirror.py` | 7/7 passing | PASS |
| MkDocs strict build | `uv run mkdocs build --strict` | Exit 0; built in 0.35s | PASS |
| YAML workflow parse | `python -c "import yaml; yaml.safe_load(open('.github/workflows/refresh.yml')); yaml.safe_load(open('.github/workflows/deploy.yml'))"` | OK | PASS |
| ons_gas download error path | (code review) | `output_path` referenced in `except` before assignment (line 44 refs value first bound at line 35 inside try) | **FAIL** (gap #2) |

### Requirements Coverage

Cross-referenced against `.planning/REQUIREMENTS.md` traceability table and PLAN frontmatter `requirements:` fields:

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|----------------|-------------|--------|----------|
| PUB-01 | 04-04 | `publish/manifest.py` builds `site/data/manifest.json` with provenance | SATISFIED | Module exists; `build()` runs; all required fields present in emitted manifest. |
| PUB-02 | 04-04 | `publish/csv_mirror.py` writes CSV alongside every Parquet | SATISFIED | 5 CSV siblings produced by snapshot.py; 7/7 quality tests pass. |
| PUB-03 | 04-04, 04-05 | `publish/snapshot.py` creates versioned snapshot on tag release | SATISFIED | Snapshot CLI + `.github/workflows/deploy.yml` tag trigger + release-asset upload all wired. |
| PUB-04 | 04-06 | `docs/data/index.md` explains journalist/academic use | SATISFIED | 144-line page with all six D-27 sections + three-language snippets. |
| PUB-05 | 04-02, 04-03, 04-04 | Three-layer pipeline operational end-to-end for CfD | SATISFIED (with structural concern) | `data/raw/` → `data/derived/` → `site/data/` paths all produce correct output. Refresh-loop gap (see gap #1) affects robustness but not the current operational state. |
| PUB-06 | 04-04, 04-06 | External consumer fetches manifest + follows URL + retrieves Parquet/CSV | SATISFIED | Manifest URLs are absolute; snapshot CLI produces files at those locations. |
| GOV-02 | 04-02, 04-03, 04-04 | manifest.json exposes full provenance per dataset | SATISFIED | Source URL + retrieval timestamp + source SHA-256 + pipeline git SHA + methodology version all present on every Dataset. |
| GOV-03 | 04-05 | Daily refresh CI workflow with per-scheme dirty-check | PARTIAL | Workflow committed; orchestrator runs; per-scheme dirty-check exists; **but refresh logic incomplete** (gap #1). |
| GOV-04 | (seed) | Methodology versioning | SATISFIED | Plan 01 confirmed `METHODOLOGY_VERSION` propagation + SEED-001 Tier 2 drift tripwire. |
| GOV-06 | 04-04, 04-05, 04-06 | Versioned-snapshot URL citability | SATISFIED | `versioned_url` on every Dataset; deploy.yml uploads release assets; docs/about/citation.md + docs/data/index.md document pattern. |
| TEST-02 | 04-03 | Pydantic schema validation on derived Parquet | SATISFIED | 5 parametrised Parquet-variant tests pass. |
| TEST-03 | 04-03 | Row-conservation across grain rollups | SATISFIED | 3 Parquet row-conservation tests pass. |
| TEST-05 | 04-03 | Byte-identical Parquet rebuild determinism | SATISFIED | 10/10 `tests/test_determinism.py` pass via `pyarrow.Table.equals()`. |

**No orphaned requirements** — every ID from the phase's declared list appears in at least one plan's `requirements:` field AND is satisfied (or partial with explicit gap) by delivered work.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/uk_subsidy_tracker/data/ons_gas.py` | 31-44 | `output_path` bound inside `try` block; `except` returns unbound variable | Blocker (for GOV-03 robustness) | On any ONS endpoint failure, download_dataset() raises `UnboundLocalError` instead of graceful degradation. Exercised precisely when the refresh workflow would need to tolerate upstream flakiness. |
| `src/uk_subsidy_tracker/schemes/cfd/_refresh.py` | 53-67 | Comment: "Elexon + ONS refresh delegated to Plan 04-05's refresh_all.py orchestrator" — but refresh_all.py does not pick up the delegation | Warning | Structural incompleteness — two of five raw sources never re-fetched on a real refresh. |
| `src/uk_subsidy_tracker/refresh_all.py` | 42-87 | No sidecar-rewrite code path anywhere in the refresh flow | Warning | After a real upstream change, sidecar SHA stays stale and `upstream_changed()` returns True perpetually; `manifest.generated_at` frozen at backfill date. |
| `.github/workflows/{refresh,deploy}.yml` | multiple | Actions pinned to floating majors (`@v8`, `@v2`, `@v5`) — not immutable SHAs | Info (accepted) | Supply-chain concern; accepted by plan rationale ("maintenance burden > supply-chain delta for open-data project"). |
| `src/uk_subsidy_tracker/publish/manifest.py` | 172-199 | `_site_url()` line-scan fragile on alternative mkdocs.yml formatting | Info | WR-03 in Review — not a blocker; `SITE_URL` env var can override in CI. |
| `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py` | 99 | `int(gen["Settlement_Date"].max().year)` has no defensive fallback for empty/all-NaT data | Info | WR-04 in Review; current data has dates so no runtime impact. |

No TODO/FIXME/PLACEHOLDER comments found in production code. No empty return stubs. No hardcoded `=[]` or `={}` that flow to rendering. Plotting and data layers operate on real pandas DataFrames with real row counts (3,460 / 11 / 52 / 33 / 68 rows per grain, matching Plan 03 reference counts).

### Human Verification Required

See `human_verification:` entries in frontmatter. Three items:

1. Manual GitHub Actions `workflow_dispatch` trigger of refresh.yml (requires user dashboard setup first).
2. Test-tag push to exercise deploy.yml + confirm release asset retrieval resolves with byte-identical SHA-256.
3. Visual inspection of `docs/data/index.md` rendered via `mkdocs serve`.

### Gaps Summary

**Gap #1 (structural — undermines SC #5 and GOV-03):** The refresh flow is wired at the orchestration layer but structurally incomplete at the data layer. `scheme.refresh()` only re-fetches LCCC; Elexon and ONS downloaders are never invoked on a refresh run. No code path writes `.meta.json` sidecars after a download — that logic lives solely in the one-shot `scripts/backfill_sidecars.py`. On the first real upstream change, the daily workflow will either produce empty diffs or perpetually report "upstream changed" because sidecar SHA stays stale, and `manifest.generated_at` (sourced from `max(sidecar.retrieved_at)`) will never advance. The *current* static-state manifest is correct; the *dynamic* refresh claim in the phase goal is fragile.

**Gap #2 (code bug — affects PUB-05/GOV-03 error resilience):** `ons_gas.download_dataset()` has an `UnboundLocalError` on any network failure because `output_path` is assigned inside the `try` block but returned in the `except` handler. This activates exactly when the ONS publisher is unavailable — the moment the project's "bulletproof" promise is tested. Fix is trivial (three-line change) but the exception path is currently untested.

Both gaps are remediable without architectural change; neither invalidates the current static state of the published manifest or the snapshot CLI. However, they directly undermine the "daily refresh ... functional" wording of ROADMAP Success Criterion #5 and the durability of GOV-03.

**Grouping:** Both gaps share a common root cause — the refresh/download layer was designed for atomic commit discipline and sidecar provenance but never closed the loop between download + sidecar rewrite + failure tolerance. A single focused gap-closure plan covering (a) an end-to-end fetch helper that handles LCCC/Elexon/ONS uniformly and writes sidecars atomically, (b) the `ons_gas` error-path fix, and (c) a refresh-loop invariant test would close both.

### Deferred Items

None. All phase-scoped work was either delivered or surfaced as an actionable gap; nothing was explicitly punted to a later phase in ROADMAP.md.

---

*Verified: 2026-04-22T21:00:00Z*
*Verifier: Claude (gsd-verifier)*
