# Cost per UK household by scheme

**The annual subsidy bill divided by UK household count, decomposed by scheme.** Stacked-bar chart with one band per scheme; the divisor is the ONS UK households count for that calendar year (~26.7 million in 2014 rising to ~28.6 million in 2024). Per-household framing answers the "what does this cost me?" question concretely, and the divisor changes year-on-year so the chart is honest about denominator drift.

![UK renewable subsidy cost per household, decomposed by scheme](../charts/html/x3_per_household_twitter.png)

[Interactive version](../charts/html/x3_per_household.html){target="_blank"}

## What the chart shows

A stacked-bar time series. The x-axis is `Year`; the y-axis is `Cost per household (£)`. Each bar is split into colour-coded bands — one per scheme — and the bands stack to give the all-scheme covered total cost per UK household for that year. Pre-2014 bars are absent because the ONS Families and Households time series begins in 2014 (the underlying RO data extends back to 2006, but the per-household denominator does not).

The chart subtitle states the partial-coverage and denominator-source posture: covers 2 of 8 schemes; ONS UK households-count denominator — see methodology. The denominator is per-year, not a single fixed value.

## The argument

This chart converts billions of pounds into a per-bill-payer figure.

1. Per-household framing answers the "what does this cost me?" question without mediation. £8 bn is an abstract number; £300 per household is a concrete one. The bands show how that £300 is split between the Renewables Obligation and Contracts for Difference contributions; see [Contracts for Difference](../schemes/cfd.md) and [Renewables Obligation](../schemes/ro.md) for the per-scheme detail.
2. The divisor changes year-on-year, so the stack is honest about denominator drift. A flat denominator would understate early-year per-household figures (when there were ~7% fewer UK households than today) and overstate the historical comparison. Per-year ONS counts give the right conversion.
3. The coverage gap (six of eight schemes not yet in the stack) means the per-household figure shown is a lower bound for total UK renewable subsidy per household. The bar height grows automatically as Phase 7-12 schemes add their bands; readers should not interpret the current bar height as the all-renewables UK figure.
4. The pre-2014 omission is documented, not extrapolated. The ONS Families and Households series begins 2014; pre-2014 RO bars are absent. The cumulative cost across 2006–2013 remains in `cross_scheme.parquet` and is read directly on X1 — only the per-household ratio drops out before 2014.

## Methodology

The chart is built by `src/uk_subsidy_tracker/plotting/portal/x3_per_household.py`. The computation is:

```python
# Computation sketch (from src/uk_subsidy_tracker/plotting/portal/x3_per_household.py)
import pandas as pd
df = pd.read_parquet("data/derived/portal/cross_scheme.parquet")
# Drop rows without a households denominator (pre-2014 RO bars):
df = df[df["households_uk"].notna() & (df["households_uk"] > 0)]
df["per_household_gbp"] = df["cost_gbp"] / df["households_uk"]
```

The per-row `households_uk` value carries the ONS UK households count for the row's `year`. For RO obligation-year start (e.g. `year=2019` = SY18 = April 2019 to March 2020), the matching ONS year is the obligation-year start calendar year (CY 2019). This year-matching rule is documented in detail in the [cross-scheme methodology — per-household division convention](./methodology.md#per-household-division-convention).

The denominator is sourced from ONS *Families and Households* 2025 edition (URL + sha256 + retrieved-on date in the [methodology page](./methodology.md)).

## Caveats

- **Pre-2014 omission.** ONS Families and Households series begins 2014. Pre-2014 RO bars (2006-2013) are absent from this chart. The cumulative cost is preserved in `cross_scheme.parquet` and visible on X1.
- **Covered-only.** Only Contracts for Difference and the Renewables Obligation are stacked today; the per-household figure shown is a lower bound for total UK renewable subsidy per household. Phase 7-12 schemes will add new bands.
- **UK total denominator.** The ONS UK households count is the all-UK total (single-family + multi-family + lone-person). This is not a per-region (England-only, GB-only) denominator — even though the RO module is GB-only, the per-household figure uses UK total households for cross-scheme comparability.
- **Year-matching rule.** Each `cross_scheme.parquet` row uses the ONS households count for its `year` value. RO obligation-year-start convention is documented in the methodology page; the rule does not split households across the obligation-year window.
- **ONS series revisions.** ONS occasionally revises the Families and Households series; the in-code dict is checked against the source XLSX by `tests/test_constants_provenance.py` so any drift produces a failing test.

## Data & code

**GOV-01 four-way coverage** — every PRODUCTION chart on this site links to its primary source, source code, test, and reproduce instructions:

1. **Primary source data:** `data/derived/portal/cross_scheme.parquet` — joined from per-scheme `annual_summary.parquet` outputs and the ONS households dict. Provenance + sha256 in [`manifest.json`](../data/index.md).
2. **Chart source code:** [`src/uk_subsidy_tracker/plotting/portal/x3_per_household.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/src/uk_subsidy_tracker/plotting/portal/x3_per_household.py)
3. **Test:** [`tests/test_aggregates.py::test_cross_scheme_row_conservation`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_aggregates.py) — row-conservation gate; [`tests/test_benchmarks.py::test_ref_total_reconciliation`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_benchmarks.py) — REF Constable cross-check (Wave 7).
4. **Reproduce locally:**
   ```bash
   git clone https://github.com/richardjlyon/uk-subsidy-tracker.git
   cd uk-subsidy-tracker
   uv sync
   uv run python -m uk_subsidy_tracker.plotting.portal.x3_per_household
   ```

## See also

- [Cross-scheme methodology — per-household division convention](./methodology.md#per-household-division-convention) — ONS source URL, sha256, retrieved-on date, year-matching rule, pre-2014 omission rationale.
- [Contracts for Difference](../schemes/cfd.md) — per-scheme deep dive.
- [Renewables Obligation](../schemes/ro.md) — per-scheme deep dive.
