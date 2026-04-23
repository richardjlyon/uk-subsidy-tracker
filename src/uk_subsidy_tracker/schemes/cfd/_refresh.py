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
