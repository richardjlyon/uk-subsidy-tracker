# CfD payments by technology category

**Monthly and cumulative CfD cost stacked by technology. Offshore wind and Drax biomass dominate; onshore wind and solar are minor categories in the spend.**

![CfD payments by technology category](../../charts/html/subsidy_cfd_payments_by_category_twitter.png)

→ [Interactive version](../../charts/html/subsidy_cfd_payments_by_category.html)

## What the chart shows

A two-panel diagnostic with shared x-axis (calendar month, scheme start to
latest LCCC settlement). The **top panel** is a stacked bar: monthly CfD
electricity cost decomposed by technology category — Offshore Wind (deep
blue), Onshore Wind (light blue), Biomass Drax & Lynemouth (red), and a
residual "Other" bucket (green) covering solar PV, ACT, energy-from-waste,
and small-scale biomass. The **bottom panel** is a stacked area of the
same data on a cumulative basis — the endpoint of each colour band reads
directly as that technology's lifetime CfD spend in £bn.

Colours follow the `TECHNOLOGY_COLORS` convention used across the site
(Offshore `#1f77b4`, Onshore `#6baed6`, Biomass `#d62728`, Other `#2ca02c`),
so the same colour in the Cost theme charts (e.g. cfd-dynamics) refers to
the same technology. The cumulative total at the right edge reconciles
with the cumulative figure in [`cfd-vs-gas-cost`](../cost/cfd-vs-gas-cost.md)
— both use the same cost definition
(`reference_price × generation + CFD_Payments_GBP` = strike × generation).

## The argument

**Offshore wind and Drax biomass dominate. Almost every pound of CfD
subsidy flows to one of two categories.**

The per-project [Lorenz](./lorenz.md) chart makes the point at the unit
level: 6 projects capture half the £29bn. This chart makes the same point
along a different axis: when you collapse those individual contracts into
technology categories, the cumulative stacked area in the bottom panel
shows the vast majority of lifetime CfD spend falls inside two bands —
Offshore Wind (largest single band) and Biomass (entirely Drax + a small
Lynemouth contribution). Onshore wind is a thin band despite its large
installed-capacity share of the wider UK renewables fleet, because most
onshore wind in Great Britain predates the CfD scheme and was built under
the Renewables Obligation regime.

This is not a criticism of offshore wind or Drax individually. It is a
statement about what the CfD mechanism is actually doing with the
consumer levy pound. A reader evaluating "does the UK need CfDs?" should
evaluate the offshore wind contracts and the Drax biomass contract *on
their specific merits* — strike price, carbon intensity, supply-chain
economics — rather than on a diffuse "supports renewables in general"
argument. The chart forces the concentration into the foreground.

The monthly top panel shows a second structural feature: **2022 appears
as negative slivers** for most technologies. During the gas crisis wholesale
prices exceeded most CfD strike prices, triggering the clawback mechanism:
generators paid consumers back, so `CFD_Payments_GBP` went negative for
that window. This is the CfD mechanism working as designed — it fixes the
price in both directions.

## Methodology

Source: LCCC *Actual CfD Generation and avoided GHG emissions* (daily
settlements with a `Technology` column).

Per-row cost:

```
cfd_cost = Market_Reference_Price_GBP_Per_MWh × CFD_Generation_MWh
         + CFD_Payments_GBP
```

This is mathematically equivalent to `Strike_Price × CFD_Generation_MWh`
by construction, but using `reference_price × gen + CFD_Payments_GBP`
directly picks up any LCCC settlement adjustments — negative-pricing
suspensions, cap/floor rules, settlement re-runs — so the totals here match
cash actually transferred rather than a theoretical strike-price reconstruction.

Technology mapping collapses the LCCC `Technology` field into four display
categories:

| LCCC `Technology`                | Display category         |
|----------------------------------|--------------------------|
| `Offshore Wind`                  | Offshore Wind            |
| `Onshore Wind`                   | Onshore Wind             |
| `Biomass Conversion`             | Biomass (Drax & Lynemouth) |
| *(anything else)*                | Other                    |

The row is then pivoted to `month × category` with `aggfunc="sum"` and
divided by 1e6 for display in £m; the cumulative panel additionally divides
by 1e3 for display in £bn.

No gas counterfactual is involved — this chart is pure attribution of
consumer spending. See the Recipients
[methodology](./methodology.md) for the technology-attribution rule.

## Caveats

- **Technology classification follows the LCCC portfolio snapshot.** A
  unit's `Technology` field is fixed per-row as reported by LCCC;
  reclassifications mid-contract are rare but not tracked.
- **"Other" aggregates several small categories.** Solar PV, Advanced
  Conversion Technology, Energy-from-Waste, and any small-scale biomass
  are pooled into the Other bucket. Individually they are too small to
  plot as distinct bands; collectively they represent a few percent of
  lifetime cost.
- **2022 negative-payment months are visible as inverted slivers.** For
  most generators `CFD_Payments_GBP` went negative during the gas crisis
  when wholesale exceeded strike. The stacked-bar rendering shows this
  as a small below-zero segment for the affected categories; it is not a
  charting glitch.
- **Biomass category is almost entirely Drax.** Lynemouth converted
  smaller tonnages and its CfD lifetime payments are dwarfed by Drax's
  Investment Contract. "Biomass" in this chart is effectively a
  single-recipient story.

## Data & code

- **CfD data** — [LCCC Actual CfD Generation and avoided GHG emissions](https://www.lowcarboncontracts.uk/data-portal/dataset/actual-cfd-generation-and-avoided-ghg-emissions/actual-cfd-generation-and-avoided-ghg-emissions)
- **Chart source** — [`src/uk_subsidy_tracker/plotting/subsidy/cfd_payments_by_category.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/src/uk_subsidy_tracker/plotting/subsidy/cfd_payments_by_category.py)
- **Tests** —
  [`tests/test_schemas.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_schemas.py)
  (validates LCCC *Actual CfD Generation* schema — the `Technology`,
  `Market_Reference_Price_GBP_Per_MWh`, `CFD_Generation_MWh`, and
  `CFD_Payments_GBP` fields this chart depends on),
  [`tests/test_aggregates.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_aggregates.py)
  (row-conservation pin on the technology-pivot aggregation pattern)

To reproduce:

```bash
uv run python -m uk_subsidy_tracker.plotting.subsidy.cfd_payments_by_category
```

## See also

- [Lorenz curve](./lorenz.md) — the project-level view of the same
  concentration story (6 projects = 50% of subsidy).
- [Cost theme](../cost/index.md) — total-spend context plus the
  gas-counterfactual comparison the stacked total here reconciles with.
- [Recipients methodology](./methodology.md) — attribution rules for
  both `Name_of_CfD_Unit` and `Technology` fields.
