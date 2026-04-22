"""4-panel diagnostic: the full CfD cost mechanism, exposed.

Volume × price gap = bill. Each panel is a direct consequence of the
one above it.

Panel 1 — Monthly generation (TWh): the volume multiplier. Fleet
growth and seasonal wind signal visible.

Panel 2 — Unit prices (£/MWh): fleet-weighted average strike price
vs generation-weighted monthly gas counterfactual. The shaded gap
between them is the per-MWh cost of the policy.

Panel 3 — Premium per MWh (£/MWh): strike − counterfactual. Red when
consumers overpay, green when the scheme is genuinely cheaper than
gas. Watch 2022 dip toward zero.

Panel 4 — Cumulative premium (£bn): running total of
(premium × generation) since the scheme began. This is the bill.

Sources: LCCC "Actual CfD Generation", ONS gas prices, UK ETS carbon
prices, BEIS Electricity Generation Costs 2023 for CCGT opex.
"""

import pandas as pd
import plotly.graph_objects as go

from uk_subsidy_tracker.counterfactual import compute_counterfactual
from uk_subsidy_tracker.data import load_lccc_dataset
from uk_subsidy_tracker.plotting import ChartBuilder


def _prepare() -> pd.DataFrame:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df = df.dropna(subset=["CFD_Generation_MWh", "Strike_Price_GBP_Per_MWh"])
    df = df[df["CFD_Generation_MWh"] > 0]

    cf_daily = compute_counterfactual().set_index("date")["counterfactual_total"]

    # Aggregate to day level: generation-weighted strike, generation, and
    # counterfactual £/MWh (aligned on Settlement_Date).
    df["strike_x_gen"] = df["Strike_Price_GBP_Per_MWh"] * df["CFD_Generation_MWh"]
    daily = df.groupby("Settlement_Date").agg(
        gen=("CFD_Generation_MWh", "sum"),
        strike_x_gen=("strike_x_gen", "sum"),
    )
    daily["strike"] = daily["strike_x_gen"] / daily["gen"]
    daily["counterfactual"] = cf_daily.reindex(daily.index)
    daily = daily.dropna(subset=["counterfactual"])
    daily["premium_per_mwh"] = daily["strike"] - daily["counterfactual"]
    daily["cf_x_gen"] = daily["counterfactual"] * daily["gen"]
    daily["premium_gbp"] = daily["premium_per_mwh"] * daily["gen"]

    daily["month"] = daily.index.to_period("M").to_timestamp()

    monthly = daily.groupby("month").agg(
        gen=("gen", "sum"),
        strike_x_gen=("strike_x_gen", "sum"),
        cf_x_gen=("cf_x_gen", "sum"),
        premium_gbp=("premium_gbp", "sum"),
    )
    monthly["strike"] = monthly["strike_x_gen"] / monthly["gen"]
    monthly["counterfactual"] = monthly["cf_x_gen"] / monthly["gen"]
    monthly["premium_per_mwh"] = monthly["strike"] - monthly["counterfactual"]
    monthly["cumulative_premium_bn"] = monthly["premium_gbp"].cumsum() / 1e9

    return monthly


