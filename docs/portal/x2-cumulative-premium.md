# Cumulative premium over gas — covered schemes

**The accumulated premium UK consumers have paid above the gas counterfactual.** Each year's premium contribution is summed across covered schemes, then accumulated to show the running total premium since the chart's start year. The premium is the difference between actual scheme cost and the cost of generating the same MWh from a CCGT fleet at the gas + carbon prices that actually occurred.

![Cumulative premium over gas across covered UK renewable subsidy schemes](../charts/html/x2_cumulative_premium_twitter.png)

[Interactive version](../charts/html/x2_cumulative_premium.html){target="_blank"}

## What the chart shows

A single-line cumulative time series. The x-axis is `Year`; the y-axis is `Cumulative premium (£bn)`. The line starts at zero in the chart's start year and rises monotonically in years where the cross-scheme premium is positive (covered schemes cost more than the gas counterfactual that year). In years where premium is negative — schemes saved consumers money relative to gas — the line dips but the cumulative does not reverse direction.

The chart subtitle states the partial-coverage posture: covers 2 of 8 schemes — see scheme grid for coverage status. The line aggregates all covered schemes per year before accumulating; reads as "what has the UK paid above the gas baseline?" across the full Renewables Obligation + Contracts for Difference window.

## The argument

This chart isolates the policy-relevant question: what is the cumulative cost above the do-nothing baseline?

1. The cumulative line shows when each scheme begins to dominate the premium. Pre-2016, the line is RO-only (the CfD scheme had not yet started settlements); post-2016, both schemes contribute. The Renewables Obligation is the larger single-scheme contributor to the cumulative premium across the full window.
2. Negative single-year premium — for example CfD 2022, where wholesale prices exceeded strike prices and CfD generators paid back to consumers — reduces the cumulative slope but does not reverse the cumulative total. The 2022 gas-crisis context is documented on [Contracts for Difference](../schemes/cfd.md) and analysed in detail on [X5 2022 gas crisis](x5-2022-crisis.md).
3. Cross-scheme aggregation is the correct axis for the policy question "what has UK paid above the gas baseline?" — single-scheme premium charts answer "did this scheme cost more than gas?" but only the cross-scheme accumulation answers the cost-of-the-policy-portfolio question.
4. As Phase 7-12 schemes ship, new schemes' premium contributions are added to `cross_scheme.parquet` and the cumulative line updates automatically on the next refresh.

## Methodology

The chart is built by `src/uk_subsidy_tracker/plotting/portal/x2_cumulative_premium.py`. The computation is:

```python
# Computation sketch (from src/uk_subsidy_tracker/plotting/portal/x2_cumulative_premium.py)
import pandas as pd
df = pd.read_parquet("data/derived/portal/cross_scheme.parquet")
# Sum premium across schemes per year, then cumulative-sum:
yearly_premium = df.groupby("year")["premium_gbp"].sum().sort_index()
cumulative_bn = yearly_premium.cumsum() / 1e9
```

The per-row `premium_gbp` value is computed by each scheme module — see `src/uk_subsidy_tracker/counterfactual.py::compute_counterfactual()` and the [gas counterfactual methodology](../methodology/gas-counterfactual.md) for the formula (fuel + carbon + O&M against the CCGT existing-fleet baseline). The `methodology_version` column in `cross_scheme.parquet` is pinned per row so any methodology bump is auditable in `CHANGES.md`.

Sign convention: positive `premium_gbp` means the scheme cost more than gas in that year; negative means the scheme was cheaper than gas. The cumulative line therefore can flatten (or briefly dip) in negative-premium years.

## Caveats

- **Covered-only.** The cumulative is for Contracts for Difference + Renewables Obligation only; it is not a UK-wide total renewable-premium figure. Phase 7-12 schemes will add to the line as they ship.
- **Sign convention.** Positive = subsidy above gas; negative = scheme cheaper than gas. The cumulative line monotonically rises only in years where every covered scheme is positive on aggregate.
- **Scheme-year vs calendar-year join.** RO `year` is the obligation-year start calendar year; CfD `year` is the calendar-year settlement anchor. See the [cross-scheme methodology](./methodology.md) for the reconciliation rule.
- **Cumulative resets to zero on chart-start year.** The line is cumulative from the earliest year present in `cross_scheme.parquet` (2006 today, RO-only); pre-2006 RO costs are not in scope for this project.
- **Gas counterfactual sensitivity.** The gas baseline depends on assumed CCGT efficiency (55%), O&M (£5/MWh existing fleet), and per-year carbon-price values. Sensitivity analysis on the [gas counterfactual page](../methodology/gas-counterfactual.md) shows the cumulative gas-alternative figure varies in an £11–17bn band under plausible assumption changes.

## Data & code

**GOV-01 four-way coverage** — every PRODUCTION chart on this site links to its primary source, source code, test, and reproduce instructions:

1. **Primary source data:** `data/derived/portal/cross_scheme.parquet` — joined from per-scheme `annual_summary.parquet` outputs. Provenance + sha256 in [`manifest.json`](../data/index.md).
2. **Chart source code:** [`src/uk_subsidy_tracker/plotting/portal/x2_cumulative_premium.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/src/uk_subsidy_tracker/plotting/portal/x2_cumulative_premium.py)
3. **Test:** [`tests/test_aggregates.py::test_cross_scheme_row_conservation`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_aggregates.py) — row-conservation gate; [`tests/test_benchmarks.py::test_ref_total_reconciliation`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_benchmarks.py) — REF Constable cross-check (Wave 7).
4. **Reproduce locally:**
   ```bash
   git clone https://github.com/richardjlyon/uk-subsidy-tracker.git
   cd uk-subsidy-tracker
   uv sync
   uv run python -m uk_subsidy_tracker.plotting.portal.x2_cumulative_premium
   ```

## See also

- [Cross-scheme methodology](./methodology.md) — aggregation rules, partial-coverage caveat, per-row methodology versioning.
- [Gas counterfactual](../methodology/gas-counterfactual.md) — formula, constants, sensitivity analysis, source provenance.
- [Contracts for Difference](../schemes/cfd.md) — 2022 negative-premium year context.
- [Renewables Obligation](../schemes/ro.md) — long-window cumulative-premium contributor.
