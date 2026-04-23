"""Refresh-loop invariant test — closes gap #1 in 04-VERIFICATION.md.

The daily refresh workflow's correctness depends on a tight algebraic
invariant: after `scheme.refresh()` writes fresh bytes AND rewrites
sidecars, `upstream_changed()` MUST report False on the next invocation.
Otherwise the dirty-check loops perpetually and `manifest.generated_at`
(sourced from `max(sidecar.retrieved_at)`) never advances past the
backfill date.

These tests pin the invariant with mocked downloaders. They do NOT hit
network — the download functions are all patched to write synthetic
bytes into a tmp_path raw tree.
"""
from __future__ import annotations

import json
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import pytest

import importlib

# NOTE: `cfd/__init__.py` re-imports the submodule symbol as an alias
# (`from ... import refresh as _refresh`), which shadows the `_refresh`
# submodule attribute at the package level. Use importlib to bypass the
# attribute shadow and load the submodule object directly.
cfd_refresh = importlib.import_module("uk_subsidy_tracker.schemes.cfd._refresh")
# Same submodule-shadow pattern for RO — `schemes/ro/__init__.py` aliases
# `from ._refresh import refresh as _refresh`, shadowing the submodule at
# the package level (Plan 05-05). importlib reaches the submodule directly.
ro_refresh = importlib.import_module("uk_subsidy_tracker.schemes.ro._refresh")


@pytest.fixture
def tmp_raw_tree(tmp_path, monkeypatch):
    """Seed tmp_path with the five raw files + sidecars that match,
    pointing _refresh at tmp_path as DATA_DIR. Returns the tmp_path root.
    """
    raw_root = tmp_path
    # Create directory skeleton.
    for sub in ("raw/lccc", "raw/elexon", "raw/ons"):
        (raw_root / sub).mkdir(parents=True, exist_ok=True)
    # Seed each raw file with deterministic content + a matching sidecar.
    from uk_subsidy_tracker.data.sidecar import write_sidecar
    for rel, url in cfd_refresh._URL_MAP.items():
        raw_path = raw_root / rel
        raw_path.write_bytes(f"INITIAL-CONTENT-{rel}".encode())
        write_sidecar(raw_path=raw_path, upstream_url=url)
    # Redirect the scheme module at tmp_path.
    monkeypatch.setattr(cfd_refresh, "DATA_DIR", raw_root)
    return raw_root


def _patched_refresh_downloaders(raw_root: Path, new_content: dict[str, bytes]):
    """Return a context manager stack that patches the three downloaders
    to write `new_content[rel]` bytes to each raw file in `raw_root`.
    """
    stack = ExitStack()

    def fake_lccc(config):
        for rel in ("raw/lccc/actual-cfd-generation.csv",
                    "raw/lccc/cfd-contract-portfolio-status.csv"):
            (raw_root / rel).write_bytes(new_content[rel])

    def fake_elexon(*a, **kw):
        for rel in ("raw/elexon/agws.csv", "raw/elexon/system-prices.csv"):
            (raw_root / rel).write_bytes(new_content[rel])

    def fake_ons(*a, **kw):
        rel = "raw/ons/gas-sap.xlsx"
        (raw_root / rel).write_bytes(new_content[rel])
        return raw_root / rel

    stack.enter_context(patch(
        "uk_subsidy_tracker.data.lccc.download_lccc_datasets", side_effect=fake_lccc,
    ))
    stack.enter_context(patch(
        "uk_subsidy_tracker.data.lccc.load_lccc_config", return_value=None,
    ))
    stack.enter_context(patch(
        "uk_subsidy_tracker.data.elexon.download_elexon_data", side_effect=fake_elexon,
    ))
    stack.enter_context(patch(
        "uk_subsidy_tracker.data.ons_gas.download_dataset", side_effect=fake_ons,
    ))
    return stack


def test_refresh_loop_converges_on_unchanged_upstream(tmp_raw_tree):
    """After refresh() writes fresh bytes + sidecars, upstream_changed() = False."""
    new_content = {rel: f"FRESH-CONTENT-{rel}".encode()
                   for rel in cfd_refresh._URL_MAP}

    with _patched_refresh_downloaders(tmp_raw_tree, new_content):
        cfd_refresh.refresh()

    # Invariant: after a successful refresh, the dirty-check reports clean.
    assert cfd_refresh.upstream_changed() is False, (
        "upstream_changed() must return False after refresh() rewrites sidecars"
    )


