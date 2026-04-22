---
phase: 04-publishing-layer
plan: 02
type: execute
wave: 2
depends_on:
  - 01
files_modified:
  - data/lccc-actual-cfd-generation.csv             # removed (git mv)
  - data/lccc-cfd-contract-portfolio-status.csv     # removed
  - data/elexon_agws.csv                            # removed
  - data/elexon_system_prices.csv                   # removed
  - data/ons_gas_sap.xlsx                           # removed
  - data/raw/lccc/actual-cfd-generation.csv         # added (via git mv)
  - data/raw/lccc/actual-cfd-generation.csv.meta.json
  - data/raw/lccc/cfd-contract-portfolio-status.csv
  - data/raw/lccc/cfd-contract-portfolio-status.csv.meta.json
  - data/raw/elexon/agws.csv
  - data/raw/elexon/agws.csv.meta.json
  - data/raw/elexon/system-prices.csv
  - data/raw/elexon/system-prices.csv.meta.json
  - data/raw/ons/gas-sap.xlsx
  - data/raw/ons/gas-sap.xlsx.meta.json
  - src/uk_subsidy_tracker/data/lccc.py
  - src/uk_subsidy_tracker/data/elexon.py
  - src/uk_subsidy_tracker/data/ons_gas.py
  - src/uk_subsidy_tracker/data/lccc_datasets.yaml
  - scripts/backfill_sidecars.py                    # new (one-shot backfill helper)
  - CHANGES.md
autonomous: true
requirements:
  - PUB-05  # The three-layer pipeline starts at data/raw/; this is the source-layer migration that PUB-05 exit criterion requires.
  - GOV-02  # Provenance per dataset begins here — the .meta.json sidecar ships the source URL + retrieval timestamp + SHA-256 that manifest.json will later surface.
tags: [migration, raw-layer, sidecar, atomic-commit]
user_setup: []

must_haves:
  truths:
    - "All five raw data files live under data/raw/<publisher>/<file> with hyphenated names"
    - "Every raw file has a sibling .meta.json sidecar carrying SHA-256, upstream URL, retrieved_at, backfilled_at marker"
    - "uv run pytest passes on the rename commit tip (CI stays green)"
    - "Existing chart generation (`uv run python -m uk_subsidy_tracker.plotting`) still succeeds unchanged"
    - "git log --follow on a moved file resolves to pre-rename history (rename similarity ≥50%)"
  artifacts:
    - path: "data/raw/lccc/actual-cfd-generation.csv"
      provides: "LCCC generation CSV at its new canonical location (via git mv)"
    - path: "data/raw/lccc/cfd-contract-portfolio-status.csv"
      provides: "LCCC portfolio CSV at new location"
    - path: "data/raw/elexon/agws.csv"
      provides: "Elexon wind/solar generation at new location"
    - path: "data/raw/elexon/system-prices.csv"
      provides: "Elexon system prices at new location"
    - path: "data/raw/ons/gas-sap.xlsx"
      provides: "ONS SAP gas prices at new location"
    - path: "data/raw/lccc/actual-cfd-generation.csv.meta.json"
      provides: "Sidecar for LCCC generation — retrieved_at, upstream_url, sha256, backfilled_at"
      contains: "sha256"
    - path: "data/raw/lccc/cfd-contract-portfolio-status.csv.meta.json"
      provides: "Sidecar for LCCC portfolio"
      contains: "sha256"
    - path: "data/raw/elexon/agws.csv.meta.json"
      provides: "Sidecar for Elexon AGWS"
      contains: "sha256"
    - path: "data/raw/elexon/system-prices.csv.meta.json"
      provides: "Sidecar for Elexon system prices"
      contains: "sha256"
    - path: "data/raw/ons/gas-sap.xlsx.meta.json"
      provides: "Sidecar for ONS gas SAP"
      contains: "sha256"
    - path: "src/uk_subsidy_tracker/data/lccc_datasets.yaml"
      provides: "LCCC config with hyphenated paths under raw/lccc/"
      contains: "raw/lccc/"
    - path: "src/uk_subsidy_tracker/data/elexon.py"
      provides: "AGWS_FILE + SYSTEM_PRICE_FILE point to data/raw/elexon/ hyphenated paths"
      contains: "raw"
    - path: "src/uk_subsidy_tracker/data/ons_gas.py"
      provides: "GAS_SAP_DATA_FILENAME points to raw/ons/gas-sap.xlsx"
      contains: "raw/ons/gas-sap.xlsx"
    - path: "scripts/backfill_sidecars.py"
      provides: "One-shot script that (re-)computes sha256 + git-log retrieved_at and writes the five sidecars"
      min_lines: 40
  key_links:
    - from: "src/uk_subsidy_tracker/data/lccc.py"
      to: "data/raw/lccc/actual-cfd-generation.csv"
      via: "pd.read_csv(DATA_DIR / filename) where YAML filename is 'raw/lccc/actual-cfd-generation.csv'"
      pattern: "raw/lccc"
    - from: "src/uk_subsidy_tracker/data/elexon.py"
      to: "data/raw/elexon/agws.csv"
      via: "AGWS_FILE = DATA_DIR / 'raw' / 'elexon' / 'agws.csv'"
      pattern: "raw.*elexon"
    - from: "src/uk_subsidy_tracker/data/ons_gas.py"
      to: "data/raw/ons/gas-sap.xlsx"
      via: "GAS_SAP_DATA_FILENAME = 'raw/ons/gas-sap.xlsx'"
      pattern: "raw/ons/gas-sap.xlsx"
