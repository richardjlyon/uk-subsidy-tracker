# Efficiency — methodology

The Efficiency theme computes £ subsidy per tonne of avoided CO₂. Three methodology pieces: (a) the £ numerator, (b) the tCO₂ denominator, (c) the gas counterfactual the carbon-displacement argument rests on.

## £ subsidy per tCO₂ avoided

Numerator: CfD `CFD_Payments_GBP` (the levy-channel subsidy — what consumers top up via the CfD levy). Excludes wholesale-channel payments because those are what consumers would have paid for any electricity. Denominator: LCCC-reported `Avoided_GHG_tonnes_CO2e`, which uses DESNZ's grid-average emission factor for the displaced margin.

## Allocation-round aggregation

Ratios are computed per allocation round (IC, AR1, AR2, AR3) and averaged over the units active in each round by year. 2022 is excluded from the time-series view because negative `CFD_Payments_GBP` values that year (strike < reference during the gas crisis) distort the ratio; the underlying data is still valid but the chart becomes unreadable.

## Reference benchmarks

Two horizontal reference lines on the flagship chart:

- **DEFRA Social Cost of Carbon** (~£280/tCO₂, 2024 central value) — the societal damage cost published for UK policy appraisal.
- **UK ETS auction price** (~£50/tCO₂, 2024-25 average) — the market price of a traded UK emissions allowance.

## Gas counterfactual

The underlying displaced-gas assumption is the same one used in Cost:

→ [Gas counterfactual (shared methodology)](../../methodology/gas-counterfactual.md)
