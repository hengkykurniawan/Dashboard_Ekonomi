"""
Presentation-styled charts (large fonts, high contrast) of Indonesian
economic indicators. BPS data, compiled 11 June 2026.
Output sized 1600x900 (16:9) for slides.
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 15,
    "axes.titlesize": 21,
    "axes.titleweight": "bold",
    "axes.labelsize": 15,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "figure.dpi": 150,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.color": "#e6e6e6",
})

# Higher-contrast palette
BLUE, ORANGE, GREEN, RED, PURPLE, GREY = (
    "#1f4e79", "#e8730c", "#2e7d32", "#c62828", "#5e35b1", "#9e9e9e"
)
FIGSIZE = (16, 9)


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#888")
    ax.spines["bottom"].set_color("#888")


def src(ax, text):
    ax.text(0, -0.13, text, transform=ax.transAxes, fontsize=12, color="#999")


# Data
q_labels = ["Q1-24", "Q2-24", "Q3-24", "Q4-24", "Q1-25", "Q2-25", "Q3-25", "Q4-25", "Q1-26"]
gdp = [5.11, 5.05, 4.95, 5.02, 4.87, 5.12, 5.04, 5.39, 5.61]
m_labels = ["Sep-25", "Oct-25", "Nov-25", "Dec-25", "Jan-26", "Feb-26", "Mar-26", "Apr-26", "May-26"]
infl = [2.65, 2.86, 2.72, 2.92, 3.55, 4.76, 3.48, 2.42, 3.08]
t_labels = ["Dec-25", "Jan-26", "Feb-26", "Mar-26", "Apr-26"]
exports = [26.35, 22.16, 22.17, 22.53, 25.30]
imports = [23.83, 21.20, 20.89, 19.21, 25.21]
balance = [2.52, 0.96, 1.28, 3.32, 0.09]
p_labels = ["Mar-23", "Mar-24", "Sep-24", "Mar-25", "Sep-25"]
pov = [9.36, 9.03, 8.57, 8.47, 8.25]

# 1. GDP
fig, ax = plt.subplots(figsize=FIGSIZE)
colors = [GREY] * len(gdp); colors[-1] = ORANGE
bars = ax.bar(q_labels, gdp, color=colors, width=0.66, zorder=3)
for b, v in zip(bars, gdp):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.03, f"{v:.2f}%", ha="center", va="bottom",
            fontsize=14, fontweight="bold" if v == gdp[-1] else "normal",
            color="#222" if v == gdp[-1] else "#666")
ax.set_title("GDP growth accelerated to 5.61% in Q1 2026", loc="left", pad=16)
ax.set_ylabel("Real GDP growth, year-on-year")
ax.set_ylim(4.4, 5.9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
clean(ax)
src(ax, "Source: Badan Pusat Statistik (BPS), 5 May 2026  ·  Full-year 2025: 5.11%")
plt.tight_layout()
plt.savefig("slide_gdp_growth.png", dpi=150, bbox_inches="tight")
plt.close()

# 2. Inflation
fig, ax = plt.subplots(figsize=FIGSIZE)
x = np.arange(len(m_labels))
ax.fill_between(x, infl, 0, color=ORANGE, alpha=0.13)
ax.plot(x, infl, color=ORANGE, lw=4)
ax.scatter(x, infl, color=ORANGE, s=90, zorder=4)
for i in (5, 8):
    ax.annotate(f"{infl[i]:.2f}%", (x[i], infl[i]), textcoords="offset points",
                xytext=(0, 16), ha="center", fontsize=15, fontweight="bold")
ax.set_title("Inflation stayed within target, at 3.08% in May 2026", loc="left", pad=16)
ax.set_ylabel("Headline CPI inflation, year-on-year")
ax.set_xticks(x); ax.set_xticklabels(m_labels)
ax.set_ylim(0, 5.4)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
clean(ax)
src(ax, "Source: Badan Pusat Statistik (BPS) monthly inflation releases  ·  Feb spike = base effect")
plt.tight_layout()
plt.savefig("slide_inflation.png", dpi=150, bbox_inches="tight")
plt.close()

# 3. Trade
fig, ax = plt.subplots(figsize=FIGSIZE)
xt = np.arange(len(t_labels)); w = 0.38
ax.bar(xt - w / 2, exports, w, label="Exports", color=GREEN, zorder=3)
ax.bar(xt + w / 2, imports, w, label="Imports", color=RED, alpha=0.9, zorder=3)
ax.set_ylabel("US$ billion")
ax.set_xticks(xt); ax.set_xticklabels(t_labels)
ax.set_ylim(0, 30)
ax2 = ax.twinx()
ax2.plot(xt, balance, color=BLUE, lw=4, marker="o", ms=12, label="Trade balance", zorder=5)
for i, v in enumerate(balance):
    ax2.annotate(f"+${v:.2f}B", (xt[i], balance[i]), textcoords="offset points",
                 xytext=(0, 18), ha="center", fontsize=13, color=BLUE, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
ax2.set_ylabel("Trade balance (US$ billion)", color=BLUE)
ax2.tick_params(axis="y", colors=BLUE)
ax2.set_ylim(0, 4.3); ax2.grid(False)
for s in ("top",):
    ax.spines[s].set_visible(False); ax2.spines[s].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_title("Trade stayed in surplus; April margin thinned to $0.09B", loc="left", pad=16)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper center", ncol=3, frameon=False,
          fontsize=14, bbox_to_anchor=(0.5, -0.07))
src(ax, "Source: Badan Pusat Statistik (BPS)  ·  Jan–Apr 2026 cumulative surplus: +US$5.64B")
plt.tight_layout()
plt.savefig("slide_trade.png", dpi=150, bbox_inches="tight")
plt.close()

# 4. Poverty
fig, ax = plt.subplots(figsize=FIGSIZE)
xp = np.arange(len(p_labels))
ax.fill_between(xp, pov, 7.5, color=PURPLE, alpha=0.13)
ax.plot(xp, pov, color=PURPLE, lw=4, marker="o", ms=12, zorder=3)
for i, v in enumerate(pov):
    ax.annotate(f"{v:.2f}%", (xp[i], pov[i]), textcoords="offset points",
                xytext=(0, 16), ha="center", fontsize=14,
                fontweight="bold" if i == len(pov) - 1 else "normal")
ax.set_title("Poverty rate fell to 8.25% — lowest in the series", loc="left", pad=16)
ax.set_ylabel("Population below poverty line")
ax.set_xticks(xp); ax.set_xticklabels(p_labels)
ax.set_ylim(7.5, 9.8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
clean(ax)
src(ax, "Source: Badan Pusat Statistik (BPS) poverty profile, 5 Feb 2026  ·  23.36M people")
plt.tight_layout()
plt.savefig("slide_poverty.png", dpi=150, bbox_inches="tight")
plt.close()

print("Saved: slide_gdp_growth.png, slide_inflation.png, slide_trade.png, slide_poverty.png")
