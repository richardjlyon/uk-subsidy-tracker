"""Backfill `.meta.json` sidecars for data/raw/<publisher>/<file> (D-05).

One-shot script run as part of the Phase 4 raw-layer migration (D-04).
For each of the five tracked raw files, computes SHA-256, reads
`git log --format=%cI` for best-effort `retrieved_at` (commit date of
the file's last change), and writes a sibling `.meta.json` with
`{retrieved_at, upstream_url, sha256, http_status, publisher_last_modified, backfilled_at}`.

Run:
    uv run python scripts/backfill_sidecars.py

Safe to re-run: overwrites existing sidecars with fresh sha256 + git-log
values. Never modifies the raw data files themselves.

Plan 04-07 refactor: SHA computation + atomic JSON write delegated to
`src/uk_subsidy_tracker/data/sidecar.py::write_sidecar()` (shared across
this backfill path and the daily `schemes/cfd/_refresh.py::refresh()`
path). This script still owns its two unique fields — `retrieved_at`
sourced from `git log --follow` rather than now(UTC), and the
`backfilled_at` reconstruction marker — which are overlaid in a
post-step re-write using the same serialisation invariants.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
BACKFILL_DATE = "2026-04-22"

# Upstream URLs — cross-check against live loaders:
#   src/uk_subsidy_tracker/data/lccc.py  (LCCC dataset UUIDs in lccc_datasets.yaml)
#   src/uk_subsidy_tracker/data/elexon.py::AGWS_URL, SYSTEM_PRICE_URL
#   src/uk_subsidy_tracker/data/ons_gas.py::GAS_SAP_URL
#
# MUST match src/uk_subsidy_tracker/schemes/cfd/_refresh.py::_URL_MAP on
# the five common keys (verified by executor diff — see Plan 04-07 Task 3).
URL_MAP = {
    "lccc/actual-cfd-generation.csv":
        "https://dp.lowcarboncontracts.uk/datastore/dump/37d1bef4-55d7-4b8e-8a47-1d24b123a20e",
    "lccc/cfd-contract-portfolio-status.csv":
        "https://dp.lowcarboncontracts.uk/datastore/dump/fdaf09d2-8cff-4799-a5b0-1c59444e492b",
    "elexon/agws.csv":
        "https://data.elexon.co.uk/bmrs/api/v1/datasets/AGWS",
    "elexon/system-prices.csv":
        "https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices",
    "ons/gas-sap.xlsx":
        "https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/output/datasets/systemaveragepricesapofgas/2026/systemaveragepriceofgasdataset160426.xlsx",
    # --- Ofgem RO (Plan 05-01, Option-D fallback) ----------------------
    # `option-d-stub:ofgem-rer-manual` is a stable marker string (not a
    # real HTTPS URL). It populates the sidecar `upstream_url` field so
    # the field is grep-comparable across paths, and signals to the Plan
    # 05-13 reviewer that real-source URLs must be plumbed during
    # post-execution review (along with `_REGISTER_URL` / `_GENERATION_URL`
    # / `_PRICES_URL` constants in the corresponding scrapers).
    "ofgem/ro-register.xlsx":
        "option-d-stub:ofgem-rer-manual",
    "ofgem/ro-generation.csv":
        "option-d-stub:ofgem-rer-manual",
    "ofgem/roc-prices.csv":
        "option-d-stub:ofgem-rer-manual",
}


def git_last_change(path: Path) -> str:
    """Best-effort retrieved_at from git log of this path (or its pre-rename origin)."""
    result = subprocess.run(
        ["git", "log", "-1", "--follow", "--format=%cI", "--", str(path)],
        cwd=PROJECT_ROOT, check=False, capture_output=True, text=True,
    )
    stamp = result.stdout.strip()
    return stamp or f"{BACKFILL_DATE}T00:00:00+00:00"


def main() -> None:
    if not RAW_ROOT.is_dir():
        raise SystemExit(
            f"Missing {RAW_ROOT}. Run `git mv` for the raw files first, "
            f"then re-run this script (see Phase 4 Plan 02 Task 2)."
        )

    # Import the shared writer (Plan 04-07 Task 1). The backfill script uses
    # it for SHA + atomic JSON write; it then overlays the two backfill-specific
    # fields (`retrieved_at` from git log + `backfilled_at` marker).
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from uk_subsidy_tracker.data.sidecar import write_sidecar

    for rel_path, upstream_url in URL_MAP.items():
        raw_path = RAW_ROOT / rel_path
        if not raw_path.exists():
            raise SystemExit(f"Expected raw file {raw_path} not found.")

        # 1. Write the common-keys sidecar via the shared helper (atomic).
        meta_path = write_sidecar(
            raw_path=raw_path,
            upstream_url=upstream_url,
            http_status=None,                # backfill marker
            publisher_last_modified=None,    # unknown for backfills
        )

        # 2. Overlay backfill-specific fields (retrieved_at from git log +
        #    backfilled_at marker). Re-serialise with the same invariants
        #    (sort_keys=True, indent=2, trailing newline) + atomic rename.
        meta = json.loads(meta_path.read_text())
        meta["retrieved_at"] = git_last_change(raw_path)
        meta["backfilled_at"] = BACKFILL_DATE
        tmp_path = meta_path.with_suffix(meta_path.suffix + ".tmp")
        tmp_path.write_text(
            json.dumps(meta, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(tmp_path, meta_path)
        print(f"wrote {meta_path}")


if __name__ == "__main__":
    main()
