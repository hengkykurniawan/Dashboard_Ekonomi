"""
Inspect specific BPS variables to confirm the right id + turvar before wiring
them into update_dashboard.py.

Usage:
    python probe_bps.py 1 526 2100      # inspect these var ids

For each variable it prints: title, the turvar (measure) options, the year
range, the vervar (region) options, and the last few national values for each
turvar — so you can match against known headline figures.
"""
from __future__ import annotations

import sys

from bps_api import BPSClient, parse_series


def recent_th(client: BPSClient, var: str, years: int = 3) -> str:
    """Return a semicolon list of the most recent `years` BPS period ids."""
    payload = client.periods(var)
    data = payload.get("th") or payload.get("data") or []
    rows = data[1] if isinstance(data, list) and len(data) > 1 else data
    ids = [str(r["th_id"]) for r in rows][:years]
    return ";".join(ids) if ids else "0"


def probe(client: BPSClient, var: str) -> None:
    try:
        th = recent_th(client, var)
        p = client.data(var, th=th)
    except Exception as e:
        print(f"var {var}: ERROR {e}\n")
        return
    vlist = p.get("var", [])
    title = vlist[0]["label"] if vlist else "?"
    turvars = p.get("turvar", [])
    vervars = p.get("vervar", [])
    years = p.get("tahun", [])
    print(f"== var {var}: {title}")
    print(f"   years: {years[0]['label'] if years else '?'} .. {years[-1]['label'] if years else '?'}"
          f"  ({len(years)} yrs)")
    print(f"   vervar (regions): {len(vervars)} -> "
          + ", ".join(f"{v['val']}:{v['label']}" for v in vervars[:4])
          + (" ..." if len(vervars) > 4 else ""))
    print(f"   turvar (measures): "
          + (", ".join(f"{t['val']}:{t['label']}" for t in turvars) if turvars else "(none / '0')"))
    for t in (turvars or [{"val": "0", "label": "default"}]):
        series = parse_series(p, turvar=str(t["val"]))
        tail = series[-4:]
        shown = "  ".join(f"{lbl}={val:g}" for _, _, lbl, val in tail)
        print(f"     [{t['val']}] {t['label']}: {shown or '(no national rows)'}")
    print()


def main(varids: list[str]) -> None:
    if not varids:
        sys.exit("Pass one or more var ids, e.g. python probe_bps.py 1 526")
    client = BPSClient()
    for v in varids:
        probe(client, v)


if __name__ == "__main__":
    main(sys.argv[1:])
