# UK Renewable Subsidy Tracker

An independent, open, data-driven audit of UK renewable electricity
subsidy costs — every scheme, every pound, every counterfactual, every
methodology exposed.

The UK runs eight distinct subsidy and levy schemes that together add
tens of billions of pounds to consumer bills each year. This site
tracks each of them — Contracts for Difference, the Renewables
Obligation, Feed-in Tariffs, the Smart Export Guarantee, Constraint
Payments, the Capacity Market, Balancing Services, and Grid
Socialisation — to one standard: every chart reproducible from a
single `git clone`, every number traceable to a regulator source,
every methodology documented.

**Current coverage:** the Contracts for Difference module is shipped
below. The remaining seven modules are under active development; the
site expands as each is published.

---

## Module in focus: Contracts for Difference

![CfD dynamics — the full mechanism in four panels](charts/html/subsidy_cfd_dynamics_twitter.png)

**Ten years into the scheme, UK consumers have paid £29 billion for
CfD electricity — roughly £14 billion more than the same MWh would
have cost from the gas fleet Britain already owned.** The premium is
paid every month. In only one year — 2022, the worst gas crisis in
living memory — did CfD electricity come close to matching the gas
alternative, and even then it still cost 7% more.

The five theme pages below document the methodology, data sources,
and code behind that conclusion, and present the charts that
substantiate it.

### What are CfDs?

A **Contract for Difference** guarantees a fixed price per MWh — the
*strike price* — to a renewable generator for fifteen years. The
electricity still sells into the wholesale market at a variable
*reference price*. When reference falls below strike, consumers top up
the difference through a levy. When reference rises above strike, the
generator pays the difference back. Total cost to the consumer: the
strike price. Always. Regardless of what gas is doing.

The generator is insulated from market risk. The consumer pays the
strike price — no more, no less. The consumer was never promised
anything about the *level* of that stable price.

### Explore by theme

The charts are organised into five argument themes:

1. **[Cost](themes/cost/index.md)** — the mechanism: volume × price gap = bill. Starts with the four-panel diagnostic.
2. **[Recipients](themes/recipients/index.md)** — where the money goes. Six projects receive 50% of the pot.
3. **[Efficiency](themes/efficiency/index.md)** — £/tCO₂ avoided against DEFRA SCC and UK ETS benchmarks.
4. **[Cannibalisation](themes/cannibalisation/index.md)** — why wind crashes its own price, and who tops the difference up.
5. **[Reliability](themes/reliability/index.md)** — the drought periods no battery can cover.

## Scheme detail pages

- [**Renewables Obligation (RO)**](schemes/ro.md) — the £67 bn scheme you've never heard of, twice the size of Contracts for Difference. Cumulative since 2002; ~£6 bn/yr forward-committed to 2037.
- Contracts for Difference (CfD) — currently documented via the [Cost theme gallery](themes/cost/index.md); a dedicated scheme page lands in a future release.

The full per-scheme overview lives at [**Schemes → Overview**](schemes/index.md). New scheme detail pages will be added as each module ships (FiT in Phase 7, then constraints / capacity market / balancing / grid / SEG in Phases 8-12).

## For journalists and academics

[**Use our data**](data/index.md) — pandas, DuckDB, and R snippets + citation templates + SHA-256 integrity verification. Start at [`manifest.json`](https://richardjlyon.github.io/uk-subsidy-tracker/data/manifest.json) and follow the URLs.

## Data sources

All analysis is built from public data:

- **[LCCC](https://www.lowcarboncontracts.uk/)** — actual CfD generation,
  strike and reference prices, payment flows, contract portfolio
- **[ONS](https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/gk36/mm22)** — System Average Price of gas (wholesale)
- **[UK ETS](https://www.gov.uk/government/publications/participating-in-the-uk-ets)** — carbon auction prices
- **[NESO](https://www.neso.energy/publications/future-energy-scenarios-fes)** — demand projections (forward scenarios)

The gas counterfactual methodology — how "what gas would have cost"
is computed — is documented in detail at
[Gas counterfactual](methodology/gas-counterfactual.md).

## Code & reproducibility

Everything on this site is reproducible from the source repository:

```bash
git clone https://github.com/richardjlyon/uk-subsidy-tracker
cd uk-subsidy-tracker
uv sync
uv run python -m uk_subsidy_tracker.plotting    # regenerate all charts
uv run mkdocs serve                      # serve this site locally
```

Source: [github.com/richardjlyon/uk-subsidy-tracker](https://github.com/richardjlyon/uk-subsidy-tracker).

## Status

Version 0.x prototype. The Contracts for Difference module is the
first of eight planned scheme modules; all five CfD theme pages (Cost,
Recipients, Efficiency, Cannibalisation, Reliability) are published
with their flagship charts, and methodology pages carry the formulas
and provenance. The remaining seven scheme modules are sequenced in
the project [roadmap](https://github.com/richardjlyon/uk-subsidy-tracker)
and will appear here as they ship. Corrections and contributions
welcome via
[GitHub Issues](https://github.com/richardjlyon/uk-subsidy-tracker/issues).
