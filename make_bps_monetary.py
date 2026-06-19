"""
Monetary indicators: Rupiah/USD (JISDOR) and BI-Rate policy rate.
Source: Bank Indonesia (NOT BPS). Compiled 19 June 2026.

Note on data: public sources document dated JISDOR observations and policy
decisions rather than a complete clean monthly series, so the exchange-rate
panel plots actual dated observations and the policy panel shows the
on-hold level and the 18 Jun 2026 hike. Figures are approximate to the
rupiah and reflect the values reported around each date.
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from datetime import date
import numpy as np

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold"})

BLUE, ORANGE, RED, TEAL = "#4C72B0", "#DD8452", "#C44E52", "#118ab2"


def clean(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# ---- Rupiah / USD (JISDOR) dated observations ----
fx_dates = [date(2025, 12, 31), date(2026, 1, 2), date(2026, 3, 20),
            date(2026, 4, 27), date(2026, 6, 2), date(2026, 6, 8), date(2026, 6, 18)]
fx_rate = [16720, 16674, 16958, 17206, 17863, 18095, 17826]

# ---- BI-Rate policy path (monthly, %) ----
br_labels = ["Jan-26", "Feb-26", "Mar-26", "Apr-26", "May-26", "Jun-26"]
bi_rate = [5.50, 5.50, 5.50, 5.50, 5.50, 5.75]

fig, (axL, axR) = plt.subplots(1, 2, figsize=(14, 6))

# Left: Rupiah depreciation
axL.fill_between(fx_dates, fx_rate, 16500, color=RED, alpha=0.10)
axL.plot(fx_dates, fx_rate, color=RED, lw=2.5, marker="o", ms=6, zorder=3)
axL.annotate(f"Rp{fx_rate[-1]:,}", (fx_dates[-1], fx_rate[-1]), textcoords="offset points",
             xytext=(-6, 12), ha="right", fontsize=10, fontweight="bold", color="#212529")
axL.annotate("year's weakest\nRp18,095 (8 Jun)", (fx_dates[5], fx_rate[5]),
             textcoords="offset points", xytext=(-70, 4), fontsize=8.5, color="#888",
             arrowprops=dict(arrowstyle="->", color="#bbb", lw=1))
axL.set_title("Rupiah weakened ~6.4% YTD against the US dollar in 2026", loc="left", fontsize=13)
axL.set_ylabel("Rupiah per US$ (JISDOR)")
axL.set_ylim(16500, 18300)
axL.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"Rp{v:,.0f}"))
axL.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
axL.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
for lab in axL.get_xticklabels():
    lab.set_rotation(0); lab.set_fontsize(8.5)
clean(axL)
axL.text(0, -0.16, "Source: Bank Indonesia JISDOR — selected dated observations  ·  end-2025 close Rp16,720",
         transform=axL.transAxes, fontsize=8.5, color="#888")

# Right: BI-Rate step
x = np.arange(len(br_labels))
colors = [TEAL] * len(bi_rate); colors[-1] = ORANGE
bars = axR.bar(br_labels, bi_rate, color=colors, width=0.6, zorder=3)
for b, v in zip(bars, bi_rate):
    axR.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.2f}%", ha="center", va="bottom",
             fontsize=10, fontweight="bold" if v == bi_rate[-1] else "normal",
             color="#212529" if v == bi_rate[-1] else "#555")
axR.annotate("+25 bps hike\n(18 Jun 2026)", (x[-1], bi_rate[-1]), textcoords="offset points",
             xytext=(-10, -42), ha="center", fontsize=8.5, color="#888",
             arrowprops=dict(arrowstyle="->", color="#bbb", lw=1))
axR.set_title("BI-Rate raised to 5.75% to defend the rupiah", loc="left", fontsize=13)
axR.set_ylabel("BI-Rate policy rate (%)")
axR.set_ylim(5.0, 6.0)
axR.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
axR.tick_params(axis="x", labelsize=9)
clean(axR)
axR.text(0, -0.16, "Source: Bank Indonesia, RDG 17–18 Jun 2026  ·  held at 5.50% through May 2026",
         transform=axR.transAxes, fontsize=8.5, color="#888")

fig.suptitle("Indonesia Monetary Indicators — Bank Indonesia",
             fontsize=16, fontweight="bold", x=0.06, ha="left", y=1.0)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("chart_monetary.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved: chart_monetary.png")
