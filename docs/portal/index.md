# Portal — Cross-scheme analysis

The Portal tier brings every shipped UK renewable subsidy scheme into a single comparative view. Five flagship charts read from `data/derived/portal/cross_scheme.parquet` — a long-format, scheme-year-grain canonical aggregation table — and present the cross-scheme cost story: total subsidy stacked by scheme, cumulative premium over gas, cost per UK household, cost per MWh of subsidised generation, and a 2022 gas-crisis premium-per-MWh comparison across schemes.

## How to read this section

Each X-chart on this site has its own narrative page following the same six-section template — headline + chart embed, what the chart shows, the argument, methodology, caveats, and data + code provenance.

Read in order:

- [X1 Total subsidy stacked by scheme](x1-stacked-total.md) first, for the headline cost story year by year.
- [X2 Cumulative premium over gas](x2-cumulative-premium.md) accumulates the year-on-year premium since the chart's start year.
- [X3 Cost per household by scheme](x3-per-household.md) puts the bill into per-bill-payer terms using the ONS UK households-count denominator.
- [X4 Cost per MWh by scheme](x4-cost-per-mwh.md) isolates unit economics from volume effects.
- [X5 2022 gas crisis](x5-2022-crisis.md) tests each scheme's contract structure against the crisis-year gas spike (2021 / 2022 / 2023 grouped bars).

The shared [Cross-scheme methodology](methodology.md) page documents the join semantics, the scheme-year vs calendar-year reconciliation rule, the per-household division convention, the no-gas-counterfactual exclusion list (Capacity Market, Balancing Services, Grid Socialisation), and the partial-coverage caveat.

## What is currently shipped

- **Contracts for Difference (CfD)** — covered (Phase 5 + 05.1).
- **Renewables Obligation (RO)** — covered (Phases 5 + 05.2).
- Six remaining schemes — coming in Phases 7-12 (FiT, Constraint Payments, Capacity Market, Balancing Services, Grid Socialisation, Smart Export Guarantee).

The X-chart stacks and lines grow automatically as Phases 7-12 add scheme rows to `cross_scheme.parquet`. Every visible band is real reconstructed data; the partial-coverage gap is documented in chart subtitles and on the methodology page rather than hidden behind greyed-out placeholder bars.

## See also

- [Cross-scheme methodology](methodology.md) — aggregation rules, scheme-year vs calendar-year reconciliation, per-household division convention, partial-coverage caveat, reproducibility command.
- [Scheme detail pages](../schemes/index.md) — per-scheme deep dives for Contracts for Difference and Renewables Obligation.
- [Data downloads](../data/index.md) — `manifest.json`, Parquet + CSV mirrors, citation templates, SHA-256 verification.
