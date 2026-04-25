"""Parquet determinism across rebuilds (TEST-05, D-21).

Rebuild the five CfD derived grains twice from the same raw state;
pyarrow.Table.equals() MUST return True. Does NOT compare raw bytes —
Parquet embeds a file-level `created_by` string and row-group metadata
timestamps that legitimately differ on every write. Content identity is
the spec-compliant determinism check.

If this fails: either (a) a non-determinism was introduced in
rebuild_derived() (clock reads, random.shuffle, groupby sort instability,
platform FMA drift), or (b) the methodology constants actually changed
— in which case bump METHODOLOGY_VERSION and add a CHANGES.md entry
under ## Methodology versions.
"""
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.schemes import cfd


GRAINS = (
    "station_month",
    "annual_summary",
    "by_technology",
    "by_allocation_round",
    "forward_projection",
)


@pytest.fixture(scope="module")
def derived_once(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("derived-run-1")
    cfd.rebuild_derived(output_dir=out)
    return out


@pytest.fixture(scope="module")
def derived_twice(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("derived-run-2")
    cfd.rebuild_derived(output_dir=out)
    return out


@pytest.mark.parametrize("grain", GRAINS)
def test_parquet_content_identical(grain, derived_once, derived_twice):
    """TEST-05: content equality across two rebuilds of the same raw state."""
    t1 = pq.read_table(derived_once / f"{grain}.parquet")
    t2 = pq.read_table(derived_twice / f"{grain}.parquet")
    assert t1.schema.equals(t2.schema, check_metadata=False), (
        f"Parquet schema drift for {grain}:\n  run1: {t1.schema}\n  run2: {t2.schema}"
    )
    assert t1.num_rows == t2.num_rows, (
        f"Row count drift for {grain}: {t1.num_rows} vs {t2.num_rows}"
    )
    assert t1.equals(t2), (
        f"Parquet content drift for {grain} — same raw input should produce "
        f"identical rows. If intentional (methodology change), bump "
        f"METHODOLOGY_VERSION (currently {METHODOLOGY_VERSION!r}) and add a "
        f"CHANGES.md `## Methodology versions` entry."
    )


@pytest.mark.parametrize("grain", GRAINS)
def test_file_metadata_created_by_is_pyarrow(grain, derived_once):
    """Pin the writer-identity so a migration to fastparquet/polars surfaces."""
    meta = pq.read_metadata(derived_once / f"{grain}.parquet")
    assert meta.created_by.startswith("parquet-cpp-arrow"), (
        f"Parquet writer changed for {grain}: {meta.created_by!r}"
    )


# ===========================================================================
# RO byte-identity parametrisation (Plan 05-10; TEST-05; D-21 Phase 4 contract).
#
# Per PATTERNS.md directive, RO uses INDEPENDENT module-scoped fixtures
# (`ro_derived_once`, `ro_derived_twice`) and a separate `RO_GRAINS` tuple.
# CfD + RO are NOT merged — each scheme rebuilds twice into its own tmp
# dirs so any cross-scheme ordering assumption is impossible.
# ===========================================================================

from uk_subsidy_tracker.schemes import ro  # noqa: E402

RO_GRAINS = (
    pytest.param("station_month", marks=pytest.mark.dormant),
    "annual_summary",
    "by_technology",
    pytest.param("by_allocation_round", marks=pytest.mark.dormant),
    pytest.param("forward_projection", marks=pytest.mark.dormant),
)


@pytest.fixture(scope="module")
def ro_derived_once(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("ro-derived-run-1")
    ro.rebuild_derived(output_dir=out)
    return out


@pytest.fixture(scope="module")
def ro_derived_twice(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("ro-derived-run-2")
    ro.rebuild_derived(output_dir=out)
    return out


@pytest.mark.parametrize("grain", RO_GRAINS)
def test_ro_parquet_content_identical(grain, ro_derived_once, ro_derived_twice):
    """TEST-05 / D-21: two consecutive ro.rebuild_derived() calls produce content-identical Parquet.

    Same semantics as the CfD test above: schema equality + row-count
    equality + ``pyarrow.Table.equals``. Catches non-determinism in
    ``schemes/ro/`` introduced via wall-clock reads, ``random.shuffle``,
    unstable groupby, or ``pd.Timestamp.now()`` anchors. Forward
    projection's deterministic ``output_period_end.max().year`` anchor
    (Phase 4 Plan 03 decision) is the load-bearing piece.
    """
    t1 = pq.read_table(ro_derived_once / f"{grain}.parquet")
    t2 = pq.read_table(ro_derived_twice / f"{grain}.parquet")
    assert t1.schema.equals(t2.schema, check_metadata=False), (
        f"RO Parquet schema drift for {grain}:\n  run1: {t1.schema}\n  run2: {t2.schema}"
    )
    assert t1.num_rows == t2.num_rows, (
        f"RO row count drift for {grain}: {t1.num_rows} vs {t2.num_rows}"
    )
    assert t1.equals(t2), (
        f"RO Parquet content drift for {grain} — same raw input should "
        f"produce identical rows. If intentional (methodology change), bump "
        f"METHODOLOGY_VERSION (currently {METHODOLOGY_VERSION!r}) and add a "
        f"CHANGES.md `## Methodology versions` entry."
    )


@pytest.mark.parametrize("grain", RO_GRAINS)
def test_ro_file_metadata_created_by_is_pyarrow(grain, ro_derived_once):
    """Pin RO writer-identity so a migration to fastparquet/polars surfaces."""
    meta = pq.read_metadata(ro_derived_once / f"{grain}.parquet")
    assert meta.created_by.startswith("parquet-cpp-arrow"), (
        f"RO Parquet writer changed for {grain}: {meta.created_by!r}"
    )
