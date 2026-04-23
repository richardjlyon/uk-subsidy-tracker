# Use our data

**Every number on this site is reproducible from a single `git clone` and one command.** This page tells you how to fetch, read, cite, and verify the published datasets — whether you are writing a news story, an academic paper, or an adversarial critique.

The stable public contract is **`manifest.json`**. Everything else — the Parquet files, the CSV mirrors, the per-table JSON schemas, the versioned snapshots — is discoverable from that single URL.

## What we publish

Three artefact types, plus one index:

- **Parquet** (`*.parquet`) — the canonical analytical format. Columnar, compressed, self-describing. Read with pandas, polars, DuckDB, Apache Arrow, R (`arrow`), Rust, or any Apache-Parquet consumer. Carries a `methodology_version` column per row tracing every figure back to the counterfactual formula that produced it.
- **CSV mirror** (`*.csv`) — the same data, journalist-friendly. Same column order as the Parquet source, LF line endings, UTF-8 (no BOM), ISO-8601 dates, full float precision. Open in Excel, Numbers, or your terminal of choice.
- **Per-table JSON Schema** (`*.schema.json`) — JSON Schema Draft 2020-12 description of each table's columns, dtypes, units, and nullability. Validate programmatically, or read by eye.
- **Manifest** (`manifest.json`) — the root document. Lists every dataset with its source URL, retrieval timestamp, SHA-256, pipeline git SHA, methodology version, and absolute URLs to the Parquet, CSV, schema, and versioned snapshot.

The full layout lives under `site/data/`:

```
site/data/
  manifest.json                          ← start here
  latest/cfd/
    station_month.parquet
    station_month.csv
    station_month.schema.json
    annual_summary.parquet
    ... (and so on)
```

Versioned snapshots live as **GitHub release assets** (`v<YYYY.MM>` tags). Academic citations always reference the versioned URL — never `latest/`.

## How to use it

Three snippets. Each fetches `manifest.json`, picks one dataset by ID, and reads the Parquet file directly over HTTPS. Copy-paste into your tool of choice.

### Python (pandas)

```python
import pandas as pd
import requests

MANIFEST = "https://richardjlyon.github.io/uk-subsidy-tracker/data/manifest.json"

# 1. Fetch the manifest (small JSON document).
manifest = requests.get(MANIFEST).json()

# 2. Find the dataset you want.
station_month = next(
    d for d in manifest["datasets"]
    if d["id"] == "cfd.station_month"
)

# 3. Read the Parquet directly (pandas delegates to pyarrow).
df = pd.read_parquet(station_month["parquet_url"])

# 4. Verify integrity against the published SHA-256.
import hashlib, urllib.request
with urllib.request.urlopen(station_month["parquet_url"]) as resp:
    published_sha = hashlib.sha256(resp.read()).hexdigest()
assert published_sha == station_month["sha256"]
```

### DuckDB (SQL)

DuckDB reads Parquet over HTTPS natively — no download, no intermediate files.

```sql
INSTALL httpfs;
LOAD httpfs;

SELECT station_id, technology,
       SUM(cfd_payments_gbp) AS lifetime_payments_gbp,
       SUM(cfd_generation_mwh) AS lifetime_generation_mwh
FROM read_parquet('https://richardjlyon.github.io/uk-subsidy-tracker/data/latest/cfd/station_month.parquet')
GROUP BY 1, 2
ORDER BY lifetime_payments_gbp DESC
LIMIT 10;
```

### R (arrow)

```r
library(arrow)
library(httr)
library(jsonlite)

manifest <- fromJSON(content(GET("https://richardjlyon.github.io/uk-subsidy-tracker/data/manifest.json"), as = "text"))
station_month <- manifest$datasets[manifest$datasets$id == "cfd.station_month", ]
df <- read_parquet(station_month$parquet_url)
```

## How to cite it

