<!-- Referenced by .github/workflows/refresh.yml on step failure.
     Rendered as GitHub Issue body via peter-evans/create-issue-from-file@v6.
     Label applied: `refresh-failure`. -->

The daily refresh workflow failed.

**Run:** https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}
**Triggered:** ${{ github.event.schedule || 'manual' }}

Check the run logs for the failing step. Common causes:

- LCCC / Elexon / ONS upstream server returned a non-200 response or changed schema (pandera validation fired in a loader).
- Benchmark floor (`test_lccc_self_reconciliation_floor`) tripped — pipeline divergence from published LCCC calendar-year total exceeded 0.1%.
- `mkdocs build --strict` surfaced a broken link or nav omission.
- Determinism test or schema conformance test failed (pyarrow writer drift, Pydantic schema mismatch, or raw file content drift with unchanged sidecar).

**Label:** `refresh-failure` (distinct from `correction`, which tracks published corrections).

Assign to the maintainer reviewer; re-run after root-cause fix. Do NOT close this issue without a documented resolution.
