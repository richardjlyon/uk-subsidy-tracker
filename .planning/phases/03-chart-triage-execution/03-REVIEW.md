---
phase: 03-chart-triage-execution
reviewed: 2026-04-22T00:00:00Z
depth: standard
files_reviewed: 26
files_reviewed_list:
  - .github/workflows/ci.yml
  - docs/index.md
  - docs/themes/cannibalisation/capture-ratio.md
  - docs/themes/cannibalisation/index.md
  - docs/themes/cannibalisation/methodology.md
  - docs/themes/cost/cfd-dynamics.md
  - docs/themes/cost/cfd-vs-gas-cost.md
  - docs/themes/cost/index.md
  - docs/themes/cost/methodology.md
  - docs/themes/cost/remaining-obligations.md
  - docs/themes/efficiency/index.md
  - docs/themes/efficiency/methodology.md
  - docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md
  - docs/themes/recipients/cfd-payments-by-category.md
  - docs/themes/recipients/index.md
  - docs/themes/recipients/lorenz.md
  - docs/themes/recipients/methodology.md
  - docs/themes/reliability/capacity-factor-seasonal.md
  - docs/themes/reliability/generation-heatmap.md
  - docs/themes/reliability/index.md
  - docs/themes/reliability/methodology.md
  - docs/themes/reliability/rolling-minimum.md
  - mkdocs.yml
  - src/uk_subsidy_tracker/counterfactual.py
  - src/uk_subsidy_tracker/plotting/__main__.py
  - tests/test_docs_structure.py
findings:
  critical: 0
  warning: 8
  info: 11
  total: 19
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-04-22T00:00:00Z
**Depth:** standard
**Files Reviewed:** 26
**Status:** issues_found

## Summary

Phase 3 delivered the chart-triage restructure: 7 PROMOTE chart pages,
5 theme directories with index + methodology, cut files removed,
`tests/test_docs_structure.py` guarding the structural invariants, and
CI wired to regenerate charts before `mkdocs build --strict`.

The structure is sound and the adversarial-proofing bar (GOV-01
four-way coverage) is enforced by a machine-readable test. No
security-sensitive code was touched. The issues below are all quality
or correctness-of-prose problems that undermine the project's own
"reproducible headline number" commitment from CLAUDE.md: chart pages
cite the same cumulative premium as £14.1bn, £14.2bn, and £14.9bn in
three adjacent files (and twice within one file), and the efficiency
theme header claims AR3 is "above UK ETS" while the chart itself
excludes AR3. These are the most important findings.

The counterfactual.py module and the docs structure test both have
small defects worth fixing; the CI workflow could be tightened to
block docs build on test failure and to give the plotting entry
point a `__main__` guard plus basic failure logging.

## Warnings

### WR-01: Internal contradiction on cumulative premium figure

**File:** `docs/themes/cost/cfd-vs-gas-cost.md:26,117`
**Issue:** The headline table on line 26 reports the CfD-vs-gas
**Premium** as **£14.2bn**. The narrative paragraph on line 117 in
the same file says *"Cumulatively, the CfD system cost £14.9bn more
than the existing gas fleet would have over the same period."*
Two different figures for the same quantity in the same document
undermines the project's "every headline number reproducible" promise
(CLAUDE.md core value). This is the **lead chart of the lead theme**
— the page a journalist is most likely to cite from.
**Fix:** Decide the canonical figure (14.2 vs 14.9) — the discrepancy
likely comes from different aggregation windows (Jan 2018 – Apr 2026
for the headline table vs. full LCCC window in the narrative). Either:
(a) quote one figure consistently and move window detail into a
footnote, or (b) re-cast line 117 as "Cumulatively over the full LCCC
window (incl. 2016–17) the CfD system cost £14.9bn more …" so the
two figures are explicitly scoped to different windows.

### WR-02: Cross-page divergence on the same "premium" figure

