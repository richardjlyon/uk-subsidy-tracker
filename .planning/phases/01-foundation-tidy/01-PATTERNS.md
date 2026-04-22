# Phase 1: Foundation Tidy - Pattern Map

**Mapped:** 2026-04-21
**Files analyzed:** 13 (6 created + 7 modified/renamed categories)
**Analogs found:** 11 / 13 (2 use external spec — no analog needed)

---

## File Classification

### Files to be CREATED

| New File | Role | Data Flow | Closest Analog | Match Quality |
|----------|------|-----------|----------------|---------------|
| `ARCHITECTURE.md` | root-doc | static-content | already exists untracked | commit-as-is (no pattern needed) |
| `RO-MODULE-SPEC.md` | root-doc | static-content | already exists untracked | commit-as-is (no pattern needed) |
| `CHANGES.md` | root-doc | static-content | Keep-a-Changelog v1.1.0 (external spec) | external-spec |
| `CITATION.cff` | root-config | static-content | CFF 1.2.0 (external spec) | external-spec |
| `docs/about/corrections.md` | docs-page | static-content | `docs/technical-details/gas-counterfactual.md` | role-match (methodology/about prose) |
| `docs/about/citation.md` | docs-page | static-content | `docs/technical-details/gas-counterfactual.md` | role-match (short methodology-style stub) |

### Files to be MODIFIED (rename sweep)

| Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---------------|------|-----------|----------------|---------------|
| `pyproject.toml` | config | static-content | `pyproject.toml` itself | self-edit (two-line change) |
| `mkdocs.yml` | config | static-content | `mkdocs.yml` itself | self-edit (theme/nav/identity blocks) |
| `src/cfd_payment/` → `src/uk_subsidy_tracker/` | package | n/a (rename) | `src/cfd_payment/__init__.py` (canonical top-of-tree) | exact (rename preserves tree) |
| `src/cfd_payment/plotting/__main__.py` | entry-point | batch-orchestration | itself (edit-in-place after rename) | self-edit (import paths) |
| `docs/index.md` | docs-page | static-content | itself (edit-in-place) | self-edit (clone/run code blocks + URLs) |
| `docs/charts/index.md` | docs-page | static-content | itself (edit-in-place) | self-edit (reproduce commands + URLs) |
| `docs/technical-details/gas-counterfactual.md` → `docs/methodology/gas-counterfactual.md` | docs-page | static-content | self (git mv + link rewrite) | self-edit (inbound link references) |
| `README.md` | root-doc | static-content | `docs/index.md` (parallel prose) | role-match (if README exists; see "No Analog Found") |

---

## Pattern Assignments

### `docs/about/corrections.md` (docs-page, static-content)

**Analog:** `docs/technical-details/gas-counterfactual.md`

**Heading + prose style pattern** (lines 1-16):
```markdown
# Gas counterfactual

An audit trail for the orange "gas alternative" line on the CfD-vs-gas chart.

## The question

> *"If we'd kept the gas fleet we already had instead of paying for renewables, what would the same electricity have cost?"*

This is a policy-level counterfactual, not a market-clearing simulation. ...
```

**Apply:** H1 = page title; one-sentence lead; H2 sections; use `> quote` blocks where a guiding question helps frame the page.

**Table pattern** (lines 31-37):
```markdown
| Term | Source | Value |
|------|--------|-------|
| Gas price | [ONS System Average Price of gas](https://www.ons.gov.uk/...) | Daily, p/kWh thermal |
| CCGT efficiency | Modern H-class CCGT typical rating | 55% |
| Gas CO₂ intensity | Natural gas combustion | 0.184 tCO₂/MWh thermal |
```

**Apply to corrections page:** Use the same three-column style for the `Date | Chart/Page | Issue | Resolution | Commit SHA` template table per CONTEXT.md D-09 / Claude's discretion note.

**Code-fence + link-to-source pattern** (lines 106-122):
```markdown
## Reproducibility

The full calculation lives in [`src/cfd_payment/counterfactual.py`](https://github.com/richlyon/cfd-payment/blob/main/src/cfd_payment/counterfactual.py).
```

**Apply to corrections page:** Close with a "How to file" section that links to GitHub Issues with the `correction` label using the same anchor-link pattern.

---

### `docs/about/citation.md` (docs-page, static-content)

