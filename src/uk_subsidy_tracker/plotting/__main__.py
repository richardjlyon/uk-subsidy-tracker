"""Entry point for regenerating every chart published on the site.

Invoked as ``python -m uk_subsidy_tracker.plotting``. Each chart's ``main()``
is executed inside a ``try/except`` so one failing chart does not silently
mask the others in CI — the run ends with a summary and a non-zero exit
code listing every failure.

The module body is guarded by ``if __name__ == "__main__":`` so that
accidental imports (e.g. ``from uk_subsidy_tracker.plotting.__main__ import
capture_ratio``) do not trigger a full chart regeneration as a side effect.
"""
import inspect
from pathlib import Path
from typing import Callable

from uk_subsidy_tracker.plotting.cannibalisation.capture_ratio import main as capture_ratio
from uk_subsidy_tracker.plotting.cannibalisation.price_vs_wind import main as price_vs_wind
from uk_subsidy_tracker.plotting.capacity_factor.monthly import main as cf_monthly
from uk_subsidy_tracker.plotting.capacity_factor.seasonal import main as cf_seasonal
from uk_subsidy_tracker.plotting.intermittency.generation_heatmap import main as heatmap
from uk_subsidy_tracker.plotting.intermittency.load_duration import main as load_duration
from uk_subsidy_tracker.plotting.intermittency.rolling_minimum import main as rolling_minimum
from uk_subsidy_tracker.plotting.subsidy.bang_for_buck import main as bang_for_buck
from uk_subsidy_tracker.plotting.subsidy.lorenz import main as lorenz
from uk_subsidy_tracker.plotting.subsidy.cfd_dynamics import main as cfd_dynamics
from uk_subsidy_tracker.plotting.subsidy.cfd_vs_gas_cost import main as cfd_vs_gas_total
from uk_subsidy_tracker.plotting.subsidy.cfd_payments_by_category import (
    main as cfd_payments_by_category,
)
from uk_subsidy_tracker.plotting.subsidy.remaining_obligations import (
    main as remaining_obligations,
)
from uk_subsidy_tracker.plotting.subsidy.ro_by_technology import (
    main as ro_by_technology,
)
from uk_subsidy_tracker.plotting.subsidy.ro_concentration import (
    main as ro_concentration,
)
from uk_subsidy_tracker.plotting.subsidy.ro_dynamics import main as ro_dynamics
from uk_subsidy_tracker.plotting.subsidy.ro_forward_projection import (
    main as ro_forward_projection,
)
from uk_subsidy_tracker.plotting.subsidy.subsidy_per_avoided_co2_tonne import (
    main as subsidy_per_avoided_co2_tonne,
)


def _is_dormant_module(path: Path | str) -> bool:
    """True iff the source file at ``path`` carries '# dormant: true' as literal line 1.

    Grep-discoverable dormancy discipline per Phase 05.2 D-08. Dormant chart
    modules are skipped by the regeneration loop; their output artefacts
    stay absent from docs/charts/html/ until DORMANT_STATION_LEVEL lifts on
    backlog 999.1.
    """
    p = Path(path)
    if not p.exists():
        return False
    with p.open("r", encoding="utf-8") as fh:
        first_line = fh.readline().rstrip("\n")
    return first_line == "# dormant: true"


def main() -> None:
    """Regenerate every published chart, collecting failures for a summary."""
    charts: list[tuple[str, Callable[[], None]]] = [
        # Subsidy economics
        ("cfd_vs_gas_total", cfd_vs_gas_total),
        ("cfd_dynamics", cfd_dynamics),
        ("cfd_payments_by_category", cfd_payments_by_category),
        ("subsidy_per_avoided_co2_tonne", subsidy_per_avoided_co2_tonne),
        ("bang_for_buck", bang_for_buck),
        ("remaining_obligations", remaining_obligations),
        ("lorenz", lorenz),
        # RO subsidy economics (Plan 05-08)
        ("ro_dynamics", ro_dynamics),
        ("ro_by_technology", ro_by_technology),
        ("ro_concentration", ro_concentration),
        ("ro_forward_projection", ro_forward_projection),
        # Capacity factor
        ("cf_monthly", cf_monthly),
        ("cf_seasonal", cf_seasonal),
        # Intermittency
        ("heatmap", heatmap),
        ("load_duration", load_duration),
        ("rolling_minimum", rolling_minimum),
        # Cannibalisation
        ("capture_ratio", capture_ratio),
        ("price_vs_wind", price_vs_wind),
    ]

    failures: list[tuple[str, Exception]] = []
    for name, fn in charts:
        source_path = inspect.getfile(fn)
        if _is_dormant_module(source_path):
            print(f"SKIP {name}: dormant chart module (# dormant: true on line 1)")
            continue
        try:
            fn()
            print(f"OK  {name}")
        except Exception as e:  # noqa: BLE001 — CI needs to see every failure
            print(f"ERR {name}: {e}")
            failures.append((name, e))

    if failures:
        raise SystemExit(
            f"{len(failures)} chart(s) failed: "
            + ", ".join(n for n, _ in failures)
        )


if __name__ == "__main__":
    main()
