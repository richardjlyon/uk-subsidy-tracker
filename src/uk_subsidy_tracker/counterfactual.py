"""
Counterfactual electricity cost modelling.

Computes what electricity would cost in a gas-only CCGT grid,
broken down into fuel cost and carbon cost components.
"""

import pandas as pd

from uk_subsidy_tracker.data import load_gas_price

CCGT_EFFICIENCY = 0.55
"""Fleet-average thermal efficiency of UK CCGT, dimensionless.

55% reflects a blend of older F-class plants (~50%) and modern H-class
(~60%). Appropriate for an existing-fleet counterfactual; a new-build-only
study should use 0.60.

Provenance:
  source:       BEIS Electricity Generation Costs 2023, Table ES.1
  url:          https://www.gov.uk/government/publications/electricity-generation-costs-2023
  basis:        Net HHV efficiency, H-class CCGT mid-range
  retrieved_on: 2026-04-22
  next_audit:   when BEIS/DESNZ publishes next Electricity Generation Costs edition
"""

GAS_CO2_INTENSITY_THERMAL = 0.18290
"""tCO2 per MWh thermal, natural gas (gross CV basis).

Provenance:
  source:       DESNZ 2024 UK Government Greenhouse Gas Conversion Factors
  url:          https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024
  basis:        Gross CV (UK convention — gas suppliers bill in kWh gross CV)
  retrieved_on: 2026-04-22
  next_audit:   2027-04-01  (DESNZ publishes annually, typically June)
"""

METHODOLOGY_VERSION: str = "0.1.0"
"""Semantic version for the gas counterfactual formula.

Pre-1.0.0: prototype phase — constants and formula may change without
ceremony. At first public release, bump to 1.0.0 and resume SemVer
discipline. After 1.0.0:

- PATCH: Constant tweak with identical formula shape (e.g., new DEFAULT_CARBON_PRICES entry).
- MINOR: Additive parameter (new kwarg with default preserving old calls).
- MAJOR: Formula-shape change (new/dropped term, changed unit).

Post-1.0.0 bumps require an entry in CHANGES.md under ## Methodology versions.
"""

CCGT_EXISTING_FLEET_OPEX_PER_MWH = 5.0
"""Non-fuel, non-carbon opex for EXISTING-fleet CCGT (£/MWh electricity).

Capex sunk, only O&M needed. Used as the default because the UK CCGT
fleet was largely built 1995–2012 and had its capital cost paid off
by the start of the CfD era (2015).

Provenance:
  source:       BEIS Electricity Generation Costs 2023, Table ES.1
  url:          https://www.gov.uk/government/publications/electricity-generation-costs-2023
  basis:        Operational H-class CCGT, fixed O&M ~£3/MWh + variable O&M ~£2/MWh
  retrieved_on: 2026-04-22
  next_audit:   when BEIS/DESNZ publishes next Electricity Generation Costs edition
"""

CCGT_NEW_BUILD_CAPEX_OPEX_PER_MWH = 20.0
"""Non-fuel opex for NEW-BUILD CCGT including capex amortisation (£/MWh).

Use when modelling a hypothetical "build new gas instead of renewables"
scenario (typically for sensitivity analysis, not the default).

Provenance:
  source:       BEIS Electricity Generation Costs 2023, Table ES.1
  url:          https://www.gov.uk/government/publications/electricity-generation-costs-2023
  basis:        Levelised capex @ 8% WACC (~£15/MWh) + fixed/variable O&M (~£5/MWh)
  retrieved_on: 2026-04-22
  next_audit:   when BEIS/DESNZ publishes next Electricity Generation Costs edition
"""

DEFAULT_NON_FUEL_OPEX = CCGT_EXISTING_FLEET_OPEX_PER_MWH
"""Default non-fuel opex: existing-fleet (capex sunk).

Answers the policy question: "what if we'd stuck with the gas fleet we
already had instead of building renewables?"
"""

