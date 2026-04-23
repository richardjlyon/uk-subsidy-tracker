"""Pydantic row models for the RO Parquet grains (Plan 05-03).

Five BaseModel subclasses, one per grain. **Field declaration order IS the
canonical Parquet column order** — any reorder is a D-10 breaking change
that requires a matching test update and a CHANGES.md ``## Methodology
versions`` entry citing D-10.

Per 05-CONTEXT.md decisions:

- **D-02** — ``station_month`` carries dual cost columns: ``ro_cost_gbp``
  (primary, buyout + recycle) and ``ro_cost_gbp_eroc`` (sensitivity,
  e-ROC clearing). Both aggregate into ``annual_summary``.
- **D-05** — ``ro_cost_gbp_nocarbon`` sensitivity column exposes the
  pure-subsidy vs carbon-price share on each station-month.
- **D-07** — Calendar year is the primary plotting axis; ``obligation_year``
  appears on ``station_month`` only, as audit-trail for the D-08 price-lookup
  rule.
- **D-09** — ``country`` column ('GB' or 'NI') on EVERY RO row model where
  scheme boundaries differ (station_month, annual_summary). Headlines are
  GB-only; NI rows in Parquet enable UK-wide reconstruction via filter.
- **D-10** — Field declaration order = Parquet column order on every grain.
- **D-11** — ``mutualisation_gbp`` is nullable (non-null on obligation year
  2021-22 only; verified scope: SY 2022-23 fell below threshold).
- **D-12** — ``methodology_version`` is the last column on every grain as
  the GOV-02 provenance stamp flowing from
  ``counterfactual.METHODOLOGY_VERSION``.

``emit_schema_json`` is scheme-agnostic — imported from schemas.cfd, **not
re-declared** — so the JSON Schema emitter upgrade is atomic across schemes.

Units convention:

- Monetary:  "GBP" (totals), "GBP/MWh" (unit prices, future grains)
- Energy:    "MWh"
- ROCs:      "ROCs" (integer-like floats), "ROCs/MWh" (banding factors)
- Dates:     "ISO-8601"
- Strings:   no unit
- Integers:  no unit unless year-like (unit: "year") or cardinality (unit: "count")
"""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

# Import, do NOT re-declare — scheme-agnostic emitter shared via schemas.cfd
# (D-10 trust-boundary contract; T-5.03-02 mitigation).
from uk_subsidy_tracker.schemas.cfd import emit_schema_json  # noqa: F401 (re-exported)


