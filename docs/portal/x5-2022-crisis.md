# 2022 gas crisis — premium per MWh by scheme

**Did each scheme work as intended during the 2022 gas crisis?** Grouped-bar chart showing premium per MWh of subsidised generation in 2021 / 2022 / 2023, by scheme. The crisis-year contrast reveals which schemes saved consumers money (negative premium) and which still cost more than gas during the spike.

![2022 gas crisis: premium per MWh by scheme, comparing 2021 / 2022 / 2023](../charts/html/x5_2022_crisis_twitter.png)

[Interactive version](../charts/html/x5_2022_crisis.html){target="_blank"}

## What the chart shows

A grouped vertical-bar chart. The x-axis is `Scheme` (Contracts for Difference, Renewables Obligation, with Phase 7-12 schemes added once they ship — excluding those without a gas counterfactual); the y-axis is `Premium per MWh (£/MWh)`. For each scheme, three grouped bars show the premium-per-MWh figure for 2021, 2022, and 2023 in chronological order, with the 2022 bar emphasised in red as the crisis-year marker (2021 and 2023 use a context-grey colour).

The chart subtitle states the year window and exclusion posture: 2021 / 2022 / 2023 grouped bars; schemes without gas counterfactual excluded.

## The argument

The 2022 gas crisis tested every scheme's contract structure differently.

### 2021 vs 2022 vs 2023

1. **Contracts for Difference 2022 — scheme paid OUT to consumers.** When wholesale prices exceeded the strike-price floor, CfD generators returned the difference to the consumer-funded settlement levy. The 2022 CfD bar is negative (premium per MWh below zero), which is the scheme working as designed: see [Contracts for Difference](../schemes/cfd.md) for the "7% saved at crisis peak" framing in the per-scheme detail.
2. **Renewables Obligation 2022 — premium spiked because the gas baseline rose.** The RO contract structure does not respond to gas price (ROC certificates trade on a separate market mechanism); the gas-counterfactual baseline rose with the wholesale-gas price spike, so the *premium* (RO cost minus gas baseline) spiked higher even though RO cost itself was approximately structural. This is not the scheme failing — it is the scheme being structurally insensitive to the gas-price input that drives the premium calculation.
3. **Cross-scheme reading.** The grouped-bar arrangement makes the contrast visible at a glance: CfD's 2022 bar dips below zero while RO's 2022 bar rises. The two schemes responded to the same gas-price spike with opposite premium signs. Phase 7-12 schemes will add their own bar groups; FiT (fixed export tariff) is expected to behave like RO; Smart Export Guarantee (variable tariff) is expected to behave more like CfD.
4. The 3-year window is short by design — the contrast is the policy story, not a long-run trend.

## Methodology

The chart is built by `src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py`. The computation is:

```python
# Computation sketch (from src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py)
import pandas as pd
EXCLUDED_SCHEMES = frozenset({"Capacity Market", "Balancing Services", "Grid Socialisation"})
CRISIS_YEARS = (2021, 2022, 2023)
df = pd.read_parquet("data/derived/portal/cross_scheme.parquet")
df = df[df["year"].isin(CRISIS_YEARS)]
df = df[~df["scheme"].isin(EXCLUDED_SCHEMES)]
df = df[df["generation_mwh"].notna() & (df["generation_mwh"] > 0)]
df["premium_per_mwh"] = df["premium_gbp"] / df["generation_mwh"]
```

Schemes without a gas counterfactual (CM, Balancing, Grid) are excluded from this view; see [methodology](./methodology.md). NaN-generation rows are dropped before division (HAZARD #2). The `CRISIS_YEARS = (2021, 2022, 2023)` tuple is iterated in declaration order so Plotly groups the bars in chronological visual order.

## Caveats

- **3-year window only.** The chart is locked to 2021 / 2022 / 2023 to isolate the crisis-year contrast against immediate pre- and post-crisis baselines. Longer-window dynamics live on X4.
- **NaN-generation drop.** Years where a scheme has NaN `generation_mwh` are silently excluded. Pre-SY18 RO + CfD pre-2016 are not in the 3-year window so this is not a visible-loss issue today.
- **Excluded schemes.** Capacity Market, Balancing Services, and Grid Socialisation are excluded from this view. The exclusion is documented in the [cross-scheme methodology](./methodology.md) and in the chart subtitle.
- **Sign convention.** Negative premium-per-MWh means the scheme was cheaper than the gas counterfactual that year (the scheme saved consumers money relative to gas); positive means the scheme cost more than gas. Read negative bars as "scheme worked as intended" only if the scheme is designed to track wholesale prices (CfD); for schemes structurally independent of wholesale (RO), the sign tells a different story (premium reflects gas-baseline movement, not scheme behaviour).
- **Covered-only.** Bar groups visible today are Contracts for Difference + Renewables Obligation only.

## Data & code

**GOV-01 four-way coverage** — every PRODUCTION chart on this site links to its primary source, source code, test, and reproduce instructions:

1. **Primary source data:** `data/derived/portal/cross_scheme.parquet` — joined from per-scheme `annual_summary.parquet` outputs. Provenance + sha256 in [`manifest.json`](../data/index.md).
2. **Chart source code:** [`src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/src/uk_subsidy_tracker/plotting/portal/x5_2022_crisis.py)
3. **Test:** [`tests/test_aggregates.py::test_cross_scheme_row_conservation`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_aggregates.py) — row-conservation gate; [`tests/test_benchmarks.py::test_ref_total_reconciliation`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_benchmarks.py) — REF Constable cross-check (Wave 7).
4. **Reproduce locally:**
   ```bash
   git clone https://github.com/richardjlyon/uk-subsidy-tracker.git
   cd uk-subsidy-tracker
   uv sync
   uv run python -m uk_subsidy_tracker.plotting.portal.x5_2022_crisis
   ```

## See also

- [Cross-scheme methodology — no-gas-counterfactual schemes](./methodology.md#no-gas-counterfactual-schemes) — exclusion rationale for CM / Balancing / Grid.
- [Contracts for Difference](../schemes/cfd.md) — 2022 negative-premium framing in per-scheme detail.
- [Renewables Obligation](../schemes/ro.md) — RO contract structure and ROC-pricing context for the 2022 baseline-rise reading.
- [Gas counterfactual](../methodology/gas-counterfactual.md) — how the gas baseline was computed during the 2022 crisis-price spike.
