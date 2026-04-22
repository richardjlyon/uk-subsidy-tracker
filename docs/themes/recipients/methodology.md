# Recipients — methodology

The Recipients theme computes concentration diagnostics on CfD payments. Two methodology pieces: (a) payment attribution per recipient, (b) concentration metrics (Lorenz curve, thresholds).

## Recipient attribution

Payments are attributed to each `Name_of_CfD_Unit` (the LCCC station-level identifier). Multi-phase stations (e.g. Hornsea Phase 1, 2A, 2B) are treated as separate recipients because they have independent strike prices and contract terms. Units with zero or negative cumulative payment over the analysis window are excluded (they are net contributors, not recipients).

## Concentration metrics

The Lorenz curve sorts recipients by cumulative payment ascending, then plots cumulative % of recipients (x) vs cumulative % of £ (y). Threshold markers ("6 projects = 50%", "11 projects = 80%") are computed by finding the smallest recipient count whose cumulative % crosses each threshold.

Grouping keys: `(Name_of_CfD_Unit, Allocation_round)` — a unit contracted under multiple rounds is a single recipient per round (reflects how the contracts are legally written). Technology-level aggregation (for the Payments-by-technology chart) groups by `Technology_Type` from the LCCC portfolio snapshot.

## Data source

All computation uses LCCC *Actual CfD Generation and avoided GHG emissions* (per-unit daily settlement) joined against LCCC *CfD Contract Portfolio Status* (unit → technology type mapping). No gas counterfactual is needed — the concentration argument is entirely internal to the payments themselves.

## Gini coefficient (supplementary)

A Gini coefficient is computed over the same per-recipient cumulative-payment vector and reported as the headline number on the flagship chart. For current data, Gini ≈ 0.74 (compared to 0.34 for UK household income and 0.85 for UK household wealth — CfD payments are closer to wealth concentration than income concentration). The Gini is sensitive to the cutoff rule applied to "net contributor" units (those with negative cumulative payment) — the current rule excludes them rather than including with zero weight.
