# Cost per MWh of subsidised generation by scheme

**How much does each MWh of subsidised renewable generation cost UK consumers?** Time series with one line per scheme; cost divided by generation MWh per (year, scheme). Per-MWh framing isolates the unit economics from the volume effect — a scheme that rapidly scales up while keeping per-MWh cost flat is a different policy outcome from a scheme that rapidly scales up while per-MWh cost rises.

![UK renewable subsidy cost per MWh of subsidised generation, by scheme over time](../charts/html/x4_cost_per_mwh_twitter.png)

[Interactive version](../charts/html/x4_cost_per_mwh.html){target="_blank"}

## What the chart shows

A multi-line time series. The x-axis is `Year`; the y-axis is `Cost per MWh (£/MWh)`. Each line represents one scheme — Contracts for Difference (blue) and Renewables Obligation (red) today; Phase 7-12 schemes will add new lines as they ship, with the explicit exclusion of those schemes that lack a meaningful gas counterfactual.

The chart subtitle states the exclusion posture: schemes without a gas counterfactual (CM, Balancing, Grid) are excluded — see methodology. Pre-SY18 RO years carry NaN generation in the source parquet and are silently dropped before the per-MWh division.

## The argument

This chart isolates per-MWh economics from total-cost volume.

1. Cost-per-MWh isolates the unit economics from the volume effect. A growing scheme can have rising total cost (X1) while per-MWh cost is falling — those are different policy outcomes and they should be readable separately.
2. Per-scheme variation reflects technology mix and contract structure. Contracts for Difference is a strike-price + 15-year-commitment instrument; the Renewables Obligation pays via tradeable ROC certificates with a buyout-price floor. The two schemes' £/MWh lines differ for structural reasons, not just for technology-mix reasons. See [Contracts for Difference](../schemes/cfd.md) and [Renewables Obligation](../schemes/ro.md) for the contract-mechanism detail.
3. Trends matter: declining cost per MWh = scheme economics improving (the same pound buys more decarbonised MWh); rising = the opposite. The chart should be read as a trend chart, not as a level chart — small £/MWh differences matter when integrated over scheme-lifetime generation volumes.
4. Schemes without a gas counterfactual are excluded by design. The methodology footnote applies here.

## Methodology

The chart is built by `src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py`. The computation is:

```python
# Computation sketch (from src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py)
import pandas as pd
EXCLUDED_SCHEMES = frozenset({"Capacity Market", "Balancing Services", "Grid Socialisation"})
df = pd.read_parquet("data/derived/portal/cross_scheme.parquet")
df = df[~df["scheme"].isin(EXCLUDED_SCHEMES)]
df = df[df["generation_mwh"].notna() & (df["generation_mwh"] > 0)]
df["cost_per_mwh"] = df["cost_gbp"] / df["generation_mwh"]
```

NaN-generation rows are dropped before division (pre-SY18 RO years carry NaN in `generation_mwh` per HAZARD #2 of the cross-scheme schema). Schemes without a gas counterfactual (CM, Balancing, Grid) are excluded from this view; see [methodology](./methodology.md). The `EXCLUDED_SCHEMES` filter is a no-op in Phase 6 (those rows do not yet exist) and auto-engages when Phases 9-11 ship.

## Caveats

- **NaN-generation drop.** Pre-SY18 RO years (2006-2017) carry NaN `generation_mwh` and are dropped before division. The total cost across those years remains visible on X1 + X2 — only the per-MWh ratio is undefined.
- **Excluded schemes.** Capacity Market, Balancing Services, and Grid Socialisation are excluded from this view. The exclusion is documented in the [cross-scheme methodology](./methodology.md) and in the chart subtitle.
- **Covered-only.** Lines visible today are Contracts for Difference + Renewables Obligation only; FiT (Phase 7), Constraint Payments (Phase 8), and Smart Export Guarantee (Phase 12) will add lines once those modules ship.
- **Trend interpretation.** Small £/MWh differences accumulate over scheme-lifetime generation volumes; readers should compare slopes, not absolute levels, when forming an "is this scheme getting cheaper?" judgement.
- **Scheme-year vs calendar-year join.** RO `year` is the obligation-year start calendar year; CfD `year` is the calendar-year settlement anchor. The per-MWh division uses scheme-internal MWh and £, so the join asymmetry does not enter the unit economics.

## Data & code

**GOV-01 four-way coverage** — every PRODUCTION chart on this site links to its primary source, source code, test, and reproduce instructions:

1. **Primary source data:** `data/derived/portal/cross_scheme.parquet` — joined from per-scheme `annual_summary.parquet` outputs. Provenance + sha256 in [`manifest.json`](../data/index.md).
2. **Chart source code:** [`src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py)
3. **Test:** [`tests/test_aggregates.py::test_cross_scheme_row_conservation`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_aggregates.py) — row-conservation gate; [`tests/test_benchmarks.py::test_ref_total_reconciliation`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_benchmarks.py) — REF Constable cross-check (Wave 7).
4. **Reproduce locally:**
   ```bash
   git clone https://github.com/richardjlyon/uk-subsidy-tracker.git
   cd uk-subsidy-tracker
   uv sync
   uv run python -m uk_subsidy_tracker.plotting.portal.x4_cost_per_mwh
   ```

## See also

- [Cross-scheme methodology — no-gas-counterfactual schemes](./methodology.md#no-gas-counterfactual-schemes) — exclusion rationale for CM / Balancing / Grid.
- [Contracts for Difference](../schemes/cfd.md) — per-scheme deep dive (strike-price + 15-year-commitment contract mechanism).
- [Renewables Obligation](../schemes/ro.md) — per-scheme deep dive (ROC pricing + buyout-price floor mechanism).