**File:** `docs/themes/cost/cfd-dynamics.md:33`,
`docs/themes/cost/cfd-vs-gas-cost.md:26`,
`docs/methodology/gas-counterfactual.md:67`
**Issue:** Three files report *the same cumulative premium* with
three different numbers:
- `cfd-dynamics.md:33` — "Endpoint currently **£14.1bn**."
- `cfd-vs-gas-cost.md:26` — "**Premium £14.2bn**"
- `gas-counterfactual.md:67` — "**£14.9bn**" (default scenario
  premium vs CfD in the sensitivity table)

These are the same quantity at rounding noise tolerances. A reader
clicking across pages will see three distinct-looking numbers and
lose confidence in the project's core claim. The CLAUDE.md principle
is that a single `uv sync` + one command reproduces *every* published
number byte-identically. Today's figures appear to come from
slightly different runs / windows of the counterfactual.
**Fix:** Define a single aggregation window + single computation path
for the "cumulative premium" figure and reference it from all three
files. Consider introducing a `HEADLINE_FIGURES.md` (generated from a
pin test) that every page links to for its numeric claims — this
would also support the Phase-4 "golden numbers" test seed.

### WR-03: Efficiency pages claim AR3 is above UK ETS but chart omits AR3

**File:** `docs/themes/efficiency/index.md:17`,
`docs/themes/efficiency/subsidy-per-avoided-co2-tonne.md:3,17`
**Issue:** Both pages open with the claim *"AR3 already well above
UK ETS"* / *"recent rounds already sit above the UK ETS ceiling"*.
The caveats section on the detail page, however, says:
*"Later rounds (AR3–AR6) do not yet have sufficient generation
history to render meaningfully and are omitted"*
(line 17) and explicitly *"AR3–AR6 are absent. They are omitted only
because their cumulative generation is too small to produce stable
per-year ratios."* (line 136). The chart therefore does **not** plot
AR3, so the "already above UK ETS" claim cannot be read off the
chart the page is describing — it's an unsupported claim in the
current deliverable.
**Fix:** Either: (a) remove the AR3 claim from both pages' headers
pending sufficient generation history, or (b) cite an external
source for the AR3 £/tCO₂ estimate and label it clearly as a
projection, not a chart observation. Recommend (a) for the current
Phase-3 deliverable.

### WR-04: Colour labelling for 2022 clawback contradicts between pages

**File:** `docs/themes/cannibalisation/capture-ratio.md:28-29`,
`docs/themes/cannibalisation/methodology.md:17`
**Issue:** On `capture-ratio.md` the caption says
*"blue for positive levy (consumers topping up), green for
negative (clawback…)"*. On `methodology.md` for the same theme
the text says *"Positive values (red in the chart) indicate consumer
top-up; negative values (green) indicate producer clawback"*. The
colour for "consumer top-up" is *blue* on one page and *red* on the
other. A reader matching prose to image will fail on one of the two
pages.
**Fix:** Inspect the actual chart output
(`docs/charts/html/cannibalisation_capture_ratio_twitter.png`) and
align both pages to the truth. The methodology page says "red" but
the detail page says "blue" and the detail page is more recent /
more detailed — likely the methodology page is stale.

### WR-05: `index.md` status paragraph is stale post-Phase-3

**File:** `docs/index.md:73-76`
**Issue:**
> "The three charts above are production; supporting analyses
> (capacity factor, intermittency, cannibalisation) are in the
> source repo but not yet documented here."

Only **one** chart (`subsidy_cfd_dynamics_twitter.png`) is embedded
above this paragraph, not three. And Phase 3 has now documented
capacity factor, intermittency, and cannibalisation as first-class
theme pages — so the second half of the sentence is also stale. The
home page is the site's front door; this paragraph contradicts the
site structure a visitor will see in the nav.
**Fix:** Update to something like:
```markdown
## Status

Version 0.x prototype. All five theme pages (Cost, Recipients,
Efficiency, Cannibalisation, Reliability) are published with their
flagship charts; methodology pages carry the formulas and provenance.
Corrections and contributions welcome via
[GitHub Issues](https://github.com/richardjlyon/uk-subsidy-tracker/issues).
```

