# UK Renewable Subsidy Tracker

An independent, open, data-driven audit of UK renewable electricity
subsidy costs — every scheme, every pound, every counterfactual,
every methodology exposed — published as a permanent national resource.

Currently a single-scheme prototype covering only Contracts for
Difference (CfD); expanding to an eight-scheme portal covering CfD, RO,
FiT, SEG, Constraint Payments, Capacity Market, Balancing Services, and
Grid Socialisation.

## Documentation

Full site: https://richardjlyon.github.io/uk-subsidy-tracker/

- [Architecture](ARCHITECTURE.md) — single source of truth design document
- [RO Module Spec](RO-MODULE-SPEC.md) — per-scheme module template
- [Changelog](CHANGES.md) — release history
- [Citation](CITATION.cff) — academic citation metadata

## Reproducing

```bash
git clone https://github.com/richardjlyon/uk-subsidy-tracker
cd uk-subsidy-tracker
uv sync
uv run python -m uk_subsidy_tracker.plotting    # regenerate all charts
uv run mkdocs serve                              # serve docs locally
```

## Core value

Every headline number on the site is reproducible from a single
`git clone` + `uv sync` + one command, backed by a methodology page,
traceable to a primary regulator source, and survives hostile reading.

## Corrections and contributions

Welcome via [GitHub Issues](https://github.com/richardjlyon/uk-subsidy-tracker/issues).
See [docs/about/corrections.md](docs/about/corrections.md) for the
corrections log.

## Licence

<!-- Licence text finalised in Task 5 after user confirms OSI licence choice. -->
