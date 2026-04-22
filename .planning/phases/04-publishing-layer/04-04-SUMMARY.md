---
phase: 04-publishing-layer
plan: 04
subsystem: publishing-layer

tags: [publishing-layer, manifest, csv-mirror, snapshot, refresh-orchestration, pub-01, pub-02, pub-03, pub-06, gov-02, gov-06]

# Dependency graph
requires:
  - phase: 04-publishing-layer-01
    provides: "pyarrow>=24.0.0 (pq.read_metadata + pq.read_table + Table.to_pandas used here); SEED-001 Tier-2 drift tripwire guards METHODOLOGY_VERSION from silent drift — the same constant that flows into manifest.json::methodology_version."
  - phase: 04-publishing-layer-02
    provides: "data/raw/<publisher>/<file>.meta.json sidecars carrying retrieved_at + upstream_url + sha256. manifest.py walks these to populate datasets[].sources[]; generated_at sources from max(retrieved_at across sidecars) for Pitfall-3 stability."
  - phase: 04-publishing-layer-03
    provides: "cfd.rebuild_derived(output_dir) emits 5 Parquet + 5 schema.json siblings deterministically (0.74s end-to-end, methodology_version column on every row). snapshot.py + refresh_all.py invoke it directly; manifest.py walks the derived_dir."
provides:
  - "src/uk_subsidy_tracker/publish/ package — the publishing contract. manifest.py (Pydantic Manifest/Dataset/Source models + build()), csv_mirror.py (pinned-pandas-args sibling CSV writer), snapshot.py (CLI assembling versioned release-asset directory)."
  - "src/uk_subsidy_tracker/refresh_all.py — CI entry point for Plan 04-05's .github/workflows/refresh.yml. Walks SCHEMES tuple; per-scheme dirty-check → refresh → rebuild → charts → validate → publish. Short-circuits when nothing upstream changed (Pitfall 3)."
  - "The D-12 chain is now closed end-to-end: counterfactual.METHODOLOGY_VERSION → DataFrame column (compute_counterfactual) → Parquet column (rebuild_derived) → cross-check (schemes/cfd/validate Check 3) → manifest top-level field (manifest.py). External consumers read `methodology_version` at the top of manifest.json and know the exact formula revision that produced every headline number."
  - "15 new passing tests (8 manifest + 7 csv_mirror). Full suite 69 passed + 4 skipped (+15 vs 04-03 baseline, zero regressions)."
