# Remaining CfD obligations

**The contracts already signed will cost consumers at least £33 billion
more before they run out — and that's before a single new contract is
awarded.**

CfD contracts lock in a strike price for fifteen years (twenty from AR7
onwards). The oldest contracts run until the late 2030s. Nuclear
(Hinkley) runs 35 years. This chart shows the forward commitment from
contracts already in the ground.

![Remaining CfD obligations](../html/subsidy_remaining_obligations_twitter.png)

## The four panels

Two scenarios × two time views:

- **Columns** — *flat* (left) assumes current generation levels persist;
  *NESO growth* (right) scales generation with projected UK electricity
  demand growth (~30% by 2035, doubling by 2050).
- **Rows** — *annual* £bn/yr (top); *cumulative* £bn (bottom).

Each bar and area is decomposed by allocation round — Investment
Contracts (red), AR1 (blue), AR2 (green). Later rounds (AR4–AR6) have
too little generation history to project meaningfully and are omitted;
this *understates* the true forward cost.

## Headline figures

Total forward cost from 2026 onwards, under the flat scenario:

| Round | Units | Annual cost | Runs to |
|---|---:|---:|---:|
| Investment Contracts | 14 | £2.6bn/yr | 2038 |
| Allocation Round 1 | 22 | £0.7bn/yr | 2040 |
| Allocation Round 2 | 9 | £0.6bn/yr | 2039 |
| **Total (these rounds only)** | **45** | **£3.9bn/yr** | **2041** |

**Cumulative forward bill: ~£33 billion** in the flat scenario.
The NESO growth scenario pushes this higher as demand scaling lifts
generation volumes.

## What's *not* in this chart

This is only a floor. The £33bn excludes:

- **AR3 onwards (~300 projects)** — not enough generation history to
  project reliably. Most are offshore wind at £39–120/MWh strike prices
  (2012 money, CPI-indexed).
- **AR7 auction (~200 projects)** — being auctioned in 2026. First-ever
  20-year contracts.
- **Hinkley Point C** — £92.50/MWh (2012 money) for 35 years from
  commissioning. Not yet generating, so omitted from the chart. Sizewell
  C will add another large nuclear contract.
- **Drax 4-year biomass CfD (2027–2031)** — a separate new contract
  not included; only Drax's original Investment Contract is shown.

Realistic forward commitment, including everything signed and pending,
is comfortably north of £50bn.

## Methodology

For each unit with generating history:

```
avg_strike          = generation-weighted average strike price (historical)
avg_annual_gen      = total generation / number of years of operation
annual_cost         = avg_strike × avg_annual_gen
remaining_years     = contract_end_year - current_year
unit_forward_cost   = annual_cost × remaining_years
```

**Contract end year** uses `Expected_Start_Date` from the LCCC
portfolio dataset where available, falling back to first observed
generation date. Contract length is 15 years for renewables, 35 for
nuclear — the standard terms.

**Growth scenario** applies a linear interpolation of NESO's
*Future Energy Scenarios* demand projections (280 TWh in 2024, 390 TWh
in 2035, 692 TWh in 2050) as a multiplier on generation volumes.

## Caveats

- **Estimates, not forecasts.** Actual generation varies with weather.
  Strike prices are contractually fixed; volumes are not.
- **Growth scenario assumes CfD generation scales with total UK
  demand.** This is the government's stated plan but is not
  contractually guaranteed.
- **Contract length for Investment Contracts is assumed at 15 years.**
  These were individually negotiated and their exact terms are not
  publicly confirmed.
- **AR7's 20-year terms are not reflected** — these are existing
  contracts only. Every new AR7 contract will make future lock-in
  longer.

## Data & code

- **Generation data** — [LCCC Actual CfD Generation](https://www.lowcarboncontracts.uk/data-portal/dataset/actual-cfd-generation-and-avoided-ghg-emissions/actual-cfd-generation-and-avoided-ghg-emissions)
- **Portfolio data** — [LCCC CfD Contract Portfolio Status](https://www.lowcarboncontracts.uk/data-portal/dataset/cfd-contract-portfolio-status)
- **Demand projections** — [NESO Future Energy Scenarios](https://www.neso.energy/publications/future-energy-scenarios-fes)
- **Chart source** — [`src/uk_subsidy_tracker/plotting/subsidy/remaining_obligations.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/src/uk_subsidy_tracker/plotting/subsidy/remaining_obligations.py)

To reproduce:

```bash
uv run python -m uk_subsidy_tracker.plotting.subsidy.remaining_obligations
```

## See also

- [CfD dynamics](cfd-dynamics.md) — the cost of the contracts signed
  *so far*, decomposed into volume × price gap.
- [CfD vs Gas Cost](cfd-vs-gas-cost.md) — what consumers have already
  paid, broken down by cash-flow channel.
