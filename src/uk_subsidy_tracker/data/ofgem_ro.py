# dormant: true
"""Ofgem RO register + generation downloaders and loaders (Plan 05-01).

Raw artefacts (see `data/raw/ofgem/README.md`):
  - data/raw/ofgem/ro-register.xlsx   — station accreditation register
  - data/raw/ofgem/ro-generation.csv  — monthly ROC issuance

Provenance: Ofgem Renewables Energy Register (RER) https://rer.ofgem.gov.uk/
  (migrated 2025-05-14 from `renewablesandchp.ofgem.gov.uk`). Direct-URL
  bulk-download availability on RER is unstable / SharePoint-OIDC walled;
  see `.planning/phases/05-ro-module/05-01-TASK-1-INVESTIGATION.md` for
  the assessment that led to the current Option-D fallback (header-only
  stub raw files + scrapers that fail-loud on invocation).

Error-path discipline (Phase 4 D-17 + Plan 07):
  - `output_path` bound BEFORE `try:` block
  - `timeout=60` on `requests.get()`
  - bare `raise` in `except requests.exceptions.RequestException`
  - Under Option D (empty `_REGISTER_URL` / `_GENERATION_URL`), each
    `download_*` raises `RuntimeError("manual refresh — see INVESTIGATION.md")`
    so accidental cron invocations surface immediately rather than silently
    overwriting the seeded stub.

Loader-owned pandera validation (Phase 2 pattern): `load_*` functions
validate the DataFrame against the module-level pandera schema before
returning. `strict=False` permits the empty-DataFrame case the Option-D
stubs produce.

Dormancy:
    This module is dormant per Phase 05.2 (RO Data Reconstruction — Aggregate
    Grain). Station-level code paths are preserved in-tree but not exercised
    by the aggregate pipeline (schemes.ro.DORMANT_STATION_LEVEL = True).
    Re-activated on backlog 999.1 (Credentialed RER Access Automation) by
    flipping DORMANT_STATION_LEVEL to False and removing the per-test
    @pytest.mark.dormant marks.

    Design note: .planning/notes/ro-data-strategy-option-a1.md
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pandera.pandas as pa
import requests

from uk_subsidy_tracker import DATA_DIR
from uk_subsidy_tracker.data.utils import HEADERS

# ---------------------------------------------------------------------------
# URL constants — populated by Plan 05-01 Task 1 investigation outcome.
#
# Under Option D (current): both URL constants are empty strings; the
# `download_*` functions detect the empty string and raise RuntimeError
# pointing the user at the investigation report.
#
# When the user approves a real-scraper path in Plan 05-13 review, these
# constants get populated with real Ofgem RER URLs (or wrappers around
# Playwright session-cookie flows) and the RuntimeError guard short-circuits.
# ---------------------------------------------------------------------------
_REGISTER_URL: str = ""
_GENERATION_URL: str = ""

_OPTION_D_MSG = (
    "manual refresh — see "
    ".planning/phases/05-ro-module/05-01-TASK-1-INVESTIGATION.md "
    "(Option-D fallback: real Ofgem RER export must be placed manually "
    "at this path; resolved in Plan 05-13 Task 5 post-execution review)"
)

# ---------------------------------------------------------------------------
# Pandera schemas — loader-owned validation per Phase 2 D-04.
# `strict=False` + `coerce=True` permits the Option-D empty-DataFrame stubs
# to pass without trip-wiring before real data lands.
# ---------------------------------------------------------------------------
ro_register_schema = pa.DataFrameSchema(
    {
        "station_id": pa.Column(str),
        "station_name": pa.Column(str, nullable=True),
        "operator": pa.Column(str, nullable=True),
        "technology_type": pa.Column(str),
        "country": pa.Column(
            str,
            checks=pa.Check.isin(
                ["GB", "NI", "England", "Wales", "Scotland", "Northern Ireland"]
            ),
        ),
        "commissioning_date": pa.Column("datetime64[ns]", nullable=True, coerce=True),
        "accreditation_date": pa.Column("datetime64[ns]", nullable=True, coerce=True),
        "DNC_MW": pa.Column(float, nullable=True, coerce=True),
        "expected_end_date": pa.Column("datetime64[ns]", nullable=True, coerce=True),
    },
    strict=False,
    coerce=True,
)

ro_generation_schema = pa.DataFrameSchema(
    {
        "station_id": pa.Column(str),
        "output_period_end": pa.Column("datetime64[ns]", coerce=True),
        "generation_mwh": pa.Column(float, coerce=True),
        "rocs_issued": pa.Column(float, coerce=True),
    },
    strict=False,
    coerce=True,
)


# ---------------------------------------------------------------------------
# Downloaders — D-17 fail-loud discipline (mirror src/uk_subsidy_tracker/data/ons_gas.py).
# ---------------------------------------------------------------------------
def download_ofgem_ro_register() -> Path:
    """Download the Ofgem RO station register XLSX.

    Under Option D (empty `_REGISTER_URL`) raises `RuntimeError` pointing
    the caller at the investigation report. When the user approves a
    real-scraper path, populate `_REGISTER_URL` and the live HTTPS path
    activates.

    Raises:
        RuntimeError: if `_REGISTER_URL` is empty (Option-D guard).
        requests.exceptions.RequestException: on any network failure
            (D-17 fail-loud).
    """
    output_path = DATA_DIR / "raw" / "ofgem" / "ro-register.xlsx"  # bound BEFORE try
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not _REGISTER_URL:
        raise RuntimeError(_OPTION_D_MSG)
    try:
        response = requests.get(
            _REGISTER_URL, headers=HEADERS, stream=True, timeout=60
        )
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading ro-register.xlsx: {e}")
        raise  # fail-loud per D-17


def download_ofgem_ro_generation() -> Path:
    """Download the Ofgem monthly ROC-issuance CSV.

    Under Option D (empty `_GENERATION_URL`) raises `RuntimeError`. When
    the user approves a real-scraper path, populate `_GENERATION_URL` and
    the live HTTPS path activates.

    Raises:
        RuntimeError: if `_GENERATION_URL` is empty (Option-D guard).
        requests.exceptions.RequestException: on any network failure
            (D-17 fail-loud).
    """
    output_path = DATA_DIR / "raw" / "ofgem" / "ro-generation.csv"  # bound BEFORE try
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not _GENERATION_URL:
        raise RuntimeError(_OPTION_D_MSG)
    try:
        response = requests.get(
            _GENERATION_URL, headers=HEADERS, stream=True, timeout=60
        )
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading ro-generation.csv: {e}")
        raise  # fail-loud per D-17


# ---------------------------------------------------------------------------
# Loaders — pandera validation inside the loader body (Phase 2 D-04).
# ---------------------------------------------------------------------------
def load_ofgem_ro_register() -> pd.DataFrame:
    """Load + validate the Ofgem RO station register.

    Under Option D the file is a header-only stub (0 data rows); pandera
    `strict=False` tolerates this. Once real data lands, the same schema
    catches column-name / dtype drift at read time.
    """
    path = DATA_DIR / "raw" / "ofgem" / "ro-register.xlsx"
    df = pd.read_excel(path)
    df = ro_register_schema.validate(df)
    return df


def load_ofgem_ro_generation() -> pd.DataFrame:
    """Load + validate the Ofgem monthly ROC-issuance dataset."""
    path = DATA_DIR / "raw" / "ofgem" / "ro-generation.csv"
    df = pd.read_csv(path, parse_dates=["output_period_end"])
    df = ro_generation_schema.validate(df)
    return df


__all__ = [
    "download_ofgem_ro_register",
    "download_ofgem_ro_generation",
    "load_ofgem_ro_register",
    "load_ofgem_ro_generation",
    "ro_register_schema",
    "ro_generation_schema",
]
