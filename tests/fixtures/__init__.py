"""Pydantic + YAML fixture loaders for the `tests/fixtures/*.yaml` files.

Mirrors the Pydantic + yaml.safe_load idiom from
`src/uk_subsidy_tracker/data/lccc.py::load_lccc_config`. Two loader families:

- `load_benchmarks()` + `BenchmarkEntry`/`Benchmarks` — per-source published
  reconciliation figures (Phase 2 D-05). Each entry carries full provenance:
  source key (from parent YAML key), year, value in £bn, URL, retrieval date,
  notes (scheme-subset / CPI / FY-vs-CY rationale), and per-entry tolerance.
- `load_constants()` + `ConstantProvenance`/`Constants` — per-constant
  provenance blocks for `src/uk_subsidy_tracker/counterfactual.py`
  (SEED-001 Tier 2 / Phase 4 D-23). Each entry mirrors the live constant's
  `Provenance:` docstring and carries the live value for drift detection.
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


class ConstantProvenance(BaseModel):
    """Provenance block for one `counterfactual.py` constant (SEED-001 Tier 2).

    Each block mirrors the `Provenance:` docstring on the live constant:
    source citation, upstream URL, methodological basis, retrieval date,
    next-audit date, the live value, and a unit string. `notes` is
    free-form for audit-trail entries (e.g. correction history).
    """

    name: str = Field(
        ...,
        description=(
            "Parent YAML key = live counterfactual.py attr name "
            "(or synthetic {ATTR}_{DICT_KEY} for dict entries like "
            "DEFAULT_CARBON_PRICES_2022)."
        ),
    )
    source: str = Field(
        ...,
        description="Human-readable source citation (regulator + publication).",
    )
    url: HttpUrl
    basis: str = Field(
        ...,
        description="Methodological basis — what's being measured, and how.",
    )
    retrieved_on: date
    next_audit: date | None = None
    value: float
    unit: str
    notes: str | None = None


class Constants(BaseModel):
    """Container: `entries` maps live attr name (or synthetic key) → `ConstantProvenance`."""

    entries: dict[str, ConstantProvenance] = Field(default_factory=dict)


def load_constants(config_path: str = "constants.yaml") -> Constants:
    """Load and validate `tests/fixtures/constants.yaml`.

    Mirrors `load_benchmarks`: injects the parent YAML key as the `name`
    field on each entry before Pydantic validation so downstream
    test-failure messages can cite the constant by name.
    """
    default_dir = Path(__file__).parent
    with open(default_dir / config_path, "r") as f:
        raw = yaml.safe_load(f) or {}

    entries: dict[str, ConstantProvenance] = {}
    for key, payload in raw.items():
        if not isinstance(payload, dict):
            continue
        payload = {**payload, "name": key}
        entries[key] = ConstantProvenance(**payload)

    return Constants(entries=entries)


__all__ = [
    "BenchmarkEntry",
    "Benchmarks",
    "load_benchmarks",
    "ConstantProvenance",
    "Constants",
    "load_constants",
]
