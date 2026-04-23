# Phase 5: RO Module — Pattern Map

**Mapped:** 2026-04-22
**Files analyzed:** 27 (20 new, 7 modified)
**Analogs found:** 25 / 27 (2 files have no analog — flagged below)
**Package root confirmed:** `src/uk_subsidy_tracker/` (NOT `src/cfd_payment/`; repo dir still `cfd-payment/` but package renamed Phase 4)

## Critical Divergence Upfront — `publish/manifest.py` NOT auto-iterating

The orchestrator brief asserts `publish/manifest.py` "already iterates `SCHEMES`; no code change needed". **This is incorrect as of HEAD.** Inspection shows:

- `manifest.py::_assemble_dataset_entries()` hard-codes `id=f"cfd.{grain}"` and `parquet_url=f"{base}/data/latest/cfd/{grain}.parquet"` (lines 307, 311-314).
- `build()` receives `derived_dir` as a parameter, but `refresh_all.publish_latest()` calls it with `DERIVED_DIR / "cfd"` as a hard-coded path (refresh_all.py:84).
- `GRAIN_SOURCES`, `GRAIN_TITLES`, `GRAIN_DESCRIPTIONS` are CfD-only (manifest.py:58-100).

**Planner must plan a refactor of `publish/manifest.py` + `refresh_all.publish_latest()` to iterate `SCHEMES`, OR accept that RO grains will not surface in `manifest.json` until a follow-up.** Flag this explicitly in planning; do NOT let it become a Phase 5 gap-closure surprise like Phase 4's refresh-loop.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| **NEW** `src/uk_subsidy_tracker/data/ofgem_ro.py` | data-ingest | request-response + atomic file I/O | `src/uk_subsidy_tracker/data/lccc.py` + `ons_gas.py` | role + data-flow exact |
| **NEW** `src/uk_subsidy_tracker/data/roc_prices.py` | data-ingest | request-response + atomic file I/O | `src/uk_subsidy_tracker/data/lccc.py` + `ons_gas.py` | role + data-flow exact |
| **NEW** `src/uk_subsidy_tracker/data/ro_bandings.yaml` | constants-yaml | static fixture | `src/uk_subsidy_tracker/data/lccc_datasets.yaml` | structural (shape only; content different) |
| **NEW** `src/uk_subsidy_tracker/data/ro_bandings.py` | data-config | Pydantic + YAML loader | `src/uk_subsidy_tracker/data/lccc.py` (LCCCDatasetConfig + LCCCAppConfig + load_lccc_config) | role exact |
| **NEW** `src/uk_subsidy_tracker/schemas/ro.py` | schema | Pydantic row models | `src/uk_subsidy_tracker/schemas/cfd.py` | role + data-flow exact |
| **MOD** `src/uk_subsidy_tracker/schemas/__init__.py` | barrel-export | static re-export | `src/uk_subsidy_tracker/schemas/__init__.py` (self, extend list) | self |
| **NEW** `src/uk_subsidy_tracker/schemes/ro/__init__.py` | scheme-module-core | §6.1 contract functions | `src/uk_subsidy_tracker/schemes/cfd/__init__.py` | role + data-flow exact (verbatim template) |
| **NEW** `src/uk_subsidy_tracker/schemes/ro/_refresh.py` | scheme-internal | request-response + SHA dirty-check | `src/uk_subsidy_tracker/schemes/cfd/_refresh.py` | role + data-flow exact |
| **NEW** `src/uk_subsidy_tracker/schemes/ro/cost_model.py` | scheme-internal | transform raw → Parquet | `src/uk_subsidy_tracker/schemes/cfd/cost_model.py` | role + data-flow exact |
| **NEW** `src/uk_subsidy_tracker/schemes/ro/aggregation.py` | scheme-internal | Parquet re-read → rollup Parquet | `src/uk_subsidy_tracker/schemes/cfd/aggregation.py` | role + data-flow exact |
| **NEW** `src/uk_subsidy_tracker/schemes/ro/forward_projection.py` | scheme-internal | station → forward-year projection | `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py` | role + data-flow exact |
| **NEW** `src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py` | chart | Parquet → Plotly PNG+HTML | `plotting/subsidy/cfd_dynamics.py` | role + data-flow exact (4-panel) |
| **NEW** `src/uk_subsidy_tracker/plotting/subsidy/ro_by_technology.py` | chart | Parquet → Plotly PNG+HTML (stacked) | `plotting/subsidy/cfd_payments_by_category.py` | role + data-flow exact |
| **NEW** `src/uk_subsidy_tracker/plotting/subsidy/ro_concentration.py` | chart | Parquet → Plotly PNG+HTML (Lorenz) | `plotting/subsidy/lorenz.py` | role + data-flow exact |
| **NEW** `src/uk_subsidy_tracker/plotting/subsidy/ro_forward_projection.py` | chart | Parquet → Plotly PNG+HTML (drawdown) | `plotting/subsidy/remaining_obligations.py` | role + data-flow exact |
| **NEW** `src/uk_subsidy_tracker/plotting/subsidy/_shared.py` | utility | shared helpers | NO ANALOG (new file; opportunistic) | no analog |
| **MOD** `src/uk_subsidy_tracker/counterfactual.py` | scheme-shared | dict extension | self (`DEFAULT_CARBON_PRICES` block) | self-modification |
| **MOD** `src/uk_subsidy_tracker/refresh_all.py` | registration | one-line SCHEMES append | self (SCHEMES tuple) | self-modification |
| **MOD** `src/uk_subsidy_tracker/publish/manifest.py` | **refactor** | CfD-hardcoded → multi-scheme | self + `refresh_all.publish_latest` | self-modification — **see Divergence Upfront** |
| **NEW** `docs/schemes/ro.md` | docs-scheme-page | static markdown | NO DIRECT ANALOG (theme pages only) — closest: `docs/themes/cost/index.md` + `docs/themes/cost/cfd-dynamics.md` | structural (scheme-level page is new pattern) |
| **MOD** `mkdocs.yml` | nav/link | YAML nav block | self (existing Cost/Recipients sections) | self-modification |
| **MOD** `docs/index.md` | nav/link | static markdown | self | self-modification |
| **MOD** `docs/themes/cost/index.md` | nav/link | gallery grid extension | self (existing `grid cards` block) | self-modification |
| **MOD** `docs/themes/recipients/index.md` | nav/link | gallery grid extension | self (existing `grid cards` block) | self-modification |
| **MOD** `CHANGES.md` | docs-log | Keep-a-Changelog append | self | self-modification |
| **MOD** `tests/test_schemas.py` | test-parametrisation | pytest parametrize over RO grains | self (lines 98-126, existing CfD parametrise block) | self-extension |
| **MOD** `tests/test_aggregates.py` | test-parametrisation | pytest parametrize over RO rollups | self (lines 64-126) | self-extension |
| **MOD** `tests/test_determinism.py` | test-parametrisation | pytest parametrize over RO grains | self (lines 24-63) | self-extension |
| **MOD** `tests/test_benchmarks.py` | test-parametrisation | new REF Constable reconciliation test | self (lines 115-150 external-anchor block) + `lccc_self` floor pattern | self-extension |
| **MOD** `tests/fixtures/benchmarks.yaml` | constants-yaml | YAML section append | self | self-modification |
| **MOD** `tests/fixtures/constants.yaml` | constants-yaml | 14 new Provenance entries (2002-2017) | self (existing `DEFAULT_CARBON_PRICES_2021` etc.) | self-extension |
| **MOD** `tests/fixtures/__init__.py` | data-config | extend Benchmarks model with `ref_constable` field | self (lines 35-57 Benchmarks class) | self-extension |
| **MOD** `tests/test_constants_provenance.py` | test-parametrisation | extend `_TRACKED` set | self (line 40-47) | self-extension |
| **NEW** `tests/data/test_ofgem_ro.py` | test-new | mocked scraper path tests | `tests/test_ons_gas_download.py` + `tests/test_refresh_loop.py` (importlib bypass) | role + data-flow exact |
| **NEW** `data/raw/ofgem/{ro-register.xlsx, ro-generation.csv, roc-prices.csv}` + `.meta.json` | raw-seed | fixture commit | `data/raw/{lccc,elexon,ons}/*` | pattern (file layout only) |

---

## Pattern Assignments

### `src/uk_subsidy_tracker/schemes/ro/__init__.py` (scheme-module-core, §6.1)

**Analog:** `src/uk_subsidy_tracker/schemes/cfd/__init__.py`

**Mirror verbatim** — this is the load-bearing §6.1 template. Only string substitutions: `cfd` → `ro`, `CfD` → `RO`, plus RO-specific validate() checks per CONTEXT D-04.

**Skeleton (lines 20-36, 38, 41-124):**
```python
from __future__ import annotations
from pathlib import Path

from uk_subsidy_tracker import PROJECT_ROOT
from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.schemes.ro._refresh import (
    refresh as _refresh,
    upstream_changed as _upstream_changed,
)
from uk_subsidy_tracker.schemes.ro.aggregation import (
    build_annual_summary,
    build_by_allocation_round,
    build_by_technology,
)
from uk_subsidy_tracker.schemes.ro.cost_model import build_station_month
from uk_subsidy_tracker.schemes.ro.forward_projection import build_forward_projection

DERIVED_DIR: Path = PROJECT_ROOT / "data" / "derived" / "ro"

def upstream_changed() -> bool: return _upstream_changed()
def refresh() -> None: _refresh()

def rebuild_derived(output_dir: Path | None = None) -> None:
    target = output_dir if output_dir is not None else DERIVED_DIR
    target.mkdir(parents=True, exist_ok=True)
    build_station_month(target)
    build_annual_summary(target)
    build_by_technology(target)
    build_by_allocation_round(target)
    build_forward_projection(target)

def regenerate_charts() -> None:
    import runpy
    runpy.run_module("uk_subsidy_tracker.plotting", run_name="__main__")

def validate() -> list[str]: ...  # RO-specific 4 checks per D-04

__all__ = ["DERIVED_DIR", "upstream_changed", "refresh", "rebuild_derived",
           "regenerate_charts", "validate"]
```

**Divergence:**
- `validate()` body replaced per CONTEXT D-04: (1) banding divergence warn if >10 stations or >5% outside 1% delta; (2) Turver/REF-Constable band drift warn if aggregate outside ±3%; (3) methodology_version drift (shared check); (4) forward-projection sanity (negative costs / >50% MWh jumps).
- Verify Protocol conformance at test collection time: `isinstance(ro, SchemeModule)` already handled by `schemes/__init__.py`.

**Planner handoff:** Copy 135-line file byte-identically with CfD→RO string replacement; then replace `validate()` body with the 4-check impl from D-04. `schemes/ro/__init__.py::__init__` does NOT need to be a package-init surface beyond public exports — mirror the CfD file exactly.

---

### `src/uk_subsidy_tracker/schemes/ro/_refresh.py` (scheme-internal, request-response + SHA compare)

**Analog:** `src/uk_subsidy_tracker/schemes/cfd/_refresh.py`

