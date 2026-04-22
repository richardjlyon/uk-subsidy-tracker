# Lorenz curve — 6 projects = 50% of CfD subsidy

**The inequality diagnostic applied to CfD payments. Six projects receive half the £29bn spent; eleven receive 80%. The renewables revolution is in practice a concentrated transfer to Drax and a handful of offshore wind stations.**

![Lorenz curve — CfD payment concentration](../../charts/html/subsidy_lorenz_twitter.png)

→ [Interactive version](../../charts/html/subsidy_lorenz.html)

## What the chart shows

A standard Lorenz curve built over CfD projects instead of households. The
x-axis is the cumulative share of projects (sorted from largest recipient
downwards); the y-axis is the cumulative share of total CfD levy payments.
A grey dashed diagonal marks the "equal distribution" reference where every
project would receive the same pound amount. The red filled curve is the
actual distribution — the further it bows below the diagonal, the more
concentrated the spending.

Two threshold annotations sit on the red curve: one marking the smallest
number of projects whose cumulative share of £ crosses **50%** (6 projects);
the other at **80%** (11 projects). The top three recipients by cumulative
payment are labelled by name — typically Drax (biomass Investment Contract),
followed by two offshore wind stations (Hornsea and Beatrice or Walney
depending on the vintage window). Exact £m figures are attached to each
marker.

## The argument

**Six projects receive 50% of all CfD subsidy. Eleven receive 80%. The
"renewables revolution" is a concentrated industrial-scale transfer to a
handful of offshore wind farms and one converted coal station.**

The headline framing of the CfD scheme — "supporting Britain's renewable
industry" — implies breadth. The arithmetic implies the opposite. Of roughly
~80 projects with positive net CfD payments to date, the top 6 alone capture
half the £29bn. One of those six is Drax, which is a biomass unit, not wind
or solar. Strip Drax out and the remainder is dominated by Investment-Contract-era
offshore wind built 2014–2019: Hornsea, Beatrice, Walney, East Anglia ONE,
Burbo Bank Extension. These are all very large single-owner sites operated
by three or four multinational developers (Ørsted, SSE, Iberdrola, Equinor).

This concentration is a feature of the subsidy design, not an accident of
the current fleet. Strike prices were set via competitive auction *per
project*, and the economics of offshore wind favour very large single
sites for capex efficiency. The result is that the CfD mechanism's total
spend is structurally dominated by a small number of very large contracts
— and adversarial readers should evaluate the scheme's merits *on those
contracts specifically*, not on the distributed "many small projects"
framing the policy is usually defended with.

The [cfd-payments-by-category](./cfd-payments-by-category.md) chart tells
the same story along the technology axis: Offshore Wind + Drax biomass
together account for the vast majority of cumulative spend. Whether you
slice by project or by technology, the concentration story is identical.

## Methodology

Source: LCCC *Actual CfD Generation and avoided GHG emissions* (daily
settlements; the full lifetime of the scheme to date).

```
by_unit = group(Name_of_CfD_Unit, Allocation_round)
        → sum(CFD_Payments_GBP)
by_unit = by_unit[payments > 0]           # filter positive-payment units
by_unit = sort_descending(payments)
cum_pct_payments   = cumulative_sum(payments) / total(payments) × 100
cum_pct_projects   = rank(unit) / n_units × 100
```

The two threshold annotations (50% and 80%) are computed as the smallest
rank whose `cum_pct_payments` first crosses the threshold —
`(cum_pct_payments >= threshold).argmax()` in numpy terms. Top-three labels
attach the raw £m figure to each of the first three ranked units.

No gas counterfactual is used. Lorenz is pure *attribution* of money
already spent: where did the £29bn go? See the Recipients theme
[methodology](./methodology.md) for the attribution rule (how
`CFD_Payments_GBP` maps to project identity via `Name_of_CfD_Unit` +
`Allocation_round`).

## Caveats

- **Positive-payment filter is load-bearing.** Units with net-negative
  payments over the window (i.e. net clawback back to consumers during
  the 2022 gas crisis for a small handful of high-strike contracts) are
  excluded — they received no net subsidy. Including them would break
  the monotonic sort Lorenz requires and distort the percentage baseline.
- **Multi-phase offshore wind farms are treated as separate recipients.**
  Hornsea Phase 1, Phase 2A, and Phase 2B each appear as their own
  `Name_of_CfD_Unit` because each is a separate contract with its own
  strike price and start date. A "single developer" view would collapse
  these, but the scheme's commercial mechanism is per-contract — the
  chart follows the mechanism.
- **2022 gas-crisis distortion.** During the 2022 price spike, many CfD
  contracts paid *back* to consumers for individual months
  (`CFD_Payments_GBP` < 0). Cumulative lifetime totals per unit remain
  positive for every unit shown; the negative monthly flows are folded
  into each unit's lifetime sum before the filter.
- **No Gini coefficient plotted.** The chart prioritises the "6 projects
  = 50%" threshold numbers as the adversarial payload; Gini is a derived
  single-number summary and can be re-computed from the same data on
  demand.

## Data & code

- **CfD data** — [LCCC Actual CfD Generation and avoided GHG emissions](https://www.lowcarboncontracts.uk/data-portal/dataset/actual-cfd-generation-and-avoided-ghg-emissions/actual-cfd-generation-and-avoided-ghg-emissions)
- **Chart source** — [`src/uk_subsidy_tracker/plotting/subsidy/lorenz.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/src/uk_subsidy_tracker/plotting/subsidy/lorenz.py)
- **Tests** —
  [`tests/test_schemas.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_schemas.py)
  (validates the LCCC *Actual CfD Generation* schema every chart reads),
  [`tests/test_aggregates.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_aggregates.py)
  (row-conservation pin on the groupby-sum pattern Lorenz relies on)

To reproduce:

```bash
uv run python -m uk_subsidy_tracker.plotting.subsidy.lorenz
```

## See also

- [CfD payments by category](./cfd-payments-by-category.md) — same
  concentration story sliced by technology instead of project.
- [Cost theme](../cost/index.md) — where the total £29bn pound figure
  lives, decomposed into wholesale + levy cash flows.
- [Recipients methodology](./methodology.md) — attribution rule + Gini
  supplementary formula.
