---
status: partial
phase: 06-flagship-cross-scheme-charts
source: [06-VERIFICATION.md]
started: 2026-04-25T00:00:00Z
updated: 2026-04-25T00:00:00Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. Homepage 3-card grid + X1 hero rendering
expected: Render docs/index.md in browser; 3 Material grid-cards (£8.0 bn / £0.1 bn / £282) render side-by-side at full width and stack on narrow viewports; italic caveat below; X1 Twitter PNG hero loads inline; Interactive link opens HTML in a new tab.
result: [pending]

### 2. X1 Plotly rangeselector interactive behaviour
expected: Open docs/charts/html/x1_stacked_total.html; 1y / 5y / All rangeselector buttons render along the x-axis; clicking each button changes the visible time window (1y = last 12 months, 5y = last 60 months, All = full series); stacked-by-scheme bands rescale.
result: [pending]

### 3. PORTAL-02 scheme-tile clickthrough
expected: Click the CfD tile on docs/index.md → loads /schemes/cfd/. Click the RO tile → loads /schemes/ro/. Placeholder tiles do not respond to click.
result: [pending]

### 4. SCHEME_COLORS palette consistency across all 5 X-chart PNGs
expected: Across x1..x5_*_twitter.png — CfD elements render blue (#1f77b4); RO elements render red (#d62728); X2 cumulative line uses RO red consistent with single-line pattern; the 2022 emphasis-red on X5 is a distinct year-overlay color, not scheme color.
result: [pending]

### 5. Methodology §7 reference-checks tone audit
expected: Render docs/portal/methodology.md in the served site; §7 Reference checks frames REF Constable and Turver as test-file tolerance anchors with explicit "NOT co-publishers" framing; clinical/dry register; no peer-publisher framing.
result: [pending]

## Summary

total: 5
passed: 0
issues: 0
pending: 5
skipped: 0
blocked: 0

## Gaps
