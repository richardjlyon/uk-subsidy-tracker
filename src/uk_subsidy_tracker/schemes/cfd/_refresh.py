"""Dirty-check + refresh helpers for the CfD scheme.

`upstream_changed()` compares SHA-256 of each raw file against its
`.meta.json` sidecar (Plan 04-02). If any differ, return True — the
daily refresh workflow will fire `refresh()` and then rebuild.

`refresh()` is a thin wrapper for this plan; Plan 04-05 wires it into
a full end-to-end refresh with sidecar rewrites.
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
    """Re-fetch LCCC/Elexon/ONS raw files.

    Phase 4 Plan 05 wires the full workflow (sidecar rewrites + git-commit-
    back). Here the minimal implementation only re-fetches LCCC; Elexon +
    ONS loaders have their own refresh paths that Plan 05 will orchestrate.
    """
    from uk_subsidy_tracker.data.lccc import (
        download_lccc_datasets,
        load_lccc_config,
    )

    config = load_lccc_config()
    download_lccc_datasets(config)
    # Elexon + ONS refresh delegated to Plan 04-05's refresh_all.py orchestrator.