**Module-constant pattern (lines 20-42):**
```python
_RAW_FILES = [
    "raw/ofgem/ro-register.xlsx",
    "raw/ofgem/ro-generation.csv",
    "raw/ofgem/roc-prices.csv",
]

_URL_MAP = {
    "raw/ofgem/ro-register.xlsx": "...",       # Ofgem RER or stable URL chosen per D-Discretion
    "raw/ofgem/ro-generation.csv": "...",
    "raw/ofgem/roc-prices.csv": "...",
}
```

**SHA-compare pattern (lines 45-68, copy verbatim):**
```python
def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()

def upstream_changed() -> bool:
    for rel in _RAW_FILES:
        raw = DATA_DIR / rel
        meta = raw.with_suffix(raw.suffix + ".meta.json")
        if not raw.exists() or not meta.exists():
            return True
        sidecar = json.loads(meta.read_text())
        if _sha256(raw) != sidecar.get("sha256"):
            return True
    return False
```

**refresh() wiring pattern (lines 71-111):**
```python
def refresh() -> None:
    from uk_subsidy_tracker.data.ofgem_ro import download_ofgem_ro_register, download_ofgem_ro_generation
    from uk_subsidy_tracker.data.roc_prices import download_roc_prices
    from uk_subsidy_tracker.data.sidecar import write_sidecar

    # 1-3: call the three downloaders (may fail-loud per D-17).
    download_ofgem_ro_register()
    download_ofgem_ro_generation()
    download_roc_prices()

    # 4: rewrite every sidecar so SHA matches + retrieved_at = now.
    for rel, upstream_url in _URL_MAP.items():
        raw_path = DATA_DIR / rel
        if not raw_path.exists():
            raise FileNotFoundError(
                f"refresh() downloaded but raw file missing: {raw_path}. "
                f"Upstream URL: {upstream_url}"
            )
        write_sidecar(raw_path=raw_path, upstream_url=upstream_url)
```

**Divergence:**
- 3 files vs CfD's 5.
- Scraper option (per CONTEXT "Claude's Discretion") may be Playwright/MS Graph/direct-URL; whichever the planner chooses, the downloader functions it produces must match the interface (no-arg callable that writes to `DATA_DIR / rel` and returns `None` or `Path`). If RER auth fails all three options, plan escalates to user before committing to manual snapshot.
- `_URL_MAP` must match whatever `scripts/backfill_sidecars.py::URL_MAP` becomes when the planner extends it for RO raw files (cross-file byte-parity rule from CfD `_refresh.py` docstring lines 28-29).

**Planner handoff:** Mirror the CfD file structure; scraper implementation in `data/ofgem_ro.py` + `data/roc_prices.py` is the unknown; `refresh()` wiring is the known template.

---

### `src/uk_subsidy_tracker/schemes/ro/cost_model.py` (scheme-internal, transform raw → Parquet)

**Analog:** `src/uk_subsidy_tracker/schemes/cfd/cost_model.py`

**Imports + schema pattern (lines 14-44):**
```python
from __future__ import annotations
from pathlib import Path
import pandas as pd
import pandera.pandas as pa
import pyarrow as pa_arrow
import pyarrow.parquet as pq

from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION, compute_counterfactual
from uk_subsidy_tracker.schemas.ro import StationMonthRow, emit_schema_json

station_month_schema = pa.DataFrameSchema(
    { # one pa.Column(...) per StationMonthRow field
      # RO-specific columns: country, obligation_year, rocs_issued, banding_factor_ofgem,
      # banding_factor_yaml, ro_cost_gbp, ro_cost_gbp_eroc, ro_cost_gbp_nocarbon,
      # gas_counterfactual_gbp, premium_gbp, mutualisation_gbp, ...
    },
    strict=False, coerce=True,
)
```

**Deterministic Parquet writer — IMPORT don't copy (lines 47-68):**
```python
# DO NOT re-implement _write_parquet. Import from schemes/cfd/cost_model.py:
from uk_subsidy_tracker.schemes.cfd.cost_model import _write_parquet
```
The writer is intentionally shared across schemes (already imported by `schemes/cfd/aggregation.py` line 39 and `schemes/cfd/forward_projection.py` line 24 — established pattern).

**build_station_month() pattern (lines 71-157) — the template:**
```python
def build_station_month(output_dir: Path) -> pd.DataFrame:
    # (1) Load raw via new loaders:
    #   gen = load_ofgem_ro_generation()         (pandera-validated inside loader)
    #   register = load_ofgem_ro_register()
    #   prices = load_roc_prices()
    #   bandings = load_ro_bandings()           (RoBandingTable)
    # (2) Join register + generation on station_id:
    #   df = gen.merge(register[["station_id", "technology", "country",
    #                            "commissioning_date", "operator"]], on="station_id", how="left")
    # (3) Assign obligation_year per D-08: OY containing output_period_end.
    # (4) Ofgem-primary rocs_issued per D-01:
    #   df["banding_factor_yaml"] = df.apply(lambda r: bandings.lookup(
    #       r["technology"], r["country"], r["commissioning_date"]), axis=1)
    #   df["rocs_computed"] = df["generation_mwh"] * df["banding_factor_yaml"]
    #   df["banding_delta_pct"] = (df["rocs_issued"] - df["rocs_computed"]).abs() / df["rocs_issued"]
    # (5) Join prices on obligation_year → buyout_gbp_per_roc + recycle_gbp_per_roc + mutualisation_gbp
    #     (mutualisation_gbp null except OY 2021-22 per D-11 research).
    # (6) Primary ro_cost_gbp = rocs_issued × (buyout + recycle) + mutualisation_gbp
    #     Sensitivity ro_cost_gbp_eroc = rocs_issued × eroc_clearing_gbp_per_roc.
    #     Sensitivity ro_cost_gbp_nocarbon = rocs_issued × (buyout + recycle with carbon-price=0).
    # (7) Gas counterfactual join at month_end via compute_counterfactual()
    #     — reads the extended DEFAULT_CARBON_PRICES dict (2002-2026) unchanged.
    # (8) df["methodology_version"] = METHODOLOGY_VERSION
    # (9) Sort + column-order + pandera validate + write:
    columns = list(StationMonthRow.model_fields.keys())
    df = (df[columns]
          .sort_values(["station_id", "month_end"], kind="mergesort")
          .reset_index(drop=True))
    df = station_month_schema.validate(df)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_parquet(df, output_dir / "station_month.parquet")
    emit_schema_json(StationMonthRow, output_dir / "station_month.schema.json")
    return df
```

**Divergence (RO-specific vs CfD):**
- **3 input loaders** (register + generation + prices) vs CfD's 2 (gen + portfolio).
- **`country` column** (`'GB'` | `'NI'`) on every row per D-09.
- **`obligation_year` column** per D-08 (April-March span containing output_period_end).
- **Dual cost columns** (`ro_cost_gbp` primary, `ro_cost_gbp_eroc` sensitivity, `ro_cost_gbp_nocarbon` sensitivity) per D-02, D-05.
- **Bandings cross-check** per D-01: compute both `rocs_issued` (Ofgem-primary) and `banding_factor_yaml × generation_mwh`; log warning when delta >1%. The warning fires in `schemes/ro/__init__.py::validate()` not here.
- **Mutualisation delta** per D-11: non-null for OY 2021-22 only.

