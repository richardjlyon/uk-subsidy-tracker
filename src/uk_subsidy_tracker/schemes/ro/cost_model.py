"""RO cost model — skeleton shell (Plan 05-05 Task 1).

Full implementation lands in Plan 05-05 Task 2. This file exists so
``schemes/ro/__init__.py`` can import ``build_station_month`` without
``ImportError`` at module load time (Task 1's §6.1 conformance verify
relies on the top-level ``from ...cost_model import build_station_month``
succeeding).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_station_month(output_dir: Path) -> pd.DataFrame:
    """Placeholder — real implementation lands in Plan 05-05 Task 2."""
    raise NotImplementedError(
        "schemes.ro.cost_model.build_station_month not yet implemented "
        "— pending Plan 05-05 Task 2."
    )
