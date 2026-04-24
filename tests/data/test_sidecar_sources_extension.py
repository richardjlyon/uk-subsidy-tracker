"""Unit tests for the ``sources[]`` extension to ``write_sidecar()`` (Phase 05.2 D-03).

The extension adds an optional ``sources: list[dict] | None = None`` keyword
argument; when provided, the sidecar JSON gains a top-level ``sources`` array
recording per-row provenance for transcribed-from-multiple-PDFs files.

Backward-compatibility contract:
  - Existing 2-positional-arg callers (``write_sidecar(raw_path, upstream_url)``)
    produce the same 5-key meta JSON byte-for-byte (apart from ``retrieved_at``
    + ``sha256`` which depend on inputs).
  - ``sources=None`` MUST omit the key entirely, NOT serialise as ``"sources": null``.
  - Serialisation invariants preserved: ``sort_keys=True``, ``indent=2``,
    trailing newline; atomic ``.tmp`` + ``os.replace`` write.
"""
from __future__ import annotations

import json

from uk_subsidy_tracker.data.sidecar import write_sidecar


def _make_raw_file(tmp_path, name="probe.bin", content=b"hello-sidecar"):
    raw_path = tmp_path / name
    raw_path.write_bytes(content)
    return raw_path


def test_write_sidecar_omits_sources_key_when_not_provided(tmp_path):
    """Backward compat: omitting `sources` produces meta with exactly 5 keys."""
    raw_path = _make_raw_file(tmp_path)
    meta_path = write_sidecar(raw_path, "https://example.test/probe.bin")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert set(meta.keys()) == {
        "retrieved_at",
        "upstream_url",
        "sha256",
        "http_status",
        "publisher_last_modified",
    }
    assert "sources" not in meta


def test_write_sidecar_sources_none_byte_parity_with_no_kwarg(tmp_path):
    """Passing `sources=None` MUST be byte-identical to omitting the kwarg.

    Critical invariant: `sources=None` must NOT serialise as `"sources": null` —
    it must omit the key entirely so existing single-URL sidecars stay
    byte-identical regardless of whether the caller passes the kwarg.
    """
    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"
    dir_a.mkdir()
    dir_b.mkdir()
    raw_a = dir_a / "probe.bin"
    raw_b = dir_b / "probe.bin"
    raw_a.write_bytes(b"hello-sidecar")
    raw_b.write_bytes(b"hello-sidecar")

    meta_a = write_sidecar(raw_a, "https://example.test/probe.bin")
    meta_b = write_sidecar(raw_b, "https://example.test/probe.bin", sources=None)

    text_a = meta_a.read_text(encoding="utf-8")
    text_b = meta_b.read_text(encoding="utf-8")
    # Strip the per-call timestamps (only differ in the ms field) before parity check.
    parsed_a = json.loads(text_a)
    parsed_b = json.loads(text_b)
    parsed_a.pop("retrieved_at")
    parsed_b.pop("retrieved_at")
    assert parsed_a == parsed_b
    assert "sources" not in parsed_a
    assert "sources" not in parsed_b


def test_write_sidecar_includes_sources_when_provided(tmp_path):
    """New behaviour: `sources=[...]` lands as a `sources` array in the meta JSON."""
    raw_path = _make_raw_file(tmp_path)
    sources = [
        {
            "url": "https://www.ofgem.gov.uk/example/sy17.pdf",
            "sha256": "abc123",
            "retrieved_on": "2026-04-24",
            "notes": "SY17 annual report",
        },
        {
            "url": "https://www.ofgem.gov.uk/example/sy18.pdf",
            "sha256": "def456",
            "retrieved_on": "2026-04-24",
            "notes": "SY18 annual report",
        },
    ]
    meta_path = write_sidecar(
        raw_path,
        "transcribed:ofgem-annual-reports",
        sources=sources,
    )
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert "sources" in meta
    assert meta["sources"] == sources
    # The 5 standard keys MUST still be present.
    for key in (
        "retrieved_at",
        "upstream_url",
        "sha256",
        "http_status",
        "publisher_last_modified",
    ):
        assert key in meta


def test_write_sidecar_serialisation_invariants_preserved(tmp_path):
    """sort_keys=True + indent=2 + trailing newline + atomic replace."""
    raw_path = _make_raw_file(tmp_path)
    sources = [{"url": "https://example.test/x.pdf", "sha256": "h", "retrieved_on": "2026-04-24", "notes": "n"}]
    meta_path = write_sidecar(
        raw_path,
        "transcribed:ofgem-annual-reports",
        sources=sources,
    )
    text = meta_path.read_text(encoding="utf-8")
    # Trailing newline.
    assert text.endswith("\n")
    # Indented JSON (2 spaces) — first nested key starts after a newline + 2 spaces.
    assert "\n  " in text
    # sort_keys=True ⇒ keys appear alphabetically. http_status < publisher_last_modified <
    # retrieved_at < sha256 < sources < upstream_url.
    expected_order = [
        "http_status",
        "publisher_last_modified",
        "retrieved_at",
        "sha256",
        "sources",
        "upstream_url",
    ]
    last_idx = -1
    for key in expected_order:
        idx = text.index(f'"{key}"')
        assert idx > last_idx, (
            f"sort_keys=True violated: {key} appeared out of alphabetical order"
        )
        last_idx = idx
    # No leftover .tmp file.
    tmp_leftover = meta_path.with_suffix(meta_path.suffix + ".tmp")
    assert not tmp_leftover.exists(), "Atomic write left a .tmp file behind"


def test_write_sidecar_sources_signature_has_param():
    """The function signature MUST expose the `sources` keyword argument."""
    import inspect

    sig = inspect.signature(write_sidecar)
    assert "sources" in sig.parameters
    param = sig.parameters["sources"]
    assert param.default is None, (
        f"sources must default to None for backward compat; got {param.default!r}"
    )
