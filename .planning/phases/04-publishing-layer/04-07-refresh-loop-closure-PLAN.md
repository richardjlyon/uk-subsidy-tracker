---
phase: 04-publishing-layer
plan: 07
type: execute
wave: 1
depends_on: []
gap_closure: true
gap_closure_source: .planning/phases/04-publishing-layer/04-VERIFICATION.md
autonomous: true
requirements: [GOV-03, PUB-05]

files_modified:
  - src/uk_subsidy_tracker/data/sidecar.py            # NEW — shared atomic sidecar writer
  - src/uk_subsidy_tracker/data/ons_gas.py            # FIX — UnboundLocalError + timeout=60 + fail-loud raise (D-17)
  - src/uk_subsidy_tracker/schemes/cfd/_refresh.py    # FIX — refresh() now fetches LCCC + Elexon + ONS + writes sidecars
  - scripts/backfill_sidecars.py                      # REFACTOR — call into sidecar.write_sidecar() for meta-shape parity
  - tests/test_refresh_loop.py                        # NEW — refresh-loop invariant test
  - tests/test_ons_gas_download.py                    # NEW — ons_gas error-path regression test
  - CHANGES.md                                        # [Unreleased] entries for 04-07

must_haves:
  truths:
    # Verbatim from 04-VERIFICATION.md gap #1 "missing:" lines
    - "End-to-end refresh helper that fetches LCCC + Elexon + ONS and rewrites .meta.json sidecars (shared helper extracted from scripts/backfill_sidecars.py)"
    - "Call sites in refresh_all.refresh_scheme() (or scheme_module.refresh() of each scheme) that invoke Elexon + ONS downloaders"
    - "Test covering the refresh loop invariant: after a simulated upstream change, running refresh_all twice produces generated_at that advances once and stays stable on the second run"
    # Verbatim from 04-VERIFICATION.md gap #2 "missing:" lines
    - "Assign output_path BEFORE the try block"
    - "Either re-raise or return None/False on failure — never silently return a non-downloaded path"
    - "Add timeout=60 to requests.get() to match the Elexon convention"
  artifacts:
    - path: "src/uk_subsidy_tracker/data/sidecar.py"
      provides: "write_sidecar(raw_path, upstream_url, http_status, publisher_last_modified) -> Path; atomic write via .tmp + os.replace; byte-identical serialisation to scripts/backfill_sidecars.py (sort_keys=True, indent=2, trailing newline)"
      min_lines: 40
      exports: ["write_sidecar"]
    - path: "src/uk_subsidy_tracker/data/ons_gas.py"
      provides: "download_dataset() with output_path bound BEFORE try, timeout=60 on requests.get, raise on network failure (D-17 fail-loud)"
      contains: "timeout=60"
    - path: "src/uk_subsidy_tracker/schemes/cfd/_refresh.py"
      provides: "refresh() fetches LCCC + Elexon + ONS and calls write_sidecar() for each of the five _RAW_FILES after successful download"
      contains: "write_sidecar"
    - path: "tests/test_refresh_loop.py"
      provides: "Invariant test: after simulated upstream change, running refresh_all twice produces generated_at that advances once and stays stable on the second run"
      min_lines: 60
    - path: "tests/test_ons_gas_download.py"
      provides: "Regression test: download_dataset() raises (not UnboundLocalError) when requests.get raises ConnectionError"
      min_lines: 20
  key_links:
    - from: "src/uk_subsidy_tracker/schemes/cfd/_refresh.py::refresh()"
      to: "src/uk_subsidy_tracker/data/elexon.py::download_elexon_data + src/uk_subsidy_tracker/data/ons_gas.py::download_dataset"
      via: "direct function calls inside refresh() body"
      pattern: "download_elexon_data\\(|ons_gas\\.download_dataset\\("
    - from: "src/uk_subsidy_tracker/schemes/cfd/_refresh.py::refresh()"
      to: "src/uk_subsidy_tracker/data/sidecar.py::write_sidecar"
      via: "import + per-file call after each download"
      pattern: "write_sidecar\\("
    - from: "scripts/backfill_sidecars.py"
      to: "src/uk_subsidy_tracker/data/sidecar.py::write_sidecar"
      via: "refactor — reduce duplication; backfill script keeps the `backfilled_at` marker it owns"
      pattern: "from uk_subsidy_tracker\\.data\\.sidecar import|write_sidecar\\("
---

<objective>
Close the two Partial/Failed observable truths identified in `.planning/phases/04-publishing-layer/04-VERIFICATION.md`:

1. **Gap #1 (structural — SC #5 / GOV-03):** `schemes/cfd/_refresh.py::refresh()` only re-fetches LCCC. Elexon and ONS downloaders are never invoked, and no code path rewrites `.meta.json` sidecars after a successful download. On any real upstream change, `upstream_changed()` returns True perpetually (sidecar SHA stays stale) and `manifest.generated_at` (sourced from `max(sidecar.retrieved_at)`) never advances.

2. **Gap #2 (code bug — PUB-05 / GOV-03 error resilience):** `src/uk_subsidy_tracker/data/ons_gas.py::download_dataset()` raises `UnboundLocalError` on network failure because `output_path` is bound inside the `try` block but returned in the `except` handler. Also missing `timeout=60` on `requests.get()` (the Elexon convention).

**Architecture choice (Option A — scheme owns its raw files):** `scheme.refresh()` is the single responsibility point. Each `schemes/<scheme>/_refresh.py::refresh()` calls its three downloaders AND writes sidecars. Rationale: Phase 5 RO will copy this pattern; centralising the sidecar rewrite in `refresh_all.py` would require every scheme to expose its sidecar path list — a weaker contract than "the scheme owns its raw tree and its provenance." This preserves the ARCHITECTURE §4.1 substrate: `data/raw/<publisher>/<file>.meta.json` is owned by the scheme that consumes those files.

**Error-handling posture (per CONTEXT D-17 "Fail-loud on errors"):** `ons_gas.download_dataset()` re-raises on network failure instead of silently returning an un-downloaded path. The current LCCC silent-swallow pattern is a pre-existing latent bug and is **out of scope for this plan** (verifier scoped the fix to ons_gas only; a follow-up audit may align lccc.py later).

Purpose: Make the refresh-loop invariant — "on upstream change, manifest.generated_at advances once and stays stable on a subsequent unchanged run" — a tested and enforced property, so GOV-03's "functional" claim survives the first real upstream publication. Ship a reusable `write_sidecar()` helper so Phase 5+ schemes inherit correct provenance discipline by default.

Output: 1 new helper module, 2 file fixes, 1 helper-refactor, 2 new test files, 1 CHANGES.md [Unreleased] entry. No new requirements introduced — only closes existing coverage on GOV-03 + PUB-05.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/phases/04-publishing-layer/04-CONTEXT.md
@.planning/phases/04-publishing-layer/04-VERIFICATION.md
@.planning/phases/04-publishing-layer/04-05-SUMMARY.md
@CLAUDE.md

# Target files (read BEFORE any edits)
@src/uk_subsidy_tracker/schemes/cfd/_refresh.py
@src/uk_subsidy_tracker/schemes/cfd/__init__.py
@src/uk_subsidy_tracker/data/ons_gas.py
@src/uk_subsidy_tracker/data/lccc.py
@src/uk_subsidy_tracker/data/elexon.py
@src/uk_subsidy_tracker/refresh_all.py
@scripts/backfill_sidecars.py
@src/uk_subsidy_tracker/publish/manifest.py

<interfaces>
<!-- Contracts the executor must honour. No codebase exploration needed beyond these. -->

Sidecar JSON shape (ARCHITECTURE §4.1, fixed — do NOT churn):
```json
{
  "retrieved_at": "2026-04-22T00:00:00+00:00",   // ISO-8601 with offset
  "upstream_url": "https://...",
  "sha256": "<64-char lowercase hex>",
  "http_status": 200,                             // null for backfill
  "publisher_last_modified": null                 // or string if upstream supplies it
}
```

