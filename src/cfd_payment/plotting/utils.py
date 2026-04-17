"""Common plotting utilities for CfD charts."""

from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from cfd_payment import OUTPUT_DIR

TECHNOLOGY_COLORS = {
    "Offshore Wind": "#1f77b4",
    "Onshore Wind": "#6baed6",
    "Solar PV": "#ff7f0e",
}


def technology_color_map(technologies: list[str]) -> dict[str, str]:
    """Build a stable color map for a list of technologies."""
    palette = px.colors.qualitative.Plotly
    remaining = [t for t in sorted(technologies) if t not in TECHNOLOGY_COLORS]
    color_map = {tech: palette[i % len(palette)] for i, tech in enumerate(remaining)}
    color_map.update({k: v for k, v in TECHNOLOGY_COLORS.items() if k in technologies})
    return color_map


def make_dual_axis_figure() -> go.Figure:
    """Create a figure with a secondary y-axis."""
    return make_subplots(specs=[[{"secondary_y": True}]])


def format_gbp_axis(
    fig: go.Figure,
    *,
    suffix: str = "",
    fmt: str = "~g",
    secondary_y: bool = False,
    title: str = "",
) -> None:
    """Apply £-prefixed formatting to a y-axis."""
    fig.update_yaxes(
        title_text=title,
        tickprefix="£",
        ticksuffix=suffix,
        tickformat=fmt,
        secondary_y=secondary_y,
    )


def save_chart(fig: go.Figure, name: str, output_dir: Path | None = None) -> Path:
    """Write a figure as HTML. Defaults to output/ if no dir given."""
    dest = output_dir or OUTPUT_DIR
    dest.mkdir(exist_ok=True)
    path = dest / f"{name}.html"
    fig.write_html(path)
    print(f"Saved {path}")
    return path
