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

**Current coverage:** the Contracts for Difference and Renewables Obligation modules are shipped. Each remaining module ships as its scheme grid tile below — see the tile for the latest status.

---

## Schemes

<div class="grid cards" markdown>

-   [![CfD dynamics preview](charts/html/subsidy_cfd_dynamics_twitter.png)](schemes/cfd.md)

    __[Contracts for Difference — £29bn since 2015](schemes/cfd.md)__

    ---

    Ten years of strike-price commitments. £14bn premium over the gas counterfactual. 2022 gas-crisis test: CfD electricity still cost 7% more than gas even at crisis peak.

-   [![RO dynamics preview](charts/html/subsidy_ro_dynamics_twitter.png)](schemes/ro.md)

    __[Renewables Obligation — £67bn since 2002](schemes/ro.md)__

    ---

    The scheme you've never heard of, twice the size of the one you have. ~£6bn/yr forward-committed to 2037; the largest legacy renewables subsidy in the UK.

-   **Feed-in Tariff (FiT)**

    ---

    *Coming in Phase 7.* Domestic and small-commercial renewables tariff; 800k+ installs.

-   **Constraint Payments**

    ---

    *Coming in Phase 8.* The growing cost of paying wind farms to switch off when transmission capacity is saturated.

-   **Capacity Market**

    ---

    *Coming in Phase 9.* Capacity payments to dispatchable generation under EMR; modified methodology (no gas counterfactual).

-   **Balancing Services**

    ---

    *Coming in Phase 10.* Pre/post-renewables balancing-cost delta — the system-operability cost of high renewable penetration.

-   **Grid Socialisation**

    ---

    *Coming in Phase 11.* Best-efforts TNUoS attribution with low/central/high sensitivity bounds; the most uncertain cost bucket.

-   **Smart Export Guarantee (SEG)**

    ---

    *Coming in Phase 12.* Aggregate-only scheme page; no station-level data available from the regulator.

</div>

## Explore by theme

The charts are organised into five argument themes:

1. **[Cost](themes/cost/index.md)** — the mechanism: volume × price gap = bill. Starts with the four-panel diagnostic.
2. **[Recipients](themes/recipients/index.md)** — where the money goes. Six projects receive 50% of the pot.
3. **[Efficiency](themes/efficiency/index.md)** — £/tCO₂ avoided against DEFRA SCC and UK ETS benchmarks.
4. **[Cannibalisation](themes/cannibalisation/index.md)** — why wind crashes its own price, and who tops the difference up.
5. **[Reliability](themes/reliability/index.md)** — the drought periods no battery can cover.

## For journalists and academics

[**Use our data**](data/index.md) — pandas, DuckDB, and R snippets + citation templates + SHA-256 integrity verification. Start at [`manifest.json`](https://richardjlyon.github.io/uk-subsidy-tracker/data/manifest.json) and follow the URLs.

## Status

Version 0.x prototype. Two scheme modules are shipped — Contracts for Difference and Renewables Obligation. The remaining six modules are sequenced in the project [roadmap](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/.planning/ROADMAP.md) and will populate the grid above as they ship. Corrections and contributions welcome via [GitHub Issues](https://github.com/richardjlyon/uk-subsidy-tracker/issues).