**Planner handoff:** `schemes/ro/cost_model.py` is the largest new module (~250 lines vs CfD's 158); the raw→Parquet transform is longer because of the 3-way join + dual-cost sensitivity branches. `_write_parquet` IS imported, not re-declared.

---

### `src/uk_subsidy_tracker/schemes/ro/aggregation.py` (scheme-internal, Parquet re-read → rollups)

**Analog:** `src/uk_subsidy_tracker/schemes/cfd/aggregation.py`

**`_read_station_month` helper pattern (lines 42-49, copy verbatim):**
```python
def _read_station_month(output_dir: Path) -> pd.DataFrame:
    path = output_dir / "station_month.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found — call build_station_month(output_dir) first."
        )
    return pq.read_table(path).to_pandas()
```

**int64 year cast pattern (Phase 4 Rule-1 auto-fix — lines 68, 125, 158 of CfD aggregation):**
```python
sm["year"] = sm["month_end"].dt.year.astype("int64")
# Mandatory cast — pandas dt.year returns int32; Pydantic row models declare int64.
```

**groupby + int64 + rollup pattern (lines 121-146 of CfD aggregation, template for by_technology):**
```python
def build_by_technology(output_dir: Path) -> pd.DataFrame:
    sm = _read_station_month(output_dir)
    sm["year"] = sm["month_end"].dt.year.astype("int64")
    df = (sm.groupby(["year", "technology"], sort=True, dropna=False)
            .agg(
                ro_generation_mwh=("generation_mwh", "sum"),       # RO-specific column names
                ro_cost_gbp=("ro_cost_gbp", "sum"),
                ro_cost_gbp_eroc=("ro_cost_gbp_eroc", "sum"),
            )
            .reset_index())
    df["methodology_version"] = METHODOLOGY_VERSION
    columns = list(ByTechnologyRow.model_fields.keys())
    df = df[columns].sort_values(["year", "technology"], kind="mergesort").reset_index(drop=True)
    _write_parquet(df, output_dir / "by_technology.parquet")
    emit_schema_json(ByTechnologyRow, output_dir / "by_technology.schema.json")
    return df
```

**Divergence (RO-specific):**
- Three rollups per CONTEXT: `annual_summary`, `by_technology`, `by_allocation_round` (the last reuses `commissioning_window` or `country` as the "round" axis — planner decides; RO-MODULE-SPEC §5 hints commissioning-window-based). Plus `forward_projection` (separate module).
- `annual_summary` rows emitted per **(obligation_year × country)** tuple per D-09 — two rows per year rather than one.
- Counterfactual join in `annual_summary` uses `compute_counterfactual()` against the **extended DEFAULT_CARBON_PRICES 2002-2017** — the join code is unchanged; the upstream dict is what changes.
- No `avoided_co2_tonnes` column on RO (that was CfD LCCC-specific); replace with `rocs_issued` or drop to match schema.

**Planner handoff:** Copy the three-builder structure; substitute RO column names; the `int64` cast line is non-negotiable (Phase 4 Rule-1 auto-fix).

---

### `src/uk_subsidy_tracker/schemes/ro/forward_projection.py` (scheme-internal, forward-year extrapolation)

**Analog:** `src/uk_subsidy_tracker/schemes/cfd/forward_projection.py`

**Deterministic anchor pattern (lines 97-99 of CfD, LOAD-BEARING — Phase 4 D-21):**
```python
# Deterministic "current year" anchor: latest settlement date in the
# raw data rounded to year. D-21: pure function of raw content.
current_year_anchor = int(gen["Settlement_Date"].max().year)
# NEVER: pd.Timestamp.now().year — breaks test_determinism.
```

**RO adaptation:**
```python
# For RO, anchor on the latest observed obligation-year-end in ro-generation.csv:
current_year_anchor = int(gen["output_period_end"].max().year)
```

**Contract-end calculation pattern (lines 49-63 of CfD):**
```python
units["contract_start_year"] = units["start"].dt.year.astype("Int64")
units["contract_end_year"] = (units["contract_start_year"] + units["contract_years"]).astype("Int64")
```

**RO divergence — accreditation-end field chosen per CONTEXT "Claude's Discretion":**
- Option A: Per-station `expected_end_date` from Ofgem register (preferred if available).
- Option B: `commissioning_date + 20_years` as a uniform rule (RO supports max 20-year accreditation per station per SI 2009/785).
- Option C: Scheme closes 2037-03-31 globally (hard cap per ARCHITECTURE §2).
Whichever the planner picks, the projection anchor is `max(metered_obligation_year)`; the remaining years per station is `min(expected_end_year, 2037) - current_year_anchor`. Output is capped at 2037.

**Planner handoff:** Deterministic anchor (`max(output_period_end).year`) is non-negotiable. Extrapolation methodology is Claude's Discretion; document the chosen rule in the module docstring per Phase 4 D-21 pattern.

---

### `src/uk_subsidy_tracker/data/ofgem_ro.py` + `src/uk_subsidy_tracker/data/roc_prices.py` (data-ingest)

**Analog (structure + loader pair):** `src/uk_subsidy_tracker/data/lccc.py`
**Analog (error-path):** `src/uk_subsidy_tracker/data/ons_gas.py` (D-17 fail-loud bare `raise`)

**Imports + Pydantic config + download pattern (LCCC lines 1-32, 77-102):**
```python
from pathlib import Path
import pandas as pd
import pandera.pandas as pa
import requests
import yaml
from pydantic import BaseModel

from uk_subsidy_tracker import DATA_DIR
from uk_subsidy_tracker.data.utils import HEADERS

# Pandera schemas (loader-owned validation):
ro_register_schema = pa.DataFrameSchema({ ... }, strict=False, coerce=True)
ro_generation_schema = pa.DataFrameSchema({ ... }, strict=False, coerce=True)

def download_ofgem_ro_register() -> Path:
    output_path = DATA_DIR / "raw/ofgem/ro-register.xlsx"  # BOUND BEFORE try (gap #2 fix)
    try:
        response = requests.get(URL, headers=HEADERS, stream=True, timeout=60)  # timeout=60 mandatory
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading ro-register.xlsx: {e}")
        raise  # fail-loud per D-17 — no silent swallow
```

**Loader-owned validation pattern (LCCC lines 105-114):**
```python
def load_ofgem_ro_register() -> pd.DataFrame:
    df = pd.read_excel(DATA_DIR / "raw/ofgem/ro-register.xlsx")
    df = ro_register_schema.validate(df)
    return df
```

**Divergence (RO-specific):**
- **XLSX parsing** (register is an Ofgem spreadsheet) — import pattern identical to `ons_gas.py::load_gas_price()` XLSX handler (lines 58-67): `pd.read_excel(path, sheet_name="...", header=...)`; header-row detection may be needed.
- **Multiple downloaders per module** — `ofgem_ro.py` hosts `download_ofgem_ro_register()` + `download_ofgem_ro_generation()`; `roc_prices.py` hosts `download_roc_prices()` (combining buyout + recycle + e-ROC into one CSV via `pd.concat` or as separate fetches appended).
- **Claude's Discretion — scraper mechanism:** planner picks Playwright/MS Graph/direct-URL per CONTEXT post-amendment. Regardless of chosen transport, the `requests.get` pattern shown here is for fallback direct-URL option; Playwright calls would replace the `requests.get(...)` line but still honour `timeout=60`, fail-loud, output_path-bound-before-try.

**Planner handoff:** `ons_gas.py` is the closer error-path template (has `timeout=60`, bare-raise, output_path-before-try); `lccc.py` is the closer structural template (has `LCCCDatasetConfig` + multi-file config). RO takes both.

---

### `src/uk_subsidy_tracker/data/ro_bandings.py` + `ro_bandings.yaml` (data-config)

**Analog:** `src/uk_subsidy_tracker/data/lccc.py::LCCCDatasetConfig` + `LCCCAppConfig` + `load_lccc_config`
**Analog (YAML shape):** `src/uk_subsidy_tracker/data/lccc_datasets.yaml`
**Analog (Provenance discipline):** RESEARCH §10 + `tests/fixtures/constants.yaml` entries

**Two-layer Pydantic pattern (lccc.py lines 16-32):**
```python
# Schema for a single banding entry
class RoBandingEntry(BaseModel):
    technology: str
    country: str                            # 'GB' or 'NI'
    commissioning_window_start: date | None # None = grandfathered / pre-banding
    commissioning_window_end: date | None
    banding_factor: float                   # ROCs per MWh
    chp: bool = False                       # CHP flag where a banding cell is CHP-specific
    grandfathered: bool = False             # pre-2006-07-11 1-ROC/MWh override
    # Provenance block (constant-provenance pattern per user memory):
    source: str                             # e.g. "Renewables Obligation Order 2009 (SI 2009/785)"
    url: HttpUrl
    basis: str                              # e.g. "Schedule 2, 2013-2017 banding review"
    retrieved_on: date
    next_audit: date | None = None

# Container + lookup
class RoBandingTable(BaseModel):
    entries: list[RoBandingEntry]

    def lookup(self, technology: str, country: str, commissioning_date: date) -> float:
        for e in self.entries:
            if e.technology == technology and e.country == country:
                if (e.commissioning_window_start is None
                    or commissioning_date >= e.commissioning_window_start):
                    if (e.commissioning_window_end is None
                        or commissioning_date <= e.commissioning_window_end):
                        return e.banding_factor
        raise KeyError(f"No banding for ({technology}, {country}, {commissioning_date})")

def load_ro_bandings(config_path: str = "ro_bandings.yaml") -> RoBandingTable:
    default_dir = Path(__file__).parent
    with open(default_dir / config_path, "r") as f:
        raw = yaml.safe_load(f)
    return RoBandingTable(**raw)
```

**YAML shape (ro_bandings.yaml) — analog `lccc_datasets.yaml`:**
```yaml
entries:
  - technology: "Offshore wind"
    country: "GB"
    commissioning_window_start: null
    commissioning_window_end: 2013-03-31
    banding_factor: 2.0
    source: "Renewables Obligation Order 2009 (SI 2009/785), Schedule 2"
    url: "https://www.legislation.gov.uk/uksi/2009/785/made"
    basis: "Pre-2013 banding"
    retrieved_on: 2026-04-22
  - technology: "Offshore wind"
    country: "GB"
    commissioning_window_start: 2013-04-01
    commissioning_window_end: 2014-03-31
    banding_factor: 2.0
    source: "The Renewables Obligation (Amendment) Order 2013 (SI 2013/768)"
    url: "https://www.legislation.gov.uk/uksi/2013/768/made"
    basis: "2013/14 banding cell"
    retrieved_on: 2026-04-22
  # ... ~60 total entries per RESEARCH §3
```

**Divergence:**
- YAML has ~60 entries (GB + NI × pre-2013 + 2013/14 + 2014/15 + 2015/16 + 2016/17 bandings per RESEARCH §3 table). Provenance cites the amendment SI the band originated from (SI 2009/785, SI 2011/2704, SI 2013/768, SI 2015/920, SI 2016/745, SI 2017/1084 per RESEARCH §3).
- NIRO bandings (country='NI') need research at plan time — RESEARCH §3 marked `[ASSUMED]`.
- Grandfathering rule (pre-2006-07-11 accreditations receive 1.0 ROC/MWh) encoded as explicit row with `grandfathered: true`.

**Planner handoff:** `lccc.py`'s `LCCCAppConfig` is the closest structural analog; substitute the two-layer pattern verbatim with `RoBandingEntry` + `RoBandingTable`. YAML content is the research-heavy part (RESEARCH §3 table is the starting point).

---

### `src/uk_subsidy_tracker/schemas/ro.py` (schema, Pydantic row models)

**Analog:** `src/uk_subsidy_tracker/schemas/cfd.py`

**Per-row-model pattern (cfd.py lines 31-71, template for every RO grain):**
```python
class StationMonthRow(BaseModel):
    """One row in ro/station_month.parquet (order = Parquet column order, D-10)."""
    station_id: str = Field(description="Ofgem station accreditation number.",
                            json_schema_extra={"dtype": "string"})
    country: str = Field(description="'GB' or 'NI' per Ofgem register.",
                         json_schema_extra={"dtype": "string"})
    technology: str = Field(description="Ofgem technology_type.",
                            json_schema_extra={"dtype": "string"})
    commissioning_window: str = Field(description="Banding window label (pre-2013, 2013/14...).",
                                       json_schema_extra={"dtype": "string"})
    month_end: date = Field(description="Month-end anchor of the obligation-month row.",
                            json_schema_extra={"dtype": "date", "unit": "ISO-8601"})
    obligation_year: int = Field(description="Apr-Mar year containing output_period_end (D-08).",
                                  json_schema_extra={"dtype": "int64", "unit": "year"})
    generation_mwh: float = Field(description="RO-eligible MWh in this month.",
                                   json_schema_extra={"dtype": "float64", "unit": "MWh"})
    rocs_issued: float = Field(description="Ofgem-published ROCs issued (primary per D-01).",
                                json_schema_extra={"dtype": "float64", "unit": "ROCs"})
    rocs_computed: float = Field(description="generation_mwh × banding_factor_yaml (audit).",
                                  json_schema_extra={"dtype": "float64", "unit": "ROCs"})
    banding_factor_yaml: float = Field(description="RO bandings YAML lookup.",
                                        json_schema_extra={"dtype": "float64", "unit": "ROCs/MWh"})
    ro_cost_gbp: float = Field(description="Primary cost: rocs_issued × (buyout + recycle) + mutualisation.",
                                json_schema_extra={"dtype": "float64", "unit": "£"})
    ro_cost_gbp_eroc: float = Field(description="Sensitivity: rocs_issued × e-ROC clearing (per D-02).",
                                     json_schema_extra={"dtype": "float64", "unit": "£"})
    ro_cost_gbp_nocarbon: float = Field(description="Sensitivity: carbon-price=0 variant (per D-05).",
                                         json_schema_extra={"dtype": "float64", "unit": "£"})
    gas_counterfactual_gbp: float = Field(description="compute_counterfactual() × generation_mwh.",
                                           json_schema_extra={"dtype": "float64", "unit": "£"})
    premium_gbp: float = Field(description="ro_cost_gbp - gas_counterfactual_gbp.",
                                json_schema_extra={"dtype": "float64", "unit": "£"})
    mutualisation_gbp: float | None = Field(default=None,
                                             description="Mutualisation delta (null except OY 2021-22 per D-11).",
                                             json_schema_extra={"dtype": "float64", "unit": "£"})
    methodology_version: str = Field(description="D-12 provenance stamp.",
                                      json_schema_extra={"dtype": "string"})
```

**`emit_schema_json` helper — IMPORT don't copy:**
```python
from uk_subsidy_tracker.schemas.cfd import emit_schema_json  # re-use the emitter
```
(CfD's `emit_schema_json` at lines 200-215 is generic over any BaseModel subclass; no need to duplicate.)

**Divergence:**
- **5 row models** (StationMonthRow, AnnualSummaryRow, ByTechnologyRow, ByAllocationRoundRow, ForwardProjectionRow) — same count and names as CfD, different columns.
- `country` column on EVERY RO row model (CfD has none).
- Dual cost columns + sensitivity variants (`ro_cost_gbp`, `ro_cost_gbp_eroc`, `ro_cost_gbp_nocarbon`) per D-02 / D-05.
- `obligation_year` column on `station_month` only (annual_summary uses `obligation_year` or `calendar_year` — D-07 picks CY as primary axis; OY surfaces in station_month for audit-trail).
- `mutualisation_gbp` is nullable Optional — only OY 2021-22 has a value per D-11.

**Planner handoff:** `schemas/cfd.py` is the shape template; import `emit_schema_json` from CfD schemas rather than duplicating. Field-order discipline (D-10) is non-negotiable: Parquet column order must equal BaseModel field-declaration order on every grain.

---

### `src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py` (chart, 4-panel)

**Analog:** `src/uk_subsidy_tracker/plotting/subsidy/cfd_dynamics.py`

**Imports + `_prepare()` pattern (cfd_dynamics.py lines 24-66, template):**
```python
import pandas as pd
import plotly.graph_objects as go

from uk_subsidy_tracker.counterfactual import compute_counterfactual
from uk_subsidy_tracker.data import ...  # RO-equivalent: load_ofgem_ro_generation + load_roc_prices
from uk_subsidy_tracker.plotting import ChartBuilder

def _prepare() -> pd.DataFrame:
    # Option A (per chart): read derived station_month.parquet (cleaner for Phase 5)
    # Option B: re-derive from raw+counterfactual (CfD-style — D-02 allows either)
    # Output: monthly DataFrame with columns: gen, strike_or_unit_cost, counterfactual,
    #         premium_per_mwh, cumulative_premium_bn
    ...
```

**ChartBuilder + 4-panel create_subplots pattern (cfd_dynamics.py lines 73-88):**
```python
builder = ChartBuilder(
    title="The RO mechanism — ROCs × ROC-price = bill",  # RO-specific title
    height=1100,
)
fig = builder.create_subplots(
    rows=4, cols=1, shared_xaxes=True,
    subplot_titles=[
        "[1] Annual ROC-eligible generation (TWh)",                # Panel 1 volume
        "[2] ROC price (£/ROC) — buyout + recycle vs gas counterfactual",  # Panel 2 price
        "[3] Premium per MWh (£/MWh) — consumer overpayment",      # Panel 3 premium
        f"[4] Cumulative RO bill (£bn) — £{total_bn:.1f}bn to date",      # Panel 4 cumulative
    ],
    vertical_spacing=0.06,
)
```

**save() entry pattern (cfd_dynamics.py line 235):**
```python
builder.save(fig, "subsidy_ro_dynamics", export_twitter=True)
# Emits: docs/charts/html/subsidy_ro_dynamics_twitter.png + .html
```

**Divergence (RO-specific):**
- **Panel 2 overlay** — buyout+recycle price band with e-ROC sensitivity shading per D-02 (a shaded region between the two price series shows the "2-10% convention-choice weight" noted in CONTEXT specifics).
- **Mutualisation spike** on OY 2021-22 per D-11 — Panel 4 cumulative cost curve visibly steps up on that single year.
- **Calendar-year x-axis** per D-07 — no obligation-year chart in Phase 5.
- **Chart filename** `subsidy_ro_dynamics_twitter.png` per RO-MODULE-SPEC Appendix A.

**Planner handoff:** `cfd_dynamics.py` (240 lines) is the verbatim 4-panel template; copy structure and substitute data source + panel titles + chart filename. Aggressive refactor to a shared helper is DEFERRED per CONTEXT D-16.

---

### `src/uk_subsidy_tracker/plotting/subsidy/ro_by_technology.py` (chart, stacked area)

**Analog:** `src/uk_subsidy_tracker/plotting/subsidy/cfd_payments_by_category.py`

**Category dict + `_categorise` pattern (cfd_payments_by_category.py lines 30-45):**
```python
CATEGORIES = {  # RO-specific: onshore wind / offshore wind / biomass cofiring / dedicated biomass / solar / other
    "Onshore Wind": "#6baed6",
    "Offshore Wind": "#1f77b4",
    "Biomass (cofiring)": "#d62728",
    "Biomass (dedicated)": "#8c564b",
    "Solar PV": "#ff7f0e",
    "Other": "#2ca02c",
}

_TECH_MAP = {
    "Onshore wind": "Onshore Wind",
    "Offshore wind": "Offshore Wind",
    "Co-firing biomass": "Biomass (cofiring)",
    "Co-firing biomass (CHP)": "Biomass (cofiring)",
    "Dedicated biomass": "Biomass (dedicated)",
    "Solar PV — ground mounted": "Solar PV",
    "Solar PV — building mounted": "Solar PV",
    # ...
}

def _categorise(tech: str) -> str:
    return _TECH_MAP.get(tech, "Other")
```

**2-panel stacked area pattern (cfd_payments_by_category.py lines 48-148, copy structure):**
```python
# Panel 1: monthly bar stack by category
# Panel 2: cumulative stackgroup area by category
# save as "subsidy_ro_by_technology"
```

**Divergence:**
- ~6 technology buckets for RO vs CfD's 4 (includes solar PV prominently).
- Biomass split cofiring vs dedicated per D-10 (philosophical contestability call-out).
- CY x-axis per D-07; chart filename `subsidy_ro_by_technology_twitter.png` per RO-MODULE-SPEC Appendix A.

**Planner handoff:** Category dict is the main new content; 2-panel structure copies directly.

---

### `src/uk_subsidy_tracker/plotting/subsidy/ro_concentration.py` (chart, Lorenz)

**Analog:** `src/uk_subsidy_tracker/plotting/subsidy/lorenz.py`

**Aggregation + cumulative-percent pattern (lorenz.py lines 31-43):**
```python
def main() -> None:
    # RO equivalent: sum ro_cost_gbp per station_id over dataset lifetime.
    by_unit = (df.groupby(["station_name", "operator"])
                 .agg(payments=("ro_cost_gbp", "sum"))
                 .reset_index())
    by_unit = by_unit[by_unit["payments"] > 0].sort_values("payments", ascending=False)
    total = by_unit["payments"].sum()
    n = len(by_unit)
    cum_pct_payments = by_unit["payments"].cumsum() / total * 100
    cum_pct_projects = np.arange(1, n + 1) / n * 100
    total_bn = total / 1e9
```

**Equality-line + curve + threshold-marker pattern (lorenz.py lines 54-125 verbatim template):**
- Diagonal equality line (lines 54-63).
- Lorenz curve with `fill='tozeroy'` + `rgba(214,39,40,0.1)` (lines 65-80).
- 50% + 80% threshold markers with `text=[f"{n_projects} projects = {threshold}%..."]` (lines 82-100).
- Top-3 named-station annotations (lines 102-124).

**Divergence:**
- **Station universe much larger** (RESEARCH §3 estimates ~500k rows; ~several thousand distinct stations vs CfD's ~100). Top-3 callouts likely to be co-firing biomass coal plants (Drax ROCs pre-CfD, Lynemouth) and large onshore-wind operators (SSE, ScottishPower Renewables).
- Chart filename `subsidy_ro_concentration_twitter.png` per RO-MODULE-SPEC Appendix A.
- GB-only or include-NI selector per D-09 — planner decides; CONTEXT D-12 implies GB-only headline, so default is GB-only with annotation noting NI inclusion available via Parquet filter.

**Planner handoff:** `lorenz.py` (143 lines) copies structure verbatim; substitute data source + callout text.

---

### `src/uk_subsidy_tracker/plotting/subsidy/ro_forward_projection.py` (chart, drawdown to 2037)

**Analog:** `src/uk_subsidy_tracker/plotting/subsidy/remaining_obligations.py`

**Contract-end + remaining-years pattern (remaining_obligations.py lines 80-131):**
```python
# RO equivalent: read data/derived/ro/forward_projection.parquet for per-station expected_end_year
# contract_end_year OR 2037 ceiling (RO scheme closes 2037-03-31 for existing accreditations).
future = units[units["end_year"] > current_year].copy()
years = list(range(current_year, 2038))  # hard cap on 2037
future["remaining_years"] = future["end_year"] - current_year
# Flat scenario: generation levels persist at historical average.
# NESO growth scenario may or may not apply to RO — RO is legacy scheme closing
# to new accreditations, so growth multiplier less meaningful than for CfD.
```

**2×2 subplot pattern (remaining_obligations.py lines 147-212 — option to simplify):**
- 4-panel `create_subplots(rows=2, cols=2, shared_xaxes=True)`: annual + cumulative × flat-only (no growth scenario for RO since no new accreditations).
- OR simplify to 2-panel (annual + cumulative) since the growth distinction is CfD-specific.

**Divergence (RO-specific):**
- **No NESO growth scenario** — RO closed to new accreditations 2017-03-31 (SI 2017/1084 per RESEARCH §3); projection is purely drawdown. Chart can drop the 2-column layout.
- **Hard cap 2037** (RO scheme closes 2037-03-31 for 20-year accreditations from 2017).
- **Color scheme** by technology (onshore wind / offshore wind / biomass cofiring / biomass dedicated) not allocation round.
- Chart filename `subsidy_ro_forward_projection_twitter.png` per RO-MODULE-SPEC Appendix A.

**Planner handoff:** `remaining_obligations.py` (240 lines) is the template but SIMPLIFIES for RO (no growth scenario → single-column 2-panel chart). Use `data/derived/ro/forward_projection.parquet` as the data source rather than re-deriving from raw.

---

### `src/uk_subsidy_tracker/plotting/subsidy/_shared.py` (utility, NEW, NO ANALOG)

**Analog:** No existing shared-helpers file under `plotting/subsidy/`.

**Structure (opportunistic; CONTEXT D-16):**
```python
"""Opportunistic helpers where 2-3 lines duplicate between CfD and RO plotting modules.

Aggressive refactor to scheme-parametric helpers is DEFERRED to Phase 6
per CONTEXT D-16. This file hosts ONLY the helpers where identical 2-3-line
snippets appear across both cfd_*.py and ro_*.py — extraction is a
duplicate-reduction move, not an abstraction layer.

Candidates (survey existing code before extracting):
- builder.save() wrapper if chart-naming convention ever parametrises.
- RGBA fillcolor hex-to-rgba conversion (cfd_payments_by_category.py line 117,
  remaining_obligations.py line 199-201 — identical idiom).
- "current year" anchor helper reading `output_period_end.max().year`.
"""
```

**Planner handoff:** This file is optional. If no 2-3-line duplicate survives across the 4 new RO charts + CfD charts, DO NOT CREATE IT. CONTEXT D-16 is explicit: Phase 6 refactors the chart infrastructure; Phase 5 copies verbatim and only hoists trivial duplicates.

---

### `src/uk_subsidy_tracker/counterfactual.py` (MOD — extend `DEFAULT_CARBON_PRICES`)

**Analog:** self — extend the existing `DEFAULT_CARBON_PRICES` dict (lines 88-98).

**Existing block (lines 88-121):**
```python
DEFAULT_CARBON_PRICES: dict[int, float] = {
    2018: 13.0,
    2019: 22.0,
    2020: 22.0,
    2021: 48.0,
    # ... through 2026
}
"""Annual carbon prices, £/tCO2.

2018–2020: EU ETS annual averages ...
2021+: UK ETS annual averages.

Provenance:
  sources:      EU ETS 2018–2020 spot (via EEX / ICE reference);
                UK ETS 2021+ via OBR Economic & Fiscal Outlook + DESNZ/GOV.UK
  urls:
    - https://obr.uk/forecasts-in-depth/tax-by-tax-spend-by-spend/emissions-trading-scheme-uk-ets/
    ...
"""
```

**Extension per D-05:**
```python
DEFAULT_CARBON_PRICES: dict[int, float] = {
    # 2002-2004: zero (no carbon scheme pre-EU ETS).
    2002: 0.0, 2003: 0.0, 2004: 0.0,
    # 2005-2017: EU ETS annual averages (EUR→GBP at contemporary average rates,
    # ICE/EEX reference — per D-05).
    2005: ...,
    2006: ...,
    # ... 13 new year entries through 2017
    # Existing 2018-2026 entries unchanged:
    2018: 13.0,
    ...
}
```

**Divergence from analog:**
- Additive only (no existing values revised) per D-06.
- `METHODOLOGY_VERSION` stays `"0.1.0"` per D-06.
- Docstring `Provenance:` block adds lines for the EU ETS 2005-2017 coverage with ICE/EEX/BoE cross-rate URLs.

**Planner handoff:** Single dict-literal extension. No code logic change. Requires matching entries in `tests/fixtures/constants.yaml` (14 new `DEFAULT_CARBON_PRICES_{YEAR}` blocks) and `_TRACKED` set extension in `tests/test_constants_provenance.py`.

---

### `src/uk_subsidy_tracker/refresh_all.py` (MOD — one-line SCHEMES append)

**Analog:** self — the `SCHEMES` tuple at lines 33-35.

**Existing:**
```python
from uk_subsidy_tracker.schemes import cfd

SCHEMES = (
    ("cfd", cfd),
)
```

**After Phase 5:**
```python
from uk_subsidy_tracker.schemes import cfd, ro   # + ro

SCHEMES = (
    ("cfd", cfd),
    ("ro", ro),
)
```

**Divergence:** None. Literal one-line append + import extension.

**Planner handoff:** Verify `schemes/ro` is discoverable as an attribute on `schemes/__init__.py` (modules auto-register via directory presence and import from `__init__.py` body). The `SchemeModule` Protocol conformance check (`isinstance(ro, SchemeModule)`) is duck-typed so no extra work.

---

### `src/uk_subsidy_tracker/publish/manifest.py` (MOD — **MUST refactor**)

**Analog:** self + `refresh_all.publish_latest()` caller.

**Current blocker (manifest.py lines 58-100, 307-318):**
```python
GRAIN_SOURCES: dict[str, list[str]] = {
    "station_month": [...],  # hard-coded CfD sources per grain
    ...
}
GRAIN_TITLES = {...}         # CfD-prefixed titles
GRAIN_DESCRIPTIONS = {...}

# line 307:
id=f"cfd.{grain}",          # hard-codes "cfd." prefix
# line 311-314:
schema_url=f"{base}/data/latest/cfd/{grain}.schema.json",
parquet_url=f"{base}/data/latest/cfd/{grain}.parquet",
csv_url=f"{base}/data/latest/cfd/{grain}.csv",
versioned_url=f"{base}/data/{vseg}/cfd/{grain}.parquet",
```

**Refactor options (planner picks):**
1. **Scheme-parametric** — `build(..., scheme_name="cfd")` → accept a tuple of schemes; iterate over all; per-scheme GRAIN_SOURCES/TITLES/DESCRIPTIONS dicts keyed by scheme.
2. **Per-scheme manifest files** — emit `site/data/manifest-cfd.json` + `manifest-ro.json` + a thin `manifest.json` index. Cheaper but breaks ARCHITECTURE §4.3 one-manifest contract.
3. **Scheme-awareness inside one manifest** — rebuild `datasets[]` by iterating both `data/derived/cfd/*` and `data/derived/ro/*`; per-grain dict keyed by `f"{scheme}.{grain}"`.

**Parallel change in `refresh_all.publish_latest()` (refresh_all.py line 82-87):**
```python
manifest_mod.build(
    version=version,
    derived_dir=DERIVED_DIR / "cfd",   # hard-coded; must become schemes-aware
    raw_dir=DATA_DIR / "raw",
    output_path=SITE_DATA_DIR / "manifest.json",
)
```

**Planner handoff (CRITICAL):** This IS a code change despite CONTEXT claiming "no code change". Plan the refactor as a named atomic commit separate from the RO scheme-module commit. Tests to update: `tests/test_manifest.py` (existing CfD assertions; extend with RO grain assertions). Without this refactor, RO grains silently fail to publish to `site/data/manifest.json`.

---

### `tests/test_schemas.py` (MOD — test-parametrisation)

**Analog:** self (lines 98-126 = existing CfD parametrisation).

**Existing structure:**
```python
@pytest.fixture(scope="module")
def derived_dir(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("test-schemas-derived")
    cfd.rebuild_derived(output_dir=out)
    return out

_GRAIN_MODELS = {
    "station_month": StationMonthRow,
    "annual_summary": AnnualSummaryRow,
    "by_technology": ByTechnologyRow,
    "by_allocation_round": ByAllocationRoundRow,
    "forward_projection": ForwardProjectionRow,
}

@pytest.mark.parametrize("grain, model", list(_GRAIN_MODELS.items()))
def test_parquet_grain_schema(grain, model, derived_dir):
    ...
```

**RO extension pattern (mirror):**
```python
# Add parallel fixture + model dict + parametrised test for RO:
@pytest.fixture(scope="module")
def ro_derived_dir(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("test-schemas-ro-derived")
    ro.rebuild_derived(output_dir=out)
    return out

_RO_GRAIN_MODELS = {
    "station_month": RoStationMonthRow,
    "annual_summary": RoAnnualSummaryRow,
    "by_technology": RoByTechnologyRow,
    "by_allocation_round": RoByAllocationRoundRow,
    "forward_projection": RoForwardProjectionRow,
}

@pytest.mark.parametrize("grain, model", list(_RO_GRAIN_MODELS.items()))
def test_ro_parquet_grain_schema(grain, model, ro_derived_dir):
    ...
```

**Divergence:**
- Doubles the test count (5 CfD grains + 5 RO grains = 10 parametrised runs).
- Uses a separate fixture scope so CfD rebuild and RO rebuild are independent (avoids cross-scheme tmp dir contention).
- Schema row-model class names either `RoStationMonthRow` or `StationMonthRow` from a `schemas.ro` submodule — planner picks namespacing. Recommend `from uk_subsidy_tracker.schemas.ro import StationMonthRow as RoStationMonthRow` to avoid collision with CfD.

**Planner handoff:** `_GRAIN_MODELS` + `@pytest.mark.parametrize` pattern extends cleanly with a parallel RO block. Do NOT merge CfD + RO into one parametrisation — keep separate for clarity and independent module-scoped fixtures.

---

### `tests/test_aggregates.py` (MOD — test-parametrisation)

**Analog:** self (lines 64-126 = existing CfD Parquet row-conservation).

**Existing row-conservation pattern (lines 95-103):**
```python
def test_annual_vs_station_month_parquet(station_month, annual_summary):
    """TEST-03 (D-20): annual_summary.cfd_payments_gbp = sum(station_month by year)."""
    from_sm = station_month.groupby("year")["cfd_payments_gbp"].sum().sort_index()
    from_annual = annual_summary.set_index("year")["cfd_payments_gbp"].sort_index()
    pd.testing.assert_series_equal(from_sm, from_annual, check_names=False)
```

**RO extension:**
```python
@pytest.fixture(scope="module")
def ro_derived_dir(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("test-aggregates-ro-derived")
    ro.rebuild_derived(output_dir=out)
    return out

@pytest.fixture(scope="module")
def ro_station_month(ro_derived_dir) -> pd.DataFrame:
    df = pq.read_table(ro_derived_dir / "station_month.parquet").to_pandas()
    df["year"] = df["month_end"].dt.year.astype("int64")
    return df

# ... parallel fixtures for ro_annual_summary, ro_by_technology, ro_by_allocation_round

def test_ro_annual_vs_station_month_parquet(ro_station_month, ro_annual_summary):
    # Group by (year, country) — per D-09 annual_summary emits per-country rows.
    from_sm = (ro_station_month.groupby(["year", "country"])["ro_cost_gbp"].sum().sort_index())
    from_annual = (ro_annual_summary.set_index(["year", "country"])["ro_cost_gbp"].sort_index())
    pd.testing.assert_series_equal(from_sm, from_annual, check_names=False)
```

**Divergence:**
- **Row-conservation groupby keys include `country`** per D-09 (annual_summary emits per-country rows).
- Dual cost columns — row-conservation holds per column (`ro_cost_gbp` AND `ro_cost_gbp_eroc` both conserved).
- Mutualisation on OY 2021-22 must flow through the sum; test the fix doesn't break row-conservation.

**Planner handoff:** Copy the 3 row-conservation tests (annual_vs_station_month, by_tech_vs_annual, by_round_vs_annual) as parallel RO versions. Watch the country-tuple groupby on annual_summary.

---

### `tests/test_determinism.py` (MOD — test-parametrisation)

**Analog:** self (lines 24-63, existing CfD parametrisation).

**Existing:**
```python
GRAINS = ("station_month", "annual_summary", "by_technology",
          "by_allocation_round", "forward_projection")

@pytest.fixture(scope="module")
def derived_once(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("derived-run-1")
    cfd.rebuild_derived(output_dir=out)
    return out

# ... derived_twice fixture

@pytest.mark.parametrize("grain", GRAINS)
def test_parquet_content_identical(grain, derived_once, derived_twice):
    t1 = pq.read_table(derived_once / f"{grain}.parquet")
    t2 = pq.read_table(derived_twice / f"{grain}.parquet")
    assert t1.equals(t2)
```

**RO extension (parallel fixtures + parametrisation):**
```python
RO_GRAINS = ("station_month", "annual_summary", "by_technology",
             "by_allocation_round", "forward_projection")

@pytest.fixture(scope="module")
def ro_derived_once(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("ro-derived-run-1")
    ro.rebuild_derived(output_dir=out)
    return out

@pytest.fixture(scope="module")
def ro_derived_twice(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("ro-derived-run-2")
    ro.rebuild_derived(output_dir=out)
    return out

@pytest.mark.parametrize("grain", RO_GRAINS)
def test_ro_parquet_content_identical(grain, ro_derived_once, ro_derived_twice):
    t1 = pq.read_table(ro_derived_once / f"{grain}.parquet")
    t2 = pq.read_table(ro_derived_twice / f"{grain}.parquet")
    assert t1.equals(t2)
```

**Divergence:**
- Same grain names as CfD but keyed to `ro.*` scheme module.
- Writer-identity check (`test_file_metadata_created_by_is_pyarrow`) extends analogously.

**Planner handoff:** Mirror the pair-fixture + parametrize pattern; both RO fixtures call `ro.rebuild_derived(output_dir=out)`. If the determinism fails, same 3 failure-mode branches apply (clock reads, random.shuffle, groupby instability).

---

### `tests/test_benchmarks.py` (MOD — REF Constable reconciliation)

**Analog:** self (lines 115-150, external-anchor parametrisation pattern).

**Existing `_TOLERANCE_BY_SOURCE` dispatch (lines 54-60):**
```python
_TOLERANCE_BY_SOURCE: dict[str, float] = {
    "ofgem_transparency": OFGEM_TOLERANCE_PCT,
    "obr_efo": OBR_EFO_TOLERANCE_PCT,
    "desnz_energy_trends": DESNZ_TOLERANCE_PCT,
    "hoc_library": HOC_LIBRARY_TOLERANCE_PCT,
    "nao_audit": NAO_TOLERANCE_PCT,
}
```

**RO extension per D-13/D-14:**
```python
REF_TOLERANCE_PCT = 3.0
"""REF Constable 2025 primary RO anchor. Per D-14, ±3% is a HARD BLOCK:
divergence exceeding this threshold blocks phase exit — investigate root
cause (REF-scope differences vs our D-12 all-in figure; banding error;
carbon-price extension) before raising tolerance."""

_TOLERANCE_BY_SOURCE: dict[str, float] = {
    ...,
    "ref_constable": REF_TOLERANCE_PCT,
}
```

**New test pattern (analog: `test_lccc_self_reconciliation_floor` lines 82-110, MANDATORY-floor flavour):**
```python
# D-14 is binary (hard block), not D-11-fallback-skippable.
@pytest.mark.parametrize("entry", load_benchmarks().ref_constable, ids=lambda e: f"ref_constable-{e.year}")
def test_ref_constable_ro_reconciliation(entry: BenchmarkEntry, ro_annual_totals_gbp_bn):
    """RO 2011-2022 aggregate within ±3% of REF Constable 2025 Table 1 per D-13/D-14.

    D-14 hard block: if divergence exceeds 3%, investigate BEFORE phase exit.
    Do NOT silently raise tolerance.
    """
    ours = ro_annual_totals_gbp_bn.get(entry.year)
    assert ours is not None, f"No pipeline data for year {entry.year}"
    divergence_pct = abs(ours - entry.value_gbp_bn) / entry.value_gbp_bn * 100.0
    assert divergence_pct <= REF_TOLERANCE_PCT, (
        f"REF Constable reconciliation failed for {entry.year}: "
        f"pipeline = £{ours:.4f} bn, REF Constable = £{entry.value_gbp_bn:.4f} bn, "
        f"divergence = {divergence_pct:.2f}% (> {REF_TOLERANCE_PCT}%). "
        f"Per D-14 this is a HARD BLOCK — investigate root cause before phase exit. "
        f"URL: {entry.url}."
    )
```

**Fixture pattern (analog: `annual_totals_gbp_bn` lines 66-72 but RO-flavoured):**
```python
@pytest.fixture(scope="module")
def ro_annual_totals_gbp_bn() -> dict[int, float]:
    """Pipeline yearly RO totals in £bn, keyed by calendar year (D-07 primary axis).

    Sums ro_cost_gbp from derived station_month.parquet filtered to GB
    (country='GB' per D-12 headline scope)."""
    import pyarrow.parquet as pq
    from uk_subsidy_tracker.schemes import ro
    # May need a module-scoped fixture that rebuilds derived; simplest: read
    # data/derived/ro/station_month.parquet if present, else rebuild-to-tmp.
    path = ro.DERIVED_DIR / "station_month.parquet"
    df = pq.read_table(path).to_pandas()
    df_gb = df[df["country"] == "GB"]
    df_gb["year"] = df_gb["month_end"].dt.year
    totals_gbp = df_gb.groupby("year")["ro_cost_gbp"].sum()
    return (totals_gbp / 1e9).to_dict()
```

**Divergence (key from analog):**
- D-14 is a **hard block**, not D-11 skippable-fallback — do NOT use `pytest.skip` if `benchmarks.ref_constable` is empty; raise.
- Fixture reads RO data not CfD; filters to `country='GB'` per D-12 headline scope.
- Source key `ref_constable` (NOT `turver` — renamed per CONTEXT amendment 1).

**Planner handoff:** Extend `_TOLERANCE_BY_SOURCE` with one line; add one tolerance constant + docstring; add one fixture; add one parametrised test. Fixture data source requires `data/derived/ro/station_month.parquet` to exist — ensure RO rebuild runs before benchmark tests (pytest fixture ordering or CONFTEST.py session-scoped rebuild).

---

### `tests/fixtures/__init__.py` (MOD — extend Benchmarks model)

**Analog:** self (lines 35-57, existing `Benchmarks` Pydantic model).

**Existing:**
```python
class Benchmarks(BaseModel):
    lccc_self: list[BenchmarkEntry] = Field(default_factory=list)
    ofgem_transparency: list[BenchmarkEntry] = Field(default_factory=list)
    obr_efo: list[BenchmarkEntry] = Field(default_factory=list)
    desnz_energy_trends: list[BenchmarkEntry] = Field(default_factory=list)
    hoc_library: list[BenchmarkEntry] = Field(default_factory=list)
    nao_audit: list[BenchmarkEntry] = Field(default_factory=list)
```

**Extension per D-13 (add one field):**
```python
class Benchmarks(BaseModel):
    ...
    ref_constable: list[BenchmarkEntry] = Field(default_factory=list)  # D-13 RO anchor
```

**Note:** `BenchmarkEntry.year` field validator is `ge=2015, le=2050` — this must change to `ge=2002, le=2050` to admit RO early-years (2011-2014 REF data is in scope). Single-line Field constraint change.

**Planner handoff:** Two single-line changes to `tests/fixtures/__init__.py`:
1. Add `ref_constable` list field to `Benchmarks` model.
2. Relax `BenchmarkEntry.year` lower bound from 2015 to 2002.

---

### `tests/fixtures/benchmarks.yaml` (MOD — add `ref_constable` section)

**Analog:** self (existing section shape like `obr_efo:`).

**Existing structure:**
```yaml
obr_efo:
  # Secondary reporting cites OBR EFO November 2025 ...
  []

lccc_self: []  # D-11 fallback, documented per audit header
```

**Extension per D-13 (transcribed from RESEARCH §5):**
```yaml
# REF (Renewable Energy Foundation) Constable 2025-05-01 Table 1.
# Primary RO benchmark anchor per D-13. 22-year RO cost series;
# 2011-2022 entries transcribed verbatim.
# URL: https://ref.org.uk/attachments/article/390/renewables.subsidies.01.05.25.pdf
# Retrieved: 2026-04-22 (researcher in RESEARCH §5).
# Tolerance: 3.0% (REF_TOLERANCE_PCT), HARD BLOCK per D-14.
ref_constable:
  - year: 2011
    value_gbp_bn: ...    # transcribed from RESEARCH §5
    url: "https://ref.org.uk/attachments/article/390/renewables.subsidies.01.05.25.pdf"
    retrieved_on: 2026-04-22
    notes: "RO all-in GB (includes mutualisation, cofiring)"
    tolerance_pct: 3.0
  - year: 2012
    value_gbp_bn: ...
    ...
  # ... through year: 2022
```

**Planner handoff:** YAML section append. Use RESEARCH §5 verbatim transcription. Add audit-header note documenting REF publication + retrieval date per analog pattern (lines 25-35 of existing `benchmarks.yaml`).

---

### `tests/fixtures/constants.yaml` (MOD — 14 new Provenance entries)

**Analog:** self (existing `DEFAULT_CARBON_PRICES_2021` block, lines 51-59).

**Existing entry template (verbatim shape, copy 14 times):**
```yaml
DEFAULT_CARBON_PRICES_2021:
  source: "UK ETS annual average via OBR Economic & Fiscal Outlook + DESNZ/GOV.UK"
  url: "https://obr.uk/forecasts-in-depth/tax-by-tax-spend-by-spend/emissions-trading-scheme-uk-ets/"
  basis: "Calendar-year annual average UK ETS allowance price, £/tCO2"
  retrieved_on: 2026-04-22
  next_audit: 2027-01-15
  value: 48.0
  unit: "£/tCO2"
  notes: "First full UK ETS year post-Brexit carbon-scheme divergence."
```

**New entries (14 total — 2002-2017):**
```yaml
DEFAULT_CARBON_PRICES_2002:
  source: "No carbon scheme pre-EU ETS"
  url: "..."
  basis: "EU ETS started 2005-01-01; pre-2005 UK has no carbon scheme"
  retrieved_on: 2026-04-22
  value: 0.0
  unit: "£/tCO2"
  notes: "Zero by construction; RO carbon-counterfactual extension per Phase 5 D-05."

DEFAULT_CARBON_PRICES_2003:    # same shape, 0.0
DEFAULT_CARBON_PRICES_2004:    # same shape, 0.0

DEFAULT_CARBON_PRICES_2005:    # EU ETS Phase I average, EUR→GBP
  source: "EU ETS annual average via ICE / EEX reference; EUR→GBP at BoE contemporary average rate"
  url: "..."
  basis: "Calendar-year EU ETS Phase I spot average, GBP-converted at BoE annual-average EUR/GBP rate"
  retrieved_on: 2026-04-22
  next_audit: 2027-01-15
  value: ...     # researched EU ETS 2005 average in £/tCO2
  unit: "£/tCO2"
  notes: "Phase I pilot; free-allocation flood caused prices to crash to near-zero in 2007."

# ... 2006-2017 (12 more blocks)
```

**Divergence from analog:**
- 3 entries with `value: 0.0` (2002-2004) require explanation in `notes` field (zero by construction).
- EU ETS entries (2005-2017) cite ICE/EEX reference + BoE EUR/GBP conversion per D-05.
- `next_audit` can be blank for historical years (pre-2020); analog sets `2027-01-15` for recent-years.

**Planner handoff:** 14 YAML blocks in a batch. Research task (researcher preparatory work noted in RESEARCH §6 — planner may need to extract EU ETS 2005-2017 £/tCO2 averages from a source citation).

---

### `tests/test_constants_provenance.py` (MOD — extend `_TRACKED` set)

**Analog:** self (lines 40-47, existing `_TRACKED` set).

**Existing:**
```python
_TRACKED = {
    "CCGT_EFFICIENCY",
    "GAS_CO2_INTENSITY_THERMAL",
    "DEFAULT_NON_FUEL_OPEX",
    "DEFAULT_CARBON_PRICES_2021",
    "DEFAULT_CARBON_PRICES_2022",
    "DEFAULT_CARBON_PRICES_2023",
}
```

**Extension per D-05:**
```python
_TRACKED = {
    "CCGT_EFFICIENCY",
    "GAS_CO2_INTENSITY_THERMAL",
    "DEFAULT_NON_FUEL_OPEX",
    # Existing UK ETS years (2018-2026 — add the remainder for completeness):
    "DEFAULT_CARBON_PRICES_2018",
    "DEFAULT_CARBON_PRICES_2019",
    "DEFAULT_CARBON_PRICES_2020",
    "DEFAULT_CARBON_PRICES_2021",
    "DEFAULT_CARBON_PRICES_2022",
    "DEFAULT_CARBON_PRICES_2023",
    "DEFAULT_CARBON_PRICES_2024",
    "DEFAULT_CARBON_PRICES_2025",
    "DEFAULT_CARBON_PRICES_2026",
    # Phase 5 backward extension (2002-2017 per D-05):
    "DEFAULT_CARBON_PRICES_2002",
    "DEFAULT_CARBON_PRICES_2003",
    "DEFAULT_CARBON_PRICES_2004",
    "DEFAULT_CARBON_PRICES_2005",
    "DEFAULT_CARBON_PRICES_2006",
    "DEFAULT_CARBON_PRICES_2007",
    "DEFAULT_CARBON_PRICES_2008",
    "DEFAULT_CARBON_PRICES_2009",
    "DEFAULT_CARBON_PRICES_2010",
    "DEFAULT_CARBON_PRICES_2011",
    "DEFAULT_CARBON_PRICES_2012",
    "DEFAULT_CARBON_PRICES_2013",
    "DEFAULT_CARBON_PRICES_2014",
    "DEFAULT_CARBON_PRICES_2015",
    "DEFAULT_CARBON_PRICES_2016",
    "DEFAULT_CARBON_PRICES_2017",
}
```

**Divergence:** None from the analog — literal set extension with the 16 missing year entries (3 zeros + 13 EU ETS + 6 UK ETS recent years CFTech).

**Note:** Adding 2018-2026 years to `_TRACKED` here fires the drift test even without Phase 5's D-05 — but the test currently passes with 3 entries (2021/2022/2023), meaning the other year entries are already in the live dict but NOT tracked. Phase 5 closes this partial coverage — worth calling out in the plan as "side-benefit tidy" vs strict scope.

**Planner handoff:** Set extension. The matching `tests/fixtures/constants.yaml` entries must land in the same commit (else `test_every_tracked_constant_in_yaml` fires). Non-trivial because 2018-2020 UK ETS entries are NOT YET in `constants.yaml` — adding to `_TRACKED` requires adding to YAML too.

---

### `tests/data/test_ofgem_ro.py` (NEW — mocked scraper tests)

**Analog:** `tests/test_ons_gas_download.py` (error-path tests) + `tests/test_refresh_loop.py` (importlib bypass + mocked downloaders).

**Error-path test pattern (test_ons_gas_download.py lines 23-30):**
```python
from unittest.mock import MagicMock, patch
import pytest
import requests
from uk_subsidy_tracker.data import ofgem_ro  # (or roc_prices)


def test_download_ro_register_raises_on_network_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(ofgem_ro, "DATA_DIR", tmp_path)
    (tmp_path / "raw" / "ofgem").mkdir(parents=True, exist_ok=True)
    with patch("uk_subsidy_tracker.data.ofgem_ro.requests.get",
               side_effect=requests.exceptions.ConnectionError("boom")):
        with pytest.raises(requests.exceptions.RequestException):
            ofgem_ro.download_ofgem_ro_register()
```

**Timeout assertion pattern (test_ons_gas_download.py lines 33-46):**
```python
def test_download_ro_register_uses_timeout(tmp_path, monkeypatch):
    monkeypatch.setattr(ofgem_ro, "DATA_DIR", tmp_path)
    (tmp_path / "raw" / "ofgem").mkdir(parents=True, exist_ok=True)
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"xlsx-bytes-stub"]
    mock_response.raise_for_status.return_value = None
    with patch("uk_subsidy_tracker.data.ofgem_ro.requests.get",
               return_value=mock_response) as mock_get:
        ofgem_ro.download_ofgem_ro_register()
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs.get("timeout") == 60
```

**importlib bypass pattern (test_refresh_loop.py line 29 — needed if scheme-module alias shadowing occurs):**
```python
import importlib
# If schemes/ro/__init__.py aliases refresh/upstream_changed from _refresh,
# bypass the shadow to reach the submodule:
ro_refresh = importlib.import_module("uk_subsidy_tracker.schemes.ro._refresh")
```

**Mocked refresh loop pattern (test_refresh_loop.py lines 52-84 — if RO gets a refresh-loop test):**
```python
# Patch the three RO downloaders to write synthetic bytes into tmp_path:
def _patched_refresh_downloaders(raw_root: Path, new_content: dict[str, bytes]):
    stack = ExitStack()
    stack.enter_context(patch(
        "uk_subsidy_tracker.data.ofgem_ro.download_ofgem_ro_register",
        side_effect=lambda: ...write bytes...,
    ))
    stack.enter_context(patch(
        "uk_subsidy_tracker.data.ofgem_ro.download_ofgem_ro_generation",
        side_effect=lambda: ...,
    ))
    stack.enter_context(patch(
        "uk_subsidy_tracker.data.roc_prices.download_roc_prices",
        side_effect=lambda: ...,
    ))
    return stack
```

**Divergence:**
- 2 new modules to test (`ofgem_ro.py` + `roc_prices.py`) — 4 tests each (RequestException, timeout=60, happy path, atomic-write to output_path).
- If the scraper option chosen is Playwright, test mocks Playwright's `page.goto`/`page.download_as` rather than `requests.get`; structure preserved.
- Refresh-loop test optional for RO (CfD one covers the pattern); Phase 5 may add a single test verifying `ro.refresh()` is idempotent.

**Planner handoff:** Mirror `test_ons_gas_download.py` structure for 4 error-path tests per new downloader. Consider adding a single `test_ro_refresh_loop_converges_on_unchanged_upstream` mirroring `test_refresh_loop.py` — probably sufficient for Phase 5 scope.

---

### `docs/schemes/ro.md` (NEW — single-page scheme overview; NO DIRECT ANALOG)

**Structure analog:** `docs/themes/cost/index.md` (theme-level index with headline + chart gallery + methodology cross-links).
**Chart-page analog:** `docs/themes/cost/cfd-dynamics.md` (section structure: headline + chart embed + narrative).
**8-section structure defined in CONTEXT D-15** — use directly, no closer analog exists.

**Headline + grid cards pattern (docs/themes/cost/index.md lines 1-52):**
```markdown
# UK Renewables Obligation (RO)

**The scheme you've never heard of, twice the size of the one you have — £X bn in RO subsidy paid by UK consumers since 2002.**

The Renewables Obligation ran 2002-2017 (closed to new accreditations) and commits consumers to pay ~£6bn/yr for another decade to 2037. It was twice the size of the CfD scheme at its peak and is still the UK's largest legacy renewables subsidy. This page documents total cost, concentration, per-technology breakdown, and forward commitments.

<div class="grid cards" markdown>

-   [![RO dynamics preview](../charts/html/subsidy_ro_dynamics_twitter.png)](./ro/#cost-dynamics)

    __Cost dynamics — the RO mechanism in four panels__

    ROCs × ROC-price = bill. Volume, price, premium, cumulative.

-   [![RO by technology preview](../charts/html/subsidy_ro_by_technology_twitter.png)](./ro/#by-technology)

    __Payments by technology__

    Onshore wind + offshore wind + biomass cofiring + solar PV breakdown.

(etc. for concentration + forward projection)

</div>

## What is the RO?

... 2-3 paragraph explainer per D-15 Section 2.

## Cost dynamics (Chart S2)

![RO dynamics — 4-panel](../charts/html/subsidy_ro_dynamics_twitter.png)

Prose commentary per D-15 Section 3.

## By technology (Chart S3)
... (per D-15 Section 4)

## Concentration (Chart S4)
... (per D-15 Section 5)

## Forward commitment (Chart S5)
... (per D-15 Section 6)

## Methodology

- Cost = rocs_issued × (buyout_gbp_per_roc + recycle_gbp_per_roc) + mutualisation (OY 2021-22 only).
- Gas counterfactual: shared with CfD, see [methodology/gas-counterfactual.md](../methodology/gas-counterfactual.md).
- Scope decisions: headline = GB-only all-in (includes cofiring, mutualisation); NIRO (£C bn) available via `country='NI'` filter in Parquet.
- Benchmark: reconciled within ±3% to REF Constable 2025 Table 1 (peer cross-check: Turver Net Zero Watch).

## Data & code (GOV-01 four-way coverage)

- **Primary source:** [Ofgem Renewables Energy Register](https://rer.ofgem.gov.uk/).
- **Chart source:** [src/uk_subsidy_tracker/plotting/subsidy/ro_dynamics.py](...permalink...).
- **Test:** [tests/test_benchmarks.py::test_ref_constable_ro_reconciliation](...permalink...).
- **Reproduce:** `git clone ... && uv sync && uv run python -m uk_subsidy_tracker.refresh_all --scheme ro`
```

**Divergence:**
- No existing `docs/schemes/` directory — Phase 5 establishes the pattern. Phase 7 (FiT) mirrors.
- Page holds 4 chart embeds vs the theme-level index files which hold 2-4 chart card links. Closer to a narrative page than a theme index.
- GOV-01 four-way coverage MUST appear at page-bottom per D-15 Section 8 — the per-chart pages don't have this at scheme-page level.

**Planner handoff:** 8-section structure is specified in D-15 verbatim; just fill in. Adversarial-payload-first headline ("the scheme you've never heard of, twice the size of the one you have") goes in the first 3 lines per CONTEXT specifics. Plotly PNGs are gitignored but the URL paths resolve at build time; `mkdocs build --strict` validates.

---

### `mkdocs.yml` (MOD — add Schemes nav)

**Analog:** self (nav block lines 57-89).

**Existing:**
```yaml
nav:
  - Home: index.md
  - Cost: [ ... ]
  - Recipients: [ ... ]
  - Efficiency: [ ... ]
  - Cannibalisation: [ ... ]
  - Reliability: [ ... ]
  - Data: data/index.md
  - Methodology: ...
  - About: ...
```

**Per CONTEXT (planner decides placement):**
```yaml
nav:
  - Home: index.md
  - Schemes:          # NEW top-level section
      - CfD: ???      # D-15 implies per-scheme pages; CfD page also migrates here?
      - RO: schemes/ro.md
  - Cost: ...
  # ... rest unchanged
```

**Divergence:** Two planner decisions:
1. **Placement:** New "Schemes" tab vs fold RO under existing Cost theme. Recommend new top-level "Schemes" tab — CONTEXT D-15 treats scheme page as GOV-01 unit.
2. **CfD scheme page?** Phase 5 only creates `docs/schemes/ro.md`; no retrofit of CfD scheme page. The Schemes section may have only RO in Phase 5, expanded in Phase 7+ as each new scheme lands. Alternatively, create a placeholder `docs/schemes/cfd.md` redirect that links to existing theme pages.

**Planner handoff:** One-line nav addition with placeholder-for-CfD discussion. `mkdocs build --strict` is the CI gate — nav changes must produce zero warnings.

---

### `docs/index.md` + `docs/themes/cost/index.md` + `docs/themes/recipients/index.md` + `CHANGES.md` (MOD — narrative/link updates)

**Analogs:** self — existing content.

- `docs/index.md` — headline paragraph update. Existing text (lines 14-18) says "the Contracts for Difference module is shipped below. The remaining seven modules are under active development". Phase 5 changes this to "CfD and RO shipped".
- `docs/themes/cost/index.md` — existing grid-cards block (lines 11-50) gains an RO-flavoured entry. Structure template is lines 15-22 (one card):
  ```markdown
  -   [![RO dynamics preview](../../charts/html/subsidy_ro_dynamics_twitter.png)](../../schemes/ro.md#cost-dynamics)

      __[RO dynamics — the 2002-2037 RO bill](../../schemes/ro.md#cost-dynamics)__

      ---

      The legacy scheme twice the CfD's size. Detailed page at Schemes → RO.
  ```
- `docs/themes/recipients/index.md` — parallel addition for Lorenz-style RO concentration chart.
- `CHANGES.md` — `[Unreleased]` entries: scraper + scheme module + Parquet grains + charts + docs page; `## Methodology versions` entry for DEFAULT_CARBON_PRICES 2002-2017 extension.

**Planner handoff:** Straightforward one-file-per-change updates. `CHANGES.md` patches go under both `[Unreleased]` (feature ledger) and `## Methodology versions` (audit-significant carbon-price extension).

---

### `data/raw/ofgem/{ro-register.xlsx, ro-generation.csv, roc-prices.csv}` + `.meta.json` (NEW — seed files)

**Analog:** `data/raw/lccc/*` + `data/raw/elexon/*` + `data/raw/ons/*` (existing structure).

**Directory pattern (already exists for other publishers):**
```
data/raw/
├── lccc/actual-cfd-generation.csv + .meta.json
├── lccc/cfd-contract-portfolio-status.csv + .meta.json
├── elexon/agws.csv + .meta.json
├── elexon/system-prices.csv + .meta.json
└── ons/gas-sap.xlsx + .meta.json
```

**RO addition:**
```
data/raw/
└── ofgem/
    ├── ro-register.xlsx + .meta.json
    ├── ro-generation.csv + .meta.json
    └── roc-prices.csv + .meta.json
```

**Sidecar creation:** use `scripts/backfill_sidecars.py` pattern from Phase 4. Extend `URL_MAP` in the backfill script to include the three RO relative paths (URLs must match `schemes/ro/_refresh.py::_URL_MAP` exactly — cross-file byte-parity rule).

**Divergence from analog:** None in structure. Content is the data download (one-time seed if chosen scraper mechanism is manual per RER auth constraints).

**Planner handoff:** Atomic commit pattern per Phase 4 D-04 — one commit for raw files + sidecars, separate from the scheme-module commit. `scripts/backfill_sidecars.py` gets extended with 3 new URL_MAP entries.

---

## Shared Patterns

### Deterministic Parquet Writer (CROSS-CUTTING, D-21/D-22)

**Source:** `src/uk_subsidy_tracker/schemes/cfd/cost_model.py::_write_parquet` (lines 47-68)

**Apply to:** `schemes/ro/cost_model.py`, `schemes/ro/aggregation.py`, `schemes/ro/forward_projection.py` — via IMPORT not copy.

```python
from uk_subsidy_tracker.schemes.cfd.cost_model import _write_parquet
# Pinned options: snappy compression, Parquet 2.6, dictionary encoding,
# page statistics, 1 MiB data-page size. Shared across schemes.
```

**Why:** The writer is intentionally scheme-agnostic; it's a "happens to live under cfd/" artefact, not a CfD-specific implementation. Duplicating re-implements a bug surface (different compression levels → determinism-test failures).

---

### Shared Atomic Sidecar (CROSS-CUTTING, Phase 4 Plan 07)

**Source:** `src/uk_subsidy_tracker/data/sidecar.py::write_sidecar` (lines 35-75)

**Apply to:** `schemes/ro/_refresh.py` — 3 calls after each successful download.

```python
from uk_subsidy_tracker.data.sidecar import write_sidecar

for rel, upstream_url in _URL_MAP.items():
    raw_path = DATA_DIR / rel
    if not raw_path.exists():
        raise FileNotFoundError(...)  # D-17 fail-loud
    write_sidecar(raw_path=raw_path, upstream_url=upstream_url)
```

**Why:** `write_sidecar()` owns atomic `.tmp + os.replace` semantics + sha256 + `json.dumps(..., sort_keys=True, indent=2) + "\n"`. Byte-parity with `scripts/backfill_sidecars.py` enforced via shared helper.

---

### Methodology-Version Column Propagation (CROSS-CUTTING, D-12)

**Source:** `counterfactual.METHODOLOGY_VERSION` flowing via `compute_counterfactual()` into every Parquet row's `methodology_version` column.

**Apply to:** Every RO grain-builder (`build_station_month`, `build_annual_summary`, `build_by_technology`, `build_by_allocation_round`, `build_forward_projection`).

```python
df["methodology_version"] = METHODOLOGY_VERSION  # before sort + validate + write
```

**Why:** Completes the end-to-end D-12 provenance chain from constant → DataFrame column → Parquet row → `manifest.json::methodology_version` (assuming planner closes the manifest.py refactor).

---

### Fail-Loud Error Handling (CROSS-CUTTING, D-17)

**Source:** `src/uk_subsidy_tracker/data/ons_gas.py::download_dataset` (lines 36-47)

**Apply to:** Every new downloader in `data/ofgem_ro.py` + `data/roc_prices.py`.

```python
def download_ofgem_ro_register() -> Path:
    output_path = DATA_DIR / "raw/ofgem/ro-register.xlsx"  # BOUND BEFORE try (gap #2 fix)
    try:
        response = requests.get(URL, headers=HEADERS, stream=True, timeout=60)  # timeout=60 mandatory
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading ...: {e}")
        raise  # fail-loud per D-17 — no silent swallow
```

**Why:** `ons_gas.py` is the closest template (has all three: `timeout=60`, `output_path` before try, bare `raise`). `lccc.py` misses two of these (legacy; not yet ported forward). New code uses `ons_gas.py` as the authority.

---

### Loader-Owned Pandera Validation (CROSS-CUTTING, Phase 2)

**Source:** `src/uk_subsidy_tracker/data/lccc.py::load_lccc_dataset` (lines 105-114)

**Apply to:** `data/ofgem_ro.py::load_ofgem_ro_register`, `data/ofgem_ro.py::load_ofgem_ro_generation`, `data/roc_prices.py::load_roc_prices`, `schemes/ro/cost_model.py::build_station_month`.

```python
def load_ofgem_ro_register() -> pd.DataFrame:
    df = pd.read_excel(DATA_DIR / "raw/ofgem/ro-register.xlsx")
    df = ro_register_schema.validate(df)  # INSIDE the loader body
    return df
```

**Why:** Phase 2 discipline: validation is the loader's job, not the test's. The loader is the enforced boundary between untrusted CSV/XLSX and trusted DataFrame.

---

### int64 Year Cast in Rollup Builders (CROSS-CUTTING, Phase 4 Rule-1 auto-fix)

**Source:** `src/uk_subsidy_tracker/schemes/cfd/aggregation.py` (lines 68, 125, 158)

**Apply to:** Every RO rollup builder that groups by year.

```python
sm["year"] = sm["month_end"].dt.year.astype("int64")
# Non-negotiable: pandas dt.year returns int32; Pydantic row models declare int64.
# Skipping this causes a pandera column-dtype mismatch at validate() time.
```

**Why:** Phase 4 Plan 03 Rule-1 auto-fix decision. The column-dtype mismatch surfaces as a pandera error, not a logic error — silent if the cast is forgotten AND the pandera schema has `coerce=True` (would silently downcast on write). Explicit cast keeps Pydantic + pandera + Parquet all int64.

---

### Provenance Docstring Discipline (CROSS-CUTTING, Phase 3 commit `efdfbbc`)

**Source:** Every regulator-sourced constant in `counterfactual.py` carries a `Provenance:` block (CCGT_EFFICIENCY lines 12-25, GAS_CO2_INTENSITY_THERMAL lines 27-36, DEFAULT_CARBON_PRICES lines 99-121).

**Apply to:** Every new entry in `ro_bandings.yaml`; every new `DEFAULT_CARBON_PRICES` year entry's docstring; every row in `benchmarks.yaml::ref_constable`.

```yaml
source: "..."                 # Human-readable regulator name + document
url: "..."                    # Stable upstream URL
basis: "..."                  # Methodological basis
retrieved_on: 2026-04-22      # ISO date
next_audit: 2027-01-15        # Optional; recent-years only
```

**Why:** Grep-discoverable audit trail (`grep -rn "^Provenance:" src/ tests/`). User-memory pattern — every regulator constant must carry provenance or the constant is adversarial-attackable.

---

### importlib Bypass for Submodule Shadow (CROSS-CUTTING, Phase 4 Plan 07)

**Source:** `tests/test_refresh_loop.py` (lines 23-29)

**Apply to:** `tests/data/test_ofgem_ro.py` if RO tests need to import `schemes.ro._refresh` directly (submodule is shadowed by `schemes/ro/__init__.py` aliasing `refresh as _refresh` at package level).

```python
import importlib
ro_refresh = importlib.import_module("uk_subsidy_tracker.schemes.ro._refresh")
# Now ro_refresh._URL_MAP, ro_refresh.upstream_changed, etc. are accessible.
```

**Why:** The alias `from .schemes.ro._refresh import refresh as _refresh` in `schemes/ro/__init__.py` (mirroring `schemes/cfd/__init__.py` line 27) shadows the submodule attribute at the package level. importlib reaches the submodule directly.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `src/uk_subsidy_tracker/plotting/subsidy/_shared.py` | utility | shared helpers | No shared-helpers file yet in `plotting/subsidy/`; opportunistic creation per CONTEXT D-16 ("hoist only 2-3 line literal duplicates") — may turn out NO duplicates warrant extraction, file stays un-created. |
| `docs/schemes/ro.md` | docs-scheme-page | static markdown | No `docs/schemes/` directory exists; closest analog is theme-level `docs/themes/cost/index.md` + per-chart `docs/themes/cost/cfd-dynamics.md` hybrid. Phase 5 establishes the scheme-page pattern; Phase 7 (FiT) mirrors. |

## Metadata

**Analog search scope:**
- `src/uk_subsidy_tracker/schemes/cfd/*.py` (scheme-module template — 5 files)
- `src/uk_subsidy_tracker/data/*.py` (scraper + loader pattern — 5 files)
- `src/uk_subsidy_tracker/schemas/cfd.py` (Pydantic row models)
- `src/uk_subsidy_tracker/plotting/subsidy/{cfd_dynamics,cfd_payments_by_category,lorenz,remaining_obligations}.py` (4 chart templates)
- `src/uk_subsidy_tracker/{counterfactual,refresh_all}.py` + `publish/manifest.py`
- `tests/{test_schemas,test_aggregates,test_determinism,test_benchmarks,test_constants_provenance,test_ons_gas_download,test_refresh_loop}.py`
- `tests/fixtures/{__init__,benchmarks,constants}.{py,yaml}`
- `docs/{index,themes/cost/index,themes/recipients/index,themes/cost/cfd-dynamics}.md`
- `mkdocs.yml`

**Files scanned:** ~30 source files + ~15 test/fixture/doc files
**Pattern extraction date:** 2026-04-22
**Package-root verified:** `src/uk_subsidy_tracker/` (repo dir still `cfd-payment/`; import path is `uk_subsidy_tracker.*`)
