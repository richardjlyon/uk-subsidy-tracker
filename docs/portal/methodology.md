# Cross-scheme methodology

This page documents how Phase 6's cross-scheme aggregation layer joins per-scheme `annual_summary.parquet` outputs into a single canonical table consumed by the five X-charts on the Portal tier. Reproducibility, provenance, and partial-coverage transparency are the constraints. Every number on the X-chart pages is reproducible from `data/derived/portal/cross_scheme.parquet` plus the regulator-sourced raw data committed to this repository.

## Cross-scheme aggregation

The canonical cross-scheme table is `data/derived/portal/cross_scheme.parquet`, in long format with one row per `(year, scheme)` pair. The schema is:

```
year | scheme | cost_gbp | premium_gbp | generation_mwh | households_uk | methodology_version
```

Every X-chart reads from this single file and projects:

- **X1** sums `cost_gbp` by `(year, scheme)` and stacks the bands.
- **X2** sums `premium_gbp` across schemes per year, then cumulative-sums.
- **X3** divides `cost_gbp` by `households_uk` per scheme-year.
- **X4** divides `cost_gbp` by `generation_mwh` per scheme-year (after dropping rows with NaN generation).
- **X5** filters `year ∈ {2021, 2022, 2023}` and divides `premium_gbp` by `generation_mwh`.

The `methodology_version` column carries the `counterfactual.METHODOLOGY_VERSION` constant (`0.1.0` at time of writing) per row, inheriting the GOV-04 versioning discipline. Any future bump audits in `CHANGES.md` under `## Methodology versions`. See [`publish/manifest.py`](../data/index.md) for downloadable Parquet + CSV mirror and the per-row provenance contract.

Future-scheme additions (Phases 7-12) are append-only rows on this canonical table — no schema migration. New schemes contribute one `_read_<scheme>_long()` projector that renames their cost / premium / generation columns, tags rows with the scheme code, and concatenates into the join. Per-scheme HAZARD discipline applies at the join site (RO requires `country == "GB"` and `ro_cost_gbp.notna()` filters; pre-SY18 RO years carry NaN generation; RO-internal sensitivity columns are not carried).

## Scheme-year vs calendar-year reconciliation

The `year` column convention diverges between schemes. For Contracts for Difference, `year` is the calendar year of the settlement-month anchor. For the Renewables Obligation, `year` is the **obligation-year start calendar year** — for example, SY18 (April 2019 to March 2020) is stored as `year=2019`, matching the REF Constable Table 1 convention.

The `latest_fully_reconciled_year` rule treats these as comparable: it is the most recent year present in **every** shipped scheme's `annual_summary.parquet` where the scheme's primary cost column is non-null **and** the scheme is past its publication-cutoff for that year. Today (Phase 6, retrieved 2026-04-25) the value is `2023` — corresponding to CfD CY 2023 (January–December 2023 settlements) and RO SY23 (April 2023 – March 2024 obligation year). The 9-month overlap between the two windows is accepted as the partial-coverage caveat at this aggregation grain.

A hard cap `LATEST_COMPLETE_CFD_YEAR = 2025` excludes the in-progress CfD 2026 partial year from the headline-card pick. The constant lives in `src/uk_subsidy_tracker/schemes/portal/__init__.py` and is reviewed at each phase boundary. Deeper axis-convention rationalisation across all eight schemes is deferred to a future phase.

The intersection rule is implemented as `latest_fully_reconciled_year()` in `schemes/portal/__init__.py`: it reads each shipped scheme's `annual_summary.parquet`, filters to non-null primary cost rows past the publication-cutoff, intersects the year sets, and returns the maximum. Adding a new scheme to `SHIPPED_SCHEMES` automatically tightens the intersection — the headline-card year may move backward as new schemes ship with shorter publication histories, which is the correct behaviour for an honest cross-scheme aggregation.

## No-gas-counterfactual schemes

X4 and X5 require a gas counterfactual, since both express scheme economics as a per-MWh ratio against the gas baseline. The Capacity Market (Phase 9), Balancing Services (Phase 10), and Grid Socialisation (Phase 11) schemes do not have a meaningful gas counterfactual under this project's methodology. Capacity Market pays for capacity rather than energy and uses a modified-S2 treatment per ARCHITECTURE.md §5.3; Balancing Services is a delta-only quantity (post-renewables minus pre-renewables); Grid Socialisation is a best-effort TNUoS attribution with explicit low/central/high sensitivity bounds.

Including those schemes in X4 and X5 with placeholder zeros would mis-represent their economics. Each chart subtitle states the exclusion in-chart; this page documents the rationale once. When the Phase 9-11 modules ship, the `EXCLUDED_SCHEMES = frozenset({"Capacity Market", "Balancing Services", "Grid Socialisation"})` filter in `src/uk_subsidy_tracker/plotting/portal/x4_cost_per_mwh.py` and `x5_2022_crisis.py` engages automatically — no chart-code change required.

X1, X2, and X3 retain those scheme rows: total cost, premium, and per-household figures are coherent for all eight schemes, so the cross-scheme stacks and lines on those charts will absorb new bands as the modules ship. The exclusion is specific to the per-MWh ratio framings.

## Per-household division convention

X3 divides `cost_gbp` by a UK households count for each scheme-year. The denominator source is locked:

- **Dataset:** ONS *Families and Households* 2025 edition.
- **URL:** [https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/datasets/familiesandhouseholdsfamiliesandhouseholds](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/datasets/familiesandhouseholdsfamiliesandhouseholds)
- **Basis:** Labour Force Survey, April–June quarter; UK total households (single-family + multi-family + lone-person).
- **Retrieved:** 2026-04-25.
- **Raw file:** `data/raw/ons/familiesandhouseholdsuk2025.xlsx` (sha256 in sidecar).

