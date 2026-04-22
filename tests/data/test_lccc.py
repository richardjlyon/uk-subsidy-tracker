"""Test LCCC dataset config and loading. Ensure datasets have been downloaded first."""

import pytest

from uk_subsidy_tracker.data.lccc import (
    download_lccc_datasets,
    load_lccc_config,
    load_lccc_dataset,
)


@pytest.mark.skip(reason="hits live wwebsite")
def test_download_lccc_datasets():
    config = load_lccc_config()
    download_lccc_datasets(config)


def test_load_config():
    config = load_lccc_config()
    assert len(config.datasets) > 0
    assert config.dataset(
        "Actual CfD Generation and avoided GHG emissions"
    ).filename.endswith(".csv")


def test_load_dataset():
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    assert not df.empty
    assert "Settlement_Date" in df.columns
