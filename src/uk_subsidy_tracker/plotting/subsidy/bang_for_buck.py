"""Bang-for-buck scatter — subsidy received vs CO2 avoided per project.

Each dot is a CfD unit. X = total levy payments received (£m),
Y = total CO2 avoided (kt). Projects in the top-left are good value;
bottom-right are bad value. Dot size = total generation (GWh).
Colour = allocation round.

The UK ETS carbon price (£50/tCO2) divides the chart into green
("worth it" — avoided carbon for less than the market price) and red
("not worth it" — paid more per tonne than carbon costs on the open
market) zones. Log scales spread the clustered small projects.

Sources: LCCC "Actual CfD Generation and avoided GHG emissions".
Methodology:
- Subsidy = sum(CFD_Payments_GBP) per unit — the actual levy payment
  (strike - market) × generation, not the total electricity cost.
- CO2 avoided = sum(Avoided_GHG_tonnes_CO2e) per unit.
- Units with negative total payments (net clawback over lifetime) are
  excluded — they received no net subsidy so £/tCO2 is meaningless.
- Units with < 100 GWh total generation excluded to remove noise from
  newly commissioned projects.
"""

import numpy as np
import plotly.graph_objects as go

from uk_subsidy_tracker.data import load_lccc_dataset
from uk_subsidy_tracker.plotting import ChartBuilder

MIN_GEN_MWH = 100_000


def main() -> None:
    # === Data Preparation (unchanged) ===
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")

    by_unit = (
        df.groupby(["Name_of_CfD_Unit", "Allocation_round"])
        .agg(
            payments=("CFD_Payments_GBP", "sum"),
            co2=("Avoided_GHG_tonnes_CO2e", "sum"),
            gen=("CFD_Generation_MWh", "sum"),
        )
        .reset_index()
    )

    by_unit = by_unit[(by_unit["payments"] > 0) & (by_unit["gen"] >= MIN_GEN_MWH)]
    by_unit["payments_m"] = by_unit["payments"] / 1e6
    by_unit["co2_kt"] = by_unit["co2"] / 1e3
    by_unit["gen_gwh"] = by_unit["gen"] / 1e3

    x_lo = by_unit["payments_m"].min() * 0.3
    x_hi = by_unit["payments_m"].max() * 3
    y_lo = by_unit["co2_kt"].min() * 0.3
    y_hi = by_unit["co2_kt"].max() * 3

    # Sample many points along ETS line so polygon follows log curvature
    xs = np.geomspace(x_lo, x_hi, 200)
    ets_ys = xs * 20  # y = x / 50 * 1000

    # === Chart Creation (NEW: using ChartBuilder) ===
    builder = ChartBuilder(
        title="Bang for Buck — subsidy received vs CO₂ avoided per CfD project",
        height=750,
    )

    # Create figure with dark theme automatically applied
    fig = builder.create_basic()

    # Get allocation round colors from builder
    round_colors = builder.get_allocation_round_colors()
    semantic_colors = builder.get_semantic_colors()

    # Green zone (above ETS line — good value)
    fig.add_trace(
        go.Scatter(
            x=xs.tolist() + [x_hi, x_lo],
            y=ets_ys.tolist() + [y_hi, y_hi],
            fill="toself",
            fillcolor="rgba(44,160,44,0.12)",
            line={"width": 0},
            name="Good value (< £50/tCO₂)",
            hoverinfo="skip",
        )
    )

    # Red zone (below ETS line — bad value)
    fig.add_trace(
        go.Scatter(
            x=xs.tolist() + [x_hi, x_lo],
            y=ets_ys.tolist() + [y_lo, y_lo],
            fill="toself",
            fillcolor="rgba(214,39,40,0.12)",
            line={"width": 0},
            name="Bad value (> £50/tCO₂)",
            hoverinfo="skip",
        )
    )

    # ETS reference line (using semantic color)
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ets_ys,
            mode="lines",
            line={"color": semantic_colors["negative"], "width": 2, "dash": "dash"},
            name="UK ETS carbon price (£50/tCO₂)",
            hoverinfo="skip",
        )
    )

    # Scatter points by allocation round (using builder's color palette)
    for ar, color in round_colors.items():
        ar_data = by_unit[by_unit["Allocation_round"] == ar]
        if ar_data.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=ar_data["payments_m"],
                y=ar_data["co2_kt"],
                mode="markers",
                name=ar,
                marker={
                    "color": color,
                    "size": np.clip(ar_data["gen_gwh"] / 2 + 5, 8, 40),
                    "opacity": 0.8,
                    "line": {"width": 1, "color": "white"},
                },
                text=ar_data["Name_of_CfD_Unit"],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    f"{ar}<br>"
                    "Subsidy: £%{x:.0f}m<br>"
                    "CO₂ avoided: %{y:.0f} kt<extra></extra>"
                ),
            )
        )

    # Label key outliers only
    labels = by_unit.nlargest(3, "payments_m")
    fig.add_trace(
        go.Scatter(
            x=labels["payments_m"],
            y=labels["co2_kt"],
            mode="text",
            text=labels["Name_of_CfD_Unit"]
            .str.replace(" Offshore Wind Farm", "", regex=False)
            .str.replace(" Phase ", " P", regex=False)
            .str.replace("3rd conversion unit (unit 1)", "", regex=False),
            textposition="top center",
            textfont={"size": 9, "color": "#e8e8e8"},  # Light text for dark theme
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # === Axis Formatting (NEW: using builder helper methods) ===
    # X-axis: Currency formatting with log scale
    builder.format_currency_axis(
        fig,
        axis="x",
        suffix="m",
        title="Total subsidy received (£m)",
    )
    fig.update_xaxes(type="log", range=[np.log10(x_lo), np.log10(x_hi)])

    # Y-axis: No currency prefix, just suffix
    builder.format_currency_axis(
        fig,
        axis="y",
        prefix="",
        suffix=" kt",
        title="Total CO₂ avoided (kt)",
    )
    fig.update_yaxes(type="log", range=[np.log10(y_lo), np.log10(y_hi)])

    # Additional layout settings
    fig.update_layout(hovermode="closest")

    # === Save (NEW: exports both HTML and Twitter PNG) ===
    paths = builder.save(fig, "subsidy_bang_for_buck", export_twitter=True)


if __name__ == "__main__":
    main()