### WR-06: `compute_counterfactual_monthly` silently drops `non_fuel_opex_per_mwh` override

**File:** `src/uk_subsidy_tracker/counterfactual.py:162-169`
**Issue:** `compute_counterfactual_monthly()` accepts
`gas_df`, `carbon_prices`, and `ccgt_efficiency` but **not**
`non_fuel_opex_per_mwh`. If a caller wants the monthly variant of the
new-build sensitivity (opex = 20.0), they cannot express that through
the monthly wrapper — it will silently use `DEFAULT_NON_FUEL_OPEX = 5.0`
with no warning. This is a parameter-passing bug (interface
inconsistency) rather than a crash, but it will produce subtly wrong
sensitivity numbers if the monthly wrapper is adopted in, say, the
`cfd_vs_gas_cost.py` chart code.
**Fix:**
```python
def compute_counterfactual_monthly(
    gas_df: pd.DataFrame | None = None,
    carbon_prices: dict[int, float] | None = None,
    ccgt_efficiency: float = CCGT_EFFICIENCY,
    non_fuel_opex_per_mwh: float = DEFAULT_NON_FUEL_OPEX,
) -> pd.DataFrame:
    """Monthly-averaged version of compute_counterfactual."""
    daily = compute_counterfactual(
        gas_df, carbon_prices, ccgt_efficiency, non_fuel_opex_per_mwh
    )
    return daily.set_index("date").resample("ME").mean(numeric_only=True).reset_index()
```

### WR-07: `plotting/__main__.py` executes at import time

**File:** `src/uk_subsidy_tracker/plotting/__main__.py:22-42`
**Issue:** All 14 chart-generation calls run at module top level,
with no `if __name__ == "__main__":` guard. `__main__.py` is only
invoked as `python -m uk_subsidy_tracker.plotting`, so in practice
this works — but any future code that accidentally imports
`uk_subsidy_tracker.plotting.__main__` (e.g. `from
uk_subsidy_tracker.plotting.__main__ import capture_ratio` or a
Python-path glob) will silently regenerate **every** chart at import
time. That's a significant side effect and a convention violation
(CLAUDE.md ARCHITECTURE notes the plotting `__init__.py` *likely
re-exports `ChartBuilder`* — further imports of this area are
plausible). Also: there is no try/except around the 14 calls, so a
single failing chart aborts the CI `Regenerate charts` step with
minimal signal about which chart broke.
**Fix:**
```python
def main() -> None:
    charts = [
        ("cfd_vs_gas_total", cfd_vs_gas_total),
        ("cfd_dynamics", cfd_dynamics),
        # ... remaining charts ...
    ]
    failures: list[tuple[str, Exception]] = []
    for name, fn in charts:
        try:
            fn()
            print(f"OK  {name}")
        except Exception as e:
            print(f"ERR {name}: {e}")
            failures.append((name, e))
    if failures:
        raise SystemExit(
            f"{len(failures)} chart(s) failed: "
            + ", ".join(n for n, _ in failures)
        )


if __name__ == "__main__":
    main()
```

### WR-08: CI `docs` job does not depend on `test` job

**File:** `.github/workflows/ci.yml:8-44`
**Issue:** `test` and `docs` are defined as sibling jobs with no
`needs: test` on the `docs` job. This means a PR with broken tests
will still run the full chart-regeneration + mkdocs build, using CI
minutes, and — more importantly — a passing **docs** run alongside
a failing **test** run can create an ambiguous PR status where
reviewers rely on "green docs" and miss the "red tests" badge. For
a project whose core principle is reproducibility backed by tests,
docs should not claim success when the underlying tests do not pass.
**Fix:**
```yaml
  docs:
    runs-on: ubuntu-latest
    needs: test   # block docs build until tests pass
    steps:
      - uses: actions/checkout@v5
      ...
```

## Info

### IN-01: `mkdocs.yml` uses `locale:` (Material expects `language:`)