Serialisation invariant (must match scripts/backfill_sidecars.py byte-for-byte on common keys):
```python
meta_path.write_text(
    json.dumps(meta, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
```

Existing _RAW_FILES list in `schemes/cfd/_refresh.py` (authoritative list — reuse, do NOT redefine):
```python
_RAW_FILES = [
    "raw/lccc/actual-cfd-generation.csv",
    "raw/lccc/cfd-contract-portfolio-status.csv",
    "raw/elexon/agws.csv",
    "raw/elexon/system-prices.csv",
    "raw/ons/gas-sap.xlsx",
]
```

URL map (mirror from scripts/backfill_sidecars.py::URL_MAP — consistency across the two writers):
```python
# Already defined in scripts/backfill_sidecars.py — the refactor should expose
# this via the shared sidecar module OR keep URL_MAP as the scheme's
# responsibility. The plan chooses the latter for locality (see Task 3).
```

Elexon timeout convention (src/uk_subsidy_tracker/data/elexon.py lines 68 + 104):
```python
resp = requests.get(..., timeout=60)
```

The LCCC download function signature (already exists; refresh calls it unchanged):
```python
def download_lccc_datasets(config: LCCCAppConfig) -> None: ...
```

Elexon download function signature (already exists; refresh calls it):
```python
def download_elexon_data(start: date = date(2017, 1, 1), end: date | None = None) -> None: ...
```

