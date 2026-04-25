# dormant: true
"""RO forward projection — per-station accreditation-end anchor (Plan 05-05 Task 3).

Implements the RESEARCH §6 Option (c) extrapolation:

- Per-station accreditation_end_year = ``expected_end_date.year`` if present,
  else ``accreditation_date.year + 20``, else the scheme close year 2037.
- 2037 is the hard cap (20-year accreditations commencing by 2017-03-31).
- Per-station avg_annual_generation = historical sum / distinct years metered.
- For each projected calendar year (current_year_anchor + 1 ... 2037),
  collect stations whose accreditation_end_year ≥ y, group by technology,
  and project:
      remaining_committed_mwh = sum(avg_annual_mwh)
      remaining_cost_gbp      = mwh × avg_banding_factor × (buyout + recycle)[latest_oy]
      station_count_active    = count of stations in the group
      avg_banding_factor      = generation-weighted mean banding from the last
                                three years of station_month.parquet; falls back
                                to 1.0 if station_month is absent (Wave-2 bootstrap).

Determinism discipline (D-21):
- ``current_year_anchor = int(gen['output_period_end'].max().year)`` — NEVER
  ``pd.Timestamp.now().year`` (the latter breaks ``test_determinism``).
- Column order = ``RoForwardProjectionRow`` field declaration order (D-10).

RO scheme closes 2037-03-31 for 20-year accreditations starting 2017-03-31.

Dormancy:
    This module is dormant per Phase 05.2 (RO Data Reconstruction — Aggregate
    Grain). Station-level code paths are preserved in-tree but not exercised
    by the aggregate pipeline (schemes.ro.DORMANT_STATION_LEVEL = True).
    Re-activated on backlog 999.1 (Credentialed RER Access Automation) by
    flipping DORMANT_STATION_LEVEL to False and removing the per-test
    @pytest.mark.dormant marks.

    Design note: .planning/notes/ro-data-strategy-option-a1.md
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.data.ofgem_ro import (
    load_ofgem_ro_generation,
    load_ofgem_ro_register,
)
from uk_subsidy_tracker.data.roc_prices import load_roc_prices
from uk_subsidy_tracker.schemas.ro import RoForwardProjectionRow, emit_schema_json
from uk_subsidy_tracker.schemes.cfd.cost_model import _write_parquet

_RO_SCHEME_CLOSE_YEAR = 2037


def _empty_forward_projection() -> pd.DataFrame:
    """Return an empty DataFrame with the canonical forward_projection schema."""
    return pd.DataFrame(
        {
            "year": pd.Series([], dtype="int64"),
            "technology": pd.Series([], dtype="object"),
            "remaining_committed_mwh": pd.Series([], dtype="float64"),
            "remaining_cost_gbp": pd.Series([], dtype="float64"),
            "station_count_active": pd.Series([], dtype="int64"),
            "avg_banding_factor": pd.Series([], dtype="float64"),
        }
    )


def build_forward_projection(output_dir: Path) -> pd.DataFrame:
    """Build ``forward_projection.parquet`` — 2026→2037 drawdown by technology."""
    gen = load_ofgem_ro_generation()
    reg = load_ofgem_ro_register()
    prices = load_roc_prices()

    # Empty-input bootstrap: zero-row stubs produce an empty, schema-correct
    # Parquet so downstream tests can still assert file presence.
    if len(gen) == 0 or len(reg) == 0:
        df = _empty_forward_projection()
        df["methodology_version"] = METHODOLOGY_VERSION
        columns = list(RoForwardProjectionRow.model_fields.keys())
        df = (
            df[columns]
            .sort_values(["year", "technology"], kind="mergesort")
            .reset_index(drop=True)
        )
        _write_parquet(df, output_dir / "forward_projection.parquet")
        emit_schema_json(
            RoForwardProjectionRow, output_dir / "forward_projection.schema.json"
        )
        return df

    # Deterministic current-year anchor (D-21).
    current_year_anchor = int(pd.to_datetime(gen["output_period_end"]).max().year)

    # ------------------------------------------------------------
    # Per-station accreditation_end_year (2037 hard cap).
    # ------------------------------------------------------------
    reg = reg.copy()

    def _end_year(row) -> int:
        eed = row.get("expected_end_date")
        if pd.notna(eed):
            return int(pd.Timestamp(eed).year)
        ad = row.get("accreditation_date")
        if pd.notna(ad):
            return int(pd.Timestamp(ad).year) + 20
        return _RO_SCHEME_CLOSE_YEAR

    reg["accreditation_end_year"] = (
        reg.apply(_end_year, axis=1).astype("int64").clip(upper=_RO_SCHEME_CLOSE_YEAR)
    )

    # ------------------------------------------------------------
    # Per-station historical avg annual generation.
    # ------------------------------------------------------------
    gen = gen.copy()
    gen["year"] = pd.to_datetime(gen["output_period_end"]).dt.year
    per_year = (
        gen.groupby(["station_id", "year"], sort=True, observed=True)["generation_mwh"]
        .sum()
        .reset_index()
    )
    station_annual = (
        per_year.groupby("station_id", sort=True, observed=True)["generation_mwh"]
        .mean()
        .rename("avg_annual_mwh")
        .reset_index()
    )

    stations = reg.merge(station_annual, on="station_id", how="left")
    stations["avg_annual_mwh"] = stations["avg_annual_mwh"].fillna(0.0)
    if "technology_type" in stations.columns:
        stations = stations.rename(columns={"technology_type": "technology"})

    # ------------------------------------------------------------
    # Latest ROC price (most recent obligation year in roc-prices.csv).
    # Falls back to 0.0 if prices table is empty (smoke context).
    # ------------------------------------------------------------
    if len(prices) == 0:
        latest_price_per_roc = 0.0
    else:
        latest_prices = prices.sort_values("obligation_year").tail(1).iloc[0]
        latest_price_per_roc = float(
            float(latest_prices.get("buyout_gbp_per_roc", 0.0) or 0.0)
            + float(latest_prices.get("recycle_gbp_per_roc", 0.0) or 0.0)
        )

    # ------------------------------------------------------------
    # Per-technology avg_banding_factor from the last 3 years of
    # station_month.parquet (generation-weighted). Falls back to 1.0
    # if station_month.parquet is absent (Wave-2 bootstrap edge).
    # ------------------------------------------------------------
    tech_banding: dict[str, float] = {}
    sm_path = output_dir / "station_month.parquet"
    if sm_path.exists():
        try:
            sm = pq.read_table(
                sm_path,
                columns=["technology", "month_end", "banding_factor_yaml", "generation_mwh"],
            ).to_pandas()
        except Exception:
            sm = pd.DataFrame()
        if len(sm) > 0:
            sm["year"] = pd.to_datetime(sm["month_end"]).dt.year
            recent_cutoff = int(sm["year"].max()) - 2  # last 3 complete years
            recent = sm[sm["year"] >= recent_cutoff].copy()
            # Drop rows with NaN banding (no lookup) to keep the weighted mean
            # honest; zero-generation rows contribute zero weight and drop out.
            recent = recent.dropna(subset=["banding_factor_yaml"])
            for tech, g in recent.groupby("technology", observed=True):
                weights = g["generation_mwh"].astype(float)
                if weights.sum() > 0:
                    tech_banding[str(tech)] = float(
                        (g["banding_factor_yaml"].astype(float) * weights).sum()
                        / weights.sum()
                    )

    # ------------------------------------------------------------
    # Year × technology projection (current_year_anchor + 1 .. 2037).
    # ------------------------------------------------------------
    rows = []
    for y in range(current_year_anchor + 1, _RO_SCHEME_CLOSE_YEAR + 1):
        active = stations[stations["accreditation_end_year"] >= y]
        if active.empty:
            continue
        for tech, sub in active.groupby("technology", sort=True, observed=True):
            mwh = float(sub["avg_annual_mwh"].sum())
            station_count = int(len(sub))
            avg_bf = float(tech_banding.get(str(tech), 1.0))
            rows.append(
                {
                    "year": int(y),
                    "technology": tech,
                    "remaining_committed_mwh": mwh,
                    "remaining_cost_gbp": mwh * avg_bf * latest_price_per_roc,
                    "station_count_active": station_count,
                    "avg_banding_factor": avg_bf,
                }
            )

    df = pd.DataFrame(rows) if rows else _empty_forward_projection()
    df["methodology_version"] = METHODOLOGY_VERSION

    columns = list(RoForwardProjectionRow.model_fields.keys())
    df = (
        df[columns]
        .sort_values(["year", "technology"], kind="mergesort")
        .reset_index(drop=True)
    )

    _write_parquet(df, output_dir / "forward_projection.parquet")
    emit_schema_json(
        RoForwardProjectionRow, output_dir / "forward_projection.schema.json"
    )
    return df
