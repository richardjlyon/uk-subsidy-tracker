"""Dirty-check + refresh helpers for the RO scheme (Plan 05-05 + Phase 05.2).

``upstream_changed()`` compares SHA-256 of the 12-year XLSX raw file against
its ``.meta.json`` sidecar (Plan 04-02 substrate reused). Returns True if the
sidecar is missing or mismatched.

``refresh()`` fetches the 12-year XLSX + writes its sidecar when DORMANT_STATION_LEVEL
is True. When False (station-level re-activated on backlog 999.1), also fetches
the station register, monthly ROC-issuance CSV, and ROC prices.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from uk_subsidy_tracker import DATA_DIR

_XLSX_REL = "raw/ofgem/rocs_report_2006_to_2018_20250410081520.xlsx"

# Upstream URL for the 12-year XLSX — used by upstream_changed() sidecar check.
_XLSX_URL = (
    "https://www.ofgem.gov.uk/sites/default/files/2025-05/"
    "rocs_report_2006_to_2018_20250410081520.xlsx"
)


def _sha256(path: Path) -> str:
    """Compute SHA-256 of a file in 64 KiB chunks (matches sidecar._sha256_of)."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def upstream_changed() -> bool:
    """Return True iff the 12-year XLSX sha256 differs from its sidecar.

    A missing sidecar or missing raw file counts as drift (True) because we
    cannot assert content identity.
    """
    raw = DATA_DIR / _XLSX_REL
    meta = raw.with_suffix(raw.suffix + ".meta.json")
    if not raw.exists() or not meta.exists():
        return True
    sidecar = json.loads(meta.read_text())
    return _sha256(raw) != sidecar.get("sha256")


def refresh() -> None:
    """Re-fetch RO raw files (XLSX only when dormant; XLSX + station-level when active).

    When DORMANT_STATION_LEVEL is True:
      - Downloads the 12-year XLSX + writes its sidecar.
      - Skips station-level downloads (ofgem_ro register/generation, roc_prices).

    When DORMANT_STATION_LEVEL is False (backlog 999.1 re-activation):
      - Also downloads the station register, monthly ROC-issuance CSV,
        and ROC prices + rewrites their sidecars.
    """
    from uk_subsidy_tracker.schemes.ro import DORMANT_STATION_LEVEL
    from uk_subsidy_tracker.data.ofgem_aggregate import (
        XLSX_URL,
        download_twelve_year_xlsx,
    )
    from uk_subsidy_tracker.data.sidecar import write_sidecar

    xlsx_path = download_twelve_year_xlsx()
    write_sidecar(
        raw_path=xlsx_path,
        upstream_url=XLSX_URL,
        http_status=200,
        publisher_last_modified="2025-05-21",
    )

    if DORMANT_STATION_LEVEL:
        return

    # Station-level path (re-activated on backlog 999.1)
    from uk_subsidy_tracker.data.ofgem_ro import (
        download_ofgem_ro_generation,
        download_ofgem_ro_register,
    )
    from uk_subsidy_tracker.data.roc_prices import download_roc_prices

    download_ofgem_ro_register()
    download_ofgem_ro_generation()
    download_roc_prices()