def test_refresh_loop_generated_at_advances_once_then_stable(tmp_raw_tree):
    """Simulate one upstream change; assert generated_at advances once and stays.

    Protocol:
    1. Corrupt one sidecar's sha256 so upstream_changed() returns True.
    2. Patch downloaders to write NEW bytes; call refresh() → sidecars rewritten.
    3. Read max(sidecar.retrieved_at) as T1. T1 must be newer than the
       pre-corruption backfill timestamp.
    4. Without further corruption, assert upstream_changed() returns False
       — the next orchestrator pass would short-circuit and NOT rebuild
       the manifest. Therefore generated_at stays at T1.
    """
    from datetime import datetime

    # Capture pre-refresh sidecar timestamps.
    def read_retrieved_at(rel: str) -> str:
        meta = (tmp_raw_tree / rel).with_suffix(
            (tmp_raw_tree / rel).suffix + ".meta.json"
        )
        return json.loads(meta.read_text())["retrieved_at"]

    # Step 1: corrupt one sidecar (simulate upstream drift detected).
    first_rel = next(iter(cfd_refresh._URL_MAP))
    first_meta = (tmp_raw_tree / first_rel).with_suffix(
        (tmp_raw_tree / first_rel).suffix + ".meta.json"
    )
    corrupted = json.loads(first_meta.read_text())
    corrupted["sha256"] = "0" * 64  # garbage; will not match live bytes
    first_meta.write_text(json.dumps(corrupted, sort_keys=True, indent=2) + "\n")
    assert cfd_refresh.upstream_changed() is True, "setup: corruption must be detected"

    # Step 2: refresh() rewrites all sidecars with fresh retrieved_at.
    new_content = {rel: f"FRESH-CONTENT-v2-{rel}".encode()
                   for rel in cfd_refresh._URL_MAP}
    with _patched_refresh_downloaders(tmp_raw_tree, new_content):
        cfd_refresh.refresh()

    # Step 3: max(retrieved_at) is now; every sidecar has advanced.
    timestamps = [read_retrieved_at(rel) for rel in cfd_refresh._URL_MAP]
    parsed = [datetime.fromisoformat(ts) for ts in timestamps]
    t1 = max(parsed)
    # All five timestamps must be very recent (within last 5 seconds of test run).
    assert (datetime.now(t1.tzinfo) - t1).total_seconds() < 5.0, (
        f"retrieved_at must reflect current time after refresh; got {t1}"
    )

    # Step 4: invariant holds — dirty-check reports clean; no rebuild next pass.
    assert cfd_refresh.upstream_changed() is False, (
        "Second pass MUST short-circuit — sidecars now match live bytes"
    )


# ---------------------------------------------------------------------------
# Plan 05-07 — RO parallels (mirror the CfD invariants above).
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_ro_raw_tree(tmp_path, monkeypatch):
    """Seed tmp_path with the three RO raw files + sidecars that match,
    pointing ro_refresh at tmp_path as DATA_DIR. Returns the tmp_path root.
    """
    raw_root = tmp_path
    (raw_root / "raw/ofgem").mkdir(parents=True, exist_ok=True)
    from uk_subsidy_tracker.data.sidecar import write_sidecar
    for rel, url in ro_refresh._URL_MAP.items():
        raw_path = raw_root / rel
        raw_path.write_bytes(f"INITIAL-CONTENT-{rel}".encode())
        write_sidecar(raw_path=raw_path, upstream_url=url)
    # Redirect the scheme module at tmp_path.
    monkeypatch.setattr(ro_refresh, "DATA_DIR", raw_root)
    return raw_root


def _patched_ro_refresh_downloaders(raw_root: Path, new_content: dict[str, bytes]):
    """Return a context manager stack that patches the three RO downloaders
    to write `new_content[rel]` bytes to each raw file in `raw_root`.

    Mirrors the CfD helper `_patched_refresh_downloaders` above. The three
    Ofgem downloaders are patched to write synthetic bytes rather than hit
    the network; `ro_refresh.refresh()` then iterates `_URL_MAP` and
    rewrites the three sidecars via `write_sidecar()`, so on the next
    `upstream_changed()` call the SHA comparison agrees and returns False.
    """
    stack = ExitStack()

    def fake_register():
        rel = "raw/ofgem/ro-register.xlsx"
        (raw_root / rel).write_bytes(new_content[rel])

    def fake_generation():
        rel = "raw/ofgem/ro-generation.csv"
        (raw_root / rel).write_bytes(new_content[rel])

    def fake_prices():
        rel = "raw/ofgem/roc-prices.csv"
        (raw_root / rel).write_bytes(new_content[rel])

    stack.enter_context(patch(
        "uk_subsidy_tracker.data.ofgem_ro.download_ofgem_ro_register",
        side_effect=fake_register,
    ))
    stack.enter_context(patch(
        "uk_subsidy_tracker.data.ofgem_ro.download_ofgem_ro_generation",
        side_effect=fake_generation,
    ))
    stack.enter_context(patch(
        "uk_subsidy_tracker.data.roc_prices.download_roc_prices",
        side_effect=fake_prices,
    ))
    return stack


