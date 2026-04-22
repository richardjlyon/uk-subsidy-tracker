# Reliability — methodology

The Reliability theme computes fleet capacity-factor diagnostics. Three methodology pieces: (a) the CF formula, (b) installed-capacity attribution, (c) rolling statistics and drought detection.

## Capacity-factor formula

For a unit *u* on day *d*:

```
CF[u, d] = CFD_Generation_MWh[u, d] / (installed_capacity_MW[u, d] × 24)
```

Fleet-level CF is capacity-weighted:

```
CF_fleet[T, d] = sum( CF[u, d] × installed_capacity_MW[u, d] ) / sum( installed_capacity_MW[u, d] )
```

over the set of units *u* with technology type *T*.

## Installed capacity attribution

Installed capacity per unit over time is derived from the LCCC *CfD Contract Portfolio Status* snapshot. A unit's installed capacity starts at its first-generation date and remains at its nameplate until contract end. Pre-commissioning days are excluded from the fleet average (fleet CF would otherwise be artificially depressed by zero-generation days from yet-to-build units).

## Rolling statistics and drought detection

Rolling-minimum chart uses `pd.Series.rolling(window=21, center=True).mean()` on the daily fleet-CF series. Drought detection uses `scipy.signal.find_peaks` on the negative series with `prominence=15` (pp of CF), filtering for troughs that fall below each technology's reference CF line (20% for wind, 5% for solar — chosen as the published DESNZ-assumption floor less a margin).

## A note on pin tests

No dedicated pytest-level pin test currently freezes the CF formula above; schema validation via `tests/test_schemas.py` covers the underlying LCCC portfolio data. A CF-formula pin test is a candidate for Phase 4 alongside the Parquet variants of TEST-02/03/05. Treat the formula definitions on this page as the human-readable contract until that test lands.
