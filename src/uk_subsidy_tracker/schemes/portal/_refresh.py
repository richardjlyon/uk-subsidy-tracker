"""Portal dirty-check — mtime-based against shipped scheme parquets (Plan 06-01).

``upstream_changed()`` returns True when any shipped scheme's ``annual_summary.parquet``
mtime is newer than ``cross_scheme.parquet``, OR ``cross_scheme.parquet`` is absent.

``refresh()`` is a no-op — the portal has no upstream URL to fetch. The portal is a
downstream aggregator that reads each per-scheme ``annual_summary.parquet`` and emits
``cross_scheme.parquet`` from them. ``refresh_all.SCHEMES`` orders the portal LAST so
all per-scheme rebuilds finish before the portal reads.
"""
from __future__ import annotations

from pathlib import Path

from uk_subsidy_tracker import PROJECT_ROOT


def _scheme_annual_summaries() -> list[Path]:
    """Per-scheme ``annual_summary.parquet`` paths the portal aggregates over.

    Phases 7-12 append one path per shipped scheme (FiT, SEG, Constraints, CM,
    Balancing, Grid). Order does not matter — the dirty-check is a max over
    mtimes.
    """
    return [
        PROJECT_ROOT / "data" / "derived" / "cfd" / "annual_summary.parquet",
        PROJECT_ROOT / "data" / "derived" / "ro" / "annual_summary.parquet",
        # Phases 7-12 append one path per scheme.
    ]


def upstream_changed() -> bool:
    """Return True iff cross_scheme.parquet is absent OR any source mtime is newer."""
    cross = PROJECT_ROOT / "data" / "derived" / "portal" / "cross_scheme.parquet"
    if not cross.exists():
        return True
    cross_mtime = cross.stat().st_mtime
    for src in _scheme_annual_summaries():
        if not src.exists():
            continue
        if src.stat().st_mtime > cross_mtime:
            return True
    return False


def refresh() -> None:
    """No-op — portal has no upstream URL to fetch."""
    return None
