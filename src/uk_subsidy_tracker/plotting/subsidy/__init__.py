"""Subsidy-economics chart modules.

Each sub-module exposes a zero-argument ``main()`` that regenerates a single
chart. The plotting orchestrator in ``uk_subsidy_tracker.plotting.__main__``
imports these ``main`` callables into a master list; no auto-discovery.

Phase 4 D-02 discipline: CfD chart modules (``cfd_*``, ``lorenz``,
``remaining_obligations``, ``subsidy_per_avoided_co2_tonne``, ``bang_for_buck``)
are preserved verbatim from Phase 3. Plan 05-08 adds the four RO analogues
(``ro_dynamics``, ``ro_by_technology``, ``ro_concentration``,
``ro_forward_projection``) as new files alongside — no refactor of CfD.
"""
