# RO Cost Tracking Module — Product Spec

**Status:** Draft v1
**Owner:** Richard Lyon
**Target:** Add a Renewables Obligation cost tracking module to `cfd-payment`,
producing an RO datafeed directly comparable to the existing CfD datafeed.

---

## 1. Goal

Build a station-month-level RO cost tracker that mirrors the CfD module's
analytical shape, so CfD and RO can be plotted on the same axes with the same
counterfactual and the same code path. Answer the question the existing CfD
analysis cannot: **did the larger, older subsidy scheme lock in crisis prices
the same way?**

The output is a reproducible, open dataset and chart set covering 2002 →
present (and a forward projection to 2037 when RO winds down), with:

- total £ cost to consumers, by scheme year;
- premium over the gas counterfactual, per MWh and cumulative;
- decomposition by technology (onshore wind / offshore wind / solar / biomass
  / hydro / landfill gas / other);
- a **combined CfD + RO view** so the full renewable-subsidy bill is visible
  in one chart.

## 2. Non-goals

- **Not** a forecast of future ROC prices. Buy-out is RPI-indexed and
  published a year ahead; recycle is a residual. We project forward using the
  most recent published value and flag scenario sensitivity.
- **Not** a rebuild of Ofgem's register. We consume their published data.
- **Not** a replacement for the Turver/REF aggregate totals — we replicate
  them as a sanity check and add the counterfactual, granularity, and code.
- **Not** an FiT or Capacity Market module. Those are separate schemes. This
  module is RO-only. (A later `subsidy_schemes/` umbrella can unify them.)

## 3. Headline analytical deliverables

Five charts, mirroring the CfD production set where possible. File naming
follows existing `subsidy_*_twitter.png` convention.

| # | Chart | Mirrors | New |
|---|---|---|---|
| 1 | `subsidy_ro_dynamics_twitter.png` — 4-panel: generation volume / ROC price vs gas counterfactual £/MWh / premium per MWh / cumulative bill | ✓ cfd_dynamics | — |
| 2 | `subsidy_ro_vs_gas_total_twitter.png` — stacked cost vs gas reference line | ✓ cfd_vs_gas_cost | — |
| 3 | `subsidy_ro_remaining_twitter.png` — forward obligation to 2037 | ✓ remaining_obligations | — |
| 4 | `subsidy_ro_by_technology_twitter.png` — stacked area £/yr by technology | — | ✓ new |
| 5 | `subsidy_combined_cfd_ro_twitter.png` — CfD + RO on shared axes | — | ✓ **flagship** |

Chart 5 is the rhetorical prize: **the full renewable-subsidy bill, on one
chart, against the gas counterfactual, with the 2022 row visible for both
schemes.**

## 4. Data sources

All public, all scrapeable. Stored under `data/` alongside existing CSVs.

### 4.1 Station register + generation (Ofgem)

