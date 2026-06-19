"""
Publication-quality charts of Indonesian economic indicators (BPS data).
Data compiled 11 June 2026 from Badan Pusat Statistik official releases.
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.titlesize": 15,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "figure.dpi": 150,
})

# Palette (colorblind-friendly seaborn deep tones)
BLUE, ORANGE, GREEN, RED, PURPLE, GREY = (
    "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#bdbdbd"
)


def clean(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# ----------------------------------------------------------------------
# 1. GDP quarterly growth (y-on-y), highlight Q1-2026
# ----------------------------------------------------------------------
q_labels = ["Q1-24", "Q2-24", "Q3-24", "Q4-24", "Q1-25", "Q2-25", "Q3-25", "Q4-25", "Q1-26"]
gdp = [5.11, 5.05, 4.95, 5.02, 4.87, 5.12, 5.04, 5.39, 5.61]
colors = [GREY] * len(gdp)
colors[-1] = ORANGE

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(q_labels, gdp, color=colors, width=0.68, zorder=3)
for b, v in zip(bars, gdp):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.03, f"{v:.2f}%",
            ha="center", va="bottom", fontsize=9,
            fontweight="bold" if v == gdp[-1] else "normal",
            color="#212529" if v == gdp[-1] else "#555")
ax.set_title("Indonesia's economy accelerated to 5.61% in Q1 2026 —\nits fastest quarterly growth in two years", loc="left")
ax.set_ylabel("Real GDP growth, year-on-year (%)")
ax.set_ylim(4.4, 5.9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}%"))
ax.margins(x=0.01)
clean(ax)
ax.text(0, -0.14, "Source: Badan Pusat Statistik (BPS), press release 5 May 2026  ·  Full-year 2025 growth: 5.11%",
        transform=ax.transAxes, fontsize=8.5, color="#888")
plt.tight_layout()
plt.savefig("chart_gdp_growth.png", dpi=150, bbox_inches="tight")
plt.close()

# ----------------------------------------------------------------------
# 2. Monthly headline inflation (y-on-y)
# ----------------------------------------------------------------------
m_labels = ["Sep-25", "Oct-25", "Nov-25", "Dec-25", "Jan-26", "Feb-26", "Mar-26", "Apr-26", "May-26"]
infl = [2.65, 2.86, 2.72, 2.92, 3.55, 4.76, 3.48, 2.42, 3.08]
x = np.arange(len(m_labels))

fig, ax = plt.subplots(figsize=(10, 6))
ax.fill_between(x, infl, 0, color=ORANGE, alpha=0.12, zorder=1)
ax.plot(x, infl, color=ORANGE, lw=2.5, zorder=3)
ax.scatter(x, infl, color=ORANGE, s=42, zorder=4)
# highlight the Feb base-effect spike and the latest point
for i in (5, 8):
    ax.annotate(f"{infl[i]:.2f}%", (x[i], infl[i]), textcoords="offset points",
                xytext=(0, 12), ha="center", fontsize=9.5, fontweight="bold", color="#212529")
ax.annotate("Feb spike is a base effect\n(low Feb-2025 from electricity-tariff discount)",
            (x[5], infl[5]), textcoords="offset points", xytext=(8, -38),
            fontsize=8.5, color="#888",
            arrowprops=dict(arrowstyle="->", color="#bbb", lw=1))
ax.set_title("Indonesian inflation stayed within Bank Indonesia's target band,\nticking up to 3.08% in May 2026", loc="left")
ax.set_ylabel("Headline CPI inflation, year-on-year (%)")
ax.set_xticks(x)
ax.set_xticklabels(m_labels)
ax.set_ylim(0, 5.4)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
clean(ax)
ax.text(0, -0.14, "Source: Badan Pusat Statistik (BPS) monthly inflation releases, Oct 2025 – Jun 2026",
        transform=ax.transAxes, fontsize=8.5, color="#888")
plt.tight_layout()
plt.savefig("chart_inflation.png", dpi=150, bbox_inches="tight")
plt.close()

# ----------------------------------------------------------------------
# 3. Trade: exports & imports (grouped bars) + balance (line)
# ----------------------------------------------------------------------
t_labels = ["Dec-25", "Jan-26", "Feb-26", "Mar-26", "Apr-26"]
exports = [26.35, 22.16, 22.17, 22.53, 25.30]
imports = [23.83, 21.20, 20.89, 19.21, 25.21]
balance = [2.52, 0.96, 1.28, 3.32, 0.09]
xt = np.arange(len(t_labels))
w = 0.38

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(xt - w / 2, exports, w, label="Exports", color=GREEN, zorder=3)
ax.bar(xt + w / 2, imports, w, label="Imports", color=RED, alpha=0.85, zorder=3)
ax.set_ylabel("US$ billion")
ax.set_xticks(xt)
ax.set_xticklabels(t_labels)
ax.set_ylim(0, 30)

ax2 = ax.twinx()
ax2.plot(xt, balance, color=BLUE, lw=2.5, marker="o", ms=7, label="Trade balance", zorder=5)
for i, v in enumerate(balance):
    ax2.annotate(f"+${v:.2f}B", (xt[i], balance[i]), textcoords="offset points",
                 xytext=(0, 14), ha="center", fontsize=8.5, color=BLUE, fontweight="bold",
                 zorder=6,
                 bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
ax2.set_ylabel("Trade balance (US$ billion)", color=BLUE)
ax2.tick_params(axis="y", colors=BLUE)
ax2.set_ylim(0, 4.2)
ax2.grid(False)
ax2.spines["top"].set_visible(False)
ax.spines["top"].set_visible(False)

ax.set_title("Indonesia's trade stayed in surplus, but the April margin\nnarrowed to $0.09B as imports surged", loc="left")
# merged legend
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.08))
ax.text(0, -0.20, "Source: Badan Pusat Statistik (BPS) export–import releases  ·  Jan–Apr 2026 cumulative surplus: +US$5.64B",
        transform=ax.transAxes, fontsize=8.5, color="#888")
plt.tight_layout()
plt.savefig("chart_trade.png", dpi=150, bbox_inches="tight")
plt.close()

# ----------------------------------------------------------------------
# 4. Poverty rate trend (semi-annual)
# ----------------------------------------------------------------------
p_labels = ["Mar-23", "Mar-24", "Sep-24", "Mar-25", "Sep-25"]
pov = [9.36, 9.03, 8.57, 8.47, 8.25]
xp = np.arange(len(p_labels))

fig, ax = plt.subplots(figsize=(10, 6))
ax.fill_between(xp, pov, 7.5, color=PURPLE, alpha=0.12, zorder=1)
ax.plot(xp, pov, color=PURPLE, lw=2.5, marker="o", ms=8, zorder=3)
for i, v in enumerate(pov):
    ax.annotate(f"{v:.2f}%", (xp[i], pov[i]), textcoords="offset points",
                xytext=(0, 12), ha="center", fontsize=9.5,
                fontweight="bold" if i == len(pov) - 1 else "normal",
                color="#212529")
ax.set_title("Indonesia's poverty rate kept falling, reaching 8.25% in Sep 2025 —\nthe lowest in the series (23.36 million people)", loc="left")
ax.set_ylabel("Population below poverty line (%)")
ax.set_xticks(xp)
ax.set_xticklabels(p_labels)
ax.set_ylim(7.5, 9.8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
clean(ax)
ax.text(0, -0.14, "Source: Badan Pusat Statistik (BPS) poverty profile, press release 5 Feb 2026  ·  Urban 6.60%, rural 10.72%",
        transform=ax.transAxes, fontsize=8.5, color="#888")
plt.tight_layout()
plt.savefig("chart_poverty.png", dpi=150, bbox_inches="tight")
plt.close()

print("Saved: chart_gdp_growth.png, chart_inflation.png, chart_trade.png, chart_poverty.png")
