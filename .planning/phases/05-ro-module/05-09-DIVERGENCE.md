---
status: per-year
phase_origin: 05.2 (close-out 2026-04-25)
covers: tests/test_benchmarks.py::test_ref_constable_ro_reconciliation
machine_readable: tests/fixtures/divergences.yaml
unlock_protocol: |
  Each entry below is xfailed in the parametrised test list via
  tests/fixtures/divergences.yaml. Demote an entry from xfail when:
  (a) for deferred-data-gated rows: the underlying source becomes available
      and values are transcribed into the pipeline;
  (b) for drift-exceeding rows: the root cause is fixed in the
      parser/aggregate model and re-measured drift falls within
      REF_TOLERANCE_PCT.
  Update procedure: remove the entry from divergences.yaml AND from the
  corresponding section below; the test will then run as a hard assertion.
  Do NOT widen REF_TOLERANCE_PCT.
sync_check: tests/test_benchmarks.py::test_divergences_yaml_sync validates
  that divergences.yaml and this file's per-year tables stay in sync.
  If this file and divergences.yaml disagree on which years are xfailed,
  the sync-check test will fail hard.
---

# Phase 05-09 — REF Constable Reconciliation: Per-Year Divergence Record

**Created:** Plan 05-09 executor, 2026-04-23 (original sentinel)
**Narrowed:** Plan 05.2-06 executor, 2026-04-25 (per-year structured entries)
**Status:** Active — 13 years xfailed (see tables below); 9 years pass hard ±3%.

This file replaces the blanket sentinel that xfailed all 22 REF years when
`.planning/phases/05-ro-module/05-09-DIVERGENCE.md` existed. The blanket
sentinel was appropriate while the pipeline had zero data (Phase 5 Plan 09
Option-D stub state). Phase 05.2 reconstructed aggregate-grain data from
publicly-downloadable Ofgem sources; 9 years now pass the hard ±3% block
without any sentinel. The remaining 13 are documented per-year below with
root-cause classification and unlock conditions.

D-14 policy preserved: REF_TOLERANCE_PCT = 3.0 is unchanged.
No tolerance widening has occurred.

---

## Per-year ref_constable divergences

### Deferred-data-gated (5 entries — pipeline produces NaN, no value to compare)

| Year | Scheme year   | REF £bn | Reason                                                                          | Cross-ref      |
|------|---------------|---------|---------------------------------------------------------------------------------|----------------|
| 2002 | SY1 (2002-03) | 0.30    | ROC buyout/recycle prices deferred — no Ofgem-published source found            | backlog 999.2  |
| 2003 | SY2 (2003-04) | 0.40    | Same                                                                            | backlog 999.2  |
| 2004 | SY3 (2004-05) | 0.50    | Same                                                                            | backlog 999.2  |
| 2005 | SY4 (2005-06) | 0.60    | Same                                                                            | backlog 999.2  |
| 2018 | SY17 (2018-19) | 5.90   | Annual report PDF-only — no XLSX dataset companion; explicit deferral per Plan 05.2-02 frontmatter `sy17_disposition` | backlog 999.3  |

### Drift-exceeding ±3% (8 entries — pipeline produces value but reconciliation fails hard block)

| Year | Scheme year    | Pipeline £bn | REF £bn | Drift  | Root-cause hypothesis                                                                                   | Owner          |
|------|----------------|--------------|---------|--------|---------------------------------------------------------------------------------------------------------|----------------|
| 2006 | SY5 (2006-07)  | 0.748        | 0.70    | +6.8%  | 12-year XLSX GB/NI scope vs REF GB-only — early years had small NIRO that may be folded in             | backlog 999.4  |
| 2008 | SY7 (2008-09)  | 1.061        | 1.00    | +6.1%  | Same as 2006                                                                                            | backlog 999.4  |
| 2013 | SY12 (2013-14) | 2.692        | 2.60    | +3.5%  | Borderline — likely rounding artefact at 2013 banding-review boundary                                  | backlog 999.4  |
| 2015 | SY14 (2015-16) | 4.015        | 3.70    | +8.5%  | 2013 banding transition — possible double-count of stations under both old + new banding for SY14 window | backlog 999.4  |
| 2016 | SY15 (2016-17) | 4.319        | 4.50    | -4.0%  | Possibly related to 2013 banding transition tail                                                        | backlog 999.4  |
| 2020 | SY19 (2020-21) | 5.951        | 5.70    | +4.4%  | SY19 ingestion path year-semantics; SY19 has no per-tech generation MWh in source XLSX                 | backlog 999.4  |
| 2021 | SY20 (2021-22) | 5.783        | 6.40    | -9.6%  | Largest negative drift; mutualisation single-row attribution may misalign with REF scope                | backlog 999.4  |
| 2022 | SY21 (2022-23) | 6.108        | 6.40    | -4.6%  | Mutualisation tail / SY21 specific                                                                      | backlog 999.4  |

### Currently passing within ±3% (9 entries — listed for completeness, NOT xfailed)

2007, 2009, 2010, 2011, 2012, 2014, 2017, 2019, 2023.

These 9 years run as hard assertions. If a future pipeline change causes any of
them to drift beyond ±3%, the test fails immediately (D-14 HARD BLOCK).

---

## Unlock procedure (for future maintainers)

To promote a year from xfailed to hard-assertion:

1. Fix the pipeline issue (data transcription for deferred-data-gated, or
   parser/model fix for drift-exceeding).
2. Re-run `uv run pytest tests/test_benchmarks.py -q -k ref_constable`.
3. Confirm the year now passes within ±3%.
4. Remove the entry from `tests/fixtures/divergences.yaml`.
5. Remove the corresponding row from the matching table in this file.
6. Run `uv run pytest tests/test_benchmarks.py -q` again to confirm:
   - The promoted year shows as `passed`, not `xfailed`.
   - The sync-check test `test_divergences_yaml_sync` still passes.
7. Commit with message `fix(05.2): promote ref_constable[YEAR] from xfail to pass`.

Do NOT remove entries from `tests/fixtures/benchmarks.yaml::ref_constable`.
The 9 currently-passing years must continue to run as hard assertions.

---

## Cross-references

- `tests/fixtures/divergences.yaml` — machine-readable xfail map consumed by test
- `tests/fixtures/benchmarks.yaml::ref_constable` — 22 REF Table 1 entries (hard assertions for passing years)
- `tests/test_benchmarks.py::test_ref_constable_ro_reconciliation` — parametrised D-14 hard-block test
- `tests/test_benchmarks.py::test_divergences_yaml_sync` — sync-check between this file and divergences.yaml
- `.planning/ROADMAP.md` backlog 999.2 — SY1-SY4 ROC price primary source
- `.planning/ROADMAP.md` backlog 999.3 — SY17 PDF transcription
- `.planning/ROADMAP.md` backlog 999.4 — per-year drift tightening
- `.planning/phases/05-ro-module/05-CONTEXT.md` D-13 (REF anchor), D-14 (hard block discipline)