- **Source:** [Ofgem Renewables and CHP Register](https://renewablesandchp.ofgem.gov.uk/) —
  accredited stations + ROCs issued per output period.
- **Expected schema:**
  `Accreditation_No, Station_Name, Operator, Technology_Group, Capacity_MW,
  Accreditation_Date, Country, Output_Period_Start, Output_Period_End,
  Generation_MWh, ROCs_Issued, Banding_Factor_Applied`
- **Format:** XLSX download, one row per station per output period.
- **Volume:** ~3,500 accredited stations × ~240 months = ~500k rows historical.
- **Refresh cadence:** Monthly (with ~3 month lag).

### 4.2 ROC buy-out price (Ofgem)

- **Source:** [Ofgem buy-out publications](https://www.ofgem.gov.uk/publications-and-updates/renewables-obligation-buy-out-price-and-mutualisation-ceilings)
- **Schema:** `obligation_year, buyout_price_gbp_per_roc, rpi_index_used`
- **Coverage:** 2002–2027 (one value per year, published ~Feb of preceding year).
- **Volume:** 25 rows.

### 4.3 ROC recycle payment (Ofgem)

- **Source:** Ofgem *Annual Report on the Renewables Obligation* +
  *ROCs Presented and Redistribution of Buy-Out Fund* publications.
- **Schema:** `obligation_year, recycle_gbp_per_roc, buyout_fund_total_gbp,
  rocs_presented_count`
- **Coverage:** 2002–present (lagged ~6 months post year-end).

### 4.4 e-ROC market price (e-roc.co.uk)

- **Source:** [e-ROC quarterly auction results](https://www.e-roc.co.uk/)
- **Schema:** `auction_date, clearing_price_gbp_per_roc, volume_rocs`
- **Use:** Sanity check against `buyout + recycle`. Secondary series, not
  primary cost driver.

### 4.5 Banding factor table (DESNZ / RO Order)

- **Source:** The Renewables Obligation Order (amended yearly). Extract into
  a static YAML file.
- **Schema:** `technology_group, commissioning_window_start,
  commissioning_window_end, band_roc_per_mwh, notes`
- **Volume:** ~60 rows (covers all technology × commissioning-window cells).
- **Rationale:** A station's banding depends on technology **and** when it
  commissioned. E.g. offshore wind: 2.0 ROC/MWh pre-2014; 1.8 ROC/MWh
  2014–2016; 1.5 ROC/MWh post-2017. Getting this right is the single biggest
  methodology risk — see §10.

### 4.6 Reused without change

- **Gas counterfactual:** `cfd_payment.counterfactual.compute_counterfactual`
  — already computes `£/MWh` for any MWh volume using ONS gas SAP, UK ETS
  carbon, CCGT efficiency, and £5/MWh O&M. Unchanged.
- **ONS gas SAP:** `cfd_payment.data.ons_gas` — already handles the daily
  wholesale price series.
- **UK ETS carbon:** `DEFAULT_CARBON_PRICES` in `counterfactual.py`. Note:
  pre-2021 values are EU ETS converted. RO goes back to 2002 — we will need
  to extend this table back to scheme inception, either with pre-2013 EU ETS
  prices or with an explicit "no carbon price before 2005" block.

## 5. Module architecture

Mirror the existing `cfd_payment` layout. New code lives alongside, not on
top of, CfD.

```
src/cfd_payment/
├── counterfactual.py          (unchanged — reused)
├── data/
│   ├── lccc.py                (unchanged)
│   ├── ons_gas.py             (unchanged)
│   ├── ofgem_ro.py            (NEW — station register + generation scraper)
│   ├── roc_prices.py          (NEW — buyout + recycle + e-roc)
│   ├── ro_bandings.yaml       (NEW — static lookup)
│   └── lccc_datasets.yaml     (unchanged)
├── ro/                        (NEW — RO-specific analytics)
│   ├── __init__.py
│   ├── cost_model.py          (NEW — station-month £ cost computation)
│   ├── aggregation.py         (NEW — monthly/annual rollups by tech, year)
│   └── forward_projection.py  (NEW — contracts-to-2037 projection)
└── plotting/
    └── subsidy/
        ├── ro_dynamics.py                 (NEW — mirrors cfd_dynamics)
        ├── ro_vs_gas_cost.py              (NEW — mirrors cfd_vs_gas_cost)
        ├── ro_remaining.py                (NEW — mirrors remaining_obligations)
        ├── ro_by_technology.py            (NEW)
        └── combined_cfd_ro.py             (NEW — flagship)
```

**Naming convention:** Everything RO-prefixed; nothing touches the `cfd_`
namespace. This makes it trivial to later hoist shared code into a
`subsidy_schemes/` umbrella without rewrites.

## 6. Data model

One canonical table per grain. Stored as Parquet under `data/derived/`
(new subdir). Raw sources stay as CSV/XLSX.

### 6.1 `ro_station_month` (primary analytical table)

One row per (station × output period). Canonical name: `ro_station_month.parquet`.

```
station_id              str    — Ofgem accreditation number
station_name            str
operator                str
technology              str    — onshore_wind | offshore_wind | solar_pv |
                                 biomass_dedicated | biomass_cofiring |
                                 hydro | landfill_gas | sewage_gas | ewt |
                                 other
commissioning_date      date
country                 str    — GB | NI
capacity_mw             float
output_period_start     date   — normally first of month
output_period_end       date
generation_mwh          float  — metered output
banding_factor          float  — ROCs per MWh, from ro_bandings.yaml lookup
rocs_issued             float  — generation_mwh × banding_factor (verified
                                 against Ofgem's issued count — warn on
                                 >1% divergence)
obligation_year         int    — Apr-Mar year this output falls in
roc_price_gbp           float  — buyout + recycle for that obligation year
ro_cost_gbp             float  — rocs_issued × roc_price_gbp
gas_counterfactual_gbp  float  — compute_counterfactual(generation_mwh)
premium_gbp             float  — ro_cost_gbp - gas_counterfactual_gbp
```

### 6.2 `ro_annual_summary`

Derived rollup. Annual totals by technology for plotting.

```
obligation_year, technology, generation_mwh, rocs_issued, ro_cost_gbp,
gas_counterfactual_gbp, premium_gbp, avg_strike_effective_gbp_per_mwh,
avg_gas_counterfactual_gbp_per_mwh
```

### 6.3 `ro_forward_projection`

Per-station remaining-years projection to 2037. Used by chart 3.

```
station_id, projection_year, projected_generation_mwh, projected_rocs,
projected_roc_price_gbp, projected_cost_gbp
```

## 7. Cost computation — authoritative formula

For each station-month:

```python
# 1. Generation → ROCs
rocs_issued = generation_mwh * banding_factor

# 2. ROCs → £
#    Effective ROC value = buyout + recycle for the obligation year.
#    (Use Ofgem published values; not e-ROC auction clearing.)
roc_price = roc_prices.loc[obligation_year, "buyout"] \
          + roc_prices.loc[obligation_year, "recycle"]
ro_cost_gbp = rocs_issued * roc_price

# 3. Gas counterfactual (identical to CfD methodology)
gas_counterfactual_gbp = compute_counterfactual(
    mwh=generation_mwh,
    date=output_period_end,
    include_carbon=True,
    opex_per_mwh=5.0,
    ccgt_efficiency=0.55,
)

# 4. Premium
premium_gbp = ro_cost_gbp - gas_counterfactual_gbp
```

**Critical difference vs CfD:** RO is additive to wholesale. A generator earns
`wholesale + ROC_value` per MWh. CfD, by contrast, pays `strike - wholesale`
and the consumer pays `strike` regardless. For a like-for-like consumer-cost
comparison, the RO cost we track is the **ROC subsidy paid by consumers via
their bills**, which is `rocs_issued × roc_price`. The wholesale portion is
paid anyway under any regime and is excluded from the subsidy figure — this
matches how CfD's £14bn premium is quoted in the existing analysis.

## 8. Pipeline stages

Each stage idempotent, checkpointable, commit-atomic.

**Stage 1 — Ingest raw**
- `uv run python -m cfd_payment.data.ofgem_ro --refresh` → pulls station
  register + monthly ROC issuance, writes `data/ofgem-ro-register.csv` and
  `data/ofgem-ro-generation.csv`.
- `uv run python -m cfd_payment.data.roc_prices --refresh` → pulls buyout,
  recycle, e-ROC; writes `data/roc-prices.csv`.

**Stage 2 — Derive station-month table**
- `uv run python -m cfd_payment.ro.cost_model` → joins raw sources, applies
  bandings, computes counterfactual; writes `data/derived/ro_station_month.parquet`.

**Stage 3 — Aggregate**
- `uv run python -m cfd_payment.ro.aggregation` → produces
  `ro_annual_summary.parquet`.

**Stage 4 — Project forward**
- `uv run python -m cfd_payment.ro.forward_projection` → produces
  `ro_forward_projection.parquet` (2026 → 2037).

**Stage 5 — Plot**
- `uv run python -m cfd_payment.plotting.subsidy.ro_dynamics` (etc.)
- `uv run python -m cfd_payment.plotting` regenerates everything.

## 9. Validation gates (must pass before merge)

| Check | Target | Fail action |
|---|---|---|
| Total ROCs issued 2002–latest matches Ofgem annual report | ±1% | Stop. Investigate. |
| Total RO cost 2011–2022 matches Turver's published aggregate | ±3% | Flag in code comment, proceed. |
| Station count by technology matches REF register | ±0.5% | Investigate mismatches individually. |
| `generation_mwh × banding_factor` matches Ofgem `rocs_issued` | ±1% per station | Log divergent stations; if >10 stations fail, stop. |
| Gas counterfactual for RO-era MWh reconciles with CfD-era MWh on overlap | identical | Bug — unified pipeline must produce identical £/MWh. |

## 10. Known risks and open decisions

**R1 — Banding assignment accuracy.** A station's ROC/MWh band depends on
commissioning date **and** technology **and** country **and** whether it
extended/re-accredited. Getting this wrong is the single largest methodology
risk. **Mitigation:** cross-check `generation_mwh × banding_factor` against
Ofgem's `ROCs_issued` column at the station level — divergence reveals band
errors. Ofgem publishes the *actual* ROCs issued, so we can short-circuit the
banding lookup where it's present.

**R2 — Pre-2013 carbon price.** The existing `counterfactual.py` only covers
2018–2026. RO extends back to 2002. We need a decision:
(a) extend with EU ETS prices 2005–2017 + "no carbon" 2002–2004, or
(b) present two RO totals: "with carbon" and "without carbon", letting the
reader choose.
**Recommendation:** Do both. Chart using (a); publish (b) as sensitivity.

**R3 — Obligation-year vs calendar-year mismatch.** RO obligation years run
April–March. CfD analysis uses calendar years. Charting them side-by-side
requires a convention. **Recommendation:** plot by calendar year throughout;
allocate RO generation to the calendar year it occurred in, using the ROC
price of the obligation year that contains it. Document prominently.

**R4 — Northern Ireland.** NIRO runs separately with different buyout prices
and bandings. **Recommendation:** include as separate rows (`country = NI`)
using NI-specific price series; headline totals are GB-only unless explicitly
stated. Scope decision.

**R5 — Co-firing biomass cost attribution.** Some coal plants burned biomass
alongside coal and received ROCs for the biomass fraction. Generation data
includes the biomass MWh only, but attribution to "renewables" is
philosophically contestable. **Recommendation:** include; flag in a
footnote; provide `technology = biomass_cofiring` slice so reader can
exclude.

**R6 — Buy-out vs recycle vs e-ROC.** Three ROC prices exist. Using
`buyout + recycle` is the consumer-cost view; using e-ROC clearing is the
generator-revenue view. They diverge by 2–10%. **Recommendation:** use
`buyout + recycle` as primary (matches what suppliers actually charge); show
e-ROC as a sanity band in the 4-panel chart.

**R7 — Mutualisation events.** When suppliers default, the remaining
suppliers cover the shortfall (mutualisation). This inflates the effective
cost per ROC in a handful of years (notably 2021–22). **Recommendation:**
include mutualisation payments in the cost total; flag the affected years in
the chart.

**R8 — Scope creep.** FiT (Feed-in Tariff) is the third major subsidy
scheme. It is out of scope for v1 but will be asked for. **Recommendation:**
add a stub `fit/` directory now with a one-line README saying "future work";
structure the `ro/` module so FiT can be added without refactoring.

## 11. Phased delivery

**Phase A — Data plumbing (1–2 days)**
- Stage 1 scrapers (Ofgem register, ROC prices).
- Banding YAML handcrafted from RO Order.
- Raw data committed; schema validated.

**Phase B — Cost model (1 day)**
- Stage 2 (`ro_station_month`) with validation against Ofgem's own
  `rocs_issued`.
- Aggregate (Stage 3) matching Turver/REF totals within tolerance.

**Phase C — Charts (1–2 days)**
- Charts 1, 2, 3 (mirrors of existing CfD charts — port the plotting code,
  swap the data).
- Chart 4 (by technology).

**Phase D — Combined view + docs (1 day)**
- Chart 5 (flagship — CfD + RO on one axis).
- Docs pages mirroring existing structure:
  `docs/charts/ro/{ro-dynamics,ro-vs-gas,ro-remaining,by-technology,
  combined-cfd-ro}.md`
- Update `docs/index.md` headline: *"£X billion for CfD + £Y billion for RO
  = £Z billion"*.

**Phase E — Publication (0.5 day)**
- Essay draft: *"The Scheme You've Never Heard Of — Twice the Size of the
  One You Have."*
- Email Turver pre-publication with the combined chart and replication of
  his totals.

**Total:** ~5–6 working days to a publishable deliverable.

## 12. Success criteria

- `uv run python -m cfd_payment.plotting` regenerates all 5 new charts plus
  all 3 existing CfD charts without error.
- `mkdocs build --strict` passes with new docs pages.
- RO aggregate 2011–2022 replicates Turver's published total within 3%.
- CfD + RO combined 2022 premium visible on one chart.
- A journalist can clone the repo and reproduce every number on this page in
  under 10 minutes.

## 13. Explicit non-commitments (v1)

- No live dashboard. Charts are regenerated on demand, committed as PNG/HTML.
- No API endpoint exposing the datasets. Parquet files in `data/derived/`
  are the interface.
- No Rust port. The whole pipeline stays Python.
- No FiT, no Capacity Market, no Contracts for Difference (Wholesale), no
  Renewable Heat Incentive. Those are separate modules for later.

---

## Appendix A — File/chart naming cross-reference

| CfD file | RO equivalent |
|---|---|
| `plotting/subsidy/cfd_dynamics.py` | `plotting/subsidy/ro_dynamics.py` |
| `plotting/subsidy/cfd_vs_gas_cost.py` | `plotting/subsidy/ro_vs_gas_cost.py` |
| `plotting/subsidy/remaining_obligations.py` | `plotting/subsidy/ro_remaining.py` |
| `subsidy_cfd_dynamics_twitter.png` | `subsidy_ro_dynamics_twitter.png` |
| `subsidy_cfd_vs_gas_total_twitter.png` | `subsidy_ro_vs_gas_total_twitter.png` |
| `subsidy_remaining_obligations_twitter.png` | `subsidy_ro_remaining_twitter.png` |
| — | `subsidy_ro_by_technology_twitter.png` |
| — | `subsidy_combined_cfd_ro_twitter.png` |
| `docs/charts/subsidy/cfd-dynamics.md` | `docs/charts/ro/ro-dynamics.md` |
| `docs/charts/subsidy/cfd-vs-gas-cost.md` | `docs/charts/ro/ro-vs-gas-cost.md` |
| `docs/charts/subsidy/remaining-obligations.md` | `docs/charts/ro/ro-remaining.md` |
