"""Station × month derivation for the CfD scheme (derived-layer writer).

Reads `data/raw/lccc/actual-cfd-generation.csv` +
`data/raw/lccc/cfd-contract-portfolio-status.csv` via the existing loaders
(post Plan 04-02 layout) and writes `station_month.parquet` +
`station_month.schema.json` to the target output directory via the pinned
deterministic Parquet writer (D-22).

Determinism discipline (D-21, Pitfall 1):
- NO datetime.now(), NO time.time(), NO random.* anywhere.
- Every groupby passes sort=True explicitly.
- Column order matches StationMonthRow field-declaration order (D-10).
- Final DataFrame sorted on a stable key (station_id, month_end).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pandera.pandas as pa
import pyarrow as pa_arrow
import pyarrow.parquet as pq

from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.data import load_lccc_dataset
from uk_subsidy_tracker.schemas.cfd import StationMonthRow, emit_schema_json


# Loader-owned pandera schema; every column matches StationMonthRow fields.
station_month_schema = pa.DataFrameSchema(
    {
        "station_id": pa.Column(str),
        "technology": pa.Column(str),
        "allocation_round": pa.Column(str),
        "month_end": pa.Column("datetime64[ns]", coerce=True),
        "cfd_generation_mwh": pa.Column(float),
        "cfd_payments_gbp": pa.Column(float),
        "strike_price_gbp_per_mwh": pa.Column(float, nullable=True),
        "market_reference_price_gbp_per_mwh": pa.Column(float, nullable=True),
        "methodology_version": pa.Column(str),
    },
    strict=False,
    coerce=True,
)


def _write_parquet(df: pd.DataFrame, path: Path) -> None:
    """Deterministic Parquet writer (D-22).

    Pinned options match the shared pattern used by every scheme module:
    snappy compression, Parquet 2.6, dictionary encoding, page statistics,
    1 MiB data-page size. Content-identity across rebuilds holds under
    these settings (pyarrow 24.x); schema + num_rows + cell values are
    bit-identical given identical input DataFrame shape + dtype.

    Explicitly NO `now()`, NO random — the writer is a pure function of
    the DataFrame's contents.
    """
    table = pa_arrow.Table.from_pandas(df, preserve_index=False)
    pq.write_table(
        table,
        path,
        compression="snappy",
        version="2.6",
        use_dictionary=True,
        write_statistics=True,
        data_page_size=1 << 20,
    )


def build_station_month(output_dir: Path) -> pd.DataFrame:
    """Build and persist `station_month.parquet` + `station_month.schema.json`.

    Pure function of data/raw/lccc/ content — no clock, no randomness.
    Column order = StationMonthRow field-declaration order (D-10).

    Parameters
    ----------
    output_dir
        Directory into which the Parquet + schema.json are written.
        Caller (rebuild_derived) creates the directory; this function
        does the same defensively.

    Returns
    -------
    pd.DataFrame
        The in-memory DataFrame that was written to Parquet. Returned so
        callers (aggregation.py) can reuse it without re-reading from disk
        if they hold the reference, though the documented pattern is to
        re-read from the written Parquet to exercise the round-trip path.
    """
    gen = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions").copy()
    portfolio = load_lccc_dataset("CfD Contract Portfolio Status").copy()

    # Hoisted from plotting/subsidy/cfd_dynamics.py::_prepare (lines 32-66).
    gen = gen.dropna(subset=["CFD_Generation_MWh", "Strike_Price_GBP_Per_MWh"])
    gen = gen[gen["CFD_Generation_MWh"] > 0]

    # Month-end anchor. `to_period("M").to_timestamp(how="end")` gives the
    # last day of the month; `.normalize()` strips time (stable sort key,
    # determinism).
    gen["month_end"] = (
        gen["Settlement_Date"]
        .dt.to_period("M")
        .dt.to_timestamp(how="end")
        .dt.normalize()
    )

    # Station × month grain: sum generation + payments; generation-weighted
    # strike price via pre-multiplied sum divided by total generation.
    gen["strike_x_gen"] = gen["Strike_Price_GBP_Per_MWh"] * gen["CFD_Generation_MWh"]
    grp = (
        gen.groupby(["CfD_ID", "month_end"], sort=True)
        .agg(
            cfd_generation_mwh=("CFD_Generation_MWh", "sum"),
            cfd_payments_gbp=("CFD_Payments_GBP", "sum"),
            strike_x_gen=("strike_x_gen", "sum"),
            market_reference_price_gbp_per_mwh=(
                "Market_Reference_Price_GBP_Per_MWh",
                "mean",
            ),
        )
        .reset_index()
    )

    grp["strike_price_gbp_per_mwh"] = grp["strike_x_gen"] / grp["cfd_generation_mwh"]
    grp = grp.drop(columns=["strike_x_gen"])

    # Join portfolio for technology + allocation_round. LCCC portfolio CSV
    # uses `CFD_ID` (uppercase) while generation uses `CfD_ID` (mixed case);
    # this rename aligns them per plotting/subsidy/remaining_obligations.py:83.
    portfolio = portfolio.rename(columns={"CFD_ID": "CfD_ID"})
    pf = portfolio[["CfD_ID", "Technology_Type", "Allocation_Round"]].rename(
        columns={
            "Technology_Type": "technology",
            "Allocation_Round": "allocation_round",
        }
    )
    df = grp.merge(pf, on="CfD_ID", how="left")
    df = df.rename(columns={"CfD_ID": "station_id"})
    df["methodology_version"] = METHODOLOGY_VERSION

    # Column order must match StationMonthRow for D-10.
    columns = list(StationMonthRow.model_fields.keys())
    df = (
        df[columns]
        .sort_values(["station_id", "month_end"], kind="mergesort")
        .reset_index(drop=True)
    )

    # Loader/derivation-owned validation (Phase 2 discipline carried forward).
    df = station_month_schema.validate(df)

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_parquet(df, output_dir / "station_month.parquet")
    emit_schema_json(StationMonthRow, output_dir / "station_month.schema.json")
    return df
