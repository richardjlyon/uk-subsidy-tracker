"""Manifest.json builder — the public contract (Plan 04-04, D-07 / D-08 / D-09).

Shape is ARCHITECTURE §4.3 verbatim (D-07). Pydantic v2 models are the source
of truth; `json.dumps(model.model_dump(mode="json"), sort_keys=True, indent=2)`
is the canonical serialisation (Pydantic v2 does NOT support `sort_keys` on
`model_dump_json()` — see GitHub issue #7424 — hence the stdlib path).

External consumers read this file to:

1. Discover every published dataset (the `datasets[]` block).
2. Follow absolute URLs to Parquet + CSV + schema.json per dataset.
3. Verify integrity via SHA-256 (lower-case 64-char hex on every file).
4. Cite a methodology (via `methodology_version` + `methodology_page`).
5. Cite a pipeline git SHA that produced the artefact (GOV-02).

D-12 chain (methodology_version provenance):
    counterfactual.py::METHODOLOGY_VERSION
      → DataFrame column via compute_counterfactual()
      → Parquet column via rebuild_derived()
      → cross-check in schemes/cfd/__init__.py::validate() Check 3
         (Parquet column == METHODOLOGY_VERSION constant)
      → top-level manifest.methodology_version field (HERE).
    The Parquet-column read is validated upstream by validate() which is
    invoked before manifest build in refresh_all.refresh_scheme(); manifest.py
    therefore reads the constant directly rather than re-reading the Parquet
    column, avoiding duplicate I/O while preserving end-to-end provenance.

Pitfall 3 mitigation (generated_at stability):
    `generated_at` sources from `max(retrieved_at across *.meta.json sidecars)`
    — content-addressed, not a wall-clock read. Two consecutive builds with
    the same raw state produce byte-identical manifest.json. `refresh_all.py`
    short-circuits BEFORE calling manifest.build() when nothing upstream
    changed, but this field-level stability is the safety net.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from uk_subsidy_tracker import PROJECT_ROOT

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Per-grain provenance wiring (B-02 mitigation — provenance is per-grain,
# not "every source feeds every dataset").
# ---------------------------------------------------------------------------

GRAIN_SOURCES: dict[str, list[str]] = {
    "station_month": [
        "lccc/actual-cfd-generation.csv",
        "lccc/cfd-contract-portfolio-status.csv",
        "ons/gas-sap.xlsx",
        "elexon/system-prices.csv",
    ],
    "annual_summary": [
        "lccc/actual-cfd-generation.csv",
        "lccc/cfd-contract-portfolio-status.csv",
        "ons/gas-sap.xlsx",
        "elexon/system-prices.csv",
    ],
    "by_technology": [
        "lccc/actual-cfd-generation.csv",
        "lccc/cfd-contract-portfolio-status.csv",
        "ons/gas-sap.xlsx",
        "elexon/system-prices.csv",
    ],
    "by_allocation_round": [
        "lccc/actual-cfd-generation.csv",
        "lccc/cfd-contract-portfolio-status.csv",
    ],
    "forward_projection": [
        "lccc/cfd-contract-portfolio-status.csv",
    ],
}

GRAIN_TITLES: dict[str, str] = {
    "station_month": "CfD Station × Month",
    "annual_summary": "CfD Annual Summary",
    "by_technology": "CfD by Technology",
    "by_allocation_round": "CfD by Allocation Round",
    "forward_projection": "CfD Forward Projection",
}

GRAIN_DESCRIPTIONS: dict[str, str] = {
    "station_month": "station × month",
    "annual_summary": "year",
    "by_technology": "year × technology",
    "by_allocation_round": "year × allocation round",
    "forward_projection": "year (forward)",
}


# ---------------------------------------------------------------------------
# Pydantic models — ARCHITECTURE §4.3 verbatim (D-07)
# ---------------------------------------------------------------------------

class Source(BaseModel):
    """One upstream source feeding a derived dataset.

    `upstream_url: str` NOT HttpUrl — Pitfall 6: HttpUrl serialisation has
    varied across Pydantic v2 minor versions; plain str is the stable public
    contract.
    """

    name: str
    upstream_url: str
    retrieved_at: datetime
    source_sha256: str = Field(
        ..., pattern=r"^[0-9a-f]{64}$",
        description="Lowercase hex SHA-256 of the raw file."
    )


class Dataset(BaseModel):
    """One published dataset (one Parquet + CSV + schema.json triple)."""

    id: str
    title: str
    grain: str
    row_count: int = Field(..., ge=0)
    schema_url: str
    parquet_url: str
    csv_url: str
    versioned_url: str
    sha256: str = Field(..., pattern=r"^[0-9a-f]{64}$")
    sources: list[Source]
    methodology_page: str


class Manifest(BaseModel):
    """Public contract. Shape is ARCHITECTURE §4.3 verbatim (D-07)."""

    version: str
    generated_at: datetime
    methodology_version: str
    pipeline_git_sha: str
    datasets: list[Dataset]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _git_sha() -> str:
    """Current HEAD SHA for GOV-02 provenance."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    """Streaming SHA-256 of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _site_url() -> str:
    """Absolute base URL for D-09 URL construction.

    Prefers SITE_URL environment variable (deploy.yml sets this to the
    Cloudflare Pages host); falls back to mkdocs.yml::site_url. Trailing
    slash stripped so `f"{base}/data/..."` works regardless of config.

    Note: mkdocs.yml contains Python-tag custom constructors (e.g.
    `!!python/name:material.extensions.emoji.twemoji`) which yaml.safe_load
    rejects. We only need `site_url`, so we line-scan for the top-level key
    rather than parsing the whole document. This is safer than
    `yaml.Loader`/`yaml.FullLoader` (which would execute arbitrary Python
    tags) and cheaper than a custom SafeLoader subclass.
    """
    override = os.environ.get("SITE_URL")
    if override:
        return override.rstrip("/")
    mkdocs_path = PROJECT_ROOT / "mkdocs.yml"
    site_url: str | None = None
    for line in mkdocs_path.read_text().splitlines():
        # Top-level key only — must start at column 0.
        if line.startswith("site_url:"):
            _, _, rhs = line.partition(":")
            site_url = rhs.strip().strip('"').strip("'")
            break
    if not site_url:
        raise RuntimeError(f"site_url not found in {mkdocs_path}")
    return site_url.rstrip("/")


