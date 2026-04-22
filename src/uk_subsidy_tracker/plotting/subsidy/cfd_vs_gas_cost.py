"""CfD electricity cost — real decomposition + gas counterfactual reference line.

Two-panel chart with shared x-axis:
- Top: monthly stacked bars (wholesale + CfD levy = total CfD cost) with
  gas counterfactual overlaid as a dashed line.
- Bottom: cumulative stacked area of the same, with gas counterfactual line.

Design principle — real vs hypothetical are visually distinct:
- STACKED BARS are all real money flows from LCCC data.
- DASHED LINE is the hypothetical gas alternative.
- This avoids the "are we adding two real things or summing real + modelled?"
  confusion of a stacked bar that mixes the two.

Sources:
- LCCC "Actual CfD Generation and avoided GHG emissions" — daily generation,
  strike price, market reference price, and CFD_Payments_GBP per unit.
- ONS System Average Price of gas — daily wholesale gas price (p/kWh thermal).

How the numbers stack (all real):
- Wholesale slice (bottom, red):   reference_price × generation.
  Paid by consumers via the kWh price on their electricity bill.
- CfD levy slice (top, blue):      CFD_Payments_GBP = (strike − reference) × gen.
  Paid by consumers via the Supplier Obligation levy line. Goes NEGATIVE when
  reference > strike (e.g. 2022 gas crisis — generators refunded the levy).
- Total bar height:                wholesale + levy = strike × generation
                                   = total CfD electricity cost.

Gas counterfactual (dashed line — "what the same electricity would have cost
from the existing UK gas fleet"):
- Answers: "if we'd stuck with the gas fleet we already had instead of
  building renewables, what would the same MWh have cost?"
- Daily £/MWh = gas_fuel + carbon_cost + plant_opex, where:
  - gas_fuel = gas_p/kWh × 10 / 0.55 (CCGT thermal efficiency)
  - carbon_cost = UK ETS annual price × (0.184 / 0.55) tCO2/MWh
  - plant_opex = £5/MWh for fixed + variable O&M on existing CCGT
    (capex sunk — fleet built 1995–2012, paid off by CfD era).
- Source for opex: BEIS Electricity Generation Costs 2023, Table ES.1.

Reading the chart:
- Bar top ABOVE line = CfD electricity cost MORE than gas fleet alternative.
- Bar top BELOW line = CfD electricity cost LESS than gas fleet alternative.
- Blue slice alone = CfD levy (the "subsidy" in popular reporting).
- Red slice alone = wholesale cost (paid regardless of generation tech).

Modelling caveats (gas counterfactual only):
- "Existing fleet" assumption: plants built 1995–2012 with capex sunk.
  Some retirements (Killingholme 2015, Cottam 2019) and mid-life refurbs
  over 2015–2026 slightly understate long-run cost. To model new-build
  gas, override non_fuel_opex_per_mwh to CCGT_NEW_BUILD_CAPEX_OPEX_PER_MWH
  (~£20/MWh).
- Assumes gas supply at observed wholesale prices even with the extra
  ~150 TWh of demand renewables displaced (arguable — more gas demand
  likely pushes the gas price up).
- 55% CCGT thermal efficiency is representative of modern H-class plants.
"""

import plotly.graph_objects as go

from cfd_payment.counterfactual import (
    CCGT_EFFICIENCY,
    CCGT_EXISTING_FLEET_OPEX_PER_MWH,
    compute_counterfactual,
)
from cfd_payment.data import load_lccc_dataset
from cfd_payment.plotting import ChartBuilder


def _prepare_monthly():
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    cf_daily = compute_counterfactual()
    gas_price = cf_daily.set_index("date")["counterfactual_total"]

    # Restrict to days where the gas counterfactual is available. Early CfD
    # generation (mid-2016 through 2017) pre-dates the ONS/UK ETS coverage
    # used to build the counterfactual. Including those days would inflate
    # the CfD total while leaving the gas total at zero — producing a
    # spurious ~£0.7bn premium against a column that doesn't exist.
    valid_dates = gas_price.dropna().index
    df = df[df["Settlement_Date"].isin(valid_dates)].copy()

    df["month"] = df["Settlement_Date"].dt.to_period("M").dt.to_timestamp()
    df["wholesale"] = (
        df["Market_Reference_Price_GBP_Per_MWh"] * df["CFD_Generation_MWh"]
    )

    daily_gen = df.groupby("Settlement_Date")["CFD_Generation_MWh"].sum()
    daily_gas_cost = daily_gen * gas_price.reindex(daily_gen.index)

    monthly_wholesale = df.groupby("month")["wholesale"].sum()
    monthly_levy = df.groupby("month")["CFD_Payments_GBP"].sum()
    monthly_gas = daily_gas_cost.resample("ME").sum()
    monthly_gas.index = monthly_gas.index.to_period("M").to_timestamp()

    monthly = (
        monthly_wholesale.to_frame("wholesale")
        .join(monthly_levy.rename("levy"), how="inner")
        .join(monthly_gas.rename("gas_counter"), how="inner")
    )
    monthly["cfd_cost"] = monthly["wholesale"] + monthly["levy"]
    return monthly


