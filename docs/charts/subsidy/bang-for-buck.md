# Bang for Buck — Subsidy vs CO₂ Avoided

## Overview

The Bang for Buck chart visualizes the cost-effectiveness of individual CfD projects by plotting total subsidy received against total CO₂ emissions avoided. Each dot represents a CfD unit, with the size indicating total generation (GWh) and color showing the allocation round.

<div markdown="0">
<iframe src="../../html/subsidy_bang_for_buck.html" width="100%" height=800px" frameborder="0" style="border: 1px solid #ccc;"></iframe>
</div>

## Key Insights

- **Top-left = Good value**: Projects that avoided significant carbon for relatively low subsidy
- **Bottom-right = Poor value**: Projects that received large subsidies but avoided less carbon
- The **UK ETS carbon price (£50/tCO₂)** divides the chart into two zones:
  - 🟢 **Green zone (above line)**: Cost-effective — avoided carbon for less than the market carbon price
  - 🔴 **Red zone (below line)**: Not cost-effective — paid more per tonne than carbon costs on the open market

## How to Read This Chart

### Axes

- **X-axis**: Total subsidy received (£ millions) — logarithmic scale
- **Y-axis**: Total CO₂ avoided (kt) — logarithmic scale

### Visual Elements

- **Dot size**: Total generation (GWh) — larger dots = more electricity generated
- **Dot color**: Allocation round (Investment Contract, AR1, AR2, AR4, AR5, AR6)
- **Log scales**: Spread out clustered small projects for better visibility

### Reference Line

The dashed red line represents the UK ETS carbon price of **£50/tCO₂**. This is the cost of carbon on the open market:

- Projects **above** this line avoided carbon more cheaply than buying carbon credits
- Projects **below** this line cost more per tonne than the market carbon price

## Methodology

### Data Source

LCCC "Actual CfD Generation and avoided GHG emissions" dataset

### Calculations

**Subsidy (X-axis)**:

```
Subsidy = Σ(Strike Price - Market Price) × Generation
```

This is the actual levy payment — the premium consumers paid above the market price.

**CO₂ Avoided (Y-axis)**:

```
CO₂ Avoided = Σ(Avoided GHG tonnes CO₂e)
```

Total greenhouse gas emissions avoided by the project over its lifetime.

**Cost per tonne**:

```
£/tCO₂ = Subsidy (£) / CO₂ Avoided (tonnes)
```

### Filters Applied

- **Positive subsidies only**: Units with negative total payments (net clawback) excluded — they received no net subsidy so £/tCO₂ is meaningless
- **Minimum generation**: Units with < 100 GWh total generation excluded to remove noise from newly commissioned projects

## Interpretation Guide

### Good Value Projects

Projects in the **top-left** quadrant:

- Low subsidy relative to CO₂ avoided
- High carbon abatement per £ spent
- Better value than the carbon market price

### Poor Value Projects

Projects in the **bottom-right** quadrant:

- High subsidy relative to CO₂ avoided
- Low carbon abatement per £ spent
- Worse value than buying carbon credits

### What Affects Position?

1. **Technology efficiency**: More efficient technologies generate more per MW, avoiding more carbon
2. **Capacity factor**: Wind/solar intermittency affects total generation over lifetime
3. **Strike price**: Higher strike prices increase subsidy costs
4. **Market prices during operation**: Lower market prices = higher subsidy payments
5. **Project timing**: Earlier projects may have different cost structures

## Key Findings

!!! note "Observations" - Investment Contracts (early projects) tend to have higher subsidies relative to CO₂ avoided - Later allocation rounds generally show improved cost-effectiveness - Offshore wind projects dominate the high-generation, high-CO₂-avoided quadrant - Some large projects received substantial subsidies but the CO₂ benefit varied significantly

## Limitations

!!! warning "Caveats" - Does not account for the **full system value** of renewable generation (grid stability, energy security, etc.) - **UK ETS price (£50/tCO₂)** is a snapshot — carbon prices fluctuate - Does not include **non-carbon benefits** (air quality, health impacts) - **Lifetime perspective**: Early projects may look expensive but enabled technology learning curves - **Gas counterfactual** assumes all displaced generation would be gas — reality is more complex

## Related Charts

- [CfD vs Gas Cost](cfd-vs-gas-cost.md) — Total system cost comparison
- [Subsidy per tCO₂](subsidy-per-co2.md) — Time series view of cost per tonne avoided
- [Lorenz Curve](lorenz.md) — Distribution of subsidies across projects

## Export

Download this chart:

- [Interactive HTML](../../html/subsidy_bang_for_buck.html) (4.6 MB)
- [Twitter PNG](../../html/subsidy_bang_for_buck_twitter.png) (1200×675)

---

_Last updated: {{ git_revision_date }}_
