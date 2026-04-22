"""Scheme-module contract (ARCHITECTURE §6.1).

Every subsidy-scheme module in this project (CfD here; RO, FiT, SEG,
Constraint Payments, Capacity Market, Balancing Services, Grid Socialisation
in later phases) exposes the same five module-level callables plus a
`DERIVED_DIR` Path constant. The `SchemeModule` `typing.Protocol` below
is the compile-/lint-time handshake — duck-typed at import time, checked
at runtime via `isinstance(module, SchemeModule)`.

Why a `typing.Protocol` rather than an abstract base class?

1. Modules cannot subclass an ABC (Python imports modules, not classes).
2. `@runtime_checkable` on a Protocol with only callable members allows
   `isinstance(cfd, SchemeModule)` to succeed — a cheap structural check
   that surfaces missing functions immediately.
3. Every future scheme module is duck-typed the same way — no inheritance
   chain to maintain; `RO-MODULE-SPEC.md` can describe the contract in
   plain terms and the Protocol enforces it.

Contract (verbatim from ARCHITECTURE §6.1):

- `DERIVED_DIR: Path` — where this scheme's derived Parquet lives.
- `upstream_changed() -> bool` — dirty-check used by the daily refresh
  workflow (Phase 4 Plan 05); compares live SHA-256 against sidecar.
- `refresh() -> None` — re-fetch raw sources and update sidecars.
- `rebuild_derived(output_dir: Path | None = None) -> None` — full
  derivation from raw to Parquet; pure function of raw content.
- `regenerate_charts() -> None` — rebuild any chart outputs this scheme
  produces (D-02: charts are a separate concern from derivation).
- `validate() -> list[str]` — sanity checks on derived output; return
  a list of human-readable warnings (empty list = all clean).
"""
from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class SchemeModule(Protocol):
    """ARCHITECTURE §6.1 contract — duck-typed module-level callables."""

    DERIVED_DIR: Path

    def upstream_changed(self) -> bool: ...
    def refresh(self) -> None: ...
    def rebuild_derived(self, output_dir: Path | None = None) -> None: ...
    def regenerate_charts(self) -> None: ...
    def validate(self) -> list[str]: ...


__all__ = ["SchemeModule"]
