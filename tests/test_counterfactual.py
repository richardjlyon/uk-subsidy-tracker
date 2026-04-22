"""Pin the gas counterfactual formula against known inputs (TEST-01, GOV-04).

Any change to CCGT_EFFICIENCY, GAS_CO2_INTENSITY_THERMAL, DEFAULT_NON_FUEL_OPEX,
or DEFAULT_CARBON_PRICES fails a pin case below and forces the PR author to
simultaneously bump METHODOLOGY_VERSION and add a CHANGES.md entry under
## Methodology versions.
"""

import pandas as pd
import pytest

from uk_subsidy_tracker.counterfactual import (
    METHODOLOGY_VERSION,
    compute_counterfactual,
)


def test_methodology_version_present():
    """GOV-04: the version constant is importable and SemVer-shaped."""
    assert isinstance(METHODOLOGY_VERSION, str)
    parts = METHODOLOGY_VERSION.split(".")
    assert len(parts) == 3 and all(p.isdigit() for p in parts), (
        f"METHODOLOGY_VERSION must be SemVer X.Y.Z, got {METHODOLOGY_VERSION!r}"
    )


def test_methodology_version_in_output():
    """GOV-04: the column flows into the DataFrame so it reaches Parquet/manifest."""
    gas = pd.DataFrame({
        "date": pd.to_datetime(["2019-01-01"]),
        "gas_p_per_kwh": [1.5],
    })
    df = compute_counterfactual(gas_df=gas)
    assert "methodology_version" in df.columns
    assert (df["methodology_version"] == METHODOLOGY_VERSION).all()


@pytest.mark.parametrize(
    "date_str, gas_p_per_kwh, expected",
    [
        ("2019-01-01", 1.5, 39.6327),
        ("2019-06-01", 1.2, 34.1782),
        ("2022-10-01", 8.0, 168.1855),
        ("2019-01-01", 0.0, 12.3600),  # zero-gas regression
    ],
)
def test_counterfactual_pin(date_str, gas_p_per_kwh, expected):
    """TEST-01: pin the formula at 4 decimal places.

    Any change to CCGT_EFFICIENCY, GAS_CO2_INTENSITY_THERMAL, DEFAULT_NON_FUEL_OPEX,
    or DEFAULT_CARBON_PRICES fails this test. If intentional, bump
    METHODOLOGY_VERSION in src/uk_subsidy_tracker/counterfactual.py and add
    an entry to CHANGES.md under ## Methodology versions documenting the change.
    """
    gas = pd.DataFrame({
        "date": pd.to_datetime([date_str]),
        "gas_p_per_kwh": [gas_p_per_kwh],
    })
    df = compute_counterfactual(gas_df=gas)
    actual = df["counterfactual_total"].iloc[0]
    assert round(actual, 4) == expected, (
        f"Formula changed for {date_str} gas={gas_p_per_kwh}: "
        f"expected {expected}, got {round(actual, 4)}. "
        f"If intentional, bump METHODOLOGY_VERSION (currently "
        f"{METHODOLOGY_VERSION!r}) and add a CHANGES.md ## Methodology versions entry."
    )