**File:** `mkdocs.yml:21`
**Issue:** Material for MkDocs theme documents the localisation key
as `theme.language`, not `theme.locale`. `locale: en` is likely
silently ignored (Material's schema will accept unknown keys without
error in most versions). English is the default so the chart rendering
is unaffected, but the key is a no-op.
**Fix:** Either drop the line or change to `language: en`.

### IN-02: Comment misdescribes `validation:` block as "--strict gate teeth"

**File:** `mkdocs.yml:43`
**Issue:** The comment on line 43 says *"--strict gate teeth"* but all
four `validation:` entries are set to `warn`/`info`, not `error`.
`mkdocs build --strict` promotes **warnings** to errors, so in the CI
context these do gate the build — but a reader of the config alone
(without knowing about `--strict`) would believe from the comment
that these are strict-error settings, which they are not by
themselves. Consider clarifying:
**Fix:** Change comment to:
```yaml
# Validation — entries below are WARNING level by default;
# `mkdocs build --strict` (used in CI) promotes them to ERROR.
```

### IN-03: `GAS_CO2_INTENSITY_THERMAL` rendered as 0.184 in multiple docs but code uses 0.18290

**File:** `docs/themes/cost/methodology.md:22`,
`docs/themes/cost/cfd-dynamics.md:60`,
`docs/themes/cost/cfd-vs-gas-cost.md:143`
**Issue:** The code constant is
`GAS_CO2_INTENSITY_THERMAL = 0.18290`
(`counterfactual.py:27`), and
`docs/methodology/gas-counterfactual.md` cites 0.18290 correctly. But
the three Cost theme pages round to 0.184 in their inline formula. Not
a bug — all three are clearly approximate renderings — but it does
mean a grep of the codebase for the canonical value turns up two
distinct values. The SEED-001 provenance seed already flags this kind
of drift as a risk.
**Fix:** Use 0.183 (more accurate 3-sig-fig rounding of 0.18290) or
quote the full 0.18290 to match the authoritative methodology page
and source code.

### IN-04: `index.md:9` figure "£29 billion" scope is unclear

**File:** `docs/index.md:9`
**Issue:** The headline says *"Ten years into the scheme, UK
consumers have paid £29 billion for CfD electricity"*. The detail
pages disambiguate £28.5bn (Jan 2018 – Apr 2026 window) vs £29.2bn
(full LCCC window including pre-2018). The home page rounds to
£29bn which happens to land near the full-window figure but reads
as if it is the "over ten years" figure. Tighten the scope.
**Fix:** Add an inline footnote or change to *"Since the scheme
began in 2016, UK consumers have paid £29 billion for CfD
electricity"*; consider linking to `cfd-vs-gas-cost.md` for the
table breakdown.

### IN-05: `cfd-vs-gas-cost.md:97` "£13bn" is inconsistent with headline "£12.6bn"

**File:** `docs/themes/cost/cfd-vs-gas-cost.md:97`
**Issue:** The headline table on line 23 says CfD levy cumulative is
**£12.6bn**. Line 97 says *"£13bn cumulatively, the blue slice"*.
Rounding inconsistency in the same document.
**Fix:** Use £12.6bn in both places, or use £13bn throughout and note
the table should be rounded similarly.

### IN-06: `test_docs_structure.py` uses relative paths

**File:** `tests/test_docs_structure.py:12,39-98`
**Issue:** `DOCS = Path("docs")`, `Path("mkdocs.yml")` and similar
relative paths will only resolve when pytest is invoked from repo
root. Most CI runs satisfy this, but a developer running
`pytest tests/test_docs_structure.py` from `tests/` will see every
assertion fail with a confusing "missing PROMOTE page" error instead
of a clear path error. CLAUDE.md tool-use guidance also says
*"always use absolute paths"*.
**Fix:** Anchor to the file's own location:
```python
REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"
# ... and use REPO_ROOT / "mkdocs.yml" for the validation test.
```

### IN-07: CI does not cache the Plotly/kaleido Chrome download