Every release has an immutable versioned URL — these are durable against repo renames and custom-domain migrations (GitHub's release storage is retention-guaranteed).

**BibTeX:**

```bibtex
@misc{lyon_uk_subsidy_tracker_2026,
  author       = {Lyon, Richard},
  title        = {UK Renewable Subsidy Tracker — {{v2026.04}} snapshot},
  year         = {2026},
  month        = {apr},
  url          = {https://github.com/richardjlyon/uk-subsidy-tracker/releases/tag/v2026.04},
  note         = {Parquet snapshot, retrieved via \url{https://github.com/richardjlyon/uk-subsidy-tracker/releases/download/v2026.04/manifest.json}}
}
```

**APA:**

> Lyon, R. (2026). UK Renewable Subsidy Tracker — v2026.04 snapshot \[Data set\]. https://github.com/richardjlyon/uk-subsidy-tracker/releases/tag/v2026.04

For citing the **code** (not the data snapshot), see [CITATION.cff](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/CITATION.cff) in the repository root. `CITATION.cff` follows the [Citation File Format 1.2.0](https://citation-file-format.github.io/) specification — GitHub, Zenodo, Zotero, and Mendeley read it directly.

Pattern: always tag-name (`v2026.04`); never `main` or `latest/`. The citation page at [`about/citation.md`](../about/citation.md) documents the versioned-snapshot URL pattern in full.

## Provenance guarantees

Every published dataset carries:

- **Source URL** — the upstream regulator's published endpoint (LCCC, Ofgem, ONS, Elexon, NESO, EMR). Stamped in `manifest.datasets[].sources[].upstream_url`.
- **Retrieval timestamp** — ISO-8601 UTC, when our pipeline fetched the raw file. `manifest.datasets[].sources[].retrieved_at`.
- **Source SHA-256** — lowercase hex of the raw file. `manifest.datasets[].sources[].source_sha256`. Re-computed on every refresh; drift triggers a rebuild.
- **Pipeline git SHA** — the exact commit of this repository that produced the snapshot. `manifest.pipeline_git_sha`.
- **Methodology version** — the gas counterfactual formula tag. `manifest.methodology_version` top-level + per-row `methodology_version` column on every Parquet table. Any change to the formula bumps this version and is logged in [`CHANGES.md` under `## Methodology versions`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/CHANGES.md).

This is the reproducibility contract: from any published version snapshot, plus our repo's state at `pipeline_git_sha`, plus the raw files at their source URLs, you can rebuild every figure byte-identical (modulo Parquet file-level metadata per [`tests/test_determinism.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_determinism.py)).

The gas counterfactual methodology — the most consequential choice in this project — is fully documented at [gas counterfactual methodology](../methodology/gas-counterfactual.md).

## Known caveats and divergences

We reconcile our aggregates against the regulator's own published totals and, where available, against third-party compilations. Full reconciliation lives in [`tests/test_benchmarks.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_benchmarks.py).

The mandatory floor is **LCCC self-reconciliation** — our pipeline reads LCCC raw data, so a divergence there is a pipeline bug, not a methodology divergence. External anchors (OBR EFO, DESNZ, HoC Library, NAO) are folded in as regulator-native figures become transcribable; their tolerances are larger (2–15%) because they aggregate over different scheme subsets, price bases (nominal vs real), or accounting horizons (fiscal vs calendar year).

See [`CHANGES.md`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/CHANGES.md) for every methodology change and its rationale.

## Corrections and updates

Found a discrepancy? [Open an issue](https://github.com/richardjlyon/uk-subsidy-tracker/issues/new) with the `correction` label. Published corrections are tracked at [`about/corrections.md`](../about/corrections.md) with date, reason, and affected charts.

Daily refreshes happen at 06:00 UTC via a GitHub Actions cron; each creates a PR with the diff — so the audit trail of every data change is visible in git history. Automation failures open issues labelled `refresh-failure` (distinct from `correction`).

Code contributions: see [`README.md`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/README.md) for the development workflow. All changes land through PRs reviewed against the adversarial-proofing quality bar (narrative page + methodology page + test + source-file link, per the project's GOV-01 four-way coverage rule).
