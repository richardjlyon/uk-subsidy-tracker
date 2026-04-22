"""Pydantic row schemas for the CfD derived Parquet grains.

Five BaseModel subclasses, one per grain. Field declaration order IS the
canonical Parquet column order (D-10 source of truth). Every Field carries
`description=` and `json_schema_extra={"dtype": ..., "unit": ...}` so the
`<grain>.schema.json` sibling emitted alongside each Parquet file carries
machine-readable dtype + unit metadata for Plan 04's manifest.py.

Units convention:
- Monetary:   "£" (totals), "£/MWh" (unit prices), "£/tCO2" (carbon pricing)
- Energy:     "MWh"
- Carbon:     "tCO2"
- Dates:      "ISO-8601"
- Strings:    no unit
- Integers:   no unit unless year-like (unit: "year")

`methodology_version: str` is the last field on every row — the provenance
stamp (GOV-02) that flows from `counterfactual.METHODOLOGY_VERSION` into
every Parquet row so a disputed figure can be traced to its methodology
revision.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field


class StationMonthRow(BaseModel):
    """One row in cfd/station_month.parquet (order = Parquet column order, D-10)."""

    station_id: str = Field(
        description="LCCC CfD Unit ID.",
        json_schema_extra={"dtype": "string"},
    )
    technology: str = Field(
        description="LCCC Technology_Type (e.g. 'Offshore Wind', 'Biomass Conversion').",
        json_schema_extra={"dtype": "string"},
    )
    allocation_round: str = Field(
        description="Allocation Round label (e.g. 'Investment Contract', 'AR1').",
        json_schema_extra={"dtype": "string"},
    )
    month_end: date = Field(
        description="Last day of the settlement month (month-end anchor).",
        json_schema_extra={"dtype": "date", "unit": "ISO-8601"},
    )
    cfd_generation_mwh: float = Field(
        description="CfD-eligible generation in this month.",
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    cfd_payments_gbp: float = Field(
        description="Gross CfD payments (top-up) in this month.",
        json_schema_extra={"dtype": "float64", "unit": "£"},
    )
    strike_price_gbp_per_mwh: float | None = Field(
        default=None,
        description="Generation-weighted strike price applicable in this month.",
        json_schema_extra={"dtype": "float64", "unit": "£/MWh"},
    )
    market_reference_price_gbp_per_mwh: float | None = Field(
        default=None,
        description="Mean market reference price (IMRP / season-ahead) in this month.",
        json_schema_extra={"dtype": "float64", "unit": "£/MWh"},
    )
    methodology_version: str = Field(
        description="Gas counterfactual methodology version (GOV-02 provenance stamp).",
        json_schema_extra={"dtype": "string"},
    )


class AnnualSummaryRow(BaseModel):
    """One row in cfd/annual_summary.parquet (one row per calendar year)."""

    year: int = Field(
        description="Calendar year of the month_end anchor.",
        json_schema_extra={"dtype": "int64", "unit": "year"},
    )
    cfd_generation_mwh: float = Field(
        description="Sum of station_month.cfd_generation_mwh across this year.",
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    cfd_payments_gbp: float = Field(
        description="Sum of station_month.cfd_payments_gbp across this year.",
        json_schema_extra={"dtype": "float64", "unit": "£"},
    )
    counterfactual_payments_gbp: float = Field(
        description=(
            "Counterfactual gas-cost payments across this year "
            "(sum of counterfactual £/MWh × generation)."
        ),
        json_schema_extra={"dtype": "float64", "unit": "£"},
    )
    premium_over_gas_gbp: float = Field(
        description="cfd_payments_gbp minus counterfactual_payments_gbp.",
        json_schema_extra={"dtype": "float64", "unit": "£"},
    )
    methodology_version: str = Field(
        description="Gas counterfactual methodology version (GOV-02).",
        json_schema_extra={"dtype": "string"},
    )


class ByTechnologyRow(BaseModel):
    """One row in cfd/by_technology.parquet (year × technology grain)."""

    year: int = Field(
        description="Calendar year.",
        json_schema_extra={"dtype": "int64", "unit": "year"},
    )
    technology: str = Field(
        description="LCCC Technology_Type (from portfolio) as reported.",
        json_schema_extra={"dtype": "string"},
    )
    cfd_generation_mwh: float = Field(
        description="Sum of station_month.cfd_generation_mwh for this (year, technology).",
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    cfd_payments_gbp: float = Field(
        description="Sum of station_month.cfd_payments_gbp for this (year, technology).",
        json_schema_extra={"dtype": "float64", "unit": "£"},
    )
    methodology_version: str = Field(
        description="Gas counterfactual methodology version (GOV-02).",
        json_schema_extra={"dtype": "string"},
    )


class ByAllocationRoundRow(BaseModel):
    """One row in cfd/by_allocation_round.parquet (year × allocation_round grain)."""

    year: int = Field(
        description="Calendar year.",
        json_schema_extra={"dtype": "int64", "unit": "year"},
    )
    allocation_round: str = Field(
        description="Allocation Round label (e.g. 'Investment Contract', 'AR1').",
        json_schema_extra={"dtype": "string"},
    )
    cfd_generation_mwh: float = Field(
        description="Sum of station_month.cfd_generation_mwh for this (year, round).",
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    cfd_payments_gbp: float = Field(
        description="Sum of station_month.cfd_payments_gbp for this (year, round).",
        json_schema_extra={"dtype": "float64", "unit": "£"},
    )
    avoided_co2_tonnes: float = Field(
        description="Sum of LCCC Avoided_GHG_tonnes_CO2e for this (year, round).",
        json_schema_extra={"dtype": "float64", "unit": "tCO2"},
    )
    methodology_version: str = Field(
        description="Gas counterfactual methodology version (GOV-02).",
        json_schema_extra={"dtype": "string"},
    )


class ForwardProjectionRow(BaseModel):
    """One row in cfd/forward_projection.parquet (one row per station)."""

    station_id: str = Field(
        description="LCCC CfD Unit ID.",
        json_schema_extra={"dtype": "string"},
    )
    technology: str = Field(
        description="LCCC Technology_Type from portfolio.",
        json_schema_extra={"dtype": "string"},
    )
    contract_start_year: int = Field(
        description="Calendar year of Expected_Start_Date (or first generation, as proxy).",
        json_schema_extra={"dtype": "int64", "unit": "year"},
    )
    contract_end_year: int = Field(
        description="contract_start_year plus 15 (standard CfD term) or 35 (nuclear).",
        json_schema_extra={"dtype": "int64", "unit": "year"},
    )
    avg_annual_generation_mwh: float = Field(
        description="Historical-actuals average annual generation for this station.",
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    avg_strike_gbp_per_mwh: float = Field(
        description="Generation-weighted historical strike price.",
        json_schema_extra={"dtype": "float64", "unit": "£/MWh"},
    )
    remaining_committed_mwh: float = Field(
        description=(
            "Remaining committed generation: "
            "avg_annual_generation_mwh × max(0, contract_end_year - current_year)."
        ),
        json_schema_extra={"dtype": "float64", "unit": "MWh"},
    )
    methodology_version: str = Field(
        description="Gas counterfactual methodology version (GOV-02).",
        json_schema_extra={"dtype": "string"},
    )


def emit_schema_json(model: type[BaseModel], path: Path) -> None:
    """Write a `<grain>.schema.json` sibling next to a Parquet file (D-11).

    The JSON Schema is produced in `serialization` mode so the emitted
    structure matches what pandas/pyarrow actually write. Output is
    UTF-8 encoded, keys sorted, indented for readability, LF line endings —
    all to keep the file byte-stable across platforms (helps the D-21
    determinism test when re-emitted by Plan 04's manifest step).
    """
    schema = model.model_json_schema(mode="serialization")
    path.write_text(
        json.dumps(schema, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
