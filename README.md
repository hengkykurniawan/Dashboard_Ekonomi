# Indonesia Economic Dashboard

A self-contained dashboard and chart set for Indonesia's key macroeconomic
indicators, built from official **Badan Pusat Statistik (BPS)** statistical
releases and **Bank Indonesia** monetary data. Data compiled **19 June 2026**.

## Contents

| File | Description |
| --- | --- |
| `indonesia_economic_dashboard.html` | Main interactive dashboard (Chart.js via CDN). KPI cards, 6 charts, detail table. Open directly in a browser — no backend required. |
| `indonesia_economic_charts_interactive.html` | Alternate interactive chart page. |
| `make_bps_charts.py` | Generates the core indicator PNG charts. |
| `make_bps_monetary.py` | Rupiah/USD (JISDOR) + BI-Rate charts. |
| `make_bps_panel.py` | 2×2 panel summary figure. |
| `make_bps_interactive.py` | Builds the interactive HTML chart page. |
| `make_bps_presentation.py` | Presentation slide PNGs. |
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

Open `indonesia_economic_dashboard.html` directly in any browser, or serve the
folder locally:

```bash
python -m http.server 8755
# then open http://localhost:8755/indonesia_economic_dashboard.html
```

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
