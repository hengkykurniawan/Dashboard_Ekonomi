# Phase 2 — wiring the live BPS / Bank Indonesia fetch

Status: **infrastructure live, fetch mapping in progress.**

The daily pipeline runs today in **preserve mode** (no `var` ids set in
`update_dashboard.py` → every value is kept from the committed `data.json`, so
the dashboard never publishes wrong/blank numbers). This file records the
confirmed BPS WebAPI mechanics so the per-indicator wiring is quick to finish.

## Confirmed API facts

- **Data endpoint requires `th`** (period): `.../var/{id}/th/{ids}/key/...`.
  `th` ids are `year - 1900` → 2026=`126`, 2025=`125`, … (list via
  `BPSClient.periods(var)`).
- **National row = `vervar` `9999` ("INDONESIA")**, always last in the list.
  `parse_series(payload, turvar=..., vervar="9999")` returns the national
  series. (Default `vervar=None` already picks the last row = national.)
- Inflation is **city-level** and split by measure into **separate variables**:
  - `var 1` = *Inflasi Bulanan (M-to-M)*. National May 2026 = **0.28%** ✓
    (matches the dashboard's stated m-t-m figure).
  - The **y-on-y** headline (dashboard KPI 3.08%) is a *different* variable —
    still to be identified (`discover_bps.py "inflasi" "y-on-y" "tahun ke tahun"`).
- `turvar` is the measure/breakdown within a variable (often just `0` = none).

## Tooling

- `python discover_bps.py [keywords...]` — find variable ids by title.
- `python probe_bps.py <var> [<var>...]` — inspect a variable: title, year
  range, regions, `turvar` options, and the last national values per `turvar`
  (auto-selects the 3 most recent periods). Use it to **validate a candidate
  against the known headline figure** before wiring it.

## Remaining work

1. Identify + validate the national `var`/`turvar` for each KPI against the
   current `data.json` values:
   | indicator | known value | period |
   |---|---|---|
   | GDP growth y-on-y | 5.61% | Q1 2026 |
   | Inflation y-on-y | 3.08% | May 2026 |
   | Unemployment (TPT) | 4.68% | Feb 2026 |
   | Poverty rate | 8.25% | Sep 2025 |
   | Trade balance | +$0.09B | Apr 2026 |
2. Fill the `var` ids into `INDICATORS` in `update_dashboard.py`, set
   `vervar="9999"`, and confirm with `python update_dashboard.py --dry-run --verbose`.
3. Wire `update_monetary()` for BI-Rate + JISDOR (Bank Indonesia has no clean
   JSON API — likely a small HTML/endpoint scrape; keep it merge-preserving).
