"""Publishing layer — manifest + CSV mirror + snapshot assembly (Plan 04-04).

Three module-level callables compose the publishing step of the three-layer
pipeline (source → derived → published):

- `manifest.build()` — writes `site/data/manifest.json`, the public contract.
- `csv_mirror.build()` — writes a CSV sibling for every derived Parquet.
- `snapshot.build()` — assembles a versioned-snapshot directory for release
  artifact upload (`deploy.yml` calls this on `git push --tags`).

`refresh_all.py` orchestrates per-scheme refresh + this publishing step.
"""

from uk_subsidy_tracker.publish import csv_mirror, snapshot
from uk_subsidy_tracker.publish.manifest import (
    Dataset,
    Manifest,
    Source,
    build,
)

__all__ = [
    "Manifest", "Dataset", "Source", "build",
    "csv_mirror", "snapshot",
]