class RoStationMonthRow(BaseModel):
    """One row in ro/station_month.parquet.

    Field declaration order IS the Parquet column order (D-10).
    """

    station_id: str = Field(
        description="Ofgem station accreditation number.",
        json_schema_extra={"dtype": "string"},
    )
    country: str = Field(
        description="'GB' or 'NI' per Ofgem register (D-09).",
        json_schema_extra={"dtype": "string"},
    )
    technology: str = Field(
        description="Ofgem technology_type (e.g. 'Onshore Wind', 'Offshore Wind').",
        json_schema_extra={"dtype": "string"},
    )
    commissioning_window: str = Field(
        description=(
            "Banding window label (pre-2013, 2013/14, 2014/15, 2015/16, 2016/17)."
        ),
        json_schema_extra={"dtype": "string"},
    )
    month_end: date = Field(
        description="Month-end anchor of the obligation-month row.",
        json_schema_extra={"dtype": "date", "unit": "ISO-8601"},
    )
    obligation_year: int = Field(
        description=(
            "Apr-Mar obligation year containing output_period_end (D-08 price-lookup "
            "rule). March 2022 generation -> OY 2021-22."
        ),
        json_schema_extra={"dtype": "int64", "unit": "year"},
    )
    generation_mwh: float = Field(
        description="RO-eligible MWh in this station-month.",
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    rocs_issued: float = Field(
        description=(
            "Ofgem-published ROCs issued — primary per D-01 (regulator certification "
            "short-circuits R1 banding-assignment risk)."
        ),
        json_schema_extra={"dtype": "float64", "unit": "ROCs"},
    )
    rocs_computed: float = Field(
        description=(
            "generation_mwh * banding_factor_yaml — audit cross-check per D-01; "
            ">1% divergence from rocs_issued surfaces as validate() warning."
        ),
        json_schema_extra={"dtype": "float64", "unit": "ROCs"},
    )
    banding_factor_yaml: float = Field(
        description="Lookup from ro_bandings.yaml (audit source).",
        json_schema_extra={"dtype": "float64", "unit": "ROCs/MWh"},
    )
    ro_cost_gbp: float = Field(
        description=(
            "Primary cost = rocs_issued * (buyout + recycle) + mutualisation_gbp "
            "(per D-02 consumer-cost view, D-11 mutualisation additive)."
        ),
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    ro_cost_gbp_eroc: float = Field(
        description=(
            "Sensitivity: rocs_issued * e-ROC quarterly clearing price "
            "(D-02 generator-revenue view)."
        ),
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    ro_cost_gbp_nocarbon: float = Field(
        description=(
            "Sensitivity: carbon-price=0 variant — isolates pure-subsidy vs "
            "carbon-cost share of the premium (D-05)."
        ),
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    gas_counterfactual_gbp: float = Field(
        description=(
            "compute_counterfactual() unit cost * generation_mwh — shared CfD/RO "
            "counterfactual (ARCHITECTURE §6.2)."
        ),
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    premium_gbp: float = Field(
        description="ro_cost_gbp - gas_counterfactual_gbp.",
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    mutualisation_gbp: float | None = Field(
        default=None,
        description=(
            "Mutualisation delta — null except obligation year 2021-22 per D-11 "
            "(Ofgem redistributed £44.0M shortfall Dec 2022)."
        ),
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    methodology_version: str = Field(
        description=(
            "counterfactual.METHODOLOGY_VERSION provenance stamp (D-12 / GOV-02)."
        ),
        json_schema_extra={"dtype": "string"},
    )


class RoAnnualSummaryRow(BaseModel):
    """One row in ro/annual_summary.parquet (per (year, country) per D-09)."""

    year: int = Field(
        description="Calendar year of the month_end anchor (D-07 primary axis).",
        json_schema_extra={"dtype": "int64", "unit": "year"},
    )
    country: str = Field(
        description="'GB' or 'NI' per D-09.",
        json_schema_extra={"dtype": "string"},
    )
    ro_generation_mwh: float = Field(
        description="Sum of station_month.generation_mwh across this (year, country).",
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    ro_cost_gbp: float = Field(
        description=(
            "Sum of station_month.ro_cost_gbp across this (year, country) — "
            "primary consumer-cost view per D-02, includes mutualisation per D-11."
        ),
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    ro_cost_gbp_eroc: float = Field(
        description=(
            "Sum of station_month.ro_cost_gbp_eroc across this (year, country) — "
            "e-ROC sensitivity per D-02."
        ),
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    gas_counterfactual_gbp: float = Field(
        description="Sum of station_month.gas_counterfactual_gbp across this (year, country).",
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    premium_gbp: float = Field(
        description="ro_cost_gbp - gas_counterfactual_gbp for this (year, country).",
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    mutualisation_gbp: float | None = Field(
        default=None,
        description=(
            "Additive mutualisation component — non-null for obligation-year "
            "overlap with 2021-22 only per D-11."
        ),
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    methodology_version: str = Field(
        description="counterfactual.METHODOLOGY_VERSION provenance stamp (D-12 / GOV-02).",
        json_schema_extra={"dtype": "string"},
    )


class RoByTechnologyRow(BaseModel):
    """One row in ro/by_technology.parquet (per (year, technology) grain)."""

    year: int = Field(
        description="Calendar year of the month_end anchor.",
        json_schema_extra={"dtype": "int64", "unit": "year"},
    )
    technology: str = Field(
        description="Ofgem technology_type as reported.",
        json_schema_extra={"dtype": "string"},
    )
    ro_generation_mwh: float = Field(
        description="Sum of station_month.generation_mwh for this (year, technology).",
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    ro_cost_gbp: float = Field(
        description="Sum of station_month.ro_cost_gbp for this (year, technology).",
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    ro_cost_gbp_eroc: float = Field(
        description="Sum of station_month.ro_cost_gbp_eroc for this (year, technology).",
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    methodology_version: str = Field(
        description="counterfactual.METHODOLOGY_VERSION provenance stamp (D-12 / GOV-02).",
        json_schema_extra={"dtype": "string"},
    )


class RoByAllocationRoundRow(BaseModel):
    """One row in ro/by_allocation_round.parquet.

    RO has no "allocation round" axis (unlike CfD); ``commissioning_window``
    serves as the banding-cohort axis per RESEARCH §5.
    """

    year: int = Field(
        description="Calendar year of the month_end anchor.",
        json_schema_extra={"dtype": "int64", "unit": "year"},
    )
    commissioning_window: str = Field(
        description=(
            "Banding window label (pre-2013, 2013/14, 2014/15, 2015/16, 2016/17) — "
            "RO's analogue to CfD's allocation round."
        ),
        json_schema_extra={"dtype": "string"},
    )
    ro_generation_mwh: float = Field(
        description=(
            "Sum of station_month.generation_mwh for this (year, commissioning_window)."
        ),
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    ro_cost_gbp: float = Field(
        description=(
            "Sum of station_month.ro_cost_gbp for this (year, commissioning_window)."
        ),
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    ro_cost_gbp_eroc: float = Field(
        description=(
            "Sum of station_month.ro_cost_gbp_eroc for this (year, commissioning_window)."
        ),
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    methodology_version: str = Field(
        description="counterfactual.METHODOLOGY_VERSION provenance stamp (D-12 / GOV-02).",
        json_schema_extra={"dtype": "string"},
    )


class RoForwardProjectionRow(BaseModel):
    """One row in ro/forward_projection.parquet.

    Per-(projected year, technology) drawdown of remaining committed RO
    subsidy to the 2037 scheme end. Extrapolation methodology documented in
    the docstring of ``schemes/ro/forward_projection.py`` (Plan 05-07).
    """

    year: int = Field(
        description="Projected future calendar year.",
        json_schema_extra={"dtype": "int64", "unit": "year"},
    )
    technology: str = Field(
        description="Ofgem technology_type carried forward from station register.",
        json_schema_extra={"dtype": "string"},
    )
    remaining_committed_mwh: float = Field(
        description="Projected RO-eligible generation from active accreditations.",
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    remaining_cost_gbp: float = Field(
        description=(
            "Projected ro_cost_gbp = remaining_committed_mwh * avg_banding_factor * "
            "(buyout + recycle) extrapolation."
        ),
        json_schema_extra={"dtype": "float64", "unit": "GBP"},
    )
    station_count_active: int = Field(
        description=(
            "Count of accreditations still within their 20-year support window for "
            "this (year, technology)."
        ),
        json_schema_extra={"dtype": "int64", "unit": "count"},
    )
    avg_banding_factor: float = Field(
        description=(
            "Generation-weighted average banding factor for this (year, technology) "
            "across active accreditations."
        ),
        json_schema_extra={"dtype": "float64", "unit": "ROCs/MWh"},
    )
    methodology_version: str = Field(
        description="counterfactual.METHODOLOGY_VERSION provenance stamp (D-12 / GOV-02).",
        json_schema_extra={"dtype": "string"},
    )
