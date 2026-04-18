# Charts Overview

This section contains 14 interactive visualizations analyzing UK CfD renewable energy subsidies, generation patterns, and market impacts. All charts feature a dark theme, interactive controls, and Twitter-ready exports.

## 📊 Chart Categories

### 💷 Subsidy Economics (7 charts)

Analyze the costs and value proposition of CfD subsidies:

| Chart | Description | Key Metric |
|-------|-------------|------------|
| [Bang for Buck](subsidy/bang-for-buck.md) | Cost-effectiveness per project: subsidy vs CO₂ avoided | £/tCO₂ vs UK ETS price |
| [CfD vs Gas Cost](subsidy/cfd-vs-gas-cost.md) | Total CfD cost compared to gas counterfactual | Monthly & cumulative £bn |
| [CfD vs Gas by Category](subsidy/cfd-vs-gas-by-category.md) | Cost breakdown by technology type | £bn by tech |
| [Scissors Chart](subsidy/scissors.md) | Strike prices vs market prices over time | £/MWh gap |
| [Subsidy per tCO₂](subsidy/subsidy-per-co2.md) | Cost per tonne of CO₂ avoided over time | £/tCO₂ trend |
| [Lorenz Curve](subsidy/lorenz.md) | Concentration of subsidies across projects | Gini coefficient |
| [Remaining Obligations](subsidy/remaining-obligations.md) | Future payment commitments by year | £bn/year forward |

### ⚡ Capacity Factor (2 charts)

Understand how efficiently renewables generate electricity:

| Chart | Description | Key Insight |
|-------|-------------|-------------|
| [Monthly Trends](capacity-factor/monthly.md) | Capacity factor by technology over time | Seasonal patterns |
| [Seasonal Patterns](capacity-factor/seasonal.md) | Wind and solar performance across months | Winter vs summer |

### 🌪️ Intermittency (3 charts)

Explore the challenges of variable renewable generation:

| Chart | Description | Key Insight |
|-------|-------------|-------------|
| [Generation Heatmap](intermittency/heatmap.md) | Daily capacity factors visualized as "wind stripes" | Dunkelflaute events |
| [Load Duration](intermittency/load-duration.md) | Distribution of generation levels | How often at each output |
| [Rolling Minimum](intermittency/rolling-minimum.md) | Worst-case generation windows | Backup capacity needs |

### 📉 Cannibalisation (2 charts)

Examine how renewables affect their own market value:

| Chart | Description | Key Insight |
|-------|-------------|-------------|
| [Capture Ratio](cannibalisation/capture-ratio.md) | Wind selling into cheaper hours as capacity grows | Declining capture price |
| [Price vs Wind](cannibalisation/price-vs-wind.md) | Market price correlation with wind output | Price suppression |

## 🎨 Chart Features

All charts include:

- **Dark theme** (`#1a1d29` background) matching Energy Dashboard UK
- **Info icons (ⓘ)** linking to detailed methodology
- **Interactive controls**: hover, zoom, pan, legend toggle
- **Dual exports**: 
  - HTML (interactive, 4-5MB)
  - PNG (Twitter-ready, 1200×675, 150-450KB)

## 📖 How to Use These Charts

### Understanding the Visualizations

1. **Hover** over data points for detailed values
2. **Click** legend items to show/hide specific series
3. **Drag** to zoom, double-click to reset
4. **Click info icon (ⓘ)** for methodology (coming soon)

### Interpreting the Data

Each chart page includes:

- **Overview** — What the chart shows
- **Key Insights** — Main takeaways
- **Methodology** — Data sources and calculations
- **Interpretation Guide** — How to read the visualization
- **Limitations** — Caveats and assumptions
- **Related Charts** — Cross-references

## 🔗 Quick Navigation

**Start here if you want to understand:**

- **💰 Total costs**: [CfD vs Gas Cost](subsidy/cfd-vs-gas-cost.md)
- **📊 Value for money**: [Bang for Buck](subsidy/bang-for-buck.md)
- **📅 Future obligations**: [Remaining Obligations](subsidy/remaining-obligations.md)
- **🌤️ Generation reliability**: [Generation Heatmap](intermittency/heatmap.md)
- **💹 Price impacts**: [Capture Ratio](cannibalisation/capture-ratio.md)

## 📥 Bulk Downloads

All chart outputs are available in the `output/` directory:

- **HTML files**: `output/*.html` (interactive)
- **Twitter PNGs**: `output/*_twitter.png` (1200×675)

## 🛠️ Technical Details

Charts are built using:

- **Python 3.13** + Plotly 6.7.0
- **Data sources**: LCCC, Elexon, National Grid ESO, ONS
- **Update frequency**: Data refreshed when new monthly reports published
- **ChartBuilder**: Custom framework for consistent styling

See [Methodology](../methodology.md) for complete technical documentation.

---

**Ready to explore?** Choose a category above or browse individual charts using the navigation menu.
