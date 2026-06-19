"""
2x2 small-multiples panel of Indonesian economic indicators (BPS data).
Data compiled 11 June 2026 from Badan Pusat Statistik official releases.
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.titleweight": "bold",
})

BLUE, ORANGE, GREEN, RED, PURPLE, GREY = (
    "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#bdbdbd"
)

# Data
q_labels = ["Q1-24", "Q2-24", "Q3-24", "Q4-24", "Q1-25", "Q2-25", "Q3-25", "Q4-25", "Q1-26"]
gdp = [5.11, 5.05, 4.95, 5.02, 4.87, 5.12, 5.04, 5.39, 5.61]
m_labels = ["Sep-25", "Oct-25", "Nov-25", "Dec-25", "Jan-26", "Feb-26", "Mar-26", "Apr-26", "May-26"]
infl = [2.65, 2.86, 2.72, 2.92, 3.55, 4.76, 3.48, 2.42, 3.08]
t_labels = ["Dec-25", "Jan-26", "Feb-26", "Mar-26", "Apr-26"]
exports = [26.35, 22.16, 22.17, 22.53, 25.30]
imports = [23.83, 21.20, 20.89, 19.21, 25.21]
p_labels = ["Mar-23", "Mar-24", "Sep-24", "Mar-25", "Sep-25"]
pov = [9.36, 9.03, 8.57, 8.47, 8.25]


def clean(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle("Indonesia Economic Snapshot — mid-2026",
             fontsize=18, fontweight="bold", x=0.06, ha="left", y=0.98)
fig.text(0.06, 0.945, "Source: Badan Pusat Statistik (BPS) official releases  ·  compiled 11 June 2026",
         fontsize=10, color="#888", ha="left")

# (0,0) GDP
ax = axes[0, 0]
colors = [GREY] * len(gdp); colors[-1] = ORANGE
ax.bar(q_labels, gdp, color=colors, width=0.68, zorder=3)
ax.text(len(gdp) - 1, gdp[-1] + 0.03, "5.61%", ha="center", va="bottom",
        fontsize=9, fontweight="bold")
ax.set_title("GDP growth accelerated to 5.61% (Q1 2026)", fontsize=12.5, loc="left")
ax.set_ylabel("Real GDP, y-o-y (%)")
ax.set_ylim(4.4, 5.9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
ax.tick_params(axis="x", labelsize=8.5)
clean(ax)

# (0,1) Inflation
ax = axes[0, 1]
x = np.arange(len(m_labels))
ax.fill_between(x, infl, 0, color=ORANGE, alpha=0.12)
ax.plot(x, infl, color=ORANGE, lw=2.5)
ax.scatter(x, infl, color=ORANGE, s=34, zorder=4)
ax.annotate("3.08%", (x[-1], infl[-1]), textcoords="offset points",
            xytext=(0, 10), ha="center", fontsize=9, fontweight="bold")
ax.set_title("Inflation eased to 3.08%, within target band (May 2026)", fontsize=12.5, loc="left")
ax.set_ylabel("Headline CPI, y-o-y (%)")
ax.set_xticks(x); ax.set_xticklabels(m_labels, fontsize=8.5)
ax.set_ylim(0, 5.4)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
clean(ax)

# (1,0) Trade
ax = axes[1, 0]
xt = np.arange(len(t_labels)); w = 0.38
ax.bar(xt - w / 2, exports, w, label="Exports", color=GREEN, zorder=3)
ax.bar(xt + w / 2, imports, w, label="Imports", color=RED, alpha=0.85, zorder=3)
ax.set_title("Exports vs imports — April surplus thinned to $0.09B", fontsize=12.5, loc="left")
ax.set_ylabel("US$ billion")
ax.set_xticks(xt); ax.set_xticklabels(t_labels, fontsize=8.5)
ax.set_ylim(0, 30)
ax.legend(frameon=False, fontsize=9, loc="lower center", ncol=2)
clean(ax)

# (1,1) Poverty
ax = axes[1, 1]
xp = np.arange(len(p_labels))
ax.fill_between(xp, pov, 7.5, color=PURPLE, alpha=0.12)
ax.plot(xp, pov, color=PURPLE, lw=2.5, marker="o", ms=6, zorder=3)
ax.annotate("8.25%", (xp[-1], pov[-1]), textcoords="offset points",
            xytext=(0, 11), ha="center", fontsize=9, fontweight="bold")
ax.set_title("Poverty rate fell to 8.25% — lowest in the series (Sep 2025)", fontsize=12.5, loc="left")
ax.set_ylabel("Below poverty line (%)")
ax.set_xticks(xp); ax.set_xticklabels(p_labels, fontsize=8.5)
ax.set_ylim(7.5, 9.8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
clean(ax)

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig("chart_panel_2x2.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved: chart_panel_2x2.png")
