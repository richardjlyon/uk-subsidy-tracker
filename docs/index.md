# CfD Payment Analysis

An independent, data-driven audit of the UK Contracts for Difference
renewable-energy subsidy scheme, built from public LCCC, ONS, and UK
ETS data.

![CfD dynamics — the full mechanism in four panels](charts/html/subsidy_cfd_dynamics_twitter.png)

**Ten years into the scheme, UK consumers have paid £29 billion for
CfD electricity — roughly £14 billion more than the same MWh would
have cost from the gas fleet Britain already owned.** The premium is
paid every month. In only one year — 2022, the worst gas crisis in
living memory — did CfD electricity come close to matching the gas
alternative, and even then it still cost 7% more.

This site documents the methodology, data sources, and code behind
that conclusion, and presents the charts that substantiate it.

## What are CfDs?

A **Contract for Difference** guarantees a fixed price per MWh — the
*strike price* — to a renewable generator for fifteen years. The
electricity still sells into the wholesale market at a variable
*reference price*. When reference falls below strike, consumers top up
the difference through a levy. When reference rises above strike, the
generator pays the difference back. Total cost to the consumer: the
strike price. Always. Regardless of what gas is doing.

The generator is insulated from market risk. The consumer pays the
strike price — no more, no less. The consumer was never promised
anything about the *level* of that stable price.

## The three charts

1. **[CfD dynamics](charts/subsidy/cfd-dynamics.md)** — the mechanism
   exposed in four panels: volume, unit prices, premium, cumulative
   bill.
2. **[CfD vs Gas Cost](charts/subsidy/cfd-vs-gas-cost.md)** — the
   same money decomposed into the two cash-flow channels consumers
   actually pay through.
3. **[Remaining Obligations](charts/subsidy/remaining-obligations.md)**
   — what the contracts already signed will cost from here on
   (£33bn+).

See the [Charts overview](charts/index.md) for how they relate.

## Data sources

All analysis is built from public data:

- **[LCCC](https://www.lowcarboncontracts.uk/)** — actual CfD generation,
  strike and reference prices, payment flows, contract portfolio
- **[ONS](https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/gk36/mm22)** — System Average Price of gas (wholesale)
- **[UK ETS](https://www.gov.uk/government/publications/participating-in-the-uk-ets)** — carbon auction prices
- **[NESO](https://www.neso.energy/publications/future-energy-scenarios-fes)** — demand projections (forward scenarios)

The gas counterfactual methodology — how "what gas would have cost"
is computed — is documented in detail at
[Gas counterfactual](methodology/gas-counterfactual.md).

## Code & reproducibility

Everything on this site is reproducible from the source repository:

```bash
git clone https://github.com/richardjlyon/uk-subsidy-tracker
cd uk-subsidy-tracker
uv sync
uv run python -m uk_subsidy_tracker.plotting    # regenerate all charts
uv run mkdocs serve                      # serve this site locally
```

Source: [github.com/richardjlyon/uk-subsidy-tracker](https://github.com/richardjlyon/uk-subsidy-tracker).

## Status

A work in progress. The three charts above are production; supporting
analyses (capacity factor, intermittency, cannibalisation) are in the
source repo but not yet documented here. Corrections and contributions
welcome via [GitHub Issues](https://github.com/richardjlyon/uk-subsidy-tracker/issues).