affects:
  - 04-05-workflows-refresh-deploy   # refresh.yml calls `uv run python -m uk_subsidy_tracker.refresh_all`; deploy.yml calls `uv run python -m uk_subsidy_tracker.publish.snapshot --version ${{ github.ref_name }} --output snapshot-out/` then uploads the directory as release assets via softprops/action-gh-release@v2
  - 04-06-docs-and-benchmark-floor   # docs/data/index.md journalist snippets read manifest.json then follow URLs; CITATION.cff references versioned_url pattern
  - 05+                               # every future scheme module copies this publish/ package shape; their schemes/<name>/__init__.py gets appended to refresh_all.SCHEMES with no other refactor

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pinned JSON serialisation (D-08): `json.dumps(manifest.model_dump(mode='json'), sort_keys=True, indent=2, ensure_ascii=False) + '\\n'` with `write_text(..., encoding='utf-8', newline='\\n')`. Pydantic v2 does NOT support sort_keys on model_dump_json() (issue #7424); the stdlib path is the only byte-stable option. test_manifest_roundtrip_byte_identical guards against drift."
    - "upstream_url: str (not HttpUrl) — Pitfall 6. Pydantic v2's HttpUrl has varied serialisation across minor versions (plain string vs wrapped object depending on model_dump mode). For a public contract that external consumers parse, plain str with no pattern validator is the lowest-surprise option. test_manifest_urls_are_strings asserts raw-JSON type."
    - "Content-addressed generated_at (Pitfall 3): `generated_at = max(retrieved_at across *.meta.json sidecars)` not `datetime.now()`. Two consecutive manifest.build() calls with the same raw state produce byte-identical manifest.json — the daily refresh PR is non-noisy (empty diff when nothing upstream changed). refresh_all.py also short-circuits before build() via upstream_changed(); the field-level stability is the safety net."
    - "Per-grain provenance table (B-02): GRAIN_SOURCES: dict[str, list[str]] maps each derived grain to its raw-file inputs (not 'every raw file to every grain'). forward_projection's sources[] correctly lists only cfd-contract-portfolio-status; by_allocation_round lists the two LCCC files but not Elexon/ONS. Phase 5+ schemes add their own GRAIN_SOURCES tables in their own manifest helpers (cross-scheme combined/ tables come later)."
    - "Raw-file SHA re-computed on build (W-05): `_source_for_raw()` calls `_sha256(Path(raw_path))` and warns-but-emits-live on sidecar disagreement. Raw file is truth, sidecar is metadata — prevents a tampered sidecar from silently entering the public manifest."
    - "Pinned pandas.to_csv args (D-10): index=False, encoding='utf-8', lineterminator='\\n', date_format='%Y-%m-%dT%H:%M:%S', float_format=None, na_rep=''. test_csv_mirror.py byte-checks each: LF line endings, no UTF-8 BOM, column order matches Parquet, dates are ISO-8601, float precision survives at 1e-9 rel_tol."
    - "Explicit mkdocs-build path ignores in .gitignore: Git cannot re-include paths under an ignored directory, so `!site/data/` does not carve site/data/ out of `site/`. Replaced blanket `site/` with explicit `/site/{assets,stylesheets,search,themes,methodology,charts,about}/` + `/site/{index.html,404.html,sitemap.xml{,.gz}}`. site/data/latest/* and site/data/manifest.json now tracked for daily refresh commit-back (D-15). Verified via mkdocs build --strict + git check-ignore probe that mkdocs outputs are still ignored."

key-files:
  created:
    - "src/uk_subsidy_tracker/publish/__init__.py — 26 lines; barrel re-exporting Manifest/Dataset/Source/build from manifest.py and csv_mirror + snapshot submodules."
    - "src/uk_subsidy_tracker/publish/manifest.py — 364 lines. Three Pydantic BaseModels (Manifest/Dataset/Source, ARCHITECTURE §4.3 verbatim, D-07), GRAIN_SOURCES/GRAIN_TITLES/GRAIN_DESCRIPTIONS module-level tables, 6 helper functions (_git_sha, _sha256, _site_url with SITE_URL env-override, _read_methodology_version with D-12 chain comment, _latest_retrieved_at for Pitfall-3 stability, _source_for_raw, _versioned_segment, _assemble_dataset_entries), top-level build() entry. Deterministic JSON write: json.dumps(sort_keys=True, indent=2) + LF newline + trailing newline."
    - "src/uk_subsidy_tracker/publish/csv_mirror.py — 60 lines; write_csv_mirror(parquet_path, csv_path) + build(derived_dir) -> list[Path]. Six pinned pandas args (D-10)."
    - "src/uk_subsidy_tracker/publish/snapshot.py — 116 lines; build(version, output_dir) + _parse_args + main CLI entry. --version, --output, --dry-run flags. Module-import smoke + python -m entry both work."
    - "src/uk_subsidy_tracker/refresh_all.py — 113 lines. SCHEMES tuple (currently just ('cfd', cfd); Phase 5+ appends). refresh_scheme(name, module) → bool (True iff refreshed). publish_latest(version) copies derived/<scheme>/* → site/data/latest/<scheme>/, writes CSV mirrors, rebuilds manifest.json. main() argparse entry; short-circuits to exit 0 with 'no upstream changes' on clean state (Pitfall 3)."
    - "tests/test_manifest.py — 248 lines, 8 tests. Module-scoped fixture copies data/raw/ into tmp + cfd.rebuild_derived(tmp) + manifest.build(tmp/site/data/manifest.json)."
    - "tests/test_csv_mirror.py — 172 lines, 7 tests. Module-scoped fixture rebuilds derived + runs csv_mirror.build()."
    - ".planning/phases/04-publishing-layer/04-04-SUMMARY.md (this file)"
  modified:
    - ".gitignore — replaced blanket `site/` ignore with explicit per-mkdocs-subtree patterns to carve out site/data/ for the daily refresh commit-back (D-15)."
    - "CHANGES.md — [Unreleased] ### Added now leads with src/uk_subsidy_tracker/publish/ package (manifest.py, csv_mirror.py, snapshot.py) + refresh_all.py + tests/test_manifest.py + tests/test_csv_mirror.py bullets (all cite controlling D-numbers + Pitfall IDs + requirement IDs). [Unreleased] ### Changed gains .gitignore entry explaining the site/ restructure."

key-decisions:
  - "site_url loader line-scans mkdocs.yml rather than yaml.safe_load: mkdocs.yml carries Python-tag custom constructors (!!python/name:material.extensions.emoji.twemoji) which yaml.safe_load rejects with a ConstructorError. yaml.FullLoader would execute arbitrary Python tags — unsafe. A top-level line-scan for `site_url:` is safer than FullLoader and cheaper than subclassing SafeLoader to register benign material tags. Only one line is needed; grep-visible to reviewers. Auto-fixed (Rule 1) when test_manifest_build_writes_file first surfaced the ConstructorError."
  - "Raw-file sha256 re-computed in manifest.build(), sidecar value NOT trusted blindly: W-05 mitigation. _source_for_raw() calls _sha256(Path(raw_path)) on the on-disk raw file and logs.warning(...) on sidecar disagreement but emits the live hash into the manifest. Raw file is truth; sidecar is metadata. A tampered sidecar cannot enter the public contract silently."
  - "GRAIN_SOURCES is a module-level dict, not a function call or a generator: B-02 mitigation. forward_projection's sources list must NOT include Elexon system-prices (irrelevant to the projection). Hard-coding per-grain in a grep-visible dict prevents 'add a source to one grain accidentally adds to all' drift. Phase 5+ schemes maintain their own tables."
  - ".gitignore Rule-1 fix: Git does NOT support re-including files under an ignored directory. The plan's Step 4A suggested adding `!site/data/` as an exception line, but `git check-ignore -v site/data/manifest.json` confirmed this is silently ineffective. Replaced blanket `site/` with explicit `/site/{assets,stylesheets,search,themes,methodology,charts,about}/` plus `/site/{index.html,404.html,sitemap.xml{,.gz}}`. Verified post-edit via `mkdocs build --strict` + probe: mkdocs outputs still ignored; site/data/manifest.json NOT ignored. This is a permanent posture change — Phase 5+ schemes publish to `site/data/latest/<scheme>/` and inherit this tracking automatically."
  - "Pydantic v2 HttpUrl avoided throughout the public manifest: upstream_url, parquet_url, csv_url, schema_url, versioned_url, methodology_page all declared as `str`. HttpUrl's serialisation has varied across Pydantic v2 minor versions (sometimes `str`, sometimes `Url(...)` object); `str` + optional regex pattern is the lowest-surprise option for an external contract. test_manifest_urls_are_strings runs a raw-JSON isinstance check on every URL as the tripwire."
  - "generated_at sources from max(retrieved_at across sidecars), NOT datetime.now(): Pitfall 3. Two consecutive manifest.build() calls with the same raw state produce byte-identical output. refresh_all.py also short-circuits via cfd.upstream_changed() before calling manifest.build() — the field-level stability is a safety net. test_manifest_generated_at_stable_when_no_upstream_change is the structural guard."

patterns-established:
  - "Phase 5+ scheme publishing template: every future scheme module (RO, FiT, SEG, Constraint, Capacity, BM, Grid) inherits the same pipeline: `from uk_subsidy_tracker.publish import manifest, csv_mirror`, its scheme/__init__.py exposes rebuild_derived(output_dir), snapshot.py and refresh_all.py pick it up with a one-line SCHEMES tuple addition. No cross-scheme plumbing required for the publishing step until Phase 6's combined/ cross-scheme grains."
  - "D-12 chain module-level documentation: manifest.py's module docstring contains the verbatim D-12 chain (METHODOLOGY_VERSION → DataFrame column → Parquet column → validate() check → manifest top-level field). Grep-visible documentation of the provenance chain; future readers see the whole end-to-end contract without chasing five files."
  - "Snapshot assembly does rebuild_derived into output_dir directly rather than copying from data/derived/: the snapshot is self-contained and cannot accidentally inherit stale content from a local derived tree. deploy.yml's tag-push release-asset upload gets a fresh rebuild at release time — bit-identical output from identical raw state (D-21)."

requirements-completed:
  - PUB-01    # publish/manifest.py builds site/data/manifest.json with provenance
  - PUB-02    # publish/csv_mirror.py writes sibling CSV for every published Parquet
  - PUB-03    # publish/snapshot.py creates versioned snapshot directory for tagged release upload
  - PUB-05    # three-layer pipeline operational end-to-end for CfD (raw → derived → published; refresh_all orchestrates)
  - PUB-06    # external consumer can fetch manifest.json → follow absolute URL → retrieve Parquet+CSV+schema.json with provenance
  - GOV-02    # provenance per dataset: url, retrieved_at, source_sha256, pipeline_git_sha, methodology_version (all five fields present on every Dataset entry)
  - GOV-06    # snapshot URL portion — versioned_url citation anchor (`f"{base}/data/{version}/cfd/{grain}.parquet"`) present on every Dataset. CITATION.cff portion was closed in Phase 1; this completes GOV-06 end-to-end.

# Metrics
duration: 12min
completed: 2026-04-22
---

# Phase 4 Plan 04: Publishing-Layer Manifest Summary

**Shipped the Pydantic-typed `manifest.json` contract (D-07 verbatim) with absolute URLs (D-09), byte-stable serialisation (D-08), per-grain provenance (B-02), content-addressed `generated_at` (Pitfall 3), and re-computed raw-file SHA-256 (W-05); sibling CSV mirrors with pinned pandas args (D-10); versioned-snapshot CLI for release-asset upload (D-13, D-14); and the per-scheme dirty-check orchestrator that makes `uv run python -m uk_subsidy_tracker.refresh_all` the "one command" that reproduces every published number from `git clone + uv sync`.** 15 new tests; 0 regressions; 5/5 success criteria green.

## Performance

- **Duration:** ~12 min
- **Started:** 2026-04-22T23:39:58Z
- **Completed:** 2026-04-22T23:51:24Z
- **Tasks:** 5 completed (5/5)
- **Files changed:** 9 (7 new + 2 modified)

## Accomplishments

- **The publishing contract is real.** `src/uk_subsidy_tracker/publish/manifest.py::build()` assembles a `Manifest` Pydantic model whose shape is ARCHITECTURE §4.3 verbatim (D-07), serialises it via `json.dumps(model.model_dump(mode="json"), sort_keys=True, indent=2, ensure_ascii=False) + "\n"`, and writes to disk with explicit `encoding="utf-8", newline="\n"`. Round-trip byte-identity is test-enforced — `test_manifest_roundtrip_byte_identical` reads the written file, calls `Manifest.model_validate_json`, re-emits with identical settings, and asserts byte-equality. Any Pydantic minor-version drift that changes URL or datetime serialisation will fail this test on the next CI run.

- **Pitfall 3 (generated_at stability) mitigated structurally.** `generated_at` sources from `max(retrieved_at across *.meta.json sidecars)`, not `datetime.now()`. Two consecutive `manifest.build()` calls on the same raw state produce byte-identical manifest.json — the daily refresh PR is non-noisy when nothing upstream changed. `refresh_all.py` also short-circuits via `cfd.upstream_changed()` before calling `manifest.build()`; the field-level stability is the safety net. `test_manifest_generated_at_stable_when_no_upstream_change` is the structural guard.

- **Pitfall 6 (HttpUrl drift) mitigated structurally.** Every URL field on every Pydantic model is declared as `str`, not `HttpUrl`. `test_manifest_urls_are_strings` asserts raw-JSON `isinstance(ds[key], str)` on every URL in every dataset — catches any future Pydantic upgrade that leaks a wrapped object into the serialised manifest.

- **W-05 (raw-file SHA tampering) mitigated structurally.** `_source_for_raw()` re-computes `_sha256(Path(raw_path))` on the on-disk raw file and `logging.warning(...)` on sidecar disagreement but emits the live hash into the manifest. A tampered sidecar cannot enter the public contract silently. The test `test_manifest_sha256_matches_parquet` adds the derived-side integrity check.

- **B-02 (per-grain provenance) mitigated structurally.** `GRAIN_SOURCES: dict[str, list[str]]` at module level maps each derived grain to its raw-file inputs: `forward_projection`'s sources list only `cfd-contract-portfolio-status.csv`; `by_allocation_round` lists the two LCCC files but NOT Elexon/ONS. Grep-visible discipline — a reviewer sees the per-grain provenance at a glance instead of tracing generator logic.

- **Three-layer pipeline is end-to-end reproducible from one command.** `uv run python -m uk_subsidy_tracker.refresh_all` walks `SCHEMES`, per-scheme dirty-checks, refreshes if anything changed, rebuilds derived Parquet + CSV mirrors + manifest.json. On clean state (current local run) it short-circuits with "no upstream changes; skipping manifest rebuild" and exits 0 in ~150ms. PUB-05 is now operational end-to-end for CfD.

- **Snapshot CLI produces a self-contained release-asset tree.** `uv run python -m uk_subsidy_tracker.publish.snapshot --version v2026.04-rc1 --output /tmp/snap --dry-run` emits `/tmp/snap/manifest.json` + `/tmp/snap/cfd/` with 5 Parquet + 5 CSV + 5 schema.json files (16 total artefacts). Plan 04-05's `deploy.yml` will call this with `${{ github.ref_name }}` on tag push and upload everything under `output_dir` as release assets via `softprops/action-gh-release@v2`.

## First manifest.json emitted (top excerpt)

The `snapshot --dry-run` produced this manifest for tag `v2026.04-rc1`:

```json
{
  "datasets": [
    {
      "csv_url": "https://richardjlyon.github.io/uk-subsidy-tracker/data/latest/cfd/annual_summary.csv",
      "grain": "year",
      "id": "cfd.annual_summary",
      "methodology_page": "https://richardjlyon.github.io/uk-subsidy-tracker/methodology/gas-counterfactual/",
      "parquet_url": "https://richardjlyon.github.io/uk-subsidy-tracker/data/latest/cfd/annual_summary.parquet",
      "row_count": 11,
      "schema_url": "https://richardjlyon.github.io/uk-subsidy-tracker/data/latest/cfd/annual_summary.schema.json",
      "sha256": "19fc6636504c77736fabc8e2c1aefba4611721dd01b5a34a6967734a44510eca",
      "sources": [
        {
          "name": "lccc.actual-cfd-generation",
          "retrieved_at": "2026-04-22T00:00:00Z",
          "source_sha256": "7f55b0b347b9a4a7eef0edbf56feaf718af9cbc261a9f31e998934af736b3c51",
          "upstream_url": "https://dp.lowcarboncontracts.uk/datastore/dump/37d1bef4-55d7-4b8e-8a47-1d24b123a20e"
        },
        ...
      ],
      "versioned_url": "https://richardjlyon.github.io/uk-subsidy-tracker/data/v2026.04-rc1/cfd/annual_summary.parquet"
    },
    ...
  ],
  "generated_at": "2026-04-22T00:00:00Z",
  "methodology_version": "0.1.0",
  "pipeline_git_sha": "<40-char hex>",
  "version": "v2026.04-rc1"
}
```

All URLs are absolute (D-09, verified: every URL starts `https://`). `methodology_version = "0.1.0"` matches `counterfactual.METHODOLOGY_VERSION` exactly (D-12 chain end). `pipeline_git_sha` is a 40-char hex (GOV-02). Every `sources[].source_sha256` is the freshly-computed hash of the on-disk raw file at build time (W-05 mitigation).

## pipeline_git_sha populated via subprocess on CI and locally

`_git_sha()` runs `subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True, cwd=PROJECT_ROOT)`. On this local run: 40-char hex returned. On CI (where the job runs inside the checked-out repo): same pattern, no shell injection surface (no `shell=True`), no command-line escaping needed. `deploy.yml` checks out the commit at `${{ github.sha }}`; `rev-parse HEAD` returns that SHA verbatim — GOV-02 provenance binding is byte-stable between local and CI builds.

## Pydantic v2 serialisation surprises encountered

One encountered during implementation, resolved at author-time:

1. **Pydantic v2 `model_dump_json(sort_keys=True)` is not supported** — Pydantic issue #7424. The correct pattern is `json.dumps(model.model_dump(mode="json"), sort_keys=True, indent=2)`. The RESEARCH document's Pattern 2 called this out; `manifest.py` uses the stdlib path throughout, and `test_manifest_roundtrip_byte_identical` is the regression guard.
2. **Datetime serialisation mode matters.** `model.model_dump()` returns raw `datetime` objects which `json.dumps` cannot serialise without a custom encoder. `model_dump(mode="json")` emits ISO-8601 strings, which the stdlib `json.dumps` handles directly. Every datetime in the manifest (`generated_at`, `retrieved_at`) lands as ISO-8601 "Z"-terminated string (e.g. `"2026-04-22T00:00:00Z"`) after Pydantic normalises the UTC-aware datetime.

**No HttpUrl surprise** because the plan anticipated Pitfall 6 and declared every URL as `str` from the outset. The round-trip test would have caught it if someone had used `HttpUrl`.

## Row counts per dataset (cross-check against Plan 03 summary)

From the snapshot manifest `datasets[].row_count` (matches Plan 04-03 §"Row Counts per Grain"):

| Grain | Row count (this plan) | Plan 03 reference | Match |
|---|---|---|---|
| station_month | 3,460 | 3,460 | YES |
| annual_summary | 11 | 11 | YES |
| by_technology | 52 | 52 | YES |
| by_allocation_round | 33 | 33 | YES |
| forward_projection | 68 | 68 | YES |
| **Total** | **3,624** | **3,624** | YES |

Identical — confirms `snapshot.build()`'s rebuild of the derived layer into the snapshot directory is content-equivalent to `cfd.rebuild_derived()` against the canonical `data/derived/cfd/`. TEST-05 (determinism) already asserted this at the Parquet level; the manifest row counts are an independent cross-check at the publishing-layer boundary.

## Task Commits

Each task was committed atomically:

1. **Task 1: publish/manifest.py + test_manifest.py (RED→GREEN)** — `2e90d11` (feat)
2. **Task 2: publish/csv_mirror.py + test_csv_mirror.py** — `f6afd73` (feat)
3. **Task 3: publish/snapshot.py CLI** — `a024c99` (feat)
4. **Task 4: refresh_all.py + .gitignore restructure** — `14125f4` (feat)
5. **Task 5: CHANGES.md entry** — `3e94bf4` (docs)

**Test count:** 54 passed + 4 skipped → 69 passed + 4 skipped (+15 from Phase-4 Plan 04: 8 manifest + 7 csv_mirror; zero regressions).

## Files Created / Modified

### Created
- `src/uk_subsidy_tracker/publish/__init__.py` — 26 lines; barrel re-exporting Manifest/Dataset/Source/build plus csv_mirror + snapshot submodules.
- `src/uk_subsidy_tracker/publish/manifest.py` — 364 lines; Pydantic models, GRAIN_SOURCES per-grain provenance table, D-12 chain module docstring, content-addressed generated_at, sidecar-line-scan site_url loader.
- `src/uk_subsidy_tracker/publish/csv_mirror.py` — 60 lines; pinned pandas to_csv args (D-10).
- `src/uk_subsidy_tracker/publish/snapshot.py` — 116 lines; argparse CLI with --version, --output, --dry-run.
- `src/uk_subsidy_tracker/refresh_all.py` — 113 lines; SCHEMES tuple, refresh_scheme + publish_latest + main.
- `tests/test_manifest.py` — 248 lines, 8 tests.
- `tests/test_csv_mirror.py` — 172 lines, 7 tests.
- `.planning/phases/04-publishing-layer/04-04-SUMMARY.md` (this file).

### Modified
- `.gitignore` — replaced blanket `site/` with per-mkdocs-subtree patterns so `site/data/` stays tracked (D-15).
- `CHANGES.md` — `[Unreleased]` gains publish/ package bullets (manifest.py, csv_mirror.py, snapshot.py) + refresh_all.py + tests; `### Changed` gains the .gitignore restructure bullet.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] `mkdocs.yml` crashes `yaml.safe_load` because of Python-tag constructors**
- **Found during:** Task 1, first run of `test_manifest_build_writes_file`.
- **Issue:** `mkdocs.yml` carries `!!python/name:material.extensions.emoji.twemoji` and similar custom constructors (line 107). `yaml.safe_load` raises `ConstructorError: could not determine a constructor for the tag ...`. The plan's interface sketch (RESEARCH §Pattern 2) used `yaml.safe_load(f)["site_url"]`; this crashes on the real file.
- **Fix:** Replaced the YAML-parse call with a top-level line-scan: read `mkdocs.yml` line by line, match `site_url:` at column 0, parse the RHS. Safer than `yaml.FullLoader` (which would execute arbitrary Python tags) and cheaper than subclassing SafeLoader to register every material.extensions tag. We only need `site_url`; one line is enough.
- **Files modified:** `src/uk_subsidy_tracker/publish/manifest.py` (`_site_url()` body); removed unused `import yaml`.
- **Commit:** `2e90d11` (shipped inside Task 1's feat commit; fix was part of turning the RED test GREEN).

**2. [Rule 1 — Bug] `!site/data/` exception cannot carve site/data/ out of ignored `site/`**
- **Found during:** Task 4, Step 4A preflight `git check-ignore site/`.
- **Issue:** Git does NOT support re-including files under an ignored directory. Adding `!site/data/` after `site/` is silently ineffective — `git check-ignore -v site/data/manifest.json` still reports the path ignored. The plan's Step 4A preflight (plan text) suggested adding the exception line but did not acknowledge the Git limitation. The daily refresh PR would have been empty.
- **Fix:** Replaced blanket `site/` ignore with explicit per-mkdocs-subtree patterns: `/site/{assets,stylesheets,search,themes,methodology,charts,about}/` + `/site/{index.html,404.html,sitemap.xml{,.gz}}`. `site/data/latest/*` and `site/data/manifest.json` are now tracked. Verified post-edit via `mkdocs build --strict` and `git check-ignore -v` probe: mkdocs outputs still ignored; publishing-layer files not.
- **Files modified:** `.gitignore`.
- **Commit:** `14125f4`.

### Rule-Rejected Alternatives

- Considered subclassing `yaml.SafeLoader` to register a benign constructor for each `!!python/name:material.extensions.*` tag. Rejected because the constructor list would need to grow with every mkdocs-material upgrade — a maintenance sink unrelated to the manifest logic. Line-scan is 8 lines of code with no external surface.
- Considered using `softprops/action-gh-release@v3`. Rejected per RESEARCH §Supporting Actions — v3 requires Node-24 which is not yet stable across all GitHub-hosted runners; v2 (v2.6.2) is Node-20-compatible and recommended. Plan 04-05 pins v2.

## Issues Encountered

- **Benign `RuntimeWarning` from `python -m uk_subsidy_tracker.publish.snapshot`**: "'uk_subsidy_tracker.publish.snapshot' found in sys.modules after import of package 'uk_subsidy_tracker.publish'". This fires because `publish/__init__.py` eagerly imports `snapshot` (so it becomes a `publish` attribute), and `-m` then re-executes it. It's a well-known Python import-order artefact; does not affect functionality (exit 0, correct output). Suppressing would require either lazy import of snapshot (breaking the barrel) or `python -m uk_subsidy_tracker.publish.snapshot` under `-W ignore::RuntimeWarning` in `deploy.yml`. Deferring the cosmetic tweak to Plan 04-05 workflow authoring where we can pass the `-W` flag in the workflow step.

## User Setup Required

None — no external service configuration required for this plan. `SITE_URL` env var is optional (defaults to `mkdocs.yml::site_url`). The daily refresh workflow in Plan 04-05 will set it explicitly; local snapshot/refresh runs use the mkdocs.yml value.

## Verification Results

**Plan `<success_criteria>` block:**

| Criterion | Result |
|---|---|
| `src/uk_subsidy_tracker/publish/{manifest,csv_mirror,snapshot}.py` + `__init__.py` ship | PASS (4/4 files present) |
| `refresh_all.py` orchestrator ships; short-circuits on clean state | PASS (printed "upstream unchanged" + "no upstream changes; skipping manifest rebuild" + exit 0) |
| `tests/test_manifest.py` (8 checks) + `tests/test_csv_mirror.py` (7 checks) pass | PASS (8/8 + 7/7) |
| Manifest.json URLs are absolute; URL fields serialise as `str` (Pitfall 6) | PASS (test_manifest_urls_are_absolute + test_manifest_urls_are_strings green) |
| Manifest.json `generated_at` stable across repeated calls with same raw state (Pitfall 3) | PASS (test_manifest_generated_at_stable_when_no_upstream_change green) |
| `methodology_version` field on manifest matches `counterfactual.METHODOLOGY_VERSION` | PASS (test_manifest_methodology_version_matches_constant green; value `"0.1.0"`) |
| `pipeline_git_sha` field populated via subprocess git (GOV-02) | PASS (40-char hex in emitted manifest) |
| snapshot.py dry-run produces a complete artifact tree deploy.yml can upload | PASS (16 files: 1 manifest.json + 5 parquet + 5 csv + 5 schema.json) |
| Full pytest suite green; `mkdocs build --strict` green | PASS (69 passed + 4 skipped; mkdocs exit 0 in 0.40s) |
| `CHANGES.md` records every publish-layer artifact | PASS (all 7 grep checks green: publish/manifest, csv_mirror, snapshot.py, refresh_all, test_manifest, test_csv_mirror, PUB-0[1-6]\|GOV-02) |

**Plan `<verification>` block:**

| Check | Result |
|---|---|
| `uv run pytest tests/test_manifest.py -v` — 8 passed | PASS (8 passed in 1.38s) |
| `uv run pytest tests/test_csv_mirror.py -v` — 7 passed | PASS (7 passed in 1.10s) |
| `uv run pytest tests/` — full suite green | PASS (69 passed + 4 skipped) |
| `uv run python -m uk_subsidy_tracker.publish.snapshot --version v2026.04-rc1 --output /tmp/snap --dry-run` — exits 0 + 5 parquet + 5 csv + 5 schema.json | PASS |
| `uv run python -m uk_subsidy_tracker.refresh_all` — short-circuits on clean state | PASS ("upstream unchanged" + "no upstream changes") |
| Manual inspection — all URLs https://, pipeline_git_sha 40-char hex, methodology_version "0.1.0" | PASS |

**Per-task acceptance criteria:** all 5 tasks hit 100% of their declared criteria (every grep check green, every file exists, every test passes). Two Rule-1 auto-fixes documented above, neither blocking.

## Next Plan Readiness

**Plan 04-05 (workflows: refresh.yml + deploy.yml) is fully unblocked.** It can now:
- Wire `refresh.yml`'s 06:00 UTC cron to call `uv run python -m uk_subsidy_tracker.refresh_all`, then (if non-zero exit or site/data/ diff) open a PR via `peter-evans/create-pull-request@v8`.
- Wire `deploy.yml`'s `on: push: tags: ['v*']` trigger to call `uv run python -m uk_subsidy_tracker.publish.snapshot --version ${{ github.ref_name }} --output snapshot-out/`, then upload everything under `snapshot-out/` as release assets via `softprops/action-gh-release@v2`.
- Rely on the short-circuit: refresh.yml only creates a PR if `site/data/manifest.json` actually changed (git-diff based). The manifest.py field-level Pitfall-3 stability ensures byte-identity when nothing upstream changed.

**Plan 04-06 (docs + benchmark floor) is unblocked.** `docs/data/index.md` can:
- Show DuckDB + pandas + R snippets fetching `manifest.json` and resolving URLs.
- Show the SHA-256 verification workflow (`shasum -a 256 station_month.parquet` should match the manifest entry).
- Show the versioned-URL citation pattern (`https://richardjlyon.github.io/uk-subsidy-tracker/data/v2026.04/cfd/station_month.parquet`).
- Reference `CITATION.cff` alongside `versioned_url`.

**No known blockers** for the remaining two Phase-4 plans.

## Self-Check: PASSED

- [x] `src/uk_subsidy_tracker/publish/__init__.py` exists
- [x] `src/uk_subsidy_tracker/publish/manifest.py` exists (contains `class Manifest`, `class Dataset`, `class Source`, `def build`, `GRAIN_SOURCES`, `pipeline_git_sha`, `model_dump(mode="json")`, `sort_keys=True`, `newline="\n"`)
- [x] `src/uk_subsidy_tracker/publish/csv_mirror.py` exists (contains `def build`, `lineterminator="\n"`, `index=False`, `date_format`, `float_format=None`)
- [x] `src/uk_subsidy_tracker/publish/snapshot.py` exists (contains `argparse`, `--version`, `--output`, `def build`, `cfd.rebuild_derived`, `csv_mirror.build`, `manifest_mod.build`)
- [x] `src/uk_subsidy_tracker/refresh_all.py` exists (contains `SCHEMES`, `upstream_changed`, `rebuild_derived`, `regenerate_charts`, "no upstream changes", `argparse`, `--version`)
- [x] `tests/test_manifest.py` exists (contains `model_validate`)
- [x] `tests/test_csv_mirror.py` exists (contains `lineterminator`)
- [x] `.gitignore` modified (explicit per-mkdocs-subtree patterns; site/data/manifest.json NOT ignored)
- [x] `CHANGES.md` modified (`publish/manifest`, `csv_mirror`, `snapshot.py`, `refresh_all`, `test_manifest`, `test_csv_mirror`, `PUB-0[1-6]|GOV-02` all grep-present)
- [x] Commit `2e90d11` in git log (Task 1: feat manifest RED→GREEN)
- [x] Commit `f6afd73` in git log (Task 2: feat csv_mirror)
- [x] Commit `a024c99` in git log (Task 3: feat snapshot)
- [x] Commit `14125f4` in git log (Task 4: feat refresh_all + gitignore)
- [x] Commit `3e94bf4` in git log (Task 5: docs CHANGES)
- [x] Full test suite: 69 passed + 4 skipped
- [x] `uv run python -m uk_subsidy_tracker.refresh_all` short-circuits on clean state + exit 0
- [x] `uv run python -m uk_subsidy_tracker.publish.snapshot --version v2026.04-rc1 --output /tmp/snap --dry-run` emits manifest.json + cfd/{5 parquet, 5 csv, 5 schema.json}
- [x] Round-trip byte-identity probe green
- [x] `uv run mkdocs build --strict` — exit 0 in 0.40s

---
*Phase: 04-publishing-layer*
*Plan: 04 (Wave 4 — publishing-layer manifest)*
*Completed: 2026-04-22*
