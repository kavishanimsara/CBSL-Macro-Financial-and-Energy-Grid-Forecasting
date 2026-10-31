import plotly.graph_objects as go
from typing import Optional

PLOTLY_FONT = dict(color="#0f172a", size=12, family="Inter, sans-serif")
PLOTLY_TITLE_FONT = dict(color="#0f172a", size=15, family="Inter, sans-serif")

ENERGY_SOURCES = {
    "hydro_pct": ("Hydro", "#3b82f6"),
    "thermal_coal_pct": ("Coal", "#475569"),
    "thermal_oil_pct": ("Fuel Oil", "#dc2626"),
    "wind_pct": ("Wind", "#16a34a"),
}

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def style_chart(
    fig: go.Figure,
    title: str,
    height: int = 360,
    xt: str = "Date",
    yt: Optional[str] = None,
    legend_top: bool = True
) -> go.Figure:
    """Apply unified styling consistent with CBSL presentation guidelines."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
        font=PLOTLY_FONT,
        title=dict(text=title, font=PLOTLY_TITLE_FONT),
        height=height,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(title=dict(text=xt, font=PLOTLY_FONT), tickfont=PLOTLY_FONT),
        yaxis=dict(title=dict(text=yt or "", font=PLOTLY_FONT), tickfont=PLOTLY_FONT),
    )
    if legend_top:
        fig.update_layout(
            legend=dict(
                font=PLOTLY_FONT,
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    return fig

def add_time_nav(fig: go.Figure) -> go.Figure:
    """Add multi-horizon range slider and selector buttons to Plotly chart."""
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(buttons=[
            dict(count=3, label="3M", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(count=1, label="1Y", step="year", stepmode="backward"),
            dict(step="all", label="All")
        ])
    )
    return fig
