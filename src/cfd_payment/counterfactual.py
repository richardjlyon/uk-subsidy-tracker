"""
Counterfactual electricity cost modelling.

Computes what electricity would cost in a gas-only CCGT grid,
broken down into fuel cost and carbon cost components.
"""

import pandas as pd

from cfd_payment.data import load_gas_price

CCGT_EFFICIENCY = 0.50
GAS_CO2_INTENSITY_THERMAL = 0.184  # tCO2 per MWh thermal (natural gas)

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
) -> pd.DataFrame:
    """
    Compute the counterfactual gas-only electricity price, daily.

    Returns columns: date, gas_p_per_kwh, gas_fuel_cost,
    carbon_price_per_t, carbon_cost, counterfactual_total (all £/MWh).
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
    df["counterfactual_total"] = df["gas_fuel_cost"] + df["carbon_cost"]

    return df


def compute_counterfactual_monthly(
    gas_df: pd.DataFrame | None = None,
    carbon_prices: dict[int, float] | None = None,
    ccgt_efficiency: float = CCGT_EFFICIENCY,
) -> pd.DataFrame:
    """Monthly-averaged version of compute_counterfactual."""
    daily = compute_counterfactual(gas_df, carbon_prices, ccgt_efficiency)
    return daily.set_index("date").resample("ME").mean(numeric_only=True).reset_index()