def _read_methodology_version() -> str:
    """Return counterfactual.METHODOLOGY_VERSION via import (D-12 chain)."""
    from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
    return METHODOLOGY_VERSION


def _latest_retrieved_at(raw_dir: Path) -> datetime:
    """Max retrieved_at across every *.meta.json sidecar (Pitfall 3).

    Content-addressed: rebuilding the manifest with the same raw state
    produces byte-identical output. When a refresh updates a sidecar's
    retrieved_at, this moves forward — and only then does the manifest
    change.
    """
    latest: datetime | None = None
    for meta in sorted(raw_dir.rglob("*.meta.json")):
        data = json.loads(meta.read_text())
        retrieved = data.get("retrieved_at")
        if not retrieved:
            continue
        # datetime.fromisoformat handles "+00:00" and "Z" (3.11+).
        if retrieved.endswith("Z"):
            retrieved = retrieved[:-1] + "+00:00"
        parsed = datetime.fromisoformat(retrieved)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        if latest is None or parsed > latest:
            latest = parsed
    if latest is None:
        raise RuntimeError(
            f"no retrieved_at found in any *.meta.json under {raw_dir}; "
            "run scripts/backfill_sidecars.py"
        )
    return latest


def _source_for_raw(rel_path: str, raw_dir: Path) -> Source:
    """Build one Source entry from the sidecar + raw file.

    Raw-file SHA is RE-COMPUTED from the on-disk raw file (W-05 mitigation).
    The sidecar's `sha256` is metadata — trusted-but-verified. If the two
    disagree, log a warning but emit the freshly-computed hash (raw file is
    truth; sidecar is metadata).
    """
    raw_path = raw_dir / rel_path
    meta_path = raw_path.with_suffix(raw_path.suffix + ".meta.json")
    if not raw_path.exists():
        raise FileNotFoundError(f"raw file missing: {raw_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"sidecar missing: {meta_path}")
    meta = json.loads(meta_path.read_text())
    # W-05 mitigation: RE-COMPUTE from Path(raw_path); do NOT trust sidecar.sha256.
    source_sha256 = _sha256(Path(raw_path))
    sidecar_sha = meta.get("sha256")
    if sidecar_sha and sidecar_sha != source_sha256:
        logger.warning(
            "sidecar sha256 drift for %s: sidecar=%s live=%s — emitting live",
            raw_path, sidecar_sha, source_sha256,
        )
    retrieved = meta["retrieved_at"]
    if isinstance(retrieved, str) and retrieved.endswith("Z"):
        retrieved = retrieved[:-1] + "+00:00"
    # Publisher name = first path component (lccc / elexon / ons).
    publisher, _, filename = rel_path.partition("/")
    name = f"{publisher}.{Path(filename).stem}"
    return Source(
        name=name,
        upstream_url=str(meta["upstream_url"]),
        retrieved_at=datetime.fromisoformat(retrieved) if isinstance(retrieved, str) else retrieved,
        source_sha256=source_sha256,
    )


def _versioned_segment(version: str) -> str:
    """Map a tag like 'v2026.04' or 'v2026.04-rc1' into the virtual path segment.

    ARCHITECTURE §4.3 example uses `v<YYYY-MM-DD>`; tag naming uses
    `v<YYYY.MM>[-rcN]` (D-14). We pass the version through unchanged — the
    caller chose it. `deploy.yml` passes `${{ github.ref_name }}` on tag push.
    """
    return version


def _assemble_dataset_entries(
    derived_dir: Path, raw_dir: Path, base: str, version: str,
) -> list[Dataset]:
    """Walk derived_dir for *.parquet and emit one Dataset per grain.

    Provenance (sources[]) per grain comes from GRAIN_SOURCES — not "every
    source to every dataset" (B-02 mitigation).
    """
    import pyarrow.parquet as pq

    datasets: list[Dataset] = []
    vseg = _versioned_segment(version)
    for parquet_path in sorted(derived_dir.glob("*.parquet")):
        grain = parquet_path.stem
        row_count = pq.read_metadata(parquet_path).num_rows
        file_sha = _sha256(parquet_path)
        rels = GRAIN_SOURCES.get(grain)
        if rels is None:
            logger.warning("grain %s not in GRAIN_SOURCES; skipping", grain)
            continue
        sources = [_source_for_raw(rel, raw_dir) for rel in rels]
        datasets.append(Dataset(
            id=f"cfd.{grain}",
            title=GRAIN_TITLES.get(grain, grain),
            grain=GRAIN_DESCRIPTIONS.get(grain, grain),
            row_count=row_count,
            schema_url=f"{base}/data/latest/cfd/{grain}.schema.json",
            parquet_url=f"{base}/data/latest/cfd/{grain}.parquet",
            csv_url=f"{base}/data/latest/cfd/{grain}.csv",
            versioned_url=f"{base}/data/{vseg}/cfd/{grain}.parquet",
            sha256=file_sha,
            sources=sources,
            methodology_page=f"{base}/methodology/gas-counterfactual/",
        ))
    return datasets


def build(
    version: str,
    derived_dir: Path = Path("data/derived/cfd"),
    raw_dir: Path = Path("data/raw"),
    output_path: Path = Path("site/data/manifest.json"),
) -> Manifest:
    """Assemble manifest from disk state and write to output_path.

    Args:
        version: calendar-based tag (e.g. 'v2026.04' or 'v2026.04-rc1') that
            feeds the versioned_url segment per dataset.
        derived_dir: Parquet source directory (default: data/derived/cfd).
        raw_dir: root of raw publisher dirs (default: data/raw).
        output_path: where to write manifest.json (default: site/data/manifest.json).

    Returns:
        The Manifest model that was written (also useful in tests).
    """
    derived_dir = Path(derived_dir)
    raw_dir = Path(raw_dir)
    output_path = Path(output_path)

    base = _site_url()
    pipeline_git_sha = _git_sha()
    generated_at = _latest_retrieved_at(raw_dir)

    datasets = _assemble_dataset_entries(derived_dir, raw_dir, base, version)

    manifest = Manifest(
        version=version,
        generated_at=generated_at,
        methodology_version=_read_methodology_version(),
        pipeline_git_sha=pipeline_git_sha,
        datasets=datasets,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(
        manifest.model_dump(mode="json"),
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    ) + "\n"
    output_path.write_text(body, encoding="utf-8", newline="\n")
    return manifest


__all__ = [
    "Manifest", "Dataset", "Source",
    "GRAIN_SOURCES", "GRAIN_TITLES", "GRAIN_DESCRIPTIONS",
    "build",
]
