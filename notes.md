# LCCC Data Analysis Framework

## 1. Capacity Factor and Its Decay

### 1a. Monthly capacity factor by technology (time series)

For each CfD unit you need its installed capacity (MW). The LCCC file doesn't contain it directly, but it is on the LCCC "CfD Register" (same portal).

- Formula: CF = generation_MWh / (capacity_MW \* hours_in_month)
- Plot: CF by month for offshore wind, onshore wind, solar, biomass.
- Insight: Reveals seasonality (solar ~2% in Dec, ~18% in June) and the much-touted but often oversold "offshore wind runs at 50%" claim.

### 1b. Capacity-factor degradation curve

For each offshore wind farm, plot CF vs. years-since-commissioning.

- Insight: Industry assumes ~0% degradation; academic studies (Staffell & Green) suggest ~1.6%/yr. A scatter with a fitted slope is powerful.

### 1c. Fleet-wide CF distribution (violin/box plot per year)

- Insight: Shows that the average hides enormous variance — some farms deliver 25%, others 55%.

---

## 2. Intermittency and "Dark Doldrums"

### 2a. Daily generation heatmap (year x day-of-year)

- Plot: Total wind + solar CfD MWh as a colour grid.
- Insight: The dunkelflaute weeks (cold, still, dark — typically late Nov / early Feb) show up as vertical blue stripes. Very visually arresting.

### 2b. Load-duration curve

- Plot: Sort daily generation descending, plot on log x-axis.
- Insight: Shows the fleet delivers >80% of peak for only ~X% of hours. Contrast with a flat gas baseload line.

### 2c. Rolling 7-day minimum generation

- Insight: Picks out the worst weeks. Useful for a "what would storage have to cover?" argument.

---

## 3. Subsidy economics

### 3a. £/MWh subsidy time series, by allocation round

- Plot: Separate lines for Investment Contracts, AR1, AR2, AR4, AR5.
- Insight: Shows Investment Contracts are the cost millstone; newer rounds are (in theory) cheap.

### 3b. Cumulative consumer subsidy (£bn), stacked by technology

- Plot: An area chart climbing to £13 bn. Offshore wind and Hinkley dominate.

### 3c. Strike-price vs. wholesale-price "scissors" chart

- Plot: Two lines. The gap = subsidy per MWh.
- Insight: Crosses in 2022, reopens afterwards.

### 3d. Subsidy-per-tonne-CO2 avoided

- Formula: CFD_Payments_GBP / Avoided_GHG_tonnes_CO2e
- Comparison: Compare against UK ETS price (~£35–80/t) and DEFRA's social cost of carbon (~£280/t).
- Insight: Many years come out at £200–400/tCO2 — i.e. more expensive than the government's own carbon value.

### 3e. Bang-for-buck scatter

- Plot: x = total subsidy £m, y = total tCO2 avoided.
- Insight: Points above the diagonal are "cheap abatement", below are "expensive". Hinkley and the Investment Contract offshore wind farms usually sit badly.

---

## 4. The "cannibalisation" effect

### 4a. Wholesale capture price vs. fleet wind output

- Plot: Scatter of daily (or half-hourly if you pull Elexon data) wholesale price against total UK wind generation.
- Insight: Strong negative correlation: when wind blows hard, prices collapse -> renewables earn less per MWh they sell -> subsidies grow. This is why CfDs are needed, and also why adding more wind makes each marginal MW less economic.

### 4b. Capture-price ratio by year

- Formula: (Volume-weighted price wind actually got) / (time-weighted average wholesale price)
- Insight: Falls from ~100% toward 70–80% as penetration rises.

---

## 5. Curtailment and constraints

### 5a. Estimated curtailment vs. generation

LCCC data shows delivered MWh, not curtailed MWh. But you can pair it with NESO's Balancing Mechanism data (bmrs-api.elexonportal.co.uk) to show £m/year paid to Scottish wind farms to switch off because the grid can't move the power south. The Viking/Seagreen constraint costs are politically explosive numbers.

---

## 6. Concentration and lock-in

### 6a. Lorenz curve of subsidy receipts by project

- Plot: X = cumulative % of projects, Y = cumulative % of £.
- Insight: Typically ~80% of subsidy goes to ~10 projects. Reveals how much of the "renewables story" is actually just Hinkley + a handful of offshore wind farms.

### 6b. Remaining contract-years outstanding

- Plot: Each CfD is 15 years (35 for Hinkley). Stacked bar of £bn of future subsidy obligations by expiry year.
- Insight: Shows consumers are locked into Investment Contract costs until the late 2030s regardless of how cheap AR7 is.

---

## 7. The "negative subsidy was a mirage" angle

### 7a. 2022 clawback in context

- Plot: Monthly net payment chart.
- Insight: The 2022 refund looks big, but if you plot cumulative subsidy it's a small dent in a rising curve. Useful antidote to "CfDs saved consumers money" headlines.

---

## Recommended Starter Pack

1. Strike vs market price scissors chart, by technology (Section 3c).
2. Subsidy £/tCO2 avoided, by allocation round, by year (Section 3d).
3. Cumulative subsidy stacked by project (Section 3b + 6a) to expose concentration.
4. Daily generation heatmap (Section 2a) to show intermittency viscerally.
