---
phase: 04-publishing-layer
plan: 06
type: execute
wave: 6
depends_on:
  - 01
  - 02
  - 03
  - 04
  - 05
# NOTE: Plan 06 is Wave 6 (after Plan 05 Wave 5) because both plans write to
# CHANGES.md; serialising the edits avoids merge conflict. Plan 06 also
# consolidates Plans 01-05 CHANGES.md entries in its Task 4 review.
files_modified:
  - docs/data/index.md
  - docs/data/.pages            # optional — enables custom nav tile within `Data` section if used
  - docs/index.md
  - docs/about/citation.md
  - mkdocs.yml
  - tests/fixtures/benchmarks.yaml
  - CHANGES.md
autonomous: false
requirements:
  - PUB-04
  - PUB-06
  - GOV-06
  - TEST-04
tags: [docs, benchmarks, citation, journalism, lccc-floor]
user_setup: []

must_haves:
  truths:
    - "docs/data/index.md exists, linked from docs/index.md, and surfaces as a top-level 'Data' nav tab on the rendered site"
    - "docs/data/index.md contains working pandas, DuckDB, and R snippets that an external consumer can copy-paste to fetch a dataset via manifest.json"
    - "docs/about/citation.md references the versioned-snapshot URL pattern (GOV-06)"
    - "tests/fixtures/benchmarks.yaml::lccc_self has at least one entry (activated the D-10 floor) OR the attempt is documented and the fallback posture (lccc_self: []) is explicitly re-confirmed with a new fallback-reason line citing the ARA PDF page consulted"
    - "mkdocs build --strict is green with the new nav entry"
  artifacts:
    - path: "docs/data/index.md"
      provides: "6-section how-to-use-our-data page: What we publish / How to use it / How to cite it / Provenance guarantees / Known caveats / Corrections + updates"
      contains: "manifest.json"
      min_lines: 120
    - path: "docs/about/citation.md"
      provides: "Updated to document versioned-snapshot URL pattern for academic citation"
      contains: "releases/download"
    - path: "mkdocs.yml"
      provides: "Top-level nav entry 'Data: data/index.md'"
      contains: "data/index.md"
    - path: "docs/index.md"
      provides: "'For journalists and academics → Use our data' link pointing at docs/data/index.md"
      contains: "data/"
    - path: "tests/fixtures/benchmarks.yaml"
      provides: "lccc_self activated (one+ entry) OR fallback re-confirmed with ARA PDF-page citation in notes"
      contains: "lccc_self"
  key_links:
    - from: "docs/data/index.md"
      to: "docs/methodology/gas-counterfactual.md"
      via: "Internal MkDocs link: [gas counterfactual methodology](../methodology/gas-counterfactual.md)"
      pattern: "methodology/gas-counterfactual"
    - from: "docs/data/index.md"
      to: "docs/about/corrections.md"
      via: "Internal link — 'Corrections and updates' section"
      pattern: "about/corrections"
    - from: "docs/data/index.md"
      to: "CITATION.cff"
      via: "Copy-pasteable BibTeX / APA template referencing the citation fields"
      pattern: "CITATION"
    - from: "docs/index.md"
      to: "docs/data/index.md"
      via: "Homepage link text: 'For journalists and academics → Use our data'"
      pattern: "data/"
    - from: "mkdocs.yml"
      to: "docs/data/index.md"
      via: "nav: entry 'Data: data/index.md'"
      pattern: "Data:.*data/index.md"
    - from: "tests/fixtures/benchmarks.yaml::lccc_self"
      to: "tests/test_benchmarks.py::test_lccc_self_reconciliation_floor"
      via: "YAML loader → test parametrises over entries; empty list triggers D-11 fallback skip"
      pattern: "lccc_self"
---

<objective>
Ship the journalist/academic-facing documentation page that makes the data
layer discoverable and citable, link it into site navigation, and close
the D-10 mandatory LCCC benchmark floor — either by transcribing the
ARA 2024/25 calendar-year CfD aggregate into `benchmarks.yaml::lccc_self`,
or by explicitly re-confirming the D-11 fallback posture with a cited PDF
reference.

Purpose: PUB-04 (how-to-use-our-data page), PUB-06 (external-consumer
fetch pattern documented), GOV-06 (citation pattern established),
TEST-04 (LCCC floor activated or fallback re-justified with primary-source
audit evidence).

Structure: standalone plan parallelisable with Plan 05 (workflows) — no
file overlap. Includes a final `checkpoint:human-verify` task because
the LCCC ARA 2024/25 PDF transcription requires human judgement on
financial-year vs calendar-year reconciliation (RESEARCH Pitfall 7).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/04-publishing-layer/04-CONTEXT.md
@.planning/phases/04-publishing-layer/04-RESEARCH.md
@.planning/phases/04-publishing-layer/04-PATTERNS.md
@.planning/phases/04-04-SUMMARY.md
@mkdocs.yml
@docs/index.md
@docs/about/citation.md
@docs/methodology/gas-counterfactual.md
@tests/fixtures/benchmarks.yaml
@tests/test_benchmarks.py
@CITATION.cff