def main() -> None:
    monthly = _prepare_monthly()

    monthly_m = monthly / 1e6
    cum_bn = monthly.cumsum() / 1e9

    cum_wholesale = cum_bn["wholesale"].iloc[-1]
    cum_levy = cum_bn["levy"].iloc[-1]
    cum_cfd = cum_bn["cfd_cost"].iloc[-1]
    cum_gas = cum_bn["gas_counter"].iloc[-1]

    builder = ChartBuilder(
        title="What consumers paid for CfD electricity — wholesale + levy, with gas alternative",
        height=900,
    )
    fig = builder.create_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=[
            "Monthly — wholesale + CfD levy (bars), gas alternative (line)",
            f"Cumulative — £{cum_cfd:.0f}bn total paid for CfD electricity",
        ],
        vertical_spacing=0.08,
    )

    # --- Top panel: stacked bars (real) + line (hypothetical) ---
    fig.add_trace(
        go.Bar(
            x=monthly_m.index,
            y=monthly_m["wholesale"],
            name="Wholesale (real, via electricity bill)",
            marker_color="#d62728",
            hovertemplate="%{x|%b %Y}<br>Wholesale: £%{y:.0f}m<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=monthly_m.index,
            y=monthly_m["levy"],
            name="CfD levy (real, via levy line on bill)",
            marker_color="#1f77b4",
            hovertemplate="%{x|%b %Y}<br>Levy: £%{y:+.0f}m<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=monthly_m.index,
            y=monthly_m["gas_counter"],
            name="Gas alternative (hypothetical)",
            mode="lines",
            line={"color": "#ff7f0e", "width": 2},
            hovertemplate="%{x|%b %Y}<br>Gas alt: £%{y:.0f}m<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # --- Bottom panel: cumulative stacked area + line ---
    fig.add_trace(
        go.Scatter(
            x=cum_bn.index,
            y=cum_bn["wholesale"],
            name=f"Wholesale (£{cum_wholesale:.0f}bn)",
            mode="lines",
            line={"color": "#d62728", "width": 2},
            fill="tozeroy",
            fillcolor="rgba(214,39,40,0.4)",
            stackgroup="cumulative",
            hovertemplate="%{x|%b %Y}<br>Wholesale: £%{y:.1f}bn<extra></extra>",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=cum_bn.index,
            y=cum_bn["levy"],
            name=f"CfD levy (£{cum_levy:.0f}bn)",
            mode="lines",
            line={"color": "#1f77b4", "width": 2},
            fill="tonexty",
            fillcolor="rgba(31,119,180,0.4)",
            stackgroup="cumulative",
            hovertemplate="%{x|%b %Y}<br>Levy: £%{y:.1f}bn<extra></extra>",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=cum_bn.index,
            y=cum_bn["gas_counter"],
            name=f"Gas alternative (£{cum_gas:.0f}bn, hypothetical)",
            mode="lines",
            line={"color": "#ff7f0e", "width": 2.5},
            hovertemplate="%{x|%b %Y}<br>Gas alt: £%{y:.1f}bn<extra></extra>",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        barmode="relative",
        hovermode="x unified",
    )

    assumptions = (
        f"Gas alternative = fuel (at {int(CCGT_EFFICIENCY * 100)}% CCGT efficiency) "
        f"+ UK ETS carbon tax + £{CCGT_EXISTING_FLEET_OPEX_PER_MWH:.0f}/MWh O&M "
        "(existing fleet, capex sunk). Source: LCCC, ONS, BEIS ElecGenCosts 2023."
    )
    fig.add_annotation(
        text=assumptions,
        xref="paper",
        yref="paper",
        x=0.0,
        y=0,
        xanchor="left",
        yanchor="top",
        yshift=-40,
        showarrow=False,
        font=dict(size=10, color="#9ca3af"),
    )

    builder.format_currency_axis(
        fig,
        axis="y",
        suffix="m",
        title="£ millions",
        row=1,
        col=1,
    )
    builder.format_currency_axis(
        fig,
        axis="y",
        suffix="bn",
        title="£ billions",
        row=2,
        col=1,
    )

    builder.save(fig, "subsidy_cfd_vs_gas_total", export_twitter=True)


if __name__ == "__main__":
    main()
