"""RO forward projection — S5 drawdown to 2037.

Mirrors ``plotting/subsidy/remaining_obligations.py`` (CfD) but simpler:

- **No NESO-growth scenario** — RO closed to new accreditations 2017-03-31
  (SI 2017/1084), so there is no growth multiplier to apply. Projection is
  purely drawdown of the existing fleet's 20-year support windows.
- **Hard cap on 2037** — RO scheme closes 2037-03-31 for the final cohort
  of 20-year accreditations from 2017.
- **Colour-keyed by technology** (not allocation round) to match
  ``ro_by_technology``'s stacking convention.

Layout: 2-panel single column (annual £bn/yr, cumulative £bn) — CfD's
2×2 scenario grid collapses to a single column since no growth axis.

Filename: ``subsidy_ro_forward_projection`` per RO-MODULE-SPEC Appendix A.

Data source: ``data/derived/ro/forward_projection.parquet`` (Plan 05-05).
Robust to empty upstream — emits a titled placeholder.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pyarrow.parquet as pq

from uk_subsidy_tracker.plotting import ChartBuilder
from uk_subsidy_tracker.schemes import ro

# Technology colour keys — aligned with ro_by_technology.CATEGORIES so the
# RO chart family reads consistently (D-02 visual-consistency guard).
TECHNOLOGY_COLORS: dict[str, str] = {
    "Offshore wind": "#1f77b4",
    "Onshore wind": "#6baed6",
    "Dedicated biomass": "#8c564b",
    "Co-firing biomass": "#d62728",
    "Solar PV": "#ff7f0e",
}

RO_SCHEME_END_YEAR = 2037


def _prepare() -> pd.DataFrame:
    path = ro.DERIVED_DIR / "forward_projection.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pq.read_table(path).to_pandas()


def _placeholder(builder: ChartBuilder) -> go.Figure:
    fig = builder.create_basic()
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        text=(
            "<b>No RO data yet</b><br><br>"
            "data/derived/ro/forward_projection.parquet is empty.<br>"
            "Regenerate after Ofgem RER URLs are plumbed (Plan 05-13)."
        ),
        showarrow=False,
        font={"size": 14, "color": "#9ca3af"},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def main() -> None:
    fp = _prepare()

    if len(fp) == 0:
        builder = ChartBuilder(
            title="RO forward-committed obligations to 2037",
            height=500,
        )
        fig = _placeholder(builder)
        builder.save(fig, "subsidy_ro_forward_projection", export_twitter=True)
        return

    # Cap at the scheme end year — belt-and-braces even though the upstream
    # forward_projection builder already applies the 2037 ceiling.
    fp = fp[fp["year"] <= RO_SCHEME_END_YEAR].copy()
    fp["cost_bn"] = fp["remaining_cost_gbp"] / 1e9

    annual_total = (
        fp.groupby("year", sort=True, observed=True)["cost_bn"].sum().reset_index()
    )
    annual_total["cum_bn"] = annual_total["cost_bn"].cumsum()
    total_bn = float(annual_total["cost_bn"].sum())

    builder = ChartBuilder(
        title=(
            "RO Forward-Committed Obligations — drawdown to 2037 "
            "(scheme closed to new accreditations)"
        ),
        height=800,
    )
    fig = builder.create_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=[
            f"[1] Annual £bn/yr by technology — £{total_bn:.1f}bn remaining",
            "[2] Cumulative remaining bill (£bn)",
        ],
        vertical_spacing=0.08,
    )
    for ann in fig.layout.annotations[:2]:
        ann.update(xanchor="left", x=0.0)

    # Panel 1 — stacked bars by technology (fall back to "Other" colour for
    # any technology not in the colour map).
    tech_keys = [t for t in TECHNOLOGY_COLORS if t in fp["technology"].unique()]
    other_techs = sorted(set(fp["technology"].unique()) - set(tech_keys))
    for tech in tech_keys + other_techs:
        sub = fp[fp["technology"] == tech].groupby("year", sort=True)["cost_bn"].sum()
        if sub.empty:
            continue
        color = TECHNOLOGY_COLORS.get(tech, "#2ca02c")
        fig.add_trace(
            go.Bar(
                x=sub.index,
                y=sub.values,
                name=tech,
                marker_color=color,
                hovertemplate=f"{tech}<br>%{{x}}<br>£%{{y:.2f}}bn<extra></extra>",
            ),
            row=1,
            col=1,
        )

    # Panel 2 — cumulative total line.
    fig.add_trace(
        go.Scatter(
            x=annual_total["year"],
            y=annual_total["cum_bn"],
            mode="lines+markers",
            name="Cumulative",
            line={"color": "#d62728", "width": 2.5},
            fill="tozeroy",
            fillcolor="rgba(214,39,40,0.25)",
            hovertemplate="%{x}<br>£%{y:.1f}bn<extra></extra>",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # 2037 scheme-end marker on both panels.
    fig.add_vline(
        x=RO_SCHEME_END_YEAR,
        line={"color": "red", "dash": "dot", "width": 1.5},
        annotation_text="2037 scheme close",
        annotation_position="top right",
        row=1,
        col=1,
    )
    fig.add_vline(
        x=RO_SCHEME_END_YEAR,
        line={"color": "red", "dash": "dot", "width": 1.5},
        row=2,
        col=1,
    )

    fig.update_layout(barmode="stack", hovermode="x unified")
    builder.format_currency_axis(
        fig, axis="y", suffix="bn", tickformat=".1f", title="£bn/yr", row=1, col=1
    )
    builder.format_currency_axis(
        fig, axis="y", suffix="bn", tickformat=".0f", title="Cumulative £bn", row=2, col=1
    )
    fig.update_xaxes(title="Year", dtick=2, row=2, col=1)

    builder.save(fig, "subsidy_ro_forward_projection", export_twitter=True)


if __name__ == "__main__":
    main()
