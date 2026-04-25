# dormant: true
"""RO rollups — re-read station_month.parquet → 3 grain Parquets (Plan 05-05 Task 3).

Three builders: ``build_annual_summary``, ``build_by_technology``,
``build_by_allocation_round``. Each reads ``station_month.parquet`` from the
same ``output_dir`` written by ``build_station_month`` (D-03 canonical-grain
pattern).

Determinism discipline (D-21):
- Reads the already-written ``station_month.parquet`` rather than re-loading
  raw CSV — guarantees rollup consistency with the upstream grain.
- Every ``groupby`` passes ``sort=True`` explicitly.
- ``year`` cast to ``int64`` to match ``Ro*Row.year`` declared dtype (D-10;
  Phase 4 Plan 03 Rule-1 int32 auto-fix carried forward).
- Column order = each Row model's field-declaration order (D-10).

Dormancy:
    This module is dormant per Phase 05.2 (RO Data Reconstruction — Aggregate
    Grain). Station-level code paths are preserved in-tree but not exercised
    by the aggregate pipeline (schemes.ro.DORMANT_STATION_LEVEL = True).
    Re-activated on backlog 999.1 (Credentialed RER Access Automation) by
    flipping DORMANT_STATION_LEVEL to False and removing the per-test
    @pytest.mark.dormant marks.

    Design note: .planning/notes/ro-data-strategy-option-a1.md
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.schemas.ro import (
    RoAnnualSummaryRow,
    RoByAllocationRoundRow,
    RoByTechnologyRow,
    emit_schema_json,
)
from uk_subsidy_tracker.schemes.cfd.cost_model import _write_parquet


def _read_station_month(output_dir: Path) -> pd.DataFrame:
    """Load the canonical station × month grain written by ``build_station_month``."""
    path = output_dir / "station_month.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found — call build_station_month(output_dir) first."
        )
    return pq.read_table(path).to_pandas()


def build_annual_summary(output_dir: Path) -> pd.DataFrame:
    """Build ``annual_summary.parquet`` — one row per ``(year, country)`` per D-09.

    Columns (per ``RoAnnualSummaryRow`` field order): year, country,
    ro_generation_mwh, ro_cost_gbp, ro_cost_gbp_eroc, gas_counterfactual_gbp,
    premium_gbp, mutualisation_gbp (null when no station-month in the group
    had any mutualisation), methodology_version.
    """
    sm = _read_station_month(output_dir)
    # int64 cast — match RoAnnualSummaryRow.year (D-10).
    if len(sm) == 0:
        df = pd.DataFrame(
            {
                "year": pd.Series([], dtype="int64"),
                "country": pd.Series([], dtype="object"),
                "ro_generation_mwh": pd.Series([], dtype="float64"),
                "ro_cost_gbp": pd.Series([], dtype="float64"),
                "ro_cost_gbp_eroc": pd.Series([], dtype="float64"),
                "gas_counterfactual_gbp": pd.Series([], dtype="float64"),
                "premium_gbp": pd.Series([], dtype="float64"),
                "mutualisation_gbp": pd.Series([], dtype="Float64"),
            }
        )
    else:
        sm["year"] = sm["month_end"].dt.year.astype("int64")
        agg = (
            sm.groupby(["year", "country"], sort=True, dropna=False)
            .agg(
                ro_generation_mwh=("generation_mwh", "sum"),
                ro_cost_gbp=("ro_cost_gbp", "sum"),
                ro_cost_gbp_eroc=("ro_cost_gbp_eroc", "sum"),
                gas_counterfactual_gbp=("gas_counterfactual_gbp", "sum"),
                premium_gbp=("premium_gbp", "sum"),
                # pandas sum treats all-NaN groups as 0.0; we convert 0 ->
                # pd.NA below for D-11 semantic fidelity (non-null only on
                # obligation-year overlap with 2021-22).
                mutualisation_gbp=("mutualisation_gbp", "sum"),
            )
            .reset_index()
        )
        # WR-02 — pin mutualisation_gbp dtype to the nullable extension dtype
        # regardless of whether the upstream groupby emitted float64 (NumPy)
        # or Float64 (pandas). The empty-frame branch above also uses Float64
        # so the Parquet column logical type is stable across empty/non-empty
        # rebuilds.
        agg["mutualisation_gbp"] = agg["mutualisation_gbp"].astype("Float64")
        # D-11 — mutualisation null on rows with no mutualisation contribution.
        # Convert the post-sum 0.0 rows (which pandas produced because every
        # input was NaN) back to null; preserve positive sums.
        # The 0-exact-vs-all-null check below is robust because valid
        # mutualisation deltas are strictly positive (£/ROC * positive ROCs).
        agg.loc[
            agg["mutualisation_gbp"].fillna(0) == 0, "mutualisation_gbp"
        ] = pd.NA
        df = agg

    df["methodology_version"] = METHODOLOGY_VERSION

    columns = list(RoAnnualSummaryRow.model_fields.keys())
    df = (
        df[columns]
        .sort_values(["year", "country"], kind="mergesort")
        .reset_index(drop=True)
    )

    _write_parquet(df, output_dir / "annual_summary.parquet")
    emit_schema_json(RoAnnualSummaryRow, output_dir / "annual_summary.schema.json")
    return df


def build_by_technology(output_dir: Path) -> pd.DataFrame:
    """Build ``by_technology.parquet`` — one row per ``(year, technology)``."""
    sm = _read_station_month(output_dir)
    if len(sm) == 0:
        df = pd.DataFrame(
            {
                "year": pd.Series([], dtype="int64"),
                "technology": pd.Series([], dtype="object"),
                "ro_generation_mwh": pd.Series([], dtype="float64"),
                "ro_cost_gbp": pd.Series([], dtype="float64"),
                "ro_cost_gbp_eroc": pd.Series([], dtype="float64"),
            }
        )
    else:
        sm["year"] = sm["month_end"].dt.year.astype("int64")
        df = (
            sm.groupby(["year", "technology"], sort=True, dropna=False)
            .agg(
                ro_generation_mwh=("generation_mwh", "sum"),
                ro_cost_gbp=("ro_cost_gbp", "sum"),
                ro_cost_gbp_eroc=("ro_cost_gbp_eroc", "sum"),
            )
            .reset_index()
        )

    df["methodology_version"] = METHODOLOGY_VERSION

    columns = list(RoByTechnologyRow.model_fields.keys())
    df = (
        df[columns]
        .sort_values(["year", "technology"], kind="mergesort")
        .reset_index(drop=True)
    )

    _write_parquet(df, output_dir / "by_technology.parquet")
    emit_schema_json(RoByTechnologyRow, output_dir / "by_technology.schema.json")
    return df


def build_by_allocation_round(output_dir: Path) -> pd.DataFrame:
    """Build ``by_allocation_round.parquet`` — one row per ``(year, commissioning_window)``.

    RO has no "allocation round" axis (unlike CfD); ``commissioning_window``
    serves as the banding-cohort axis per RESEARCH §5.
    """
    sm = _read_station_month(output_dir)
    if len(sm) == 0:
        df = pd.DataFrame(
            {
                "year": pd.Series([], dtype="int64"),
                "commissioning_window": pd.Series([], dtype="object"),
                "ro_generation_mwh": pd.Series([], dtype="float64"),
                "ro_cost_gbp": pd.Series([], dtype="float64"),
                "ro_cost_gbp_eroc": pd.Series([], dtype="float64"),
            }
        )
    else:
        sm["year"] = sm["month_end"].dt.year.astype("int64")
        df = (
            sm.groupby(["year", "commissioning_window"], sort=True, dropna=False)
            .agg(
                ro_generation_mwh=("generation_mwh", "sum"),
                ro_cost_gbp=("ro_cost_gbp", "sum"),
                ro_cost_gbp_eroc=("ro_cost_gbp_eroc", "sum"),
            )
            .reset_index()
        )

    df["methodology_version"] = METHODOLOGY_VERSION

    columns = list(RoByAllocationRoundRow.model_fields.keys())
    df = (
        df[columns]
        .sort_values(["year", "commissioning_window"], kind="mergesort")
        .reset_index(drop=True)
    )

    _write_parquet(df, output_dir / "by_allocation_round.parquet")
    emit_schema_json(
        RoByAllocationRoundRow, output_dir / "by_allocation_round.schema.json"
    )
    return df
