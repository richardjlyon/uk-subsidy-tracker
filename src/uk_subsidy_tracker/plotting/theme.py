"""Dark theme configuration for CfD plotting library."""

import plotly.graph_objects as go
import plotly.io as pio

PAPER_BG = "#1a1d29"
PLOT_BG = "#252936"
GRID_COLOR = "#3a3d4a"
TEXT_COLOR = "#e8e8e8"
TITLE_COLOR = "#ffffff"
HOVER_BORDER = "#00d9ff"
FONT_FAMILY = "Inter, -apple-system, sans-serif"


def create_cfd_dark_template() -> go.layout.Template:
    """Create the dark theme template for CfD charts."""
    template = go.layout.Template()

    template.layout = go.Layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(family=FONT_FAMILY, color=TEXT_COLOR, size=12),
        title=dict(
            font=dict(family=FONT_FAMILY, color=TITLE_COLOR, size=20, weight="bold"),
            x=0.05,
            xanchor="left",
        ),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(color=TEXT_COLOR),
            title=dict(font=dict(color=TITLE_COLOR)),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(color=TEXT_COLOR),
            title=dict(font=dict(color=TITLE_COLOR)),
        ),
        hoverlabel=dict(
            bgcolor=PLOT_BG,
            bordercolor=HOVER_BORDER,
            font=dict(family=FONT_FAMILY, size=12, color=TEXT_COLOR),
        ),
        legend=dict(
            bgcolor="rgba(37, 41, 54, 0.8)",
            bordercolor=GRID_COLOR,
            borderwidth=1,
            font=dict(color=TEXT_COLOR),
        ),
    )

    return template


def register_cfd_dark_theme() -> None:
    """Register the cfd_dark template with Plotly."""
    template = create_cfd_dark_template()
    pio.templates["cfd_dark"] = template
    pio.templates.default = "cfd_dark"


def apply_dark_theme(fig: go.Figure) -> go.Figure:
    """Apply the dark theme to an existing figure."""
    fig.update_layout(template="cfd_dark")
    return fig
