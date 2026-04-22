"""Test ONS dataset download and loading."""

import pytest

from uk_subsidy_tracker.data.ons_gas import download_dataset, load_gas_price


@pytest.mark.skip(reason="hits live website")
def test_download_dataset():
    download_dataset()


def test_load_dataset():
    df = load_gas_price()
    assert not df.empty
    assert "date" in df.columns
