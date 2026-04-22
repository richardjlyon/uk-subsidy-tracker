"""
Counterfactual electricity cost modelling.

Computes what electricity would cost in a gas-only CCGT grid,
broken down into fuel cost and carbon cost components.
"""

import pandas as pd

from uk_subsidy_tracker.data import load_gas_price

CCGT_EFFICIENCY = 0.55
GAS_CO2_INTENSITY_THERMAL = 0.184  # tCO2 per MWh thermal (natural gas)

# Non-fuel, non-carbon opex for a CCGT (£/MWh of electricity).
#
# EXISTING FLEET — capex sunk, only O&M needed. Used as the default because
# the UK CCGT fleet was largely built 1995–2012 and had its capital cost paid
# off by the start of the CfD era (2015). Source: BEIS Electricity Generation
# Costs 2023, Table ES.1 — fixed O&M ~£3/MWh + variable O&M ~£2/MWh for
# operational H-class CCGT.
CCGT_EXISTING_FLEET_OPEX_PER_MWH = 5.0

# NEW-BUILD — adds overnight capex + finance + fixed/variable O&M. Use when
# modelling a hypothetical "build new gas instead of renewables" scenario.
# Source: BEIS Electricity Generation Costs 2023, Table ES.1 — levelised
# capex @ 8% WACC (~£15/MWh) + fixed/variable O&M (~£5/MWh).
CCGT_NEW_BUILD_CAPEX_OPEX_PER_MWH = 20.0

# Default: existing fleet. Answers the policy question "what if we'd stuck
# with the gas fleet we already had instead of building renewables?"
DEFAULT_NON_FUEL_OPEX = CCGT_EXISTING_FLEET_OPEX_PER_MWH

# Annual average carbon prices (£/tCO2).
# 2018–2020: EU ETS converted EUR→GBP.  2021+: UK ETS (GOV.UK published).
DEFAULT_CARBON_PRICES: dict[int, float] = {
    2018: 13.0,
    2019: 22.0,
    2020: 22.0,
    2021: 48.0,
    2022: 53.0,
    2023: 45.0,
    2024: 36.0,
    2025: 42.0,
    2026: 40.0,
}


def compute_counterfactual(
    gas_df: pd.DataFrame | None = None,
    carbon_prices: dict[int, float] | None = None,
    ccgt_efficiency: float = CCGT_EFFICIENCY,
    non_fuel_opex_per_mwh: float = DEFAULT_NON_FUEL_OPEX,
) -> pd.DataFrame:
    """
    Compute the counterfactual gas-only electricity price, daily.

    Returns columns: date, gas_p_per_kwh, gas_fuel_cost,
    carbon_price_per_t, carbon_cost, plant_opex, counterfactual_total
    (all £/MWh).

    counterfactual_total = gas_fuel_cost + carbon_cost + plant_opex.

    Callers who want fuel-only (e.g. scissors chart) should reference
    gas_fuel_cost directly instead of counterfactual_total.
    """
    if gas_df is None:
        gas_df = load_gas_price()
    if carbon_prices is None:
        carbon_prices = DEFAULT_CARBON_PRICES

    df = gas_df.copy()
    df["gas_fuel_cost"] = df["gas_p_per_kwh"] * 10.0 / ccgt_efficiency

    co2_intensity = GAS_CO2_INTENSITY_THERMAL / ccgt_efficiency
    df["carbon_price_per_t"] = df["date"].dt.year.map(carbon_prices).fillna(0.0)
    df["carbon_cost"] = df["carbon_price_per_t"] * co2_intensity
    df["plant_opex"] = non_fuel_opex_per_mwh
    df["counterfactual_total"] = (
        df["gas_fuel_cost"] + df["carbon_cost"] + df["plant_opex"]
    )

    return df


def compute_counterfactual_monthly(
    gas_df: pd.DataFrame | None = None,
    carbon_prices: dict[int, float] | None = None,
    ccgt_efficiency: float = CCGT_EFFICIENCY,
) -> pd.DataFrame:
    """Monthly-averaged version of compute_counterfactual."""
    daily = compute_counterfactual(gas_df, carbon_prices, ccgt_efficiency)
    return daily.set_index("date").resample("ME").mean(numeric_only=True).reset_index()