ONS download function signature (will be fixed in Task 2):
```python
def download_dataset() -> Path: ...   # after fix: raises RequestException on failure instead of returning unbound path
```
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create src/uk_subsidy_tracker/data/sidecar.py with atomic write_sidecar()</name>
  <files>src/uk_subsidy_tracker/data/sidecar.py</files>

  <read_first>
    - scripts/backfill_sidecars.py  (SOURCE-OF-TRUTH for sidecar serialisation — sha256_of(), json.dumps kwargs, trailing newline, URL_MAP contents)
    - src/uk_subsidy_tracker/__init__.py  (DATA_DIR + PROJECT_ROOT exports — for consistent import pattern)
    - src/uk_subsidy_tracker/data/__init__.py  (current barrel — decide whether to re-export write_sidecar from data package)
  </read_first>

  <action>
    Create `src/uk_subsidy_tracker/data/sidecar.py` (new module). The module MUST expose exactly one public function:

    ```python
    """Shared sidecar writer for data/raw/<publisher>/<file>.meta.json (ARCHITECTURE §4.1).

    Called by:
    - src/uk_subsidy_tracker/schemes/cfd/_refresh.py::refresh()  (daily refresh path)
    - scripts/backfill_sidecars.py                               (one-shot reconstruction)

    Atomicity: writes to `<path>.meta.json.tmp` then `os.replace()`s. On crash
    mid-write, either the old sidecar survives intact or the new sidecar is
    fully present — never a partial JSON document.

    Serialisation byte-parity: `json.dumps(meta, sort_keys=True, indent=2) + "\n"`.
    Matches scripts/backfill_sidecars.py output on the common keys so
    test_manifest round-trip determinism holds regardless of which writer
    produced the sidecar.
    """
    from __future__ import annotations

    import hashlib
    import json
    import os
    from datetime import datetime, timezone
    from pathlib import Path


    def _sha256_of(path: Path) -> str:
        """64 KiB chunked SHA-256 (matches schemes/cfd/_refresh.py::_sha256 and
        scripts/backfill_sidecars.py::sha256_of exactly)."""
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 16), b""):
                h.update(chunk)
        return h.hexdigest()


    def write_sidecar(
        raw_path: Path,
        upstream_url: str,
        http_status: int | None = 200,
        publisher_last_modified: str | None = None,
    ) -> Path:
        """Write a `.meta.json` sidecar alongside `raw_path` atomically.

        Fields (ARCHITECTURE §4.1 verbatim — do NOT add `backfilled_at` here;
        that key is exclusive to scripts/backfill_sidecars.py which owns the
        reconstruction marker):
            retrieved_at            : ISO-8601 with offset (datetime.now(UTC))
            upstream_url            : the URL that was fetched
            sha256                  : computed from raw_path content
            http_status             : 200 for live fetches; None on backfill
            publisher_last_modified : from upstream headers if available, else None

        Returns the path to the written sidecar (<raw_path>.meta.json).

        Raises FileNotFoundError if `raw_path` does not exist (cannot compute SHA).
        """
        if not raw_path.exists():
            raise FileNotFoundError(
                f"Cannot write sidecar — raw file missing: {raw_path}"
            )
        meta = {
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "upstream_url": upstream_url,
            "sha256": _sha256_of(raw_path),
            "http_status": http_status,
            "publisher_last_modified": publisher_last_modified,
        }
        meta_path = raw_path.with_suffix(raw_path.suffix + ".meta.json")
        tmp_path = meta_path.with_suffix(meta_path.suffix + ".tmp")
        # Write to .tmp, then os.replace (atomic on POSIX + Windows).
        tmp_path.write_text(
            json.dumps(meta, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(tmp_path, meta_path)
        return meta_path


    __all__ = ["write_sidecar"]
    ```

    DO NOT re-export `write_sidecar` from `src/uk_subsidy_tracker/data/__init__.py` — the existing barrel only exports loaders; keep the sidecar writer import-explicit to reinforce that callers consciously reach for the provenance-writing layer.

    Commit message: `feat(04-07): add sidecar.write_sidecar() atomic helper`.
  </action>

  <verify>
    <automated>test -f src/uk_subsidy_tracker/data/sidecar.py && grep -n "def write_sidecar" src/uk_subsidy_tracker/data/sidecar.py && grep -c "sort_keys=True" src/uk_subsidy_tracker/data/sidecar.py && grep -c "os.replace" src/uk_subsidy_tracker/data/sidecar.py && uv run python -c "from uk_subsidy_tracker.data.sidecar import write_sidecar; print('ok')"</automated>
  </verify>

  <acceptance_criteria>
    - `src/uk_subsidy_tracker/data/sidecar.py` exists and is at least 40 non-blank lines
    - `grep -n "def write_sidecar" src/uk_subsidy_tracker/data/sidecar.py` returns a match on a line that shows the exact signature `def write_sidecar(raw_path: Path, upstream_url: str, http_status: int | None = 200, publisher_last_modified: str | None = None) -> Path:`
    - `grep -c "sort_keys=True" src/uk_subsidy_tracker/data/sidecar.py` returns at least 1
    - `grep -c 'indent=2' src/uk_subsidy_tracker/data/sidecar.py` returns at least 1
    - `grep -c 'os.replace' src/uk_subsidy_tracker/data/sidecar.py` returns at least 1 (atomicity)
    - `grep -c 'datetime.now(timezone.utc)' src/uk_subsidy_tracker/data/sidecar.py` returns at least 1 (UTC retrieved_at)
    - `grep -c 'backfilled_at' src/uk_subsidy_tracker/data/sidecar.py` returns 0 (that field is exclusive to the backfill script)
    - `uv run python -c "from uk_subsidy_tracker.data.sidecar import write_sidecar; print('ok')"` exits 0 with output `ok`
    - The module is NOT re-exported from `src/uk_subsidy_tracker/data/__init__.py` (grep `write_sidecar` in that barrel returns 0 matches)
    - Docstring mentions both call sites (scheme refresh AND backfill script)
  </acceptance_criteria>

  <done>
    `write_sidecar()` is a one-argument-plus-optional-kwargs callable that produces a byte-identical sidecar to `scripts/backfill_sidecars.py` on the five common keys; atomicity verified by code inspection (`.tmp` + `os.replace`); importable from `uk_subsidy_tracker.data.sidecar`.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Fix ons_gas.download_dataset() error path + add timeout + fail-loud</name>
  <files>src/uk_subsidy_tracker/data/ons_gas.py, tests/test_ons_gas_download.py</files>

  <read_first>
    - src/uk_subsidy_tracker/data/ons_gas.py   (current bug — lines 26–44 verbatim; confirm the UnboundLocalError path)
    - src/uk_subsidy_tracker/data/elexon.py    (source of `timeout=60` convention — lines 68, 104)
    - .planning/phases/04-publishing-layer/04-CONTEXT.md  (D-17 "Fail-loud on errors. Scrape failures … fail the workflow job — no silent skips")
    - tests/test_schemas.py                     (pandera-fixture pattern for mocking requests)
  </read_first>

  <behavior>
    - Test 1 (RED first): `tests/test_ons_gas_download.py::test_download_dataset_raises_on_network_failure` — patches `requests.get` to raise `ConnectionError`; asserts `download_dataset()` raises `requests.exceptions.RequestException` (or subclass). MUST NOT raise `UnboundLocalError`.
    - Test 2: `test_download_dataset_uses_timeout` — patches `requests.get` to record kwargs; runs `download_dataset()` inside a tmp_path (monkeypatch `DATA_DIR`); asserts `timeout=60` was passed.
    - Test 3 (optional smoke): `test_download_dataset_returns_path_on_success` — patches `requests.get` to return a mock response with 10 bytes of content; asserts `download_dataset()` returns `DATA_DIR / GAS_SAP_DATA_FILENAME` and the file exists with those bytes.
  </behavior>

  <action>
    **Step A — write the regression test FIRST (RED state).** Create `tests/test_ons_gas_download.py`:

    ```python
    """Regression guard for ons_gas.download_dataset() error-path.

    Gap #2 in .planning/phases/04-publishing-layer/04-VERIFICATION.md:
    `output_path` was assigned inside the try block but the except handler
    returned it — UnboundLocalError on any network failure. Exercised
    precisely when the ONS publisher is unavailable, i.e. when the
    'methodologically bulletproof' promise is being tested.

    This test pins the D-17 'fail-loud' posture: network failure raises a
    RequestException (the workflow job fails loud, opens a refresh-failure
    issue), never UnboundLocalError, never a silent un-downloaded path.
    """
    from __future__ import annotations

    from unittest.mock import MagicMock, patch

    import pytest
    import requests

    from uk_subsidy_tracker.data import ons_gas


    def test_download_dataset_raises_on_network_failure(tmp_path, monkeypatch):
        """Network failure must propagate as RequestException, not UnboundLocalError."""
        monkeypatch.setattr(ons_gas, "DATA_DIR", tmp_path)
        (tmp_path / "raw" / "ons").mkdir(parents=True, exist_ok=True)
        with patch("uk_subsidy_tracker.data.ons_gas.requests.get",
                   side_effect=requests.exceptions.ConnectionError("boom")):
            with pytest.raises(requests.exceptions.RequestException):
                ons_gas.download_dataset()


    def test_download_dataset_uses_timeout(tmp_path, monkeypatch):
        """Every requests.get call MUST carry timeout=60 (Elexon convention)."""
        monkeypatch.setattr(ons_gas, "DATA_DIR", tmp_path)
        (tmp_path / "raw" / "ons").mkdir(parents=True, exist_ok=True)
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"hello"]
        mock_response.raise_for_status.return_value = None
        with patch("uk_subsidy_tracker.data.ons_gas.requests.get",
                   return_value=mock_response) as mock_get:
            ons_gas.download_dataset()
        call_kwargs = mock_get.call_args.kwargs
        assert call_kwargs.get("timeout") == 60, (
            f"ons_gas.download_dataset() must pass timeout=60; got {call_kwargs.get('timeout')!r}"
        )


    def test_download_dataset_returns_path_on_success(tmp_path, monkeypatch):
        """Happy path: return the path; file exists with downloaded bytes."""
        monkeypatch.setattr(ons_gas, "DATA_DIR", tmp_path)
        (tmp_path / "raw" / "ons").mkdir(parents=True, exist_ok=True)
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"xlsx-bytes-stub"]
        mock_response.raise_for_status.return_value = None
        with patch("uk_subsidy_tracker.data.ons_gas.requests.get",
                   return_value=mock_response):
            path = ons_gas.download_dataset()
        assert path == tmp_path / ons_gas.GAS_SAP_DATA_FILENAME
        assert path.exists()
        assert path.read_bytes() == b"xlsx-bytes-stub"
    ```

    Run `uv run pytest tests/test_ons_gas_download.py -x` — expect 3 failures (UnboundLocalError on test 1, timeout assertion fail on test 2, test 3 may or may not fail depending on which line errors first). This is RED.

    **Step B — fix `src/uk_subsidy_tracker/data/ons_gas.py` to GREEN.** Replace the `download_dataset()` function body with:

    ```python
    def download_dataset() -> Path:
        """Download the latest ONS SAP gas dataset to the data directory.

        Raises requests.exceptions.RequestException on any network failure
        (D-17 fail-loud posture — the daily refresh workflow needs to see
        the failure, not a silently un-downloaded path).
        """
        # The official ONS file URI for the latest SAP gas dataset
        GAS_SAP_URL = "https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/output/datasets/systemaveragepricesapofgas/2026/systemaveragepriceofgasdataset160426.xlsx"

        output_path = DATA_DIR / GAS_SAP_DATA_FILENAME  # BOUND BEFORE try (gap #2 fix)

        try:
            response = requests.get(GAS_SAP_URL, headers=HEADERS, stream=True, timeout=60)
            response.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return output_path
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while downloading ons_gas: {e}")
            raise  # fail loud per D-17 — no silent swallow
    ```

    Re-run `uv run pytest tests/test_ons_gas_download.py -x` — expect 3 passing tests. This is GREEN.

    Run the full suite `uv run pytest tests/ -q` to confirm no regressions (expect 72 passed + 4 skipped, up from 69 passed + 4 skipped).

    Commit message: `fix(04-07): ons_gas download error-path + timeout=60 (gap #2)`.
  </action>

  <verify>
    <automated>uv run pytest tests/test_ons_gas_download.py -v && grep -c "timeout=60" src/uk_subsidy_tracker/data/ons_gas.py && grep -B1 "try:" src/uk_subsidy_tracker/data/ons_gas.py | grep "output_path = DATA_DIR" && grep -c "raise$" src/uk_subsidy_tracker/data/ons_gas.py</automated>
  </verify>

  <acceptance_criteria>
    - `tests/test_ons_gas_download.py` exists, at least 20 non-blank lines
    - `uv run pytest tests/test_ons_gas_download.py -v` exits 0 with 3 passing tests
    - `grep -c "timeout=60" src/uk_subsidy_tracker/data/ons_gas.py` returns at least 1
    - `src/uk_subsidy_tracker/data/ons_gas.py` contains the line `output_path = DATA_DIR / GAS_SAP_DATA_FILENAME` AT A LINE NUMBER LOWER than the `try:` keyword (verify with `grep -n "output_path = DATA_DIR\|try:" src/uk_subsidy_tracker/data/ons_gas.py | head -4` — the output_path line must appear BEFORE try in the ordering)
    - The `except` block re-raises: `grep -nE "^[[:space:]]+raise$" src/uk_subsidy_tracker/data/ons_gas.py` returns at least 1 match inside the except clause (bare `raise`)
    - The `except` block does NOT contain `return output_path` (the unbound-variable bug is removed): `grep -c "return output_path" src/uk_subsidy_tracker/data/ons_gas.py` returns exactly 1 (only the happy-path return inside the try)
    - Full suite stays green: `uv run pytest tests/ -q` exits 0 with `72 passed` (3 new tests added) + 4 skipped
  </acceptance_criteria>

  <done>
    ons_gas.download_dataset() cannot raise UnboundLocalError; network failure raises RequestException (fail-loud per D-17); `timeout=60` matches the Elexon convention; happy-path return unchanged; regression test locks the three invariants.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Wire Elexon + ONS into scheme.refresh() + write sidecars after each download</name>
  <files>src/uk_subsidy_tracker/schemes/cfd/_refresh.py</files>

  <read_first>
    - src/uk_subsidy_tracker/schemes/cfd/_refresh.py   (current refresh() — LCCC-only; _RAW_FILES list authoritative)
    - src/uk_subsidy_tracker/data/lccc.py              (download_lccc_datasets signature)
    - src/uk_subsidy_tracker/data/elexon.py            (download_elexon_data signature)
    - src/uk_subsidy_tracker/data/ons_gas.py           (download_dataset signature AFTER Task 2 fix)
    - scripts/backfill_sidecars.py                     (URL_MAP — SOURCE-OF-TRUTH for upstream URLs; MUST match to-the-byte)
    - src/uk_subsidy_tracker/data/sidecar.py           (write_sidecar signature from Task 1)
  </read_first>

  <behavior>
    After this task, `schemes/cfd/_refresh.py::refresh()` MUST:
    1. Call `download_lccc_datasets(config)` (already present — keep).
    2. Call `download_elexon_data()` (NEW — was not being invoked).
    3. Call `ons_gas.download_dataset()` (NEW — was not being invoked).
    4. For EACH of the five paths in `_RAW_FILES`: call `write_sidecar(raw_path=DATA_DIR / rel, upstream_url=URL_MAP[rel])` — so post-refresh, sidecar SHA matches the live raw bytes AND `retrieved_at` advances to now().
    5. If ANY downloader raises, `refresh()` propagates the exception (fail-loud per D-17). Sidecars for the files that DID succeed may or may not have been written — partial success is acceptable; the workflow will see the failure and open a `refresh-failure` issue.

    (The refresh-loop INVARIANT test — "generated_at advances once, stays stable on second run" — is Task 4's concern; Task 3 ships only the data-path wiring.)
  </behavior>

  <action>
    Rewrite `src/uk_subsidy_tracker/schemes/cfd/_refresh.py::refresh()` (and add a local `URL_MAP` constant mirroring `scripts/backfill_sidecars.py::URL_MAP`). Full replacement body for the module (keeping `upstream_changed()` unchanged):

    ```python
    """Dirty-check + refresh helpers for the CfD scheme.

    `upstream_changed()` compares SHA-256 of each raw file against its
    `.meta.json` sidecar (Plan 04-02). If any differ, return True — the
    daily refresh workflow will fire `refresh()` and then rebuild.

    `refresh()` (Plan 04-07) re-fetches LCCC + Elexon + ONS end-to-end and
    rewrites sidecars so SHA matches and retrieved_at advances. This closes
    gap #1 in 04-VERIFICATION.md — the refresh loop now terminates on
    unchanged upstream and advances manifest.generated_at on real changes.
    """
    from __future__ import annotations

    import hashlib
    import json
    from pathlib import Path

    from uk_subsidy_tracker import DATA_DIR

    _RAW_FILES = [
        "raw/lccc/actual-cfd-generation.csv",
        "raw/lccc/cfd-contract-portfolio-status.csv",
        "raw/elexon/agws.csv",
        "raw/elexon/system-prices.csv",
        "raw/ons/gas-sap.xlsx",
    ]

    # Upstream URLs — MUST match scripts/backfill_sidecars.py::URL_MAP exactly.
    # Any change here requires the same change in the backfill script so that
    # sidecars written by both paths are byte-identical on common keys.
    _URL_MAP = {
        "raw/lccc/actual-cfd-generation.csv":
            "https://dp.lowcarboncontracts.uk/datastore/dump/37d1bef4-55d7-4b8e-8a47-1d24b123a20e",
        "raw/lccc/cfd-contract-portfolio-status.csv":
            "https://dp.lowcarboncontracts.uk/datastore/dump/fdaf09d2-8cff-4799-a5b0-1c59444e492b",
        "raw/elexon/agws.csv":
            "https://data.elexon.co.uk/bmrs/api/v1/datasets/AGWS",
        "raw/elexon/system-prices.csv":
            "https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices",
        "raw/ons/gas-sap.xlsx":
            "https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/output/datasets/systemaveragepricesapofgas/2026/systemaveragepriceofgasdataset160426.xlsx",
    }


    def _sha256(path: Path) -> str:
        """Compute SHA-256 of a file in 64 KiB chunks."""
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 16), b""):
                h.update(chunk)
        return h.hexdigest()


    def upstream_changed() -> bool:
        """Return True iff any raw file's sha256 differs from its sidecar.

        A missing sidecar is treated as drift (True) because we cannot assert
        identity; a missing raw file is also drift (force re-fetch).
        """
        for rel in _RAW_FILES:
            raw = DATA_DIR / rel
            meta = raw.with_suffix(raw.suffix + ".meta.json")
            if not raw.exists() or not meta.exists():
                return True
            sidecar = json.loads(meta.read_text())
            if _sha256(raw) != sidecar.get("sha256"):
                return True
        return False


    def refresh() -> None:
        """Re-fetch all raw sources and rewrite sidecars atomically.

        Closes gap #1 in Plan 04-07: previous implementation re-fetched only
        LCCC; Elexon + ONS downloaders are now invoked in-line. Each
        successful download triggers a `write_sidecar()` call so `retrieved_at`
        advances and `sha256` matches the new bytes — this is what lets
        `upstream_changed()` report False on the next run (preventing the
        perpetual dirty-check loop identified in 04-VERIFICATION.md).

        Fail-loud (D-17): any downloader exception propagates; the daily
        refresh workflow sees the failure and opens a `refresh-failure` issue.
        """
        from uk_subsidy_tracker.data.elexon import download_elexon_data
        from uk_subsidy_tracker.data.lccc import (
            download_lccc_datasets,
            load_lccc_config,
        )
        from uk_subsidy_tracker.data.ons_gas import download_dataset as download_ons_gas
        from uk_subsidy_tracker.data.sidecar import write_sidecar

        # 1. LCCC (two files).
        config = load_lccc_config()
        download_lccc_datasets(config)

        # 2. Elexon (AGWS + system prices).
        download_elexon_data()

        # 3. ONS (SAP gas).
        download_ons_gas()

        # 4. Rewrite every sidecar so SHA matches fresh bytes + retrieved_at = now.
        for rel, upstream_url in _URL_MAP.items():
            raw_path = DATA_DIR / rel
            if not raw_path.exists():
                # Downloader returned without writing the file — fail loud.
                raise FileNotFoundError(
                    f"refresh() downloaded but raw file missing: {raw_path}. "
                    f"Upstream URL: {upstream_url}"
                )
            write_sidecar(raw_path=raw_path, upstream_url=upstream_url)
    ```

    Do NOT change `src/uk_subsidy_tracker/schemes/cfd/__init__.py` — its public `refresh()` already delegates to `_refresh.refresh()`.

    Do NOT change `src/uk_subsidy_tracker/refresh_all.py` — Option A architecture (scheme owns its raw files) means the orchestrator is already correct; the fix is entirely inside the scheme module.

    Run `uv run pytest tests/ -q` to confirm no regressions. (The invariant test shipped in Task 4 will exercise the new refresh behaviour under mocked downloaders.)

    Commit message: `fix(04-07): wire Elexon + ONS + sidecar rewrites into cfd refresh (gap #1)`.
  </action>

  <verify>
    <automated>grep -c "download_elexon_data\|download_ons_gas" src/uk_subsidy_tracker/schemes/cfd/_refresh.py && grep -c "write_sidecar" src/uk_subsidy_tracker/schemes/cfd/_refresh.py && grep -c "_URL_MAP" src/uk_subsidy_tracker/schemes/cfd/_refresh.py && uv run pytest tests/ -q</automated>
  </verify>

  <acceptance_criteria>
    - `grep -c "download_elexon_data" src/uk_subsidy_tracker/schemes/cfd/_refresh.py` returns at least 2 (import + call)
    - `grep -c "download_ons_gas\|ons_gas.download_dataset\|download_dataset as download_ons_gas" src/uk_subsidy_tracker/schemes/cfd/_refresh.py` returns at least 2 (import + call)
    - `grep -c "download_lccc_datasets" src/uk_subsidy_tracker/schemes/cfd/_refresh.py` returns at least 2 (LCCC path preserved)
    - `grep -c "from uk_subsidy_tracker.data.sidecar import write_sidecar" src/uk_subsidy_tracker/schemes/cfd/_refresh.py` returns exactly 1
    - `grep -c "write_sidecar(" src/uk_subsidy_tracker/schemes/cfd/_refresh.py` returns at least 1 (the loop call)
    - `grep -c "_URL_MAP" src/uk_subsidy_tracker/schemes/cfd/_refresh.py` returns at least 2 (definition + iteration)
    - Every URL string in `_URL_MAP` matches `scripts/backfill_sidecars.py::URL_MAP` VERBATIM (verify via `diff <(uv run python -c "from uk_subsidy_tracker.schemes.cfd._refresh import _URL_MAP; import json; print(json.dumps(dict(sorted(_URL_MAP.items())), indent=2))") <(uv run python -c "import sys; sys.path.insert(0, 'scripts'); import importlib.util; spec=importlib.util.spec_from_file_location('bf','scripts/backfill_sidecars.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); import json; print(json.dumps(dict(sorted({'raw/'+k:v for k,v in m.URL_MAP.items()}.items())), indent=2))")` returns no diff)
    - `refresh_all.py` is UNCHANGED: `git diff src/uk_subsidy_tracker/refresh_all.py` returns empty
    - Full suite stays green: `uv run pytest tests/ -q` exits 0 with at least 72 passed + 4 skipped (Task 2's 3 new tests still present; no regressions)
  </acceptance_criteria>

  <done>
    `scheme.refresh()` is a complete data-layer operation: three downloaders + five sidecar rewrites. `upstream_changed()` after a successful `refresh()` MUST return False on unchanged upstream (because sidecar SHA now matches live bytes) — this is the algebraic invariant Task 4 locks with a test.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 4: Write refresh-loop invariant test (simulates upstream change, asserts generated_at advances once)</name>
  <files>tests/test_refresh_loop.py</files>

  <read_first>
    - src/uk_subsidy_tracker/schemes/cfd/_refresh.py   (POST-TASK-3 state — refresh() now calls three downloaders + write_sidecar)
    - src/uk_subsidy_tracker/refresh_all.py            (orchestrator — calls scheme.upstream_changed → refresh → rebuild → publish)
    - src/uk_subsidy_tracker/publish/manifest.py       (generated_at computation — sources from max(sidecar.retrieved_at); lines mentioning `generated_at`)
    - tests/test_manifest.py                           (patterns for building manifest in-tests; tmp_path + monkeypatch idioms)
    - tests/test_determinism.py                        (patterns for seeding fixtures into tmp_path and running rebuild_derived)
  </read_first>

  <behavior>
    - Test 1: `test_refresh_loop_converges_on_unchanged_upstream` — After one successful `refresh()` against mocked downloaders that write DETERMINISTIC bytes, calling `upstream_changed()` returns False. (This is the perpetual-dirty-check-loop regression guard.)
    - Test 2: `test_refresh_loop_generated_at_advances_once_then_stable` — Simulate an upstream change by corrupting one sidecar's sha256 field + mocking the downloaders to write NEW bytes to raw files. Run `refresh_all.main(['--version', 'latest'])` once → capture manifest.generated_at (T0). Run it again WITHOUT corrupting sidecars → assert manifest.generated_at is unchanged (still T0). Strictly: after run 1, `upstream_changed()` returns False (sidecars now match bytes), so run 2 short-circuits and does NOT rebuild the manifest, so generated_at remains at T0.
    - Tests MUST NOT hit network — all three downloaders (`download_lccc_datasets`, `download_elexon_data`, `ons_gas.download_dataset`) patched via `monkeypatch` to write synthetic bytes to the DATA_DIR fixture paths.
    - Tests MUST NOT touch the real `data/raw/` tree — use `tmp_path` + monkeypatch `DATA_DIR` (or point _RAW_FILES to a tmp_path root).
  </behavior>

  <action>
    Create `tests/test_refresh_loop.py`. Reference structure (adapt as needed; the BEHAVIOUR is fixed, the exact helpers can flex):

    ```python
    """Refresh-loop invariant test — closes gap #1 in 04-VERIFICATION.md.

    The daily refresh workflow's correctness depends on a tight algebraic
    invariant: after `scheme.refresh()` writes fresh bytes AND rewrites
    sidecars, `upstream_changed()` MUST report False on the next invocation.
    Otherwise the dirty-check loops perpetually and `manifest.generated_at`
    (sourced from `max(sidecar.retrieved_at)`) never advances past the
    backfill date.

    These tests pin the invariant with mocked downloaders. They do NOT hit
    network — the download functions are all patched to write synthetic
    bytes into a tmp_path raw tree.
    """
    from __future__ import annotations

    import json
    from pathlib import Path
    from unittest.mock import patch

    import pytest

    from uk_subsidy_tracker.schemes.cfd import _refresh as cfd_refresh


    @pytest.fixture
    def tmp_raw_tree(tmp_path, monkeypatch):
        """Seed tmp_path with the five raw files + sidecars that match,
        pointing _refresh at tmp_path as DATA_DIR. Returns the tmp_path root.
        """
        raw_root = tmp_path
        # Create directory skeleton.
        for sub in ("raw/lccc", "raw/elexon", "raw/ons"):
            (raw_root / sub).mkdir(parents=True, exist_ok=True)
        # Seed each raw file with deterministic content + a matching sidecar.
        from uk_subsidy_tracker.data.sidecar import write_sidecar
        for rel, url in cfd_refresh._URL_MAP.items():
            raw_path = raw_root / rel
            raw_path.write_bytes(f"INITIAL-CONTENT-{rel}".encode())
            write_sidecar(raw_path=raw_path, upstream_url=url)
        # Redirect both the scheme module AND the sidecar helper at tmp_path.
        monkeypatch.setattr(cfd_refresh, "DATA_DIR", raw_root)
        return raw_root


    def _patched_refresh_downloaders(raw_root: Path, new_content: dict[str, bytes]):
        """Return a context manager stack that patches the three downloaders
        to write `new_content[rel]` bytes to each raw file in `raw_root`.
        """
        from contextlib import ExitStack
        stack = ExitStack()

        def fake_lccc(config):
            for rel in ("raw/lccc/actual-cfd-generation.csv",
                        "raw/lccc/cfd-contract-portfolio-status.csv"):
                (raw_root / rel).write_bytes(new_content[rel])

        def fake_elexon(*a, **kw):
            for rel in ("raw/elexon/agws.csv", "raw/elexon/system-prices.csv"):
                (raw_root / rel).write_bytes(new_content[rel])

        def fake_ons(*a, **kw):
            rel = "raw/ons/gas-sap.xlsx"
            (raw_root / rel).write_bytes(new_content[rel])
            return raw_root / rel

        stack.enter_context(patch(
            "uk_subsidy_tracker.data.lccc.download_lccc_datasets", side_effect=fake_lccc,
        ))
        stack.enter_context(patch(
            "uk_subsidy_tracker.data.lccc.load_lccc_config", return_value=None,
        ))
        stack.enter_context(patch(
            "uk_subsidy_tracker.data.elexon.download_elexon_data", side_effect=fake_elexon,
        ))
        stack.enter_context(patch(
            "uk_subsidy_tracker.data.ons_gas.download_dataset", side_effect=fake_ons,
        ))
        return stack


    def test_refresh_loop_converges_on_unchanged_upstream(tmp_raw_tree):
        """After refresh() writes fresh bytes + sidecars, upstream_changed() = False."""
        new_content = {rel: f"FRESH-CONTENT-{rel}".encode()
                       for rel in cfd_refresh._URL_MAP}

        with _patched_refresh_downloaders(tmp_raw_tree, new_content):
            cfd_refresh.refresh()

        # Invariant: after a successful refresh, the dirty-check reports clean.
        assert cfd_refresh.upstream_changed() is False, (
            "upstream_changed() must return False after refresh() rewrites sidecars"
        )


    def test_refresh_loop_generated_at_advances_once_then_stable(tmp_raw_tree):
        """Simulate one upstream change; assert generated_at advances once and stays.

        Protocol:
        1. Corrupt one sidecar's sha256 so upstream_changed() returns True.
        2. Patch downloaders to write NEW bytes; call refresh() → sidecars rewritten.
        3. Read max(sidecar.retrieved_at) as T1. T1 must be newer than the
           pre-corruption backfill timestamp.
        4. Without further corruption, assert upstream_changed() returns False
           — the next orchestrator pass would short-circuit and NOT rebuild
           the manifest. Therefore generated_at stays at T1.
        """
        from datetime import datetime

        # Capture pre-refresh sidecar timestamps.
        def read_retrieved_at(rel: str) -> str:
            meta = (tmp_raw_tree / rel).with_suffix(
                (tmp_raw_tree / rel).suffix + ".meta.json"
            )
            return json.loads(meta.read_text())["retrieved_at"]

        # Step 1: corrupt one sidecar (simulate upstream drift detected).
        first_rel = next(iter(cfd_refresh._URL_MAP))
        first_meta = (tmp_raw_tree / first_rel).with_suffix(
            (tmp_raw_tree / first_rel).suffix + ".meta.json"
        )
        corrupted = json.loads(first_meta.read_text())
        corrupted["sha256"] = "0" * 64  # garbage; will not match live bytes
        first_meta.write_text(json.dumps(corrupted, sort_keys=True, indent=2) + "\n")
        assert cfd_refresh.upstream_changed() is True, "setup: corruption must be detected"

        # Step 2: refresh() rewrites all sidecars with fresh retrieved_at.
        new_content = {rel: f"FRESH-CONTENT-v2-{rel}".encode()
                       for rel in cfd_refresh._URL_MAP}
        with _patched_refresh_downloaders(tmp_raw_tree, new_content):
            cfd_refresh.refresh()

        # Step 3: max(retrieved_at) is now; every sidecar has advanced.
        timestamps = [read_retrieved_at(rel) for rel in cfd_refresh._URL_MAP]
        parsed = [datetime.fromisoformat(ts) for ts in timestamps]
        t1 = max(parsed)
        # All five timestamps must be very recent (within last 5 seconds of test run).
        assert (datetime.now(t1.tzinfo) - t1).total_seconds() < 5.0, (
            f"retrieved_at must reflect current time after refresh; got {t1}"
        )

        # Step 4: invariant holds — dirty-check reports clean; no rebuild next pass.
        assert cfd_refresh.upstream_changed() is False, (
            "Second pass MUST short-circuit — sidecars now match live bytes"
        )
    ```

    Run `uv run pytest tests/test_refresh_loop.py -v` — expect 2 passing tests.

    Run the full suite `uv run pytest tests/ -q` — expect at least 74 passed + 4 skipped (69 pre-existing + 3 from Task 2 + 2 from Task 4).

    Commit message: `test(04-07): refresh-loop invariant test (gap #1)`.
  </action>

  <verify>
    <automated>test -f tests/test_refresh_loop.py && uv run pytest tests/test_refresh_loop.py -v && grep -c "upstream_changed() is False" tests/test_refresh_loop.py && grep -c "generated_at\|retrieved_at" tests/test_refresh_loop.py && uv run pytest tests/ -q</automated>
  </verify>

  <acceptance_criteria>
    - `tests/test_refresh_loop.py` exists, at least 60 non-blank lines
    - `uv run pytest tests/test_refresh_loop.py -v` exits 0 with exactly 2 passing tests
    - Test names grep-match: `grep -E "def test_refresh_loop_converges_on_unchanged_upstream|def test_refresh_loop_generated_at_advances_once_then_stable" tests/test_refresh_loop.py` returns 2 matches
    - `grep -c "upstream_changed() is False" tests/test_refresh_loop.py` returns at least 2 (invariant asserted in both tests)
    - Test does NOT hit network: `grep -c "mock\|patch\|monkeypatch" tests/test_refresh_loop.py` returns at least 3 (all downloaders stubbed)
    - Test does NOT touch real data/raw: `grep -c "tmp_path\|tmp_raw_tree" tests/test_refresh_loop.py` returns at least 3 (fixture-based isolation)
    - Full suite stays green: `uv run pytest tests/ -q` exits 0 with at least 74 passed + 4 skipped
    - Test runtime under 5 seconds: `uv run pytest tests/test_refresh_loop.py --durations=0` reports total duration < 5.0s
  </acceptance_criteria>

  <done>
    The refresh-loop invariant ("after upstream change, generated_at advances once and stays stable on unchanged second run") is now locked by a test. Any future regression that breaks the sidecar-rewrite contract (e.g. a scheme module forgets to call `write_sidecar`) will fail `test_refresh_loop_converges_on_unchanged_upstream` immediately.
  </done>
</task>

<task type="auto">
  <name>Task 5: Refactor scripts/backfill_sidecars.py to use write_sidecar() + update CHANGES.md</name>
  <files>scripts/backfill_sidecars.py, CHANGES.md</files>

  <read_first>
    - scripts/backfill_sidecars.py                   (current implementation — main() loop writes sidecars inline)
    - src/uk_subsidy_tracker/data/sidecar.py         (write_sidecar signature from Task 1)
    - CHANGES.md                                      (current [Unreleased] section — append NEW bullets, do not rewrite)
  </read_first>

  <action>
    **Step A — refactor backfill script.** Update `scripts/backfill_sidecars.py::main()` to use `write_sidecar()` for the SHA-256 + JSON-write mechanics, preserving the script's unique responsibility (the `backfilled_at` marker and the `git log --follow` based `retrieved_at` fallback).

    The cleanest split of responsibility:
    - `write_sidecar()` (shared) handles the common path: compute SHA, write JSON atomically, serialise with `sort_keys=True, indent=2, trailing newline`.
    - `backfill_sidecars.py` uses its own `retrieved_at` (from `git log`) and appends `backfilled_at`. Since `write_sidecar()` doesn't accept a custom `retrieved_at` nor emit `backfilled_at`, the backfill script performs a small POST-STEP: after `write_sidecar()` writes the common-key sidecar, the backfill script reads it back, overrides `retrieved_at` with the git-log value, injects `backfilled_at`, and re-writes atomically using the same `sort_keys=True, indent=2, \n` serialiser.

    Replacement for `scripts/backfill_sidecars.py::main()`:

    ```python
    def main() -> None:
        if not RAW_ROOT.is_dir():
            raise SystemExit(
                f"Missing {RAW_ROOT}. Run `git mv` for the raw files first, "
                f"then re-run this script (see Phase 4 Plan 02 Task 2)."
            )

        # Import the shared writer (Plan 04-07 Task 1). The backfill script uses
        # it for SHA + atomic JSON write; it then overlays the two backfill-specific
        # fields (`retrieved_at` from git log + `backfilled_at` marker).
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / "src"))
        from uk_subsidy_tracker.data.sidecar import write_sidecar

        for rel_path, upstream_url in URL_MAP.items():
            raw_path = RAW_ROOT / rel_path
            if not raw_path.exists():
                raise SystemExit(f"Expected raw file {raw_path} not found.")

            # 1. Write the common-keys sidecar via the shared helper (atomic).
            meta_path = write_sidecar(
                raw_path=raw_path,
                upstream_url=upstream_url,
                http_status=None,                # backfill marker
                publisher_last_modified=None,    # unknown for backfills
            )

            # 2. Overlay backfill-specific fields (retrieved_at from git log +
            #    backfilled_at marker). Re-serialise with the same invariants.
            meta = json.loads(meta_path.read_text())
            meta["retrieved_at"] = git_last_change(raw_path)
            meta["backfilled_at"] = BACKFILL_DATE
            tmp_path = meta_path.with_suffix(meta_path.suffix + ".tmp")
            tmp_path.write_text(
                json.dumps(meta, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            import os
            os.replace(tmp_path, meta_path)
            print(f"wrote {meta_path}")
    ```

    Remove the now-unused `sha256_of` function (live calls route through `write_sidecar` internally). Keep `git_last_change` — that's unique backfill logic.

    Re-run the backfill on the actual raw tree to confirm byte-identity on common keys: `uv run python scripts/backfill_sidecars.py` then `git diff data/raw/**/*.meta.json` — the expected diff is: `retrieved_at` timestamps may update to new ISO format (both are valid ISO-8601 with offset), but `sha256` + `upstream_url` + `backfilled_at` MUST be unchanged, and JSON structure + key order + trailing newline MUST be identical.

    **Step B — update CHANGES.md.** Append three bullets under `## [Unreleased]` → `### Added` / `### Fixed` / `### Changed` as appropriate. Do NOT rewrite existing bullets. Suggested new entries:

    ```markdown
    ### Added
    - `src/uk_subsidy_tracker/data/sidecar.py` (Plan 04-07) — shared
      `write_sidecar()` helper for `.meta.json` atomicity. Used by both the
      daily refresh path (`schemes/cfd/_refresh.py::refresh()`) and the
      one-shot `scripts/backfill_sidecars.py`. Serialisation is byte-identical
      across both call sites (sort_keys=True, indent=2, trailing newline);
      writes go via `<path>.meta.json.tmp` + `os.replace` so sidecars are
      never partial on crash. Closes gap #1 from 04-VERIFICATION.md.
    - `tests/test_refresh_loop.py` (Plan 04-07) — invariant test locking the
      refresh-loop algebraic property: after `scheme.refresh()` rewrites
      sidecars, `upstream_changed()` returns False on the next call, and
      `manifest.generated_at` advances once then stays stable on unchanged
      second runs. Uses `monkeypatch` + `tmp_path` + mocked downloaders; does
      not hit network.
    - `tests/test_ons_gas_download.py` (Plan 04-07) — regression test for the
      `ons_gas.download_dataset()` error-path (3 tests: raises on network
      failure, uses timeout=60, returns path on success).

    ### Fixed
    - `src/uk_subsidy_tracker/data/ons_gas.py::download_dataset` (Plan 04-07
      gap #2) — `output_path` is now bound BEFORE the `try` block (previously
      raised `UnboundLocalError` on any network failure); `requests.get` now
      carries `timeout=60` matching the Elexon convention; the `except`
      handler now re-`raise`s (fail-loud per CONTEXT D-17) instead of
      silently returning an un-downloaded path.
    - `src/uk_subsidy_tracker/schemes/cfd/_refresh.py::refresh` (Plan 04-07
      gap #1) — now invokes all three downloaders (LCCC + Elexon + ONS;
      previously only LCCC was re-fetched) and calls `write_sidecar()` for
      each of the five raw files after successful download. This closes the
      perpetual dirty-check loop identified in 04-VERIFICATION.md: on
      unchanged upstream, the orchestrator short-circuits correctly; on
      upstream change, `manifest.generated_at` advances once and stays
      stable on the next unchanged run.

    ### Changed
    - `scripts/backfill_sidecars.py` (Plan 04-07) — refactored to delegate
      SHA computation + atomic JSON write to `write_sidecar()`, then overlay
      the two backfill-specific fields (`retrieved_at` from `git log
      --follow`, `backfilled_at` marker). Output bytes unchanged on all
      common keys; the script's public behaviour and CLI contract are
      identical.
    ```

    Commit message: `docs(04-07): CHANGES entries + backfill script refactor to shared sidecar helper`.
  </action>

  <verify>
    <automated>grep -c "from uk_subsidy_tracker.data.sidecar import write_sidecar" scripts/backfill_sidecars.py && grep -c "04-07" CHANGES.md && uv run python scripts/backfill_sidecars.py && uv run pytest tests/ -q && git diff data/raw/ | grep -E "^-.*sha256|^\+.*sha256" | head -5</automated>
  </verify>

  <acceptance_criteria>
    - `grep -c "from uk_subsidy_tracker.data.sidecar import write_sidecar" scripts/backfill_sidecars.py` returns exactly 1
    - `grep -c "write_sidecar(" scripts/backfill_sidecars.py` returns at least 1
    - `scripts/backfill_sidecars.py` still exposes `git_last_change`, `URL_MAP`, `BACKFILL_DATE` (backfill-specific logic preserved): `grep -E "def git_last_change|URL_MAP|BACKFILL_DATE" scripts/backfill_sidecars.py` returns at least 3 matches
    - Running `uv run python scripts/backfill_sidecars.py` exits 0 and prints 5 `wrote ...` lines (one per raw file)
    - After re-running the backfill, `git diff data/raw/**/*.meta.json` shows NO changes to `sha256` values (byte-identity preserved): `git diff data/raw/ 2>/dev/null | grep -cE '^[+-].*\"sha256\"'` returns 0
    - `backfilled_at` key is still present in every sidecar post-refactor: `for f in data/raw/**/*.meta.json; do grep -q backfilled_at "$f" || echo FAIL; done` prints nothing
    - `CHANGES.md` gains at least 3 new bullets mentioning `04-07`: `grep -c "04-07" CHANGES.md` returns at least 3
    - `CHANGES.md` has entries under `### Added`, `### Fixed`, and `### Changed` referencing this plan: `grep -B1 "04-07" CHANGES.md | grep -c "^### " ` returns at least 3 (one Added, one Fixed, one Changed entry block)
    - Full suite stays green: `uv run pytest tests/ -q` exits 0 with at least 74 passed + 4 skipped
  </acceptance_criteria>

  <done>
    `write_sidecar()` is the single source of truth for `.meta.json` mechanics across both call sites (daily refresh + one-shot backfill). Backfill script still owns its two unique fields. CHANGES.md reflects the plan's delivery. No sidecar content changed on-disk (byte-identity preserved) — future consumers who read the sidecars see no difference.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| publisher endpoint → local raw file | Untrusted bytes land on disk; SHA computed + sidecar written |
| local raw file → derived Parquet | Already inside trust zone; pandera validates shape |
| local raw file → manifest.json | Already inside trust zone; sha256 re-computed on build |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-04-07-01 | Tampering | `.meta.json` partial-write on crash | mitigate | `write_sidecar()` writes to `.tmp` + `os.replace()`; atomic on POSIX + Windows. Verified by code inspection (Task 1). |
| T-04-07-02 | Denial of Service | ONS endpoint hangs indefinitely | mitigate | `timeout=60` on `requests.get` per Elexon convention (Task 2). Refresh job fails loud after 60s instead of blocking the 5-min daily budget. |
| T-04-07-03 | Information Disclosure | ons_gas `UnboundLocalError` leaks Python internals in logs | mitigate | Replaced with explicit `raise` inside except handler; log message is the scoped `f"An error occurred while downloading ons_gas: {e}"` — no local-variable state leaks. (Task 2.) |
| T-04-07-04 | Tampering | Sidecar desynchronised from raw file after refresh (gap #1 state) | mitigate | Refresh flow now writes sidecar via `write_sidecar()` IMMEDIATELY after download succeeds; test_refresh_loop locks the invariant that `upstream_changed()` reports False post-refresh. (Tasks 3 + 4.) |
| T-04-07-05 | Repudiation | Manifest `generated_at` frozen at backfill date (current state) | mitigate | After Task 3, each refresh advances `retrieved_at` on five sidecars → `max(retrieved_at)` → `manifest.generated_at` advances. Lock with test_refresh_loop (Task 4). Public auditor can diff release-to-release and see the advance. |
| T-04-07-06 | Spoofing | Backfill script writes different sidecar bytes than refresh path | mitigate | Both paths now call `write_sidecar()` for the common keys; byte-identity verified by Task 5 acceptance criterion (`git diff` on re-backfill shows no sha256 churn). |
| T-04-07-07 | Elevation of Privilege | Network failure silently masquerades as successful download (current ons_gas state) | mitigate | `raise` in except handler (Task 2) propagates to `refresh_all.main()` → non-zero exit → workflow fails loud → `refresh-failure` issue opens. |
</threat_model>

<verification>
## Plan-Level Verification

After all 5 tasks complete, verify the plan as a whole:

1. **Full suite green**: `uv run pytest tests/ -q` exits 0 with ≥74 passed + 4 skipped (was 69 + 4 pre-plan; +3 from Task 2, +2 from Task 4).

2. **Refresh-loop invariant locked**:
   - `uv run pytest tests/test_refresh_loop.py -v` exits 0 with 2 tests passing.
   - Inspecting `tests/test_refresh_loop.py`: both tests call `cfd_refresh.upstream_changed() is False` after a patched-downloader `refresh()`.

3. **No network in tests**:
   - `grep -rE "requests\.get|requests\.post" tests/test_refresh_loop.py tests/test_ons_gas_download.py` returns 0 (all mocked via `patch()`/`monkeypatch`).

4. **Gap #1 missing items all delivered** (verbatim lines from 04-VERIFICATION.md):
   - ✅ "End-to-end refresh helper that fetches LCCC + Elexon + ONS and rewrites .meta.json sidecars" → Task 3 (`_refresh.py::refresh()`) + Task 1 (`sidecar.py::write_sidecar`)
   - ✅ "Call sites in refresh_all.refresh_scheme() (or scheme_module.refresh()) that invoke Elexon + ONS downloaders" → Task 3 (chose scheme_module.refresh() per Option A; grep confirms `download_elexon_data` + `download_ons_gas` present)
   - ✅ "Test covering the refresh loop invariant" → Task 4 (`tests/test_refresh_loop.py::test_refresh_loop_generated_at_advances_once_then_stable`)

5. **Gap #2 missing items all delivered** (verbatim lines from 04-VERIFICATION.md):
   - ✅ "Assign output_path BEFORE the try block" → Task 2 (`ons_gas.py` now binds `output_path` before `try:`)
   - ✅ "Either re-raise or return None/False on failure — never silently return a non-downloaded path" → Task 2 (bare `raise` at end of except block)
   - ✅ "Add timeout=60 to requests.get() to match the Elexon convention" → Task 2 (`timeout=60` kwarg on the single `requests.get` call)

6. **Scope discipline**:
   - No edits to `src/uk_subsidy_tracker/publish/manifest.py` (W-03 mkdocs site_url line-scan is "Info accepted" — excluded per verifier).
   - No edits to `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py` (W-04 empty-data fallback is "Info" — excluded per verifier).
   - No edits to `.github/workflows/refresh.yml` or `deploy.yml` for SHA-pinning of actions (supply-chain "Info accepted" — excluded per verifier).
   - No edits to `src/uk_subsidy_tracker/data/lccc.py` (pre-existing silent-swallow pattern is out of scope per verifier's scoped guidance).

7. **Commit hygiene**: 5 atomic commits (one per task) following the project's Phase 1 D-16 atomic-commit discipline; each commit message starts with `feat(04-07)` / `fix(04-07)` / `test(04-07)` / `docs(04-07)` as appropriate.

## Behavioural Spot-Checks (for gsd-verifier on re-run)

| Behavior | Command | Expected |
|----------|---------|----------|
| Sidecar helper importable | `uv run python -c "from uk_subsidy_tracker.data.sidecar import write_sidecar; print('ok')"` | Exit 0, output `ok` |
| ons_gas regression test green | `uv run pytest tests/test_ons_gas_download.py -v` | 3 passing |
| Refresh-loop invariant test green | `uv run pytest tests/test_refresh_loop.py -v` | 2 passing |
| Backfill script still works | `uv run python scripts/backfill_sidecars.py` | 5 `wrote ...` lines; exit 0 |
| Full suite green | `uv run pytest tests/ -q` | ≥74 passed, 4 skipped |
| Refresh path grep-present | `grep -c "download_elexon_data\|download_ons_gas" src/uk_subsidy_tracker/schemes/cfd/_refresh.py` | ≥2 |
| Sidecar-rewrite grep-present | `grep -c "write_sidecar" src/uk_subsidy_tracker/schemes/cfd/_refresh.py` | ≥1 |
| No UnboundLocalError risk | `grep -A2 "except requests" src/uk_subsidy_tracker/data/ons_gas.py \| grep -c "return output_path"` | 0 |
| Timeout convention | `grep -c "timeout=60" src/uk_subsidy_tracker/data/ons_gas.py` | ≥1 |
</verification>

<success_criteria>
Plan 04-07 is complete when ALL of these hold simultaneously:

1. `src/uk_subsidy_tracker/data/sidecar.py` exists; `write_sidecar()` is importable; atomic (.tmp + os.replace); UTC retrieved_at; byte-identical serialisation to `scripts/backfill_sidecars.py` on common keys.

2. `src/uk_subsidy_tracker/data/ons_gas.py::download_dataset()` cannot raise `UnboundLocalError`; `output_path` is bound BEFORE `try:`; `requests.get` carries `timeout=60`; network failure propagates via bare `raise` (fail-loud per D-17); `tests/test_ons_gas_download.py` (3 tests) passes.

3. `src/uk_subsidy_tracker/schemes/cfd/_refresh.py::refresh()` calls LCCC + Elexon + ONS downloaders AND calls `write_sidecar()` for each of the 5 `_RAW_FILES` after successful download; `_URL_MAP` in this file byte-matches `scripts/backfill_sidecars.py::URL_MAP`.

4. `tests/test_refresh_loop.py` (2 tests) passes; the invariant "after refresh, upstream_changed() returns False" and "generated_at advances once then stays stable" is locked.

5. `scripts/backfill_sidecars.py` delegates SHA + atomic JSON write to `write_sidecar()`; preserves `backfilled_at` marker + `git log`-based `retrieved_at`; re-running produces no sha256 churn on existing sidecars.

6. `CHANGES.md [Unreleased]` gains entries under `### Added` / `### Fixed` / `### Changed` citing plan 04-07, the two gaps it closes, and the three REQ-IDs re-greenified (GOV-03 + PUB-05 + indirectly GOV-06 via sidecar atomicity).

7. Full test suite: `uv run pytest tests/ -q` exits 0 with ≥74 passed + 4 skipped.

8. No scope creep: `git diff src/uk_subsidy_tracker/publish/manifest.py src/uk_subsidy_tracker/schemes/cfd/forward_projection.py src/uk_subsidy_tracker/data/lccc.py .github/workflows/refresh.yml .github/workflows/deploy.yml` returns empty (verifier scoped these OUT).

9. Requirements re-coverage: GOV-03 ("Daily refresh CI workflow ... functional") and PUB-05 ("Three-layer pipeline operational end-to-end") are now FULLY satisfied rather than PARTIAL — a re-run of 04-VERIFICATION.md would downgrade both gaps to `verified` (not `partial`).
</success_criteria>

<output>
After completion, create `.planning/phases/04-publishing-layer/04-07-SUMMARY.md` using the standard summary template. The summary MUST:

- Reference plan frontmatter: `phase: 04-publishing-layer`, `plan: 07`, `subsystem: refresh-loop-closure`, `tags: [gap-closure, refresh, sidecar, ons-gas, gov-03, pub-05]`, `gap_closure: true`, `gap_closure_source: .planning/phases/04-publishing-layer/04-VERIFICATION.md`.
- Record `requires:` dependency on plan 04-05 (which shipped refresh_all.py + refresh.yml that this plan completes) and 04-02 (raw-layer migration + sidecar shape).
- Record `provides:` = the 5 new/modified artefacts (sidecar.py, ons_gas.py fixes, _refresh.py wiring, test_refresh_loop.py, test_ons_gas_download.py) + CHANGES.md entries.
- Record `affects:` = phase 05+ (future RO/FiT/etc. schemes copy the Option A refresh pattern verbatim — each scheme's `_refresh.py::refresh()` fetches its own raw files and calls `write_sidecar()` for each).
- Note which verifier-scoped OUT items were respected (W-03 mkdocs line-scan, W-04 empty-data fallback, supply-chain SHA pinning, lccc.py silent-swallow alignment).
- Confirm the two VERIFICATION.md gaps are both closed with verbatim "missing:" lines ticked off.

File path: `.planning/phases/04-publishing-layer/04-07-refresh-loop-closure-SUMMARY.md`.
</output>
