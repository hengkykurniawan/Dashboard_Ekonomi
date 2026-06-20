# Indonesia Economic Dashboard

A self-contained dashboard and chart set for Indonesia's key macroeconomic
indicators, built from official **Badan Pusat Statistik (BPS)** statistical
releases and **Bank Indonesia** monetary data. Data compiled **19 June 2026**.

## Contents

| File | Description |
| --- | --- |
| `indonesia_economic_dashboard.html` | Main interactive dashboard (Chart.js via CDN). KPI cards + 6 charts, rendered from `data.json`. |
| `data.json` | Single source of truth for all dashboard figures. Refreshed by the updater. |
| `index.html` | Redirect to the dashboard (entry point for GitHub Pages). |
| `update_dashboard.py` | Fetches the latest figures and rewrites `data.json` (merge-preserving on failure). |
| `discover_bps.py` | One-off helper to find BPS WebAPI variable IDs by keyword. |
| `bps_api.py` | Shared BPS WebAPI client + key loading. |
| `requirements.txt` | Python dependencies for the updater (`requests`). |
| `.github/workflows/update-data.yml` | Daily GitHub Actions job that runs the updater and commits changes. |
| `indonesia_economic_charts_interactive.html` | Alternate interactive chart page. |
| `make_bps_*.py` | matplotlib chart/slide PNG generators. |
| `chart_*.png`, `slide_*.png` | Generated images. |

## Indicators covered

- **GDP growth** — 5.61% (Q1 2026, y-on-y); full-year 2025: 5.11%
- **Inflation** — 3.08% (May 2026, y-on-y)
- **Unemployment** — 4.68% (Feb 2026)
- **Poverty rate** — 8.25% (Sep 2025)
- **Trade balance** — +US$5.64B cumulative (Jan–Apr 2026)
- **BI-Rate** — 5.75% (raised +25 bps on 18 Jun 2026)
- **Rupiah / US$ (JISDOR)** — Rp17,826 (18 Jun 2026)

## Viewing the dashboard

The dashboard fetches `data.json`, so it must be **served over HTTP** (opening
the file directly with `file://` will be blocked by the browser). Serve the
folder locally:

```bash
python -m http.server 8755
# then open http://localhost:8755/   (or /indonesia_economic_dashboard.html)
```

On GitHub Pages it is served over HTTPS, so it just works.

## Regenerating the charts

Requires Python with `matplotlib` and `numpy`:

```bash
pip install matplotlib numpy
python make_bps_charts.py
python make_bps_monetary.py
python make_bps_panel.py
python make_bps_presentation.py
python make_bps_interactive.py
```

## Automatic daily updates

The dashboard reads its figures from **`data.json`**, which is refreshed by
**`update_dashboard.py`** and published daily by a **GitHub Actions** workflow.

**How it works**
- `update_dashboard.py` loads the committed `data.json` as a base, overlays any
  value it successfully fetches, and writes it back. If a source fails, the old
  value is **preserved** — the dashboard never goes blank.
- `.github/workflows/update-data.yml` runs daily (01:17 UTC), executes the
  updater with the `BPS_API_KEY` secret, and commits `data.json` if it changed.
- With Pages set to *Deploy from a branch → main / root*, each commit
  republishes the live site automatically.

> BPS publishes monthly/quarterly/semi-annually, so most days the job finds
> nothing new and makes no commit. It updates when a fresh release lands.

**The API key (never commit it)**
- **CI:** store it as a repository secret named `BPS_API_KEY`
  (*Settings → Secrets and variables → Actions*).
- **Local testing:** put the key in a file named `bps_key.txt` (gitignored), or
  set `$env:BPS_API_KEY` in PowerShell.

**What updates automatically**

| Panel | Source | Auto? |
| --- | --- | --- |
| GDP growth (y-o-y **and** q-o-q), household consumption | BPS WebAPI | ✅ daily |
| Inflation, unemployment, poverty, trade | BPS WebAPI | ✅ daily |
| Producer Price Index, Wholesale Price Index (IHPB), manufacturing output | BPS WebAPI | ✅ daily |
| Foreign tourist arrivals, Farmer's Terms of Trade (NTP) | BPS WebAPI | ✅ daily |
| USD/IDR (reference rate) | [Frankfurter](https://frankfurter.dev/) (ECB) | ✅ daily |
| BI-Rate (policy rate) | Bank Indonesia | ✍️ semi-manual |
| Foreign reserves | Bank Indonesia | ✍️ semi-manual (monthly) |
| Inflation target | Bank Indonesia | ✍️ static (annual policy) |

The BPS variable mappings are validated and documented in [PHASE2.md](PHASE2.md).
USD/IDR is a market reference rate (ECB via Frankfurter), **not** the official
BI JISDOR fixing — JISDOR has no usable API. The other Bank Indonesia series
have no free API either.

> **Inflation breakdown:** the **by-category** split (11 COICOP groups — food,
> transport, personal care, …) **is** in the WebAPI and is charted as a ranked
> bar (auto-updates daily). The **by-component** split (core / administered /
> volatile-food) is **not** in the WebAPI — BPS only publishes that in press
> releases — so it can't be auto-fetched.

**Updating the semi-manual panels** (edit the matching `kpis[]` entry in
`data.json` — `value`, `period`, `change` — then commit; the pipeline preserves
them in between):
- **BI-Rate** (`birate`): on RDG meeting days; also append the month to `charts.birate`.
- **Foreign reserves** (`reserves`): monthly, when BI publishes (~7th).
- **Inflation target** (`inflation_target`): yearly, when BI revises the target.

**Local testing of the fetcher**: put your key in `bps_key.txt` (gitignored),
then `pip install -r requirements.txt && python update_dashboard.py --dry-run --verbose`.

## Sources

- **Real-sector data** (GDP, inflation, unemployment, poverty, trade):
  [Badan Pusat Statistik (BPS)](https://www.bps.go.id/en/pressrelease) — for
  auto-refreshing data, register at the
  [BPS WebAPI developer portal](https://webapi.bps.go.id/developer/).
- **Monetary data** (BI-Rate, rupiah/US$ JISDOR):
  [Bank Indonesia](https://www.bi.go.id/en/default.aspx). Exchange-rate points
  are selected dated JISDOR observations.

> Figures are embedded from dated official releases and reflect values reported
> around each date. They are a snapshot, not a live feed.