**File:** `.github/workflows/ci.yml:26-44`
**Issue:** `kaleido >= 1.2.0` (the Plotly static-export backend)
downloads Chrome on first use. Each CI run currently pays this cost.
`astral-sh/setup-uv@v8.1.0` caches Python deps but not the kaleido
Chrome binary. This is a *performance* issue (per review scope:
out of v1 scope) but also a *reliability* issue when the kaleido
CDN is flaky — a flaky third-party download will fail the docs job
non-deterministically.
**Fix:** Consider a `actions/cache@v4` step keyed on the kaleido
version for `~/.cache/kaleido` or similar. Out of Phase-3 scope;
record as a follow-up.

### IN-08: `plotting/__main__.py` imports a `price_vs_wind` chart but no doc page appears to cover it

**File:** `src/uk_subsidy_tracker/plotting/__main__.py:2,42`
**Issue:** `price_vs_wind` is generated on every CI run but is not
listed in `mkdocs.yml` navigation nor in any of the 7 PROMOTE pages
from `test_docs_structure.py`. If this chart is intentionally
orphaned (behind-the-scenes diagnostic) that is fine, but it does
produce artefacts in `docs/charts/html/` that mkdocs' `omitted_files:
warn` may complain about. Verify the output filename does not fall
inside `nav` / linked-from scope.
**Fix:** If `price_vs_wind` is intentional but unpublished, add a
comment above the import line flagging it. Similarly for
`load_duration`, `bang_for_buck`, `cf_monthly` — all generate outputs
but none of the four PROMOTE-list pages mention them. Either document
them or move their generation out of the default `__main__` run to
avoid `mkdocs --strict` surfacing `omitted_files` warnings on those
PNG/HTML outputs.

### IN-09: Trivial doc typo — "top the difference up"

**File:** `docs/index.md:40`
**Issue:** *"why wind crashes its own price, and who tops the
difference up"* reads awkwardly. Compare with the more polished
`themes/cannibalisation/index.md:3` which says *"consumers top up
the difference through the CfD levy"*.
**Fix:** *"why wind crashes its own price, and who pays the top-up"*
or *"why wind crashes its own price, and who covers the difference"*.

### IN-10: `cfd-payments-by-category.md:54-57` describes "2022 negative slivers" imprecisely

**File:** `docs/themes/recipients/cfd-payments-by-category.md:54-57`
**Issue:** The prose says *"2022 appears as negative slivers"* for
*"most technologies"*. The chart plots
`reference_price × generation + CFD_Payments_GBP`; in 2022 the
`CFD_Payments_GBP` term went negative but `reference × gen` did not,
so the total cost cell typically remained positive. The claim that
monthly bars went below zero requires the magnitude of the negative
payments to exceed the positive wholesale component — which may not
be the case for most technologies. If the chart actually does show
negative slivers, the caveats section (line 105-109) is correct; if
not, the argument copy is describing a different diagnostic.
**Fix:** Verify against the rendered PNG and either (a) adjust prose
to "2022 shows sharply reduced bar heights as the negative levy
offset compressed the total CfD cost" or (b) confirm slivers are
visible and leave as-is.

### IN-11: Methodology page promises "Gini ≈ 0.74" but Lorenz page says "No Gini coefficient plotted"

**File:** `docs/themes/recipients/methodology.md:21`,
`docs/themes/recipients/lorenz.md:99-102`
**Issue:** Methodology says *"a Gini coefficient is computed over the
same per-recipient cumulative-payment vector and reported as the
headline number on the flagship chart. For current data, Gini ≈
0.74"*. The Lorenz page explicitly says *"No Gini coefficient
plotted"*. These contradict: either the Gini is rendered on the
flagship chart or it is not.
**Fix:** Inspect the rendered chart; align both pages. Likely fix:
in `methodology.md` change to *"A Gini coefficient can be computed
from the same vector (≈ 0.74 for current data); it is not plotted
on the chart itself but is quoted here as a single-number summary."*

---

_Reviewed: 2026-04-22T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