<interfaces>
<!-- D-27 audience + six-section table of contents (verbatim) -->

1. **What we publish** — Parquet canonical, CSV mirror, schema.json, manifest.json. What each is for.
2. **How to use it** — Copy-pasteable snippets for pandas, DuckDB, and R, fetching the latest manifest and reading one table.
3. **How to cite it** — Template referencing `CITATION.cff` + a versioned-snapshot URL. Example BibTeX / APA.
4. **Provenance guarantees** — SHA-256 checksums, retrieval timestamps, pipeline git SHA, methodology version. Link to `CHANGES.md`.
5. **Known caveats and divergences** — Link to `test_benchmarks.py` reconciliation table.
6. **Corrections and updates** — Link to `docs/about/corrections.md` + the `correction` GitHub Issues label.

<!-- Pandas / DuckDB / R snippets — RESEARCH Code Examples section -->

```python
# pandas snippet (RESEARCH lines 1367-1393)
import pandas as pd
import requests
MANIFEST = "https://richardjlyon.github.io/uk-subsidy-tracker/data/manifest.json"
manifest = requests.get(MANIFEST).json()
station_month = next(d for d in manifest["datasets"] if d["id"] == "cfd.station_month")
df = pd.read_parquet(station_month["parquet_url"])
```

```sql
-- DuckDB snippet (RESEARCH lines 1396-1411)
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

```r
# R snippet (new — mirror pandas pattern)
library(arrow)
library(httr)
library(jsonlite)

manifest <- fromJSON(content(GET("https://richardjlyon.github.io/uk-subsidy-tracker/data/manifest.json"), as="text"))
station_month <- manifest$datasets[manifest$datasets$id == "cfd.station_month", ]
df <- read_parquet(station_month$parquet_url)
```

<!-- Integrity check snippet (RESEARCH lines 1385-1393) -->

```python
# Verify SHA-256 against manifest
import hashlib, urllib.request
with urllib.request.urlopen(station_month["parquet_url"]) as resp:
    published_sha = hashlib.sha256(resp.read()).hexdigest()
assert published_sha == station_month["sha256"]
```

<!-- LCCC ARA 2024/25 transcription guidance -->

Primary source URL: `https://www.lowcarboncontracts.uk/documents/293/LCCC_ARA_24-25_11.pdf`
Secondary reporting cites ~£2.4bn calendar-year 2024 (rounded). Pitfall 7:
report is FINANCIAL-YEAR (Apr 2024 – Mar 2025); calendar-year reconstruction
requires the quarterly table. If quarterly breakdown absent from the PDF,
the D-11 fallback (`lccc_self: []`) is the correct posture — a wrong floor
is worse than no floor per Phase 2 D-10.

<!-- mkdocs.yml nav shape — read current nav block, APPEND "Data" tab -->

Currently the nav (per STATE.md "22-entry 5-theme D-04 tree") ends with the
five-theme Cost/Recipients/Efficiency/Cannibalisation/Reliability tabs +
About section. Add a top-level `Data:` entry between theme tabs and About:

