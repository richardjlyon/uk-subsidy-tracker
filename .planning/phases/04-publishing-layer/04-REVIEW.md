---
phase: 04-publishing-layer
reviewed: 2026-04-22T00:00:00Z
depth: standard
files_reviewed: 35
files_reviewed_list:
  - .github/refresh-failure-template.md
  - .github/workflows/deploy.yml
  - .github/workflows/refresh.yml
  - .gitignore
  - docs/about/citation.md
  - docs/data/index.md
  - docs/index.md
  - mkdocs.yml
  - pyproject.toml
  - scripts/backfill_sidecars.py
  - src/uk_subsidy_tracker/data/elexon.py
  - src/uk_subsidy_tracker/data/lccc_datasets.yaml
  - src/uk_subsidy_tracker/data/ons_gas.py
  - src/uk_subsidy_tracker/publish/__init__.py
  - src/uk_subsidy_tracker/publish/csv_mirror.py
  - src/uk_subsidy_tracker/publish/manifest.py
  - src/uk_subsidy_tracker/publish/snapshot.py
  - src/uk_subsidy_tracker/refresh_all.py
  - src/uk_subsidy_tracker/schemas/__init__.py
  - src/uk_subsidy_tracker/schemas/cfd.py
  - src/uk_subsidy_tracker/schemes/__init__.py
  - src/uk_subsidy_tracker/schemes/cfd/__init__.py
  - src/uk_subsidy_tracker/schemes/cfd/_refresh.py
  - src/uk_subsidy_tracker/schemes/cfd/aggregation.py
  - src/uk_subsidy_tracker/schemes/cfd/cost_model.py
  - src/uk_subsidy_tracker/schemes/cfd/forward_projection.py
  - tests/fixtures/__init__.py
  - tests/fixtures/benchmarks.yaml
  - tests/fixtures/constants.yaml
  - tests/test_aggregates.py
  - tests/test_constants_provenance.py
  - tests/test_csv_mirror.py
  - tests/test_determinism.py
  - tests/test_manifest.py
  - tests/test_schemas.py
findings:
  critical: 1
  warning: 6
  info: 7
  total: 14
status: issues_found
---

# Phase 4: Code Review Report

**Reviewed:** 2026-04-22T00:00:00Z
**Depth:** standard
**Files Reviewed:** 35
**Status:** issues_found

## Summary

Phase 4 delivers the publishing layer (manifest, CSV mirror, snapshot, refresh orchestrator) plus the daily-refresh and release GitHub Actions workflows. The core invariants demanded by the project charter — content-addressed `generated_at`, deterministic Parquet writer, live SHA re-computation, methodology-version provenance chain, strict CSV mirror semantics — are all implemented and covered by tests. The manifest round-trip / determinism / SHA-match tests are particularly strong guards against the adversarial-proofing risks called out in the planning docs.

Two structural gaps nonetheless undermine the end-to-end reproducibility story:

1. **Refresh is incomplete.** `cfd._refresh.refresh()` only re-fetches LCCC datasets. Elexon and ONS are explicitly deferred "to Plan 04-05's orchestrator" — but `refresh_all.py` (Plan 04-05) does not re-fetch them either. More critically, **no refresh path updates the `.meta.json` sidecars**. Because `upstream_changed()` compares live SHA against sidecar SHA, and `generated_at` sources from `max(sidecar.retrieved_at)`, the daily workflow will either (a) never advance `generated_at` after a raw-file change, or (b) perpetually report "upstream changed" because sidecar SHA stays stale.
2. **`ons_gas.download_dataset()` has an unconditional `UnboundLocalError`** on any network failure — the fallback path references a variable that is only assigned after a successful request.

The GitHub Actions workflows are well-scoped (minimum permissions, pinned major versions, release-tag regex validation). Security posture is sound.

All other findings are code-quality / robustness concerns that do not block the phase from shipping but should be addressed before v1.0.0 public release.

## Critical Issues

### CR-01: `UnboundLocalError` in ONS gas downloader exception path

**File:** `src/uk_subsidy_tracker/data/ons_gas.py:31-44`
**Issue:** `output_path` is assigned at line 35 *inside* the `try` block, *after* `requests.get()` on line 32. If the network call raises `requests.exceptions.RequestException`, control jumps to the `except` block at line 42 where `return output_path` (line 44) references a variable that was never bound. The function raises `UnboundLocalError` instead of the intended graceful degradation. This path is exercised precisely when the upstream ONS endpoint is down — the moment you most need the error handler to behave.

