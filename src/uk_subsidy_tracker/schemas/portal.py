"""Portal cross-scheme aggregation Pydantic row model (Plan 06-01).

Mirrors ``schemas/ro.py`` shape. ``emit_schema_json`` is re-exported from
``schemas.cfd`` per D-10 (scheme-agnostic emitter; import, do NOT re-declare).

Field declaration order IS the canonical Parquet column order (D-10 source
of truth). Every Field carries ``description=`` and ``json_schema_extra={"dtype": ..., "unit": ...}``
so the ``cross_scheme.schema.json`` sibling emitted alongside the Parquet
file carries machine-readable dtype + unit metadata for ``publish/manifest.py``.

Per-row shape (long format, one row per (year, scheme) tuple for shipped schemes):

- year                : calendar year (CfD CY) or RO obligation-year start
- scheme              : 'CfD' / 'RO' / + future scheme codes
- cost_gbp            : total scheme cost (GB-only for RO)
- premium_gbp         : cost_gbp - gas_counterfactual_gbp
- generation_mwh      : subsidised MWh; nullable for pre-SY18 RO years
- households_uk       : per-year ONS UK household count (X3 denominator)
- methodology_version : counterfactual.METHODOLOGY_VERSION provenance stamp (D-12 / GOV-04)
"""
from __future__ import annotations

from pydantic import BaseModel, Field

# Import, do NOT re-declare — scheme-agnostic emitter shared via schemas.cfd
# (D-10 trust-boundary contract; mirrors schemas/ro.py).
from uk_subsidy_tracker.schemas.cfd import emit_schema_json  # noqa: F401  # re-exported


class CrossSchemeRow(BaseModel):
    """One row in portal/cross_scheme.parquet (long format; one row per (year, scheme))."""

    year: int = Field(
        description="Calendar year (CfD CY) or RO obligation-year start.",
        json_schema_extra={"dtype": "int64", "unit": "year"},
    )
    scheme: str = Field(
        description=(
            "Scheme code: 'CfD','RO',+future ('FiT','Constraints',etc.)."
        ),
        json_schema_extra={"dtype": "string"},
    )
    cost_gbp: float = Field(
        description="Total scheme cost for (year, scheme); GB-only for RO.",
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    premium_gbp: float = Field(
        description=(
            "cost_gbp - gas_counterfactual_gbp; negative when scheme cheaper than gas."
        ),
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    generation_mwh: float | None = Field(
        default=None,
        description="Subsidised generation MWh; None for pre-SY18 RO years.",
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    households_uk: int = Field(
        description=(
            "ONS UK household count for year (per-year for X3 historical accuracy)."
        ),
        json_schema_extra={"dtype": "int64", "unit": "count"},
    )
    methodology_version: str = Field(
        description=(
            "counterfactual.METHODOLOGY_VERSION provenance stamp (D-12 / GOV-04)."
        ),
        json_schema_extra={"dtype": "string"},
    )


__all__ = ["CrossSchemeRow", "emit_schema_json"]
