---
phase: 04-publishing-layer
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - pyproject.toml
  - uv.lock
  - tests/fixtures/__init__.py
  - tests/fixtures/constants.yaml
  - tests/test_constants_provenance.py
  - CHANGES.md
autonomous: true
requirements:
  - GOV-04
  # GOV-04 is already Complete in REQUIREMENTS.md; this plan reinforces it by
  # adding the SEED-001 Tier 2 drift test that makes the Phase-2
  # "bump METHODOLOGY_VERSION" discipline machine-checkable. No new req ID
  # in the official phase list — SEED-001 + GOV-04 carries this work.
tags: [dependencies, fixtures, tests, drift]
user_setup: []

must_haves:
  truths:
    - "pyarrow and duckdb are installed after `uv sync`"
    - "tests/fixtures/constants.yaml exists with six counterfactual.py constants"
    - "tests/test_constants_provenance.py passes on green main"
    - "Any edit to a tracked counterfactual.py constant fails the drift test with a remediation message"
  artifacts:
    - path: "pyproject.toml"
      provides: "pyarrow>=24.0.0 + duckdb>=1.5.2 added to [project.dependencies]"
      contains: "pyarrow"
    - path: "uv.lock"
      provides: "Locked versions for pyarrow + duckdb reproducible via uv sync --frozen"
    - path: "tests/fixtures/constants.yaml"
      provides: "Provenance block for six counterfactual constants (CCGT_EFFICIENCY, GAS_CO2_INTENSITY_THERMAL, CCGT_EXISTING_FLEET_OPEX_PER_MWH, DEFAULT_CARBON_PRICES_2021/2022/2023)"
      min_lines: 40
    - path: "tests/fixtures/__init__.py"
      provides: "ConstantProvenance + Constants Pydantic models + load_constants() loader alongside existing BenchmarkEntry/Benchmarks/load_benchmarks"
      contains: "class ConstantProvenance"
    - path: "tests/test_constants_provenance.py"
      provides: "Parametrised drift test: every live constant has a YAML entry + value matches exactly + next_audit warn-not-fail"
      min_lines: 60
      contains: "METHODOLOGY_VERSION"
    - path: "CHANGES.md"
      provides: "[Unreleased] entry: pyarrow+duckdb deps + constants.yaml drift test (SEED-001 Tier 2)"
      contains: "pyarrow"
  key_links:
    - from: "tests/test_constants_provenance.py"
      to: "src/uk_subsidy_tracker/counterfactual.py"
      via: "import counterfactual; getattr(counterfactual, attr)"
      pattern: "from uk_subsidy_tracker import counterfactual"
    - from: "tests/test_constants_provenance.py"
      to: "tests/fixtures/constants.yaml"
      via: "load_constants() reads YAML via fixtures/__init__.py loader"
      pattern: "load_constants"
    - from: "tests/fixtures/__init__.py"
      to: "tests/fixtures/constants.yaml"
      via: "yaml.safe_load + Pydantic Constants(**raw)"
      pattern: "yaml.safe_load"
---

<objective>
Wave 0: add pyarrow + duckdb to the dependency set and ship the SEED-001 Tier 2
constants-drift tripwire. This plan MUST land before every other Phase 4 plan
because (a) every Parquet writer imports pyarrow, (b) the docs/data/index.md
snippet uses duckdb, and (c) the drift test is the only automated defence
against a repeat of the Phase-2 `0.184` vs `0.18290` incident. Ship the
tripwire before the publishing work introduces new methodology-version surface
area.

Purpose: unblock all downstream plans (02-05) with deps + establish the
constant-drift enforcement mechanism per SEED-001 Tiers 2 (Tier 3 deferred
per D-25).

