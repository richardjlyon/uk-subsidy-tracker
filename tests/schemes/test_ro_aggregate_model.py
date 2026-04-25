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