DEFAULT_CARBON_PRICES: dict[int, float] = {
    # 2002-2004: Pre-EU-ETS. No carbon scheme operated; zero by construction (D-05).
    # RO launched 2002-04-01; these years anchor the table at the scheme start.
    2002: 0.0,
    2003: 0.0,
    2004: 0.0,
    # 2005-2017: EU ETS Phase I (2005-2007), Phase II (2008-2012), Phase III (2013-2017)
    # annual averages (EUR→GBP at Bank of England contemporary annual-average rates;
    # ICE/EEX spot reference). Additive extension per D-05 for RO scheme coverage.
    # Phase I (2005-2007) collapsed to ~€0.10 by Sept-2007 because allowances were
    # non-bankable into Phase II; 2007 ~£0.5/tCO2 is historically correct (see
    # docs/schemes/ro.md methodology callout for the artefact explanation).
    # [VERIFICATION-PENDING] values below are executor-accepted research seeds from
    # Plan 05-04 <interfaces> block; a future audit should verify against the EEA
    # "Emissions, allowances, surplus and prices in the EU ETS 2005-2020" viewer
    # and the BoE historical EUR/GBP annual-average series before next_audit.
    2005: 12.3,
    2006: 11.9,
    2007: 0.5,
    2008: 17.7,
    2009: 11.7,
    2010: 12.3,
    2011: 11.3,
    2012: 6.0,
    2013: 3.8,
    2014: 4.8,
    2015: 5.6,
    2016: 4.3,
    2017: 5.1,
    # 2018-2020: EU ETS Phase III / IV annual averages (UK still in EU ETS pre-Brexit
    # carbon-scheme divergence), converted EUR→GBP at contemporary average rates.
    2018: 13.0,
    2019: 22.0,
    2020: 22.0,
    # 2021+: UK ETS annual averages (post-Brexit carbon-scheme divergence).
    2021: 48.0,
    2022: 73.0,
    2023: 45.0,
    2024: 36.0,
    2025: 42.0,
    2026: 40.0,
}
"""Annual carbon prices, £/tCO2.

2002-2004: No carbon scheme operated; zero by construction (D-05).

2005-2017: EU ETS annual averages (Phase I 2005-2007 pilot;
Phase II 2008-2012; Phase III 2013-2017). EUR→GBP at BoE contemporary
annual-average rates; ICE/EEX spot reference.

2018-2020: EU ETS Phase III/IV annual averages (UK still in EU ETS
pre-Brexit carbon-scheme divergence), converted EUR→GBP.

2021+: UK ETS annual averages (post-Brexit divergence).

Provenance:
  sources:
    - 2002-2004: No carbon scheme pre-EU-ETS Phase I start (2005-01-01); D-05
    - 2005-2017: EU ETS annual averages (ICE/EEX reference; EUR→GBP at
      Bank of England annual-average rate)
    - 2018-2020: EU ETS Phase III/IV spot (via EEX / ICE reference)
    - 2021+: UK ETS via OBR Economic & Fiscal Outlook + DESNZ/GOV.UK
  urls:
    - https://www.eea.europa.eu/en/analysis/maps-and-charts/emissions-allowances-surplus-and-prices
    - https://www.bankofengland.co.uk/boeapps/database/
    - https://www.ice.com/products/197/EUA-Futures
    - https://obr.uk/forecasts-in-depth/tax-by-tax-spend-by-spend/emissions-trading-scheme-uk-ets/
    - https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price/uk-ets-carbon-prices-for-use-in-civil-penalties-2024
  basis:        Calendar-year annual average carbon allowance price, £/tCO2
  retrieved_on: 2026-04-22
  next_audit:   2027-01-15  (OBR EFO published late-March; refresh for full 2026 + 2027 initial estimate)

Notes:
- 2002-2004 zeros reflect the absence of any UK or EU carbon-allowance
  scheme; EU ETS Phase I did not start until 2005-01-01.
- 2005-2017 values shipped via Phase 5 Plan 05-04 for RO scheme coverage
  (RO launched 2002-04-01; counterfactual needs full 2002-present span).
  Values carry [VERIFICATION-PENDING] inline comment flag — executor
  accepted Plan 05-04 research seeds pending audit against primary EEA
  + BoE sources before next_audit.
- 2007 (£0.5) reflects EU ETS Phase I price crash; allowances were
  non-bankable into Phase II and collapsed to ~€0.10 by September 2007.
  Historically correct (see docs/schemes/ro.md methodology callout).
- METHODOLOGY_VERSION stays "0.1.0" per D-06 — 2002-2017 extension is
  additive (new year keys; no existing 2018-2026 values revised; no
  formula-shape change). Bump to 1.0.0 reserved for Phase 6+ portal launch.
- 2022 (73.0) is OBR-cited; UK ETS 2022 was volatile, peaking near
  £100 mid-year; OBR uses 73 as its calendar-year reference.
- 2023 (45.0) and 2025 (42.0) are approximate — revisit before v1.0.0
  public release.
"""


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

    Callers who want fuel-only should reference gas_fuel_cost directly
    instead of counterfactual_total.
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
    df["methodology_version"] = METHODOLOGY_VERSION

    return df


def compute_counterfactual_monthly(
    gas_df: pd.DataFrame | None = None,
    carbon_prices: dict[int, float] | None = None,
    ccgt_efficiency: float = CCGT_EFFICIENCY,
    non_fuel_opex_per_mwh: float = DEFAULT_NON_FUEL_OPEX,
) -> pd.DataFrame:
    """Monthly-averaged version of compute_counterfactual.

    Accepts the same keyword arguments as :func:`compute_counterfactual` and
    forwards them through, so sensitivity scenarios (e.g. new-build opex =
    ``CCGT_NEW_BUILD_CAPEX_OPEX_PER_MWH``) work identically at monthly
    granularity.
    """
    daily = compute_counterfactual(
        gas_df, carbon_prices, ccgt_efficiency, non_fuel_opex_per_mwh
    )
    return daily.set_index("date").resample("ME").mean(numeric_only=True).reset_index()