Output: `pyarrow>=24.0.0`, `duckdb>=1.5.2` in pyproject.toml + uv.lock;
tests/fixtures/constants.yaml with six entries; tests/fixtures/__init__.py
with ConstantProvenance + Constants + load_constants(); passing
tests/test_constants_provenance.py; CHANGES.md [Unreleased] entry.
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
@.planning/phases/04-publishing-layer/04-VALIDATION.md
@.planning/seeds/SEED-001-constant-provenance-tiers-2-3.md
@pyproject.toml
@tests/fixtures/__init__.py
@tests/fixtures/benchmarks.yaml
@src/uk_subsidy_tracker/counterfactual.py
@CHANGES.md

<interfaces>
<!-- Extracted from tests/fixtures/__init__.py — loader + two-layer Pydantic pattern to mirror. -->

```python
# tests/fixtures/__init__.py:13-17  (imports to keep)
from datetime import date
from pathlib import Path
import yaml
from pydantic import BaseModel, Field, HttpUrl

# tests/fixtures/__init__.py:20-54  (Pydantic shape — BenchmarkEntry + Benchmarks mirror)
class BenchmarkEntry(BaseModel):
    source: str = Field(...)
    year: int = Field(..., ge=2015, le=2050)
    value_gbp_bn: float
    url: HttpUrl
    retrieved_on: date
    notes: str
    tolerance_pct: float = Field(..., gt=0, le=50.0)

class Benchmarks(BaseModel):
    lccc_self: list[BenchmarkEntry] = Field(default_factory=list)
    # ... other source categories

# tests/fixtures/__init__.py:57-74  (loader — source-key injection idiom)
def load_benchmarks(config_path: str = "benchmarks.yaml") -> Benchmarks:
    default_dir = Path(__file__).parent
    with open(default_dir / config_path, "r") as f:
        raw = yaml.safe_load(f) or {}
    for source_key, entries in raw.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            entry["source"] = source_key
    return Benchmarks(**raw)
```

<!-- Extracted from src/uk_subsidy_tracker/counterfactual.py — constants to cover in constants.yaml. -->

```python
# Module-level uppercase constants to pin (SEED-001 Tier 2 tracked set):
CCGT_EFFICIENCY = 0.55                    # line 12
GAS_CO2_INTENSITY_THERMAL = 0.18290       # line 27
# Grep `Provenance:` docstrings in counterfactual.py for canonical URL/basis/retrieved_on/next_audit text.
# DEFAULT_CARBON_PRICES: dict[int, float] keyed by year → three synthetic YAML entries
#   DEFAULT_CARBON_PRICES_2021 = 48.0
#   DEFAULT_CARBON_PRICES_2022 = 73.0
#   DEFAULT_CARBON_PRICES_2023 = 45.0
# CCGT_EXISTING_FLEET_OPEX_PER_MWH (or equivalent — verify live name by reading
# counterfactual.py before authoring; research named DEFAULT_NON_FUEL_OPEX as well).

METHODOLOGY_VERSION: str = "0.1.0"        # line 38  (string, not numeric — exclude from _TRACKED)
```

