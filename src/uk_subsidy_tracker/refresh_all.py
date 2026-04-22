"""CI entry point — per-scheme dirty-check + conditional rebuild (D-16, D-18).

Invoked by `.github/workflows/refresh.yml` daily cron. Walks all known
schemes, calls `scheme.upstream_changed()`, and only invokes
`refresh() → rebuild_derived() → regenerate_charts() → validate()` for
those whose raw-file SHA-256 differs from the sidecar.

When anything changed:
    - copies derived/<scheme>/* → site/data/latest/<scheme>/
    - writes CSV mirrors alongside each Parquet
    - rebuilds site/data/manifest.json

When nothing changed:
    - exits 0 with "no upstream changes; skipping manifest rebuild"
    - refresh.yml then skips the create-pull-request step (Pitfall 3 — no
      noisy daily PRs)

Exit codes: 0 on clean run (whether or not anything changed), non-zero only
if a scheme's refresh/rebuild/validate actually errored.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from uk_subsidy_tracker import DATA_DIR, PROJECT_ROOT
from uk_subsidy_tracker.publish import csv_mirror, manifest as manifest_mod
from uk_subsidy_tracker.schemes import cfd

# Known schemes (Phase 5+ appends here: ('ro', ro), ('fit', fit), ...).
SCHEMES = (
    ("cfd", cfd),
)

SITE_DATA_DIR = PROJECT_ROOT / "site" / "data"
DERIVED_DIR = PROJECT_ROOT / "data" / "derived"
LATEST_DIR = SITE_DATA_DIR / "latest"


def refresh_scheme(name: str, scheme_module) -> bool:
    """Refresh one scheme if upstream changed.

    Returns True if the scheme was refreshed (upstream changed), False if
    skipped (sidecar SHAs match live raw files).
    """
    if not scheme_module.upstream_changed():
        print(f"[{name}] upstream unchanged — skipping refresh")
        return False
    print(f"[{name}] upstream changed — refreshing…")
    scheme_module.refresh()
    scheme_module.rebuild_derived()
    # Charts are regenerated after derivation (D-02 allows either data path;
    # either way, the daily refresh re-exports PNG + HTML so the docs site
    # shows current data).
    scheme_module.regenerate_charts()
    warnings = scheme_module.validate()
    if warnings:
        print(f"[{name}] validate() warnings:")
        for w in warnings:
            print(f"  - {w}")
    return True


def publish_latest(version: str) -> None:
    """Copy derived/<scheme>/ → site/data/latest/<scheme>/, mirror CSVs, build manifest."""
    LATEST_DIR.mkdir(parents=True, exist_ok=True)
    for scheme_name, _module in SCHEMES:
        src = DERIVED_DIR / scheme_name
        dst = LATEST_DIR / scheme_name
        if not src.is_dir():
            continue
        dst.mkdir(parents=True, exist_ok=True)
        # Copy all *.parquet + *.schema.json from derived to latest.
        for path in src.glob("*"):
            if not path.is_file():
                continue
            dst_path = dst / path.name
            dst_path.write_bytes(path.read_bytes())
        csv_mirror.build(dst)
    manifest_mod.build(
        version=version,
        derived_dir=DERIVED_DIR / "cfd",
        raw_dir=DATA_DIR / "raw",
        output_path=SITE_DATA_DIR / "manifest.json",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uk_subsidy_tracker.refresh_all",
        description="Per-scheme dirty-check + conditional rebuild (D-18).",
    )
    parser.add_argument(
        "--version", default="latest",
        help="Manifest version tag (default 'latest'). deploy.yml passes e.g. v2026.04.",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    any_changed = False
    for name, module in SCHEMES:
        if refresh_scheme(name, module):
            any_changed = True

    if not any_changed:
        print("refresh_all: no upstream changes; skipping manifest rebuild")
        return 0

    publish_latest(version=args.version)
    print(f"refresh_all: site/data/manifest.json rebuilt (version={args.version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "SCHEMES", "SITE_DATA_DIR", "DERIVED_DIR", "LATEST_DIR",
    "refresh_scheme", "publish_latest", "main",
]
