"""
utils/charts.py
Reusable Plotly visual components with the neon dark theme.
"""
import plotly.graph_objects as go

NEON = ["#00e5ff", "#7b5cff", "#ff5cf0", "#5cff9d", "#ffb627", "#ff4d6d"]
LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
              font=dict(color="#cdd6ff"), margin=dict(l=20, r=20, t=40, b=20))


def gauge(value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        title={"text": title, "font": {"size": 16}},
        gauge={"axis": {"range": [0, 100]},
               "bar": {"color": "#00e5ff"},
               "steps": [{"range": [0, 45], "color": "#3a1020"},
                         {"range": [45, 70], "color": "#3a2e10"},
                         {"range": [70, 100], "color": "#0e2a33"}],
               "bgcolor": "rgba(0,0,0,0)"}))
    fig.update_layout(**LAYOUT, height=280)
    return fig


def radar(categories, values, name="You"):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], theta=categories + [categories[0]],
        fill="toself", name=name, line=dict(color="#7b5cff"),
        fillcolor="rgba(123,92,255,0.35)"))
    fig.update_layout(**LAYOUT, height=380,
                      polar=dict(bgcolor="rgba(0,0,0,0)",
                                 radialaxis=dict(range=[0, 100], color="#778")))
    return fig


def trend_line(x, series: dict, title=""):
    fig = go.Figure()
    for i, (name, y) in enumerate(series.items()):
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", name=name,
                                 line=dict(color=NEON[i % len(NEON)], width=3)))
    fig.update_layout(**LAYOUT, title=title, height=360)
    return fig


def sentiment_pie(counts: dict):
    fig = go.Figure(go.Pie(labels=list(counts.keys()), values=list(counts.values()),
                           hole=0.55, marker=dict(colors=NEON)))
    fig.update_layout(**LAYOUT, height=340)
    return fig


def risk_bar(risks: dict):
    labels = [k.replace("_", " ").title() for k in risks]
    vals = list(risks.values())
    colors = ["#ff4d6d" if v >= 60 else "#ffb627" if v >= 35 else "#5cff9d" for v in vals]
    fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
                           marker=dict(color=colors), text=[f"{v}%" for v in vals],
                           textposition="auto"))
    fig.update_layout(**LAYOUT, height=400, xaxis=dict(range=[0, 100]))
    return fig


def mood_heatmap(z, x, y):
    fig = go.Figure(go.Heatmap(z=z, x=x, y=y, colorscale="Viridis"))
    fig.update_layout(**LAYOUT, height=320)
    return fig