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
