"""Structural invariants for the Phase-3 docs tree (TRIAGE-01..04, GOV-01).

These tests guard against accidental regressions of the Phase-3 restructure:
- CUT files remain absent
- 5 theme directories exist with index + methodology
- 7 PROMOTE pages exist at correct theme paths
- Each PROMOTE page carries the 6 D-01 section headers
- GOV-01 four-way coverage is grep-verifiable on every PROMOTE page
- mkdocs.yml keeps the validation: block active
"""
from pathlib import Path

DOCS = Path("docs")
THEMES = ["cost", "recipients", "efficiency", "cannibalisation", "reliability"]
PROMOTE_PAGES = [
    "themes/recipients/lorenz.md",
    "themes/recipients/cfd-payments-by-category.md",
    "themes/efficiency/subsidy-per-avoided-co2-tonne.md",
    "themes/cannibalisation/capture-ratio.md",
    "themes/reliability/capacity-factor-seasonal.md",
    "themes/reliability/generation-heatmap.md",
    "themes/reliability/rolling-minimum.md",
]
EXISTING_COST_PAGES = [
    "themes/cost/cfd-dynamics.md",
    "themes/cost/cfd-vs-gas-cost.md",
    "themes/cost/remaining-obligations.md",
]
D01_SECTIONS = [
    "## What the chart shows",
    "## The argument",
    "## Methodology",
    "## Caveats",
    "## Data & code",
    "## See also",
]


def test_cut_files_deleted():
    """TRIAGE-01: scissors.py + bang_for_buck_old.py preserved only in git history."""
    assert not Path("src/uk_subsidy_tracker/plotting/subsidy/scissors.py").exists()
    assert not Path(
        "src/uk_subsidy_tracker/plotting/subsidy/bang_for_buck_old.py"
    ).exists()


def test_all_themes_have_index_and_methodology():
    """TRIAGE-03: 5 theme directories each with index.md + methodology.md."""
    for t in THEMES:
        assert (DOCS / "themes" / t / "index.md").exists()
        assert (DOCS / "themes" / t / "methodology.md").exists()


def test_promote_chart_pages_exist():
    """TRIAGE-02: 7 PROMOTE chart pages at their theme paths."""
    for p in PROMOTE_PAGES:
        assert (DOCS / p).exists(), f"Missing PROMOTE page: {p}"


def test_existing_cost_pages_moved():
    """TRIAGE-03: existing 3 CfD pages live under docs/themes/cost/ (git-mv'd)."""
    for p in EXISTING_COST_PAGES:
        assert (DOCS / p).exists(), f"Missing Cost page: {p}"
    assert not (DOCS / "charts" / "subsidy" / "cfd-dynamics.md").exists()
    assert not (DOCS / "charts" / "index.md").exists()


def test_six_section_template_present_in_promote_pages():
    """TRIAGE-02 (D-01): each PROMOTE page has all 6 canonical H2 sections."""
    for p in PROMOTE_PAGES:
        content = (DOCS / p).read_text(encoding="utf-8")
        for section in D01_SECTIONS:
            assert section in content, f"{p} missing section: {section}"


def test_gov01_four_way_coverage():
    """GOV-01: every PROMOTE page cites source + test + embeds PNG + links methodology."""
    for p in PROMOTE_PAGES:
        content = (DOCS / p).read_text(encoding="utf-8")
        assert "blob/main/src/uk_subsidy_tracker/plotting/" in content, (
            f"{p} missing Python source permalink"
        )
        assert "blob/main/tests/test_" in content, (
            f"{p} missing test permalink"
        )
        assert "charts/html/" in content and "_twitter.png" in content, (
            f"{p} missing PNG embed"
        )
        assert "methodology" in content.lower(), (
            f"{p} missing methodology reference"
        )


def test_mkdocs_validation_block_present():
    """RESEARCH §3: mkdocs.yml promotes nav.omitted_files to warn."""
    mkdocs_yml = Path("mkdocs.yml").read_text(encoding="utf-8")
    assert "validation:" in mkdocs_yml
    assert "omitted_files: warn" in mkdocs_yml
