"""Demo of the dark theme system."""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from uk_subsidy_tracker.plotting import ChartBuilder
from uk_subsidy_tracker.plotting.colors import GENERATION_COLORS
from uk_subsidy_tracker.plotting.theme import register_cfd_dark_theme

# Register theme
register_cfd_dark_theme()

# Create output
output_dir = Path("output/demo")
output_dir.mkdir(parents=True, exist_ok=True)

# Demo: Donut Chart
data = {
    "Wind": 18.4,
    "Gas": 4.9,
    "Solar": 4.8,
    "Nuclear": 5.1,
    "Imports": 3.4,
    "Biomass": 2.3,
}
total_gw = sum(data.values())

builder = ChartBuilder(title="Generation Mix - Today at 09:40", height=600)
fig = builder.create_basic()

fig.add_trace(
    go.Pie(
        labels=list(data.keys()),
        values=list(data.values()),
        hole=0.65,
        marker=dict(
            colors=[GENERATION_COLORS.get(k, "#7f7f7f") for k in data.keys()],
            line=dict(color="#1a1d29", width=2),
        ),
        textinfo="label+percent",
        textposition="outside",
    )
)
fig.add_annotation(
    text=f"<b>Total</b><br><span style='font-size:28px'>{total_gw:.1f} GW</span>",
    x=0.5,
    y=0.5,
    font=dict(size=16, color="#ffffff"),
    showarrow=False,
)

# Save
html_path = output_dir / "generation_mix.html"
fig.write_html(html_path)
print(f"   ✓ HTML: {html_path}")

# Try PNG export
try:
    png_path = output_dir / "generation_mix_twitter.png"
    fig.write_image(png_path, width=1200, height=675, scale=2)
    print(f"   ✓ PNG:  {png_path} (Twitter: 1200x675)")
except Exception as e:
    print(f"   ⚠ PNG export needs kaleido: pip install kaleido")

# Demo 2: Stacked Area Chart
print("\n2. Creating Stacked Area Chart...")
hours = pd.date_range("2024-01-01", periods=48, freq="30min")
df = pd.DataFrame(
    {
        "time": hours,
        "Nuclear": [5.0 + i * 0.02 for i in range(48)],
        "Wind": [10 + (i % 12) * 1.5 for i in range(48)],
        "Gas": [6 - (i % 24) * 0.2 for i in range(48)],
        "Solar": [
            0 if i % 48 < 12 or i % 48 > 36 else (i % 24) * 0.3 for i in range(48)
        ],
    }
)

builder2 = ChartBuilder(title="Generation Over Time - Yesterday/Today", height=500)
fig2 = builder2.create_basic()

for source in ["Nuclear", "Wind", "Gas", "Solar"]:
    fig2.add_trace(
        go.Scatter(
            x=df["time"],
            y=df[source],
            name=source,
            mode="lines",
            line=dict(width=0.5, color=GENERATION_COLORS.get(source, "#7f7f7f")),
            fillcolor=GENERATION_COLORS.get(source, "#7f7f7f"),
            stackgroup="one",
        )
    )

fig2.update_layout(
    yaxis_title="Generation (GW)",
    xaxis=dict(tickformat="%H:%M"),
    hovermode="x unified",
)

html_path2 = output_dir / "generation_timeseries.html"
fig2.write_html(html_path2)
print(f"   ✓ HTML: {html_path2}")

try:
    png_path2 = output_dir / "generation_timeseries_twitter.png"
    fig2.write_image(png_path2, width=1200, height=675, scale=2)
    print(f"   ✓ PNG:  {png_path2}")
except Exception:
    pass

print("\n" + "=" * 60)
print("✓ Demo Complete!")
print("=" * 60)
print(f"\nOpen these files in your browser:")
print(f"  - {html_path}")
print(f"  - {html_path2}")
print("\nThey should have a dark navy theme matching Energy Dashboard UK!")
