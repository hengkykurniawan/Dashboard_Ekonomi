"""
Interactive (Plotly) charts of Indonesian economic indicators (BPS data).
Outputs one self-contained HTML file with all four charts (hover + zoom).
Data compiled 11 June 2026 from Badan Pusat Statistik official releases.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
balance = [2.52, 0.96, 1.28, 3.32, 0.09]
p_labels = ["Mar-23", "Mar-24", "Sep-24", "Mar-25", "Sep-25"]
pov = [9.36, 9.03, 8.57, 8.47, 8.25]

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "GDP growth accelerated to 5.61% (Q1 2026)",
        "Inflation eased to 3.08%, within target (May 2026)",
        "Trade surplus thinned to $0.09B in April 2026",
        "Poverty rate fell to 8.25% — lowest in series (Sep 2025)",
    ),
    specs=[[{"type": "bar"}, {"type": "scatter"}],
           [{"secondary_y": True}, {"type": "scatter"}]],
    vertical_spacing=0.14, horizontal_spacing=0.09,
)

# 1. GDP
gdp_colors = [GREY] * len(gdp); gdp_colors[-1] = ORANGE
fig.add_trace(go.Bar(
    x=q_labels, y=gdp, marker_color=gdp_colors, name="GDP growth",
    hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>", showlegend=False,
), row=1, col=1)

# 2. Inflation
fig.add_trace(go.Scatter(
    x=m_labels, y=infl, mode="lines+markers", line=dict(color=ORANGE, width=3),
    fill="tozeroy", fillcolor="rgba(221,132,82,0.12)", name="Inflation",
    hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>", showlegend=False,
), row=1, col=2)

# 3. Trade
fig.add_trace(go.Bar(x=t_labels, y=exports, name="Exports", marker_color=GREEN,
                     hovertemplate="%{x}<br>Exports: $%{y:.2f}B<extra></extra>"),
              row=2, col=1, secondary_y=False)
fig.add_trace(go.Bar(x=t_labels, y=imports, name="Imports", marker_color=RED,
                     hovertemplate="%{x}<br>Imports: $%{y:.2f}B<extra></extra>"),
              row=2, col=1, secondary_y=False)
fig.add_trace(go.Scatter(x=t_labels, y=balance, name="Trade balance", mode="lines+markers",
                         line=dict(color=BLUE, width=3), marker=dict(size=9),
                         hovertemplate="%{x}<br>Balance: +$%{y:.2f}B<extra></extra>"),
              row=2, col=1, secondary_y=True)

# 4. Poverty
fig.add_trace(go.Scatter(
    x=p_labels, y=pov, mode="lines+markers", line=dict(color=PURPLE, width=3),
    marker=dict(size=9), fill="tozeroy", fillcolor="rgba(129,114,179,0.12)",
    name="Poverty", hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>", showlegend=False,
), row=2, col=2)

# Axes
fig.update_yaxes(title_text="GDP y-o-y (%)", range=[4.4, 5.9], ticksuffix="%", row=1, col=1)
fig.update_yaxes(title_text="CPI y-o-y (%)", range=[0, 5.4], ticksuffix="%", row=1, col=2)
fig.update_yaxes(title_text="US$ billion", range=[0, 30], row=2, col=1, secondary_y=False)
fig.update_yaxes(title_text="Balance (US$B)", range=[0, 4.3], showgrid=False,
                 row=2, col=1, secondary_y=True)
fig.update_yaxes(title_text="Below poverty line (%)", range=[7.5, 9.8], ticksuffix="%", row=2, col=2)

fig.update_layout(
    title=dict(text="<b>Indonesia Economic Dashboard — mid-2026</b><br>"
                    "<sub>Source: Badan Pusat Statistik (BPS) official releases · compiled 11 June 2026</sub>",
               x=0.05, xanchor="left", font=dict(size=20)),
    template="plotly_white",
    barmode="group", bargap=0.25,
    legend=dict(orientation="h", y=-0.06, x=0.5, xanchor="center"),
    height=820, width=1300, margin=dict(t=110, b=70),
    font=dict(family="Segoe UI, sans-serif", size=12),
)

fig.write_html("indonesia_economic_charts_interactive.html", include_plotlyjs="cdn")
print("Saved: indonesia_economic_charts_interactive.html")
