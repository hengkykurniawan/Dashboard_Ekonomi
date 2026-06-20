"""
Refresh data.json for the Indonesia Economic Dashboard from live sources.

Strategy: load the committed data.json as a BASE, then overlay any value we
successfully fetch. Anything that fails to fetch keeps its last-known value, so
the dashboard never regresses to blank on a transient API/network error.

Sources:
  - BPS WebAPI   -> GDP, inflation, unemployment, poverty, trade   (needs BPS_API_KEY)
  - Bank Indonesia -> BI-Rate, Rupiah/US$ (JISDOR)                  (monetary, Phase 2)

Run:
    python update_dashboard.py            # fetch + write data.json
    python update_dashboard.py --dry-run  # fetch + print, do not write
    python update_dashboard.py --verbose
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from bps_api import BPSClient, parse_series

DATA_FILE = Path(__file__).with_name("data.json")

# ---------------------------------------------------------------------------
# BPS variable mapping.
#
# Fill `var` with the ids reported by `python discover_bps.py` (Phase 2). Any
# indicator left with var=None is SKIPPED — its values are preserved from the
# existing data.json. This lets the pipeline ship now and light up per indicator.
#
#   kind:    how to format the headline value ("percent" | "usd_b" | "rupiah")
#   turvar:  derived-variable id within the BPS variable (usually "0")
#   chart:   which data.charts.<key> series this indicator feeds
#   points:  how many trailing periods to keep in the chart
# ---------------------------------------------------------------------------
INDICATORS = {
    "gdp":          {"var": None, "turvar": "0", "kind": "percent", "chart": "gdp_quarterly",     "field": "growth",  "points": 9},
    "inflation":    {"var": None, "turvar": "0", "kind": "percent", "chart": "inflation_monthly", "field": "yoy",     "points": 9},
    "unemployment": {"var": None, "turvar": "0", "kind": "percent", "chart": None,                "field": None,      "points": 0},
    "poverty":      {"var": None, "turvar": "0", "kind": "percent", "chart": "poverty",           "field": "rate",    "points": 5},
    "trade":        {"var": None, "turvar": "0", "kind": "usd_b",   "chart": "trade_monthly",     "field": "balance", "points": 5},
}


def log(msg: str) -> None:
    print(msg, flush=True)


def load_base() -> dict:
    if not DATA_FILE.exists():
        sys.exit(f"Base {DATA_FILE.name} not found — cannot merge.")
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def kpi_index(data: dict) -> dict:
    return {k["key"]: k for k in data.get("kpis", [])}


def fmt_value(value: float, kind: str) -> str:
    if kind == "percent":
        return f"{value:.2f}%"
    if kind == "usd_b":
        return f"{'+' if value >= 0 else ''}${value:.2f}B"
    if kind == "rupiah":
        return f"Rp{value:,.0f}"
    return str(value)


def update_bps(data: dict, verbose: bool) -> list[str]:
    """Overlay BPS indicators onto `data`. Returns a list of warnings."""
    warnings: list[str] = []
    configured = {k: c for k, c in INDICATORS.items() if c["var"] is not None}
    if not configured:
        return ["BPS: no variable ids configured yet (run discover_bps.py — Phase 2). "
                "All BPS values preserved from existing data.json."]

    client = BPSClient()
    kpis = kpi_index(data)
    for key, cfg in configured.items():
        try:
            payload = client.data(cfg["var"])
            series = parse_series(payload, turvar=cfg.get("turvar", "0"))
            if not series:
                warnings.append(f"BPS:{key}: empty series for var {cfg['var']} — preserved.")
                continue
            latest = series[-1]
            value_str = fmt_value(latest[3], cfg["kind"])
            if key in kpis:
                kpis[key]["value"] = value_str
                kpis[key]["period"] = latest[2]
            if cfg.get("chart") and cfg.get("field"):
                pts = series[-cfg["points"]:]
                chart = data["charts"].setdefault(cfg["chart"], {})
                chart["labels"] = [p[2] for p in pts]
                chart[cfg["field"]] = [round(p[3], 2) for p in pts]
            if verbose:
                log(f"BPS:{key}: {value_str} @ {latest[2]} ({len(series)} periods)")
        except Exception as e:  # one bad indicator must not sink the run
            warnings.append(f"BPS:{key}: {e} — preserved.")
    return warnings


def update_monetary(data: dict, verbose: bool) -> list[str]:
    """
    Bank Indonesia BI-Rate + JISDOR.

    Phase 2: BI has no clean JSON API, so this will fetch from the BI statistics
    pages / JISDOR endpoint once that source is wired in. Until then, monetary
    values are preserved from the existing data.json.
    """
    return ["Monetary (BI-Rate, JISDOR): source not wired yet (Phase 2) — preserved."]


def main() -> int:
    ap = argparse.ArgumentParser(description="Refresh data.json from BPS + Bank Indonesia.")
    ap.add_argument("--dry-run", action="store_true", help="fetch but do not write data.json")
    ap.add_argument("--verbose", action="store_true", help="print each fetched value")
    args = ap.parse_args()

    data = load_base()
    warnings = update_bps(data, args.verbose) + update_monetary(data, args.verbose)

    today = dt.date.today().isoformat()
    data.setdefault("meta", {})
    data["meta"]["generated_at"] = today
    data["meta"]["generator"] = "update_dashboard.py"

    for w in warnings:
        log(f"  ! {w}")

    if args.dry_run:
        log("\n--dry-run: data.json NOT written.")
        return 0

    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log(f"\nWrote {DATA_FILE.name} ({today}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
