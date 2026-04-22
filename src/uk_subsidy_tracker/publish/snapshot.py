"""Versioned-snapshot assembler (Plan 04-04, PUB-03, D-13, D-14).

Produces a temp-dir layout of Parquet + CSV + schema.json + manifest.json
that `.github/workflows/deploy.yml` uploads as release assets via
`softprops/action-gh-release@v2` on `git push --tags`.

Invocation (from deploy.yml):
    uv run --frozen python -m uk_subsidy_tracker.publish.snapshot \\
        --version "${{ github.ref_name }}" \\
        --output snapshot-out/

Invocation (dry-run, local):
    uv run python -m uk_subsidy_tracker.publish.snapshot \\
        --version v2026.04-rc1 \\
        --output /tmp/snapshot-dry-run \\
        --dry-run

Layout produced:
    output_dir/
      manifest.json
      cfd/
        station_month.parquet
        station_month.csv
        station_month.schema.json
        ...

Caller (deploy.yml) uploads everything under `output_dir` as release assets.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from uk_subsidy_tracker import DATA_DIR
from uk_subsidy_tracker.publish import csv_mirror, manifest as manifest_mod
from uk_subsidy_tracker.schemes import cfd


def build(version: str, output_dir: Path) -> Path:
    """Assemble a snapshot directory for release upload.

    Order of operations:

    1. Rebuild derived Parquet (+ schema.json siblings) into output_dir/cfd/
       directly — no intermediate copy.
    2. Write CSV mirrors alongside each Parquet (same dir).
    3. Build manifest.json with absolute URLs pointing at the versioned path
       (D-13 / D-14).

    Returns the output_dir unchanged for the caller's convenience.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Derived Parquet + schema.json siblings.
    cfd_out = output_dir / "cfd"
    cfd.rebuild_derived(output_dir=cfd_out)

    # 2. CSV mirrors alongside each Parquet.
    csv_mirror.build(cfd_out)

    # 3. Manifest with versioned URLs.
    manifest_path = output_dir / "manifest.json"
    manifest_mod.build(
        version=version,
        derived_dir=cfd_out,
        raw_dir=DATA_DIR / "raw",
        output_path=manifest_path,
    )
    return output_dir


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="uk_subsidy_tracker.publish.snapshot",
        description="Assemble a versioned-snapshot directory for release upload.",
    )
    parser.add_argument(
        "--version", required=True,
        help="Calendar-based tag, e.g. v2026.04 or v2026.04-rc1 (D-14).",
    )
    parser.add_argument(
        "--output", type=Path, required=True,
        help="Output directory (created if absent; see --dry-run for non-empty handling).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="If output dir is non-empty, clear it first (local iteration).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    if args.output.exists() and any(args.output.iterdir()):
        if args.dry_run:
            shutil.rmtree(args.output)
        else:
            print(
                f"snapshot: output dir {args.output} already non-empty; "
                "pass --dry-run to clear or choose a fresh path.",
                file=sys.stderr,
            )
            return 2
    build(args.version, args.output)
    print(f"snapshot: {args.output} ready for release-asset upload.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["build", "main"]