```yaml
# Current (conceptual) nav:
nav:
  - Home: index.md
  - Cost: themes/cost/...
  - Recipients: themes/recipients/...
  - Efficiency: themes/efficiency/...
  - Cannibalisation: themes/cannibalisation/...
  - Reliability: themes/reliability/...
  - About: about/...

# After this plan:
nav:
  - Home: index.md
  - Cost: themes/cost/...
  - ...
  - Data: data/index.md       # NEW — top-level tab
  - About: about/...
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Author docs/data/index.md (6 sections per D-27)</name>
  <files>docs/data/index.md</files>
  <read_first>
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-27 (audience + six sections)
    - .planning/phases/04-publishing-layer/04-RESEARCH.md §Code Examples lines 1325-1411 (verified pandas + DuckDB + integrity snippets)
    - docs/methodology/gas-counterfactual.md (linking target from "What we publish" section)
    - docs/about/corrections.md (linking target from "Corrections and updates" section)
    - CITATION.cff (reference fields — authors, repository, version)
    - CHANGES.md (linking target from "Provenance guarantees")
    - .planning/phases/03-chart-triage-execution/03-CONTEXT.md D-01 section pattern (6-section skeleton already established for chart pages — mirror tone)
  </read_first>
  <action>
    Create `docs/data/index.md` with six sections matching D-27 verbatim.
    Target length 150-200 lines.

    ### Front matter + intro

    ```markdown
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
    ```

    ### Section 2: How to use it

    Three subsections — one each for pandas, DuckDB, R. Use the snippets from
    the interface block verbatim. Add a short note at the top of each:

    ```markdown
    ## How to use it

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

    manifest <- fromJSON(content(GET("https://richardjlyon.github.io/uk-subsidy-tracker/data/manifest.json"), as="text"))
    station_month <- manifest$datasets[manifest$datasets$id == "cfd.station_month", ]
    df <- read_parquet(station_month$parquet_url)
    ```
    ```

    ### Section 3: How to cite it

    ```markdown
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

    For citing the **code** (not the data snapshot), see [CITATION.cff](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/CITATION.cff) in the repository root. `citation.cff` follows the [Citation File Format 1.2.0](https://citation-file-format.github.io/) specification.
    ```

    ### Section 4: Provenance guarantees

    ```markdown
    ## Provenance guarantees

    Every published dataset carries:

    - **Source URL** — the upstream regulator's published endpoint (LCCC, Ofgem, ONS, Elexon, NESO, EMR). Stamped in `manifest.datasets[].sources[].upstream_url`.
    - **Retrieval timestamp** — ISO-8601 UTC, when our pipeline fetched the raw file. `manifest.datasets[].sources[].retrieved_at`.
    - **Source SHA-256** — lowercase hex of the raw file. `manifest.datasets[].sources[].source_sha256`. Re-computes on every refresh; drift triggers a rebuild.
    - **Pipeline git SHA** — the exact commit of this repository that produced the snapshot. `manifest.pipeline_git_sha`.
    - **Methodology version** — the gas counterfactual formula tag. `manifest.methodology_version` top-level + per-row `methodology_version` column on every Parquet table. Any change to the formula bumps this version and is logged in [`CHANGES.md` under `## Methodology versions`](../CHANGES.md).

    This is the reproducibility contract: from any published version snapshot, plus our repo's state at `pipeline_git_sha`, plus the raw files at their source URLs, you can rebuild every figure byte-identical (modulo Parquet file-level metadata per [TEST-05](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_determinism.py)).
    ```

    ### Section 5: Known caveats and divergences

    ```markdown
    ## Known caveats and divergences

    We reconcile our aggregates against the regulator's own published totals and, where available, against third-party compilations. Full reconciliation lives in [`tests/test_benchmarks.py`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/tests/test_benchmarks.py).

    The mandatory floor is LCCC self-reconciliation — our pipeline reads LCCC raw data, so a divergence there is a pipeline bug, not a methodology divergence. External anchors (OBR EFO, DESNZ, HoC Library, NAO) are folded as regulator-native figures become transcribable; their tolerances are larger (2-15%) because they aggregate over different scheme subsets, price bases (nominal vs real), or accounting horizons (fiscal vs calendar year).

    See [`CHANGES.md`](../CHANGES.md) for every methodology change and its rationale.

    The gas counterfactual methodology — the most consequential choice in this project — is fully documented at [`docs/methodology/gas-counterfactual.md`](../methodology/gas-counterfactual.md).
    ```

    ### Section 6: Corrections and updates

    ```markdown
    ## Corrections and updates

    Found a discrepancy? [Open an issue](https://github.com/richardjlyon/uk-subsidy-tracker/issues/new) with the `correction` label. Published corrections are tracked at [`docs/about/corrections.md`](../about/corrections.md) with date, reason, and affected charts.

    Daily refreshes happen at 06:00 UTC via a GitHub Actions cron; each creates a PR with the diff — so the audit trail of every data change is visible in git history. Automation failures open issues labelled `refresh-failure` (distinct from `correction`).

    Code contributions: see [`README.md`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/README.md) for the development workflow. All changes land through PRs reviewed against the adversarial-proofing quality bar (narrative + methodology + test + source-file link per [GOV-01](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/.planning/REQUIREMENTS.md#gov-01)).
    ```

    ### Final check

    ```bash
    uv run mkdocs build --strict
    # Expect: no broken links, no nav warnings (the mkdocs.yml nav update is Task 2)
    ```
    Note: `mkdocs build --strict` may warn about `data/index.md` not being in
    the nav until Task 2 wires it in. Run the strict build AFTER Task 2 completes.
  </action>
  <verify>
    <automated>test -f docs/data/index.md &amp;&amp; grep -q "## What we publish" docs/data/index.md &amp;&amp; grep -q "## How to use it" docs/data/index.md &amp;&amp; grep -q "## How to cite it" docs/data/index.md &amp;&amp; grep -q "## Provenance guarantees" docs/data/index.md &amp;&amp; grep -q "## Known caveats" docs/data/index.md &amp;&amp; grep -q "## Corrections and updates" docs/data/index.md</automated>
  </verify>
  <acceptance_criteria>
    - `test -f docs/data/index.md` exits 0
    - `wc -l docs/data/index.md` reports ≥ 120
    - All six D-27 sections present: `grep -cE "^## (What we publish|How to use it|How to cite it|Provenance guarantees|Known caveats|Corrections and updates)" docs/data/index.md` returns 6
    - pandas snippet: `grep -q "pd.read_parquet" docs/data/index.md` AND `grep -q "station_month\[.sha256.\]" docs/data/index.md || grep -q "hashlib.sha256" docs/data/index.md`
    - DuckDB snippet: `grep -q "INSTALL httpfs" docs/data/index.md` AND `grep -q "read_parquet" docs/data/index.md`
    - R snippet: `grep -q "library(arrow)" docs/data/index.md` AND `grep -q "read_parquet" docs/data/index.md`
    - BibTeX reference: `grep -q "@misc{" docs/data/index.md`
    - APA-style reference present: `grep -q "\[Data set\]" docs/data/index.md` OR `grep -q "APA:" docs/data/index.md`
    - Cross-links to methodology: `grep -q "methodology/gas-counterfactual" docs/data/index.md`
    - Cross-links to corrections: `grep -q "about/corrections" docs/data/index.md`
    - Cross-links to CHANGES.md: `grep -q "CHANGES.md" docs/data/index.md`
    - References to manifest.json absolute URLs: `grep -c "manifest.json" docs/data/index.md` ≥ 3
    - References to SHA-256: `grep -q "SHA-256\|sha256" docs/data/index.md`
    - References to pipeline_git_sha: `grep -q "pipeline_git_sha" docs/data/index.md`
    - References to methodology_version: `grep -q "methodology_version" docs/data/index.md`
  </acceptance_criteria>
  <done>docs/data/index.md lives at 120+ lines with all six D-27 sections, three working language snippets, BibTeX + APA citation templates, and full cross-links to methodology + corrections + CHANGES.md.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Wire nav — mkdocs.yml + docs/index.md homepage link + docs/about/citation.md update</name>
  <files>mkdocs.yml, docs/index.md, docs/about/citation.md</files>
  <read_first>
    - mkdocs.yml (current nav: block — add "Data" entry before About)
    - docs/index.md (current homepage — add "For journalists and academics → Use our data" link)
    - docs/about/citation.md (current citation page — update to reference versioned-snapshot URL pattern)
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-09 (absolute URLs — relevant to citation update), D-27 (audience)
  </read_first>
  <action>
    ### Step 2A — mkdocs.yml: add "Data" nav entry

    Find the `nav:` block. Insert a top-level `- Data: data/index.md` entry
    between the theme tabs (Cost / Recipients / Efficiency / Cannibalisation
    / Reliability) and the About section. Example insertion:

    ```yaml
    # BEFORE (simplified):
    nav:
      - Home: index.md
      - Cost: themes/cost/index.md
      - ... (other themes)
      - About: about/index.md

    # AFTER:
    nav:
      - Home: index.md
      - Cost: themes/cost/index.md
      - ... (other themes)
      - Data: data/index.md      # NEW — single top-level page; promote to section if future subpages land
      - About: about/index.md
    ```

    DO NOT reorder existing entries. Simply insert the Data line in the
    correct slot. Preserve indentation.

    ### Step 2B — docs/index.md homepage link

    Find the appropriate section (likely the existing "Explore by theme" or
    "For readers" section). APPEND — not replace — a new bullet:

    ```markdown
    ## For journalists and academics

    [**Use our data**](data/index.md) — pandas, DuckDB, and R snippets + citation templates + SHA-256 integrity verification. Start at [`manifest.json`](https://richardjlyon.github.io/uk-subsidy-tracker/data/manifest.json) and follow the URLs.
    ```

    If a "For journalists" section already exists (from a prior plan), EXTEND
    rather than duplicate. Keep the existing text; add the **Use our data**
    link and brief description.

    ### Step 2C — docs/about/citation.md update

    Read the current citation.md. It should reference CITATION.cff but may
    not yet describe the versioned-snapshot URL pattern. Append a section:

    ```markdown
    ## Citing a specific data snapshot

    Every tagged release produces an immutable snapshot of the published datasets — the URLs listed in `manifest.json::versioned_url` resolve to GitHub release assets with retention guarantees.

    To cite the **data** (e.g. in an academic paper where the specific snapshot matters more than the code state that produced it):

    ```bibtex
    @misc{uk_subsidy_tracker_v2026_04,
      author       = {Lyon, Richard},
      title        = {UK Renewable Subsidy Tracker — {{v2026.04}} data snapshot},
      year         = {2026},
      url          = {https://github.com/richardjlyon/uk-subsidy-tracker/releases/tag/v2026.04},
      note         = {See manifest.json for per-dataset SHA-256 checksums and upstream provenance.}
    }
    ```

    Pattern: always tag-name; never `main` or `latest/`. See [`docs/data/index.md`](../data/index.md) for full reader-side documentation.
    ```

    If docs/about/citation.md does not yet exist, create it based on this
    template and the pre-existing CITATION.cff — check git log for the
    Phase-1 citation page authorship.

    ### Step 2D — Verify strict build

    ```bash
    uv run mkdocs build --strict
    ```

    Expected: 0 warnings, 0 errors. If the build flags the new `Data` nav
    as omitting subpages, that's acceptable — it's a single page, not a
    section. Adjust `docs/data/.pages` (mkdocs-material `awesome-pages`
    plugin) only if the plugin is active in the repo — check
    `mkdocs.yml::plugins` first.
  </action>
  <verify>
    <automated>grep -q "Data: data/index.md" mkdocs.yml &amp;&amp; grep -q "data/" docs/index.md &amp;&amp; grep -q "releases/tag\|releases/download" docs/about/citation.md &amp;&amp; uv run mkdocs build --strict</automated>
  </verify>
  <acceptance_criteria>
    - `grep -qE "^\s+- Data:\s+data/index.md" mkdocs.yml` exits 0
    - Homepage link added: `grep -q "data/index.md\|Use our data" docs/index.md` exits 0
    - `test -f docs/about/citation.md` exits 0
    - Versioned-snapshot pattern in citation.md: `grep -q "releases/tag\|releases/download" docs/about/citation.md`
    - `grep -q "manifest.json\|versioned_url" docs/about/citation.md`
    - `uv run mkdocs build --strict` exits 0 (zero warnings, zero errors)
    - Rendered nav tab appears (manual or via grep on site/ output): `grep -q "Data" site/data/index.html || grep -q 'nav.*Data' site/index.html` OR simply confirm `--strict` build passes since it would have warned about an orphan nav entry
    - `uv run pytest tests/` still green (no test regressions from doc changes)
  </acceptance_criteria>
  <done>Top-level "Data" nav tab active; homepage links to `data/index.md`; citation page documents the versioned-snapshot URL pattern; mkdocs-strict build is green.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 3 (checkpoint): Transcribe LCCC ARA 2024/25 calendar-year CfD aggregate OR re-confirm D-11 fallback</name>
  <files>tests/fixtures/benchmarks.yaml</files>
  <action>
    This is a CHECKPOINT: the executor pauses here and requires a human
    decision + human action before proceeding. The executor does NOT attempt
    to transcribe the PDF autonomously — human judgement is required on the
    FY-vs-CY reconciliation (RESEARCH Pitfall 7). See `<what-built>`,
    `<how-to-verify>`, and `<resume-signal>` blocks below for the full
    procedure. The executor's role is to:

    1. Present the checkpoint to the user (including the three-disposition
       decision matrix).
    2. Wait for the resume-signal reply naming Disposition A, B, or C.
    3. Apply the YAML edit matching the chosen disposition.
    4. Run the verify command to confirm the test suite still passes.
    5. Only then proceed to Task 4 (CHANGES.md consolidation).
  </action>
  <verify>
    <automated>uv run pytest tests/test_benchmarks.py -v &amp;&amp; uv run pytest tests/ -x</automated>
  </verify>
  <done>User has replied with a disposition (A / B / C); benchmarks.yaml matches that disposition; test_benchmarks.py either passes the activated lccc_self floor or skips cleanly with a D-11-citing reason string; full test suite green.</done>
  <what-built>
    Plans 01-04 and Tasks 1-2 above have delivered the full publishing layer.
    The final Phase-4 closure item is the D-10 mandatory LCCC self-
    reconciliation floor — Phase 2 shipped the D-11 fallback (`lccc_self: []`)
    because the LCCC ARA 2024/25 figure had not yet been transcribed from the
    primary-source PDF. Phase 4's CONTEXT D-26 calls for activating the floor
    if the PDF supports a clean calendar-year transcription.

    RESEARCH Pitfall 7 flags the FY-vs-CY reconciliation as the potential
    blocker: UK gov reports default to financial years, and the 0.1% floor
    tolerance cannot hold against a rounded secondary-source figure like
    the Watts Up With That £2.4bn.

    This checkpoint requires a human to:
    1. Download the PDF (`https://www.lowcarboncontracts.uk/documents/293/LCCC_ARA_24-25_11.pdf`).
    2. Locate the per-quarter CfD payments table.
    3. Decide one of three dispositions (see how-to-verify).
    4. Implement the chosen disposition.
  </what-built>
  <how-to-verify>
    ### Step A — Download and review the PDF

    ```bash
    curl -L -o /tmp/LCCC_ARA_24-25_11.pdf \
         https://www.lowcarboncontracts.uk/documents/293/LCCC_ARA_24-25_11.pdf
    open /tmp/LCCC_ARA_24-25_11.pdf   # or your preferred PDF reader
    ```

    ### Step B — Locate CfD payments breakdown

    Look for:
    - A table showing CfD payments by quarter (Q1 2024 through Q4 2024 or Q4 24/25).
    - Any table that decomposes the annual FY aggregate into calendar-year sums.
    - The "Actual CfD Generation" or "CfD Settlement" dataset summary.

    If the PDF only reports FY aggregates (April 2024 – March 2025) with no
    quarterly breakdown, proceed to Disposition C.

    ### Step C — Choose a disposition

    **Disposition A: Clean CY 2024 transcription**

    If the PDF reports quarterly CfD payments and Q1+Q2+Q3+Q4 2024 sums
    cleanly to a 4-significant-figure value: add an entry to
    `tests/fixtures/benchmarks.yaml::lccc_self`. Example shape:

    ```yaml
    lccc_self:
      - year: 2024
        value_gbp_bn: 2.387   # ACTUAL value from the PDF, 4 sig figs
        url: "https://www.lowcarboncontracts.uk/documents/293/LCCC_ARA_24-25_11.pdf"
        retrieved_on: 2026-04-22
        notes: "Transcribed from LCCC ARA 2024/25 Table X (p. Y): sum of Q1+Q2+Q3+Q4 2024 CfD payments. Calendar-year reconstructed from per-quarter figures; matches 'Actual CfD Generation' LCCC data portal aggregate to within pipeline-computation precision."
        tolerance_pct: 0.1
    ```

    Run the test to confirm the floor holds:

    ```bash
    uv run pytest tests/test_benchmarks.py::test_lccc_self_reconciliation_floor -v
    ```

    If it fails with a >0.1% divergence, the transcription rounding is too
    aggressive OR the pipeline has a bug. Investigate — do NOT weaken the
    tolerance.

    **Disposition B: Fiscal-year-only transcription**

    If the PDF only gives FY 2024/25, and no quarterly breakdown: DO NOT
    populate `lccc_self` at 0.1% tolerance (Pitfall 7 — tolerance mismatch
    would fail CI daily). Instead, add the entry with notes explicitly
    documenting the FY reporting, and bump the tolerance to 3-5% (documented
    as "FY reporting" per Phase 2 D-06 + D-07):

    ```yaml
    # NOTE: 0.1% floor NOT activated because ARA 2024/25 reports FY only.
    # Follow-up: transcribe from a future LCCC quarterly publication when available.
    lccc_self: []
    ```

    And add a comment line to benchmarks.yaml describing the FY issue
    and the follow-up plan.

    **Disposition C: PDF unavailable / ambiguous**

    Keep the Phase-2 D-11 fallback (`lccc_self: []`). Update the YAML
    header comment block to record the Phase-4 audit attempt:

    ```yaml
    # lccc_self: Phase 2 shipped as D-11 fallback empty. Phase 4 attempted
    # activation per D-26 (2026-04-22) — confirmed ARA 2024/25 PDF
    # accessible at https://www.lowcarboncontracts.uk/documents/293/LCCC_ARA_24-25_11.pdf
    # but only reports FY 2024/25 aggregate (no quarterly breakdown).
    # Follow-up: transcribe from a future LCCC CY publication (Watts Up
    # With That cited £2.4bn CY 2024 — secondary source not adequate for
    # 0.1% floor tolerance per Pitfall 7).
    lccc_self: []
    ```

    ### Step D — Update CHANGES.md in either case

    Under `### Changed`:

    ```markdown
    - `tests/fixtures/benchmarks.yaml::lccc_self` reviewed per D-26. {Choose one:
      (A) Activated with LCCC ARA 2024/25 Q1-Q4 2024 calendar-year aggregate of £X.XXX bn, 0.1% tolerance per D-10.
      (B) FY-only posture — entry present with elevated tolerance documenting the FY-vs-CY reconciliation limitation.
      (C) D-11 fallback re-confirmed — PDF audit complete; follow-up todo carried forward for CY publication.}
    ```

    ### Step E — Run full test suite

    ```bash
    uv run pytest tests/ -v
    ```

    Expected: all tests green. If `test_lccc_self_reconciliation_floor`
    runs (Disposition A) and fails, the chosen value has a precision
    mismatch — review the transcription.

    ### Step F — Document the disposition chosen

    Reply in the checkpoint resume message with ONE of:
    - "Disposition A — activated lccc_self with £X.XXX bn CY 2024 at 0.1% tolerance, PDF p. Y. All tests green."
    - "Disposition B — lccc_self activated with FY data at Z% tolerance; 0.1% floor posture deferred."
    - "Disposition C — D-11 fallback re-confirmed; PDF reviewed and found to report FY only. Todo logged for future CY source."
  </how-to-verify>
  <resume-signal>Reply with disposition (A / B / C), the chosen value if applicable, and "approved"</resume-signal>
  <autonomous_fallback>
    If the user does not respond within 24 hours of checkpoint pause, the
    executor MAY proceed autonomously with Disposition C (D-11 fallback
    re-confirmed: keep `tests/fixtures/benchmarks.yaml::lccc_self: []`; the
    `test_lccc_self_reconciliation_floor` test stays skipped per Phase 2
    D-11 posture). This is consistent with CONTEXT.md §Benchmark floor
    activation, which treats the ARA 2024/25 transcription as best-effort
    — a skipped floor is strictly better than a silently-wrong one (Pitfall 7).
    The phase SUMMARY MUST document the auto-selection explicitly (e.g.
    "Disposition C auto-selected after 24h checkpoint timeout on
    2026-MM-DD; user review not received. TODO: revisit when ARA 2024/25
    quarterly primary source is transcribed.") and open a TODO in STATE.md
    tracking the follow-up. Disposition A/B require human PDF reading and
    cannot be auto-selected.
  </autonomous_fallback>
</task>

<task type="auto" tdd="false">
  <name>Task 4: CHANGES.md consolidation + STATE.md todo closure notes</name>
  <files>CHANGES.md</files>
  <read_first>
    - CHANGES.md (current [Unreleased] — Plans 01-05 entries already present; this plan's Tasks 1-2 entries should go under Added/Changed)
    - The disposition chosen in Task 3 (for the LCCC floor line)
  </read_first>
  <action>
    Consolidate all Phase-4 entries under `## [Unreleased]`. Under each
    `### Added` / `### Changed` subsection, ensure the following topics have
    been covered across all plans:

    **Added (consolidated — some from earlier plans, plus Plan 06 additions):**
    - dependencies: pyarrow + duckdb (Plan 01)
    - tests/fixtures/constants.yaml + ConstantProvenance/load_constants (Plan 01)
    - tests/test_constants_provenance.py (Plan 01)
    - scripts/backfill_sidecars.py (Plan 02)
    - .meta.json sidecars (Plan 02)
    - src/uk_subsidy_tracker/schemas/ (Plan 03)
    - src/uk_subsidy_tracker/schemes/ Protocol + cfd/ module (Plan 03)
    - tests/test_determinism.py (Plan 03)
    - Parquet variants in test_schemas.py + test_aggregates.py (Plan 03)
    - src/uk_subsidy_tracker/publish/ (manifest + csv_mirror + snapshot) (Plan 04)
    - src/uk_subsidy_tracker/refresh_all.py (Plan 04)
    - tests/test_manifest.py + tests/test_csv_mirror.py (Plan 04)
    - .github/workflows/refresh.yml + deploy.yml + refresh-failure-template.md (Plan 05)
    - **docs/data/index.md — journalist/academic how-to-use-our-data page (PUB-04)** (Plan 06 Task 1)
    - **mkdocs.yml Data nav tab + docs/index.md homepage link** (Plan 06 Task 2)
    - **docs/about/citation.md versioned-snapshot pattern documentation** (Plan 06 Task 2)

    **Changed (consolidated):**
    - Raw data layout migration (Plan 02)
    - methodology_version column on every derived Parquet row (Plan 03)
    - **tests/fixtures/benchmarks.yaml::lccc_self disposition** (Plan 06 Task 3 — insert text per disposition A/B/C chosen)

    If any Phase-4 topic is MISSING from CHANGES.md at this point, add it.
    The goal is a single coherent `## [Unreleased]` block summarising
    everything Phase 4 delivered, ready to become `## [0.2.0]` on the first
    release tag.

    DO NOT add a `## Methodology versions` entry — `METHODOLOGY_VERSION`
    remains `"0.1.0"` per pre-existing condition; bump is Phase-6-or-later.
  </action>
  <verify>
    <automated>grep -q "docs/data/index.md" CHANGES.md &amp;&amp; grep -q "lccc_self" CHANGES.md &amp;&amp; grep -q "PUB-04" CHANGES.md &amp;&amp; uv run mkdocs build --strict</automated>
  </verify>
  <acceptance_criteria>
    - `grep -q "docs/data/index.md\|Use our data" CHANGES.md` exits 0
    - `grep -q "lccc_self\|LCCC ARA" CHANGES.md` exits 0
    - `grep -q "versioned-snapshot\|versioned_url\|releases/tag" CHANGES.md` exits 0
    - Phase-4 req IDs represented: at least 4 of {PUB-01, PUB-02, PUB-03, PUB-04, PUB-05, PUB-06, GOV-02, GOV-03, GOV-06, TEST-02, TEST-03, TEST-05} appear in the CHANGES.md [Unreleased] section: `grep -cE 'PUB-0[1-6]|GOV-0[236]|TEST-0[235]' CHANGES.md` ≥ 4
    - `uv run mkdocs build --strict` exits 0
    - METHODOLOGY_VERSION unchanged: `grep -q 'METHODOLOGY_VERSION: str = "0.1.0"' src/uk_subsidy_tracker/counterfactual.py`
    - No new `## Methodology versions` entry: `git diff HEAD~1 CHANGES.md -- | grep -c "^+## Methodology versions"` returns 0 (no +-prefixed additions of that header)
  </acceptance_criteria>
  <done>CHANGES.md [Unreleased] section consolidates every Phase-4 artefact + the LCCC floor disposition. Ready for release tagging in Phase 5+ when METHODOLOGY_VERSION bumps to 1.0.0.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| docs/data/index.md snippets → external consumer's local machine | Copy-paste snippets execute in journalists'/academics' own Python / R / SQL environments. |
| Versioned-snapshot URL pattern (`github.com/.../releases/tag/v2026.04`) → academic citation database | A mis-documented URL pattern propagates into papers and breaks years later. |
| LCCC ARA 2024/25 PDF transcription → benchmarks.yaml | Human transcription is an attack surface for typo/mis-read errors that pass through CI. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-04-06-01 | Tampering | Docs snippet contains malicious code (would execute in reader's env) | accept | Project is open source; snippets are visible in the PR diff + rendered on the site. No secret loading; no credential usage. Third-party libraries referenced (pandas, duckdb, arrow) are widely-audited and pinned via their own version conventions on the reader's side. |
| T-04-06-02 | Tampering | A versioned snapshot URL is mis-documented as a `main`-branch reference | mitigate | Task 2C's citation.md text explicitly states "always tag-name; never `main` or `latest/`". BibTeX template uses `releases/tag/v2026.04` as the authoritative citation target. Code review catches `/blob/main/` in citation context. |
| T-04-06-03 | Tampering | LCCC ARA transcription captures wrong digit (e.g. £2.4bn misread as £4.2bn) | mitigate | Checkpoint requires a human review step with PDF page reference. Test_lccc_self_reconciliation_floor at 0.1% tolerance catches any transcription error >0.1% of the pipeline value. If human picks Disposition A and the test fails, the transcription is rejected — no data ships with a silently-wrong floor. |
| T-04-06-04 | Information Disclosure | Homepage link text leaks a planning detail | accept | docs are public; all Phase-4 decisions are documented in the repo `.planning/` tree. |
| T-04-06-05 | Denial of Service | mkdocs-strict fails on the new nav entry, blocking docs-build CI | mitigate | Task 2 verification includes `uv run mkdocs build --strict`. Phase 3 already demonstrated strict-green with 22 nav entries; 23 is within proven capacity. |
</threat_model>

<verification>
Phase-4 Plan 06 verifications:

1. `uv run mkdocs build --strict` — green (nav + new page render)
2. `uv run pytest tests/` — green (test_benchmarks may skip or pass depending on Task 3 disposition)
3. `grep -q "data/index.md" mkdocs.yml && grep -q "data/" docs/index.md` — nav + homepage wiring in place
4. Section 6 D-27 check: six sections present in docs/data/index.md (counted via grep)
5. Citation page has versioned-snapshot URL pattern: `grep -q "releases/tag" docs/about/citation.md`
6. LCCC floor disposition documented: benchmarks.yaml reflects choice A/B/C
7. CHANGES.md consolidated: all Phase-4 req IDs mentioned

Manual (post-merge, Phase 4 exit checkpoint):
- Navigate to rendered site; confirm "Data" tab appears in top nav; confirm pandas snippet renders with syntax highlighting.
- Copy the pandas snippet to a scratch Python file; run against the live manifest.json URL; confirm a valid DataFrame is returned.
</verification>

<success_criteria>
- `docs/data/index.md` exists with all six D-27 sections and working snippets for pandas + DuckDB + R
- `docs/about/citation.md` references the versioned-snapshot URL pattern (GOV-06)
- `mkdocs.yml` has a "Data" top-level nav tab and `mkdocs build --strict` is green
- `docs/index.md` links to `docs/data/index.md`
- `tests/fixtures/benchmarks.yaml::lccc_self` is either (a) populated with a CY 2024 entry at 0.1% tolerance (D-10 floor green), or (b) explicitly re-confirmed as the D-11 fallback with an updated comment block citing the ARA 2024/25 PDF review
- `uv run pytest tests/` is green; `test_lccc_self_reconciliation_floor` either passes (floor activated) or skips with a D-11-citing reason
- `CHANGES.md` [Unreleased] consolidates every Phase-4 artefact + disposition
</success_criteria>

<output>
After completion, create `.planning/phases/04-publishing-layer/04-06-SUMMARY.md`. Must include:
- Which disposition (A / B / C) was chosen for the LCCC floor
- PDF page reference if Disposition A (transcribed value + page + table label)
- Count of mkdocs nav entries before and after (baseline = 22 per Phase 3; target = 23 after adding Data tab)
- Any broken link that mkdocs-strict surfaced and how it was fixed
- Phase 4 exit checklist progress: 5 ROADMAP success criteria mapped to which plans delivered them
</output>
