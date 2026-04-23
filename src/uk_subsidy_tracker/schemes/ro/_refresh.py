"""Dirty-check + refresh helpers for the RO scheme (Plan 05-05).

Mirrors ``schemes/cfd/_refresh.py`` verbatim with Ofgem substitutions. Under
the current Plan 05-01 Option-D posture all three ``_URL_MAP`` values are the
stable marker string ``option-d-stub:ofgem-rer-manual`` — a real HTTPS URL
is plumbed in Plan 05-13 post-execution review (together with populating the
``_REGISTER_URL`` / ``_GENERATION_URL`` / ``_PRICES_URL`` constants in the
three scraper modules).

``upstream_changed()`` compares SHA-256 of each raw Ofgem file against its
``.meta.json`` sidecar (Plan 04-02 substrate reused). Returns True if any
sidecar is missing or mismatched.

``refresh()`` wires the three downloaders + rewrites three sidecars. Under
Option D each downloader raises ``RuntimeError`` — the daily refresh workflow
will surface the failure as a ``refresh-failure`` Issue until Plan 05-13
lands real URLs.

Cross-file byte-parity invariant (test_refresh_loop): ``_URL_MAP`` MUST match
``scripts/backfill_sidecars.py::URL_MAP`` byte-for-byte on the three Ofgem
keys.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from uk_subsidy_tracker import DATA_DIR

_RAW_FILES = [
    "raw/ofgem/ro-register.xlsx",
    "raw/ofgem/ro-generation.csv",
    "raw/ofgem/roc-prices.csv",
]

# Upstream URLs — MUST match scripts/backfill_sidecars.py::URL_MAP exactly on
# the three Ofgem keys. Option-D stub markers live on both sides until Plan
# 05-13 review replaces them with real HTTPS URLs (or wrappers around
# Playwright session-cookie flows for RER SharePoint access).
_URL_MAP: dict[str, str] = {
    "raw/ofgem/ro-register.xlsx": "option-d-stub:ofgem-rer-manual",
    "raw/ofgem/ro-generation.csv": "option-d-stub:ofgem-rer-manual",
    "raw/ofgem/roc-prices.csv": "option-d-stub:ofgem-rer-manual",
}


def _sha256(path: Path) -> str:
    """Compute SHA-256 of a file in 64 KiB chunks (matches sidecar._sha256_of)."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def upstream_changed() -> bool:
    """Return True iff any Ofgem raw file's sha256 differs from its sidecar.

    A missing sidecar or missing raw file counts as drift (True) because we
    cannot assert content identity.
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
    """Re-fetch the three Ofgem raw files and rewrite sidecars atomically.

    Under Option D each downloader raises ``RuntimeError`` (Plan 05-01) —
    the daily refresh workflow sees the failure and opens a
    ``refresh-failure`` Issue. This is by design until Plan 05-13 review
    unblocks a real-URL path.

    Fail-loud (Phase 4 D-17): any downloader exception propagates; the
    sidecar-rewrite loop runs only on successful downloads.
    """
    from uk_subsidy_tracker.data.ofgem_ro import (
        download_ofgem_ro_generation,
        download_ofgem_ro_register,
    )
    from uk_subsidy_tracker.data.roc_prices import download_roc_prices
    from uk_subsidy_tracker.data.sidecar import write_sidecar

    # 1. Ofgem RO station register (XLSX).
    download_ofgem_ro_register()

    # 2. Ofgem monthly ROC-issuance (CSV).
    download_ofgem_ro_generation()

    # 3. ROC prices (buyout + recycle + e-ROC + mutualisation).
    download_roc_prices()

    # 4. Rewrite each sidecar so SHA matches fresh bytes + retrieved_at = now.
    for rel, upstream_url in _URL_MAP.items():
        raw_path = DATA_DIR / rel
        if not raw_path.exists():
            raise FileNotFoundError(
                f"refresh() downloaded but raw file missing: {raw_path}. "
                f"Upstream URL: {upstream_url}"
            )
        write_sidecar(raw_path=raw_path, upstream_url=upstream_url)
