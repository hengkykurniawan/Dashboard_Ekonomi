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

**Phase 2 — activating the live fetch**

The pipeline ships in a safe "preserve" mode. To turn on live BPS fetching:

1. Add your key locally (`bps_key.txt`) and run the discovery helper:
   ```bash
   pip install -r requirements.txt
   python discover_bps.py
   ```
2. Copy the reported `var` ids into the `INDICATORS` table in
   `update_dashboard.py` (replace the `None` placeholders).
3. Test: `python update_dashboard.py --dry-run --verbose`.

The two **monetary** panels (BI-Rate, Rupiah/US$ JISDOR) come from Bank
Indonesia, which has no clean JSON API; wiring that source is the remaining
Phase 2 task (`update_monetary()` in `update_dashboard.py`).

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
