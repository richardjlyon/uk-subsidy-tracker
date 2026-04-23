# Scheme detail pages

This section collects per-scheme detail pages — each dedicated to one UK renewable subsidy scheme, with headline cost, cost dynamics, breakdown by technology, concentration analysis, and forward-commitment projection.

Each scheme page follows the same eight-section structure (headline / what is it / cost dynamics / by technology / concentration / forward commitment / methodology / data & code), with [GOV-01 four-way coverage](../about/citation.md) at the page bottom: primary regulator URL, chart source-code permalinks, test permalink, and a reproduce-from-`git clone` bash block.

**Currently published:**

- [**Renewables Obligation (RO)**](ro.md) — £67 bn all-in GB total since 2002; 2002-2037 span; the largest legacy renewables subsidy in the UK.

**Coming soon:**

- Contracts for Difference (CfD) — currently documented via the [Cost theme](../themes/cost/index.md) chart gallery; a dedicated scheme page will land in a future release.
- Feed-in Tariff (FiT) — Phase 7.
- Constraint Payments, Capacity Market, Balancing Services, Grid Socialisation, Smart Export Guarantee — Phases 8-12.

## How to read a scheme page

Every scheme page on this site is built to the same template so cross-scheme comparisons require the same reader effort whether you are looking at RO, FiT, or any other scheme. The eight sections are ordered to mirror an adversarial reader's questions: headline figure first (the most-quoted number), then the explanatory background (so the figure is intelligible), then four chart embeds that decompose the figure into the channels that drive policy debate, then methodology + data lineage so any number on the page can be reproduced from the source repository.

The **GOV-01 four-way coverage** block at the bottom of each scheme page is the project's central transparency promise: every chart is traceable to (1) a primary regulator URL, (2) the Python source code that produced it, (3) a test that pins the methodology against an external benchmark, and (4) a reproduce-from-`git clone` bash block. If any of those four are missing, the chart is not eligible for the published site.

Cross-scheme comparison charts (X1-X5: combined cost, share-of-pot, per-MWh, per-tCO2) live on the [Cost](../themes/cost/index.md) and [Recipients](../themes/recipients/index.md) themes — those are the cross-scheme reading paths. The per-scheme pages collected here are the deep-dive paths.
