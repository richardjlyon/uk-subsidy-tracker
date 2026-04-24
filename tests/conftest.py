"""Pytest configuration — shared marks + fixtures (Phase 05.2).

Introduced to support the ``@pytest.mark.dormant`` registration + auto-skip
hook for Phase 05.2 station-level RO tests (D-06). On backlog 999.1
activation (credentialed RER access), this hook is deleted and the
station-level tests re-activate unchanged.

Behaviour:
  - ``pytest_configure`` registers the ``dormant`` marker so
    ``pytest --strict-markers`` does not trip.
  - ``pytest_collection_modifyitems`` walks every collected test and
    auto-skips any test carrying ``@pytest.mark.dormant`` with the
    standardised reason ``"dormant per Phase 05.2; un-skip on backlog 999.1"``.

Re-activation discipline (backlog 999.1): delete the
``pytest_collection_modifyitems`` body OR delete the ``@pytest.mark.dormant``
decorators on individual tests; either path re-enables the dormant tests
without touching their bodies.
"""
from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom marks so ``pytest --strict-markers`` does not trip."""
    config.addinivalue_line(
        "markers",
        "dormant: tests for code paths currently dormant per Phase 05.2; "
        "auto-skipped with reason 'dormant per Phase 05.2; un-skip on backlog 999.1'",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Auto-skip every test carrying @pytest.mark.dormant with a standardised reason."""
    skip_marker = pytest.mark.skip(
        reason="dormant per Phase 05.2; un-skip on backlog 999.1"
    )
    for item in items:
        if "dormant" in item.keywords:
            item.add_marker(skip_marker)
