# CfD Payment Analysis

Welcome to the **CfD Payment Analysis** documentation — a comprehensive analysis of UK Contracts for Difference (CfD) renewable energy subsidy payments.

## What are CfDs?

**Contracts for Difference (CfDs)** are the UK government's main mechanism for supporting low-carbon electricity generation. They work by:

1. **Guaranteeing a "strike price"** — a fixed price per MWh of electricity generated
2. **Topping up the market price** — when wholesale prices are low, generators receive payments to bring their revenue up to the strike price
3. **Clawing back excess** — when wholesale prices are high, generators pay money back

The result is **price certainty** for renewable generators and **cost predictability** for consumers.

## About This Analysis

This project analyzes real-world CfD performance data from 2015 onwards, covering:

- 💷 **Subsidy costs** — how much consumers have paid and what we got for it
- ⚡ **Generation patterns** — capacity factors, seasonality, and intermittency
- 📊 **Cost-effectiveness** — bang for buck, CO₂ abatement costs
- 📉 **Market impacts** — price cannibalisation and capture ratios

All charts feature:

- 🌙 **Dark theme** matching Energy Dashboard UK aesthetic
- 📱 **Interactive visualizations** built with Plotly
- 🐦 **Twitter-ready exports** (1200×675 PNG)
- ℹ️ **Info icons** linking to detailed methodology

## Chart Categories

### [Subsidy Economics](charts/index.md)

Analyze the costs and value of CfD subsidies:

- **[Bang for Buck](charts/subsidy/bang-for-buck.md)** — Subsidy received vs CO₂ avoided per project
- **[CfD vs Gas Cost](charts/subsidy/cfd-vs-gas-cost.md)** — Total cost comparison with gas counterfactual
- **[Scissors Chart](charts/subsidy/scissors.md)** — Strike prices vs market prices over time
- **[Lorenz Curve](charts/subsidy/lorenz.md)** — Concentration of subsidies across projects
- **[Remaining Obligations](charts/subsidy/remaining-obligations.md)** — Future payment commitments

### [Capacity Factor](charts/index.md)

Understand renewable generation performance:

- **[Monthly Trends](charts/capacity-factor/monthly.md)** — Capacity factor by technology over time
- **[Seasonal Patterns](charts/capacity-factor/seasonal.md)** — How weather affects generation

### [Intermittency](charts/index.md)

Explore the challenges of variable generation:

- **[Generation Heatmap](charts/intermittency/heatmap.md)** — Daily capacity factors visualized as wind stripes
- **[Load Duration](charts/intermittency/load-duration.md)** — How often different output levels occur
- **[Rolling Minimum](charts/intermittency/rolling-minimum.md)** — Dunkelflaute events and minimum output windows

### [Cannibalisation](charts/index.md)

Examine how renewables affect their own economics:

- **[Capture Ratio](charts/cannibalisation/capture-ratio.md)** — Wind selling into cheaper hours as capacity grows
- **[Price vs Wind](charts/cannibalisation/price-vs-wind.md)** — Market price correlation with wind output

## Data Sources

All analysis uses publicly available data:

- **[LCCC](https://www.lowcarboncontracts.uk/)** — Actual CfD Generation and avoided GHG emissions
- **[Elexon/BMRS](https://www.bmreports.com/)** — Balancing Mechanism Reporting Service data
- **[National Grid ESO](https://www.nationalgrideso.com/)** — Carbon Intensity API
- **[ONS](https://www.ons.gov.uk/)** — System Average Price of gas

See [Data Sources](data-sources.md) for detailed information.

## Key Features

### Dark Theme

All charts use a dark navy theme (`#1a1d29`) matching the Energy Dashboard UK aesthetic, with:

- Left-aligned bold titles
- Cyan accent colors (`#00d9ff`)
- High contrast for readability
- Info icons (ⓘ) for methodology

### Interactive Charts

- **Hover** for detailed values
- **Click** legend items to show/hide traces
- **Zoom** and pan on charts
- **Download** as static images

### Twitter Integration

Every chart exports a Twitter-optimized PNG (1200×675) perfect for sharing insights on social media.

## Methodology

Our analysis follows these principles:

1. **Transparency** — All calculations documented and reproducible
2. **Primary sources** — Direct from LCCC, Elexon, National Grid
3. **Daily granularity** — Captures price spikes and generation patterns
4. **Lifetime perspective** — Cumulative totals from project start to present
5. **Like-for-like comparisons** — Gas counterfactuals use actual generation profiles

See [Methodology](methodology.md) for detailed explanations.

## Quick Start

Browse the charts by category using the navigation menu, or:

1. **Start with [Bang for Buck](charts/subsidy/bang-for-buck.md)** — A high-level view of value for money
2. **Explore [CfD vs Gas](charts/subsidy/cfd-vs-gas-cost.md)** — See if CfDs saved or cost money
3. **Check [Cannibalisation](charts/cannibalisation/capture-ratio.md)** — Understand the self-defeating economics

## About

This analysis is an independent examination of publicly available CfD data. It aims to:

- 📊 **Inform public debate** with transparent, data-driven analysis
- 🔍 **Highlight trade-offs** between carbon reduction and cost
- 📈 **Track real-world performance** against policy goals
- 🌍 **Contribute to energy policy** discussions

All code and analysis is available on [GitHub](https://github.com/yourusername/cfd-payment).

---

**Questions or feedback?** [Open an issue](https://github.com/yourusername/cfd-payment/issues) or contribute improvements.
