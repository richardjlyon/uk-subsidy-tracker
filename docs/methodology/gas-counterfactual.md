# Gas counterfactual

An audit trail for the orange "gas alternative" line on the CfD-vs-gas chart.

## The question

> *"If we'd kept the gas fleet we already had instead of paying for renewables, what would the same electricity have cost?"*

This is a policy-level counterfactual, not a market-clearing simulation. We are
not modelling what wholesale prices would have done in the absence of renewables
— that depends on gas supply elasticity, demand response, and interconnector
flows that are beyond the scope of this analysis. We are asking: **given the
gas prices and carbon prices that actually occurred, what would it have cost to
generate the same MWh from a CCGT fleet?**

## The formula

For each day, compute an implied £/MWh for gas-generated electricity:

```
gas_alt_£/MWh  =  fuel  +  carbon  +  O&M

fuel    =  gas_price_p_per_kWh × 10 / 0.55
carbon  =  UK_ETS_£_per_tCO2 × (0.18290 / 0.55)
O&M     =  £5 / MWh   (existing fleet, capex sunk)
```

Each daily £/MWh is multiplied by the actual daily CfD generation (MWh) and
summed to monthly, then cumulative, totals.

| Term | Source | Value |
|------|--------|-------|
| Gas price | [ONS System Average Price of gas](https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/gk36/mm22) | Daily, p/kWh thermal |
| CCGT efficiency | [BEIS *Electricity Generation Costs 2023*, Table ES.1](https://www.gov.uk/government/publications/electricity-generation-costs-2023) | 55% |
| Gas CO₂ intensity | [DESNZ 2024 *UK Government GHG Conversion Factors*](https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024) (gross CV) | 0.18290 tCO₂/MWh thermal |
| Carbon price | EU ETS (2018–20) → UK ETS (2021+), annual average ([OBR](https://obr.uk/forecasts-in-depth/tax-by-tax-spend-by-spend/emissions-trading-scheme-uk-ets/)) | £13–£73/tCO₂ |
| O&M | [BEIS *Electricity Generation Costs 2023*, Table ES.1](https://www.gov.uk/government/publications/electricity-generation-costs-2023) | £5/MWh |

<sub>Constants last audited against primary sources: **2026-04-22**. Full provenance (source URL, basis, retrieval date, next-audit trigger) is recorded on each constant's docstring in [`counterfactual.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/src/uk_subsidy_tracker/counterfactual.py). Grep `^Provenance:` across the source tree to enumerate every audited constant.</sub>

The `× 10 / 0.55` converts p/kWh of gas (thermal) into £/MWh of electricity:
the `× 10` is a unit conversion, and dividing by 0.55 accounts for the heat lost
in combustion — 1.82 kWh of gas burned per 1 kWh of electricity delivered.

## Why existing fleet, not new-build

The UK CCGT fleet was largely built 1995–2012. By the time the CfD scheme
started paying generators (2015) most of that capex was already sunk. The
policy choice wasn't *"build renewables or build gas"*; it was *"pay for
renewables or keep running the gas plants we already had."* For that
comparison, only **operating costs** (fuel, carbon, O&M) are relevant —
capital costs are bygones.

Using £5/MWh (BEIS Table ES.1 — fixed ~£3/MWh + variable ~£2/MWh for
operational H-class CCGT) captures this. A new-build figure (£20/MWh with
capex + finance) would be appropriate for a different counterfactual — *"what
if we'd built new gas plants instead of wind and solar?"* — but that isn't the
question the chart is answering.

## Sensitivity

All figures are cumulative totals over **Jan 2018 – Apr 2026** (the window
where both the LCCC CfD data and the gas counterfactual are available)
against **£28.5bn** of actual CfD electricity cost (wholesale + levy) over
the same window. Numbers are generated from the current code via
`compute_counterfactual(...)` — see the snippet at the end of this page.

| Scenario | O&M (£/MWh) | Carbon tax | Gas alternative | Premium vs CfD |
|---|---|---|---|---|
| **Default (existing fleet)** | 5 | UK ETS | **£14.4bn** | **£14.1bn** |
| Fuel + carbon, no O&M | 0 | UK ETS | £13.5bn | £15.1bn |
| Fuel only (no carbon, no O&M) | 0 | — | £10.9bn | £17.6bn |
| New-build (capex + O&M) | 20 | UK ETS | £17.3bn | £11.2bn |
| No carbon tax, existing O&M | 5 | — | £11.9bn | £16.6bn |

Including the earlier 2016–17 CfD generation (no gas counterfactual
available for that period) brings the full-window CfD total to **£29.1bn**
— the headline "~£29bn over ten years" figure on the home page. The £0.7bn
difference is real CfD spending but cannot be set against a like-for-like
gas comparator.

The choice of O&M and carbon-price assumptions moves the cumulative gas
alternative within a **£11–17bn band**. The actual CfD cost (£28.5bn) sits
comfortably above that band in every scenario: the premium is robust to
plausible assumption changes.

## Caveats

These are limits of the model, not reasons to distrust the direction:

- **Gas supply elasticity.** We assume gas would have been available at the
  observed wholesale prices even with ~150 TWh/year of extra gas demand
  (the renewable generation that would not exist in the counterfactual).
  In reality extra demand would likely push gas prices up, which would make
  the gas alternative *more expensive* than the line shows — the premium
  shown here is if anything a lower bound on the 2021–23 crisis years.

- **Fleet age and retirements.** Some of the 1995–2012 fleet has retired
  (Killingholme 2015, Cottam 2019) or had mid-life refurbishment over
  2015–26. Using a flat £5/MWh O&M slightly understates long-run costs
  for a fleet aging past 30 years.

- **Thermal efficiency.** 55% is representative of modern H-class CCGT.
  Older F-class plants run closer to 50%, which would raise fuel cost by
  ~10%. Using the best-case efficiency makes the gas alternative look
  cheaper — again making the shown premium conservative.

- **Carbon price coverage.** 2018–20 used EU ETS (UK was still in scheme).
  UK ETS prices from 2021 onward. Pre-2018 carbon costs are omitted because
  the UK Carbon Price Floor was much lower and CfD generation volumes were
  small, so the effect is negligible.

## Reproducibility

The full calculation lives in [`src/uk_subsidy_tracker/counterfactual.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/src/uk_subsidy_tracker/counterfactual.py).

Key constants:

- `CCGT_EFFICIENCY = 0.55`
- `GAS_CO2_INTENSITY_THERMAL = 0.18290`  (tCO₂/MWh thermal, DESNZ 2024 gross CV)
- `CCGT_EXISTING_FLEET_OPEX_PER_MWH = 5.0`
- `CCGT_NEW_BUILD_CAPEX_OPEX_PER_MWH = 20.0`
- `DEFAULT_CARBON_PRICES`  (dict keyed by year; 2018–2020 EU ETS, 2021+ UK ETS)

Each constant carries a full `Provenance:` block in its docstring. To list all audited constants:

```bash
grep -rn "^Provenance:" src/ tests/
```

To reproduce the chart:

```bash
uv run python -m uk_subsidy_tracker.plotting.subsidy.cfd_vs_gas_cost
```

To run a sensitivity scenario, call `compute_counterfactual()` with overrides:

```python
from uk_subsidy_tracker.counterfactual import (
    compute_counterfactual,
    CCGT_NEW_BUILD_CAPEX_OPEX_PER_MWH,
)

# new-build instead of existing fleet
cf = compute_counterfactual(
    non_fuel_opex_per_mwh=CCGT_NEW_BUILD_CAPEX_OPEX_PER_MWH,
)

# strip carbon tax entirely
cf = compute_counterfactual(carbon_prices={})
```
