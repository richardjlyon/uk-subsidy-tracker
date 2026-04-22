"""Load and validate `tests/fixtures/benchmarks.yaml`.

Mirrors the Pydantic + yaml.safe_load idiom from
`src/uk_subsidy_tracker/data/lccc.py::load_lccc_config`. Two-layer model:
`BenchmarkEntry` for a single published figure, `Benchmarks` for the
collection grouped by source.

Per CONTEXT D-05, each entry carries full provenance: source key (from
parent YAML key), year, value in £bn, URL, retrieval date, notes
(scheme-subset / CPI / FY-vs-CY rationale), and per-entry tolerance.
"""

from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, HttpUrl


class BenchmarkEntry(BaseModel):
    """A single benchmark figure from a named source."""

    source: str = Field(..., description="Parent YAML key, e.g. 'lccc_self' or 'obr_efo'.")
    year: int = Field(..., ge=2015, le=2050)
    value_gbp_bn: float = Field(..., description="Published aggregate value in £bn.")
    url: HttpUrl
    retrieved_on: date
    notes: str
    tolerance_pct: float = Field(..., gt=0, le=50.0)


class Benchmarks(BaseModel):
    """Collection of benchmark entries, grouped by source key.

    Each field is a list of `BenchmarkEntry`. Default `[]` so a source
    can be present-but-empty (D-11 fallback posture).
    """

    lccc_self: list[BenchmarkEntry] = Field(default_factory=list)
    ofgem_transparency: list[BenchmarkEntry] = Field(default_factory=list)
    obr_efo: list[BenchmarkEntry] = Field(default_factory=list)
    desnz_energy_trends: list[BenchmarkEntry] = Field(default_factory=list)
    hoc_library: list[BenchmarkEntry] = Field(default_factory=list)
    nao_audit: list[BenchmarkEntry] = Field(default_factory=list)

    def all_external_entries(self) -> list[BenchmarkEntry]:
        """All non-LCCC-floor entries (for parametrised external-anchor tests)."""
        return [
            *self.ofgem_transparency,
            *self.obr_efo,
            *self.desnz_energy_trends,
            *self.hoc_library,
            *self.nao_audit,
        ]


def load_benchmarks(config_path: str = "benchmarks.yaml") -> Benchmarks:
    """Load and validate benchmarks from `tests/fixtures/benchmarks.yaml`.

    Injects the parent YAML key as the `source` field on each
    `BenchmarkEntry` so downstream test-failure messages can cite it.
    """
    default_dir = Path(__file__).parent
    with open(default_dir / config_path, "r") as f:
        raw = yaml.safe_load(f) or {}

    # Inject `source` on every entry from its parent key before Pydantic validation.
    for source_key, entries in raw.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            entry["source"] = source_key

    return Benchmarks(**raw)


__all__ = ["BenchmarkEntry", "Benchmarks", "load_benchmarks"]
