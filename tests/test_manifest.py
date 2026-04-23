"""Manifest.json build, provenance, and round-trip discipline (Plan 04-04).

Tests cover eight behaviours:

1. `test_manifest_build_writes_file` — call publish.manifest.build(), assert
   site/data/manifest.json (or tmp equivalent) exists.
2. `test_manifest_provenance_fields_present` — every Dataset has id, title,
   grain, row_count, schema_url, parquet_url, csv_url, versioned_url, sha256,
   sources (non-empty), methodology_page. Top-level has version, generated_at,
   methodology_version, pipeline_git_sha, datasets.
3. `test_manifest_urls_are_absolute` — every URL starts with http(s)://.
4. `test_manifest_urls_are_strings` — Pitfall 6: URLs are plain `str` in JSON,
   not a wrapped object.
5. `test_manifest_roundtrip_byte_identical` — build → read → re-emit via the
   same json.dumps(sort_keys=True, indent=2) → assert byte-equal. Catches
   Pydantic version drift.
6. `test_manifest_sha256_matches_parquet` — recompute sha256 of the on-disk
   parquet; assert the stored value matches.
7. `test_manifest_methodology_version_matches_constant` — top-level field
   equals counterfactual.METHODOLOGY_VERSION exactly.
8. `test_manifest_generated_at_stable_when_no_upstream_change` — Pitfall 3
   mitigation: two consecutive calls with the same raw state produce the same
   generated_at (content-addressed, NOT datetime.now()).
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from uk_subsidy_tracker import DATA_DIR
from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.schemes import cfd


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def manifest_artifacts(tmp_path_factory):
    """Rebuild derived + build manifest once per test module.

    Copies raw files (including .meta.json sidecars) into a tmp dir so the
    manifest walker finds the sidecars. Uses shutil.copytree (portable to
    any CI runner / sandbox, including filesystems that disable symlinks).
    """
    from uk_subsidy_tracker.publish import manifest as manifest_mod

    out = tmp_path_factory.mktemp("manifest-artifacts")
    (out / "data" / "raw").mkdir(parents=True)
    for sub in ("lccc", "elexon", "ons"):
        target = DATA_DIR / "raw" / sub
        link = out / "data" / "raw" / sub
        shutil.copytree(target, link, dirs_exist_ok=True)
    derived_root = out / "data" / "derived"
    derived = derived_root / "cfd"
    cfd.rebuild_derived(output_dir=derived)
    manifest_path = out / "site" / "data" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    built = manifest_mod.build(
        version="v2026.04-rc1",
        schemes=[("cfd", cfd)],
        derived_root=derived_root,
        raw_dir=out / "data" / "raw",
        output_path=manifest_path,
    )
    return {
        "manifest": built,
        "manifest_path": manifest_path,
        "derived_dir": derived,
        "derived_root": derived_root,
        "raw_dir": out / "data" / "raw",
    }


# ---------------------------------------------------------------------------
# 1. File is written
# ---------------------------------------------------------------------------

def test_manifest_build_writes_file(manifest_artifacts):
    """build() emits manifest.json to output_path."""
    assert manifest_artifacts["manifest_path"].exists(), (
        f"Expected {manifest_artifacts['manifest_path']} on disk."
    )
    assert manifest_artifacts["manifest_path"].stat().st_size > 0


# ---------------------------------------------------------------------------
# 2. Provenance fields present
# ---------------------------------------------------------------------------

def test_manifest_provenance_fields_present(manifest_artifacts):
    """Every dataset + top-level manifest carries full GOV-02 provenance."""
    body = json.loads(manifest_artifacts["manifest_path"].read_text())
    # Top-level required fields (D-07 + GOV-02):
    for field in (
        "version", "generated_at", "methodology_version",
        "pipeline_git_sha", "datasets",
    ):
        assert field in body, f"manifest missing top-level field: {field}"
    assert body["datasets"], "datasets[] empty; expected 5 CfD grains"
    required = {
        "id", "title", "grain", "row_count",
        "schema_url", "parquet_url", "csv_url", "versioned_url",
        "sha256", "sources", "methodology_page",
    }
    for ds in body["datasets"]:
        missing = required - set(ds.keys())
        assert not missing, f"dataset {ds.get('id')} missing fields: {missing}"
        assert ds["sources"], f"dataset {ds['id']} has empty sources[]"
        for src in ds["sources"]:
            for field in ("name", "upstream_url", "retrieved_at", "source_sha256"):
                assert field in src, (
                    f"source of {ds['id']} missing field: {field}"
                )


# ---------------------------------------------------------------------------
# 3. Absolute URLs
# ---------------------------------------------------------------------------

def test_manifest_urls_are_absolute(manifest_artifacts):
    """D-09: every URL in the manifest is absolute (https://... or http://...)."""
    body = json.loads(manifest_artifacts["manifest_path"].read_text())
    for ds in body["datasets"]:
        for key in ("schema_url", "parquet_url", "csv_url", "versioned_url", "methodology_page"):
            url = ds[key]
            assert url.startswith(("http://", "https://")), (
                f"dataset {ds['id']} {key} not absolute: {url!r}"
            )
        for src in ds["sources"]:
            url = src["upstream_url"]
            assert url.startswith(("http://", "https://")), (
                f"dataset {ds['id']} source {src['name']} upstream_url not absolute: {url!r}"
            )


# ---------------------------------------------------------------------------
# 4. URLs are plain strings (Pitfall 6: Pydantic HttpUrl vs str)
# ---------------------------------------------------------------------------

def test_manifest_urls_are_strings(manifest_artifacts):
    """Pitfall 6: `upstream_url` etc. must serialise as str, not a wrapped object.

    A Pydantic v2 `HttpUrl` field can serialise differently across minor
    versions — sometimes as `str`, sometimes as an object with a __str__.
    We require plain `str` in the JSON to keep the public contract stable.
    """
    body = json.loads(manifest_artifacts["manifest_path"].read_text())
    for ds in body["datasets"]:
        for key in ("schema_url", "parquet_url", "csv_url", "versioned_url", "methodology_page"):
            assert isinstance(ds[key], str), (
                f"{ds['id']} {key} is {type(ds[key]).__name__}, expected str"
            )
        for src in ds["sources"]:
            assert isinstance(src["upstream_url"], str), (
                f"{ds['id']} source {src['name']} upstream_url is "
                f"{type(src['upstream_url']).__name__}, expected str"
            )


# ---------------------------------------------------------------------------
# 5. Byte-identical round-trip
# ---------------------------------------------------------------------------

def test_manifest_roundtrip_byte_identical(manifest_artifacts):
    """build → read bytes → parse via Manifest.model_validate → re-emit.

    The re-emitted bytes MUST equal the original — guards against Pydantic
    serialisation drift (HttpUrl vs str, datetime formatting, etc.).
    """
    from uk_subsidy_tracker.publish import manifest as manifest_mod

    body1 = manifest_artifacts["manifest_path"].read_text()
    reloaded = manifest_mod.Manifest.model_validate_json(body1)
    body2 = json.dumps(
        reloaded.model_dump(mode="json"),
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    ) + "\n"
    assert body1 == body2, (
        "Manifest round-trip not byte-identical — Pydantic is serialising "
        "differently on re-emit. Likely suspect: HttpUrl field or datetime "
        "with microseconds."
    )


# ---------------------------------------------------------------------------
# 6. sha256 matches the Parquet on disk
# ---------------------------------------------------------------------------

def test_manifest_sha256_matches_parquet(manifest_artifacts):
    """Each dataset.sha256 equals hashlib.sha256 of the on-disk Parquet."""
    body = json.loads(manifest_artifacts["manifest_path"].read_text())
    derived = manifest_artifacts["derived_dir"]
    for ds in body["datasets"]:
        # ds.id is 'cfd.station_month' → grain_file = 'station_month.parquet'
        grain = ds["id"].split(".", 1)[1]
        parquet_path = derived / f"{grain}.parquet"
        assert parquet_path.exists(), f"{parquet_path} missing"
        live = _sha256(parquet_path)
        assert ds["sha256"] == live, (
            f"{ds['id']} sha256 drift: manifest={ds['sha256']!r} "
            f"live={live!r}"
        )


# ---------------------------------------------------------------------------
# 7. methodology_version matches the live constant
# ---------------------------------------------------------------------------

def test_manifest_methodology_version_matches_constant(manifest_artifacts):
    """D-12 chain: top-level methodology_version equals the live constant."""
    body = json.loads(manifest_artifacts["manifest_path"].read_text())
    assert body["methodology_version"] == METHODOLOGY_VERSION, (
        f"manifest.methodology_version={body['methodology_version']!r} "
        f"disagrees with counterfactual.METHODOLOGY_VERSION={METHODOLOGY_VERSION!r}"
    )


# ---------------------------------------------------------------------------
# 8. generated_at stable across rebuilds (Pitfall 3)
# ---------------------------------------------------------------------------

def test_manifest_generated_at_stable_when_no_upstream_change(manifest_artifacts, tmp_path):
    """Pitfall 3: two manifest.build() calls with same raw state → same generated_at.

    If `generated_at = datetime.now()`, this fails on every run. The mitigation
    is to source generated_at from the latest retrieved_at across sidecars
    (content-addressed). This test is the structural guard.
    """
    from uk_subsidy_tracker.publish import manifest as manifest_mod

    derived_root = manifest_artifacts["derived_root"]
    raw = manifest_artifacts["raw_dir"]

    m2_path = tmp_path / "second-manifest.json"
    m2 = manifest_mod.build(
        version="v2026.04-rc1",
        schemes=[("cfd", cfd)],
        derived_root=derived_root,
        raw_dir=raw,
        output_path=m2_path,
    )
    # First call stored on manifest_artifacts["manifest"]
    m1 = manifest_artifacts["manifest"]
    assert m1.generated_at == m2.generated_at, (
        f"generated_at drifted without upstream change: "
        f"{m1.generated_at} vs {m2.generated_at}. "
        "Likely using datetime.now() somewhere — should be "
        "max(retrieved_at across sidecars)."
    )


# ---------------------------------------------------------------------------
# 9-11. Plan 05-06 — multi-scheme iteration (SCHEMES-parametric)
#
# These tests prove manifest.build iterates the `schemes` iterable rather than
# hard-coding CfD. They underpin Plan 05-07's RO registration (`("ro", ro)`
# appended to refresh_all.SCHEMES) — without SCHEMES iteration, RO Parquet
# grains would silently fail to surface in site/data/manifest.json.
#
# Fixtures build a synthetic `derived_root` tree with two schemes × five
# grains each (10 Parquet files). Sidecars in `raw_dir` satisfy the
# `_latest_retrieved_at` walker. GRAIN_SOURCES/TITLES/DESCRIPTIONS are
# extended via monkeypatch so RO entries surface through _build_dataset_entry
# (the B-02 per-grain provenance contract is preserved).
# ---------------------------------------------------------------------------

_RO_GRAINS = (
    "station_month",
    "annual_summary",
    "by_technology",
    "by_allocation_round",
    "forward_projection",
)

_FAKE_UPSTREAM_URL = "https://example.test/fake-raw"
_FAKE_RETRIEVED_AT = "2026-04-22T19:11:17+00:00"


def _write_fake_raw_with_sidecar(raw_dir: Path, publisher: str, filename: str) -> None:
    """Write a fake raw file + matching *.meta.json sidecar.

    Manifest._source_for_raw re-computes sha256 from the on-disk raw file
    (W-05 mitigation), so the sidecar's sha256 need not match pre-computation —
    but the sidecar MUST carry a 64-char hex SHA to satisfy the Pydantic
    pattern validator. We compute the real sha256 so sidecar and raw match
    from the first build.
    """
    publisher_dir = raw_dir / publisher
    publisher_dir.mkdir(parents=True, exist_ok=True)
    raw_path = publisher_dir / filename
    raw_path.write_text("col_a,col_b\n1,2\n", encoding="utf-8")
    digest = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    meta_path = raw_path.with_suffix(raw_path.suffix + ".meta.json")
    meta_path.write_text(
        json.dumps(
            {
                "sha256": digest,
                "upstream_url": _FAKE_UPSTREAM_URL,
                "retrieved_at": _FAKE_RETRIEVED_AT,
            },
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )


def _write_fake_parquet(path: Path) -> None:
    """Write a minimal valid Parquet file at `path`."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    path.parent.mkdir(parents=True, exist_ok=True)
    tbl = pa.table({"methodology_version": ["0.1.0"]})
    pq.write_table(tbl, path)


@pytest.fixture
def two_scheme_tree(tmp_path, monkeypatch):
    """Build a synthetic two-scheme derived_root + raw_dir.

    Extends GRAIN_SOURCES/TITLES/DESCRIPTIONS (via monkeypatch so other tests
    are unaffected) to register the five RO grains pointing at a fake
    `ofgem/fake.csv` raw file. Returns a dict the per-test bodies use to
    drive `manifest_mod.build`.
    """
    from uk_subsidy_tracker.publish import manifest as manifest_mod

    derived_root = tmp_path / "data" / "derived"
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)

    # One fake raw file per scheme — satisfies the `sources[]` contract for
    # every grain without exploding fixture size.
    _write_fake_raw_with_sidecar(raw_dir, "lccc", "fake.csv")
    _write_fake_raw_with_sidecar(raw_dir, "ofgem", "fake.csv")

    for scheme in ("cfd", "ro"):
        scheme_dir = derived_root / scheme
        scheme_dir.mkdir(parents=True)
        for grain in _RO_GRAINS:
            _write_fake_parquet(scheme_dir / f"{grain}.parquet")

    # Register minimal CfD overrides (pointing at fake raw) and a full RO
    # block. Preserves B-02: every (scheme, grain) pair has explicit sources.
    fake_cfd = {grain: ["lccc/fake.csv"] for grain in _RO_GRAINS}
    fake_ro = {grain: ["ofgem/fake.csv"] for grain in _RO_GRAINS}

    patched_sources = {"cfd": fake_cfd, "ro": fake_ro}
    patched_titles = {
        "cfd": {g: f"CfD {g}" for g in _RO_GRAINS},
        "ro": {g: f"RO {g}" for g in _RO_GRAINS},
    }
    patched_descriptions = {
        "cfd": {g: g for g in _RO_GRAINS},
        "ro": {g: g for g in _RO_GRAINS},
    }
    monkeypatch.setattr(manifest_mod, "GRAIN_SOURCES", patched_sources)
    monkeypatch.setattr(manifest_mod, "GRAIN_TITLES", patched_titles)
    monkeypatch.setattr(manifest_mod, "GRAIN_DESCRIPTIONS", patched_descriptions)

    class _FakeSchemeModule:
        """Protocol-shaped placeholder; manifest discovers grains via filesystem."""

        DERIVED_DIR = None

    schemes = [("cfd", _FakeSchemeModule()), ("ro", _FakeSchemeModule())]

    return {
        "derived_root": derived_root,
        "raw_dir": raw_dir,
        "schemes": schemes,
        "output_path": tmp_path / "site" / "data" / "manifest.json",
    }


def test_manifest_build_handles_two_schemes(two_scheme_tree):
    """Plan 05-06: two schemes × five grains each → exactly 10 datasets.

    IDs match `<scheme>.<grain>` for every (scheme, grain) pair — proves
    the f"cfd.{grain}" hard-code is gone and the iteration surfaces every
    registered scheme.
    """
    from uk_subsidy_tracker.publish import manifest as manifest_mod

    manifest = manifest_mod.build(
        version="v2026.04",
        schemes=two_scheme_tree["schemes"],
        derived_root=two_scheme_tree["derived_root"],
        raw_dir=two_scheme_tree["raw_dir"],
        output_path=two_scheme_tree["output_path"],
    )

    # 2 schemes × 5 grains = 10 datasets
    assert len(manifest.datasets) == 10, (
        f"expected 10 datasets (2 schemes × 5 grains), "
        f"got {len(manifest.datasets)}"
    )
    ids = sorted(d.id for d in manifest.datasets)
    expected = sorted(
        f"{scheme}.{grain}"
        for scheme in ("cfd", "ro")
        for grain in _RO_GRAINS
    )
    assert ids == expected, f"id set drift: {ids} != {expected}"


def test_manifest_urls_include_scheme_segment(two_scheme_tree):
    """Plan 05-06: every Dataset URL carries `/data/latest/<scheme>/<grain>.*`.

    Enforces that URLs route via the scheme segment — the contract external
    consumers (R, Python, JS) rely on for scheme-parametric file resolution.
    """
    import re
    from uk_subsidy_tracker.publish import manifest as manifest_mod

    manifest = manifest_mod.build(
        version="v2026.04",
        schemes=two_scheme_tree["schemes"],
        derived_root=two_scheme_tree["derived_root"],
        raw_dir=two_scheme_tree["raw_dir"],
        output_path=two_scheme_tree["output_path"],
    )

    # Site URL may carry a path prefix (e.g. GitHub Pages project subpath);
    # match absolute URL up to `/data/<segment>/<scheme>/<grain>.<ext>`.
    url_re = re.compile(r"^https?://\S+/data/latest/(cfd|ro)/[^/]+\.parquet$")
    versioned_re = re.compile(
        r"^https?://\S+/data/v2026\.04/(cfd|ro)/[^/]+\.parquet$"
    )
    schema_re = re.compile(
        r"^https?://\S+/data/latest/(cfd|ro)/[^/]+\.schema\.json$"
    )
    csv_re = re.compile(r"^https?://\S+/data/latest/(cfd|ro)/[^/]+\.csv$")

    for ds in manifest.datasets:
        scheme, _, grain = ds.id.partition(".")
        assert f"/data/latest/{scheme}/{grain}.parquet" in ds.parquet_url, (
            f"{ds.id} parquet_url missing scheme segment: {ds.parquet_url}"
        )
        assert f"/data/latest/{scheme}/{grain}.csv" in ds.csv_url, (
            f"{ds.id} csv_url missing scheme segment: {ds.csv_url}"
        )
        assert f"/data/latest/{scheme}/{grain}.schema.json" in ds.schema_url, (
            f"{ds.id} schema_url missing scheme segment: {ds.schema_url}"
        )
        assert f"/data/v2026.04/{scheme}/{grain}.parquet" in ds.versioned_url, (
            f"{ds.id} versioned_url missing scheme segment: {ds.versioned_url}"
        )
        assert url_re.match(ds.parquet_url), ds.parquet_url
        assert versioned_re.match(ds.versioned_url), ds.versioned_url
        assert schema_re.match(ds.schema_url), ds.schema_url
        assert csv_re.match(ds.csv_url), ds.csv_url

    # Both schemes must appear — proves iteration covers every registered
    # scheme, not just the first.
    all_urls = {ds.parquet_url for ds in manifest.datasets}
    assert any("/data/latest/cfd/" in u for u in all_urls), (
        "no CfD URL in manifest.datasets"
    )
    assert any("/data/latest/ro/" in u for u in all_urls), (
        "no RO URL in manifest.datasets — iteration stopped at cfd"
    )


def test_manifest_empty_scheme_derived_is_skipped(tmp_path, monkeypatch):
    """Plan 05-06: a scheme whose derived_root/<name>/ does not exist is skipped.

    Valid pre-first-rebuild state: a scheme is registered in SCHEMES before
    its first `rebuild_derived()` has run. manifest.build must not crash;
    it emits zero Dataset entries for that scheme and continues with the
    rest of the iteration.
    """
    from uk_subsidy_tracker.publish import manifest as manifest_mod

    derived_root = tmp_path / "data" / "derived"
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    _write_fake_raw_with_sidecar(raw_dir, "lccc", "fake.csv")

    # Create CfD scheme_derived dir + 1 grain; do NOT create ro/.
    cfd_dir = derived_root / "cfd"
    cfd_dir.mkdir(parents=True)
    _write_fake_parquet(cfd_dir / "station_month.parquet")

    # Monkeypatch scheme-keyed provenance to keep CfD grain registered.
    monkeypatch.setattr(
        manifest_mod, "GRAIN_SOURCES",
        {"cfd": {"station_month": ["lccc/fake.csv"]}},
    )
    monkeypatch.setattr(
        manifest_mod, "GRAIN_TITLES",
        {"cfd": {"station_month": "CfD station-month"}},
    )
    monkeypatch.setattr(
        manifest_mod, "GRAIN_DESCRIPTIONS",
        {"cfd": {"station_month": "station × month"}},
    )

    class _FakeSchemeModule:
        DERIVED_DIR = None

    schemes = [
        ("cfd", _FakeSchemeModule()),
        ("ro", _FakeSchemeModule()),  # no derived/ro/ on disk — must skip
    ]

    manifest = manifest_mod.build(
        version="v2026.04",
        schemes=schemes,
        derived_root=derived_root,
        raw_dir=raw_dir,
        output_path=tmp_path / "manifest.json",
    )

    # Only CfD's single grain surfaces; RO is silently skipped (not an error).
    assert len(manifest.datasets) == 1
    assert manifest.datasets[0].id == "cfd.station_month"
    ro_ids = [d.id for d in manifest.datasets if d.id.startswith("ro.")]
    assert not ro_ids, f"RO should be skipped (no derived dir), got: {ro_ids}"