---

<objective>
Migrate the five raw data files from the flat `data/*.csv` / `data/*.xlsx`
layout into the canonical `data/raw/<publisher>/<file>` nested layout per
ARCHITECTURE §4.1, backfill a `.meta.json` sidecar next to each file, and
update every Python loader + YAML config path in the SAME commit so CI stays
green on the rename tip.

Purpose: Phase 5 (RO) adds `data/raw/ofgem/*` files and would force the
re-layout anyway. Doing it now — while we already touch every raw-data path
to add sidecars — keeps the Phase-4 publishing work (manifest.json reads
sidecar SHA-256) fed by well-structured provenance from day one.

Output: five moved files + five sidecars + three loader path updates + one
YAML config update + one one-shot backfill script (retained in `scripts/` for
future re-use on a full re-scrape) + one CHANGES.md entry. All delivered in
a single atomic commit (D-06).
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
@.planning/phases/04-01-SUMMARY.md
@ARCHITECTURE.md
@src/uk_subsidy_tracker/__init__.py
@src/uk_subsidy_tracker/data/lccc.py
@src/uk_subsidy_tracker/data/elexon.py
@src/uk_subsidy_tracker/data/ons_gas.py
@src/uk_subsidy_tracker/data/lccc_datasets.yaml

<interfaces>
<!-- Verbatim D-04 rename table (copied from CONTEXT.md) -->

| Current path | New path |
|---|---|
| `data/lccc-actual-cfd-generation.csv` | `data/raw/lccc/actual-cfd-generation.csv` |
| `data/lccc-cfd-contract-portfolio-status.csv` | `data/raw/lccc/cfd-contract-portfolio-status.csv` |
| `data/elexon_agws.csv` | `data/raw/elexon/agws.csv` |
| `data/elexon_system_prices.csv` | `data/raw/elexon/system-prices.csv` |
| `data/ons_gas_sap.xlsx` | `data/raw/ons/gas-sap.xlsx` |

<!-- D-05 sidecar shape (verbatim) -->

```json
{
  "retrieved_at": "2024-11-18T09:12:44+00:00",
  "upstream_url": "https://dp.lowcarboncontracts.uk/datastore/dump/37d1bef4-55d7-4b8e-8a47-1d24b123a20e",
  "sha256": "abc123...",
  "http_status": null,
  "publisher_last_modified": null,
  "backfilled_at": "2026-04-22"
}
```

<!-- Loader import convention (from CONVENTIONS.md + existing code) -->

```python
# src/uk_subsidy_tracker/__init__.py:3-4  (existing — DATA_DIR is stable anchor)
DATA_DIR = PROJECT_ROOT / "data"

# Loaders resolve file paths as DATA_DIR / <relative-from-data>
```

<!-- Current loader paths — updates required (verbatim excerpts) -->

```python
# src/uk_subsidy_tracker/data/elexon.py:30-31  (replace)
AGWS_FILE = DATA_DIR / "elexon_agws.csv"
SYSTEM_PRICE_FILE = DATA_DIR / "elexon_system_prices.csv"

# becomes:
AGWS_FILE = DATA_DIR / "raw" / "elexon" / "agws.csv"
SYSTEM_PRICE_FILE = DATA_DIR / "raw" / "elexon" / "system-prices.csv"
```

```python
# src/uk_subsidy_tracker/data/ons_gas.py:12  (replace)
GAS_SAP_DATA_FILENAME = "ons_gas_sap.xlsx"

# becomes:
GAS_SAP_DATA_FILENAME = "raw/ons/gas-sap.xlsx"
```