Additionally, the function signature declares `-> Path` but the bare `print(...); return output_path` pattern both hides the error from the refresh workflow (no re-raise, no False/None signal) and corrupts the contract. The LCCC downloader (referenced in CLAUDE.md §Error Handling) has the same shape, but at least its `output_path` is defined before the `try`.

**Fix:**
```python
def download_dataset() -> Path:
    """Download a file from a URL and save it to the data directory."""
    GAS_SAP_URL = "https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/output/datasets/systemaveragepricesapofgas/2026/systemaveragepriceofgasdataset160426.xlsx"
    output_path = DATA_DIR / GAS_SAP_DATA_FILENAME  # assign BEFORE the try

    try:
        response = requests.get(GAS_SAP_URL, headers=HEADERS, stream=True, timeout=60)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise  # don't silently return a non-downloaded path to downstream
```
Also add a `timeout=` argument to the `requests.get()` call (Elexon loaders use `timeout=60` — match the convention).

## Warnings

### WR-01: Daily refresh never updates `.meta.json` sidecars — breaks `generated_at` stability guarantee

**File:** `src/uk_subsidy_tracker/schemes/cfd/_refresh.py:53-67`, `src/uk_subsidy_tracker/refresh_all.py:42-63`
**Issue:** `refresh()` re-fetches only LCCC datasets (via `download_lccc_datasets`). Elexon + ONS are deferred in a comment ("delegated to Plan 04-05's refresh_all.py orchestrator") — but `refresh_all.py`'s `refresh_scheme()` just calls `scheme_module.refresh()` and never fetches Elexon/ONS itself. More importantly, **no code path updates `.meta.json` sidecars after a successful download.** The `scripts/backfill_sidecars.py` is a one-shot migration script.

Consequences:
1. `upstream_changed()` compares live SHA against sidecar SHA (line 48). After a real upstream change, `download_lccc_datasets` rewrites the CSV; the sidecar SHA is now stale. On the *next* refresh-workflow run, `upstream_changed()` returns True again, the pipeline re-rebuilds everything, and the daily PR carries a no-op diff. This repeats forever.
2. `manifest.py::_latest_retrieved_at` (line 208) sources `generated_at` from `max(sidecar.retrieved_at)` (Pitfall 3 mitigation). If sidecars never advance, `generated_at` is frozen at the backfill date even as raw files update. The "content-addressed timestamp" guarantee breaks.
3. The `test_manifest_generated_at_stable_when_no_upstream_change` test only verifies stability when raw files are unchanged — it does not catch the missing-advance bug.

**Fix:** Implement an end-to-end refresh that (a) calls the Elexon + ONS downloaders, (b) recomputes SHA on every raw file after download, (c) writes a sibling `.meta.json` with fresh `retrieved_at` (UTC now, ISO-8601) + fresh `sha256` + HTTP status captured from the response. Factor the sidecar-write helper out of `backfill_sidecars.py` into `uk_subsidy_tracker.data.sidecar` so both the backfill script and the live refresh use one implementation. Until this lands, document the gap prominently — the refresh.yml workflow will generate daily PRs of zero utility.

### WR-02: `build_forward_projection` mutates `gen` after loading, breaking copy-on-read invariant

