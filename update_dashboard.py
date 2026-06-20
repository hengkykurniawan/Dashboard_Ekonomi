"""
Refresh data.json for the Indonesia Economic Dashboard from live sources.

Strategy: load the committed data.json as a BASE, then overlay any value we
successfully fetch. Anything that fails to fetch keeps its last-known value, so
the dashboard never regresses to blank on a transient API/network error.

Sources:
  - BPS WebAPI    -> GDP, inflation, unemployment, poverty, trade  (needs BPS_API_KEY)
  - Bank Indonesia -> BI-Rate, Rupiah/US$ (JISDOR)                 (monetary, Phase 2)

Run:
    python update_dashboard.py            # fetch + write data.json
    python update_dashboard.py --dry-run  # fetch + print, do not write
    python update_dashboard.py --verbose
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

from bps_api import BPSClient, parse_series

DATA_FILE = Path(__file__).with_name("data.json")

# ---------------------------------------------------------------------------
# Validated BPS mappings (each confirmed against the known headline figure).
#   var/turvar/vervar : national series selector
#   ptype             : period type to keep — Q(uarter) | M(onth) | S(emester)
#   kind              : value format — "percent" | "usd_b" (source is US$ million)
#   good              : which direction is "good" (drives green/red) — "up"|"down"
#   compare           : periods back for the change calc (4=YoY quarter, 1=prev
#                       month, 2=same semester last year)
# ---------------------------------------------------------------------------
INDICATORS = {
    "gdp":          dict(var=104,  turvar="5", vervar="99003", ptype="Q", kind="percent", good="up",
                         compare=4, chart="gdp_quarterly",     field="growth", points=9),
    "inflation":    dict(var=2249, turvar="0", vervar="151",   ptype="M", kind="percent", good="down",
                         compare=1, chart="inflation_monthly", field="yoy",    points=9),
    "unemployment": dict(var=543,  turvar="0", vervar="9999",  ptype="M", kind="percent", good="down",
                         compare=2, chart=None,                field=None,     points=0),
    "poverty":      dict(var=184,  turvar="0", vervar="3",     ptype="S", kind="percent", good="down",
                         compare=2, chart="poverty",           field="rate",   points=5),
}
# Trade is special: three variables feed one chart + the balance KPI.
TRADE = dict(exports=196, imports=497, balance=498, vervar="9999", turvar="0", points=5)

ID_MONTHS = {
    "januari": "Jan", "februari": "Feb", "maret": "Mar", "april": "Apr",
    "mei": "May", "juni": "Jun", "juli": "Jul", "agustus": "Aug",
    "september": "Sep", "oktober": "Oct", "november": "Nov", "desember": "Dec",
}
ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4}


def log(msg: str) -> None:
    print(msg, flush=True)


def load_base() -> dict:
    if not DATA_FILE.exists():
        sys.exit(f"Base {DATA_FILE.name} not found — cannot merge.")
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def kpi_index(data: dict) -> dict:
    return {k["key"]: k for k in data.get("kpis", [])}


def classify_period(label: str):
    """Map a BPS period label to (period_human, chart_label, ptype) or None to skip."""
    low = label.lower()
    year = next((p for p in re.findall(r"\d{4}", label)), None)
    if not year or "tahunan" in low:        # skip annual roll-ups
        return None
    yy = year[-2:]
    if "triwulan" in low:
        toks = low.split()
        i = toks.index("triwulan")
        rn = ROMAN.get(toks[i + 1]) if i + 1 < len(toks) else None
        return (f"Q{rn} {year}", f"Q{rn}-{yy}", "Q") if rn else None
    if "semester" in low:
        m = re.search(r"\(([^)]+)\)", label)
        mon = ID_MONTHS.get(m.group(1).strip().lower()) if m else None
        return (f"{mon} {year}", f"{mon}-{yy}", "S") if mon else None
    for p in low.split():
        if p in ID_MONTHS:
            mon = ID_MONTHS[p]
            return (f"{mon} {year}", f"{mon}-{yy}", "M")
    return None


def fmt_value(value: float, kind: str) -> str:
    if kind == "percent":
        return f"{value:.2f}%"
    if kind == "usd_b":                       # source is US$ million
        b = value / 1000.0
        return f"{'+' if b >= 0 else '−'}${abs(b):.2f}B"
    return str(value)


def arrow(delta: float) -> str:
    return "▲" if delta > 0 else "▼" if delta < 0 else "▬"


def direction(delta: float, good: str) -> str:
    if good == "up":
        return "positive" if delta >= 0 else "negative"
    return "positive" if delta <= 0 else "negative"


def collect_points(client: BPSClient, var, turvar, vervar, ptype):
    """Return chronological [(period_human, chart_label, value), ...] for one variable."""
    payload = client.data(var, th=client.recent_th(var))
    out = []
    for _y, _s, label, val in parse_series(payload, turvar=turvar, vervar=vervar):
        c = classify_period(label)
        if c and c[2] == ptype:
            out.append((c[0], c[1], val))
    return out


def update_bps(data: dict, verbose: bool) -> list[str]:
    warnings: list[str] = []
    client = BPSClient()
    kpis = kpi_index(data)

    for key, cfg in INDICATORS.items():
        try:
            pts = collect_points(client, cfg["var"], cfg["turvar"], cfg["vervar"], cfg["ptype"])
            if not pts:
                warnings.append(f"BPS:{key}: empty series — preserved.")
                continue
            period, _lbl, value = pts[-1]
            kpis[key]["value"] = fmt_value(value, cfg["kind"])
            kpis[key]["period"] = period
            off = cfg["compare"]
            if len(pts) > off:
                pp, _pl, pv = pts[-1 - off]
                delta = value - pv
                kpis[key]["change"] = f"{arrow(delta)} {'+' if delta >= 0 else '−'}{abs(delta):.2f} pp vs {pp} ({pv:.2f}%)"
                kpis[key]["dir"] = direction(delta, cfg["good"])
            if cfg["chart"] and cfg["field"]:
                tail = pts[-cfg["points"]:]
                ch = data["charts"].setdefault(cfg["chart"], {})
                ch["labels"] = [p[1] for p in tail]
                ch[cfg["field"]] = [round(p[2], 2) for p in tail]
            if verbose:
                log(f"BPS:{key}: {kpis[key]['value']} @ {period}  ({len(pts)} periods)")
        except Exception as e:
            warnings.append(f"BPS:{key}: {e} — preserved.")

    # ---- trade: exports + imports + balance ----
    try:
        ex = collect_points(client, TRADE["exports"], TRADE["turvar"], TRADE["vervar"], "M")
        im = collect_points(client, TRADE["imports"], TRADE["turvar"], TRADE["vervar"], "M")
        ba = collect_points(client, TRADE["balance"], TRADE["turvar"], TRADE["vervar"], "M")
        if ex and im and ba:
            n = TRADE["points"]
            labels = [p[1] for p in ba[-n:]]
            ch = data["charts"].setdefault("trade_monthly", {})
            ch["labels"] = labels
            ch["exports"] = [round(p[2] / 1000.0, 2) for p in ex[-n:]]
            ch["imports"] = [round(p[2] / 1000.0, 2) for p in im[-n:]]
            ch["balance"] = [round(p[2] / 1000.0, 2) for p in ba[-n:]]
            period, _lbl, bal = ba[-1]
            kpis["trade"]["value"] = fmt_value(bal, "usd_b")
            kpis["trade"]["period"] = period
            if len(ba) > 1:
                pp, _pl, pv = ba[-2]
                delta = bal - pv
                kpis["trade"]["change"] = f"{arrow(delta)} from {fmt_value(pv, 'usd_b')} in {pp}"
                kpis["trade"]["dir"] = direction(delta, "up")
            if verbose:
                log(f"BPS:trade: {kpis['trade']['value']} @ {period}  (exp {ch['exports'][-1]}B / imp {ch['imports'][-1]}B)")
        else:
            warnings.append("BPS:trade: incomplete export/import/balance series — preserved.")
    except Exception as e:
        warnings.append(f"BPS:trade: {e} — preserved.")

    return warnings


def update_monetary(data: dict, verbose: bool) -> list[str]:
    """
    Bank Indonesia BI-Rate + JISDOR.

    Phase 2 (next): BI has no clean JSON API, so this will scrape the BI
    statistics / JISDOR pages. Until then, monetary values are preserved.
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
