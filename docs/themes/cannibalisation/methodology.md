# Cannibalisation — methodology

The Cannibalisation theme computes the gap between fleet-average wholesale prices and technology-specific capture prices. Two methodology pieces: (a) capture-price ratio, (b) the CfD levy per MWh.

## Capture-price ratio

Capture price for technology *T* is the generation-weighted wholesale price during the hours *T* generated:

```
capture_price[T] = sum( market_reference_price[t] × generation[T, t] ) / sum( generation[T, t] )
```

Time-weighted wholesale is the unweighted mean of `Market_Reference_Price_GBP_Per_MWh` across the same period. The ratio is `capture_price[T] / time_weighted_wholesale`. Values < 1 indicate the technology's output correlates with low prices (cannibalisation); values > 1 would indicate output correlates with high prices. Wind trends down from ~0.95 in 2016 to below 0.75 today.

## CfD levy per MWh

For the bottom-panel levy bar chart, aggregation is AR1 wind units only (the allocation round with the longest price-history). Levy `£/MWh = CFD_Payments_GBP / CFD_Generation_MWh`. Positive values (blue in the chart) indicate consumer top-up; negative values (green) indicate producer clawback during high-gas periods like 2022.

## Data source

All computation uses LCCC *Actual CfD Generation and avoided GHG emissions* as the single input. No gas counterfactual is needed for this theme — the cannibalisation argument is market-internal (capture price vs time-weighted price, both from the same LCCC reference price field).
