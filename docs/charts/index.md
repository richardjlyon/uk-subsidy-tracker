# Charts

This section presents the three production charts analysing the UK
Contracts for Difference (CfD) scheme. They are designed to be read
in order — each answers a different question about the same data.

| Chart | Question it answers |
|---|---|
| [CfD dynamics](subsidy/cfd-dynamics.md) | *How* does the cost arise — volume × price gap? |
| [CfD vs Gas Cost](subsidy/cfd-vs-gas-cost.md) | *Who* paid, and through which cash-flow channel? |
| [Remaining Obligations](subsidy/remaining-obligations.md) | *How much* more is already locked in? |

## Start here: the 4-panel diagnostic

[![CfD dynamics preview](html/subsidy_cfd_dynamics_twitter.png)](subsidy/cfd-dynamics.md)

[CfD dynamics](subsidy/cfd-dynamics.md) exposes the full cost mechanism
in four stacked panels: generation volume, unit prices (strike vs gas
counterfactual), per-MWh premium, and cumulative bill. Read top to
bottom; each panel is a consequence of the one above.

## Then: decompose the cash flows

[![CfD vs Gas Cost preview](html/subsidy_cfd_vs_gas_total_twitter.png)](subsidy/cfd-vs-gas-cost.md)

[CfD vs Gas Cost](subsidy/cfd-vs-gas-cost.md) splits the total cost of
CfD electricity into the two channels consumers pay through: the
wholesale price on the electricity bill, and the CfD levy on the
Supplier Obligation line. The gas counterfactual is drawn as a
reference line — real money flows distinguished from hypothetical ones.

## Finally: the forward bill

[![Remaining Obligations preview](html/subsidy_remaining_obligations_twitter.png)](subsidy/remaining-obligations.md)

[Remaining Obligations](subsidy/remaining-obligations.md) shows the
minimum forward commitment from contracts already signed — at least
£33bn more, running to 2041. Excludes AR7 (auctioning 2026) and AR3–AR6
projects not yet generating.

## Conventions

All charts:

- use publicly available data (LCCC, ONS, UK ETS, NESO);
- aggregate daily → monthly to preserve gas-price spikes while keeping
  the chart legible;
- are built with [Plotly](https://plotly.com/python/) and exported as
  both interactive HTML (`docs/charts/html/*.html`) and
  Twitter-optimised PNG (1200×675, `docs/charts/html/*_twitter.png`);
- compute the gas counterfactual identically — see
  [Gas counterfactual](../technical-details/gas-counterfactual.md).

## Reproducing

All charts are regenerated from public data by a single command:

```bash
uv run python -m cfd_payment.plotting
```

Or an individual chart:

```bash
uv run python -m cfd_payment.plotting.subsidy.cfd_dynamics
```

Source: [github.com/richardjlyon/cfd-payment](https://github.com/richardjlyon/cfd-payment).
