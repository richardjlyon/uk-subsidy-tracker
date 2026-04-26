"""X1 — Total UK subsidy stacked by scheme, annual.

PORTAL-01 P1 flagship chart. Plotly native rangeselector (1y/5y/All) on the
interactive HTML; Twitter-PNG hero is a static All-time view (UI-SPEC
§"X1 hero embed" lock — D-07). Stacks only schemes with full reconstruction
(CfD + RO today; Phases 7-12 add to ``SHIPPED_SCHEMES`` as they ship).

REQUIREMENT X-01.

The TWO-figure pattern is the contract:
1. Build a base figure (traces + layout + subtitle) — no rangeselector.
2. PNG export: copy the base, set ``xaxis.type='date'``, save with
   ``export_twitter=True`` only. No rangeselector buttons in the raster.
3. HTML export: copy the base, add the rangeselector buttons + ``type='date'``
   axis, save with ``export_html=True`` and ``export_div=True``.

Per RESEARCH §"Plotly rangeselector specifics", a date-typed axis is required
for the rangeselector to render — the parquet's ``year`` int64 column is
coerced to ``year_dt`` (datetime) at the plotting boundary.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pyarrow.parquet as pq

from uk_subsidy_tracker.plotting import ChartBuilder
from uk_subsidy_tracker.plotting.colors import SCHEME_COLORS
from uk_subsidy_tracker.schemes import portal


def _prepare() -> pd.DataFrame:
    """Read cross_scheme.parquet, coerce year → datetime, sort schemes by total cost.

    Returns the raw long-format frame plus a ``year_dt`` datetime column for the
    rangeselector-compatible date axis. Empty DataFrame returned when the
    parquet is absent or zero-row, so ``main()`` can short-circuit to the
    placeholder figure.

    Stack order: smallest scheme at the bottom, biggest at the top, per
    UI-SPEC §"Stack order on X1". Plotly stacks bars in trace-order, so we
    sort the categorical accordingly.
    """
    src = portal.DERIVED_DIR / "cross_scheme.parquet"
    if not src.exists():
        return pd.DataFrame()
    df = pq.read_table(src).to_pandas()
    if len(df) == 0:
        return df

    # Coerce year → datetime for rangeselector compatibility (X1 only).
    # Parquet `year` stays int64 for D-21 determinism; coercion lives at the
    # plotting boundary per RESEARCH §"Plotly rangeselector specifics".
    df["year_dt"] = pd.to_datetime(df["year"], format="%Y")

    # Stack order: smaller-total scheme at the bottom (UI-SPEC §"Stack order").
    # Compute per-scheme total cost; sort schemes ascending so the categorical
    # preserves that order through the groupby downstream.
    totals = df.groupby("scheme")["cost_gbp"].sum().sort_values(ascending=True)
    df["scheme"] = pd.Categorical(
        df["scheme"], categories=list(totals.index), ordered=True
    )
    return df.sort_values(["year", "scheme"])


def _placeholder(builder: ChartBuilder) -> go.Figure:
    """Titled single-panel placeholder for the empty-substrate path.

    Matches the "chart files emit without raising on stub data" contract so
    ``python -m uk_subsidy_tracker.plotting`` succeeds end-to-end even when
    cross_scheme.parquet has not yet been rebuilt.
    """
    fig = builder.create_basic()
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        text=(
            "<b>No cross-scheme data yet</b><br><br>"
            "data/derived/portal/cross_scheme.parquet is empty.<br>"
            "Run schemes.portal.rebuild_derived() first."
        ),
        showarrow=False,
        font={"size": 14, "color": "#9ca3af"},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def _build_stacked_figure(df: pd.DataFrame, builder: ChartBuilder) -> go.Figure:
    """Build the base stacked-bar figure (traces + layout + subtitle).

    Extracted so the TWO-figure pattern can clone the base for PNG (no
    rangeselector) and HTML (rangeselector + date axis) without re-running
    the trace-construction logic.
    """
    fig = builder.create_basic()
    for scheme_name, sub in df.groupby("scheme", observed=True, sort=False):
        fig.add_trace(
            go.Bar(
                x=sub["year_dt"],
                y=sub["cost_gbp"] / 1e9,
                name=str(scheme_name),
                marker_color=SCHEME_COLORS[str(scheme_name)],
                hovertemplate=(
                    "%{x|%Y}<br>"
                    + str(scheme_name)
                    + "<br>£%{y:.2f} bn<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        barmode="stack",
        title=dict(
            text="<b>Total UK subsidy stacked by scheme</b>",
            subtitle=dict(
                text="Covers 2 of 8 schemes — see scheme grid for coverage status.",
                font=dict(size=12, color="#a0a4b8"),
            ),
            x=0.05,
            xanchor="left",
        ),
    )
    builder.format_currency_axis(
        fig, axis="y", suffix=" bn", title="Subsidy cost (£bn)"
    )
    return fig


def main() -> None:
    df = _prepare()
    builder = ChartBuilder(
        title="Total UK subsidy stacked by scheme",
        height=600,
    )
    if df.empty:
        fig = _placeholder(builder)
        builder.save(fig, "x1_stacked_total", export_twitter=True)
        return

    # Build BASE figure (traces + layout + subtitle), no rangeselector.
    fig_base = _build_stacked_figure(df, builder)

    # PNG hero — All-time view, NO rangeselector (UI-SPEC §"X1 hero embed" lock).
    fig_png = go.Figure(fig_base)
    fig_png.update_xaxes(type="date", title="Year")
    builder.save(
        fig_png,
        "x1_stacked_total",
        export_twitter=True,
        export_html=False,
        export_div=False,
    )

    # HTML interactive — native Plotly rangeselector buttons (1y / 5y / All).
    fig_html = go.Figure(fig_base)
    # Note: Plotly's rangeselector has no `active` property — the default
    # (no button highlighted) coincides with the natural full-range startup
    # state, which IS the "All" view per UI-SPEC §"X1 hero embed".
    fig_html.update_xaxes(
        rangeselector=dict(
            buttons=[
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(step="all", label="All"),
            ],
            xanchor="left",
            yanchor="bottom",
            x=0.0,
            y=1.02,
        ),
        type="date",  # REQUIRED — rangeselector needs a date-typed axis
        title="Year",
    )
    builder.save(
        fig_html,
        "x1_stacked_total",
        export_twitter=False,
        export_html=True,
        export_div=True,
    )


if __name__ == "__main__":
    main()
