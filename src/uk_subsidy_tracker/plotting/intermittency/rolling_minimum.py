"""Rolling 21-day capacity factor — wind and solar drought detection.

Shows sustained output droughts in any rolling 21-day window.
Wind and solar on separate panels with independent y-axes.
Three weeks is beyond what any deployed battery storage can cover.

Sources: LCCC "Actual CfD Generation" and "CfD Contract Portfolio Status".
Methodology:
- Daily CF = sum(generation MWh) / (installed capacity MW × 24).
- Installed capacity derived from first generation date per unit.
- Rolling 21-day mean of daily CF plotted as time series.
- Current incomplete month excluded to avoid partial-data bias.
- Wind and solar on separate panels — their drought patterns differ
  (wind droughts are summer high-pressure; solar droughts are winter).

Trough detection:
- Significant droughts are identified using scipy.signal.find_peaks on
  the inverted (negated) rolling CF signal.
- A minimum prominence of 15 percentage points is required — meaning
  the CF must recover by at least 15pp before a new trough is counted.
  This is analogous to the topographic prominence used in mountain
  classification (e.g. Munros): a dip only counts as a separate event
  if it is separated from neighbouring dips by a meaningful recovery.
- Only troughs that fall below the technology's reference CF line are
  marked (wind: 20%, solar: 5%).
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.signal import find_peaks

from uk_subsidy_tracker.data import load_lccc_dataset
from uk_subsidy_tracker.plotting import ChartBuilder

WINDOW = 21

TECH_GROUPS = {
    "Wind": {
        "types": ["Offshore Wind", "Onshore Wind"],
        "filter": "Wind",
        "color": "#1f77b4",
        "ref_cf": 0.20,
    },
    "Solar": {
        "types": ["Solar PV"],
        "filter": "Solar",
        "color": "#ff7f0e",
        "ref_cf": 0.05,
    },
}


def _installed_capacity_by_date(
    df: pd.DataFrame,
    df_cap: pd.DataFrame,
    tech_types: list[str],
) -> pd.Series:
    cap = df_cap[df_cap["Technology_Type"].isin(tech_types)]
    unit_cap = cap.groupby("CfD_ID")["Maximum_Contract_Capacity_MW"].sum()

    gen = df[df["CfD_ID"].isin(unit_cap.index)]
    first_gen = gen.groupby("CfD_ID")["Settlement_Date"].min().rename("start_date")
    unit_info = pd.concat([first_gen, unit_cap], axis=1).dropna()

    all_dates = pd.date_range(
        gen["Settlement_Date"].min(), gen["Settlement_Date"].max()
    )
    cap_by_date = np.zeros(len(all_dates))
    for _, row in unit_info.iterrows():
        mask = all_dates >= row["start_date"]
        cap_by_date[mask] += row["Maximum_Contract_Capacity_MW"]
    return pd.Series(cap_by_date, index=all_dates)


def _compute_daily_cf(
    df: pd.DataFrame,
    df_cap: pd.DataFrame,
    tech_filter: str,
    tech_types: list[str],
) -> pd.Series:
    tech_df = df[df["Technology"].str.contains(tech_filter, na=False)]
    daily_gen = (
        tech_df.groupby("Settlement_Date")["CFD_Generation_MWh"].sum().sort_index()
    )

    installed = _installed_capacity_by_date(df, df_cap, tech_types)
    daily_cf = daily_gen / (installed.reindex(daily_gen.index) * 24)

    current_month = pd.Timestamp.now().to_period("M")
    daily_cf = daily_cf[daily_cf.index.to_period("M") < current_month]
    return daily_cf


def main() -> None:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df_cap = load_lccc_dataset("CfD Contract Portfolio Status")
    df_cap = df_cap.rename(columns={"CFD_ID": "CfD_ID"})

    panels = list(TECH_GROUPS.keys())
    builder = ChartBuilder(
        title=f"CfD Rolling {WINDOW}-Day Capacity Factor — Wind and Solar",
        height=800,
    )
    fig = builder.create_subplots(
        rows=len(panels),
        cols=1,
        shared_xaxes=True,
        subplot_titles=[
            f"{name} — Rolling {WINDOW}-Day Capacity Factor" for name in panels
        ],
        vertical_spacing=0.08,
    )

    for row_idx, (tech_name, cfg) in enumerate(TECH_GROUPS.items(), start=1):
        daily_cf = _compute_daily_cf(df, df_cap, cfg["filter"], cfg["types"])
        rolling = daily_cf.rolling(WINDOW).mean().dropna()

        fig.add_trace(
            go.Scatter(
                x=daily_cf.index,
                y=daily_cf.values,
                mode="lines",
                line={"color": "rgba(180,180,180,0.3)", "width": 0.5},
                showlegend=False,
                hovertemplate=f"{tech_name}<br>%{{x|%b %d %Y}}<br>CF: %{{y:.1%}}<extra></extra>",
            ),
            row=row_idx,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=rolling.index,
                y=rolling.values,
                mode="lines",
                line={"color": cfg["color"], "width": 1.5},
                showlegend=False,
                hovertemplate=f"{tech_name} {WINDOW}d<br>%{{x|%b %d %Y}}<br>CF: %{{y:.1%}}<extra></extra>",
            ),
            row=row_idx,
            col=1,
        )

        inverted = -rolling.values
        peaks, props = find_peaks(inverted, prominence=0.15)

        positions = ["bottom left", "bottom right"]
        marker_count = 0
        for i, p in enumerate(peaks):
            worst_val = rolling.values[p]
            if worst_val > cfg["ref_cf"]:
                continue
            worst_date = rolling.index[p]
            worst_start = worst_date - pd.Timedelta(days=WINDOW - 1)
            fig.add_trace(
                go.Scatter(
                    x=[worst_date],
                    y=[worst_val],
                    mode="markers+text",
                    marker={"size": 10, "color": "red", "symbol": "diamond"},
                    text=[f"{worst_val:.0%}"],
                    textposition=positions[marker_count % 2],
                    textfont={"size": 9, "color": "red"},
                    showlegend=False,
                    hovertemplate=(
                        f"Drought ending {worst_date.strftime('%b %d %Y')}<br>"
                        f"{worst_start.strftime('%b %d')}–{worst_date.strftime('%b %d %Y')}<br>"
                        f"CF: {worst_val:.1%}<br>"
                        f"Prominence: {props['prominences'][i]:.1%}<extra></extra>"
                    ),
                ),
                row=row_idx,
                col=1,
            )
            marker_count += 1

        fig.add_hline(
            y=cfg["ref_cf"],
            line_dash="dot",
            line_color="red",
            line_width=1,
            annotation_text=f"{cfg['ref_cf']:.0%} CF",
            annotation_position="bottom right",
            annotation_font_size=10,
            row=row_idx,
            col=1,
        )

    for row_idx in range(1, len(panels) + 1):
        fig.update_yaxes(
            title="Capacity Factor",
            tickformat=".0%",
            rangemode="tozero",
            row=row_idx,
            col=1,
        )

    fig.update_xaxes(dtick="M12", tickformat="%Y")

    builder.save(fig, "intermittency_rolling_minimum", export_twitter=True)


if __name__ == "__main__":
    main()
