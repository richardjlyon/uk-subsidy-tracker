---
id: SEED-001
status: dormant
planted: 2026-04-22
planted_during: "Phase 2 — Test & Benchmark Scaffolding (milestone v1.0)"
trigger_when: "Phase 4 (publishing-layer) planning begins, OR when constants count exceeds ~12, OR at first milestone-v1.0 audit"
scope: medium
---

# SEED-001: Formalize formula-constant provenance (Tier 2 + Tier 3)

## Why This Matters

During Phase 2's adversarial audit (2026-04-22) of `tests/test_counterfactual.py`
pin values, two constants in `src/uk_subsidy_tracker/counterfactual.py`
(`GAS_CO2_INTENSITY_THERMAL` and `carbon_prices[2022]`) did not match the
regulator sources they cited — they had silently drifted since initial
authoring. The drift was caught only because the user asked "check against
an external source."

To be defensible under the project's "survives hostile reading" constraint
(PROJECT.md core value), we need three layers of discipline:

1. **Tier 1** (shipped 2026-04-22, commit `efdfbbc`): every institutional
   constant carries a structured `Provenance:` docstring with source, URL,
   basis, retrieval date, and next-audit trigger. Grep-discoverable via
   `grep -rn "^Provenance:" src/ tests/`.

2. **Tier 2** (THIS SEED): a machine-queryable `tests/fixtures/constants.yaml`
   mirroring the Pydantic pattern of `benchmarks.yaml`, plus a drift test
   that asserts the live constants in `counterfactual.py` match the YAML.
   This adds an explicit tripwire: if someone edits a constant without
   updating the YAML entry, the test fails. A second test can warn when
   `next_audit` dates are overdue.

3. **Tier 3** (THIS SEED): auto-render the YAML as a provenance table on
   `docs/methodology/gas-counterfactual.md` (or a new
   `docs/methodology/sources.md`). A hostile reader clicks a URL and sees
   the exact line of our audit trail, including retrieval date and basis.

Tier 1 is enough for six constants; as scheme modules land (RO, FiT, SEG,
Capacity Market, Constraint Payments, Balancing Services, Grid
Socialisation — Phases 5 to 12), the constant count will grow to dozens,
and Tier 1's grep-discipline won't scale. Tier 2/3 are the right home for
that scale.

## When to Surface

**Primary trigger:** Phase 4 (publishing-layer) planning. Phase 4 already
builds `manifest.json` with full provenance for every Parquet output and
reconciles against published regulator totals — constants.yaml fits the
same ethos.

**Secondary triggers:**
- When the constant count exceeds ~12 (grep discipline stops scaling).
- At the first milestone-v1.0 audit pass, before the site goes public.
- If any scheme-module phase introduces its own institutional constants
  (likely Phase 5: RO module) and wants a consistent place to record
  provenance.

## Scope Estimate

**Medium** — ~1 day's work, concretely:

- 2 hours: design the `ConstantProvenance` Pydantic model + YAML schema
  (source, url, basis, retrieved_on, next_audit, value, unit). Reuse
  `BenchmarkEntry` patterns from `tests/fixtures/__init__.py`.
- 2 hours: write `tests/fixtures/constants.yaml` covering the six
  `counterfactual.py` constants (and whatever exists by Phase 4 in scheme
  modules).
- 2 hours: write `tests/test_constants_provenance.py`:
  - `test_every_live_constant_in_yaml` — reflection over `counterfactual.py`
    symbols finds any that lacks a YAML entry.
  - `test_yaml_values_match_live_constants` — drift detector.
  - `test_no_overdue_audits` — warning (not failure) when `next_audit` has
    passed.
- 2 hours: mkdocs rendering — jinja hook or a `scripts/render_provenance_table.py`
  that's invoked in the same pre-build step as chart generation. Table
  renders into either the existing `docs/methodology/gas-counterfactual.md`
  or a new `docs/methodology/sources.md` that the formula page links to.

## Breadcrumbs

Related code and decisions in the current codebase:

- `src/uk_subsidy_tracker/counterfactual.py` — Tier 1 `Provenance:` blocks
  (reference the shape when designing constants.yaml).
- `tests/fixtures/__init__.py` — `BenchmarkEntry` Pydantic model and
  `load_benchmarks()` are the direct analog to mirror.
- `tests/fixtures/benchmarks.yaml` — YAML shape reference (source, year,
  value, url, retrieved_on, notes, tolerance_pct).
- `tests/test_benchmarks.py` — LCCC floor + external anchor parametrise
  pattern; `tests/test_constants_provenance.py` can follow the same layout.
- `docs/methodology/gas-counterfactual.md` — rendering target; current
  "Last audited" footnote already points readers at the provenance blocks.
- Commit `ecb6786` — the constant-correction commit that triggered this
  seed (includes both the drift findings and the fix).
- Commit `efdfbbc` — Tier 1 provenance implementation (reference for
  docstring structure).
- ARCHITECTURE.md §11 P3 (Publishing layer) — Phase 4 scope, where this
  seed most naturally lands.
- `.planning/phases/02-test-benchmark-scaffolding/02-CONTEXT.md` D-05 —
  benchmarks.yaml provenance requirement; constants.yaml should follow
  the same discipline.

## Notes

The adversarial audit that revealed the drift is a useful demonstration
to cite when Phase 4 picks this up — it is concrete evidence that Tier 1's
grep-discipline is insufficient even at six constants. If the YAML had
existed in Phase 2, a drift test would have failed on the first CI run
and the 0.184-vs-0.18290 and 53.0-vs-73.0 discrepancies would have been
caught before any methodology-version commitment.

Status note: seeds are officially surfaced by `/gsd-new-milestone`, not
by `/gsd-new-phase`. Until that scan is extended to phase planning,
remember to grep `.planning/seeds/` before starting `/gsd-discuss-phase 4`
— or promote this seed to an explicit Phase-4 requirement in REQUIREMENTS.md
when the discuss-phase runs.
