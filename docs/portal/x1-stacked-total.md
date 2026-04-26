# Total UK subsidy stacked by scheme

**The full UK renewable-subsidy bill, scheme by scheme, year by year.** This stacked-bar chart shows annual subsidy by scheme since 2006 (Renewables Obligation) and 2016 (Contracts for Difference). Each band is a separate scheme reconstructed from primary regulator data; only schemes with full coverage are shown, so the visible stack today represents two of the eight UK renewable subsidy schemes.

![Total UK subsidy stacked by scheme — covered schemes only](../charts/html/x1_stacked_total_twitter.png)

[Interactive version](../charts/html/x1_stacked_total.html){target="_blank"}

## What the chart shows

A stacked-bar time series. The x-axis is `Year`; the y-axis is `Subsidy cost (£bn)` aggregated annually. Each bar is split into colour-coded bands — one band per scheme — and the bands stack to give the all-scheme covered total for that year. The Renewables Obligation band (red) extends back to 2006; the Contracts for Difference band (blue) joins from 2016 onward.

The chart subtitle states the partial-coverage posture explicitly: covers 2 of 8 schemes — see the scheme grid for coverage status. The interactive HTML carries native Plotly rangeselector buttons (1y / 5y / All) on the date-typed x-axis so readers can isolate recent years; the static PNG hero shows the All-time view for embeddability and social-media sharing.

The chart has no benchmark line, no greyed-out "data pending" bands, and no synthetic numbers. Every visible coloured band is real reconstructed data from the per-scheme `annual_summary.parquet` outputs joined into `cross_scheme.parquet`.

## The argument

This chart anchors the cross-scheme cost story.

1. Of the two schemes shipped, the Renewables Obligation is by far the larger cumulative contributor. Its band extends back over a decade further than CfD and is consistently the taller layer in years where both schemes are present. See [Renewables Obligation](../schemes/ro.md) for the per-scheme deep dive.
2. Contracts for Difference ramps fast post-2016 and quickly becomes a material annual contributor — the policy mechanism shifted the marginal renewable subsidy from the RO to CfD, but RO obligations contracted before 2017 continue to roll forward to 2037. See [Contracts for Difference](../schemes/cfd.md) for the strike-price + 15-year-commitment context.
3. The total annual UK renewable-subsidy bill for the two covered schemes alone is in the £8–10 bn band in recent years. The cross-scheme grand total once Phases 7-12 ship will be larger; the X1 stack will grow automatically as new bands are added to `cross_scheme.parquet`.
4. The "covers 2 of 8 schemes" caveat is structural: it is not noise added late in the chart, it is the project's posture wherever a number is shown. Hostile readers cannot accuse this site of hiding the gap, because the gap is stated in the subtitle.

## Methodology

The chart is built by `src/uk_subsidy_tracker/plotting/portal/x1_stacked_total.py`. The data path is:

```python
# Computation sketch (from src/uk_subsidy_tracker/plotting/portal/x1_stacked_total.py)
import pandas as pd
df = pd.read_parquet("data/derived/portal/cross_scheme.parquet")
# Plotly stacked-bar requires a date-typed x-axis for the rangeselector to work,
# so coerce the int64 year column at the plotting boundary (D-21 determinism is
# preserved on disk; the coercion is in-memory only):
df["year_dt"] = pd.to_datetime(df["year"], format="%Y")
# One trace per scheme; bars stack at each year via Plotly's barmode="stack":
for scheme, group in df.groupby("scheme"):
    fig.add_bar(x=group["year_dt"], y=group["cost_gbp"] / 1e9, name=scheme,
                marker_color=SCHEME_COLORS[scheme])
```

Scheme-year alignment: RO `year` is the obligation-year start calendar year (SY18 = `year=2019`); CfD `year` is the calendar-year settlement-month anchor. The 9-month overlap between the two windows is documented in the [cross-scheme methodology](./methodology.md). Both schemes are stacked at their respective `year` values without further normalisation — a deeper axis-convention rationalisation across all eight schemes is deferred to a future phase.

## Caveats

- **Covers 2 of 8 schemes.** Only Contracts for Difference and the Renewables Obligation are shipped today. The remaining six (FiT, Constraint Payments, Capacity Market, Balancing Services, Grid Socialisation, Smart Export Guarantee) ship in Phases 7-12 and will appear as new stacked bands automatically.
- **Scheme-year vs calendar-year mismatch.** RO `year=2019` corresponds to SY18 (April 2019 – March 2020); CfD `year=2019` corresponds to CY 2019 (January – December 2019). The 9-month overlap is documented in the methodology page.
- **Rangeselector buttons appear in HTML only.** The static PNG hero shows the All-time view for embeddability; the 1y / 5y / All buttons are native Plotly controls on the interactive HTML page only.
- **Negative single-year contributions are possible.** During the 2022 gas crisis, CfD `cost_gbp` went briefly negative as wholesale prices exceeded strike prices; the band shrinks below zero in that year. Stacked-bar semantics handle the negative band cleanly.

## Data & code

**GOV-01 four-way coverage** — every PRODUCTION chart on this site links to its primary source, source code, test, and reproduce instructions:

1. **Primary source data:** `data/derived/portal/cross_scheme.parquet` — joined from per-scheme `annual_summary.parquet` outputs. Provenance + sha256 in [`manifest.json`](../data/index.md).
2. **Chart source code:** [`src/uk_subsidy_tracker/plotting/portal/x1_stacked_total.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/src/uk_subsidy_tracker/plotting/portal/x1_stacked_total.py)
3. **Test:** [`tests/test_aggregates.py::test_cross_scheme_row_conservation`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_aggregates.py) — row-conservation gate; [`tests/test_benchmarks.py::test_ref_total_reconciliation`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_benchmarks.py) — REF Constable cross-check (Wave 7).
4. **Reproduce locally:**
   ```bash
   git clone https://github.com/richardjlyon/uk-subsidy-tracker.git
   cd uk-subsidy-tracker
   uv sync
   uv run python -m uk_subsidy_tracker.plotting.portal.x1_stacked_total
   ```

## See also

- [Cross-scheme methodology](./methodology.md) — aggregation rules, scheme-year vs calendar-year reconciliation, partial-coverage caveat.
- [Contracts for Difference](../schemes/cfd.md) — per-scheme deep dive (strike prices, 15-year commitments, technology mix).
- [Renewables Obligation](../schemes/ro.md) — per-scheme deep dive (ROC pricing, obligation-year structure, 2002-2037 span).
