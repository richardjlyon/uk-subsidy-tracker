"""Chart builder for creating standardized dark-themed charts.

The ChartBuilder class provides a high-level interface for creating charts
with the dark theme automatically applied, common formatting patterns, and
built-in export to both HTML (for dashboards) and PNG (for Twitter).

Example:
    builder = ChartBuilder(title="My Chart", height=600)
    fig = builder.create_basic()
    # Add your traces...
    builder.format_currency_axis(fig, axis="y", suffix="m")
    paths = builder.save(fig, "my_chart", export_twitter=True)
"""

from pathlib import Path
from typing import Any, Literal

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from cfd_payment import OUTPUT_DIR
from cfd_payment.plotting.colors import (
    ALLOCATION_ROUND_COLORS,
    GENERATION_COLORS,
    SEMANTIC_COLORS,
    TECHNOLOGY_COLORS,
)
from cfd_payment.plotting.theme import register_cfd_dark_theme


class ChartBuilder:
    """Builder class for creating dark-themed charts with common patterns.

    Automatically applies the dark theme and provides helper methods for
    common chart patterns, axis formatting, and export to multiple formats.

    Attributes:
        title: Chart title
        height: Chart height in pixels
        output_dir: Directory for saving charts (defaults to OUTPUT_DIR)
    """

    def __init__(
        self,
        title: str = "",
        height: int = 600,
        output_dir: Path | None = None,
    ):
        """Initialize the chart builder.

        Args:
            title: Chart title
            height: Chart height in pixels
            output_dir: Output directory (defaults to OUTPUT_DIR)
        """
        self.title = title
        self.height = height
        self.output_dir = output_dir or OUTPUT_DIR

        # Auto-register dark theme
        register_cfd_dark_theme()

    # ========================================================================
    # Chart Creation Methods
    # ========================================================================

    def create_basic(self) -> go.Figure:
        """Create a basic single-panel chart with dark theme.

        Returns:
            Figure with dark theme and title/height configured.
        """
        fig = go.Figure()

        # Include info icon in title
        title_with_icon = f"<b>{self.title}</b>&nbsp;&nbsp;&nbsp;<span style='color:#00d9ff; border:2px solid #00d9ff; border-radius:50%; padding:2px 6px; font-size:16px;'>ⓘ</span>"

        fig.update_layout(
            title={
                "text": title_with_icon,
                "subtitle": {
                    "text": "─" * 150,
                    "font": {"size": 8, "color": "#4a5568"},
                },
                "x": 0.05,
                "xanchor": "left",
            },
            height=self.height,
        )

        return fig

    def create_dual_axis(self) -> go.Figure:
        """Create a chart with dual y-axes (secondary_y).

        Useful for showing two different metrics with different scales
        on the same x-axis.

        Returns:
            Figure with secondary y-axis configured.
        """
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Include info icon in title
        title_with_icon = f"<b>{self.title}</b>&nbsp;&nbsp;&nbsp;<span style='color:#00d9ff; border:2px solid #00d9ff; border-radius:50%; padding:2px 6px; font-size:16px;'>ⓘ</span>"

        fig.update_layout(
            title={
                "text": title_with_icon,
                "subtitle": {
                    "text": "─" * 150,
                    "font": {"size": 8, "color": "#4a5568"},
                },
                "x": 0.05,
                "xanchor": "left",
            },
            height=self.height,
        )

        return fig

    def create_subplots(
        self,
        rows: int,
        cols: int,
        subplot_titles: list[str] | None = None,
        shared_xaxes: bool = False,
        shared_yaxes: bool = False,
        vertical_spacing: float = 0.08,
        horizontal_spacing: float = 0.1,
        **kwargs: Any,
    ) -> go.Figure:
        """Create a multi-panel subplot figure.

        Args:
            rows: Number of subplot rows
            cols: Number of subplot columns
            subplot_titles: List of titles for each subplot
            shared_xaxes: Whether to share x-axes across subplots
            shared_yaxes: Whether to share y-axes across subplots
            vertical_spacing: Vertical spacing between subplots (0-1)
            horizontal_spacing: Horizontal spacing between subplots (0-1)
            **kwargs: Additional arguments passed to make_subplots

        Returns:
            Configured subplot figure with dark theme.
        """
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=subplot_titles,
            shared_xaxes=shared_xaxes,
            shared_yaxes=shared_yaxes,
            vertical_spacing=vertical_spacing,
            horizontal_spacing=horizontal_spacing,
            **kwargs,
        )

        # Include info icon in title
        title_with_icon = f"<b>{self.title}</b>&nbsp;&nbsp;&nbsp;<span style='color:#00d9ff; border:2px solid #00d9ff; border-radius:50%; padding:2px 6px; font-size:16px;'>ⓘ</span>"

        fig.update_layout(
            title={
                "text": title_with_icon,
                "subtitle": {
                    "text": "─" * 150,
                    "font": {"size": 8, "color": "#4a5568"},
                },
                "x": 0.05,
                "xanchor": "left",
            },
            height=self.height,
        )

        return fig

    # ========================================================================
    # Formatting Helper Methods
    # ========================================================================

    def format_currency_axis(
        self,
        fig: go.Figure,
        axis: Literal["x", "y"] = "y",
        *,
        suffix: str = "",
        prefix: str = "£",
        tickformat: str = "~g",
        secondary_y: bool = False,
        title: str = "",
        row: int | None = None,
        col: int | None = None,
    ) -> None:
        """Apply currency formatting to an axis.

        Args:
            fig: The figure to modify
            axis: Which axis to format ("x" or "y")
            suffix: Tick suffix (e.g., "m" for millions, "bn" for billions)
            prefix: Tick prefix (default "£")
            tickformat: D3 format string (default "~g" for compact)
            secondary_y: Whether this is a secondary y-axis
            title: Axis title
            row: Subplot row (for subplots)
            col: Subplot column (for subplots)
        """
        update_kwargs = {
            "tickprefix": prefix,
            "ticksuffix": suffix,
            "tickformat": tickformat,
        }

        if title:
            update_kwargs["title_text"] = title

        if row is not None and col is not None:
            update_kwargs["row"] = row
            update_kwargs["col"] = col

        if secondary_y:
            update_kwargs["secondary_y"] = secondary_y

        if axis == "y":
            fig.update_yaxes(**update_kwargs)
        else:
            fig.update_xaxes(**update_kwargs)

    def format_percentage_axis(
        self,
        fig: go.Figure,
        axis: Literal["x", "y"] = "y",
        *,
        decimals: int = 0,
        title: str = "",
        row: int | None = None,
        col: int | None = None,
    ) -> None:
        """Apply percentage formatting to an axis.

        Args:
            fig: The figure to modify
            axis: Which axis to format ("x" or "y")
            decimals: Number of decimal places
            title: Axis title
            row: Subplot row (for subplots)
            col: Subplot column (for subplots)
        """
        tickformat = f".{decimals}%"

        update_kwargs = {
            "tickformat": tickformat,
        }

        if title:
            update_kwargs["title_text"] = title

        if row is not None and col is not None:
            update_kwargs["row"] = row
            update_kwargs["col"] = col

        if axis == "y":
            fig.update_yaxes(**update_kwargs)
        else:
            fig.update_xaxes(**update_kwargs)

    # ========================================================================
    # Color Palette Access
    # ========================================================================

    @staticmethod
    def get_allocation_round_colors() -> dict[str, str]:
        """Get the allocation round color palette.

        Returns:
            Dictionary mapping allocation round names to hex colors.
        """
        return ALLOCATION_ROUND_COLORS

    @staticmethod
    def get_technology_colors() -> dict[str, str]:
        """Get the CfD technology color palette.

        Returns:
            Dictionary mapping technology names to hex colors.
        """
        return TECHNOLOGY_COLORS

    @staticmethod
    def get_generation_colors() -> dict[str, str]:
        """Get the generation source color palette.

        Returns:
            Dictionary mapping generation sources to hex colors.
        """
        return GENERATION_COLORS

    @staticmethod
    def get_semantic_colors() -> dict[str, str]:
        """Get semantic colors (positive, negative, emphasis, etc.).

        Returns:
            Dictionary mapping semantic meanings to hex colors.
        """
        return SEMANTIC_COLORS

    # ========================================================================
    # Save/Export Methods
    # ========================================================================

    def save(
        self,
        fig: go.Figure,
        name: str,
        *,
        export_twitter: bool = False,
        export_html: bool = True,
        export_div: bool = True,
    ) -> dict[str, Path]:
        """Save chart as HTML and/or PNG for Twitter.

        Args:
            fig: The figure to save
            name: Filename (without extension)
            export_twitter: Whether to export PNG for Twitter (1200x675)
            export_html: Whether to export interactive HTML (full page)
            export_div: Whether to export div-only HTML (for markdown embedding)

        Returns:
            Dictionary with paths: {'html': Path, 'twitter': Path, 'div': Path}
        """
        self.output_dir.mkdir(exist_ok=True, parents=True)
        paths = {}

        # Add attribution at bottom right using paper coordinates
        # Increase bottom margin to make room
        margin = fig.layout.margin
        current_b = getattr(margin, "b", None) or 80

        fig.update_layout(
            margin=dict(b=current_b + 30),
            annotations=list(fig.layout.annotations)
            + [
                dict(
                    text="richardlyon.substack.com",
                    xref="paper",
                    yref="paper",
                    x=1.0,  # Right edge of plot area
                    y=0,  # Bottom of plot area
                    xanchor="right",
                    yanchor="top",
                    yshift=-40,  # Push below x-axis labels
                    showarrow=False,
                    font=dict(size=10, color="#9ca3af"),
                )
            ],
        )

        # Export interactive HTML for dashboard
        if export_html:
            html_path = self.output_dir / f"{name}.html"
            fig.write_html(html_path)
            print(f"✓ Saved HTML: {html_path}")
            paths["html"] = html_path

        # Export div-only HTML for markdown embedding (no iframe needed)
        if export_div:
            div_path = self.output_dir / f"{name}.div.html"
            fig.write_html(
                div_path,
                full_html=False,
                include_plotlyjs="cdn",
                div_id=f"chart-{name}",
            )
            print(f"✓ Saved DIV: {div_path}")
            paths["div"] = div_path

        # Export static PNG for Twitter
        if export_twitter:
            try:
                png_path = self.output_dir / f"{name}_twitter.png"
                fig.write_image(
                    png_path,
                    width=1200,
                    height=675,
                    scale=2,
                )
                print(f"✓ Saved Twitter PNG: {png_path} (1200x675)")
                paths["twitter"] = png_path
            except Exception as e:
                print(f"⚠ Could not export PNG: {e}")
                print("  Install kaleido with: pip install kaleido")

        return paths

    def save_multiple_formats(
        self,
        fig: go.Figure,
        name: str,
    ) -> dict[str, Path]:
        """Save chart in multiple formats for different platforms.

        Exports:
        - HTML for interactive dashboards
        - PNG for Twitter (1200x675, 16:9)
        - PNG for presentations (1920x1080, 16:9)

        Args:
            fig: The figure to save
            name: Base filename (without extension)

        Returns:
            Dictionary mapping format names to file paths.
        """
        self.output_dir.mkdir(exist_ok=True, parents=True)
        paths = {}

        # HTML
        html_path = self.output_dir / f"{name}.html"
        fig.write_html(html_path)
        print(f"✓ HTML: {html_path}")
        paths["html"] = html_path

        try:
            # Twitter
            twitter_path = self.output_dir / f"{name}_twitter.png"
            fig.write_image(twitter_path, width=1200, height=675, scale=2)
            print(f"✓ Twitter: {twitter_path} (1200x675)")
            paths["twitter"] = twitter_path

            # Presentation
            presentation_path = self.output_dir / f"{name}_presentation.png"
            fig.write_image(presentation_path, width=1920, height=1080, scale=2)
            print(f"✓ Presentation: {presentation_path} (1920x1080)")
            paths["presentation"] = presentation_path

        except Exception as e:
            print(f"⚠ Could not export PNG: {e}")
            print("  Install kaleido with: pip install kaleido")

        return paths
