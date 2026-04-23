"""RO concentration — S4 Lorenz curve on station-level lifetime RO cost.

Mirrors ``plotting/subsidy/lorenz.py`` (CfD). GB-only per D-12 / D-09;
NIRO rows suppressed from the headline curve but remain accessible via
the Parquet ``country='NI'`` filter (T-5.08-02 mitigation).

X-axis: cumulative % of GB RO-accredited stations, sorted largest-
recipient first. Y-axis: cumulative % of lifetime ``ro_cost_gbp``.
Dashed diagonal = perfect equality.

Threshold markers pinned at 50% and 80% cumulative cost show the classic
concentration story; top-3 station callouts land the "a handful of plants
account for most of the bill" narrative in the Lorenz convention.

Filename: ``subsidy_ro_concentration`` per RO-MODULE-SPEC Appendix A.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pyarrow.parquet as pq

from uk_subsidy_tracker.plotting import ChartBuilder
from uk_subsidy_tracker.schemes import ro


def _prepare() -> pd.DataFrame:
    """Read station_month, restrict to GB, collapse to lifetime cost per station."""
    path = ro.DERIVED_DIR / "station_month.parquet"
    if not path.exists():
        return pd.DataFrame()

    sm = pq.read_table(path).to_pandas()
    if len(sm) == 0:
        return sm

    gb = sm[sm["country"] == "GB"]
    by_station = (
        gb.groupby(["station_id"], sort=False, observed=True)
        .agg(payments=("ro_cost_gbp", "sum"))
        .reset_index()
    )
    by_station = (
        by_station[by_station["payments"] > 0]
        .sort_values("payments", ascending=False)
        .reset_index(drop=True)
    )
    return by_station


def _placeholder(builder: ChartBuilder) -> go.Figure:
    fig = builder.create_basic()
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        text=(
            "<b>No RO data yet</b><br><br>"
            "data/derived/ro/station_month.parquet is empty.<br>"
            "Regenerate after Ofgem RER URLs are plumbed (Plan 05-13)."
        ),
        showarrow=False,
        font={"size": 14, "color": "#9ca3af"},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def main() -> None:
    by_station = _prepare()

    if len(by_station) == 0:
        builder = ChartBuilder(
            title="RO cost concentration — Lorenz curve (GB-only)",
            height=500,
        )
        fig = _placeholder(builder)
        builder.save(fig, "subsidy_ro_concentration", export_twitter=True)
        return

    total = float(by_station["payments"].sum())
    n = len(by_station)
    cum_pct_payments = (by_station["payments"].cumsum() / total * 100).tolist()
    cum_pct_stations = (np.arange(1, n + 1) / n * 100).tolist()
    total_bn = total / 1e9

    builder = ChartBuilder(
        title=(
            f"RO Cost Concentration — £{total_bn:.1f}bn across {n} GB stations, "
            "shared very unequally"
        ),
        height=700,
    )
    fig = builder.create_basic()

    # Equality diagonal.
    fig.add_trace(
        go.Scatter(
            x=[0, 100],
            y=[0, 100],
            mode="lines",
            line={"color": "grey", "width": 1, "dash": "dash"},
            name="Equal distribution",
            hoverinfo="skip",
        )
    )

    # Lorenz curve.
    x_vals = [0] + cum_pct_stations
    y_vals = [0] + cum_pct_payments
    fig.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines",
            line={"color": "#d62728", "width": 3},
            name="Actual distribution",
            fill="tozeroy",
            fillcolor="rgba(214,39,40,0.1)",
            hoverinfo="skip",
        )
    )

    # 50% + 80% threshold markers.
    for threshold in (50, 80):
        idx = next((i for i, v in enumerate(cum_pct_payments) if v >= threshold), n - 1)
        n_stations = idx + 1
        pct_stations = cum_pct_stations[idx]
        fig.add_trace(
            go.Scatter(
                x=[pct_stations],
                y=[threshold],
                mode="markers+text",
                marker={"size": 10, "color": "#d62728"},
                text=[f"{n_stations} stations = {threshold}% of £{total_bn:.1f}bn"],
                textposition="middle right",
                textfont={"size": 11},
                showlegend=False,
                hovertemplate=(
                    f"{n_stations} stations<br>{threshold}% of subsidy<extra></extra>"
                ),
            )
        )

    # Top-3 named-station callouts.
    for i in range(min(3, n)):
        station = str(by_station.iloc[i]["station_id"])
        pmt = float(by_station.iloc[i]["payments"]) / 1e6
        fig.add_trace(
            go.Scatter(
                x=[cum_pct_stations[i]],
                y=[cum_pct_payments[i]],
                mode="markers+text",
                marker={"size": 8, "color": "#1f77b4"},
                text=[f"{station} (£{pmt:.0f}m)"],
                textposition="top left" if i > 0 else "bottom right",
                textfont={"size": 9},
                showlegend=False,
                hovertemplate=f"{station}<br>£{pmt:.0f}m<extra></extra>",
            )
        )

    # GB-only annotation per D-09 + T-5.08-02.
    fig.add_annotation(
        text="GB-only; NIRO stations available via country='NI' filter in Parquet",
        xref="paper",
        yref="paper",
        x=0.0,
        y=1.04,
        xanchor="left",
        yanchor="bottom",
        showarrow=False,
        font={"size": 9, "color": "#9ca3af"},
    )

    fig.update_xaxes(
        title="Cumulative % of stations (largest first)",
        ticksuffix="%",
        range=[0, 100],
    )
    fig.update_yaxes(
        title="Cumulative % of total RO subsidy",
        ticksuffix="%",
        range=[0, 100],
    )
    fig.update_layout(showlegend=False)

    builder.save(fig, "subsidy_ro_concentration", export_twitter=True)


if __name__ == "__main__":
    main()
