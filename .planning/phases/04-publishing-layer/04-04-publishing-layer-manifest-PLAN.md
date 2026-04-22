---
phase: 04-publishing-layer
plan: 04
type: execute
wave: 4
depends_on:
  - 01
  - 02
  - 03
files_modified:
  - src/uk_subsidy_tracker/publish/__init__.py
  - src/uk_subsidy_tracker/publish/manifest.py
  - src/uk_subsidy_tracker/publish/csv_mirror.py
  - src/uk_subsidy_tracker/publish/snapshot.py
  - src/uk_subsidy_tracker/refresh_all.py
  - tests/test_manifest.py
  - tests/test_csv_mirror.py
  - .gitignore
  - CHANGES.md
autonomous: true
requirements:
  - PUB-01
  - PUB-02
  - PUB-03
  - PUB-05
  - PUB-06
  - GOV-02
  - GOV-06  # snapshot URL portion — versioned_url field on manifest is the citation anchor
tags: [publishing-layer, manifest, csv-mirror, snapshot, refresh-orchestration]
user_setup: []

must_haves:
  truths:
    - "manifest.json carries full provenance per dataset (source URL, SHA-256, retrieved_at, pipeline git SHA, methodology_version)"
    - "A CSV mirror exists alongside every Parquet under site/data/latest/cfd/, same column order, LF line endings, full float precision"
    - "publish/snapshot.py assembles a temp dir of Parquet+CSV+schema.json+manifest.json that deploy.yml can upload as release assets"
    - "refresh_all.py invokes cfd.upstream_changed() and short-circuits when nothing has changed (Pitfall 3)"
    - "tests/test_manifest.py passes the round-trip: write manifest → read back → re-write → byte-identical"
    - "tests/test_csv_mirror.py passes: column order matches Parquet, line terminator is \\n, no UTF-8 BOM, floats unrounded"
  artifacts:
    - path: "src/uk_subsidy_tracker/publish/__init__.py"
      provides: "Barrel re-exporting manifest.build, csv_mirror.build, snapshot.build (module-level callables)"
    - path: "src/uk_subsidy_tracker/publish/manifest.py"
      provides: "Pydantic Manifest/Dataset/Source models + build() that reads derived/raw state and writes site/data/manifest.json via json.dumps(sort_keys=True, indent=2)"
      contains: "class Manifest"
      min_lines: 120
    - path: "src/uk_subsidy_tracker/publish/csv_mirror.py"
      provides: "build() reads every derived Parquet, writes a sibling CSV with pinned pandas args (index=False, lineterminator='\\n', date_format ISO-8601)"
      contains: "lineterminator"
      min_lines: 40
    - path: "src/uk_subsidy_tracker/publish/snapshot.py"
      provides: "CLI entry: --version v<YYYY.MM> --output <dir>; assembles version-tagged Parquet+CSV+schema.json+manifest.json in a temp dir for release-asset upload"
      contains: "--version"
      min_lines: 60
    - path: "src/uk_subsidy_tracker/refresh_all.py"
      provides: "CI entry point: iterates known schemes, calls upstream_changed/refresh/rebuild_derived/regenerate_charts; only builds manifest.json if anything changed (short-circuit per Pitfall 3)"
      contains: "upstream_changed"
      min_lines: 50
    - path: "tests/test_manifest.py"
      provides: "Manifest round-trip + provenance-field-presence + absolute-URL + sort-keys stability"
      contains: "model_validate"
      min_lines: 50
    - path: "tests/test_csv_mirror.py"
      provides: "Line-ending, column-order, encoding, float-precision checks"
      contains: "lineterminator"
      min_lines: 40
  key_links:
    - from: "src/uk_subsidy_tracker/publish/manifest.py"
      to: "data/raw/**/*.meta.json"
      via: "Reads sidecar JSON for retrieved_at / upstream_url / source_sha256 (does NOT trust sidecar hash blindly — re-computes from raw file)"
      pattern: ".meta.json"
    - from: "src/uk_subsidy_tracker/publish/manifest.py"
      to: "data/derived/cfd/*.parquet"
      via: "Walks derived_dir; each .parquet → one Dataset entry"
      pattern: "parquet"
    - from: "src/uk_subsidy_tracker/publish/manifest.py"
      to: "mkdocs.yml::site_url"
      via: "yaml.safe_load + _site_url() helper with SITE_URL env override (D-09)"
      pattern: "site_url"
    - from: "src/uk_subsidy_tracker/publish/manifest.py"
      to: "src/uk_subsidy_tracker/counterfactual.py::METHODOLOGY_VERSION"
      via: "Top-level manifest.methodology_version read from the module constant (not the Parquet column — one source of truth for the whole site)"
      pattern: "METHODOLOGY_VERSION"
    - from: "src/uk_subsidy_tracker/publish/csv_mirror.py"
      to: "data/derived/cfd/*.parquet"
      via: "pq.read_table(...).to_pandas().to_csv(..., lineterminator='\\n', index=False)"
      pattern: "read_table"
    - from: "src/uk_subsidy_tracker/refresh_all.py"
      to: "src/uk_subsidy_tracker/schemes/cfd/__init__.py"
      via: "from uk_subsidy_tracker.schemes import cfd; cfd.upstream_changed(); cfd.rebuild_derived(); ..."
      pattern: "from uk_subsidy_tracker.schemes import cfd"
---

<objective>
Ship the publishing layer: `manifest.json` contract + faithful CSV mirror +
versioned snapshot assembly + refresh orchestration. This is the plan that
makes the project citable — external consumers read `manifest.json`, follow
URLs, fetch Parquet + CSV + schema.json, and verify integrity via SHA-256.

Purpose: deliver PUB-01, PUB-02, PUB-03, PUB-05 (end-to-end three-layer
pipeline), PUB-06 (external-consumer fetchable), GOV-02 (provenance per
dataset), GOV-06 (snapshot URL citable). Manifest is the stable public
contract — shape is ARCHITECTURE §4.3 verbatim (D-07).

Output: `src/uk_subsidy_tracker/publish/` package with Pydantic-modelled
manifest, pinned CSV mirror, and snapshot CLI; `refresh_all.py` orchestrator
that short-circuits on SHA-unchanged upstream (Pitfall 3); two new test
files covering round-trip + CSV-pandas-args discipline.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/04-publishing-layer/04-CONTEXT.md
@.planning/phases/04-publishing-layer/04-RESEARCH.md
@.planning/phases/04-publishing-layer/04-PATTERNS.md
@.planning/phases/04-publishing-layer/04-VALIDATION.md
@.planning/phases/04-03-SUMMARY.md
@ARCHITECTURE.md
@src/uk_subsidy_tracker/counterfactual.py
@src/uk_subsidy_tracker/schemas/cfd.py
@src/uk_subsidy_tracker/schemes/cfd/__init__.py
@tests/fixtures/__init__.py
@mkdocs.yml

