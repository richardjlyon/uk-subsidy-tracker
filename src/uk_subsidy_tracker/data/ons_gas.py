"""Handles Downloading and opening ONS gas price dataset."""

from pathlib import Path

import pandas as pd
import pandera.pandas as pa
import requests

from uk_subsidy_tracker import DATA_DIR
from uk_subsidy_tracker.data.utils import HEADERS

GAS_SAP_DATA_FILENAME = "raw/ons/gas-sap.xlsx"


# Pandera schema for the output of load_gas_price() (Phase 2 pre-Parquet scaffolding for TEST-02).
ons_gas_schema = pa.DataFrameSchema(
    {
        "date": pa.Column("datetime64[ns]", coerce=True),
        "gas_p_per_kwh": pa.Column(float, coerce=True),
    },
    strict=False,
    coerce=True,
)


def download_dataset() -> Path:
    """Download the latest ONS SAP gas dataset to the data directory.

    Raises requests.exceptions.RequestException on any network failure
    (D-17 fail-loud posture — the daily refresh workflow needs to see
    the failure, not a silently un-downloaded path).
    """
    # The official ONS file URI for the latest SAP gas dataset
    GAS_SAP_URL = "https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/output/datasets/systemaveragepricesapofgas/2026/systemaveragepriceofgasdataset160426.xlsx"

    output_path = DATA_DIR / GAS_SAP_DATA_FILENAME  # BOUND BEFORE try (gap #2 fix)

    try:
        response = requests.get(GAS_SAP_URL, headers=HEADERS, stream=True, timeout=60)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading ons_gas: {e}")
        raise  # fail loud per D-17 — no silent swallow


def load_gas_price() -> pd.DataFrame:
    """
    Load ONS daily System Average Price of gas.

    Returns a DataFrame with columns:
        date           : datetime64
        gas_p_per_kwh  : float — pence per kWh (thermal), as published
    """
    path = DATA_DIR / GAS_SAP_DATA_FILENAME
    raw = pd.read_excel(path, sheet_name="1.Daily SAP Gas", header=None)

    header_idx = raw[raw.iloc[:, 0].astype(str).str.contains("Date", na=False)].index[0]
    df = raw.iloc[header_idx + 1 :, :2].copy()
    df.columns = ["date", "gas_p_per_kwh"]
    df["date"] = pd.to_datetime(df["date"])
    df["gas_p_per_kwh"] = pd.to_numeric(df["gas_p_per_kwh"], errors="coerce")
    df = df.dropna(subset=["gas_p_per_kwh"]).reset_index(drop=True)
    df = ons_gas_schema.validate(df)
    return df


if __name__ == "__main__":
    download_dataset()
