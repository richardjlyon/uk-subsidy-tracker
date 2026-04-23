"""Shared sidecar writer for data/raw/<publisher>/<file>.meta.json (ARCHITECTURE §4.1).

Called by:
- src/uk_subsidy_tracker/schemes/cfd/_refresh.py::refresh()  (daily refresh path)
- scripts/backfill_sidecars.py                               (one-shot reconstruction)

Atomicity: writes to `<path>.meta.json.tmp` then `os.replace()`s. On crash
mid-write, either the old sidecar survives intact or the new sidecar is
fully present — never a partial JSON document.

Serialisation byte-parity: `json.dumps(meta, sort_keys=True, indent=2) + "\n"`.
Matches scripts/backfill_sidecars.py output on the common keys so
test_manifest round-trip determinism holds regardless of which writer
produced the sidecar.
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
