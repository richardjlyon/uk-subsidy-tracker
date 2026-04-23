"""RO forward projection — skeleton shell (Plan 05-05 Task 1).

Full implementation lands in Plan 05-05 Task 3. This file exists so
``schemes/ro/__init__.py`` imports can succeed at module load time
(Task 1's §6.1 conformance verify relies on it).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_forward_projection(output_dir: Path) -> pd.DataFrame:
    """Placeholder — real implementation lands in Plan 05-05 Task 3."""
    raise NotImplementedError(
        "schemes.ro.forward_projection.build_forward_projection not yet implemented "
        "— pending Plan 05-05 Task 3."
    )
