# CfD Payment Analysis

"Renewable" electricity—electricty obtained from low-carbon generation sources like wind and solar—is eye-wateringly expensive. So expensive, in fact, that it costs almost three as much to generate it from those sources than it would if we were to generate it directly from gas.

![CfD vs Gas Cost](charts/html/subsidy_cfd_vs_gas_total_twitter.png)

That fact is not well known. One reason that it is not well known is that advocates for it simply claim that it is inexpensive, and they repeat that claim until it aquires the appearance of being true.

But every day, the UK government [publishes every payment we made the previous day](https://dp.lowcarboncontracts.uk/dataset/actual-cfd-generation-and-avoided-ghg-emissions) to the producers of "renewable" electricity under its "Contract for Differences" scheme. By analysing the pattern of these payments over time, we can understand its true cost to us.

Welcome to the **CfD Payment Analysis** documentation—a comprehensive analysis of UK Contracts for Difference (CfD) renewable energy subsidy payments.

## What are CfDs?

**Contracts for Difference (CfDs)** are the UK government's main mechanism for subsidising low-carbon electricity generation. They work by:

1. **Guaranteeing a "strike price"** — a fixed price per MWh of electricity generated
2. **Topping up the market price** — when wholesale prices are lower than the guaranteed price, the public pay subsidies to generators to bring their revenue up to the strike price
3. **Clawing back excess** — when wholesale prices are high, generators pay money back

The result is **profit certainty** for renewable generators and **expensive electricity** for consumers.

## About This Analysis

This project analyzes real-world CfD performance data from 2015 onwards, covering:

- **Subsidy costs** — how much consumers have paid and what we got for it
- **Generation patterns** — capacity factors, seasonality, and intermittency
- **Cost-effectiveness** — bang for buck, CO₂ abatement costs
- **Market impacts** — price cannibalisation and capture ratios

<!--## Chart Categories

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
- **[Price vs Wind](charts/cannibalisation/price-vs-wind.md)** — Market price correlation with wind output-->

## Data Sources

All analysis uses publicly available data:

- **[LCCC](https://www.lowcarboncontracts.uk/)** — Actual CfD Generation and avoided GHG emissions
- **[Elexon/BMRS](https://www.bmreports.com/)** — Balancing Mechanism Reporting Service data
- **[National Grid ESO](https://www.nationalgrideso.com/)** — Carbon Intensity API
- **[ONS](https://www.ons.gov.uk/)** — System Average Price of gas

See [Data Sources](technical-details/data-sources.md) for detailed information.

## Key Features

### Interactive Charts

- **Hover** for detailed values
- **Click** legend items to show/hide traces
- **Zoom** and pan on charts
- **Download** as static images

### Twitter Integration

Every chart exports a Twitter-optimized PNG (1200×675) perfect for sharing insights on social media.

## Methodology

See [Methodology](technical-details/methodology.md) for detailed explanations.

## Quick Start

Browse the charts by category using the navigation menu, or:

1. **Start with [Bang for Buck](charts/subsidy/bang-for-buck.md)** — A high-level view of value for money
2. **Explore [CfD vs Gas](charts/subsidy/cfd-vs-gas-cost.md)** — See if CfDs saved or cost money
3. **Check [Cannibalisation](charts/cannibalisation/capture-ratio.md)** — Understand the self-defeating economics

## About

This analysis is an independent examination of publicly available CfD data. It aims to:

- **Inform public debate** with transparent, data-driven analysis
- **Highlight trade-offs** between carbon reduction and cost
- **Track real-world performance** against policy goals
- **Contribute to energy policy** discussions

All code and analysis is available on [GitHub](https://github.com/yourusername/cfd-payment).

---

**Questions or feedback?** [Open an issue](https://github.com/yourusername/cfd-payment/issues) or contribute improvements.