A per-year denominator is used rather than a single fixed value: the ONS UK households count rose from approximately 26.7 million in 2014 to approximately 28.6 million in 2024 (a ~7% increase), which materially changes the early-year bars on X3. Each `cross_scheme.parquet` row's `households_uk` cell carries the ONS count for that `year` (calendar year). For RO obligation-year start (e.g. `year=2019` = SY18 = April 2019 to March 2020), the matching ONS year is the obligation-year start calendar year (CY 2019).

**Pre-2014 omission.** The ONS Families and Households time series begins in 2014. Pre-2014 X3 bars (RO 2006–2013) are omitted because the denominator is absent from the ONS source. The omission is documented here rather than papered over with an extrapolated denominator. Cumulative cost across 2006–2013 is preserved in `cross_scheme.parquet` for direct reading.

The `UK_HOUSEHOLDS` dict in `src/uk_subsidy_tracker/data/uk_households.py` carries one entry per year 2014–2024, transcribed verbatim from Sheet 7 ("All households") of the ONS XLSX. Each year-key is registered as a synthetic `UK_HOUSEHOLDS_YYYY` entry in `tests/fixtures/constants.yaml` and parametrised through `tests/test_constants_provenance.py::_live_constants()` so any drift between the source XLSX and the in-code dict produces a failing test on the next refresh.

## Partial-coverage caveat

The "covers 2 of 8 schemes" framing appears across the Portal surfaces — the homepage caveat line, every X-chart subtitle, and this page. It is the project's adversarial-proofing posture: a hostile reader cannot accuse the project of obscuring the coverage gap, because the gap is stated wherever a number is shown.

The headline-sync regression test (`tests/test_headline_sync.py`) re-arms automatically as Phase 7-12 schemes ship. Each new scheme adds rows to `cross_scheme.parquet`; on the next refresh, headline figures update; if prose figures in `docs/index.md` or any scheme page have not been updated, the test fails RED; a human PR updates the prose and `CHANGES.md`; the test goes green again. The X1 stack grows automatically — every visible band is real reconstructed data; no greyed-out "data pending" bands; no synthetic numbers from external estimates.

The cadence is: daily `refresh.yml` cron updates parquets and `manifest.json` automatically; prose headline updates happen in a separate human-reviewed PR triggered by the regression test going red. Humans review each headline change; small lag between data refresh and prose refresh is accepted as the cost of audit-anchored prose. There is no build-time substitution layer (no `mkdocs-macros`, no jinja templates) — every published number is plain markdown text under a regression test.

## Reference checks

REF Constable 2025 (*Renewable Subsidies*) and Andrew Turver's published per-scheme totals serve as **test-file tolerance anchors** for the project's pipeline reconciliation. They are NOT co-publishers of the figures shown on this site. The clinical citation surfaces are:

- `tests/fixtures/benchmarks.yaml::ref_constable` — 22 RO entries (2002–2023), per-entry tolerance ±3%.
- `tests/test_benchmarks.py::test_ref_constable_ro_reconciliation` — HARD CI block at ±3% per year (Phase 05.2 discipline).
- `tests/test_benchmarks.py::test_ref_total_reconciliation` — Wave 7 per-scheme REF subset cross-check; arms with both CfD and RO entries when CfD entries are transcribed.

REF's £25.8bn aggregate is the full-UK-2024 single-year cross-scheme total, not a sum of REF Table 1 per-scheme entries (2002–2023). The Phase 6 reconciliation test uses the per-scheme subset, not the £25.8bn aggregate.

Where a benchmark divergence above the per-entry tolerance is detected, the project's discipline is to investigate — not to silently skip the test, and not to revise the published figures to match the anchor. The benchmark is a check on this project's pipeline; this project's pipeline is not a check on the benchmark. The clinical-citation discipline applies to every reference anchor that may enter the audit in future phases.

## Reproducibility

Every chart and every number on this tier is reproducible from a fresh clone:

```bash
git clone https://github.com/richardjlyon/uk-subsidy-tracker.git
cd uk-subsidy-tracker
uv sync
uv run python -c "from uk_subsidy_tracker.schemes import portal; portal.refresh(); portal.rebuild_derived(); portal.regenerate_charts()"
```

Outputs:

- `data/derived/portal/cross_scheme.parquet` — long-format aggregation table.
- `data/derived/portal/cross_scheme.schema.json` — Pydantic schema sidecar.
- Five chart artefact triples in `docs/charts/html/x{1..5}_*.{png,html,div.html}`.
- `site/data/manifest.json` — updated with the `portal` entry on the next `refresh_all.publish_latest()` run.

Determinism (Phase 4 D-21 discipline) holds end-to-end: the same per-scheme `annual_summary.parquet` inputs produce a byte-identical `cross_scheme.parquet` output. `tests/test_determinism.py` re-runs the full rebuild twice and asserts byte-equality on the emitted file. Any non-determinism — floating-point reordering, dict-iteration drift, sort instability — fails the test before the parquet ships.

Two consecutive `portal.rebuild_derived()` calls against the same source parquets must produce a byte-identical output file (sha256 stable across runs). The single command above plus `uv run pytest tests/` reproduces the full audit chain: substrate → charts → tests → published `manifest.json`.

If a refresh fails or a benchmark check fails, the failure surfaces in CI before the parquet or chart artefacts are published — the `mkdocs build --strict` gate, the `pytest` suite, and the GitHub Actions workflow are the gates between this code and the live site.
