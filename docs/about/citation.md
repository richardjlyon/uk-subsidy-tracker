# Citation

How to cite this dataset in academic, policy, and journalistic work.

## Machine-readable citation

The canonical citation metadata lives in
[`CITATION.cff`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/CITATION.cff)
at the repository root, in the [Citation File Format 1.2.0](https://citation-file-format.github.io/).
GitHub, Zenodo, and citation management tools (Zotero, Mendeley) read this
file directly.

## Current version

- **Version:** 0.1.0
- **Released:** 2026-04-21
- **Repository:** [github.com/richardjlyon/uk-subsidy-tracker](https://github.com/richardjlyon/uk-subsidy-tracker)

## Versioned snapshots

Versioned snapshot URLs (for citing the specific state of the data at a
point in time) are produced on every tagged release via the publishing
layer. Release assets live at GitHub's retention-guaranteed storage —
they survive repo renames, custom-domain migrations, and GitHub's own
URL-format changes.

## Citing a specific data snapshot

Every tagged release produces an immutable snapshot of the published
datasets — the URLs listed in `manifest.json::versioned_url` resolve to
GitHub release assets with retention guarantees.

To cite the **data** (e.g. in an academic paper where the specific
snapshot matters more than the code state that produced it):

```bibtex
@misc{uk_subsidy_tracker_v2026_04,
  author       = {Lyon, Richard},
  title        = {UK Renewable Subsidy Tracker — {{v2026.04}} data snapshot},
  year         = {2026},
  url          = {https://github.com/richardjlyon/uk-subsidy-tracker/releases/tag/v2026.04},
  note         = {See manifest.json for per-dataset SHA-256 checksums and upstream provenance.}
}
```

The manifest for any tagged release is always at:

```
https://github.com/richardjlyon/uk-subsidy-tracker/releases/download/v<YYYY.MM>/manifest.json
```

Pattern: always tag-name; never `main` or `latest/`. See
[`data/index.md`](../data/index.md) for full reader-side documentation
— pandas, DuckDB, and R snippets, plus the SHA-256 integrity
verification workflow.
