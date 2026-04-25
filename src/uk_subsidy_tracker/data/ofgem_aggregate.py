"""Ofgem aggregate-grain loaders (Phase 05.2).

Raw artefacts consumed:
  - data/raw/ofgem/rocs_report_2006_to_2018_20250410081520.xlsx  (12-year XLSX primary)
  - data/raw/ofgem/ro-annual-aggregate.csv                        (SY17–SY23 transcription)
  - data/raw/ofgem/roc-prices.csv                                 (buyout + recycle + eroc + mutualisation)
  - data/raw/ofgem/ro-generation.csv                              (regenerated from XLSX, D-01)

Provenance: Ofgem 12-year XLSX is the authoritative pre-2019 source (GB aggregate
by technology x month x country). Post-2018 aggregates are transcribed from
Ofgem annual-report PDFs — see each transcribed CSV's header Provenance block
and `.meta.json::sources[]` array for per-row source URL + sha256 + retrieved_on
(D-03 multi-source sidecar discipline).

Error-path discipline (Phase 4 D-17 + Plan 07):
  - `output_path` bound BEFORE `try:` block
  - `timeout=60` on `requests.get()`
  - bare `raise` in `except requests.exceptions.RequestException`
  - successful download returns `output_path`

Loader-owned pandera validation per Phase 2 D-04: each `load_*_csv()` validates
its DataFrame against a module-level schema before returning.

Wave scoping (Phase 05.2 Plan 01):
  - This module lands the loader skeleton + download function + pandera schemas.
  - `parse_xlsx_to_monthly()` is intentionally stubbed (raises NotImplementedError) —
    Wave 3 ``schemes/ro/aggregate_model.py`` provides the parsing strategy once
    Wave 2 commits the XLSX file. The signature + docstring contract is fixed now
    so downstream consumers can plan against it.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pandera.pandas as pa
import requests
import yaml
from pydantic import BaseModel

from uk_subsidy_tracker import DATA_DIR
from uk_subsidy_tracker.data.utils import HEADERS


# ---------------------------------------------------------------------------
# Module constants — single source of truth for the 12-year XLSX upstream.
# ---------------------------------------------------------------------------
XLSX_URL = (
    "https://www.ofgem.gov.uk/sites/default/files/2025-05/"
    "rocs_report_2006_to_2018_20250410081520.xlsx"
)
XLSX_FILENAME = "rocs_report_2006_to_2018_20250410081520.xlsx"


# ---------------------------------------------------------------------------
# Pandera schemas — loader-owned validation per Phase 2 D-04.
# ``strict=False`` permits additional un-validated columns (CSVs may carry
# transcribed-source-PDF URLs etc. without breaking schema evolution).
# ---------------------------------------------------------------------------
ofgem_annual_aggregate_schema = pa.DataFrameSchema(
    {
        "scheme_year": pa.Column(str, checks=pa.Check.str_matches(r"^SY\d{2}$")),
        "year": pa.Column("int64", coerce=True),
        "country": pa.Column(str, checks=pa.Check.isin(["GB", "NI"])),
        "technology": pa.Column(str, coerce=True),
        "generation_gwh": pa.Column(float, nullable=True, coerce=True),
        "rocs_issued": pa.Column(float, nullable=True, coerce=True),
        "ro_cost_gbp_nominal": pa.Column(float, nullable=True, coerce=True),
        "source_pdf_url": pa.Column(str, nullable=True, coerce=True),
    },
    strict=False,
    coerce=True,
)

ofgem_roc_prices_schema = pa.DataFrameSchema(
    {
        "obligation_year": pa.Column(
            str,
            checks=pa.Check.str_matches(r"^\d{4}-\d{2}$|^SY\d{2}$"),
        ),
        "buyout_gbp_per_roc": pa.Column(float, coerce=True),
        "recycle_gbp_per_roc": pa.Column(float, nullable=True, coerce=True),
        "eroc_gbp_per_roc": pa.Column(float, nullable=True, coerce=True),
        "mutualisation_gbp_total": pa.Column(float, nullable=True, coerce=True),
    },
    strict=False,
    coerce=True,
)

ofgem_monthly_schema = pa.DataFrameSchema(
    {
        "year": pa.Column("int64", coerce=True),
        "month": pa.Column("int64", coerce=True, checks=pa.Check.in_range(1, 12)),
        "country": pa.Column(str, checks=pa.Check.isin(["GB", "NI"])),
        "technology": pa.Column(str, coerce=True),
        "generation_mwh": pa.Column(float, nullable=True, coerce=True),
        "rocs_issued": pa.Column(float, nullable=True, coerce=True),
    },
    strict=False,
    coerce=True,
)


# ---------------------------------------------------------------------------
# 12-year XLSX download — D-17 fail-loud (output_path bound BEFORE try).
# ---------------------------------------------------------------------------
def download_twelve_year_xlsx() -> Path:
    """Download the Ofgem 12-year RO aggregate XLSX (2006-2018) into ``data/raw/ofgem/``.

    Returns the path to the written file on success.

    Raises:
        requests.exceptions.RequestException: on any network failure
            (D-17 fail-loud — daily refresh workflow needs to see the failure
            propagate, not a silently un-downloaded path).
    """
    output_path = DATA_DIR / "raw" / "ofgem" / XLSX_FILENAME  # BOUND BEFORE try (D-17 gap #2 fix)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        response = requests.get(
            XLSX_URL, headers=HEADERS, stream=True, timeout=60
        )
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading 12-year XLSX: {e}")
        raise  # fail loud per D-17


# ---------------------------------------------------------------------------
# XLSX → monthly DataFrame — STUBBED until Wave 3 lands the parsing strategy.
# ---------------------------------------------------------------------------
def parse_xlsx_to_monthly() -> pd.DataFrame:
    """Parse the 12-year Ofgem XLSX into a deterministic monthly aggregate.

    Return-shape contract: a DataFrame conforming to ``ofgem_monthly_schema``
    (columns: ``year``, ``month``, ``country``, ``technology``,
    ``generation_mwh``, ``rocs_issued``).

    Determinism discipline (Phase 4 D-21): same XLSX bytes → byte-identical
    output DataFrame across runs. No clock, no randomness, every ``groupby``
    explicit on sort order.

    Implementation deferred to Wave 3 (``schemes/ro/aggregate_model.py``) once
    Wave 2 commits the real XLSX. Calling now raises ``NotImplementedError``
    so accidental refresh-loop invocation fails loud rather than silently
    emitting an empty Parquet.
    """
    raise NotImplementedError(
        "Wave 3 aggregate_model.py provides the parsing strategy — "
        "planner discretion per CONTEXT.md (Claude's Discretion: "
        "Openpyxl XLSX parsing strategy)."
    )


# ---------------------------------------------------------------------------
# Transcribed-CSV loaders — pandera-validated, comment-aware.
# ---------------------------------------------------------------------------
def load_annual_aggregate_csv() -> pd.DataFrame:
    """Load + validate the SY17–SY23 transcribed annual-aggregate CSV.

    The CSV file begins with a ``# Provenance:`` block (D-03) listing each
    source PDF URL + sha256 + retrieved_on. ``pandas.read_csv(comment="#")``
    skips those header lines so only data rows reach the pandera validator.
    """
    path = DATA_DIR / "raw" / "ofgem" / "ro-annual-aggregate.csv"
    df = pd.read_csv(path, comment="#")
    df = ofgem_annual_aggregate_schema.validate(df)
    return df


def load_roc_prices_csv() -> pd.DataFrame:
    """Load + validate the transcribed ROC-prices CSV (multi-source provenance).

    The CSV file begins with a ``# Provenance:`` block (D-03) listing each
    source PDF URL + sha256 + retrieved_on. ``pandas.read_csv(comment="#")``
    skips those header lines so only data rows reach the pandera validator.
    """
    path = DATA_DIR / "raw" / "ofgem" / "roc-prices.csv"
    df = pd.read_csv(path, comment="#")
    df = ofgem_roc_prices_schema.validate(df)
    return df


__all__ = [
    "XLSX_URL",
    "XLSX_FILENAME",
    "ofgem_annual_aggregate_schema",
    "ofgem_roc_prices_schema",
    "ofgem_monthly_schema",
    "download_twelve_year_xlsx",
    "parse_xlsx_to_monthly",
    "load_annual_aggregate_csv",
    "load_roc_prices_csv",
    "OfgemAnnualReportConfig",
    "OfgemAnnualReportsConfig",
    "load_ofgem_annual_reports_config",
    "download_annual_xlsx",
    "parse_annual_xlsx_to_aggregate_rows",
    "emit_annual_aggregate_csv",
]


# ----- Phase 05.2 Plan 02 (revised): SY18-SY23 annual-report XLSX path -----


class OfgemAnnualReportConfig(BaseModel):
    scheme_year: str
    period: str
    url: str
    local_filename: str
    expected_min_size_bytes: int
    notes: str


class OfgemAnnualReportsConfig(BaseModel):
    reports: list[OfgemAnnualReportConfig]

    def by_scheme_year(self, scheme_year: str) -> OfgemAnnualReportConfig:
        for r in self.reports:
            if r.scheme_year == scheme_year:
                return r
        raise KeyError(scheme_year)


_ANNUAL_REPORTS_YAML = Path(__file__).parent / "ofgem_annual_reports.yaml"


def load_ofgem_annual_reports_config(path: Path | None = None) -> OfgemAnnualReportsConfig:
    """Load the SY18-SY23 XLSX-companion manifest.

    Provenance: data/ofgem_annual_reports.yaml carries the verbatim URL inventory
    from CONTEXT.md (SY17-SY23 discovery, 2026-04-24, commit b934492).
    """
    target = path if path is not None else _ANNUAL_REPORTS_YAML
    with open(target, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return OfgemAnnualReportsConfig(**raw)


def download_annual_xlsx(scheme_year: str) -> Path:
    """Download a single SY18-SY23 annual-report XLSX dataset companion.

    Resolves URL via the YAML manifest. D-17 fail-loud discipline:
      - output_path bound BEFORE try (gap #2 fix from Phase 4 Plan 07)
      - timeout=60 on requests.get
      - bare raise in except RequestException

    Raises KeyError if scheme_year not in manifest (e.g. 'SY17' deferred).
    """
    cfg = load_ofgem_annual_reports_config()
    entry = cfg.by_scheme_year(scheme_year)  # raises KeyError on SY17
    output_path = DATA_DIR / "raw" / "ofgem" / entry.local_filename  # BOUND BEFORE try (D-17 gap #2)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        response = requests.get(entry.url, headers=HEADERS, stream=True, timeout=60)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading {scheme_year} XLSX: {e}")
        raise  # fail loud per D-17


def parse_annual_xlsx_to_aggregate_rows(scheme_year: str) -> pd.DataFrame:
    """Parse one SY18-SY23 XLSX into ofgem_annual_aggregate_schema rows.

    Returns DataFrame with columns: scheme_year, year, country, technology,
    generation_gwh, rocs_issued, ro_cost_gbp_nominal, source_pdf_url
    (under XLSX path: source_pdf_url carries the XLSX URL).

    Pure function: same XLSX bytes -> same DataFrame (D-21). Real implementation
    in Task 5.
    """
    raise NotImplementedError("Plan 02 Task 5 fills this body")


def emit_annual_aggregate_csv(output_path: Path | None = None) -> Path:
    """Concatenate SY18-SY23 parsed rows into ro-annual-aggregate.csv.

    Writes a Provenance: comment header + the unified data rows + emits the
    sibling .meta.json sidecar with sources[] enumerating the 6 XLSX upstreams.
    Real implementation in Task 5.
    """
    raise NotImplementedError("Plan 02 Task 5 fills this body")
