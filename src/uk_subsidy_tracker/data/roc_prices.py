"""Ofgem ROC-prices downloader and loader (Plan 05-01).

Raw artefact: `data/raw/ofgem/roc-prices.csv` carrying yearly buyout +
recycle + e-ROC clearing + mutualisation prices per obligation year
(`YYYY-YY` string keying).

Provenance: Ofgem buy-out + mutualisation transparency PDFs
(https://www.ofgem.gov.uk/publications/renewables-obligation-buy-out-price-and-mutualisation-ceilings)
plus the e-ROC quarterly auction results (https://www.e-roc.co.uk/).
Public PDFs, no authentication required, but the URL templates surfaced
by RESEARCH §2 are stale (404) as of 2026-04-23 and pdfplumber is not in
`pyproject.toml`. See
`.planning/phases/05-ro-module/05-01-TASK-1-INVESTIGATION.md` for the
Option-D fallback rationale (header-only stub + RuntimeError-on-invocation).

Error-path discipline (Phase 4 D-17 + Plan 07):
  - `output_path` bound BEFORE `try:` block
  - `timeout=60` on `requests.get()`
  - bare `raise` in `except requests.exceptions.RequestException`
  - Under Option D (empty `_PRICES_URL`), `download_roc_prices()` raises
    `RuntimeError("manual refresh — see INVESTIGATION.md")` so the
    refresh cron never silently overwrites the transcribed file with a
    stale download.

Loader-owned pandera validation per Phase 2 D-04: `obligation_year`
matches `^\\d{4}-\\d{2}$`; mutualisation price is nullable (only
SY 2021-22 triggered mutualisation per CONTEXT D-11).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pandera.pandas as pa
import requests

from uk_subsidy_tracker import DATA_DIR
from uk_subsidy_tracker.data.utils import HEADERS

# ---------------------------------------------------------------------------
# URL constant — populated by Plan 05-01 Task 1 investigation.
# Under Option D (current): empty string. Once user approves a real source
# (e.g. a stable Ofgem PDF URL + pdfplumber dep, or manual transcription
# from public PDFs), this gets populated.
# ---------------------------------------------------------------------------
_PRICES_URL: str = ""

_OPTION_D_MSG = (
    "manual refresh — see "
    ".planning/phases/05-ro-module/05-01-TASK-1-INVESTIGATION.md "
    "(Option-D fallback: roc-prices.csv must be transcribed from Ofgem "
    "public PDFs or populated by a future plan; resolved in Plan 05-13 "
    "Task 5 post-execution review)"
)

# Pandera schema — loader-owned validation per Phase 2 D-04.
# `strict=False` permits the Option-D header-only stub (0 data rows).
roc_prices_schema = pa.DataFrameSchema(
    {
        "obligation_year": pa.Column(
            str,
            checks=pa.Check.str_matches(r"^\d{4}-\d{2}$"),
        ),
        "buyout_gbp_per_roc": pa.Column(float, coerce=True),
        "recycle_gbp_per_roc": pa.Column(float, coerce=True),
        "eroc_clearing_gbp_per_roc": pa.Column(float, nullable=True, coerce=True),
        "mutualisation_gbp_per_roc": pa.Column(float, nullable=True, coerce=True),
    },
    strict=False,
    coerce=True,
)


def download_roc_prices() -> Path:
    """Download the combined buyout + recycle + e-ROC + mutualisation CSV.

    Under Option D (empty `_PRICES_URL`) raises `RuntimeError`. Critically
    we want this guard rather than a no-op return: the committed CSV is
    the ground truth (transcribed from public PDFs in a later plan), so a
    silent download-and-overwrite path could destroy human-curated data.

    Raises:
        RuntimeError: if `_PRICES_URL` is empty (Option-D guard).
        requests.exceptions.RequestException: on any network failure
            (D-17 fail-loud).
    """
    output_path = DATA_DIR / "raw" / "ofgem" / "roc-prices.csv"  # bound BEFORE try
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not _PRICES_URL:
        raise RuntimeError(_OPTION_D_MSG)
    try:
        response = requests.get(
            _PRICES_URL, headers=HEADERS, stream=True, timeout=60
        )
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading roc-prices.csv: {e}")
        raise  # fail-loud per D-17


def load_roc_prices() -> pd.DataFrame:
    """Load + validate the ROC-prices CSV.

    Under Option D the CSV is a header-only stub (0 data rows); pandera
    `strict=False` tolerates this. Once real prices land, the same
    schema catches column-name / dtype / regex drift at read time.
    """
    path = DATA_DIR / "raw" / "ofgem" / "roc-prices.csv"
    df = pd.read_csv(path)
    df = roc_prices_schema.validate(df)
    return df


__all__ = [
    "download_roc_prices",
    "load_roc_prices",
    "roc_prices_schema",
]
