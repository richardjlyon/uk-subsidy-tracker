# Phase 2: Test & Benchmark Scaffolding - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-22
**Phase:** 02-test-benchmark-scaffolding
**Areas discussed:** Scope of TEST-02/TEST-03 (schema + aggregates), Benchmark divergence format (TEST-04)
**Areas deferred to Claude's Discretion:** CI workflow shape (TEST-06), Methodology versioning (GOV-04)

---

## Area 1: Scope of TEST-02/TEST-03 (schema + aggregates)

### Q1: What should TEST-02 (`test_schemas.py`) cover in Phase 2?

| Option | Description | Selected |
|--------|-------------|----------|
| Validate current CSVs via pandera | Reinterpret "schema" broadly; load each raw CSV and assert pandera validation. Phase 4 adds Parquet variants to the same file. | ✓ |
| Stub and skip | File exists with `@pytest.mark.skip("derived Parquet lands in Phase 4")` placeholders. | |
| Defer to Phase 4 | Do not create the file in Phase 2; update REQUIREMENTS/ROADMAP. | |

**User's choice:** Validate current CSVs via pandera.
**Notes:** Reuses existing `lccc_generation_schema` / `lccc_portfolio_schema`; adds sibling schemas for Elexon AGWS, Elexon system prices, and ONS gas SAP.

### Q2: What should TEST-03 (`test_aggregates.py`) cover in Phase 2?

| Option | Description | Selected |
|--------|-------------|----------|
| In-memory aggregates on current CfD pipeline | Row-conservation assertions (`sum by year == sum by year × tech`) against live pandas aggregation chain. | ✓ |
| Stub with skip markers | Placeholder tests skipped pending Phase 4 derived tables. | |
| Defer to Phase 4 | Don't ship the file in Phase 2; update REQUIREMENTS/ROADMAP. | |

**User's choice:** In-memory aggregates on current CfD pipeline.

### Q3: What should TEST-05 (`test_determinism.py`) do when there's no Parquet output yet?

| Option | Description | Selected |
|--------|-------------|----------|
| Hash in-memory aggregate output | Two runs, serialise to temp Parquet via pyarrow, SHA-256 compare. | |
| Stub with skip markers | File exists, test skipped pending Phase 4 pipeline. | |
| Defer to Phase 4 entirely | No file created in Phase 2. | ✓ |

**User's choice:** Defer to Phase 4 entirely.
**Notes:** Deterministic byte-identity has no meaning without the Parquet layer it targets.

### Q4: How should we reconcile ROADMAP/REQUIREMENTS with whatever we ship?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep REQ-IDs in Phase 2; CONTEXT records pre-Parquet interpretation | No changes to REQUIREMENTS.md; CONTEXT.md notes the variant. | |
| Move TEST-02/03/05 to Phase 4 | Update traceability so Phase 2 ships TEST-01/TEST-04/TEST-06 + GOV-04. | ✓ |
| Split each REQ into 2a/2b | TEST-02a (CSV, Phase 2) + TEST-02b (Parquet, Phase 4); same for TEST-03/TEST-05. | |

**User's choice:** Move TEST-02/03/05 to Phase 4.
**Notes:** Phase 2 still ships pre-Parquet variants of `test_schemas.py` and `test_aggregates.py` as useful-today scaffolding, but the formal REQ-IDs satisfy when the Parquet layer lands in Phase 4. ROADMAP Phase 2 success criterion 1 rewords from "all five test classes present" to "four test classes present and passing."

---

## Area 2: Benchmark divergence format (TEST-04)

### Q1: Where should the external benchmark numbers live?

| Option | Description | Selected |
|--------|-------------|----------|
| Hardcoded dict in `test_benchmarks.py` | Inline Python dicts with citing docstrings. | |
| YAML fixture at `tests/fixtures/benchmarks.yaml` | Structured: source / year / value / url / retrieved_on / notes. | ✓ |
| Committed CSV snapshots | One CSV per external source under `tests/fixtures/benchmarks/`. | |

**User's choice:** YAML fixture.
**Notes:** Cleaner PR diffs, surfaces retrieval metadata, matches "commit the data" discipline.

### Q2: How are divergences (our_total vs external) documented?

| Option | Description | Selected |
|--------|-------------|----------|
| Assert with named tolerance + docstring rationale | Tolerances as named constants with docstrings; self-documenting. | ✓ |
| Print table on test run + docstring | Noisy markdown table to stdout. | |
| Dedicated docs page + minimal test | `docs/about/benchmarks.md` rendered from test data. | |
| All three — belt and braces | Maximum adversarial-proofing; highest maintenance cost. | |

**User's choice:** Assert with named tolerance + docstring rationale.

