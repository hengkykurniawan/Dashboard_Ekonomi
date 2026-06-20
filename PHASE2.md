# Phase 2 — wiring the live BPS / Bank Indonesia fetch

Status: **complete.** 5 BPS indicators + USD/IDR fetch live; BI-Rate semi-manual.

The daily pipeline fetches GDP, inflation, unemployment, poverty and trade from
the BPS WebAPI (each mapping validated against its known headline figure — see
the table below) and USD/IDR from Frankfurter (ECB). BI-Rate is kept in
`data.json` and bumped by hand on RDG meeting days. The fetcher always
merge-preserves, so any source failure keeps the last-known value.

## Monetary sources

- **USD/IDR** — auto-fetched daily from [Frankfurter](https://frankfurter.dev/)
  (ECB reference, keyless JSON). This is a *market reference rate*, not the
  official BI JISDOR fixing (which has no usable API — static HTML behind a WAF,
  and BI's SOAP service is unreliable). The panel is labeled accordingly. The
  chart keeps a rolling 12-point window; YTD % is vs `meta.fx_baseline`.
- **BI-Rate** — semi-manual. It only changes at the monthly RDG board meeting,
  so there's no daily source worth scraping. To update it, edit the `birate`
  KPI (`value`, `period`, `change`) and append to `charts.birate` in
  `data.json`. The pipeline preserves it between edits.

## Live BPS mappings (validated)

| indicator | var | turvar | national vervar | check |
|---|---|---|---|---|
| GDP growth (y-on-y) | 104 | 5 | 99003 | 5.61% Q1 2026 ✓ |
| GDP growth (q-on-q) | 104 | 4 | 99003 | −0.77% Q1 2026 ✓ |
| Inflation (y-on-y) | 2249 | 0 | 151 | 3.08% May 2026 ✓ |
| Unemployment (TPT) | 543 | 0 | 9999 | 4.68% Feb 2026 ✓ |
| Poverty (P0) | 184 | 0 | 3 (Kota+Desa) | 8.25% Sep 2025 ✓ |
| Trade balance | 498 (+196/497) | 0 | 9999 | +$0.09B Apr 2026 ✓ |
| Foreign tourist arrivals | 1470 | 0 | 248 (Grand Total) | 1.25M Apr 2026 ✓ |
| Farmer's Terms of Trade (NTP) | 1717 | 1390 | 22 | 127.73 May 2026 ✓ |

Note: inflation components (core / administered / volatile food) are **not**
exposed by the WebAPI — only in BPS press releases — so they can't be wired.

Note: auto-generated KPI `period`/`change` are clean and accurate but drop some
hand-authored extras (e.g. "· CPI 111.40", "· 7.24M unemployed"); those came
from additional variables and can be re-added later if wanted.

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

1. ~~Identify + validate BPS variables~~ — **done** (table above).
2. ~~Wire monetary~~ — **done**: USD/IDR auto via Frankfurter; BI-Rate semi-manual.

Optional future polish: re-add the hand-authored KPI extras dropped during
automation ("· CPI 111.40", "· 7.24M unemployed", "· Jan–Apr: +$5.64B") by
fetching the supporting BPS variables; refresh the BPS press-release `src_url`s
from the latest releases.