<interfaces>
<!-- ARCHITECTURE §4.3 verbatim manifest shape (D-07) — reproduced inline -->

```python
# Manifest top-level:
class Manifest(BaseModel):
    version: str                # e.g. 'v2026.04' or ISO date — caller supplies
    generated_at: datetime      # ISO-8601 UTC; stable when no upstream changed (Pitfall 3)
    methodology_version: str    # counterfactual.METHODOLOGY_VERSION
    pipeline_git_sha: str       # GOV-02; subprocess git rev-parse HEAD
    datasets: list[Dataset]

class Dataset(BaseModel):
    id: str                     # e.g. 'cfd.station_month'
    title: str                  # e.g. 'CfD Station × Month'
    grain: str                  # e.g. 'station × month'
    row_count: int
    schema_url: str             # absolute URL to <grain>.schema.json
    parquet_url: str            # absolute URL to <grain>.parquet
    csv_url: str                # absolute URL to <grain>.csv
    versioned_url: str          # e.g. https://<host>/data/v<YYYY-MM-DD>/cfd/<grain>.parquet
    sha256: str                 # lowercase 64-char hex of the parquet file
    sources: list[Source]
    methodology_page: str       # e.g. 'https://<host>/methodology/gas-counterfactual/'

class Source(BaseModel):
    name: str                   # e.g. 'lccc.actual-cfd-generation'
    upstream_url: str           # plain str (NOT HttpUrl — RESEARCH pitfall 6)
    retrieved_at: datetime
    source_sha256: str          # lowercase hex
```

<!-- Pinned JSON write (D-08) — Pydantic v2 does NOT support sort_keys on model_dump_json -->

```python
# manifest.py::build() bottom
body = json.dumps(
    manifest.model_dump(mode="json"),
    sort_keys=True,
    indent=2,
    ensure_ascii=False,
) + "\n"
output_path.write_text(body, encoding="utf-8", newline="\n")
```

<!-- Pinned pandas.to_csv (D-10) — RESEARCH Pattern 4 -->

```python
df.to_csv(
    csv_path,
    index=False,
    encoding="utf-8",
    lineterminator="\n",
    date_format="%Y-%m-%dT%H:%M:%S",
    float_format=None,
    na_rep="",
)
```

<!-- Existing model_fields access (Pydantic v2) -->