### Q3: When an external benchmark diverges beyond tolerance, what happens?

| Option | Description | Selected |
|--------|-------------|----------|
| Fail the test + force CHANGES.md entry | Tolerance bump requires `## Methodology versions` entry. | ✓ |
| Fail the test — tolerance bump is normal code change | Lighter process; weaker audit trail. | |
| Mark xfail + raise issue in daily CI only | Matches ARCHITECTURE §9.6 daily-CI pattern; weakens commit gate. | |

**User's choice:** Fail the test + force CHANGES.md entry.

### Q4: Which benchmark sources must Phase 2's test_benchmarks.py actually cover?

| Option | Description | Selected |
|--------|-------------|----------|
| All three: Ben Pile (2021 + 2026), REF CfD subset, Turver aggregate | Literal read of ARCHITECTURE §11 P1 / ROADMAP success criterion 3. | |
| Start with Ben Pile only | Defer REF + Turver until multi-scheme data exists. | |
| Ben Pile + REF; defer Turver to Phase 5 | Middle ground. | |
| **Other — user notes** | "Ben Pile and Dav Turver were just two other commentators when I was discussing project scope. They are not canonical — we need to research other sources of key comparison data." | ✓ |

**User's choice:** Other — Ben Pile/Turver are not canonical; surface canonical sources via researcher.

---

## Area 2 follow-up: Canonical benchmark sources

### Q5: Which regulator/official sources should the researcher prioritise?

| Option | Description | Selected |
|--------|-------------|----------|
| LCCC's own published annual summary totals | Floor self-reconciliation. | ✓ |
| Ofgem CfD levy spend transparency + CfD budget dashboards | Independent supplier-levy view. | ✓ |
| DESNZ / BEIS CfD Allocation Round summaries + Energy Trends | Government-side anchors. | ✓ |
| NAO + House of Commons Library + CCC | Audit-grade independent scrutineers. | ✓ |

**User's choice:** All four categories.

### Q6: Should test_benchmarks.py always include a "our totals == LCCC's published totals (within 0.1%)" floor check?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — mandatory floor, always green | Non-negotiable pipeline red-line. | ✓ |
| Yes, but only if LCCC publishes a single canonical total table | Conditional on researcher finding such a table. | |
| No — redundant with the pipeline | External reconciliation only. | |

**User's choice:** Yes — mandatory floor, always green.

### Q7: If the researcher can't produce a short list of canonical benchmarks, what then?

| Option | Description | Selected |
|--------|-------------|----------|
| Ship LCCC floor only; external benchmarks as follow-up | test_benchmarks.py passes with LCCC floor; external anchors slip as they're located. | ✓ |
| Block Phase 2 until 2+ external sources found | Strictest adversarial-proofing. | |
| Defer all of TEST-04 to a later phase | Phase 2 shrinks to TEST-01 + TEST-06 + GOV-04. | |

**User's choice:** Ship LCCC floor only; external anchors as follow-up.

---

## Claude's Discretion

- **CI workflow shape (TEST-06)** — single-job `.github/workflows/ci.yml` on push/PR, Python 3.12, `astral-sh/setup-uv@v4`, `uv sync --frozen` + `uv run pytest`. No ruff/pyright/mkdocs-strict gate in Phase 2.
- **Methodology versioning (GOV-04) shape** — `METHODOLOGY_VERSION = "1.0.0"` as a module-level constant in `counterfactual.py`, returned as a DataFrame column. SemVer semantics: patch = constant tweak, minor = additive parameter, major = formula-shape change. CHANGES.md seeds `### 1.0.0 — 2026-04-22 — Initial formula (fuel + carbon + O&M)`.
- **Pin test mechanics** — hardcoded float expected to 4 decimal places for 2022 + 2019 slices + synthetic all-zeros input.
- **Benchmark YAML schema location** — Pydantic model in `tests/fixtures/__init__.py` or `tests/conftest.py`; planner decides.

---

## Deferred Ideas

- `tests/test_determinism.py` — Phase 4.
- Parquet-variant checks in `test_schemas.py` / `test_aggregates.py` — Phase 4.
- `mkdocs build --strict` CI gate — Phase 3.
- ruff / pyright / pre-commit in CI — Phase 3+ polish.
- Daily-refresh CI workflow — Phase 4 (GOV-03).
- Multi-scheme benchmarks (RO, FiT, etc.) — later scheme phases.
- Coverage reports — indefinitely unless adopted as project norm.
- Benchmark drift monitoring (weekly re-fetch + diff) — post-P11 steady-state.
- Zenodo DOI registration — V2-COMM-01, after Phase 5.
- Ben Pile / Turver reconciliations — non-canonical; if ever added, under a `commentators:` key flagged as non-regulator.