**File:** `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py:45-65`
**Issue:** `load_lccc_dataset(...)` returns a pandas DataFrame; downstream callers that share a module-level cache could observe mutations. Line 66 does `gen_year = gen.copy()`, but line 57 assigns `units["contract_years"] = ...` on `units` (derived via `cap.merge(first_gen, ...)` — a fresh object, safe). However, line 47 does `cap = cap.rename(columns={"CFD_ID": "CfD_ID"})` — pandas `rename` without `inplace=True` returns a new DataFrame (safe), but `cost_model.py:132` does the same rename on portfolio, and `build_by_allocation_round` in `aggregation.py:183` does yet another rename. If `load_lccc_dataset` caches the DataFrame (it doesn't appear to, based on the read, but `cost_model.py:92-93` adds `.copy()` defensively while `forward_projection.py:45-46` does not), an iteration order where `forward_projection` runs after the other grains could see already-renamed columns. Currently safe because each call hits `pd.read_csv` fresh, but this is fragile and inconsistent.

**Fix:** Match `cost_model.py`'s defensive pattern — `.copy()` at load time in every grain builder that plans to mutate columns:
```python
gen = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions").copy()
cap = load_lccc_dataset("CfD Contract Portfolio Status").copy()
```
Or (better) have `load_lccc_dataset` itself return a fresh copy on every call and document this in its docstring.

### WR-03: `manifest._site_url` line-scan is fragile on mkdocs.yml formatting

**File:** `src/uk_subsidy_tracker/publish/manifest.py:172-199`
**Issue:** The heuristic YAML reader only matches lines that `startswith("site_url:")` at column 0. This breaks silently under any of:
- Commented-out line: `# site_url: https://...` — fine (caught by startswith), but a `#site_url:` typo slips through (ignored).
- Indented top-level (some YAML formatters indent the first key) — key missed, raises "not found".
- Multiline string: `site_url: >\n  https://...` — captures `>` as the URL.
- Quoted key: `"site_url":` (valid YAML) — missed.
- Trailing comment on the value line: `site_url: https://foo  # prod` — comment swallowed into the URL.

The rationale in the docstring (custom Python tags reject safe_load) is correct, but a narrower fix exists: parse the file with `yaml.safe_load` after filtering out the offending Python-tag lines, or use `yaml.SafeLoader` + register a no-op handler for `!!python/name:`. Simplest defensive fix: require `SITE_URL` env var in any CI/build context and make the line-scan a local-dev convenience only.

**Fix:** Either (a) set `SITE_URL` in `refresh.yml` and `deploy.yml` explicitly so CI never hits the line-scan path, or (b) strip trailing `#` comments and reject multiline values:
```python
for line in mkdocs_path.read_text().splitlines():
    if line.startswith("site_url:"):
        _, _, rhs = line.partition(":")
        # Strip inline comment + quotes.
        rhs = rhs.split("#", 1)[0].strip().strip('"').strip("'")
        if rhs and not rhs.startswith(("|", ">")):
            site_url = rhs
        break
```

### WR-04: `forward_projection` anchor year crashes on empty/all-NaT generation data

**File:** `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py:99`
**Issue:** `int(gen["Settlement_Date"].max().year)` — if `gen` is empty or all `Settlement_Date` rows are NaT, `.max()` returns `NaT`, and `NaT.year` raises `AttributeError`. More subtly, if `Settlement_Date` is object dtype (e.g. CSV-parse regression), `.max()` returns the lexically greatest string. The determinism guarantee ("pure function of raw input") is fine, but the function has no defensive fallback. Compare to `aggregation.py::build_annual_summary` which `dropna`s first (line 81) — `forward_projection` dropna happens only for the contract columns (line 102), not `Settlement_Date`.

**Fix:** Filter `gen` to non-null Settlement_Date before computing the anchor, and raise a clear error when empty:
```python
gen_with_dates = gen.dropna(subset=["Settlement_Date"])
if gen_with_dates.empty:
    raise ValueError(
        "forward_projection: no rows with valid Settlement_Date — cannot derive anchor year"
    )
current_year_anchor = int(gen_with_dates["Settlement_Date"].max().year)
```

### WR-05: `test_parquet_grain_schema` row-level validation hides partial-failure detail

**File:** `tests/test_schemas.py:124-125`
**Issue:** The loop validates each row via `model.model_validate(row)`. On the first failure, Pydantic raises `ValidationError` and pytest stops — but the error message shows only that one row. With 15-20k station_month rows, root-causing requires bisecting. Also, `to_dict(orient="records")` materialises every row into a Python dict with pandas.Timestamp objects; `StationMonthRow.month_end: date` coerces from Timestamp but the silent coercion hides dtype drift (a Timestamp leaking into a `date` field would be caught by a stricter validator but currently passes).

**Fix:** Track the failing index and surface it in the assertion message:
```python
errors = []
for idx, row in enumerate(df.to_dict(orient="records")):
    try:
        model.model_validate(row)
    except Exception as e:
        errors.append((idx, str(e)))
        if len(errors) >= 5:
            break
assert not errors, f"{grain}: row-validation failed for {len(errors)} rows (showing first 5):\n" + "\n".join(f"  row {i}: {m}" for i, m in errors)
```

### WR-06: `softprops/action-gh-release@v2` and `peter-evans/*` pinned to floating majors

**File:** `.github/workflows/deploy.yml:53`, `.github/workflows/refresh.yml:64, 85`
**Issue:** `softprops/action-gh-release@v2`, `peter-evans/create-pull-request@v8`, and `peter-evans/create-issue-from-file@v6` are pinned to major-version tags. These are mutable refs — the maintainer can retag, and a supply-chain compromise would silently update the action used at every run. The project's adversarial-proofing bar is explicit about traceability; release-asset signing and PR-body construction are both privileged operations (they touch `contents: write` and `pull-requests: write`).

Note: `actions/checkout@v5` and `astral-sh/setup-uv@v8.1.0` have the same property — `v5` is a floating major; `v8.1.0` is a pinned minor but still a tag (mutable).

**Fix:** Pin every action to its immutable commit SHA (`@<40-hex>`) and add a comment showing the human-readable version. GitHub's Dependabot can manage updates by PR. Example:
```yaml
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v5 (2025-10-15)
```
For a project whose core value proposition is "every number traceable", the same discipline belongs in the CI pipeline.

## Info

### IN-01: `backfill_sidecars.py::BACKFILL_DATE` hardcoded to today's date

**File:** `scripts/backfill_sidecars.py:23`
**Issue:** `BACKFILL_DATE = "2026-04-22"` is a calendar constant. Re-running this script after today recomputes SHAs + rewrites `retrieved_at` from git-log but stamps `backfilled_at` to a stale date. Low impact (the field is purely audit), but a re-run after a git-rename operation would want the fresh run date.
**Fix:** `BACKFILL_DATE = date.today().isoformat()` using `from datetime import date`.

### IN-02: `refresh_all.publish_latest` copies files via `read_bytes()` / `write_bytes()` instead of `shutil.copy2`

**File:** `src/uk_subsidy_tracker/refresh_all.py:80`
**Issue:** `dst_path.write_bytes(path.read_bytes())` reads the entire file into memory. For Parquet files this is fine (<10 MB each), but the pattern loses file metadata (mtime, mode) that `shutil.copy2` preserves. Determinism-wise content is identical, so no correctness issue.
**Fix:** Use `shutil.copy2(path, dst_path)` for clarity and preserved metadata.

### IN-03: Counterfactual import coupling in `manifest._read_methodology_version`

**File:** `src/uk_subsidy_tracker/publish/manifest.py:202-205`
**Issue:** The helper does a local import inside a tiny function. Fine for avoiding circular imports, but the docstring doesn't explain which direction the cycle would go. Reading: `publish.manifest` → `counterfactual` is acyclic (counterfactual imports nothing from publish). The local import is defensive but unmotivated.
**Fix:** Move to top-of-file imports unless there's a documented reason for the lazy import. If there is, state it in the helper's docstring.

### IN-04: `_versioned_segment` is a pass-through with a 7-line docstring

**File:** `src/uk_subsidy_tracker/publish/manifest.py:275-282`
**Issue:** The function just returns its argument. If no transformation is ever expected, inline the expression into `_assemble_dataset_entries` and drop the helper.
**Fix:** Remove the helper; replace `vseg = _versioned_segment(version)` with `vseg = version`. Move the D-14 documentation note to the `build()` docstring.

### IN-05: `pyproject.toml` missing dev-dependencies group

**File:** `pyproject.toml`
**Issue:** `pytest`, `pandera` (used heavily in tests), and the dev-only chain (e.g. pyright) live in the top-level `dependencies` list rather than `[project.optional-dependencies]` or `[dependency-groups]`. Every `uv sync` installs them — fine for this project, but a consumer who wants the library-only surface can't opt out.
**Fix:** Optional. Move test-only deps (pytest, kaleido if only used for chart export) to `[project.optional-dependencies.dev]` and have CI do `uv sync --extra dev`.

### IN-06: CLAUDE.md Python version mismatch with pyproject.toml

**File:** `CLAUDE.md` (top of file, multiple references to "Python 3.11+") vs `pyproject.toml:5` (`requires-python = ">=3.12"`)
**Issue:** CLAUDE.md says "Python 3.11+" in several places; `pyproject.toml` requires ≥3.12; `pyrightconfig.json` (per CLAUDE.md) targets 3.11. The project charter in CLAUDE.md §Constraints also says "Python 3.12+ only". Cosmetic inconsistency; 3.12 is the source of truth.
**Fix:** Update CLAUDE.md references to 3.12+. Out-of-scope for Phase 4 but worth noting.

### IN-07: `tests/fixtures/__init__.py::load_benchmarks` mutates input dict during iteration

**File:** `tests/fixtures/__init__.py:71-76`
**Issue:** The loop over `raw.items()` writes into `entry["source"]` before handing `raw` to the Pydantic constructor. This works (we're mutating the list elements, not `raw` itself), but it is a subtle contract. A future refactor that reads `raw` downstream would see injected `source` fields. Tests pass today.
**Fix:** Make a deep copy before mutation or construct the Pydantic models directly without round-tripping through the mutated dict:
```python
processed = {
    key: [{**entry, "source": key} for entry in entries]
    for key, entries in raw.items()
    if isinstance(entries, list)
}
return Benchmarks(**processed)
```

---

_Reviewed: 2026-04-22T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
