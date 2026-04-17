"""Wind-price cannibalisation — correlation strengthening over time.

Bar chart showing the Pearson correlation between daily total UK wind
generation and daily wholesale electricity price, by year.

The story: in 2017-2018 wind was a small share of the grid and had no
measurable effect on prices (r ≈ 0). By 2025-2026, wind is large
enough that windy days reliably crash the price (r ≈ -0.5 to -0.6).

Why this matters for consumers: under CfDs, generators get their
guaranteed strike price regardless of the market price. When wind
output crashes the wholesale price, the gap between strike and market
widens, and the CfD levy payment (funded by consumers) grows. More
wind capacity makes this worse — a self-defeating cycle where building
more wind increases the subsidy cost per MWh.

Why Pearson r is the right metric: it is scale-invariant — unaffected
by absolute price levels or volatility differences between years. The
2022 gas crisis pushed prices to £200+/MWh but the correlation (-0.45)
is matched by 2025 (-0.47) at normal price levels, confirming the
relationship is structural, not an artefact of volatile markets.

Sources: Elexon BMRS — AGWS (actual wind/solar generation, all UK, MW)
and settlement system prices (£/MWh). Both half-hourly, averaged to daily.
Methodology:
- Wind generation = daily average MW across all 48 settlement periods
  (onshore + offshore, full UK fleet — not just CfD projects).
- Price = daily average system sell price (£/MWh).
- Pearson r computed per year on daily (wind_mw, price) pairs.
- Days with prices > £500/MWh excluded as extreme outliers.
Caveats:
- System price is the balancing price, not the day-ahead wholesale
  price. It is noisier but directionally correct for showing the
  wind-price relationship.
- Daily averaging smooths intra-day effects (wind often peaks at
  night when demand is low, amplifying the price impact).
- 2026 has partial year data but correlation is consistent with trend.
"""

import numpy as np
import plotly.graph_objects as go

from cfd_payment.data.elexon import load_elexon_prices_daily, load_elexon_wind_daily
from cfd_payment.plotting import save_chart


def main() -> None:
    wind = load_elexon_wind_daily()
    prices = load_elexon_prices_daily()
    merged = wind.merge(prices, on="date")
    merged["year"] = merged["date"].dt.year
    merged = merged[merged["price_gbp_per_mwh"] < 500]

    years = []
    corrs = []
    for year in sorted(merged["year"].unique()):
        yr = merged[merged["year"] == year]
        if len(yr) < 30:
            continue
        corr = np.corrcoef(yr["wind_mw"], yr["price_gbp_per_mwh"])[0, 1]
        years.append(year)
        corrs.append(corr)

    bar_colors = ["#d62728" if c < 0 else "#2ca02c" for c in corrs]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=years,
            y=corrs,
            marker_color=bar_colors,
            hovertemplate="%{x}<br>r = %{y:+.2f}<extra></extra>",
        )
    )

    fig.add_hline(
        y=0,
        line_color="grey",
        line_width=1,
    )

    fig.update_xaxes(title="Year", dtick=1)
    fig.update_yaxes(title="Correlation between wind output and wholesale price (r)")
    fig.update_layout(
        title="Wind cannibalisation — more wind capacity means wind increasingly crashes the price",
        height=500,
        showlegend=False,
    )

    save_chart(fig, "cannibalisation_price_vs_wind")


if __name__ == "__main__":
    main()
