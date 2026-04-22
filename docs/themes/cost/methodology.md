# Cost — methodology

The Cost theme aggregates CfD payments over time and compares them against a gas counterfactual. Three methodology pieces live here: (a) how cost totals are aggregated, (b) allocation-round handling for forward projections, (c) the link to the shared gas-counterfactual.

## Aggregation

Cost totals are monthly sums of `CFD_Payments_GBP + reference_price × CFD_Generation_MWh` (the two cash-flow channels consumers pay through — levy top-ups + wholesale-embedded cost). Weekly/daily aggregation uses calendar-week or calendar-day sums; monthly uses calendar months (`pd.to_datetime(...).dt.to_period("M")`). Allocation round is preserved as a grouping key.

## Allocation round handling

Charts by allocation round group units via `Allocation_round` from the LCCC portfolio snapshot. Each round (Investment Contract, AR1, AR2, AR3, AR4) has its own cost profile because strike prices differ. Remaining-obligations projections extend each unit's current strike forward to its contract end date.

## Gas counterfactual

The "gas alternative" line used across Cost charts is computed identically to Efficiency's denominator. See the single shared source of truth:

→ [Gas counterfactual (shared methodology)](../../methodology/gas-counterfactual.md)

Cited constants (all carry `Provenance:` blocks — `grep -rn "^Provenance:" src/`):

- `CCGT_EFFICIENCY` (0.55) — BEIS *Electricity Generation Costs 2023*
- `GAS_CO2_INTENSITY_THERMAL` (0.184 tCO₂/MWh thermal) — DESNZ GHG factors
- `CCGT_EXISTING_FLEET_OPEX_PER_MWH` (£5/MWh) — BEIS EGC 2023 Table ES.1
- `DEFAULT_CARBON_PRICES` (2018–2026 annual) — UK ETS / EU ETS auction results

Full definitions: [`src/uk_subsidy_tracker/counterfactual.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/src/uk_subsidy_tracker/counterfactual.py).