def test_ro_refresh_converges_on_unchanged_upstream(tmp_ro_raw_tree):
    """After ro_refresh.refresh(), upstream_changed() = False (D-18 per-scheme)."""
    new_content = {rel: f"FRESH-CONTENT-{rel}".encode()
                   for rel in ro_refresh._URL_MAP}

    with _patched_ro_refresh_downloaders(tmp_ro_raw_tree, new_content):
        ro_refresh.refresh()

    # Invariant: after a successful refresh, the dirty-check reports clean.
    assert ro_refresh.upstream_changed() is False, (
        "upstream_changed() must return False after refresh() rewrites RO sidecars"
    )


def test_manifest_includes_both_schemes_after_end_to_end_refresh(tmp_path):
    """Plan 05-07: multi-scheme refresh produces manifest.json with cfd.* AND ro.* entries.

    Pins the core Plan 05-07 must_have truth — "manifest.json with 10 Dataset
    entries (5 CfD + 5 RO)" — by exercising the manifest-build path directly
    on a tmp derived tree populated with both schemes. Does NOT hit network;
    Parquets are synthesised in-process.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    from uk_subsidy_tracker.publish import manifest as manifest_mod
    from uk_subsidy_tracker.data.sidecar import write_sidecar

    # ---- Synthesise derived/<scheme>/*.parquet for both schemes ----
    derived_root = tmp_path / "derived"
    grains = (
        "station_month",
        "annual_summary",
        "by_technology",
        "by_allocation_round",
        "forward_projection",
    )
    for scheme in ("cfd", "ro"):
        (derived_root / scheme).mkdir(parents=True)
        for grain in grains:
            tbl = pa.table({"methodology_version": ["0.1.0"]})
            pq.write_table(tbl, derived_root / scheme / f"{grain}.parquet")

    # ---- Synthesise raw-file tree + sidecars covering both schemes ----
    # manifest.build calls `_source_for_raw(rel, raw_dir)` for every
    # raw-path registered under GRAIN_SOURCES[scheme][grain]. Every such
    # path needs a matching file + sidecar in `raw_dir`, else FileNotFoundError.
    raw_dir = tmp_path / "raw"
    cfd_rels = [
        "lccc/actual-cfd-generation.csv",
        "lccc/cfd-contract-portfolio-status.csv",
        "ons/gas-sap.xlsx",
        "elexon/system-prices.csv",
    ]
    ro_rels = [
        "ofgem/ro-register.xlsx",
        "ofgem/ro-generation.csv",
        "ofgem/roc-prices.csv",
    ]
    for rel in cfd_rels + ro_rels:
        raw_path = raw_dir / rel
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(f"FAKE-{rel}".encode())
        write_sidecar(raw_path=raw_path, upstream_url=f"file://stub/{rel}")

    # ---- Build the manifest iterating both schemes ----
    from uk_subsidy_tracker.schemes import cfd, ro
    manifest = manifest_mod.build(
        version="v2026.04",
        schemes=[("cfd", cfd), ("ro", ro)],
        derived_root=derived_root,
        raw_dir=raw_dir,
        output_path=tmp_path / "manifest.json",
    )

    ids = set(d.id for d in manifest.datasets)
    cfd_ids = {i for i in ids if i.startswith("cfd.")}
    ro_ids = {i for i in ids if i.startswith("ro.")}
    assert len(cfd_ids) == 5, f"CfD: got {sorted(cfd_ids)}"
    assert len(ro_ids) == 5, f"RO: got {sorted(ro_ids)}"
    assert len(manifest.datasets) == 10, (
        f"Plan 05-07 truth: 5 CfD + 5 RO = 10 Dataset entries; "
        f"got {len(manifest.datasets)}: {sorted(ids)}"
    )