<!-- NOTE to executor: Before authoring constants.yaml, grep the module for Provenance: blocks
     and use those docstrings verbatim as the source of source/url/basis/retrieved_on/next_audit text:
     `grep -n "^Provenance:" src/uk_subsidy_tracker/counterfactual.py` -->
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Add pyarrow + duckdb to pyproject.toml; refresh uv.lock</name>
  <files>pyproject.toml, uv.lock</files>
  <read_first>
    - pyproject.toml (current dependencies block; 19 lines already)
    - .planning/phases/04-publishing-layer/04-RESEARCH.md §Standard Stack (verified versions: pyarrow>=24.0.0, duckdb>=1.5.2)
    - .planning/phases/04-publishing-layer/04-CONTEXT.md D-22 (pyarrow is REQUIRED dependency)
  </read_first>
  <action>
    Use `uv add` so that uv.lock updates atomically:

    ```bash
    uv add "pyarrow>=24.0.0" "duckdb>=1.5.2"
    ```

    This will (a) append both lines to `[project.dependencies]` in pyproject.toml
    and (b) resolve + write uv.lock. Do NOT hand-edit pyproject.toml.

    Expected diff in pyproject.toml `[project.dependencies]` — two new lines
    (alphabetical insertion point between "pandera>=0.31.1" and "plotly"):

    ```toml
    "pandera>=0.31.1",
    "duckdb>=1.5.2",     # NEW — docs/data/index.md DuckDB snippets + future validate() helper
    "plotly",
    "pyarrow>=24.0.0",   # NEW — Parquet I/O + determinism strip (D-22, D-21)
    "pydantic>=2.13.1",
    ```

    uv will pick its own exact placement; alphabetical is fine either way.
    After the add completes:

    ```bash
    uv sync --frozen
    uv run python -c "import pyarrow, duckdb; print(pyarrow.__version__, duckdb.__version__)"
    ```

    The one-liner MUST print two version strings (≥24.0.0 for pyarrow and
    ≥1.5.2 for duckdb). If it fails, investigate PyPI wheel availability for
    Python 3.12/3.13 on macOS-arm64 + linux-x86_64 before proceeding.
  </action>
  <verify>
    <automated>uv sync --frozen &amp;&amp; uv run python -c "import pyarrow, duckdb; assert pyarrow.__version__ >= '24.0.0' and duckdb.__version__ >= '1.5.2', (pyarrow.__version__, duckdb.__version__)"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -E '^\s*"(pyarrow|duckdb)' pyproject.toml` prints TWO lines (one for each)
    - `grep -E '^\s*"pyarrow>=24' pyproject.toml` returns exit 0
    - `grep -E '^\s*"duckdb>=1\.5' pyproject.toml` returns exit 0
    - `uv.lock` modified (git diff --stat shows change)
    - `uv run python -c "import pyarrow"` exits 0
    - `uv run python -c "import duckdb"` exits 0
    - `uv run pytest tests/` exits 0 (no test regression from dep add)
  </acceptance_criteria>
  <done>pyarrow + duckdb installed; existing test suite still green; uv.lock refreshed and committed.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Create tests/fixtures/constants.yaml + extend fixtures loader + ship drift test</name>
  <files>tests/fixtures/constants.yaml, tests/fixtures/__init__.py, tests/test_constants_provenance.py</files>
  <read_first>
    - tests/fixtures/__init__.py (current BenchmarkEntry/Benchmarks/load_benchmarks — mirror its shape EXACTLY)
    - tests/fixtures/benchmarks.yaml (current comment-block header — reuse its tone)
    - src/uk_subsidy_tracker/counterfactual.py (all `Provenance:` docstring blocks — copy source/url/basis/retrieved_on/next_audit text verbatim into constants.yaml)
    - tests/test_counterfactual.py (parametrised-pin + remediation-hook-failure-message template; lines 38-67)
    - .planning/phases/04-publishing-layer/04-RESEARCH.md §Pattern 7 (full test file shape, lines 896-997)
    - .planning/phases/04-publishing-layer/04-PATTERNS.md §A (Pydantic + YAML loader pattern)
    - .planning/phases/04-publishing-layer/04-PATTERNS.md §E (parametrised pin + remediation-hook pattern)
    - .planning/seeds/SEED-001-constant-provenance-tiers-2-3.md (cite the 0.184 vs 0.18290 incident in test docstring)
  </read_first>
  <behavior>
    <!-- TDD: write these tests first; they MUST fail with "ModuleNotFoundError" or
         "No constants.yaml entry" before constants.yaml + loader are written.
         Then author YAML + loader; tests turn green. -->

    Test 1 (`test_every_tracked_constant_in_yaml`) — parametrised over six names:
      CCGT_EFFICIENCY, GAS_CO2_INTENSITY_THERMAL, CCGT_EXISTING_FLEET_OPEX_PER_MWH
      (OR DEFAULT_NON_FUEL_OPEX — check live counterfactual.py; use whichever name
      the module exports),
      DEFAULT_CARBON_PRICES_2021, DEFAULT_CARBON_PRICES_2022, DEFAULT_CARBON_PRICES_2023.
      For each: asserts the name is present in constants.yaml entries.

    Test 2 (`test_yaml_value_matches_live`) — same parametrisation. For each:
      asserts `live_value == entry.value` (exact equality). Failure message MUST
      cite: (a) actual live value, (b) YAML value, (c) SEED-001 Tier 2 remediation
      (bump METHODOLOGY_VERSION + update constants.yaml + add CHANGES.md ##
      Methodology versions entry), (d) the entry.url for source.

    Test 3 (`test_audits_not_overdue`) — NOT parametrised. Iterates over all
      entries; if any `next_audit < today`, issues `warnings.warn(...)` — does
      NOT fail. Rationale documented in docstring: calendar events ≠ CI failures.

    Reflection helper (`_live_constants`) — iterates `dir(counterfactual)` for
      UPPERCASE attrs of (int, float) type; for `DEFAULT_CARBON_PRICES` dict,
      expands each {year: price} into synthetic `DEFAULT_CARBON_PRICES_{year}`
      keys. Excludes `METHODOLOGY_VERSION` (str, not numeric — naturally filtered
      by isinstance check).
  </behavior>
  <action>
    Three sub-steps in a single task (author in this order — TDD):

    ### Step 2A — Write `tests/test_constants_provenance.py` FIRST (RED)

    Mirror tests/test_counterfactual.py:38-67 for parametrisation + remediation-
    message shape. Full file ≈ 80 lines; spec is RESEARCH §Pattern 7 lines
    896-997. Mandatory elements:

    ```python
    """Constants drift test (SEED-001 Tier 2).

    The Phase-2 adversarial audit caught `GAS_CO2_INTENSITY_THERMAL = 0.184`
    (wrong) vs 0.18290 (correct) by user inspection only. Tier 1 grep-
    discipline missed it. This test is the tripwire that would have caught it.

    Any edit to a counterfactual.py constant must:
      1. Update the live value in counterfactual.py.
      2. Update the matching entry in tests/fixtures/constants.yaml.
      3. Bump METHODOLOGY_VERSION.
      4. Add a CHANGES.md `## Methodology versions` entry.
    Missing any of (2)-(4) fails this test.
    """

    from datetime import date
    import warnings
    import pytest

    from tests.fixtures import load_constants
    from uk_subsidy_tracker import counterfactual


    _TRACKED = {
        "CCGT_EFFICIENCY",
        "GAS_CO2_INTENSITY_THERMAL",
        # NOTE: Replace with actual live name — grep counterfactual.py for
        # the O&M constant (DEFAULT_NON_FUEL_OPEX or CCGT_EXISTING_FLEET_OPEX_PER_MWH).
        "DEFAULT_NON_FUEL_OPEX",
        "DEFAULT_CARBON_PRICES_2021",
        "DEFAULT_CARBON_PRICES_2022",
        "DEFAULT_CARBON_PRICES_2023",
    }


    def _live_constants() -> dict[str, float]:
        live: dict[str, float] = {}
        for attr in dir(counterfactual):
            if not attr.isupper():
                continue
            value = getattr(counterfactual, attr)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                live[attr] = float(value)
            elif attr == "DEFAULT_CARBON_PRICES" and isinstance(value, dict):
                for year, price in value.items():
                    live[f"DEFAULT_CARBON_PRICES_{year}"] = float(price)
        return live


    @pytest.fixture(scope="module")
    def constants():
        return load_constants()


    @pytest.mark.parametrize("name", sorted(_TRACKED))
    def test_every_tracked_constant_in_yaml(name, constants):
        live = _live_constants()
        assert name in live, (
            f"{name} is in _TRACKED but not on counterfactual module."
        )
        assert name in constants.entries, (
            f"No constants.yaml entry for {name}. "
            f"Add {{source, url, basis, retrieved_on, next_audit, value, unit}} "
            f"per SEED-001 Tier 2."
        )


    @pytest.mark.parametrize("name", sorted(_TRACKED))
    def test_yaml_value_matches_live(name, constants):
        live = _live_constants()
        entry = constants.entries[name]
        assert live[name] == entry.value, (
            f"Drift detected for {name}: live = {live[name]}, yaml = {entry.value}. "
            f"Per SEED-001 Tier 2, bump METHODOLOGY_VERSION (currently "
            f"{counterfactual.METHODOLOGY_VERSION!r}), update "
            f"tests/fixtures/constants.yaml, and add CHANGES.md `## Methodology "
            f"versions` entry. YAML source: {entry.url}"
        )


    def test_audits_not_overdue(constants):
        today = date.today()
        overdue = [
            (name, entry) for name, entry in constants.entries.items()
            if entry.next_audit is not None and entry.next_audit < today
        ]
        if overdue:
            for name, entry in overdue:
                warnings.warn(
                    f"Overdue audit for {name}: next_audit = {entry.next_audit} "
                    f"({(today - entry.next_audit).days} days ago). "
                    f"Review source ({entry.url}) and update retrieved_on + next_audit."
                )
    ```

    ### Step 2B — Extend `tests/fixtures/__init__.py` with loader (TURN GREEN pt 1)

    APPEND (do NOT replace) to the existing file. Preserve the module docstring
    and existing BenchmarkEntry/Benchmarks/load_benchmarks. Add, below the
    existing __all__ (and update __all__):

    ```python
    class ConstantProvenance(BaseModel):
        """Provenance block for one counterfactual.py constant (SEED-001 Tier 2)."""

        name: str = Field(..., description="Parent YAML key = live counterfactual.py attr name (or synthetic {ATTR}_{KEY} for dict entries).")
        source: str = Field(..., description="Human-readable source citation (regulator + publication).")
        url: HttpUrl
        basis: str = Field(..., description="Methodological basis — what's being measured, how.")
        retrieved_on: date
        next_audit: date | None = None
        value: float
        unit: str
        notes: str | None = None


    class Constants(BaseModel):
        """Container: `entries` maps live attr name → ConstantProvenance."""

        entries: dict[str, ConstantProvenance] = Field(default_factory=dict)


    def load_constants(config_path: str = "constants.yaml") -> Constants:
        """Load + validate tests/fixtures/constants.yaml.

        Mirrors `load_benchmarks`: injects the parent YAML key as the
        `name` field on each entry before Pydantic validation.
        """
        default_dir = Path(__file__).parent
        with open(default_dir / config_path, "r") as f:
            raw = yaml.safe_load(f) or {}
        entries = {}
        for key, payload in raw.items():
            if not isinstance(payload, dict):
                continue
            payload = {**payload, "name": key}
            entries[key] = ConstantProvenance(**payload)
        return Constants(entries=entries)


    __all__ = [
        "BenchmarkEntry", "Benchmarks", "load_benchmarks",
        "ConstantProvenance", "Constants", "load_constants",
    ]
    ```

    ### Step 2C — Author `tests/fixtures/constants.yaml` (TURN GREEN pt 2)

    Header block (adapt from benchmarks.yaml:1-14):

    ```yaml
    # Constant provenance fixtures for `tests/test_constants_provenance.py` (SEED-001 Tier 2).
    #
    # Each top-level key is the live attribute name on
    # `src/uk_subsidy_tracker/counterfactual.py`. For dict-valued constants
    # (e.g. DEFAULT_CARBON_PRICES), the key is synthetic: {ATTR}_{DICT_KEY}
    # such as DEFAULT_CARBON_PRICES_2022.
    #
    # Each entry MUST match the `Provenance:` docstring block on the live
    # constant (field-for-field: source, url, basis, retrieved_on, next_audit)
    # and MUST match the live numerical value to exact equality. Drift
    # between the YAML value and the live constant fails
    # `test_yaml_value_matches_live` with a remediation message that points
    # at this file.
    ```

    Entries — SIX (verbatim values + docstring text from counterfactual.py):

    1. **CCGT_EFFICIENCY** — value `0.55`, unit `"dimensionless (fraction)"`.
       Copy `source`/`url`/`basis`/`retrieved_on` from counterfactual.py:19-25
       Provenance block; `next_audit` = `2027-06-01` (next BEIS edition ~18 mo).
    2. **GAS_CO2_INTENSITY_THERMAL** — value `0.18290`, unit `"tCO2 / MWh thermal"`.
       Copy from counterfactual.py:30-36. `next_audit` = `2027-04-01`.
       `notes`: `"Corrected from 0.184 during 2026-04-22 audit (SEED-001 tripwire origin)."`
    3. **DEFAULT_NON_FUEL_OPEX** (or CCGT_EXISTING_FLEET_OPEX_PER_MWH — match
       the actual live constant name; grep counterfactual.py first) — value
       matching live, unit `"£/MWh"`. Copy Provenance from counterfactual.py.
    4. **DEFAULT_CARBON_PRICES_2021** — value `48.0`, unit `"£/tCO2"`,
       source `"OBR Economic & Fiscal Outlook — UK ETS annual average"`,
       url `"https://obr.uk/forecasts-in-depth/tax-by-tax-spend-by-spend/emissions-trading-scheme-uk-ets/"`,
       basis `"UK ETS annual average, £/tCO2"`, retrieved_on `2026-04-22`,
       next_audit `2027-01-15`, notes `"First full UK ETS year post-Brexit divergence."`
    5. **DEFAULT_CARBON_PRICES_2022** — same structure, value = live module value.
    6. **DEFAULT_CARBON_PRICES_2023** — same structure, value = live module value.

    CRITICAL: Before writing the YAML, run `grep -n "^Provenance:" src/uk_subsidy_tracker/counterfactual.py`
    AND read each docstring block to get the exact source/url/basis text. Do NOT
    invent citations. If a live constant has no Provenance: docstring block, STOP
    and add one in counterfactual.py BEFORE shipping its YAML entry (SEED-001
    Tier 1 prerequisite for Tier 2).

    After all three files exist: `uv run pytest tests/test_constants_provenance.py -v`
    must report 13 passed (6 name-in-yaml + 6 value-matches-live + 1 audits-not-overdue).
  </action>
  <verify>
    <automated>uv run pytest tests/test_constants_provenance.py -v</automated>
  </verify>
  <acceptance_criteria>
    - `tests/fixtures/constants.yaml` file exists
    - `wc -l tests/fixtures/constants.yaml` reports at least 40 lines
    - `grep -c "^CCGT_EFFICIENCY:\|^GAS_CO2_INTENSITY_THERMAL:\|^DEFAULT_CARBON_PRICES_2021:\|^DEFAULT_CARBON_PRICES_2022:\|^DEFAULT_CARBON_PRICES_2023:" tests/fixtures/constants.yaml` returns 5 (plus the O&M entry = 6 total top-level keys)
    - `grep -c "^[A-Z_]*:" tests/fixtures/constants.yaml` returns at least 6 (six tracked constants)
    - `grep -q "class ConstantProvenance" tests/fixtures/__init__.py` exits 0
    - `grep -q "def load_constants" tests/fixtures/__init__.py` exits 0
    - `grep -q "ConstantProvenance" tests/fixtures/__init__.py` in __all__ block
    - `uv run python -c "from tests.fixtures import load_constants; c = load_constants(); assert len(c.entries) >= 6"` exits 0
    - `uv run pytest tests/test_constants_provenance.py -v` reports "13 passed" (or equivalent — 6+6+1)
    - `uv run pytest tests/` (full suite) shows NO regressions — same count as before plus 13 new passes
    - `grep -q "SEED-001" tests/test_constants_provenance.py` exits 0 (seed origin cited in test docstring)
    - `grep -q "METHODOLOGY_VERSION" tests/test_constants_provenance.py` exits 0 (remediation message)
    - `grep -q "CHANGES.md" tests/test_constants_provenance.py` exits 0 (remediation message)
    - Drift-proof check: `sed -i.bak 's/CCGT_EFFICIENCY = 0.55/CCGT_EFFICIENCY = 0.56/' src/uk_subsidy_tracker/counterfactual.py && uv run pytest tests/test_constants_provenance.py::test_yaml_value_matches_live 2>&1 | grep -q "Drift detected"; RC=$?; mv src/uk_subsidy_tracker/counterfactual.py.bak src/uk_subsidy_tracker/counterfactual.py; exit $RC` — MUST print "Drift detected" (demonstrating the tripwire fires; test this manually then restore)
  </acceptance_criteria>
  <done>Drift test passes with 13 cases; constants.yaml documents all six live counterfactual constants; `load_constants()` exposed via tests/fixtures/__init__.py; tripwire verified by manual edit/revert cycle.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: CHANGES.md [Unreleased] entry for Wave 0</name>
  <files>CHANGES.md</files>
  <read_first>
    - CHANGES.md (current [Unreleased] section + last released version — mirror Keep-a-Changelog 1.1.0 format already used)
    - .planning/phases/04-publishing-layer/04-CONTEXT.md #### Established Patterns (atomic commits; "CHANGES.md is the log where constants.yaml entries and methodology bumps are recorded")
  </read_first>
  <action>
    Append under `## [Unreleased]` → `### Added` (create the subsection if
    absent, per Keep-a-Changelog 1.1.0):

    ```markdown
    ### Added

    - `pyarrow>=24.0.0` and `duckdb>=1.5.2` added to `pyproject.toml` dependencies. Phase 4 adds Parquet I/O + determinism strip (pyarrow) and DuckDB reference snippets in `docs/data/index.md` + possible `validate()` helper.
    - `tests/fixtures/constants.yaml` — provenance YAML for the six `src/uk_subsidy_tracker/counterfactual.py` constants (SEED-001 Tier 2 scaffold).
    - `tests/fixtures/__init__.py` — `ConstantProvenance`, `Constants`, `load_constants()` alongside existing `BenchmarkEntry` + `load_benchmarks()` (same two-layer Pydantic + YAML + source-key-injection pattern).
    - `tests/test_constants_provenance.py` — drift tripwire: every live uppercase numeric constant on `counterfactual.py` must have a YAML entry with exact-equality value, plus a non-failing `next_audit` overdue-audit warning. Remediation-hook failure message cites `METHODOLOGY_VERSION` + `CHANGES.md ## Methodology versions` (Phase-2 `test_counterfactual.py` template).
    ```

    Do NOT add a `## Methodology versions` entry — `METHODOLOGY_VERSION` stays
    at `"0.1.0"` per pre-existing condition in CONTEXT.md (`Phase 4 does NOT
    bump this`). Bumping is Phase-6-or-later.
  </action>
  <verify>
    <automated>grep -q "pyarrow" CHANGES.md &amp;&amp; grep -q "tests/fixtures/constants.yaml" CHANGES.md &amp;&amp; grep -q "tests/test_constants_provenance.py" CHANGES.md &amp;&amp; grep -q "SEED-001" CHANGES.md</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "^- .*pyarrow" CHANGES.md` returns 1 (one bullet mentioning pyarrow)
    - `grep -q "constants.yaml" CHANGES.md` exits 0
    - `grep -q "test_constants_provenance" CHANGES.md` exits 0
    - `grep -q "SEED-001" CHANGES.md` exits 0 (citation)
    - CHANGES.md has NO new `## Methodology versions` entry (`diff` against HEAD~1 shows `## Methodology versions` section unchanged). METHODOLOGY_VERSION stays `"0.1.0"`.
    - `uv run mkdocs build --strict` passes (CHANGES.md is a doc page; build catches breakage)
  </acceptance_criteria>
  <done>CHANGES.md [Unreleased] records the Wave 0 dep additions + drift test shipment.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| live module → YAML fixture | a regulator-sourced constant edit on `counterfactual.py` crosses into the YAML provenance file via a PR author. This plan makes the crossing observable. |
