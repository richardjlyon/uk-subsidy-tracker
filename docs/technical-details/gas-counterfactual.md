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
carbon  =  UK_ETS_£_per_tCO2 × (0.184 / 0.55)
O&M     =  £5 / MWh   (existing fleet, capex sunk)
```

Each daily £/MWh is multiplied by the actual daily CfD generation (MWh) and
summed to monthly, then cumulative, totals.

| Term | Source | Value |
|------|--------|-------|
| Gas price | [ONS System Average Price of gas](https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/gk36/mm22) | Daily, p/kWh thermal |
| CCGT efficiency | Modern H-class CCGT typical rating | 55% |
| Gas CO₂ intensity | Natural gas combustion | 0.184 tCO₂/MWh thermal |
| Carbon price | EU ETS (2018–20) → UK ETS (2021+), annual average | £13–£53/tCO₂ |
| O&M | BEIS *Electricity Generation Costs 2023*, Table ES.1 | £5/MWh |

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

All figures are cumulative totals over Jun 2016 – Apr 2026 against £29.2bn
of actual CfD electricity cost (wholesale + levy).

| Scenario | O&M (£/MWh) | Carbon tax | Gas alternative | Premium vs CfD |
|---|---|---|---|---|
| **Default (existing fleet)** | 5 | UK ETS | **£14.3bn** | **£14.9bn** |
| Fuel + carbon, no O&M | 0 | UK ETS | £9.3bn | £19.9bn |
| Fuel only (no carbon, no O&M) | 0 | — | £10.9bn* | £18.3bn |
| New-build (capex + O&M) | 20 | UK ETS | £17.2bn | £12.0bn |
| No carbon tax, existing O&M | 5 | — | £11.9bn | £17.3bn |

<sup>*Fuel-only figure is higher than fuel+no-O&M because the latter retains
the carbon tax term. The "no carbon, no O&M" scenario is the hypothetical
minimum; all realistic variants sit between £12bn and £17bn.</sup>

The choice of O&M and carbon-price assumptions moves the cumulative gas
alternative within a **£12–17bn band**. The actual CfD cost (£29bn) sits
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

The full calculation lives in [`src/cfd_payment/counterfactual.py`](https://github.com/richlyon/cfd-payment/blob/main/src/cfd_payment/counterfactual.py).

Key constants:

- `CCGT_EFFICIENCY = 0.55`
- `GAS_CO2_INTENSITY_THERMAL = 0.184`  (tCO₂/MWh thermal)
- `CCGT_EXISTING_FLEET_OPEX_PER_MWH = 5.0`
- `CCGT_NEW_BUILD_CAPEX_OPEX_PER_MWH = 20.0`
- `DEFAULT_CARBON_PRICES`  (dict keyed by year)

To reproduce the chart:

```bash
uv run python -m cfd_payment.plotting.subsidy.cfd_vs_gas_cost
```

To run a sensitivity scenario, call `compute_counterfactual()` with overrides:

```python
from cfd_payment.counterfactual import (
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
