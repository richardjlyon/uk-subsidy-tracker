"""Handles downloading and opening LCCC datasets."""

from pathlib import Path

import pandas as pd
import requests
import yaml
from pydantic import BaseModel

from cfd_payment import DATA_DIR
from cfd_payment.data.utils import HEADERS


# Schema for a single dataset entry
class LCCCDatasetConfig(BaseModel):
    name: str
    uuid: str
    filename: str
    description: str
    url: str


# Schema for the datasets
class LCCCAppConfig(BaseModel):
    datasets: list[LCCCDatasetConfig]

    def dataset(self, name: str) -> LCCCDatasetConfig:
        for d in self.datasets:
            if d.name == name:
                return d
        raise KeyError(name)


def load_lccc_config(config_path: str = "lccc_datasets.yaml") -> LCCCAppConfig:
    """Load the dataset configurations from a YAML file."""
    default_dir = Path(__file__).parent
    with open(default_dir / config_path, "r") as f:
        raw_config = yaml.safe_load(f)
        return LCCCAppConfig(**raw_config)


def download_lccc_datasets(config: LCCCAppConfig) -> None:
    """Download all datasets specified in the configuration."""
    for dataset in config.datasets:
        download_lccc_dataset(dataset.uuid, dataset.filename)


def download_lccc_dataset(uuid: str, filename: str) -> None:
    """Download a dataset by its UUID and save it to the data directory."""
    output_path = DATA_DIR / filename
    url = f"https://dp.lowcarboncontracts.uk/datastore/dump/{uuid}"
    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading {filename}: {e}")


def load_lccc_dataset(description: str) -> pd.DataFrame:
    """Load an LCCC dataset from its lccc_datasets.yaml description."""
    config = load_lccc_config()
    filename = config.dataset(description).filename
    return pd.read_csv(DATA_DIR / filename, parse_dates=["Settlement_Date"])