| PyPI → repo (`uv add`) | new third-party dependencies (`pyarrow`, `duckdb`) land in CI + on developer machines. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-04-01-01 | Tampering | `counterfactual.py` numeric constant silently changed without updating YAML or CHANGES.md | mitigate | `test_yaml_value_matches_live` (exact equality) + remediation-hook failure message citing `METHODOLOGY_VERSION` + `CHANGES.md`. This is the SEED-001 tripwire; the `0.184` → `0.18290` incident motivated it. |
| T-04-01-02 | Tampering | `tests/fixtures/constants.yaml` edited without updating the live constant | mitigate | Same test catches reverse drift — YAML value mismatched to live module fails identically. |
| T-04-01-03 | Tampering | Dependency supply-chain on `pyarrow` or `duckdb` | accept | `uv.lock` pins exact wheel hashes; `uv sync --frozen` refuses any out-of-lock resolution in CI. PyPI hash-verified. Wider supply-chain attack is out of scope for an open-data-only project with no secrets. |
| T-04-01-04 | Information Disclosure | YAML includes licence-restricted or non-public regulator text | accept | All sources used are UK gov open data (gov.uk publications, OBR EFO). `basis` + `notes` free-text fields may paraphrase regulator prose; quoting is short-form per UK Crown Copyright OGL. |
| T-04-01-05 | Repudiation | Which constants are "tracked" may silently drift | mitigate | `_TRACKED` set is an explicit allowlist in the test file — pyright + grep discoverable; adding a new constant without adding to `_TRACKED` means no enforcement, but the missing YAML entry keeps it visible on any new Provenance: docstring. |
</threat_model>

