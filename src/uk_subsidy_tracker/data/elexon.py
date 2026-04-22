"""Download and cache Elexon BMRS data — UK-wide wind/solar generation and system prices.

No API key required. Data is half-hourly (48 settlement periods per day).

Endpoints:
- AGWS: Actual or estimated wind and solar power generation (MW per period).
- System prices: settlement system buy/sell prices (£/MWh per period).

Downloaded data is cached as CSV in the project data directory. Re-running
the downloader appends new dates only.

Downloads are parallelised using concurrent.futures to keep total runtime
manageable (~3,500 days of system prices).
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

import pandas as pd
import requests

from cfd_payment import DATA_DIR

AGWS_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/AGWS"
SYSTEM_PRICE_URL = (
    "https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices"
)

AGWS_FILE = DATA_DIR / "elexon_agws.csv"
SYSTEM_PRICE_FILE = DATA_DIR / "elexon_system_prices.csv"

MAX_WORKERS = 10


def _fetch_agws_chunk(start: date, end: date) -> list[dict]:
    resp = requests.get(
        AGWS_URL,
        params={
            "publishDateTimeFrom": start.isoformat(),
            "publishDateTimeTo": end.isoformat(),
            "format": "json",
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def _fetch_agws(start: date, end: date) -> pd.DataFrame:
    """Fetch wind/solar generation data in parallel 7-day chunks."""
    chunks = []
    current = start
    while current < end:
        chunk_end = min(current + timedelta(days=7), end)
        chunks.append((current, chunk_end))
        current = chunk_end

    all_rows = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(_fetch_agws_chunk, s, e): (s, e) for s, e in chunks
        }
        done = 0
        for future in as_completed(futures):
            done += 1
            s, e = futures[future]
            rows = future.result()
            all_rows.extend(rows)
            if done % 20 == 0 or done == len(futures):
                print(f"  AGWS: {done}/{len(futures)} chunks")

    return pd.DataFrame(all_rows)


def _fetch_system_price_day(d: date) -> list[dict]:
    resp = requests.get(
        f"{SYSTEM_PRICE_URL}/{d.isoformat()}",
        params={"format": "json"},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def _fetch_system_prices(start: date, end: date) -> pd.DataFrame:
    """Fetch system prices in parallel, one day per request."""
    days = []
    current = start
    while current < end:
        days.append(current)
        current += timedelta(days=1)

    all_rows = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_fetch_system_price_day, d): d for d in days}
        done = 0
        for future in as_completed(futures):
            done += 1
            rows = future.result()
            all_rows.extend(rows)
            if done % 100 == 0 or done == len(futures):
                print(f"  System prices: {done}/{len(futures)} days")

    return pd.DataFrame(all_rows)


def download_elexon_data(
    start: date = date(2017, 1, 1),
    end: date | None = None,
) -> None:
    """Download AGWS and system price data to cached CSVs."""
    if end is None:
        end = date.today()

    print("Downloading Elexon AGWS (wind/solar generation)...")
    agws = _fetch_agws(start, end)
    if not agws.empty:
        agws.to_csv(AGWS_FILE, index=False)
        print(f"  Saved {len(agws)} rows to {AGWS_FILE}")

    print("Downloading Elexon system prices...")
    prices = _fetch_system_prices(start, end)
    if not prices.empty:
        prices.to_csv(SYSTEM_PRICE_FILE, index=False)
        print(f"  Saved {len(prices)} rows to {SYSTEM_PRICE_FILE}")


def load_elexon_wind_daily() -> pd.DataFrame:
    """Load cached AGWS data, aggregate to daily average wind MW.

    Returns DataFrame with columns: date, wind_mw (average onshore + offshore).
    """
    df = pd.read_csv(AGWS_FILE)
    wind = df[df["businessType"] == "Wind generation"]
    wind = wind.copy()
    wind["date"] = pd.to_datetime(wind["settlementDate"]).dt.date
    daily = wind.groupby("date")["quantity"].mean().rename("wind_mw").reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    return daily


def load_elexon_prices_daily() -> pd.DataFrame:
    """Load cached system prices, aggregate to daily average.

    Returns DataFrame with columns: date, price_gbp_per_mwh.
    """
    df = pd.read_csv(SYSTEM_PRICE_FILE)
    df["date"] = pd.to_datetime(df["settlementDate"]).dt.date
    daily = (
        df.groupby("date")["systemSellPrice"]
        .mean()
        .rename("price_gbp_per_mwh")
        .reset_index()
    )
    daily["date"] = pd.to_datetime(daily["date"])
    return daily


if __name__ == "__main__":
    download_elexon_data()
