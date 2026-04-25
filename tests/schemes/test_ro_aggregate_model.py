"""Unit tests for the RO aggregate-grain pipeline (Plan 05.2-03 Task 2a + 2b).

Tests 1-5: module-level isolation (Task 2a).
Tests 6-8: integration with schemes.ro (Task 2b — added in a later step).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pyarrow.parquet as pq
import pytest


# ===========================================================================
# Task 2a — module-level tests (aggregate_model.py in isolation).
# ===========================================================================


def test_aggregate_model_imports():
    """Test 1: both public build functions importable without error."""
    from uk_subsidy_tracker.schemes.ro.aggregate_model import (
        build_annual_summary_aggregate,
        build_by_technology_aggregate,
    )
    assert callable(build_annual_summary_aggregate)
    assert callable(build_by_technology_aggregate)


def test_build_annual_summary_aggregate_emits_parquet(tmp_path):
    """Test 2: annual_summary.parquet lands in tmp_path with at least 7 GB rows."""
    from uk_subsidy_tracker.schemes.ro.aggregate_model import build_annual_summary_aggregate

    df = build_annual_summary_aggregate(tmp_path)
    parquet_path = tmp_path / "annual_summary.parquet"
    assert parquet_path.exists(), "annual_summary.parquet not written to tmp_path"
    assert len(df) > 0, "Returned DataFrame is empty"

    # At least 7 GB rows (SY17-SY23, one row per year per GB country)
    gb_rows = df[df["country"] == "GB"]
    assert len(gb_rows) >= 7, (
        f"Expected at least 7 GB rows (SY17-SY23), got {len(gb_rows)}"
    )


def test_build_by_technology_aggregate_emits_parquet(tmp_path):
    """Test 3: by_technology.parquet lands in tmp_path with rows keyed on (year, technology)."""
    from uk_subsidy_tracker.schemes.ro.aggregate_model import build_by_technology_aggregate

    df = build_by_technology_aggregate(tmp_path)
    parquet_path = tmp_path / "by_technology.parquet"
    assert parquet_path.exists(), "by_technology.parquet not written to tmp_path"
    assert len(df) > 0, "Returned DataFrame is empty"
    assert "year" in df.columns
    assert "technology" in df.columns


def test_annual_summary_is_deterministic(tmp_path):
    """Test 4: two consecutive calls produce byte-identical Parquet files (D-21)."""
    from uk_subsidy_tracker.schemes.ro.aggregate_model import build_annual_summary_aggregate

    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    build_annual_summary_aggregate(out1)
    build_annual_summary_aggregate(out2)

    p1 = out1 / "annual_summary.parquet"
    p2 = out2 / "annual_summary.parquet"
    sha1 = hashlib.sha256(p1.read_bytes()).hexdigest()
    sha2 = hashlib.sha256(p2.read_bytes()).hexdigest()
    assert sha1 == sha2, (
        f"Non-deterministic Parquet output: sha256 mismatch between two runs "
        f"(D-21 violation)"
    )


def test_every_row_has_methodology_version_0_1_0(tmp_path):
    """Test 5: methodology_version == '0.1.0' on every row of both grains."""
    from uk_subsidy_tracker.schemes.ro.aggregate_model import (
        build_annual_summary_aggregate,
        build_by_technology_aggregate,
    )

    df_ann = build_annual_summary_aggregate(tmp_path)
    df_tech = build_by_technology_aggregate(tmp_path)

    for df, name in [(df_ann, "annual_summary"), (df_tech, "by_technology")]:
        unique = df["methodology_version"].unique().tolist()
        assert unique == ["0.1.0"], (
            f"{name}: expected methodology_version == ['0.1.0'], got {unique}"
        )


# ===========================================================================
# Task 2b — integration tests (schemes.ro wiring + DORMANT_STATION_LEVEL).
# ===========================================================================


def test_schemes_ro_is_scheme_module():
    """Test 6: schemes.ro satisfies the SchemeModule Protocol (five-function contract)."""
    from uk_subsidy_tracker.schemes import ro
    from uk_subsidy_tracker.schemes import SchemeModule

    assert isinstance(ro, SchemeModule), (
        "schemes.ro does not satisfy SchemeModule Protocol — "
        "check that all five callables are present and DERIVED_DIR is a Path"
    )


def test_rebuild_derived_dormant_emits_only_two_grains(tmp_path):
    """Test 7: with DORMANT_STATION_LEVEL=True, rebuild_derived emits only the two aggregate grains."""
    from uk_subsidy_tracker.schemes import ro

    assert ro.DORMANT_STATION_LEVEL is True, (
        "DORMANT_STATION_LEVEL must be True for this test; flip the flag to re-run station-level"
    )

    ro.rebuild_derived(tmp_path)

    # Must exist
    assert (tmp_path / "annual_summary.parquet").exists(), "annual_summary.parquet not emitted"
    assert (tmp_path / "by_technology.parquet").exists(), "by_technology.parquet not emitted"

    # Must NOT exist (D-05: station-level grains skipped while dormant)
    assert not (tmp_path / "station_month.parquet").exists(), (
        "station_month.parquet was emitted despite DORMANT_STATION_LEVEL=True"
    )
    assert not (tmp_path / "by_allocation_round.parquet").exists(), (
        "by_allocation_round.parquet was emitted despite DORMANT_STATION_LEVEL=True"
    )
    assert not (tmp_path / "forward_projection.parquet").exists(), (
        "forward_projection.parquet was emitted despite DORMANT_STATION_LEVEL=True"
    )


def test_refresh_dormant_skips_station_level(monkeypatch):
    """Test 8: when DORMANT_STATION_LEVEL=True, refresh() does not call station-level downloaders.

    Monkeypatches the module-level functions that _refresh.py imports from
    inside its function body (lazy imports). The patched targets are the
    module objects that contain the functions, not the function names in _refresh
    itself (since _refresh uses lazy `from ... import ...` inside refresh()).
    """
    from pathlib import Path

    # Patch download_twelve_year_xlsx on its own module so the lazy import
    # inside _refresh.refresh() picks up the stub.
    import uk_subsidy_tracker.data.ofgem_aggregate as agg_mod

    def fake_download_twelve_year_xlsx() -> Path:
        import tempfile
        p = Path(tempfile.mktemp(suffix=".xlsx"))
        p.write_bytes(b"fake")
        return p

    monkeypatch.setattr(agg_mod, "download_twelve_year_xlsx", fake_download_twelve_year_xlsx)

    # Patch write_sidecar on its own module.
    import uk_subsidy_tracker.data.sidecar as sidecar_mod
    monkeypatch.setattr(sidecar_mod, "write_sidecar", lambda **kwargs: None)

    # Station-level downloaders must NOT be called when dormant.
    def _should_not_be_called(*args, **kwargs):
        raise RuntimeError("station-level downloader called despite DORMANT_STATION_LEVEL=True")

    try:
        import uk_subsidy_tracker.data.ofgem_ro as ofgem_ro_mod
        monkeypatch.setattr(ofgem_ro_mod, "download_ofgem_ro_register", _should_not_be_called)
        monkeypatch.setattr(ofgem_ro_mod, "download_ofgem_ro_generation", _should_not_be_called)
    except (ImportError, AttributeError):
        pass  # dormant module may not expose these callables; skip

    try:
        import uk_subsidy_tracker.data.roc_prices as roc_prices_mod
        monkeypatch.setattr(roc_prices_mod, "download_roc_prices", _should_not_be_called)
    except (ImportError, AttributeError):
        pass

    # Call ro.refresh() — it delegates to _refresh.refresh() via the bound alias.
    from uk_subsidy_tracker.schemes import ro
    assert ro.DORMANT_STATION_LEVEL is True
    # Should complete without raising RuntimeError from any _should_not_be_called stub.
    ro.refresh()
