"""RO banding-factor table (technology x commissioning-window x country) Pydantic loader.

The bandings table encodes ROC-issuance multipliers per the Renewables Obligation Order 2009
(SI 2009/785) + 6 amendment SIs (2011/2704, 2013/768, 2015/920, 2016/745, 2017/1084).

Per CONTEXT D-01 the authoritative ``rocs_issued`` source is Ofgem's published
``ROCs_Issued`` column; this YAML table is used as an AUDIT CROSS-CHECK in
``schemes/ro/cost_model.py``. Divergence between Ofgem-published and YAML-computed rocs
triggers a per-station warning via ``schemes/ro/validate()`` per D-04 Check 1.

Two-layer Pydantic + YAML pattern from Phase 2 D-07 (``lccc.py`` as reference analog).

Provenance: every entry MUST declare ``source`` (SI reference), ``url``, ``basis``,
``retrieved_on``.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, HttpUrl


class RoBandingEntry(BaseModel):
    """One (technology x commissioning-window x country) banding cell."""

    technology: str = Field(description="Ofgem technology_type string (verbatim)")
    country: str = Field(description="'GB' or 'NI'")
    commissioning_window_start: date | None = Field(
        default=None,
        description="None = pre-banding / grandfathered anchor",
    )
    commissioning_window_end: date | None = Field(
        default=None,
        description="None = open-ended window",
    )
    banding_factor: float = Field(description="ROCs/MWh issued for this cell")
    chp: bool = Field(default=False, description="CHP variant of the technology")
    grandfathered: bool = Field(
        default=False,
        description="Pre-2006-07-11 accreditation 1-ROC/MWh rule override",
    )

    # Provenance block (constant-provenance pattern per user memory).
    source: str = Field(description='Regulator citation, e.g. "SI 2009/785 Schedule 2"')
    url: HttpUrl = Field(description="Stable legislation.gov.uk or Ofgem URL")
    basis: str = Field(description="Methodological basis")
    retrieved_on: date = Field(description="ISO-8601 retrieval date")
    next_audit: date | None = Field(
        default=None, description="Optional re-audit anchor"
    )


class RoBandingTable(BaseModel):
    """Collection of :class:`RoBandingEntry` rows with a lookup helper."""

    entries: list[RoBandingEntry]

    def lookup(
        self,
        technology: str,
        country: str,
        commissioning_date: date,
        chp: bool = False,
    ) -> float:
        """Return ``banding_factor`` for a station's (technology, country, window) cell.

        Raises :class:`KeyError` if no cell matches. Matches the first entry where:

        - ``technology == entry.technology``
        - ``country == entry.country``
        - ``commissioning_date`` in ``[entry.commissioning_window_start,
          entry.commissioning_window_end]``
        - ``chp == entry.chp``

        Grandfathering override: if ``commissioning_date < 2006-07-11``, a
        ``grandfathered=True`` entry with ``banding_factor=1.0`` takes precedence for
        that ``(technology, country)`` tuple.
        """
        # Grandfathering short-circuit
        grandfathering_anchor = date(2006, 7, 11)
        if commissioning_date < grandfathering_anchor:
            for e in self.entries:
                if (
                    e.grandfathered
                    and e.technology == technology
                    and e.country == country
                ):
                    return e.banding_factor

        for e in self.entries:
            if e.technology != technology:
                continue
            if e.country != country:
                continue
            if e.chp != chp:
                continue
            if e.grandfathered:
                # Grandfathered rows only match in the pre-2006-07-11 short-circuit above.
                continue
            start_ok = (
                e.commissioning_window_start is None
                or commissioning_date >= e.commissioning_window_start
            )
            end_ok = (
                e.commissioning_window_end is None
                or commissioning_date <= e.commissioning_window_end
            )
            if start_ok and end_ok:
                return e.banding_factor

        raise KeyError(
            f"No banding for technology={technology!r}, country={country!r}, "
            f"commissioning_date={commissioning_date.isoformat()}, chp={chp}. "
            f"Check src/uk_subsidy_tracker/data/ro_bandings.yaml coverage."
        )


def load_ro_bandings(config_path: str = "ro_bandings.yaml") -> RoBandingTable:
    """Load and validate the RO bandings YAML.

    Path resolution matches ``lccc.py``: relative paths resolve against this module's
    directory (``src/uk_subsidy_tracker/data/``).
    """
    default_dir = Path(__file__).parent
    path = (
        default_dir / config_path
        if not Path(config_path).is_absolute()
        else Path(config_path)
    )
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    return RoBandingTable(**raw)
