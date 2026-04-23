"""RO dynamics — S2 flagship 4-panel chart.

Panels (CY x-axis per D-07):
  [1] Annual ROC-eligible generation (TWh, GB-only per D-12).
  [2] ROC price (£/ROC) — buyout + recycle primary plus e-ROC sensitivity
      overlay visualising the D-02 "2-10% convention-choice weight" band.
  [3] Premium per MWh (£/MWh) — (ro_cost - gas_counterfactual) / generation.
  [4] Cumulative RO bill (£bn) with visible mutualisation spike on
      obligation year 2021-22 (D-11).

Filename: ``subsidy_ro_dynamics`` per RO-MODULE-SPEC Appendix A.

Data source: ``data/derived/ro/station_month.parquet`` (Plan 05-05). GB rows
only per D-12; the chart is robust to an empty upstream — when the stub seed
produces a zero-row Parquet (pre-Plan 05-13) the chart emits a titled
placeholder rather than raising, so the plotting orchestrator (`__main__`)
still succeeds under CI.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pyarrow.parquet as pq

from uk_subsidy_tracker.plotting import ChartBuilder
from uk_subsidy_tracker.schemes import ro


def _prepare() -> pd.DataFrame:
    """Read station_month.parquet, restrict to GB rows, aggregate to CY.

    Columns returned:
      cy, generation_twh, cost_gbp, cost_eroc_gbp, counterfactual_gbp,
      premium_gbp, mutualisation_gbp, cumulative_bn, premium_per_mwh,
      roc_price_buyout_recycle (proxy £/ROC), roc_price_eroc (proxy).
    """
    sm_path = ro.DERIVED_DIR / "station_month.parquet"
    if not sm_path.exists():
        return pd.DataFrame()

    sm = pq.read_table(sm_path).to_pandas()
    if len(sm) == 0:
        return sm

    # D-12 — GB-only headline.
    gb = sm[sm["country"] == "GB"].copy()
    if len(gb) == 0:
        return gb

    gb["cy"] = pd.to_datetime(gb["month_end"]).dt.year.astype("int64")

    annual = gb.groupby("cy", sort=True, observed=True).agg(
        generation_mwh=("generation_mwh", "sum"),
        rocs_issued=("rocs_issued", "sum"),
        cost_gbp=("ro_cost_gbp", "sum"),
        cost_eroc_gbp=("ro_cost_gbp_eroc", "sum"),
        counterfactual_gbp=("gas_counterfactual_gbp", "sum"),
        premium_gbp=("premium_gbp", "sum"),
        mutualisation_gbp=("mutualisation_gbp", "sum"),
    ).reset_index()

    annual["generation_twh"] = annual["generation_mwh"] / 1e6
    annual["cumulative_bn"] = annual["cost_gbp"].cumsum() / 1e9

    # premium per MWh of generation (avoid div-by-zero on stub data).
    gen_mwh = annual["generation_mwh"].where(annual["generation_mwh"] > 0)
    annual["premium_per_mwh"] = annual["premium_gbp"] / gen_mwh

    # Proxy £/ROC series for Panel 2. Real columns absent on station_month
    # (buyout + recycle price is carried on upstream roc-prices.csv and
    # embedded into ro_cost_gbp multiplicatively); surface a generation-
    # weighted proxy = total cost / total ROCs. Gated by rocs_issued > 0
    # so the stub-data path does not divide by zero.
    rocs = annual["rocs_issued"].where(annual["rocs_issued"] > 0)
    annual["roc_price_buyout_recycle"] = annual["cost_gbp"] / rocs
    annual["roc_price_eroc"] = annual["cost_eroc_gbp"] / rocs

    return annual


def _placeholder(builder: ChartBuilder) -> go.Figure:
    """Titled single-panel placeholder for the empty-stub path.

    Matches the D-02 "chart files emit without raising on stub data" contract
    so ``python -m uk_subsidy_tracker.plotting`` succeeds under CI pre-5-13.
    """
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
    df = _prepare()

    if len(df) == 0:
        builder = ChartBuilder(
            title="The RO mechanism — ROCs × ROC-price = consumer bill",
            height=500,
        )
        fig = _placeholder(builder)
        builder.save(fig, "subsidy_ro_dynamics", export_twitter=True)
        return

    total_bn = float(df["cumulative_bn"].iloc[-1]) if len(df) else 0.0

    builder = ChartBuilder(
        title="The RO mechanism — ROCs × ROC-price = consumer bill",
        height=1100,
    )
    fig = builder.create_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        subplot_titles=[
            "[1] Annual ROC-eligible generation (TWh, GB-only)",
            "[2] ROC price (£/ROC) — buyout + recycle vs e-ROC sensitivity",
            "[3] Premium per MWh (£/MWh) — consumer overpayment vs gas counterfactual",
            f"[4] Cumulative RO bill (£bn) — £{total_bn:.1f}bn to date; "
            "mutualisation spike visible OY 2021-22",
        ],
        vertical_spacing=0.06,
    )

    # Left-align subplot titles so they can be referenced as [1]-[4].
    for ann in fig.layout.annotations[:4]:
        ann.update(xanchor="left", x=0.0)

    # Panel 1 — annual generation (TWh) bars.
    fig.add_trace(
        go.Bar(
            x=df["cy"],
            y=df["generation_twh"],
            name="Generation",
            marker_color="#9ca3af",
            hovertemplate="%{x}<br>%{y:.1f} TWh<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # Panel 2 — buyout + recycle line with e-ROC sensitivity fill.
    fig.add_trace(
        go.Scatter(
            x=df["cy"],
            y=df["roc_price_buyout_recycle"],
            mode="lines+markers",
            name="buyout + recycle",
            line={"color": "#1f77b4", "width": 2.5},
            hovertemplate="buyout + recycle<br>%{x}<br>£%{y:.0f}/ROC<extra></extra>",
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["cy"],
            y=df["roc_price_eroc"],
            mode="lines",
            name="e-ROC sensitivity",
            line={"color": "#ff7f0e", "width": 1.5, "dash": "dot"},
            fill="tonexty",
            fillcolor="rgba(255,127,14,0.12)",
            hovertemplate="e-ROC<br>%{x}<br>£%{y:.0f}/ROC<extra></extra>",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # Panel 3 — premium per MWh.
    premium_colors = [
        "#d62728" if (v is not None and v >= 0) else "#2ca02c"
        for v in df["premium_per_mwh"].values
    ]
    fig.add_trace(
        go.Bar(
            x=df["cy"],
            y=df["premium_per_mwh"],
            name="Premium",
            marker_color=premium_colors,
            hovertemplate="%{x}<br>£%{y:+.0f}/MWh<extra></extra>",
            showlegend=False,
        ),
        row=3,
        col=1,
    )
    fig.add_hline(y=0, line_color="#9ca3af", line_width=1, row=3, col=1)

    # Panel 4 — cumulative £bn + mutualisation annotation on spike years.
    fig.add_trace(
        go.Scatter(
            x=df["cy"],
            y=df["cumulative_bn"],
            mode="lines+markers",
            name="Cumulative",
            line={"color": "#d62728", "width": 2.5},
            fill="tozeroy",
            fillcolor="rgba(214,39,40,0.25)",
            hovertemplate="%{x}<br>£%{y:.1f}bn<extra></extra>",
            showlegend=False,
        ),
        row=4,
        col=1,
    )

    # Mutualisation spike annotation — D-11 verified non-null for 2021-22 only.
    mut_col = df["mutualisation_gbp"].fillna(0)
    for idx in df.index[mut_col > 0].tolist():
        year = int(df.loc[idx, "cy"])
        mut_m = float(df.loc[idx, "mutualisation_gbp"]) / 1e6
        fig.add_annotation(
            x=year,
            y=float(df.loc[idx, "cumulative_bn"]),
            text=f"£{mut_m:.0f}M mutualisation (SY 2021-22)",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
            font={"size": 10, "color": "#d62728"},
            row=4,
            col=1,
        )

    # GB-only annotation on Panel 1 — T-5.08-02 mitigation (NIRO framing).
    fig.add_annotation(
        text="GB-only; NIRO rows available via country='NI' filter in Parquet",
        xref="paper",
        yref="paper",
        x=0.0,
        y=1.04,
        xanchor="left",
        yanchor="bottom",
        showarrow=False,
        font={"size": 9, "color": "#9ca3af"},
    )

    fig.update_layout(hovermode="x unified")

    fig.update_yaxes(title_text="TWh", row=1, col=1)
    builder.format_currency_axis(
        fig, axis="y", prefix="", suffix="", title="£/ROC", row=2, col=1
    )
    builder.format_currency_axis(
        fig, axis="y", prefix="", suffix="", title="£/MWh", row=3, col=1
    )
    builder.format_currency_axis(
        fig, axis="y", prefix="", suffix="", title="£ billions", row=4, col=1
    )
    fig.update_yaxes(title_standoff=25, ticklabelstandoff=8)
    fig.update_xaxes(ticklabelstandoff=8)
    fig.update_layout(margin={"l": 100, "b": 70})

    builder.save(fig, "subsidy_ro_dynamics", export_twitter=True)


if __name__ == "__main__":
    main()