<verification>
Phase-4 Plan 01 verifications (automated, each <60s):

1. `uv run pytest tests/test_constants_provenance.py -v` — 13 passes.
2. `uv run pytest tests/` — full suite green; no regression.
3. `uv run python -c "import pyarrow, duckdb"` — both import cleanly.
4. `grep -q "class ConstantProvenance" tests/fixtures/__init__.py` — loader extended.
5. Drift-proof verification (manual): edit a counterfactual constant, run pytest, see "Drift detected", revert.
6. `uv run mkdocs build --strict` — docs still build (CHANGES.md diff clean).
</verification>

<success_criteria>
- `uv sync --frozen` installs pyarrow≥24.0.0 and duckdb≥1.5.2
- `uv run pytest tests/test_constants_provenance.py -v` reports 13 passed, 0 failed, 0 errors
- `tests/fixtures/constants.yaml` has entries for 6 counterfactual constants
- `tests/fixtures/__init__.py` exports `ConstantProvenance`, `Constants`, `load_constants` via `__all__`
- `CHANGES.md` [Unreleased] section mentions pyarrow + duckdb + constants.yaml + test_constants_provenance
- All pre-existing tests still pass (count matches STATE.md — 23 passed + 4 skipped — plus 13 new passes from this plan)
- `METHODOLOGY_VERSION` in `counterfactual.py` is unchanged (still `"0.1.0"`)
</success_criteria>

<output>
After completion, create `.planning/phases/04-publishing-layer/04-01-SUMMARY.md`
following the standard summary template. Summary must include:
- Number of pre-existing vs new tests (23+4 before → 36+4 after, plus any delta)
- Final pyarrow + duckdb versions resolved in uv.lock (output of `uv pip show`)
- Confirmation that drift tripwire fires on a manual constant edit
- Any Provenance: docstring blocks added to counterfactual.py as SEED-001 Tier 1 precursors
</output>
