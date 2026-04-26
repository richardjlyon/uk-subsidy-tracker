"""Cross-scheme portal chart modules (Phase 6, REQUIREMENTS X-01..X-05).

Each X-chart reads ``data/derived/portal/cross_scheme.parquet`` (Wave 1
substrate) and emits Twitter-PNG + interactive HTML + div HTML via
``ChartBuilder.save()``. UI-SPEC §"Component Inventory" + Copywriting Contract
are the visual contract.

The X1 stacked-total chart implements the locked TWO-figure pattern (D-07):
the Twitter PNG hero is a static all-time view; the interactive HTML carries
native Plotly ``rangeselector`` 1y/5y/All buttons. X2 (cumulative premium) and
X3 (per-household) are single-figure charts.

Chart ``main()`` callables are imported into the orchestrator at
``uk_subsidy_tracker.plotting.__main__`` directly — no auto-discovery.
"""
