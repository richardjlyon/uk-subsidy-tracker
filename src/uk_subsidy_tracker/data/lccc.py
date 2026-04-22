"""Handles downloading and opening LCCC datasets."""

from pathlib import Path

import pandas as pd
import pandera.pandas as pa
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


# Define validation schemas for the .csv datasets
lccc_generation_schema = pa.DataFrameSchema(
    {
        "Settlement_Date": pa.Column("datetime64[ns]"),
        "CfD_ID": pa.Column(str),
        "Name_of_CfD_Unit": pa.Column(str),
        "Technology": pa.Column(str),
        "Allocation_round": pa.Column(str),
        "Reference_Type": pa.Column(str),
        "CFD_Generation_MWh": pa.Column(float, nullable=True),
        "Avoided_GHG_tonnes_CO2e": pa.Column(float, nullable=True),
        "Strike_Price_GBP_Per_MWh": pa.Column(float, nullable=True),
        "CFD_Payments_GBP": pa.Column(float),
        "Avoided_GHG_Cost_GBP": pa.Column(float, nullable=True),
        "Market_Reference_Price_GBP_Per_MWh": pa.Column(float, nullable=True),
        "Weighted_IMRP_GBP_Per_MWh": pa.Column(float, nullable=True),
    },
    strict=False,
    coerce=True,
)

lccc_portfolio_schema = pa.DataFrameSchema(
    {
        "CFD_ID": pa.Column(str),
        "Name_of_CFD_Unit": pa.Column(str),
        "Allocation_Round": pa.Column(str),
        "Technology_Type": pa.Column(str),
        "Transmission_or_Distribution_connection": pa.Column(str),
        "Status": pa.Column(str),
        "Expected_Start_Date": pa.Column("datetime64[ns]", nullable=True),
        "Maximum_Contract_Capacity_MW": pa.Column(float, nullable=True),
    },
    strict=False,
    coerce=True,
)

SCHEMAS = {
    "Actual CfD Generation and avoided GHG emissions": lccc_generation_schema,
    "CfD Contract Portfolio Status": lccc_portfolio_schema,
}


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
    """Load and vallidate an LCCC dataset from its lccc_datasets.yaml description."""
    config = load_lccc_config()
    filename = config.dataset(description).filename
    df = pd.read_csv(DATA_DIR / filename)

    schema = SCHEMAS[description]
    df = schema.validate(df)

    return df