```python
# from uk_subsidy_tracker.schemas.cfd import StationMonthRow
# StationMonthRow.model_fields.keys() -> column names in declaration order
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: publish/manifest.py + tests/test_manifest.py (RED first, then GREEN)</name>
  <files>
    src/uk_subsidy_tracker/publish/__init__.py,
    src/uk_subsidy_tracker/publish/manifest.py,
    tests/test_manifest.py
  </files>
  <read_first>
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-07, D-08, D-09, D-12
    - .planning/phases/04-publishing-layer/04-RESEARCH.md §Pattern 2 (full manifest.py template lines 484-614), Pitfall 3 (generated_at stability), Pitfall 6 (HttpUrl vs str)
    - .planning/phases/04-publishing-layer/04-PATTERNS.md §A (Pydantic idiom from tests/fixtures/__init__.py)
    - ARCHITECTURE.md §4.3 lines 265-295 (verbatim manifest shape)
    - tests/fixtures/__init__.py (two-layer Pydantic loader pattern)
    - src/uk_subsidy_tracker/counterfactual.py (METHODOLOGY_VERSION)
    - src/uk_subsidy_tracker/schemes/cfd/__init__.py (DERIVED_DIR, rebuild_derived for fixture)
    - mkdocs.yml (site_url = "https://richardjlyon.github.io/uk-subsidy-tracker/")
  </read_first>
  <behavior>
    tests/test_manifest.py behavior (RED first):

    1. `test_manifest_build_writes_file` — call `publish.manifest.build(...)`,
       assert `site/data/manifest.json` (or tmp equivalent) exists.
    2. `test_manifest_provenance_fields_present` — every dataset has id, title,
       grain, row_count, schema_url, parquet_url, csv_url, versioned_url, sha256,
       sources (non-empty), methodology_page. Top-level has version, generated_at,
       methodology_version, pipeline_git_sha, datasets.
    3. `test_manifest_urls_are_absolute` — every URL starts with `http://` or
       `https://`; none are relative. Covers parquet_url, csv_url, schema_url,
       versioned_url, upstream_url on sources, methodology_page.
    4. `test_manifest_urls_are_strings` — Pitfall 6: every URL is `str`, not a
       wrapped object. Assert `isinstance(dataset['parquet_url'], str)` on the
       raw JSON re-read.
    5. `test_manifest_roundtrip_byte_identical` — build → read bytes → read
       parsed JSON via Manifest.model_validate → re-emit via the same
       `json.dumps(sort_keys=True, indent=2)` → assert byte equal. This
       catches Pydantic version drift.
    6. `test_manifest_sha256_matches_parquet` — re-compute sha256 from the
       on-disk Parquet; assert the manifest stored value matches. (Raw-file
       sha validation is covered by sidecar-backfill; this is the derived
       side.)
    7. `test_manifest_methodology_version_matches_constant` — top-level
       field equals `counterfactual.METHODOLOGY_VERSION` exactly.
    8. `test_manifest_generated_at_stable_when_no_upstream_change` — Pitfall 3
       mitigation. Strategy: `generated_at` sources from the LATEST
       `retrieved_at` across sidecars (content-addressed), NOT
       `datetime.now()`. Assert two consecutive calls with the same raw
       state produce the same `generated_at`. This is the test that
       guards manifest stability.

    Fixture: module-scoped rebuild via cfd.rebuild_derived(tmp_path), sidecar
    files copied (or linked) from `data/raw/`. Re-uses Plan 03 pattern.
  </behavior>
  <action>
    ### Step 1A — Write `tests/test_manifest.py` FIRST (RED)

    Full test file — 150-200 lines. Use the behaviors above and cross-reference
    RESEARCH §Validation Architecture Axis 5. Key fixtures:

    ```python
    @pytest.fixture(scope="module")
    def manifest_artifacts(tmp_path_factory):
        """Rebuild derived + build manifest once per test module."""
        out = tmp_path_factory.mktemp("manifest-artifacts")
        (out / "data" / "raw").mkdir(parents=True)
        # Copy raw files into tmp so the manifest walker finds sidecars.
        # shutil.copytree is portable to any CI runner / sandbox (including
        # filesystems or container mounts that disable symlinks).
        import shutil
        from uk_subsidy_tracker import DATA_DIR
        for sub in ("lccc", "elexon", "ons"):
            target = DATA_DIR / "raw" / sub
            link = out / "data" / "raw" / sub
            shutil.copytree(target, link, dirs_exist_ok=True)
        derived = out / "data" / "derived" / "cfd"
        cfd.rebuild_derived(output_dir=derived)
        manifest_path = out / "site" / "data" / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        from uk_subsidy_tracker.publish import manifest as manifest_mod
        built = manifest_mod.build(
            version="v2026.04-rc1",
            derived_dir=derived,
            raw_dir=out / "data" / "raw",
            output_path=manifest_path,
        )
        return built, manifest_path
    ```

    All 8 tests referenced in behavior above, mirroring the
    `tests/test_counterfactual.py` parametrise + remediation-hook shape where
    helpful.

    Run: `uv run pytest tests/test_manifest.py -v` → expect 8 failures
    (ImportError: publish.manifest does not exist).

    ### Step 1B — Author `src/uk_subsidy_tracker/publish/__init__.py`

    ```python
    """Publishing layer — manifest + CSV mirror + snapshot assembly."""
    from uk_subsidy_tracker.publish.manifest import Manifest, Dataset, Source, build
    from uk_subsidy_tracker.publish.csv_mirror import build as build_csv_mirror
    from uk_subsidy_tracker.publish.snapshot import build as build_snapshot

    __all__ = ["Manifest", "Dataset", "Source", "build", "build_csv_mirror", "build_snapshot"]
    ```

    (csv_mirror + snapshot land in later tasks this plan; placeholder imports
    OK — author tasks in parallel during implementation.)

    ### Step 1C — Author `src/uk_subsidy_tracker/publish/manifest.py` (TURN GREEN)

    Full file matches RESEARCH §Pattern 2 lines 484-614 with these key details:

    - `class Manifest(BaseModel)`: verbatim D-07 shape; pipeline_git_sha added
      per GOV-02.
    - `class Dataset(BaseModel)`: verbatim D-07; `sha256: str =
      Field(..., pattern=r"^[0-9a-f]{64}$")`.
    - `class Source(BaseModel)`: verbatim D-07; `upstream_url: str` NOT
      HttpUrl (Pitfall 6); `source_sha256` matching pattern.
    - `_git_sha()`: `subprocess.run(["git", "rev-parse", "HEAD"], …).stdout.strip()`.
    - `_sha256(path)`: hashlib helper.
    - `_site_url()`: prefers `SITE_URL` env var; else `yaml.safe_load(mkdocs.yml)["site_url"]`.
      Strips trailing `/`.
    - `_read_methodology_version()`: imports and returns `counterfactual.METHODOLOGY_VERSION`.
      **D-12 chain closure (include verbatim in manifest.py module docstring):**
      "D-12 chain: `METHODOLOGY_VERSION` (counterfactual.py) → DataFrame column
      (compute_counterfactual) → Parquet column (rebuild_derived) →
      cross-check (schemes/cfd/__init__.py::validate() Check 3 —
      `methodology_version` Parquet column == `METHODOLOGY_VERSION` constant)
      → manifest top-level field (here). The Parquet-column read is validated
      upstream by `validate()` which runs before manifest build in
      `refresh_all.refresh_scheme()`; manifest.py therefore reads the constant
      directly rather than re-reading the Parquet column, avoiding duplicate
      I/O while preserving end-to-end provenance."

    - `_latest_retrieved_at(raw_dir)`: walks `raw_dir/**/*.meta.json`,
      `max(json.load(m)["retrieved_at"] for m in metas)` — this is the
      content-addressed `generated_at` value per Pitfall 3.
    - `_assemble_dataset_entries(derived_dir, raw_dir, base, version)`: walks
      `derived_dir/*.parquet`, for each:
        - Reads row_count via `pq.read_metadata(parquet_path).num_rows`
        - Computes sha256 via `_sha256(parquet_path)`
        - `parquet_url = f"{base}/data/latest/cfd/{grain}.parquet"`
        - `csv_url = f"{base}/data/latest/cfd/{grain}.csv"`
        - `schema_url = f"{base}/data/latest/cfd/{grain}.schema.json"`
        - `versioned_url = f"{base}/data/{version}/cfd/{grain}.parquet"`
        - Sources derived by matching grain → the raw files it consumed via
          an explicit `GRAIN_SOURCES: dict[str, list[str]]` module-level
          mapping (verbatim — copy into `manifest.py`):

          ```python
          GRAIN_SOURCES: dict[str, list[str]] = {
              "station_month": [
                  "lccc/actual-cfd-generation.csv",
                  "lccc/cfd-contract-portfolio-status.csv",
                  "ons/gas-sap.xlsx",
                  "elexon/system-prices.csv",
              ],
              "annual_summary": [
                  "lccc/actual-cfd-generation.csv",
                  "lccc/cfd-contract-portfolio-status.csv",
                  "ons/gas-sap.xlsx",
                  "elexon/system-prices.csv",
              ],
              "by_technology": [
                  "lccc/actual-cfd-generation.csv",
                  "lccc/cfd-contract-portfolio-status.csv",
                  "ons/gas-sap.xlsx",
                  "elexon/system-prices.csv",
              ],
              "by_allocation_round": [
                  "lccc/actual-cfd-generation.csv",
                  "lccc/cfd-contract-portfolio-status.csv",
              ],
              "forward_projection": [
                  "lccc/cfd-contract-portfolio-status.csv",
              ],
          }
          ```

          `_assemble_dataset_entries` reads `GRAIN_SOURCES[grain]` for each
          dataset's `sources[]` list — provenance is per-grain, not "all
          five to every dataset". Phase 5+ schemes add their own
          `GRAIN_SOURCES` tables in per-scheme manifest-builder helpers.
        - For each Source entry: `source_sha256 = _sha256(Path('data/raw') / relative_path)`
          — re-compute from the raw file on disk, do NOT trust the
          sidecar-reported `sha256`. Compare against sidecar as a sanity
          check; if mismatch, log a warning via `logging.warning(...)`
          (still emit the manifest using the freshly-computed hash — raw
          file is truth, sidecar is metadata).
        - `methodology_page = f"{base}/methodology/gas-counterfactual/"`
        - `grain` = a human-readable string from a dict lookup
          `{"station_month": "station × month", "annual_summary": "year", ...}`.
        - `title` = similar dict lookup (`"CfD Station × Month"`, etc.).
        - `id` = `f"cfd.{grain_file_name}"`.
    - `build(version, derived_dir, raw_dir, output_path)`:
        - `generated_at = _latest_retrieved_at(raw_dir)` (NOT `datetime.now()`).
        - `manifest = Manifest(version=..., generated_at=..., methodology_version=..., pipeline_git_sha=..., datasets=[...])`.
        - `body = json.dumps(manifest.model_dump(mode="json"), sort_keys=True, indent=2, ensure_ascii=False) + "\n"`.
        - `output_path.write_text(body, encoding="utf-8", newline="\n")`.
        - Returns `manifest`.

    ### Step 1D — Run tests to GREEN

    ```bash
    uv run pytest tests/test_manifest.py -v
    ```

    All 8 tests should pass. If `test_manifest_generated_at_stable_when_no_upstream_change`
    fails, the most likely bug is using `datetime.now()` somewhere — grep:

    ```bash
    grep -n 'datetime.now\|time.time' src/uk_subsidy_tracker/publish/manifest.py
    ```

    Only legitimate call in this file is building a datetime FROM the latest
    retrieved_at string (not generating "now").

    If `test_manifest_roundtrip_byte_identical` fails, Pydantic is serialising
    a wrapped URL object — confirm `upstream_url: str` (not `HttpUrl`).

    ### Step 1E — Full test suite green

    ```bash
    uv run pytest tests/ -v
    ```
  </action>
  <verify>
    <automated>uv run pytest tests/test_manifest.py -v &amp;&amp; uv run pytest tests/ -x</automated>
  </verify>
  <acceptance_criteria>
    - `test -f src/uk_subsidy_tracker/publish/__init__.py` exits 0
    - `test -f src/uk_subsidy_tracker/publish/manifest.py` exits 0
    - `test -f tests/test_manifest.py` exits 0
    - `grep -cE "^class (Manifest|Dataset|Source)\b" src/uk_subsidy_tracker/publish/manifest.py` returns 3
    - `grep -q "pipeline_git_sha" src/uk_subsidy_tracker/publish/manifest.py` exits 0 (GOV-02)
    - Pydantic v2 dump pattern: `grep -q 'model_dump(mode="json")' src/uk_subsidy_tracker/publish/manifest.py` exits 0
    - Deterministic JSON: `grep -q 'sort_keys=True' src/uk_subsidy_tracker/publish/manifest.py` exits 0
    - `grep -q 'indent=2' src/uk_subsidy_tracker/publish/manifest.py` exits 0
    - LF-only newline write: `grep -q 'newline="\\\\n"' src/uk_subsidy_tracker/publish/manifest.py` OR `grep -q "newline='\\\\n'" src/uk_subsidy_tracker/publish/manifest.py` exits 0 (D-discretion default)
    - Pitfall-6 mitigation: `grep -qE 'upstream_url:\s*str' src/uk_subsidy_tracker/publish/manifest.py` exits 0 (NOT HttpUrl)
    - `grep -q 'sha256: str = Field' src/uk_subsidy_tracker/publish/manifest.py` exits 0 AND `grep -q "0-9a-f.*64" src/uk_subsidy_tracker/publish/manifest.py` exits 0 (sha256 pattern validator)
    - `grep -q 'git rev-parse HEAD' src/uk_subsidy_tracker/publish/manifest.py` exits 0 (pipeline_git_sha source)
    - `grep -q 'site_url' src/uk_subsidy_tracker/publish/manifest.py` exits 0 (D-09)
    - `grep -q 'SITE_URL' src/uk_subsidy_tracker/publish/manifest.py` exits 0 (env-var override)
    - NO `datetime.now()` in manifest.py body (Pitfall 3): `! grep -n 'datetime.now\|time.time\|utcnow' src/uk_subsidy_tracker/publish/manifest.py` returns empty
    - `uv run pytest tests/test_manifest.py -v` reports ≥8 passed
    - Round-trip proof: `uv run python -c "from pathlib import Path; import tempfile, os; from uk_subsidy_tracker.schemes import cfd; from uk_subsidy_tracker.publish import manifest as m; tmp = Path(tempfile.mkdtemp()); d = tmp / 'derived'; cfd.rebuild_derived(output_dir=d); from uk_subsidy_tracker import DATA_DIR; mp = tmp / 'manifest.json'; m.build(version='v2026.04-rc1', derived_dir=d, raw_dir=DATA_DIR / 'raw', output_path=mp); body1 = mp.read_text(); reloaded = m.Manifest.model_validate_json(body1); import json; body2 = json.dumps(reloaded.model_dump(mode='json'), sort_keys=True, indent=2, ensure_ascii=False) + '\n'; assert body1 == body2, 'round-trip not byte-identical'"` exits 0
    - Per-grain provenance (B-02 mitigation): `grep -q 'GRAIN_SOURCES' src/uk_subsidy_tracker/publish/manifest.py && uv run python -c "from uk_subsidy_tracker.publish.manifest import GRAIN_SOURCES; assert 'elexon/system-prices.csv' not in GRAIN_SOURCES['forward_projection'], 'forward_projection must not list Elexon system-prices'"` exits 0
    - Raw-file sha recompute (W-05 mitigation): `grep -qE '_sha256\(Path' src/uk_subsidy_tracker/publish/manifest.py || grep -qE 'source_sha256.*_sha256' src/uk_subsidy_tracker/publish/manifest.py` exits 0
    - `uv run pytest tests/` (full suite) green
  </acceptance_criteria>
  <done>manifest.py builds a provenance-rich manifest.json with absolute URLs, GOV-02-complete fields, and stable generated_at. test_manifest.py passes 8/8 including round-trip byte-identity.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: publish/csv_mirror.py + tests/test_csv_mirror.py (pandas-args discipline)</name>
  <files>
    src/uk_subsidy_tracker/publish/csv_mirror.py,
    tests/test_csv_mirror.py
  </files>
  <read_first>
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-10
    - .planning/phases/04-publishing-layer/04-RESEARCH.md §Pattern 4 (pandas arg pinning, lines 721-761), Pitfall 4 (Windows CRLF)
    - .planning/phases/04-publishing-layer/04-PATTERNS.md §C (csv_mirror.py role)
    - src/uk_subsidy_tracker/schemas/cfd.py (for `model_fields.keys()` → column order)
  </read_first>
  <behavior>
    tests/test_csv_mirror.py (RED first):

    1. `test_csv_mirror_written_for_every_parquet` — after build(), every
       .parquet under derived dir has a sibling .csv.
    2. `test_csv_column_order_matches_parquet` — read CSV header, assert ==
       `pq.read_table(parquet).column_names`.
    3. `test_csv_line_endings_are_lf` — read CSV as bytes, assert NO `\r\n`,
       only `\n` (Pitfall 4).
    4. `test_csv_no_bom` — first bytes of CSV ≠ `\xef\xbb\xbf`.
    5. `test_csv_no_index_column` — no leading unnamed column (D-10).
    6. `test_csv_dates_iso8601` — date columns in ISO-8601 format
       (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`). Regex check on one row.
    7. `test_csv_floats_preserve_precision` — a known high-precision value
       from Parquet round-trips into the CSV with full precision (no
       truncation). E.g. `1234.567890123` stays >10 significant figures.
  </behavior>
  <action>
    ### Step 2A — `tests/test_csv_mirror.py` (RED)

    Skeleton ≈ 80 lines. Reuse the module-scoped rebuild fixture from
    test_manifest.py style:

    ```python
    @pytest.fixture(scope="module")
    def mirror_dir(tmp_path_factory):
        from uk_subsidy_tracker.schemes import cfd
        from uk_subsidy_tracker.publish import csv_mirror
        out = tmp_path_factory.mktemp("csv-mirror")
        cfd.rebuild_derived(output_dir=out)
        csv_mirror.build(out)
        return out
    ```

    Seven tests from the behavior list.

    ### Step 2B — `src/uk_subsidy_tracker/publish/csv_mirror.py` (GREEN)

    Full file ≈ 50 lines matching RESEARCH §Pattern 4 lines 723-753:

    ```python
    """Faithful CSV mirror for every derived Parquet (PUB-02, D-10).

    Journalists open these in Excel; Python / R users read with their
    native CSV parsers. Pinned args prevent cross-platform line-ending drift
    (Pitfall 4).
    """

    from __future__ import annotations

    from pathlib import Path

    import pandas as pd
    import pyarrow.parquet as pq


    def write_csv_mirror(parquet_path: Path, csv_path: Path) -> None:
        """Faithful CSV mirror of one Parquet (D-10 defaults)."""
        df = pq.read_table(parquet_path).to_pandas()
        df.to_csv(
            csv_path,
            index=False,                       # D-10: no row number
            encoding="utf-8",                  # no BOM (Excel 2016+ is fine)
            lineterminator="\n",               # LF even on Windows (Pitfall 4)
            date_format="%Y-%m-%dT%H:%M:%S",   # ISO-8601, no sub-seconds
            float_format=None,                 # full precision
            na_rep="",                         # empty cell for NaN
        )


    def build(derived_dir: Path) -> list[Path]:
        """Iterate derived_dir, write a .csv next to every .parquet.

        Returns the list of CSV paths written.
        """
        written: list[Path] = []
        for parquet_path in sorted(derived_dir.glob("*.parquet")):
            csv_path = parquet_path.with_suffix(".csv")
            write_csv_mirror(parquet_path, csv_path)
            written.append(csv_path)
        return written
    ```

    ### Step 2C — Run tests green

    ```bash
    uv run pytest tests/test_csv_mirror.py -v
    ```

    Expect 7 passed. If `test_csv_line_endings_are_lf` fails on macOS, that's
    a test bug (macOS default is `\n` already — the test matters for
    Windows CI, but the `lineterminator="\n"` arg makes the test a no-op
    on Unix).
  </action>
  <verify>
    <automated>uv run pytest tests/test_csv_mirror.py -v</automated>
  </verify>
  <acceptance_criteria>
    - `test -f src/uk_subsidy_tracker/publish/csv_mirror.py` exits 0
    - `test -f tests/test_csv_mirror.py` exits 0
    - `grep -q 'lineterminator="\\\\n"' src/uk_subsidy_tracker/publish/csv_mirror.py` OR `grep -q "lineterminator='\\\\n'" src/uk_subsidy_tracker/publish/csv_mirror.py` exits 0
    - `grep -q 'index=False' src/uk_subsidy_tracker/publish/csv_mirror.py` exits 0
    - `grep -q 'date_format=' src/uk_subsidy_tracker/publish/csv_mirror.py` exits 0
    - `grep -q 'float_format=None' src/uk_subsidy_tracker/publish/csv_mirror.py` exits 0
    - `grep -q "def build" src/uk_subsidy_tracker/publish/csv_mirror.py` exits 0
    - `uv run pytest tests/test_csv_mirror.py -v` — 7 passed
    - `uv run pytest tests/` green overall
  </acceptance_criteria>
  <done>CSV mirror sibling file for every Parquet, with pinned pandas args (LF, no BOM, no index, ISO dates, full float precision). Seven tests green.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: publish/snapshot.py (CLI for versioned snapshots)</name>
  <files>src/uk_subsidy_tracker/publish/snapshot.py</files>
  <read_first>
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-13, D-14 (GitHub release artifact storage + tag naming)
    - .planning/phases/04-publishing-layer/04-RESEARCH.md Open Question 3 (dry-run Phase 4 exit checkpoint)
    - .planning/phases/04-publishing-layer/04-PATTERNS.md §C (snapshot.py shape)
    - src/uk_subsidy_tracker/publish/manifest.py (build signature)
    - src/uk_subsidy_tracker/publish/csv_mirror.py (build signature)
    - src/uk_subsidy_tracker/schemes/cfd/__init__.py (rebuild_derived signature)
  </read_first>
  <action>
    `src/uk_subsidy_tracker/publish/snapshot.py` — CLI entry producing a
    self-contained snapshot directory for the `deploy.yml` workflow
    (Plan 05) to upload as release assets. 80-100 lines.

    ```python
    """Versioned-snapshot assembler (PUB-03, D-13, D-14).

    Produces a temp-dir layout of Parquet + CSV + schema.json + manifest.json
    that `.github/workflows/deploy.yml` uploads as release assets via
    `softprops/action-gh-release@v2` on `git push --tags`.

    Invocation (from deploy.yml):
        uv run --frozen python -m uk_subsidy_tracker.publish.snapshot \\
            --version "${{ github.ref_name }}" \\
            --output snapshot-out/

    Invocation (dry-run, local):
        uv run python -m uk_subsidy_tracker.publish.snapshot \\
            --version v2026.04-rc1 \\
            --output /tmp/snapshot-dry-run
    """

    from __future__ import annotations

    import argparse
    import shutil
    import sys
    from pathlib import Path

    from uk_subsidy_tracker import DATA_DIR, PROJECT_ROOT
    from uk_subsidy_tracker.schemes import cfd
    from uk_subsidy_tracker.publish import csv_mirror, manifest as manifest_mod


    def build(version: str, output_dir: Path) -> Path:
        """Assemble a snapshot directory for release upload.

        Layout produced:
            output_dir/
              manifest.json
              cfd/
                station_month.parquet
                station_month.csv
                station_month.schema.json
                ...

        Returns output_dir. Caller (deploy.yml) uploads everything under it.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Rebuild derived into the snapshot directory directly (no
        #    intermediate copy; also re-emits schema.json siblings).
        cfd_out = output_dir / "cfd"
        cfd.rebuild_derived(output_dir=cfd_out)

        # 2. CSV mirrors alongside each Parquet.
        csv_mirror.build(cfd_out)

        # 3. Manifest — absolute URLs point at the versioned path (D-13/D-14).
        manifest_path = output_dir / "manifest.json"
        manifest_mod.build(
            version=version,
            derived_dir=cfd_out,
            raw_dir=DATA_DIR / "raw",
            output_path=manifest_path,
        )
        return output_dir


    def _parse_args(argv: list[str]) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            prog="uk_subsidy_tracker.publish.snapshot",
            description="Assemble a versioned-snapshot directory for release upload.",
        )
        parser.add_argument("--version", required=True,
                            help="Calendar-based tag, e.g. v2026.04 or v2026.04-rc1.")
        parser.add_argument("--output", type=Path, required=True,
                            help="Output directory (will be created if absent).")
        parser.add_argument("--dry-run", action="store_true",
                            help="Assemble but do not exit 0 if output_dir is non-empty.")
        return parser.parse_args(argv)


    def main(argv: list[str] | None = None) -> int:
        args = _parse_args(sys.argv[1:] if argv is None else argv)
        if args.output.exists() and any(args.output.iterdir()):
            if args.dry_run:
                shutil.rmtree(args.output)
            else:
                print(f"snapshot: output dir {args.output} already non-empty; "
                      f"pass --dry-run to clear or choose a fresh path.")
                return 2
        build(args.version, args.output)
        print(f"snapshot: {args.output} ready for release-asset upload.")
        return 0


    if __name__ == "__main__":
        raise SystemExit(main())
    ```

    Post-authoring dry-run check:

    ```bash
    uv run python -m uk_subsidy_tracker.publish.snapshot \
        --version v2026.04-rc1 --output /tmp/snapshot-dry-run --dry-run
    ls /tmp/snapshot-dry-run/
    # Expect: manifest.json + cfd/ subtree with 5 .parquet + 5 .csv + 5 .schema.json
    ```
  </action>
  <verify>
    <automated>uv run python -m uk_subsidy_tracker.publish.snapshot --version v2026.04-rc1 --output /tmp/snapshot-plan04-test --dry-run &amp;&amp; test -f /tmp/snapshot-plan04-test/manifest.json &amp;&amp; ls /tmp/snapshot-plan04-test/cfd/ | grep -c '\.parquet$' | grep -q '^5$' &amp;&amp; ls /tmp/snapshot-plan04-test/cfd/ | grep -c '\.csv$' | grep -q '^5$' &amp;&amp; ls /tmp/snapshot-plan04-test/cfd/ | grep -c '\.schema\.json$' | grep -q '^5$'</automated>
  </verify>
  <acceptance_criteria>
    - `test -f src/uk_subsidy_tracker/publish/snapshot.py` exits 0
    - `grep -q 'argparse' src/uk_subsidy_tracker/publish/snapshot.py` exits 0
    - `grep -qE '[-]-version' src/uk_subsidy_tracker/publish/snapshot.py` exits 0
    - `grep -qE '[-]-output' src/uk_subsidy_tracker/publish/snapshot.py` exits 0
    - `grep -q 'def build' src/uk_subsidy_tracker/publish/snapshot.py` exits 0
    - `grep -q 'cfd.rebuild_derived' src/uk_subsidy_tracker/publish/snapshot.py` exits 0
    - `grep -q 'csv_mirror.build' src/uk_subsidy_tracker/publish/snapshot.py` exits 0
    - `grep -q 'manifest.*build' src/uk_subsidy_tracker/publish/snapshot.py` exits 0
    - Dry-run produces the expected layout (see verify command)
    - `uv run python -c "from uk_subsidy_tracker.publish import snapshot; snapshot.main(['--version', 'v2026.04-rc1', '--output', '/tmp/snapshot-smoke', '--dry-run'])"` exits 0
  </acceptance_criteria>
  <done>snapshot.py CLI assembles a versioned artifact directory: manifest.json + cfd/ with 5 parquet + 5 csv + 5 schema.json files. Ready for deploy.yml upload (Plan 05).</done>
</task>

<task type="auto" tdd="false">
  <name>Task 4: refresh_all.py — per-scheme dirty-check + short-circuit (D-18, Pitfall 3)</name>
  <files>
    src/uk_subsidy_tracker/refresh_all.py,
    .gitignore
  </files>
  <read_first>
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-16, D-17, D-18
    - .planning/phases/04-publishing-layer/04-RESEARCH.md §Pattern 8 "Control flow on daily refresh" (lines 271-299), Pitfall 3 (generated_at stability)
    - src/uk_subsidy_tracker/schemes/cfd/__init__.py (the cfd module)
    - src/uk_subsidy_tracker/publish/__init__.py (manifest.build, csv_mirror.build)
    - src/uk_subsidy_tracker/publish/manifest.py (build signature)
    - .gitignore (check current entries; avoid duplicates)
  </read_first>
  <action>
    ### Step 4A — `.gitignore` preflight + intent comment

    **Preflight (N-03):** Verify `site/` is NOT already gitignored:

    ```bash
    git check-ignore site/ && echo "WARN: site/ is gitignored" || echo "OK: site/ is tracked"
    ```

    If the command reports `site/` is ignored, add an exception line
    `!site/data/` to `.gitignore` BEFORE proceeding. The daily refresh PR
    MUST be able to commit `site/data/latest/cfd/*` — if `site/` is ignored,
    the PR body will be empty and the workflow silently succeeds-without-
    committing.

    **Chart regen cost note (W-03):** `regenerate_charts()` delegates to
    `runpy.run_module('uk_subsidy_tracker.plotting')` (see schemes/cfd/__init__.py
    Task 2 Step 2F of Plan 03). The current CfD dataset is well under the
    `refresh.yml` 30-min timeout (typical chart regen: ~1-2 min end-to-end);
    D-18 dirty-check via `cfd.upstream_changed()` short-circuits on unchanged
    upstream, so the cost is only incurred when data actually changed. No
    caching layer required for Phase 4; revisit only if a future scheme
    (e.g. Phase 8 NESO BM half-hourly) pushes past the 30-min cap.

    Append to `.gitignore` (only if not already present):

    ```gitignore
    # Phase 4 publishing layer: site/data/latest is produced by refresh_all.
    # The daily refresh PR commits these paths intentionally (D-15); the
    # gitignore below is for local dev builds. Do NOT add site/data/.
    # Note: Cloudflare Pages reads from main — refresh PR merges push these.
    ```

    (No actual ignore needed — `site/data/latest/` is committed. The daily
    refresh PR writes to `site/data/latest/cfd/*` and commits it. Document
    this intent explicitly in the `.gitignore` comment.)

    ### Step 4B — `src/uk_subsidy_tracker/refresh_all.py`

    Full file ≈ 100 lines:

    ```python
    """CI entry point — per-scheme dirty-check + conditional rebuild (D-18).

    Invoked by `.github/workflows/refresh.yml` daily cron. Walks all known
    schemes, calls `scheme.upstream_changed()`, and only invokes
    `refresh() → rebuild_derived() → regenerate_charts()` for those whose
    raw-file SHA-256 differs from the sidecar.

    When anything changed: also rebuilds `site/data/manifest.json` + CSV
    mirrors + writes a human-friendly summary to stdout for the PR body.

    When nothing changed: exits 0 with "no upstream changes" — refresh.yml
    then skips the create-pull-request step (Pitfall 3 — no noisy daily PRs).
    """

    from __future__ import annotations

    import argparse
    import sys
    from pathlib import Path

    from uk_subsidy_tracker import DATA_DIR, PROJECT_ROOT
    from uk_subsidy_tracker.schemes import cfd
    from uk_subsidy_tracker.publish import manifest as manifest_mod
    from uk_subsidy_tracker.publish import csv_mirror

    SCHEMES = (
        ("cfd", cfd),
        # Phase 5+ schemes append here: ("ro", ro), ("fit", fit), ...
    )

    SITE_DATA_DIR = PROJECT_ROOT / "site" / "data"
    DERIVED_DIR = PROJECT_ROOT / "data" / "derived"
    LATEST_DIR = SITE_DATA_DIR / "latest"


    def refresh_scheme(name: str, scheme_module) -> bool:
        """Return True if the scheme was refreshed (upstream changed), False if skipped."""
        if not scheme_module.upstream_changed():
            print(f"[{name}] upstream unchanged — skipping refresh")
            return False
        print(f"[{name}] upstream changed — refreshing…")
        scheme_module.refresh()
        scheme_module.rebuild_derived()
        # Chart regeneration is expensive; only if needed. D-02 permits
        # charts to consume derived or raw — either way, refresh happens.
        scheme_module.regenerate_charts()
        warnings = scheme_module.validate()
        if warnings:
            print(f"[{name}] validate() warnings:")
            for w in warnings:
                print(f"  - {w}")
        return True


    def publish_latest(version: str) -> None:
        """Copy derived/ to site/data/latest/ + write CSV mirrors + manifest."""
        LATEST_DIR.mkdir(parents=True, exist_ok=True)
        # For each scheme: copy <scheme>/*.parquet + *.schema.json into latest,
        # build CSV mirrors, then build the top-level manifest.
        for scheme_name, _module in SCHEMES:
            src = DERIVED_DIR / scheme_name
            dst = LATEST_DIR / scheme_name
            if not src.is_dir():
                continue
            dst.mkdir(parents=True, exist_ok=True)
            for path in src.glob("*"):
                dst_path = dst / path.name
                dst_path.write_bytes(path.read_bytes())
            csv_mirror.build(dst)
        manifest_mod.build(
            version=version,
            derived_dir=DERIVED_DIR,
            raw_dir=DATA_DIR / "raw",
            output_path=SITE_DATA_DIR / "manifest.json",
        )


    def main(argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(prog="uk_subsidy_tracker.refresh_all")
        parser.add_argument("--version", default="latest",
                            help="Manifest version tag (default 'latest'). "
                                 "deploy.yml passes e.g. v2026.04.")
        args = parser.parse_args(sys.argv[1:] if argv is None else argv)

        any_changed = False
        for name, module in SCHEMES:
            if refresh_scheme(name, module):
                any_changed = True

        if not any_changed:
            print("refresh_all: no upstream changes; skipping manifest rebuild")
            return 0

        publish_latest(version=args.version)
        print(f"refresh_all: site/data/manifest.json rebuilt (version={args.version})")
        return 0


    if __name__ == "__main__":
        raise SystemExit(main())
    ```

    ### Step 4C — Smoke test

    ```bash
    # First call: upstream is unchanged (sha sidecars match files), expect short-circuit.
    uv run python -m uk_subsidy_tracker.refresh_all
    # Expect: "[cfd] upstream unchanged — skipping refresh"
    #         "refresh_all: no upstream changes; skipping manifest rebuild"

    # Force a refresh via manual --version (module-level behaviour unchanged
    # unless we pretend a file changed — skip this probe unless debugging).
    ```
  </action>
  <verify>
    <automated>uv run python -m uk_subsidy_tracker.refresh_all 2>&amp;1 | grep -q "upstream unchanged\|refresh_all"</automated>
  </verify>
  <acceptance_criteria>
    - `test -f src/uk_subsidy_tracker/refresh_all.py` exits 0
    - `grep -q "SCHEMES" src/uk_subsidy_tracker/refresh_all.py` exits 0
    - `grep -q "from uk_subsidy_tracker.schemes import cfd" src/uk_subsidy_tracker/refresh_all.py` exits 0
    - `grep -q "upstream_changed" src/uk_subsidy_tracker/refresh_all.py` exits 0
    - `grep -q "rebuild_derived" src/uk_subsidy_tracker/refresh_all.py` exits 0
    - `grep -q "regenerate_charts" src/uk_subsidy_tracker/refresh_all.py` exits 0
    - Short-circuit mention: `grep -q "no upstream changes\|skipping" src/uk_subsidy_tracker/refresh_all.py` exits 0 (Pitfall 3)
    - `grep -q "argparse" src/uk_subsidy_tracker/refresh_all.py` exits 0
    - `grep -qE "[-]-version" src/uk_subsidy_tracker/refresh_all.py` exits 0
    - First run short-circuits (sidecar sha matches file): `uv run python -m uk_subsidy_tracker.refresh_all 2>&1 | grep -q "upstream unchanged"` exits 0
    - Exit code 0 on clean run: `uv run python -m uk_subsidy_tracker.refresh_all; echo $?` prints "0"
    - `uv run pytest tests/` green overall
  </acceptance_criteria>
  <done>refresh_all.py orchestrates dirty-check → refresh → rebuild → regen → validate per scheme; short-circuits before manifest rebuild when nothing changed.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 5: CHANGES.md — publishing layer entries</name>
  <files>CHANGES.md</files>
  <read_first>
    - CHANGES.md current [Unreleased] (Plans 01-03 entries)
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-07 through D-18
  </read_first>
  <action>
    Under `### Added`:

    ```markdown
    - `src/uk_subsidy_tracker/publish/` package — the publishing layer:
      - `manifest.py` — Pydantic `Manifest` / `Dataset` / `Source` models; `build()` assembles `site/data/manifest.json` via `json.dumps(model.model_dump(mode="json"), sort_keys=True, indent=2)` (Pydantic v2 does NOT support `sort_keys` on `model_dump_json` — issue #7424). Shape is ARCHITECTURE §4.3 verbatim (D-07). URLs absolute (D-09); `generated_at` sourced from latest sidecar `retrieved_at` rather than `datetime.now()` (Pitfall 3 — stable manifest when nothing upstream changes).
      - `csv_mirror.py` — sibling CSV for every derived Parquet (PUB-02). Pinned pandas args per D-10: `index=False`, `lineterminator="\n"`, `date_format="%Y-%m-%dT%H:%M:%S"`, `float_format=None`, no BOM.
      - `snapshot.py` — CLI (`--version`, `--output`) assembles a self-contained versioned-snapshot directory for `deploy.yml` to upload as release assets on tag push (D-13, D-14).
    - `src/uk_subsidy_tracker/refresh_all.py` — CI entry point orchestrating per-scheme dirty-check + refresh + derived rebuild + chart regen + manifest write (D-16, D-18).
    - `tests/test_manifest.py` — 8 checks covering manifest provenance fields, absolute URLs, Pydantic-v2 URL-type-is-str (Pitfall 6), byte-identical round-trip, sha256-matches-parquet, methodology_version=constant, generated_at stability when nothing upstream changed.
    - `tests/test_csv_mirror.py` — 7 checks covering line endings, BOM absence, column order, index-column absence, ISO-8601 dates, float precision.
    ```
  </action>
  <verify>
    <automated>grep -q "publish/manifest.py\|src/uk_subsidy_tracker/publish" CHANGES.md &amp;&amp; grep -q "refresh_all.py" CHANGES.md &amp;&amp; grep -q "test_manifest.py" CHANGES.md &amp;&amp; grep -q "test_csv_mirror.py" CHANGES.md &amp;&amp; uv run mkdocs build --strict</automated>
  </verify>
  <acceptance_criteria>
    - `grep -q "publish/manifest" CHANGES.md` exits 0
    - `grep -q "csv_mirror" CHANGES.md` exits 0
    - `grep -q "snapshot.py" CHANGES.md` exits 0
    - `grep -q "refresh_all" CHANGES.md` exits 0
    - `grep -q "test_manifest" CHANGES.md` exits 0
    - `grep -q "test_csv_mirror" CHANGES.md` exits 0
    - `grep -q "PUB-0[1-6]\|GOV-02" CHANGES.md` exits 0 (at least one requirement ID cited)
    - `uv run mkdocs build --strict` exits 0
  </acceptance_criteria>
  <done>CHANGES.md records the full publishing layer + orchestrator + tests.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| `data/raw/*.meta.json` → `manifest.json` | A tampered sidecar could inject a wrong `upstream_url` or `retrieved_at` into the public manifest. |
| `mkdocs.yml::site_url` / `SITE_URL` env → absolute manifest URLs | A mis-set site_url would emit wrong-host URLs (e.g. `http://localhost:8000/…`) into a production manifest. |
| Pydantic `model_dump(mode="json")` | Serialisation format changes between minor versions could break round-trip byte identity. |
| Git HEAD → `manifest.json::pipeline_git_sha` | subprocess call to git — CI pins this. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-04-04-01 (T-04-M) | Tampering | `manifest.json` URLs emit wrong host because `site_url` mis-configured | mitigate | `_site_url()` prefers `SITE_URL` env var; fallback reads `mkdocs.yml::site_url`. Empty string fails Pydantic validation (`str` with non-empty pattern). Plan 06 also adds a `test_site_url_matches_production` smoke check. Deploy.yml always pins `SITE_URL` to the Cloudflare Pages host. |
| T-04-04-02 (T-04-S) | Tampering | Raw sidecar SHA-256 tampered to hide a content change | mitigate | `manifest.py::build()` re-computes sha256 on the RAW file (`_sha256(raw_path)`); sidecar-reported hash is NOT trusted blindly. Any mismatch between sidecar and computed sha surfaces in `refresh_all.upstream_changed()` (triggers refresh). |
| T-04-04-03 | Tampering | Pydantic minor upgrade changes URL serialisation (Pitfall 6) | mitigate | `upstream_url: str` (not `HttpUrl`). `test_manifest_urls_are_strings` checks raw-JSON type on every URL. `test_manifest_roundtrip_byte_identical` catches any serialisation drift on the whole model. |
| T-04-04-04 | Information Disclosure | `site/data/manifest.json` leaks a private-URL because a scheme was mis-wired | accept | All upstream URLs are UK gov open-data endpoints; no private APIs. Phase-4 allowlist: `data/raw/<publisher>/…` sources, plus the site_url host itself. New scheme modules must re-verify in their own phase. |
| T-04-04-05 | Denial of Service | Manifest rebuild churns every day with a new `generated_at`, making PRs noisy and CI burning time | mitigate | Pitfall 3: `generated_at = max(retrieved_at across sidecars)` (content-addressed). `refresh_all.py` short-circuits before calling `manifest.build()` when `upstream_changed()` is False across all schemes. |
| T-04-04-06 | Tampering | CSV mirror written with non-LF line endings on a Windows developer machine, breaks journalists' Unix pipelines | mitigate | Pinned `lineterminator="\n"` (D-10). `test_csv_line_endings_are_lf` byte-checks the output. |
| T-04-04-07 | Repudiation | A published figure disputed; can't prove which pipeline git SHA produced it | mitigate | `Manifest.pipeline_git_sha` field populated via `git rev-parse HEAD` at build time. Snapshot URL on release asset is immutable (GitHub releases are retention-guaranteed). |
</threat_model>

<verification>
Phase-4 Plan 04 verifications:

1. `uv run pytest tests/test_manifest.py -v` — 8 passed
2. `uv run pytest tests/test_csv_mirror.py -v` — 7 passed
3. `uv run pytest tests/` — full suite green (adds ~15 tests from this plan)
4. `uv run python -m uk_subsidy_tracker.publish.snapshot --version v2026.04-rc1 --output /tmp/snap --dry-run` — exits 0; produces manifest.json + cfd/ with 15 files (5 parquet + 5 csv + 5 schema.json)
5. `uv run python -m uk_subsidy_tracker.refresh_all` — short-circuits on clean state (no upstream change)
6. Manual: inspect `/tmp/snap/manifest.json` — all URLs start `https://`, pipeline_git_sha is 40-char hex, methodology_version is "0.1.0"
</verification>

<success_criteria>
- `src/uk_subsidy_tracker/publish/{manifest,csv_mirror,snapshot}.py` + `__init__.py` ship
- `refresh_all.py` orchestrator ships; short-circuits on clean state
- `tests/test_manifest.py` (8 checks) and `tests/test_csv_mirror.py` (7 checks) pass
- Manifest.json URLs are absolute; Pydantic URL fields serialise as `str` (Pitfall 6)
- Manifest.json `generated_at` is stable across repeated calls with same raw state (Pitfall 3)
- `methodology_version` field on manifest matches `counterfactual.METHODOLOGY_VERSION` (GOV-02 top-level)
- `pipeline_git_sha` field populated via subprocess git (GOV-02)
- snapshot.py dry-run produces a complete artifact tree deploy.yml can upload
- Full pytest suite green; `mkdocs build --strict` green
- `CHANGES.md` records every publish-layer artifact
</success_criteria>

<output>
After completion, create `.planning/phases/04-publishing-layer/04-04-SUMMARY.md`. Must include:
- First example `manifest.json` emitted (5-10 line excerpt of the top-level JSON) — demonstrates D-07 shape
- Confirmation that `pipeline_git_sha` is populated via subprocess on CI and locally
- Any Pydantic-v2 serialisation surprises (HttpUrl vs str) encountered during round-trip testing
- Row counts per dataset as cross-check against Plan 03 summary (should match; if not, document divergence)
</output>
