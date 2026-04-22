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
    derived = out / "data" / "derived" / "cfd"
    cfd.rebuild_derived(output_dir=derived)
    manifest_path = out / "site" / "data" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    built = manifest_mod.build(
        version="v2026.04-rc1",
        derived_dir=derived,
        raw_dir=out / "data" / "raw",
        output_path=manifest_path,
    )
    return {
        "manifest": built,
        "manifest_path": manifest_path,
        "derived_dir": derived,
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

    derived = manifest_artifacts["derived_dir"]
    raw = manifest_artifacts["raw_dir"]

    m2_path = tmp_path / "second-manifest.json"
    m2 = manifest_mod.build(
        version="v2026.04-rc1",
        derived_dir=derived,
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
