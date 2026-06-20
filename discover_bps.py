"""
One-off helper to discover BPS WebAPI variable IDs for the dashboard indicators.

Usage (after putting your key in bps_key.txt or $env:BPS_API_KEY):
    python discover_bps.py
    python discover_bps.py inflasi kemiskinan        # custom keywords

It pages through the national variable catalogue and prints every variable
whose title matches one of the keywords, as:  <var_id>  <title>  [<unit>]

Copy the relevant ids into INDICATORS in update_dashboard.py. Prints only
public catalogue metadata — never the API key.
"""
from __future__ import annotations

import sys

from bps_api import BPSClient

DEFAULT_KEYWORDS = [
    "pertumbuhan ekonomi", "produk domestik bruto", "pdb",   # GDP
    "inflasi",                                                 # inflation
    "pengangguran", "tpt",                                     # unemployment
    "kemiskinan", "penduduk miskin",                           # poverty
    "ekspor", "impor", "neraca perdagangan",                   # trade
]


def main(keywords: list[str]) -> None:
    kws = [k.lower() for k in keywords]
    client = BPSClient()
    print(f"Searching national variable catalogue for: {', '.join(kws)}\n")

    page, pages, hits = 1, 1, 0
    while page <= pages:
        payload = client.list_variables(page=page)
        pagination = payload.get("data", [[], []])
        meta = pagination[0] if isinstance(pagination, list) and pagination else {}
        pages = int(meta.get("pages", 1)) if isinstance(meta, dict) else 1
        rows = pagination[1] if isinstance(pagination, list) and len(pagination) > 1 else []
        for v in rows:
            title = str(v.get("title", ""))
            if any(k in title.lower() for k in kws):
                hits += 1
                unit = v.get("unit", "")
                print(f"  var {v.get('var_id', v.get('val','?')):>6}  {title}"
                      + (f"  [{unit}]" if unit else ""))
        page += 1

    print(f"\nDone. {hits} matching variable(s) across {pages} page(s).")
    if not hits:
        print("No matches — try broader keywords, e.g. 'python discover_bps.py inflasi'.")


if __name__ == "__main__":
    main(sys.argv[1:] or DEFAULT_KEYWORDS)
