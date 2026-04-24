"""Verify the @pytest.mark.dormant auto-skip hook registered in conftest.py (D-06).

Two tests:
  1. A `@pytest.mark.dormant`-marked test MUST be auto-skipped — if the body runs,
     the conftest.py hook is broken and we fail loud.
  2. A non-marked sanity-check test runs normally.

Re-activation on backlog 999.1: deleting the
``pytest_collection_modifyitems`` body in ``tests/conftest.py`` re-enables
this file's first test (it then fails the ``pytest.fail`` line, which is the
intended signal that the hook needs replacing with explicit decorator
removal — a planner-discretion call at 999.1 activation time).
"""
import pytest


@pytest.mark.dormant
def test_dormant_hook_auto_skips_this():
    """This test MUST be auto-skipped — if it runs, the hook is broken."""
    pytest.fail("dormant hook did NOT auto-skip this test — conftest.py is broken")


def test_non_dormant_test_runs_normally():
    """Sanity check: an un-marked test still runs."""
    assert True
