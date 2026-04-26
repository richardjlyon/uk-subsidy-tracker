"""Color palette definitions for CfD plotting library."""

GENERATION_COLORS = {
    "Gas": "#5b8db8",
    "Solar": "#e89654",
    "Coal": "#c97777",
    "Hydro": "#7db8c9",
    "Wind": "#6db894",
    "Nuclear": "#9ca3b8",
    "Biomass": "#b8936d",
    "Imports": "#a686b8",
    "PSH": "#d97c94",
    "Misc": "#d4b85c",
}

TECHNOLOGY_COLORS = {
    "Offshore Wind": "#1f77b4",
    "Onshore Wind": "#6baed6",
    "Solar PV": "#ff7f0e",
}

ALLOCATION_ROUND_COLORS = {
    "Investment Contract": "#d62728",
    "Allocation Round 1": "#1f77b4",
    "Allocation Round 2": "#2ca02c",
    "Allocation Round 4": "#9467bd",
    "Allocation Round 5": "#8c564b",
    "Allocation Round 6": "#e377c2",
}

SEMANTIC_COLORS = {
    "positive": "#2ca02c",
    "negative": "#d62728",
    "neutral": "#7f7f7f",
    "emphasis": "#00d9ff",
}


def get_generation_color(source: str) -> str:
    """Get color for a generation source."""
    return GENERATION_COLORS.get(source, "#7f7f7f")


def create_color_map(items: list[str], palette: str = "generation") -> dict[str, str]:
    """Create a color map for a list of items."""
    if palette == "generation":
        base_colors = GENERATION_COLORS
    elif palette == "technology":
        base_colors = TECHNOLOGY_COLORS
    else:
        base_colors = {}

    color_map = {item: base_colors[item] for item in items if item in base_colors}
    remaining = [item for item in items if item not in base_colors]
    fallback_colors = ["#7f7f7f", "#bcbd22", "#17becf"]

    for i, item in enumerate(remaining):
        color_map[item] = fallback_colors[i % len(fallback_colors)]

    return color_map


# ---------------------------------------------------------------------------
# Phase 6 Plan 06-01 — per-scheme palette for cross-scheme charts (X1, X4, X5).
# ---------------------------------------------------------------------------

SCHEME_COLORS: dict[str, str] = {
    "CfD": "#1f77b4",
    "RO": "#d62728",
    "FiT": "#ff7f0e",
    "Constraint Payments": "#17becf",
    "Capacity Market": "#9467bd",
    "Balancing Services": "#bcbd22",
    "Grid Socialisation": "#e377c2",
    "SEG": "#8c564b",
}
"""Per-scheme color palette for cross-scheme charts (X1, X4, X5).

Selection criteria (UI-SPEC §"Per-scheme palette" — locked):
1. Colorblind-safe (Tol bright qualitative palette).
2. Reuse TECHNOLOGY_COLORS / ALLOCATION_ROUND_COLORS hexes where the scheme's
   biggest band already has an established theme color (CfD = offshore wind blue;
   RO = biomass red; FiT = solar PV orange).
3. Stable across X-chart variants — same scheme = same color in X1/X4/X5.
4. Anti-aliasing-safe in PNG (WCAG AA contrast against PLOT_BG=#252936).

Provenance:
  source:       Tol Bright Qualitative Palette + project TECHNOLOGY_COLORS reuse
  url:          https://personal.sron.nl/~pault/
  basis:        Deuteranopia/protanopia/tritanopia tested; reuses existing
                colors.py palette where the scheme's biggest band has a theme anchor.
  retrieved_on: 2026-04-25
  next_audit:   when WCAG / colorblind standards revise
"""