**Analog:** `docs/technical-details/gas-counterfactual.md` (short methodology-style stub)

**Short-page shell pattern** — this is a stub page per CONTEXT.md D-12. Reuse the lead-sentence + H2-sections shape from the counterfactual page at lines 1-16 but keep the body to two short sections:
1. "How to cite" — point at root-level `CITATION.cff`, note that versioned snapshot URLs land in Phase 4.
2. "Current version" — mirror `CITATION.cff` `version: "0.1.0"` field.

**Cross-link pattern** — mirror the `docs/index.md` pattern at line 59:
```markdown
The gas counterfactual methodology — how "what gas would have cost"
is computed — is documented in detail at
[Gas counterfactual](technical-details/gas-counterfactual.md).
```
For `citation.md`, link out to the root-relative `CITATION.cff` using a GitHub blob URL pattern (same shape as the source-code link at `docs/technical-details/gas-counterfactual.md:108`).

---

### `CHANGES.md` (root-doc, static-content)

**Analog:** None in codebase — follow Keep-a-Changelog v1.1.0 external spec verbatim.

**Reference URL:** https://keepachangelog.com/en/1.1.0/

**Seed structure (per CONTEXT.md Claude's Discretion):**
- `# Changelog` H1
- Preamble paragraph pointing at Keep-a-Changelog + Semantic Versioning.
- `## [Unreleased]` section header.
- `## [0.1.0] — 2026-04-21` entry with `### Changed`, `### Added`, `### Removed` subheadings summarising: package rename, theme swap, root docs commit.
- `## Methodology versions` trailing section header (empty body — hook for Phase 2 GOV-04 per CONTEXT.md `<specifics>`).

No codebase analog required — format is externally specified.

---

### `CITATION.cff` (root-config, static-content)

**Analog:** None in codebase — follow CFF 1.2.0 external spec verbatim.

**Reference URL:** https://citation-file-format.github.io/

**Required fields per CONTEXT.md Claude's Discretion:**
```yaml
cff-version: 1.2.0
message: "If you use this data or analysis, please cite it as below."
title: "UK Renewable Subsidy Tracker"
authors:
  - family-names: Lyon
    given-names: Richard
    email: richlyon@fastmail.com
version: "0.1.0"
date-released: 2026-04-21
repository-code: "https://github.com/richardjlyon/uk-subsidy-tracker"
```

No codebase analog required — format is externally specified. ORCID omitted until user provides.

---

### `pyproject.toml` (config, self-edit)

**Analog:** `pyproject.toml` itself (lines 2, 29)

**Current state to change** (lines 1-5):
```toml
[project]
name = "cfd-payment"
version = "0.1.0"
description = "Analysis of UK Contracts for Difference (CfD) renewable energy subsidy payments"
requires-python = ">=3.11"
```

**Hatch packages block** (lines 28-29):
```toml
[tool.hatch.build.targets.wheel]
packages = ["src/cfd_payment"]
```

**Change pattern:**
- Line 2: `name = "cfd-payment"` → `name = "uk-subsidy-tracker"`
- Line 29: `packages = ["src/cfd_payment"]` → `packages = ["src/uk_subsidy_tracker"]`
- Line 4 description: judgment call — recommend updating to reflect portal scope per PROJECT mission statement.

---

### `mkdocs.yml` (config, self-edit — integration point)

**Analog:** `mkdocs.yml` itself

**Current site identity block** (lines 1-16):
```yaml
# MkDocs Configuration for CfD Payment Analysis
#
# IMPORTANT: Before building/serving docs, generate charts:
#   uv run python -m cfd_payment.plotting
# This populates docs/charts/html/ with chart files (ignored by git)
#   uv run mkdocs gh-deploy
# This updates the GitHub Pages site

site_name: CfD Payment Analysis
site_url: https://richardjlyon.github.io/cfd-payment/
site_description: Analysis of UK Contracts for Difference (CfD) renewable energy subsidy payments
site_author: Richard Lyon

# Repository
repo_name: cfd-payment
repo_url: https://github.com/richardjlyon/cfd-payment
```

**Target (per CONTEXT.md D-05, D-06, D-07):**
- `site_name: UK Renewable Subsidy Tracker`
- `site_url: https://richardjlyon.github.io/uk-subsidy-tracker/`
- `repo_name: uk-subsidy-tracker`
- `repo_url: https://github.com/richardjlyon/uk-subsidy-tracker`
- Header comment `uv run python -m cfd_payment.plotting` → `uv run python -m uk_subsidy_tracker.plotting`

**Current theme block** (lines 18-21):
```yaml
# Theme
theme:
  name: readthedocs
  locale: en
```

**Target theme block (per CONTEXT.md D-01 through D-04):**
```yaml
theme:
  name: material
  locale: en
  features:
    - navigation.tabs
    - navigation.sections
    - toc.follow
    - search.suggest
    - search.highlight
    - content.code.copy
  palette:
    - scheme: default
      toggle:
        icon: material/weather-night
        name: Switch to dark mode
    - scheme: slate
      toggle:
        icon: material/weather-sunny
        name: Switch to light mode
```

**Current nav block** (lines 23-31):
```yaml
nav:
  - Home: index.md
  - Charts:
      - Overview: charts/index.md
      - CfD Dynamics (4-panel): charts/subsidy/cfd-dynamics.md
      - CfD vs Gas Cost: charts/subsidy/cfd-vs-gas-cost.md
      - Remaining Obligations: charts/subsidy/remaining-obligations.md
  - Gas Counterfactual: technical-details/gas-counterfactual.md
```

**Target nav block (per CONTEXT.md D-10, D-11):**
```yaml
nav:
  - Home: index.md
  - Charts:
      - Overview: charts/index.md
      - CfD Dynamics: charts/subsidy/cfd-dynamics.md
      - CfD vs Gas Cost: charts/subsidy/cfd-vs-gas-cost.md
      - Remaining Obligations: charts/subsidy/remaining-obligations.md
  - Gas Counterfactual: methodology/gas-counterfactual.md
  - About:
      - Corrections: about/corrections.md
      - Citation: about/citation.md
```

**Keep unchanged:** `markdown_extensions` (lines 33-66), `plugins` (lines 68-70), `extra.social` (lines 73-76), `copyright` (line 79 — update year only if needed).

---

### `src/cfd_payment/` → `src/uk_subsidy_tracker/` (package rename)

**Analog:** `src/cfd_payment/__init__.py` (lines 1-5)

**Canonical shape — unchanged content after git mv:**
```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "charts" / "html"
```

**Apply:** `git mv src/cfd_payment src/uk_subsidy_tracker` (per CONTEXT.md D-14). File contents identical. Only the directory path changes.

**Import rewrite sweep — 24 Python files contain `from cfd_payment`:**
- All 24 files must change in the same commit (CONTEXT.md D-15 gate criterion).
- Mechanical substitution: `from cfd_payment` → `from uk_subsidy_tracker`, `cfd_payment.` → `uk_subsidy_tracker.`.
- Full file list from codebase sweep: `src/cfd_payment/counterfactual.py`, `src/cfd_payment/data/elexon.py`, `src/cfd_payment/data/lccc.py`, `src/cfd_payment/data/ons_gas.py`, `src/cfd_payment/plotting/__main__.py`, `src/cfd_payment/plotting/chart_builder.py`, `src/cfd_payment/plotting/utils.py`, `src/cfd_payment/plotting/capacity_factor/__init__.py`, `src/cfd_payment/plotting/capacity_factor/monthly.py`, `src/cfd_payment/plotting/capacity_factor/seasonal.py`, `src/cfd_payment/plotting/cannibalisation/capture_ratio.py`, `src/cfd_payment/plotting/cannibalisation/price_vs_wind.py`, `src/cfd_payment/plotting/intermittency/generation_heatmap.py`, `src/cfd_payment/plotting/intermittency/load_duration.py`, `src/cfd_payment/plotting/intermittency/rolling_minimum.py`, `src/cfd_payment/plotting/subsidy/bang_for_buck.py`, `src/cfd_payment/plotting/subsidy/bang_for_buck_old.py`, `src/cfd_payment/plotting/subsidy/cfd_dynamics.py`, `src/cfd_payment/plotting/subsidy/cfd_payments_by_category.py`, `src/cfd_payment/plotting/subsidy/cfd_vs_gas_cost.py`, `src/cfd_payment/plotting/subsidy/lorenz.py`, `src/cfd_payment/plotting/subsidy/remaining_obligations.py`, `src/cfd_payment/plotting/subsidy/scissors.py`, `src/cfd_payment/plotting/subsidy/subsidy_per_avoided_co2_tonne.py`.
- Also `tests/data/test_lccc.py` and `tests/data/test_ons.py` contain `cfd_payment` references.
- `demo_dark_theme.py` (3 occurrences) — repo-root script; update or quarantine per planner discretion.

---

### `src/uk_subsidy_tracker/plotting/__main__.py` (entry-point, batch-orchestration)

**Analog:** existing `src/cfd_payment/plotting/__main__.py` (canonical entry-point form)

**Canonical import-aliased-main pattern** (lines 1-22):
```python
from cfd_payment.plotting.cannibalisation.capture_ratio import main as capture_ratio
from cfd_payment.plotting.cannibalisation.price_vs_wind import main as price_vs_wind
from cfd_payment.plotting.capacity_factor.monthly import main as cf_monthly
from cfd_payment.plotting.capacity_factor.seasonal import main as cf_seasonal
...
from cfd_payment.plotting.subsidy.remaining_obligations import (
    main as remaining_obligations,
)
```

**Apply:** every `from cfd_payment.` becomes `from uk_subsidy_tracker.`. The "alias-as-main" pattern per CLAUDE.md conventions (allows parallel execution in orchestration) is preserved — only the package prefix changes.

---

### `docs/index.md` (docs-page, self-edit)

**Analog:** itself

**Code-block + URL pattern to update** (lines 65-73):
```markdown
```bash
git clone https://github.com/richardjlyon/cfd-payment
cd cfd-payment
uv sync
uv run python -m cfd_payment.plotting    # regenerate all charts
uv run mkdocs serve                      # serve this site locally
```

Source: [github.com/richardjlyon/cfd-payment](https://github.com/richardjlyon/cfd-payment).
```

**Changes:**
- Line 66: `cfd-payment` → `uk-subsidy-tracker`
- Line 67: `cd cfd-payment` → `cd uk-subsidy-tracker`
- Line 69: `cfd_payment.plotting` → `uk_subsidy_tracker.plotting`
- Line 73: both URL and link text swap `cfd-payment` → `uk-subsidy-tracker`
- Line 80: same URL swap in Corrections/Issues link
- Line 59: link `technical-details/gas-counterfactual.md` → `methodology/gas-counterfactual.md` (per CONTEXT.md D-11)

**Title/H1 — judgment call** (line 1): `# CfD Payment Analysis` — leave as-is (narrative refers specifically to CfD chapter, not the portal). Matches CONTEXT.md discretion note: "leave narrative text describing the 'CfD' scheme untouched."

---

### `docs/charts/index.md` (docs-page, self-edit)

**Analog:** itself

**Reproduce-command pattern** (lines 54-68):
```markdown
## Reproducing

All charts are regenerated from public data by a single command:

```bash
uv run python -m cfd_payment.plotting
```

Or an individual chart:

```bash
uv run python -m cfd_payment.plotting.subsidy.cfd_dynamics
```

Source: [github.com/richardjlyon/cfd-payment](https://github.com/richardjlyon/cfd-payment).
```

**Changes:**
- Lines 59, 65: `cfd_payment.plotting` → `uk_subsidy_tracker.plotting`
- Line 68: both URL and link text swap.
- Line 52: internal link `../technical-details/gas-counterfactual.md` → `../methodology/gas-counterfactual.md`.

---

### `docs/technical-details/gas-counterfactual.md` → `docs/methodology/gas-counterfactual.md`

**Analog:** itself (git mv)

**GitHub source-link pattern to update** (lines 108, 122, 126-128):
```markdown
The full calculation lives in [`src/cfd_payment/counterfactual.py`](https://github.com/richlyon/cfd-payment/blob/main/src/cfd_payment/counterfactual.py).
...
```bash
uv run python -m cfd_payment.plotting.subsidy.cfd_vs_gas_cost
```
...
from cfd_payment.counterfactual import (
    compute_counterfactual,
    CCGT_NEW_BUILD_CAPEX_OPEX_PER_MWH,
)
```

**Changes:**
- Line 108: `cfd_payment` → `uk_subsidy_tracker` (both path and URL).
- Line 108: URL `richlyon/cfd-payment` → `richardjlyon/uk-subsidy-tracker` (note the existing file has `richlyon/` — **broken URL, fix during rename sweep**).
- Line 121: `cfd_payment.plotting.subsidy.cfd_vs_gas_cost` → `uk_subsidy_tracker.plotting.subsidy.cfd_vs_gas_cost`
- Line 127: `from cfd_payment.counterfactual import` → `from uk_subsidy_tracker.counterfactual import`

**Inbound link rewrites required (per CONTEXT.md D-11):**
- `docs/index.md:59` → `methodology/gas-counterfactual.md`
- `docs/charts/index.md:52` → `../methodology/gas-counterfactual.md`
- `docs/charts/subsidy/cfd-dynamics.md:104` (`../../technical-details/gas-counterfactual.md` → `../../methodology/gas-counterfactual.md`)
- Likely similar in `cfd-vs-gas-cost.md` and `remaining-obligations.md` — grep `technical-details` under `docs/` before commit.

---

## Shared Patterns

### Prose style (all new docs pages)

**Source:** `docs/technical-details/gas-counterfactual.md` lines 1-16

**Apply to:** `docs/about/corrections.md`, `docs/about/citation.md`

```markdown
# <Page Title>

<One-sentence lead in plain English.>

## <First H2 — typically "The question" or "The commitment">

<Framing paragraph. Use > blockquote for guiding question where helpful.>
```

### GitHub source-link convention

**Source:** `docs/technical-details/gas-counterfactual.md:108`

**Apply to:** all docs pages that reference source files, CITATION.cff link in `docs/about/citation.md`, CHANGES.md commit references.

```markdown
[`<relative/path>`](https://github.com/richardjlyon/uk-subsidy-tracker/blob/main/<relative/path>)
```

Note: canonical user handle is `richardjlyon` (not `richlyon` — which appears as a bug at `docs/technical-details/gas-counterfactual.md:108` and should be fixed during rename sweep).

### Reproduce-command code fence

**Source:** `docs/index.md:65-71` and `docs/charts/index.md:58-66`

**Apply to:** any new docs page with a runnable command; use `uv run python -m uk_subsidy_tracker.<subpath>` form.

```bash
uv run python -m uk_subsidy_tracker.plotting
```

### Absolute imports from package root

**Source:** CLAUDE.md "Import Organization" conventions + every Python file in the sweep.

**Apply to:** every Python file (existing and new) — no relative imports except within adjacent submodules (e.g., `from .lccc import ...` in `src/uk_subsidy_tracker/data/__init__.py`).

```python
# Within package
from .lccc import download_lccc_datasets, load_lccc_dataset   # relative — adjacent
# Cross-module / consumer
from uk_subsidy_tracker import DATA_DIR                       # absolute — package root
from uk_subsidy_tracker.data import load_gas_price            # absolute — submodule
```

### Snake_case + UPPER_SNAKE constants

**Source:** `src/cfd_payment/__init__.py:3-5` and CLAUDE.md "Naming Patterns"

**Apply to:** zero functional changes in Phase 1 — this pattern is preserved verbatim across the rename. Called out so the planner does not accidentally introduce `ukSubsidyTracker`-style renaming.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `README.md` | root-doc | static-content | No `README.md` exists at repo root today. Planner should create one (parallel prose to `docs/index.md`) **or** defer creation and only touch it if already present. CONTEXT.md §"Files to modify" names it — treat as "create-if-missing" and mirror the clone-and-run block from `docs/index.md:65-73` with updated package/URL tokens. |
| `CHANGES.md` | root-doc | static-content | No in-repo analog; format dictated by Keep-a-Changelog v1.1.0 external spec (see Pattern Assignments above). |
| `CITATION.cff` | root-config | static-content | No in-repo analog; format dictated by CFF 1.2.0 external spec (see Pattern Assignments above). |

---

## Metadata

**Analog search scope:**
- `/Users/rjl/Code/github/cfd-payment/src/cfd_payment/` (Python package)
- `/Users/rjl/Code/github/cfd-payment/docs/` (site source)
- `/Users/rjl/Code/github/cfd-payment/` (root config + root docs)
- `/Users/rjl/Code/github/cfd-payment/tests/` (test call sites)

**Files scanned:** 52 contain `cfd_payment`/`cfd-payment` tokens (257 total occurrences). 24 Python source files require import rewrites in the rename sweep. 6 docs/config files require URL + module-path rewrites.

**Pattern extraction date:** 2026-04-21
