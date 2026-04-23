"""Constants drift test (SEED-001 Tier 2).

The Phase-2 adversarial audit caught `GAS_CO2_INTENSITY_THERMAL = 0.184`
(wrong) vs 0.18290 (correct) by user inspection only. Tier-1 grep-
discipline on the `Provenance:` docstring blocks missed it. This test
is the tripwire that would have caught it.

Any edit to a counterfactual.py constant must:
  1. Update the live value in counterfactual.py.
  2. Update the matching entry in tests/fixtures/constants.yaml.
  3. Bump METHODOLOGY_VERSION.
  4. Add a CHANGES.md `## Methodology versions` entry.

Missing any of (2)-(4) fails this test with a remediation message
that points at the offender. `next_audit` overdue produces a warning
but does NOT fail (calendar events are not CI failures).

Tests ship in three shapes, mirroring `tests/test_counterfactual.py`:

- `test_every_tracked_constant_in_yaml`: parametrised over `_TRACKED`
  — every tracked constant has a YAML entry.
- `test_yaml_value_matches_live`: parametrised over `_TRACKED` — each
  YAML `value` matches its live constant to exact equality.
- `test_audits_not_overdue`: iterates all YAML entries; `warnings.warn`
  for any `next_audit < today`. Does not fail.
"""

from datetime import date
import warnings

import pytest

from tests.fixtures import load_constants
from uk_subsidy_tracker import counterfactual


# The enforcement allowlist. Adding a new regulator-sourced constant to
# counterfactual.py requires adding it here AND to tests/fixtures/constants.yaml;
# otherwise the tripwire does not fire.
_TRACKED = {
    "CCGT_EFFICIENCY",
    "GAS_CO2_INTENSITY_THERMAL",
    "DEFAULT_NON_FUEL_OPEX",
    # Every DEFAULT_CARBON_PRICES year key (2002-2026) is tracked so the
    # drift tripwire fires on any silent edit. Phase 5 Plan 05-04 extended
    # the live dict backward to 2002 for RO scheme coverage AND closed the
    # Phase 4 SEED-001 partial-coverage gap where 2018-2020 + 2024-2026
    # year keys lived on the module but were not tracked by this fixture.
    "DEFAULT_CARBON_PRICES_2002",
    "DEFAULT_CARBON_PRICES_2003",
    "DEFAULT_CARBON_PRICES_2004",
    "DEFAULT_CARBON_PRICES_2005",
    "DEFAULT_CARBON_PRICES_2006",
    "DEFAULT_CARBON_PRICES_2007",
    "DEFAULT_CARBON_PRICES_2008",
    "DEFAULT_CARBON_PRICES_2009",
    "DEFAULT_CARBON_PRICES_2010",
    "DEFAULT_CARBON_PRICES_2011",
    "DEFAULT_CARBON_PRICES_2012",
    "DEFAULT_CARBON_PRICES_2013",
    "DEFAULT_CARBON_PRICES_2014",
    "DEFAULT_CARBON_PRICES_2015",
    "DEFAULT_CARBON_PRICES_2016",
    "DEFAULT_CARBON_PRICES_2017",
    "DEFAULT_CARBON_PRICES_2018",
    "DEFAULT_CARBON_PRICES_2019",
    "DEFAULT_CARBON_PRICES_2020",
    "DEFAULT_CARBON_PRICES_2021",
    "DEFAULT_CARBON_PRICES_2022",
    "DEFAULT_CARBON_PRICES_2023",
    "DEFAULT_CARBON_PRICES_2024",
    "DEFAULT_CARBON_PRICES_2025",
    "DEFAULT_CARBON_PRICES_2026",
}
# 3 base + 25 DEFAULT_CARBON_PRICES_YYYY year keys = 28 tracked constants.


def _live_constants() -> dict[str, float]:
    """Reflect UPPERCASE numeric constants off the counterfactual module.

    Scalar constants (int/float) are returned as-is. The `DEFAULT_CARBON_PRICES`
    dict is expanded into synthetic `DEFAULT_CARBON_PRICES_{year}` keys so each
    year-price pair can be tracked separately in the YAML.
    """
    live: dict[str, float] = {}
    for attr in dir(counterfactual):
        if not attr.isupper():
            continue
        value = getattr(counterfactual, attr)
        # Bools are a subclass of int; exclude explicitly so flags never slip
        # into the tracked set.
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            live[attr] = float(value)
        elif attr == "DEFAULT_CARBON_PRICES" and isinstance(value, dict):
            for year, price in value.items():
                live[f"DEFAULT_CARBON_PRICES_{year}"] = float(price)
    return live


@pytest.fixture(scope="module")
def constants():
    return load_constants()


@pytest.mark.parametrize("name", sorted(_TRACKED))
def test_every_tracked_constant_in_yaml(name, constants):
    """Every `_TRACKED` constant must have a matching entry in constants.yaml."""
    live = _live_constants()
    assert name in live, (
        f"{name} is in _TRACKED but not exported by counterfactual. "
        f"Either remove it from _TRACKED or add it to counterfactual.py."
    )
    assert name in constants.entries, (
        f"No tests/fixtures/constants.yaml entry for {name}. "
        f"Per SEED-001 Tier 2, add a block with "
        f"{{source, url, basis, retrieved_on, next_audit, value, unit}} "
        f"matching the `Provenance:` docstring on the live constant. "
        f"Live value: {live[name]}."
    )


@pytest.mark.parametrize("name", sorted(_TRACKED))
def test_yaml_value_matches_live(name, constants):
    """YAML `value` must match the live constant to exact equality (drift detector)."""
    live = _live_constants()
    entry = constants.entries[name]
    assert live[name] == entry.value, (
        f"Drift detected for {name}: live = {live[name]}, yaml = {entry.value}. "
        f"Per SEED-001 Tier 2, if this change is intentional: "
        f"(1) bump METHODOLOGY_VERSION (currently "
        f"{counterfactual.METHODOLOGY_VERSION!r}), "
        f"(2) update tests/fixtures/constants.yaml to the new value, and "
        f"(3) add a CHANGES.md `## Methodology versions` entry documenting the change. "
        f"YAML source URL: {entry.url}"
    )


def test_audits_not_overdue(constants):
    """Warn (do NOT fail) when any YAML `next_audit` has passed.

    Calendar events are not CI failures — an overdue audit is a to-do item,
    not broken code. The warning surfaces in pytest output so maintainers
    see it during normal test runs.
    """
    today = date.today()
    overdue = [
        (name, entry)
        for name, entry in constants.entries.items()
        if entry.next_audit is not None and entry.next_audit < today
    ]
    for name, entry in overdue:
        warnings.warn(
            f"Overdue audit for {name}: next_audit = {entry.next_audit} "
            f"({(today - entry.next_audit).days} days ago). "
            f"Review source ({entry.url}) and update retrieved_on + next_audit."
        )