```yaml
# src/uk_subsidy_tracker/data/lccc_datasets.yaml — update filename: fields
# (leave 'description' + other keys untouched)
filename: "lccc-actual-cfd-generation.csv"
# becomes:
filename: "raw/lccc/actual-cfd-generation.csv"

filename: "lccc-cfd-contract-portfolio-status.csv"
# becomes:
filename: "raw/lccc/cfd-contract-portfolio-status.csv"
```

<!-- Sidecar upstream URLs (from existing loaders + CONTEXT) -->

| Path | Upstream URL (from loaders) |
|---|---|
| lccc/actual-cfd-generation.csv | `https://dp.lowcarboncontracts.uk/datastore/dump/37d1bef4-55d7-4b8e-8a47-1d24b123a20e` |
| lccc/cfd-contract-portfolio-status.csv | `https://dp.lowcarboncontracts.uk/datastore/dump/fdaf09d2-8cff-4799-a5b0-1c59444e492b` |
| elexon/agws.csv | `https://data.elexon.co.uk/bmrs/api/v1/datasets/AGWS` |
| elexon/system-prices.csv | `https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices` |
| ons/gas-sap.xlsx | `https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/output/datasets/systemaveragepricesapofgas/2026/systemaveragepriceofgasdataset160426.xlsx` |

