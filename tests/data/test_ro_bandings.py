"""Unit tests for RO bandings YAML + Pydantic loader (Plan 05-02 Task 2).

No network, no mocks -- straightforward in-process loader + lookup tests
against the committed ``src/uk_subsidy_tracker/data/ro_bandings.yaml``.

7 tests covering the CONTEXT D-01 (Ofgem-primary rocs_issued, YAML as cross-
check) + D-09 (NIROC coverage) + grandfathering (pre-2006-07-11 1 ROC/MWh
override) acceptance criteria.
"""

from __future__ import annotations

from datetime import date

import pytest

from uk_subsidy_tracker.data.ro_bandings import (
    RoBandingTable,
    load_ro_bandings,
)


@pytest.fixture(scope="module")
def table() -> RoBandingTable:
    """Shared RoBandingTable loaded once per test module."""
    return load_ro_bandings()


def test_load_returns_ro_banding_table(table: RoBandingTable) -> None:
    """Load succeeds and yields a RoBandingTable with >=44 entries."""
    assert isinstance(table, RoBandingTable)
    assert len(table.entries) >= 44, (
        f"expected >=44 entries, got {len(table.entries)}"
    )


def test_every_entry_has_provenance_fields(table: RoBandingTable) -> None:
    """Every entry carries source, url, basis, retrieved_on per constant-provenance pattern."""
    for entry in table.entries:
        assert entry.source.strip(), f"missing source: {entry}"
        assert entry.url is not None, f"missing url: {entry}"
        assert entry.basis.strip(), f"missing basis: {entry}"
        assert entry.retrieved_on is not None, f"missing retrieved_on: {entry}"


def test_lookup_offshore_wind_gb_pre_2013(table: RoBandingTable) -> None:
    """Offshore wind GB pre-2013 band returns 2.0 ROCs/MWh (REF Table 1 Pre-2013 cell)."""
    assert table.lookup("Offshore wind", "GB", date(2010, 6, 1)) == 2.0


def test_lookup_offshore_wind_gb_2013_14(table: RoBandingTable) -> None:
    """Offshore wind GB 2013/14 band returns 2.0 ROCs/MWh (REF Table 1 2013/14 cell)."""
    assert table.lookup("Offshore wind", "GB", date(2013, 8, 1)) == 2.0


def test_lookup_unknown_cell_raises_keyerror(table: RoBandingTable) -> None:
    """Unknown (technology, country, date) tuple raises KeyError with informative message."""
    with pytest.raises(KeyError) as exc:
        table.lookup("Unknown tech", "GB", date(2020, 1, 1))
    assert "Unknown tech" in str(exc.value)


def test_grandfathering_override(table: RoBandingTable) -> None:
    """Pre-2006-07-11 commissioning returns 1.0 regardless of the technology's banded rate."""
    # Onshore wind banded rate is 1.0 for the pre-2013 window; grandfathering also yields
    # 1.0, so use the date range to confirm the short-circuit fires (the grandfathered
    # row must exist and be the match, not a coincidence of the pre-2013 banded value).
    val = table.lookup("Onshore wind", "GB", date(2005, 3, 1))
    assert val == 1.0
    # Offshore wind's banded rate is 2.0 pre-2013, so pre-2006-07-11 returning 1.0 proves
    # the grandfathering short-circuit is doing real work.
    val_offshore = table.lookup("Offshore wind", "GB", date(2005, 3, 1))
    assert val_offshore == 1.0


def test_ni_offshore_wind_pre_2013(table: RoBandingTable) -> None:
    """NIROC offshore wind pre-2013 resolves to [ASSUMED] 2.0 entry."""
    val = table.lookup("Offshore wind", "NI", date(2010, 6, 1))
    assert val == 2.0
