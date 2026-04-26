"""X5 — 2022 gas-crisis comparison: grouped bars per scheme for premium-per-MWh.

Reproduces the cfd.md "7% more in 2022" insight cross-scheme. Three grouped
bars per scheme for years 2021/2022/2023. Schemes without a gas counterfactual
(CM, Balancing, Grid) are excluded per D-16 — listed in :data:`EXCLUDED_SCHEMES`.
NaN-generation rows are dropped. REQUIREMENT X-05.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pyarrow.parquet as pq

from uk_subsidy_tracker.plotting import ChartBuilder
from uk_subsidy_tracker.schemes import portal

# D-16: schemes without gas counterfactual are excluded from X4 + X5.
# No-op in Phase 6 (these schemes ship in Phases 9-11); armed for the future.
EXCLUDED_SCHEMES: frozenset[str] = frozenset({
    "Capacity Market",
    "Balancing Services",
    "Grid Socialisation",
})

# UI-SPEC §"Open items for planner" Q4 chronological order: 2021 / 2022 / 2023.
CRISIS_YEARS: tuple[int, ...] = (2021, 2022, 2023)

# Color per crisis year. 2022 emphasised as the crisis-year via red;
# 2021/2023 = adjacent context (subtitle-grey).
YEAR_COLORS: dict[int, str] = {
    2021: "#a0a4b8",  # subtitle-grey (pre-crisis context)
    2022: "#d62728",  # red (crisis emphasis)
    2023: "#a0a4b8",  # subtitle-grey (post-crisis context)
}


def _prepare() -> pd.DataFrame:
    """Read cross_scheme.parquet, filter to crisis-year window, compute premium per MWh.

    Returns long-format frame with ``premium_per_mwh`` column. Empty DataFrame
    returned when the parquet is absent or zero-row, so ``main()`` can short-
    circuit to the placeholder figure.
    """
    src = portal.DERIVED_DIR / "cross_scheme.parquet"
    if not src.exists():
        return pd.DataFrame()
    df = pq.read_table(src).to_pandas()
    if len(df) == 0:
        return df
    # D-16: omit no-gas-counterfactual schemes (no-op in Phase 6).
    df = df[~df["scheme"].isin(EXCLUDED_SCHEMES)]
    # Filter to crisis-year window per UI-SPEC Q4 chronological order.
    df = df[df["year"].isin(CRISIS_YEARS)].copy()
    # NaN-generation guard (HAZARD #2 from cross_scheme schema).
    df = df[df["generation_mwh"].notna() & (df["generation_mwh"] > 0)].copy()
    df["premium_per_mwh"] = df["premium_gbp"] / df["generation_mwh"]
    return df


def _placeholder(builder: ChartBuilder) -> go.Figure:
    """Titled single-panel placeholder for the empty-substrate path."""
    fig = builder.create_basic()
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        text=(
            "<b>No 2022-crisis comparison data yet</b><br><br>"
            "data/derived/portal/cross_scheme.parquet has no rows for "
            "2021/2022/2023 with valid generation MWh."
        ),
        showarrow=False,
        font={"size": 14, "color": "#9ca3af"},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def main() -> None:
    df = _prepare()
    builder = ChartBuilder(
        title="2022 gas crisis — premium per MWh by scheme",
        height=600,
    )
    if df.empty:
        fig = _placeholder(builder)
        builder.save(fig, "x5_2022_crisis", export_twitter=True)
        return

    fig = builder.create_basic()
    # One trace per crisis year; x-axis = scheme; y = premium_per_mwh.
    # Chronological order per UI-SPEC §"Open items for planner" Q4
    # (2021 / 2022 / 2023) preserved by iterating CRISIS_YEARS in declaration
    # order — Plotly groups bars in trace-order.
    for year in CRISIS_YEARS:
        sub = df[df["year"] == year]
        if sub.empty:
            continue
        fig.add_trace(
            go.Bar(
                x=sub["scheme"],
                y=sub["premium_per_mwh"],
                name=str(year),
                marker_color=YEAR_COLORS[year],
                hovertemplate=(
                    "%{x} "
                    + str(year)
                    + "<br>£%{y:.1f}/MWh<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        barmode="group",
        title=dict(
            text="<b>2022 gas crisis — premium per MWh by scheme</b>",
            subtitle=dict(
                text="2021 / 2022 / 2023 grouped bars; schemes without gas counterfactual excluded.",
                font=dict(size=12, color="#a0a4b8"),
            ),
            x=0.05,
            xanchor="left",
        ),
    )
    fig.update_xaxes(title="Scheme")
    builder.format_currency_axis(fig, axis="y", title="Premium per MWh (£/MWh)")
    builder.save(
        fig,
        "x5_2022_crisis",
        export_twitter=True,
        export_html=True,
        export_div=True,
    )


if __name__ == "__main__":
    main()