def main() -> None:
    m = _prepare()
    total_bn = m["cumulative_premium_bn"].iloc[-1]

    builder = ChartBuilder(
        title="The CfD mechanism — volume × price gap = bill",
        height=1100,
    )
    fig = builder.create_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        subplot_titles=[
            "[1] Monthly generation (TWh) — the volume multiplier",
            "[2] Unit prices (£/MWh) — fleet-weighted strike price vs gas alternative",
            "[3] Premium per MWh (£/MWh) — what consumers overpay for each unit",
            f"[4] Cumulative premium (£bn) — £{total_bn:.1f}bn to date",
        ],
        vertical_spacing=0.06,
    )

    # Left-align the subplot titles so they can be referenced as [1]–[4].
    for ann in fig.layout.annotations[:4]:
        ann.update(xanchor="left", x=0.0)

    # Panel 1 — Generation volume
    fig.add_trace(
        go.Bar(
            x=m.index,
            y=m["gen"] / 1e6,
            name="Generation",
            marker_color="#9ca3af",
            hovertemplate="%{x|%b %Y}<br>%{y:.2f} TWh<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # Panel 2 — Prices: strike and gas counterfactual
    fig.add_trace(
        go.Scatter(
            x=m.index,
            y=m["counterfactual"],
            name="Gas alternative",
            mode="lines",
            line={"color": "#ff7f0e", "width": 2.5},
            hovertemplate="Gas alt<br>%{x|%b %Y}<br>£%{y:.0f}/MWh<extra></extra>",
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=m.index,
            y=m["strike"],
            name="Fleet-weighted strike price",
            mode="lines",
            line={"color": "#1f77b4", "width": 3},
            fill="tonexty",
            fillcolor="rgba(31,119,180,0.15)",
            hovertemplate="Strike<br>%{x|%b %Y}<br>£%{y:.0f}/MWh<extra></extra>",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # Direct annotations on Panel 2 at the right end of each line
    last_x = m.index[-1]
    fig.add_annotation(
        text="<b>Strike price</b>",
        x=last_x,
        y=m["strike"].iloc[-1],
        xanchor="left",
        yanchor="middle",
        xshift=6,
        showarrow=False,
        font={"color": "#1f77b4", "size": 12},
        row=2,
        col=1,
    )
    fig.add_annotation(
        text="<b>Gas alternative</b>",
        x=last_x,
        y=m["counterfactual"].iloc[-1],
        xanchor="left",
        yanchor="middle",
        xshift=6,
        showarrow=False,
        font={"color": "#ff7f0e", "size": 12},
        row=2,
        col=1,
    )

    # Panel 3 — Premium per MWh
    premium_colors = [
        "#d62728" if v >= 0 else "#2ca02c" for v in m["premium_per_mwh"].values
    ]
    fig.add_trace(
        go.Bar(
            x=m.index,
            y=m["premium_per_mwh"],
            name="Premium per MWh",
            marker_color=premium_colors,
            hovertemplate="%{x|%b %Y}<br>£%{y:+.0f}/MWh<extra></extra>",
            showlegend=False,
        ),
        row=3,
        col=1,
    )
    fig.add_hline(y=0, line_color="#9ca3af", line_width=1, row=3, col=1)

    # Panel 4 — Cumulative premium £bn
    fig.add_trace(
        go.Scatter(
            x=m.index,
            y=m["cumulative_premium_bn"],
            name="Cumulative premium",
            mode="lines",
            line={"color": "#d62728", "width": 2.5},
            fill="tozeroy",
            fillcolor="rgba(214,39,40,0.25)",
            hovertemplate="%{x|%b %Y}<br>£%{y:.1f}bn<extra></extra>",
            showlegend=False,
        ),
        row=4,
        col=1,
    )

    # Label the final cumulative premium on panel 4.
    fig.add_annotation(
        text=f"<b>£{total_bn:.1f}bn</b>",
        x=last_x,
        y=total_bn,
        xanchor="left",
        yanchor="middle",
        xshift=6,
        showarrow=False,
        font={"color": "#d62728", "size": 13},
        row=4,
        col=1,
    )

    fig.update_layout(hovermode="x unified")

    # Axis titles carry the units; tick labels stay unadorned.
    fig.update_yaxes(title_text="TWh", row=1, col=1)
    builder.format_currency_axis(
        fig, axis="y", prefix="", suffix="", title="£/MWh", row=2, col=1
    )
    fig.update_yaxes(rangemode="tozero", row=2, col=1)
    builder.format_currency_axis(
        fig, axis="y", prefix="", suffix="", title="£/MWh", row=3, col=1
    )
    builder.format_currency_axis(
        fig, axis="y", prefix="", suffix="", title="£ billions", row=4, col=1
    )

    # Breathing room: push y-axis titles and tick labels away from the axis
    # line, and widen the left / bottom margins so nothing crowds.
    fig.update_yaxes(title_standoff=25, ticklabelstandoff=8)
    fig.update_xaxes(ticklabelstandoff=8)
    fig.update_layout(margin={"l": 100, "b": 70})

    builder.save(fig, "subsidy_cfd_dynamics", export_twitter=True)


if __name__ == "__main__":
    main()