(Executor: grep `^(AGWS_URL\|SYSTEM_PRICE_URL\|GAS_SAP_URL\|url:)` in loaders to
verify URLs before writing sidecars — use the live values, not the table.)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Write scripts/backfill_sidecars.py (one-shot backfill helper)</name>
  <files>scripts/backfill_sidecars.py</files>
  <read_first>
    - .planning/phases/04-publishing-layer/04-RESEARCH.md §Pattern 6 lines 832-891 (backfill script full template)
    - src/uk_subsidy_tracker/data/lccc.py (live URLs in lccc_datasets.yaml + download code)
    - src/uk_subsidy_tracker/data/elexon.py:25-31 (AGWS_URL, SYSTEM_PRICE_URL)
    - src/uk_subsidy_tracker/data/ons_gas.py:29 (GAS_SAP_URL)
    - src/uk_subsidy_tracker/__init__.py (DATA_DIR, PROJECT_ROOT)
  </read_first>
  <action>
    Create `scripts/backfill_sidecars.py` (repo root `scripts/` directory may
    not exist — create it). Purpose: one-shot script that iterates the five
    `data/raw/<publisher>/<file>` paths, computes sha256, reads git log for
    best-effort `retrieved_at`, and writes sibling `.meta.json` files. Kept
    after this plan as reusable tooling (e.g. for a future full re-scrape).

    Full file content (mirror RESEARCH §Pattern 6 exactly, adapt URLs to match
    what's already in the live loader files):

    ```python
    """Backfill `.meta.json` sidecars for data/raw/<publisher>/<file> (D-05).

    One-shot script run as part of the Phase 4 raw-layer migration (D-04).
    For each of the five tracked raw files, computes SHA-256, reads
    `git log --format=%cI` for best-effort `retrieved_at` (commit date of
    the file's last change), and writes a sibling `.meta.json` with
    `{retrieved_at, upstream_url, sha256, http_status, publisher_last_modified, backfilled_at}`.

    Run:
        uv run python scripts/backfill_sidecars.py

    Safe to re-run: overwrites existing sidecars with fresh sha256 + git-log
    values. Never modifies the raw data files themselves.
    """

    import hashlib
    import json
    import subprocess
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    RAW_ROOT = PROJECT_ROOT / "data" / "raw"
    BACKFILL_DATE = "2026-04-22"

    # Upstream URLs — cross-check against live loaders:
    #   src/uk_subsidy_tracker/data/lccc.py  (LCCC dataset UUIDs in lccc_datasets.yaml)
    #   src/uk_subsidy_tracker/data/elexon.py::AGWS_URL, SYSTEM_PRICE_URL
    #   src/uk_subsidy_tracker/data/ons_gas.py::GAS_SAP_URL
    URL_MAP = {
        "lccc/actual-cfd-generation.csv":
            "https://dp.lowcarboncontracts.uk/datastore/dump/37d1bef4-55d7-4b8e-8a47-1d24b123a20e",
        "lccc/cfd-contract-portfolio-status.csv":
            "https://dp.lowcarboncontracts.uk/datastore/dump/fdaf09d2-8cff-4799-a5b0-1c59444e492b",
        "elexon/agws.csv":
            "https://data.elexon.co.uk/bmrs/api/v1/datasets/AGWS",
        "elexon/system-prices.csv":
            "https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices",
        "ons/gas-sap.xlsx":
            "https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/output/datasets/systemaveragepricesapofgas/2026/systemaveragepriceofgasdataset160426.xlsx",
    }


    def git_last_change(path: Path) -> str:
        """Best-effort retrieved_at from git log of this path (or its pre-rename origin)."""
        result = subprocess.run(
            ["git", "log", "-1", "--follow", "--format=%cI", "--", str(path)],
            cwd=PROJECT_ROOT, check=False, capture_output=True, text=True,
        )
        stamp = result.stdout.strip()
        return stamp or f"{BACKFILL_DATE}T00:00:00+00:00"


    def sha256_of(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 16), b""):
                h.update(chunk)
        return h.hexdigest()


    def main() -> None:
        if not RAW_ROOT.is_dir():
            raise SystemExit(
                f"Missing {RAW_ROOT}. Run `git mv` for the raw files first, "
                f"then re-run this script (see Phase 4 Plan 02 Task 2)."
            )

        for rel_path, upstream_url in URL_MAP.items():
            raw_path = RAW_ROOT / rel_path
            if not raw_path.exists():
                raise SystemExit(f"Expected raw file {raw_path} not found.")
            meta = {
                "retrieved_at": git_last_change(raw_path),
                "upstream_url": upstream_url,
                "sha256": sha256_of(raw_path),
                "http_status": None,              # backfill marker
                "publisher_last_modified": None,  # unknown for backfills
                "backfilled_at": BACKFILL_DATE,   # D-05 marker
            }
            meta_path = raw_path.with_suffix(raw_path.suffix + ".meta.json")
            meta_path.write_text(
                json.dumps(meta, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"wrote {meta_path}")


    if __name__ == "__main__":
        main()
    ```

    Do NOT execute this script yet — Task 2 moves the files first, then Task
    2 invokes this script as part of the atomic migration.
  </action>
  <verify>
    <automated>uv run python -c "import ast; ast.parse(open('scripts/backfill_sidecars.py').read())"</automated>
  </verify>
  <acceptance_criteria>
    - `scripts/backfill_sidecars.py` exists
    - `python -c "import ast; ast.parse(open('scripts/backfill_sidecars.py').read())"` exits 0 (parses)
    - `grep -c 'URL_MAP' scripts/backfill_sidecars.py` ≥ 1
    - `grep -c 'sha256' scripts/backfill_sidecars.py` ≥ 2 (hash function + field name)
    - `grep -q 'backfilled_at' scripts/backfill_sidecars.py` exits 0 (D-05 marker)
    - `grep -q 'git log' scripts/backfill_sidecars.py` exits 0 (retrieved_at source)
    - Five URLs present: `grep -c 'https' scripts/backfill_sidecars.py` ≥ 5
  </acceptance_criteria>
  <done>Backfill script ready to run — produces five sidecars given the expected data/raw/ layout.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Atomic raw-layer migration — git mv + loader updates + sidecar backfill in a single commit</name>
  <files>
    data/raw/lccc/actual-cfd-generation.csv,
    data/raw/lccc/actual-cfd-generation.csv.meta.json,
    data/raw/lccc/cfd-contract-portfolio-status.csv,
    data/raw/lccc/cfd-contract-portfolio-status.csv.meta.json,
    data/raw/elexon/agws.csv,
    data/raw/elexon/agws.csv.meta.json,
    data/raw/elexon/system-prices.csv,
    data/raw/elexon/system-prices.csv.meta.json,
    data/raw/ons/gas-sap.xlsx,
    data/raw/ons/gas-sap.xlsx.meta.json,
    src/uk_subsidy_tracker/data/lccc.py,
    src/uk_subsidy_tracker/data/elexon.py,
    src/uk_subsidy_tracker/data/ons_gas.py,
    src/uk_subsidy_tracker/data/lccc_datasets.yaml
  </files>
  <read_first>
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-04 (verbatim rename table), D-05 (sidecar shape), D-06 (atomic commit discipline)
    - .planning/phases/04-publishing-layer/04-PATTERNS.md §I (loader path migration — exact constant replacements)
    - .planning/phases/04-publishing-layer/04-RESEARCH.md Pitfall 5 (rename commit breaks CI signal detector)
    - src/uk_subsidy_tracker/data/lccc.py (read filename: handling — pd.read_csv(DATA_DIR / filename))
    - src/uk_subsidy_tracker/data/elexon.py:30-31 (AGWS_FILE, SYSTEM_PRICE_FILE constants)
    - src/uk_subsidy_tracker/data/ons_gas.py:12 (GAS_SAP_DATA_FILENAME constant)
    - src/uk_subsidy_tracker/data/lccc_datasets.yaml (filename: fields for both datasets)
  </read_first>
  <action>
    This task is a SINGLE ATOMIC COMMIT (per D-06). Execute in this exact order
    WITHOUT committing until step 6 confirms green pytest:

    ### Step 2.1 — Create the directories

    ```bash
    mkdir -p data/raw/lccc data/raw/elexon data/raw/ons
    ```

    ### Step 2.2 — `git mv` all five files (with D-04 hyphenation)

    ```bash
    git mv data/lccc-actual-cfd-generation.csv           data/raw/lccc/actual-cfd-generation.csv
    git mv data/lccc-cfd-contract-portfolio-status.csv   data/raw/lccc/cfd-contract-portfolio-status.csv
    git mv data/elexon_agws.csv                           data/raw/elexon/agws.csv
    git mv data/elexon_system_prices.csv                  data/raw/elexon/system-prices.csv
    git mv data/ons_gas_sap.xlsx                          data/raw/ons/gas-sap.xlsx
    ```

    Verify the moves:

    ```bash
    git status  # expect: renamed: ... (5 entries)
    ls data/raw/lccc/ data/raw/elexon/ data/raw/ons/
    ```

    ### Step 2.3 — Update loader constants (exact replacements)

    In `src/uk_subsidy_tracker/data/elexon.py` lines 30-31:

    Replace:
    ```python
    AGWS_FILE = DATA_DIR / "elexon_agws.csv"
    SYSTEM_PRICE_FILE = DATA_DIR / "elexon_system_prices.csv"
    ```
    With:
    ```python
    AGWS_FILE = DATA_DIR / "raw" / "elexon" / "agws.csv"
    SYSTEM_PRICE_FILE = DATA_DIR / "raw" / "elexon" / "system-prices.csv"
    ```

    In `src/uk_subsidy_tracker/data/ons_gas.py` line 12:

    Replace:
    ```python
    GAS_SAP_DATA_FILENAME = "ons_gas_sap.xlsx"
    ```
    With:
    ```python
    GAS_SAP_DATA_FILENAME = "raw/ons/gas-sap.xlsx"
    ```

    In `src/uk_subsidy_tracker/data/lccc.py`: the loader reads
    `pd.read_csv(DATA_DIR / filename)` where `filename` comes from the YAML.
    Check that the YAML update in Step 2.4 is sufficient (no hard-coded paths
    in lccc.py). If lccc.py contains any hard-coded `"lccc-actual-cfd-*"` or
    `"lccc-cfd-contract-*"` string, replace those too. Likely there are none
    — grep to confirm: `grep -n 'lccc-' src/uk_subsidy_tracker/data/lccc.py`
    should return 0 hits (the YAML owns the filename).

    ### Step 2.4 — Update `lccc_datasets.yaml` filename fields

    In `src/uk_subsidy_tracker/data/lccc_datasets.yaml`, replace the two
    `filename:` values:

    ```yaml
    # Before:
    filename: "lccc-actual-cfd-generation.csv"
    # After:
    filename: "raw/lccc/actual-cfd-generation.csv"

    # Before:
    filename: "lccc-cfd-contract-portfolio-status.csv"
    # After:
    filename: "raw/lccc/cfd-contract-portfolio-status.csv"
    ```

    Keep all other YAML keys (description, columns, etc.) UNCHANGED.

    ### Step 2.5 — Run backfill script to emit the five sidecars

    ```bash
    uv run python scripts/backfill_sidecars.py
    ```

    Expected output: five `wrote data/raw/.../*.meta.json` lines. If the
    script errors, investigate (likely a missing file — re-verify Step 2.2).

    Stage the five sidecars:

    ```bash
    git add data/raw/lccc/*.meta.json data/raw/elexon/*.meta.json data/raw/ons/*.meta.json
    ```

    ### Step 2.6 — Run the full test suite BEFORE committing

    ```bash
    uv run pytest tests/ -v
    ```

    This is the CI-green gate (Pitfall 5). If any test fails because of a
    path issue, investigate before committing. Common failure modes:
    - `FileNotFoundError` — a loader constant still points at the old path.
    - `pandera.SchemaError` — unrelated; not a rename issue.
    - Test count mismatch — should still be 36+4 (23 original + 13 drift tests
      from Plan 01) passing, plus 0 new failures.

    ### Step 2.7 — Atomic commit

    Stage ALL of: the 5 renames + 5 new sidecars + 3 loader edits + 1 YAML
    edit + scripts/backfill_sidecars.py (if not already staged from Task 1).

    ```bash
    git add src/uk_subsidy_tracker/data/elexon.py \
            src/uk_subsidy_tracker/data/ons_gas.py \
            src/uk_subsidy_tracker/data/lccc_datasets.yaml \
            src/uk_subsidy_tracker/data/lccc.py   # include if grep found any hard-coded paths
    git add scripts/backfill_sidecars.py
    git status  # verify: 5 R entries + 5 A (.meta.json) + 3-4 M + 1 A (script)

    git commit -m "refactor(04-02): migrate data/ to data/raw/<publisher>/<file> layout + sidecars

    Atomic raw-layer migration per Phase 4 CONTEXT D-04 / D-05 / D-06:

    - git mv all 5 raw files into data/raw/<publisher>/ with hyphenated names
    - backfill .meta.json sidecars (SHA-256 + git-log retrieved_at + backfilled_at marker)
    - update loader paths in elexon.py + ons_gas.py + lccc_datasets.yaml
    - ship scripts/backfill_sidecars.py for future re-runs

    Layout matches ARCHITECTURE.md §4.1. No functional change; CI green
    across this commit. Phase 5 (RO) adds data/raw/ofgem/ on this layout.

    Requirements: PUB-05 (three-layer pipeline source layer), GOV-02
    (sidecar SHA-256 + retrieval timestamp feed manifest.json provenance).
    "
    ```

    ### Step 2.8 — Post-commit verifications

    ```bash
    # 1. Rename similarity preserved (≥50% keeps R status in git log):
    git log --oneline --follow -- data/raw/lccc/actual-cfd-generation.csv
    # Expect: commits predating the rename resolve too.

    # 2. Green pytest on commit tip:
    uv run pytest tests/

    # 3. Chart generation still works:
    uv run python -m uk_subsidy_tracker.plotting
    # Expect: docs/charts/html/*.png regenerated without error.

    # 4. mkdocs build still strict-green:
    uv run mkdocs build --strict
    ```

    If any step 2.8 fails, DO NOT amend the commit — file a follow-up fix
    commit within this same plan's scope.
  </action>
  <verify>
    <automated>test -f data/raw/lccc/actual-cfd-generation.csv &amp;&amp; test -f data/raw/lccc/actual-cfd-generation.csv.meta.json &amp;&amp; test -f data/raw/lccc/cfd-contract-portfolio-status.csv.meta.json &amp;&amp; test -f data/raw/elexon/agws.csv.meta.json &amp;&amp; test -f data/raw/elexon/system-prices.csv.meta.json &amp;&amp; test -f data/raw/ons/gas-sap.xlsx.meta.json &amp;&amp; ! test -f data/elexon_agws.csv &amp;&amp; ! test -f data/ons_gas_sap.xlsx &amp;&amp; uv run pytest tests/ -x &amp;&amp; uv run python -m uk_subsidy_tracker.plotting &amp;&amp; uv run mkdocs build --strict</automated>
  </verify>
  <acceptance_criteria>
    - `test -d data/raw/lccc` exits 0
    - `test -d data/raw/elexon` exits 0
    - `test -d data/raw/ons` exits 0
    - `test -f data/raw/lccc/actual-cfd-generation.csv` exits 0
    - `test -f data/raw/lccc/cfd-contract-portfolio-status.csv` exits 0
    - `test -f data/raw/elexon/agws.csv` exits 0
    - `test -f data/raw/elexon/system-prices.csv` exits 0
    - `test -f data/raw/ons/gas-sap.xlsx` exits 0
    - ALL five original flat paths absent: `! test -f data/lccc-actual-cfd-generation.csv && ! test -f data/lccc-cfd-contract-portfolio-status.csv && ! test -f data/elexon_agws.csv && ! test -f data/elexon_system_prices.csv && ! test -f data/ons_gas_sap.xlsx`
    - Each of the five new files has a sibling `.meta.json`: `for f in data/raw/lccc/actual-cfd-generation.csv data/raw/lccc/cfd-contract-portfolio-status.csv data/raw/elexon/agws.csv data/raw/elexon/system-prices.csv data/raw/ons/gas-sap.xlsx; do test -f "${f}.meta.json" || exit 1; done`
    - Every sidecar has a valid 64-char hex sha256: `for f in data/raw/**/*.meta.json; do jq -r '.sha256' "$f" | grep -qE '^[0-9a-f]{64}$' || exit 1; done` (bash globstar or `find data/raw -name '*.meta.json'`)
    - Every sidecar has `backfilled_at: "2026-04-22"`: `jq -r '.backfilled_at' data/raw/lccc/actual-cfd-generation.csv.meta.json | grep -q '2026-04-22'`
    - Every sidecar has a non-null `retrieved_at`: `jq -r '.retrieved_at' data/raw/lccc/actual-cfd-generation.csv.meta.json | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T'`
    - `grep -q 'raw/lccc/actual-cfd-generation.csv' src/uk_subsidy_tracker/data/lccc_datasets.yaml` exits 0
    - `grep -q 'raw/lccc/cfd-contract-portfolio-status.csv' src/uk_subsidy_tracker/data/lccc_datasets.yaml` exits 0
    - `grep -qE 'raw.*elexon.*agws\.csv' src/uk_subsidy_tracker/data/elexon.py` exits 0
    - `grep -qE 'raw.*elexon.*system-prices\.csv' src/uk_subsidy_tracker/data/elexon.py` exits 0
    - `grep -q 'raw/ons/gas-sap.xlsx' src/uk_subsidy_tracker/data/ons_gas.py` exits 0
    - NO hard-coded old paths remain: `! grep -rE 'elexon_agws\.csv|elexon_system_prices\.csv|lccc-actual-cfd-generation\.csv|lccc-cfd-contract-portfolio-status\.csv|ons_gas_sap\.xlsx' src/ tests/` returns exit 0 (no matches)
    - `uv run pytest tests/` exits 0 (CI green on rename commit tip per D-06)
    - `uv run python -m uk_subsidy_tracker.plotting` exits 0 (chart generation unaffected)
    - `uv run mkdocs build --strict` exits 0 (docs build still green)
    - `git log --follow --oneline data/raw/lccc/actual-cfd-generation.csv | wc -l` returns ≥2 (pre-rename history resolves — rename similarity held)
    - Commit message body mentions `PUB-05` AND `GOV-02` AND `D-04`
  </acceptance_criteria>
  <done>All five raw files live at data/raw/<publisher>/<file> with hyphenated names; each has a sibling .meta.json with valid SHA-256; three loader files + one YAML config updated; scripts/backfill_sidecars.py committed; full test suite green; chart generation + mkdocs build both green; single atomic commit with R entries preserving git history.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: CHANGES.md entry + STATE.md todo closure for raw-layer migration</name>
  <files>CHANGES.md</files>
  <read_first>
    - CHANGES.md [Unreleased] block (Plan 01 already added Wave 0 entries)
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-04 / D-05 / D-06 (wording to mirror)
  </read_first>
  <action>
    Add under the existing `## [Unreleased]` → `### Changed` subsection (create
    if missing; Plan 01 only used `### Added`):

    ```markdown
    ### Changed

    - **Raw data layout migrated** from flat `data/*.csv` / `data/*.xlsx` to the canonical `data/raw/<publisher>/<file>` nested structure per ARCHITECTURE §4.1. Filenames hyphenated (underscores → hyphens). Five files renamed atomically via `git mv`:
      - `data/lccc-actual-cfd-generation.csv` → `data/raw/lccc/actual-cfd-generation.csv`
      - `data/lccc-cfd-contract-portfolio-status.csv` → `data/raw/lccc/cfd-contract-portfolio-status.csv`
      - `data/elexon_agws.csv` → `data/raw/elexon/agws.csv`
      - `data/elexon_system_prices.csv` → `data/raw/elexon/system-prices.csv`
      - `data/ons_gas_sap.xlsx` → `data/raw/ons/gas-sap.xlsx`
    - Loaders updated in the same commit: `src/uk_subsidy_tracker/data/{lccc.py,elexon.py,ons_gas.py,lccc_datasets.yaml}`. CI stayed green across the rename commit (D-06).
    ```

    Add under `### Added`:

    ```markdown
    - `.meta.json` sidecars for all five raw files (D-05): `{retrieved_at, upstream_url, sha256, http_status, publisher_last_modified, backfilled_at}`. `retrieved_at` best-effort from git log; `http_status` + `publisher_last_modified` are `null` (backfill markers); `backfilled_at: "2026-04-22"` flags reconstructed entries.
    - `scripts/backfill_sidecars.py` — one-shot backfill helper, retained for future re-runs on fresh re-scrapes.
    ```
  </action>
  <verify>
    <automated>grep -q 'data/raw/<publisher>' CHANGES.md &amp;&amp; grep -q '.meta.json sidecars' CHANGES.md &amp;&amp; grep -q 'backfill_sidecars.py' CHANGES.md &amp;&amp; uv run mkdocs build --strict</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c 'data/raw' CHANGES.md` ≥ 2 (at least two bullets reference the new layout)
    - `grep -q '.meta.json' CHANGES.md` exits 0
    - `grep -q 'backfill_sidecars' CHANGES.md` exits 0
    - `grep -q 'D-0[456]' CHANGES.md` exits 0 (at least one of D-04/D-05/D-06 cited for traceability)
    - `uv run mkdocs build --strict` exits 0 (docs still green after CHANGES.md diff)
  </acceptance_criteria>
  <done>CHANGES.md records the migration + sidecar backfill + helper script under [Unreleased].</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| git working tree → commit | Atomic rename commit writes to history; if the rename is interrupted mid-way the repo is half-renamed. |
| scripts/backfill_sidecars.py → git log | Shell-out to `git log` happens on developer / CI machines only; not at runtime in prod. |
| Sidecar JSON → manifest.json | Plan 04's manifest.py reads each sidecar's `sha256` + `retrieved_at` + `upstream_url`. A tampered sidecar → tampered manifest → academic citation lineage broken. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-04-02-01 | Tampering | sidecar `.meta.json` file hand-edited without matching raw file change | mitigate | Plan 04's `manifest.py::build()` re-computes sha256 from raw file (does NOT trust sidecar-reported hash) — the sidecar is metadata, the raw file is truth. This plan also ships `scripts/backfill_sidecars.py` which overwrites sidecars from ground truth so drift is self-healing on next run. |
| T-04-02-02 | Tampering | raw file edited without sidecar update | mitigate | Plan 04 + Plan 05 `refresh_all.py::upstream_changed()` compare live sha256 vs sidecar.sha256; mismatch triggers refresh. Plan 03 pandera schema validation at derived-layer-build catches any content mutations that would produce invalid Parquet. |
| T-04-02-03 | Information Disclosure | sidecar leaks PII or secrets | accept | All data in `data/raw/` is UK government open data; sidecar fields are hash + URL + timestamp only. No PII vector. |
| T-04-02-04 | Denial of Service | rename commit breaks CI, blocks team (=user) | mitigate | Task 2 Step 2.6 runs `uv run pytest` BEFORE committing; Pitfall 5 check. D-06 atomicity contract holds. |
| T-04-02-05 | Repudiation | git mv rename loses history (similarity <50%) | mitigate | Task 2 Step 2.8 verification #1 runs `git log --follow` post-commit; if history is broken, fail loud and re-commit without reflow. |
</threat_model>

<verification>
Phase-4 Plan 02 verifications:

1. Migration atomicity: `git log --name-status HEAD | grep -cE '^R.*data/.*->.*data/raw'` returns 5 (five R[ename] entries on the single migration commit)
2. Sidecar integrity: `for f in data/raw/**/*.meta.json; do jq empty "$f" || exit 1; done` (all valid JSON)
3. Loader correctness: `uv run pytest tests/` — 36+4+new tests all pass
4. Chart generation: `uv run python -m uk_subsidy_tracker.plotting` — emits PNG/HTML to docs/charts/html/ without error
5. Docs strict-build: `uv run mkdocs build --strict` — no new broken references
6. Rename history: `git log --follow --oneline data/raw/lccc/actual-cfd-generation.csv` returns ≥2 commits (pre-rename commits resolve via --follow)
</verification>

<success_criteria>
- Five raw files live under `data/raw/<publisher>/` with hyphenated names per D-04 table
- Five sibling `.meta.json` sidecars exist with valid SHA-256 hashes (64-char hex)
- Loader files (`lccc.py`, `elexon.py`, `ons_gas.py`) and `lccc_datasets.yaml` all updated IN THE SAME COMMIT
- `uv run pytest tests/` green on the migration commit tip (CI stays green across rename per D-06)
- `uv run python -m uk_subsidy_tracker.plotting` succeeds (charts still build)
- `uv run mkdocs build --strict` green (docs still build)
- `git log --follow` resolves pre-rename history on at least one moved file
- No hard-coded old paths remain anywhere in `src/` or `tests/`
- `scripts/backfill_sidecars.py` is present, parseable, and has been run at least once
- `CHANGES.md` [Unreleased] records the migration + sidecar + script
</success_criteria>

<output>
After completion, create `.planning/phases/04-publishing-layer/04-02-SUMMARY.md`.
Must include:
- List of the five SHA-256 hashes (12-char prefix each is sufficient) so Plan 04 can cross-verify manifest.py output
- Any hard-coded path found in `src/uk_subsidy_tracker/data/lccc.py` during Task 2 (there should be none — confirm)
- Confirmation that chart regeneration post-rename produced byte-identical PNGs to pre-rename (bonus: adversarial check on determinism path)
- Note whether git rename similarity held (yes = R status in git log; no = A+D pair with manual investigation)
</output>
