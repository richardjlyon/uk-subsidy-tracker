"""Handles Downloading and opening ONS gas price dataset."""

from pathlib import Path

import pandas as pd
import requests

from cfd_payment import DATA_DIR
from cfd_payment.data.utils import HEADERS

GAS_SAP_DATA_FILENAME = "ons_gas_sap.xlsx"


def download_dataset() -> Path:
    """Download a file from a URL and save it to the data directory."""
    # The official ONS file URI for the latest SAP gas dataset
    GAS_SAP_URL = "https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/output/datasets/systemaveragepricesapofgas/2026/systemaveragepriceofgasdataset160426.xlsx"

    try:
        response = requests.get(GAS_SAP_URL, headers=HEADERS, stream=True)
        response.raise_for_status()

        output_path = DATA_DIR / GAS_SAP_DATA_FILENAME
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return output_path


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
    return df


if __name__ == "__main__":
    download_dataset()
