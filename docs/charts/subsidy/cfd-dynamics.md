# The CfD mechanism in four panels

**Volume × price gap = bill. Each panel is a direct consequence of the
one above it.**

This is the diagnostic chart. It exposes the full cost mechanism of the
CfD scheme — how much electricity was generated, what consumers paid per
MWh for it, what gas would have cost instead, and the cumulative
premium that gap represents.

![CfD dynamics — the full mechanism in four panels](../html/subsidy_cfd_dynamics_twitter.png)

## The four panels

**Panel [1] — Monthly generation (TWh).** The volume multiplier. Fleet
growth is visible as rising bar heights, with a clear seasonal wind
signal (winter peaks, summer troughs).

**Panel [2] — Unit prices (£/MWh).** The mechanism itself. Blue is the
fleet-weighted strike price consumers pay for every CfD MWh. Orange is
the generation-weighted gas counterfactual — what the same MWh would
have cost from the existing UK CCGT fleet. The shaded blue gap between
them is the per-MWh cost of the policy.

**Panel [3] — Premium per MWh (£/MWh).** Strike minus counterfactual.
**Red** when consumers overpay relative to gas; **green** when the
scheme is genuinely cheaper. Watch 2022 dip toward zero — but never
below it.

**Panel [4] — Cumulative premium (£bn).** Running total of
`premium_per_mwh × generation` since the scheme began. This is the bill
consumers paid *over and above* what the existing gas fleet would have
cost for the same electricity. Endpoint currently **£14.1bn**.

## What the chart reveals

The CfD shield does not work. In every year of the scheme's operation
the blue line has sat above the orange line — *including 2022*, the
worst gas crisis in living memory. The one year the two nearly
converged, CfD electricity still cost consumers 7% more than gas would
have.

In normal years — 2018, 2019, 2020, 2023, 2024, 2025 — CfD electricity
has cost roughly **2× the gas alternative**. In 2020, when gas was
cheap, it cost **5×**. The scheme was sold as protection from crisis
prices. What it actually did was take the ceiling of volatility and
turn it into the floor of consumer bills.

Panel [4]'s red cumulative curve tells the cost of that policy
choice: ~£14bn more than consumers would have paid for the same
electricity from the gas fleet Britain already owned.

## How the numbers stack

For each day:

```
strike_price        = fleet-weighted strike across generating CfD units
counterfactual      = fuel (gas_p/kWh × 10 / 0.55)
                    + carbon (UK_ETS × 0.184 / 0.55)
                    + £5/MWh O&M (existing CCGT fleet)
premium_per_mwh     = strike - counterfactual
premium_gbp         = premium_per_mwh × CFD_Generation_MWh
```

Monthly aggregation weights by generation. The cumulative in panel [4]
is the running sum of daily `premium_gbp`.

## Caveats

- **Early period excluded.** Days before Jan 2018 have no gas
  counterfactual (ONS/UK ETS coverage starts then), so ~5.6 TWh of
  early 2016–17 generation is excluded. Including it would add at most
  ~£0.4bn to the cumulative figure.
- **Gas counterfactual assumes existing-fleet economics.** Capex sunk,
  £5/MWh O&M. Using new-build gas (~£20/MWh all-in) would reduce the
  premium by ~£2bn over the same window. The direction of the result
  is robust to this choice; the magnitude is not.
- **Assumes gas supply at observed wholesale prices.** In reality,
  displacing CfDs with ~150 TWh of additional gas demand would likely
  push gas prices up. This biases the counterfactual *cheaper* than
  the real displacement case would be.

## Data & code

- **CfD data** — [LCCC Actual CfD Generation and avoided GHG emissions](https://www.lowcarboncontracts.uk/data-portal/dataset/actual-cfd-generation-and-avoided-ghg-emissions/actual-cfd-generation-and-avoided-ghg-emissions)
- **Gas price** — [ONS System Average Price of gas](https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/gk36/mm22)
- **Carbon price** — [UK ETS auction results (GOV.UK)](https://www.gov.uk/government/publications/participating-in-the-uk-ets)
- **Chart source** — [`src/cfd_payment/plotting/subsidy/cfd_dynamics.py`](https://github.com/richardjlyon/cfd-payment/blob/main/src/cfd_payment/plotting/subsidy/cfd_dynamics.py)
- **Counterfactual model** — [`src/cfd_payment/counterfactual.py`](https://github.com/richardjlyon/cfd-payment/blob/main/src/cfd_payment/counterfactual.py)

To reproduce:

```bash
uv run python -m cfd_payment.plotting.subsidy.cfd_dynamics
```

## See also

- [CfD vs Gas Cost](cfd-vs-gas-cost.md) — the same story decomposed into
  real cash flows (wholesale + levy) vs hypothetical gas alternative.
- [Remaining Obligations](remaining-obligations.md) — what the
  contracts already signed will cost from here on.
- [Gas counterfactual](../../technical-details/gas-counterfactual.md) —
  full methodology for the orange line.
