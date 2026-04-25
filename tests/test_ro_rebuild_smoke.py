"""Smoke tests for the RO scheme module (Plan 05-05 Task 4).

Proves ARCHITECTURE §6.1 contract + Phase 4 D-21/D-12 invariants hold for
RO. Uses ``tmp_path_factory`` fixtures — no writes to ``data/derived/ro/``
itself.

Six tests (per Plan 05-05 <behavior>):
  1. ``isinstance(ro, SchemeModule)`` — Protocol conformance.
  2. ``rebuild_derived(tmp)`` emits 5 Parquet + 5 schema.json siblings.
  3. ``methodology_version`` column present on every grain (when non-empty).
  4. Byte-identical Parquet content across two rebuilds (D-21).
  5. ``validate()`` returns a list (may be empty on a clean rebuild).
  6. ``upstream_changed()`` returns a bool (True expected on Plan 05-01
     Option-D stubs because sidecars were backfilled separately; the
     assertion is a type check, with a note that False will hold once
     Plan 05-13 review lands real URLs + matching sidecars).

DORMANT: This entire module is dormant (Plan 05.2-02 audit cleanup, 2026-04-25).
All tests require ``ro.rebuild_derived()`` which reads ``ro-register.xlsx``
(station-level data, Option-D deferred). Re-activate on backlog 999.1.
"""
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.schemes import SchemeModule, ro

# All tests in this module are dormant — station-level RO path is Option-D deferred.
# Re-activate on backlog 999.1 (credentialed RER access) or 999.2 (SY1-SY4 prices).
pytestmark = pytest.mark.dormant


_GRAINS = [
    "station_month",
    "annual_summary",
    "by_technology",
    "by_allocation_round",
    "forward_projection",
]


@pytest.fixture(scope="module")
def ro_tmp(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("test-ro-smoke")
    ro.rebuild_derived(output_dir=out)
    return out


def test_ro_is_scheme_module():
    """§6.1 conformance — duck-typed Protocol check."""
    assert isinstance(ro, SchemeModule)


def test_ro_rebuild_emits_5_parquet(ro_tmp):
    for grain in _GRAINS:
        assert (ro_tmp / f"{grain}.parquet").exists(), f"missing {grain}.parquet"
        assert (
            ro_tmp / f"{grain}.schema.json"
        ).exists(), f"missing {grain}.schema.json"


def test_ro_methodology_version_column(ro_tmp):
    """Every RO Parquet column schema includes methodology_version; when the
    Parquet has rows, every row carries METHODOLOGY_VERSION (D-12 / GOV-02).
    Empty-row Parquets are accepted — they legitimately occur with the Plan
    05-01 Option-D stub inputs until Plan 05-13 review lands real data.
    """
    for grain in _GRAINS:
        table = pq.read_table(ro_tmp / f"{grain}.parquet")
        assert (
            "methodology_version" in table.column_names
        ), f"{grain} missing methodology_version column"
        df = table.to_pandas()
        if len(df) > 0:
            unique = set(df["methodology_version"].dropna().unique())
            assert unique == {
                METHODOLOGY_VERSION
            }, f"{grain} methodology_version drift: {unique}"


def test_ro_rebuild_is_deterministic(tmp_path_factory):
    """D-21 byte-identity: two rebuilds from identical raw state produce
    content-equal Parquet tables."""
    tmp1 = tmp_path_factory.mktemp("ro-det-1")
    tmp2 = tmp_path_factory.mktemp("ro-det-2")
    ro.rebuild_derived(output_dir=tmp1)
    ro.rebuild_derived(output_dir=tmp2)
    for grain in _GRAINS:
        t1 = pq.read_table(tmp1 / f"{grain}.parquet")
        t2 = pq.read_table(tmp2 / f"{grain}.parquet")
        assert t1.equals(t2), f"{grain} not deterministic across rebuilds"


def test_ro_validate_returns_list(ro_tmp, monkeypatch):
    """D-04 validate() returns list[str]. Point DERIVED_DIR at the smoke
    tmp so validate() reads the just-built tree rather than the repo's
    (possibly absent) data/derived/ro/ directory."""
    monkeypatch.setattr(ro, "DERIVED_DIR", ro_tmp)
    warnings = ro.validate()
    assert isinstance(warnings, list)
    assert all(isinstance(w, str) for w in warnings)


def test_ro_upstream_changed_returns_bool():
    """upstream_changed() must always return a bool (never None / raise).

    With the Plan 05-01 committed stubs + backfilled sidecars the expected
    value is False (sidecars were backfilled from the committed stub
    bytes). A True return here indicates stub drift between raw and
    sidecar — flag in Plan 05-13 review.
    """
    result = ro.upstream_changed()
    assert isinstance(result, bool)
