"""Shared sidecar writer for data/raw/<publisher>/<file>.meta.json (ARCHITECTURE §4.1).

Called by:
- src/uk_subsidy_tracker/schemes/cfd/_refresh.py::refresh()  (daily refresh path)
- src/uk_subsidy_tracker/schemes/ro/_refresh.py::refresh()   (daily refresh path)
- scripts/backfill_sidecars.py                               (one-shot reconstruction)

Atomicity: writes to `<path>.meta.json.tmp` then `os.replace()`s. On crash
mid-write, either the old sidecar survives intact or the new sidecar is
fully present — never a partial JSON document.

Serialisation byte-parity: `json.dumps(meta, sort_keys=True, indent=2) + "\n"`.
Matches scripts/backfill_sidecars.py output on the common keys so
test_manifest round-trip determinism holds regardless of which writer
produced the sidecar.

Optional ``sources[]`` field (Phase 05.2 D-03): for transcribed-from-multiple-PDFs
raw artefacts (e.g. ``data/raw/ofgem/ro-annual-aggregate.csv``), the sidecar
gains a top-level ``sources`` array with one entry per source PDF:

    {
      "url": "https://www.ofgem.gov.uk/...sy17.pdf",
      "sha256": "<sha256 of the source PDF>",
      "retrieved_on": "2026-04-24",
      "notes": "SY17 annual report"
    }

The field is OPTIONAL and OMITTED entirely when ``sources is None``; existing
single-URL sidecars (CfD, ONS gas SAP, Elexon, etc.) stay byte-identical.
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
    sources: list[dict] | None = None,
) -> Path:
    """Write a `.meta.json` sidecar alongside `raw_path` atomically.

    Fields (ARCHITECTURE §4.1 verbatim — the backfill-reconstruction marker
    key is intentionally absent from this writer; that key is exclusive to
    scripts/backfill_sidecars.py which owns the reconstruction marker):
        retrieved_at            : ISO-8601 with offset (datetime.now(UTC))
        upstream_url            : the URL that was fetched
        sha256                  : computed from raw_path content
        http_status             : 200 for live fetches; None on backfill
        publisher_last_modified : from upstream headers if available, else None
        sources                 : OPTIONAL list of per-source provenance dicts
                                  (Phase 05.2 D-03 — transcribed-from-multiple-PDFs
                                  raw artefacts). When ``None`` (default), the key
                                  is OMITTED from the meta JSON entirely so existing
                                  single-URL sidecars stay byte-identical.

    Each entry in ``sources`` SHOULD carry the four keys ``url`` / ``sha256`` /
    ``retrieved_on`` / ``notes``; the writer does not enforce shape (callers own
    the per-row provenance discipline) but downstream manifest consumers expect
    those four fields.

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
    if sources is not None:
        meta["sources"] = sources
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
