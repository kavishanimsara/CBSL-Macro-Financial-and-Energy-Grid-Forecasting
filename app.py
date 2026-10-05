import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# ==============================================================================
# 1. PAGE CONFIG & THEME
# ==============================================================================
st.set_page_config(page_title="CBSL Macroeconomic & Energy Grid System", page_icon="⚡",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main {background-color:#f8fafc;color:#0f172a;font-family:'Inter',-apple-system,sans-serif;}
    .header-banner {background:linear-gradient(135deg,#fff 0%,#f1f5f9 100%);border:1px solid #cbd5e1;border-radius:12px;padding:24px;margin-bottom:24px;box-shadow:0 4px 16px rgba(15,23,42,.04);}
    .header-title {font-size:2.1rem;font-weight:800;color:#0f172a;margin-bottom:4px;}
    .header-subtitle {font-size:1rem;color:#475569;}
    .kpi-card {background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:18px;text-align:center;box-shadow:0 2px 10px rgba(15,23,42,.03);transition:transform .2s,border-color .2s;}
    .kpi-card:hover {transform:translateY(-2px);border-color:#2563eb;}
    .kpi-title {font-size:.85rem;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.05em;}
    .kpi-value {font-size:1.8rem;font-weight:800;color:#0f172a;margin:6px 0;}
    .kpi-delta-up {font-size:.85rem;font-weight:700;color:#16a34a;}
    .kpi-delta-down {font-size:.85rem;font-weight:700;color:#dc2626;}
    .takeaway-box {background:#f0f9ff;border-left:4px solid #0284c7;border-radius:8px;padding:16px 20px;margin:18px 0;color:#0c4a6e;font-size:.95rem;line-height:1.6;}
    .takeaway-box-green {background:#ecfdf5;border-left:4px solid #10b981;border-radius:8px;padding:16px 20px;margin:18px 0;color:#064e3b;font-size:.95rem;line-height:1.6;}
    .chip {display:inline-block;background:#e0f2fe;color:#0c4a6e;border-radius:999px;padding:2px 10px;margin:2px 4px 2px 0;font-size:.75rem;font-weight:600;}
    .stTabs [data-baseweb="tab-list"] {gap:8px;}
    .stTabs [data-baseweb="tab"] {background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:8px 16px;font-weight:600;color:#334155;}
    .stTabs [aria-selected="true"] {background:#2563eb !important;color:#fff !important;border-color:#2563eb !important;}
</style>
""", unsafe_allow_html=True)

PLOTLY_FONT = dict(color="#0f172a", size=12, family="Inter, sans-serif")
PLOTLY_TITLE_FONT = dict(color="#0f172a", size=15, family="Inter, sans-serif")
SRC = {  # column -> (label, colour, gwh column)
    "hydro_pct": ("Hydro", "#3b82f6"),
    "thermal_coal_pct": ("Coal", "#475569"),
    "thermal_oil_pct": ("Fuel Oil", "#dc2626"),
    "wind_pct": ("Wind", "#16a34a"),
}
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def style(fig, title, height=360, xt="Date", yt=None, legend_top=True):
    """Shared Plotly styling (presentation only)."""
    fig.update_layout(
        template="plotly_white", paper_bgcolor="#fff", plot_bgcolor="#fff", font=PLOTLY_FONT,
        title=dict(text=title, font=PLOTLY_TITLE_FONT), height=height, hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(title=dict(text=xt, font=PLOTLY_FONT), tickfont=PLOTLY_FONT),
        yaxis=dict(title=dict(text=yt or "", font=PLOTLY_FONT), tickfont=PLOTLY_FONT),
    )
    if legend_top:
        fig.update_layout(legend=dict(font=PLOTLY_FONT, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig


def add_time_nav(fig):
    fig.update_xaxes(rangeslider_visible=True, rangeselector=dict(buttons=[
        dict(count=3, label="3M", step="month", stepmode="backward"),
        dict(count=6, label="6M", step="month", stepmode="backward"),
        dict(count=1, label="1Y", step="year", stepmode="backward"),
        dict(step="all", label="All")]))
    return fig


# ==============================================================================
# 2. DATA PIPELINE  (UNCHANGED)
# ==============================================================================
CSV_PATH = "cbsl_daily_economic_indicators_2020_2026_preprocesd.csv"

@st.cache_data(show_spinner=False)
def load_and_preprocess_data():
    try:
        df = pd.read_csv(CSV_PATH)
        df['report_date'] = pd.to_datetime(df['report_date'])
        df = df.sort_values('report_date').reset_index(drop=True)
    except Exception as e:
        st.warning("⚠️ Real CSV dataset not found in workspace root. Operating on calibrated synthetic dataset.")
        dates = pd.date_range(start="2020-01-01", end="2026-08-10", freq="B")
        np.random.seed(42)
        n = len(dates)

        usd_rate = np.linspace(185, 310, n) + np.sin(np.linspace(0, 10, n)) * 15 + np.random.normal(0, 2, n)
        peak_demand = 2200 + np.sin(np.linspace(0, 30, n)) * 300 + np.random.normal(0, 40, n)
        total_energy = peak_demand * 0.019 + np.random.normal(0, 1, n)

        df = pd.DataFrame({
            "report_date": dates,
            "usd_tt_selling": usd_rate,
            "usd_tt_buying": usd_rate * 0.98,
            "indicative_usd_spot": usd_rate * 0.99,
            "peak_demand": peak_demand,
            "total_energy": total_energy,
            "hydro_pct": np.clip(40 + np.sin(np.linspace(0, 20, n)) * 20, 10, 75),
            "thermal_coal_pct": np.clip(35 + np.cos(np.linspace(0, 20, n)) * 10, 10, 60),
            "thermal_oil_pct": np.clip(15 + np.sin(np.linspace(0, 10, n)) * 8, 5, 40),
            "wind_pct": np.clip(10 + np.random.normal(0, 2, n), 2, 20),
            "real_gdp_growth": np.random.uniform(-2, 4, n),
            "ncpi_yoy": np.random.uniform(5, 50, n),
            "ccpi_yoy": np.random.uniform(4, 45, n)
        })

    energy_cols = ["thermal_coal_pct", "thermal_oil_pct", "hydro_pct", "wind_pct"]
    df[energy_cols] = df[energy_cols].clip(lower=0.0)
    e_sum = df[energy_cols].sum(axis=1)
    for c in energy_cols:
        df[c] = np.where(e_sum > 0, (df[c] / e_sum) * 100.0, df[c])

    df["year"] = df["report_date"].dt.year
    df["month"] = df["report_date"].dt.month
    df["month_name"] = df["report_date"].dt.strftime("%B")
    df["quarter"] = df["report_date"].dt.to_period("Q").astype(str)
    df["day_name"] = df["report_date"].dt.day_name()
    df["is_weekend"] = df["report_date"].dt.dayofweek >= 5
    return df

# ==============================================================================
# 3. MODEL TRAINING ENGINE  (UNCHANGED)
# ==============================================================================
@st.cache_resource(show_spinner=False)
def train_dashboard_models(_df):
    df = _df.copy()
    df_t2 = df[["report_date", "peak_demand", "total_energy", "hydro_pct", "thermal_coal_pct"]].dropna().copy().reset_index(drop=True)
    df_t2["demand_lag1"] = df_t2["peak_demand"].shift(1)
    df_t2["demand_lag2"] = df_t2["peak_demand"].shift(2)
    df_t2["demand_lag7"] = df_t2["peak_demand"].shift(7)
    df_t2["energy_lag1"] = df_t2["total_energy"].shift(1)
    df_t2["hydro_lag1"]  = df_t2["hydro_pct"].shift(1)

    df_t2["demand_delta_target"] = df_t2["peak_demand"] - df_t2["demand_lag1"]
    df_t2["demand_diff1"] = df_t2["demand_lag1"] - df_t2["demand_lag2"]
    df_t2["demand_diff7"] = df_t2["demand_lag1"] - df_t2["demand_lag7"]
    df_t2["sin_dow"] = np.sin(2 * np.pi * df_t2["report_date"].dt.dayofweek / 5.0)
    df_t2["cos_dow"] = np.cos(2 * np.pi * df_t2["report_date"].dt.dayofweek / 5.0)

    t2_features = ["demand_diff1", "demand_diff7", "energy_lag1", "hydro_lag1", "sin_dow", "cos_dow"]
    df_t2_clean = df_t2.dropna().reset_index(drop=True)
    X2 = df_t2_clean[t2_features]
    y2_delta = df_t2_clean["demand_delta_target"]

    scaler2 = StandardScaler()
    X2_sc = scaler2.fit_transform(X2)

    reg_t2 = Lasso(alpha=0.2, random_state=42)
    reg_t2.fit(X2_sc, y2_delta)

    cluster_cols = ["usd_tt_selling", "peak_demand", "total_energy", "hydro_pct", "thermal_coal_pct"]
    df_t4 = df[["report_date"] + cluster_cols].dropna().copy().reset_index(drop=True)

    scaler4 = StandardScaler()
    X4_sc = scaler4.fit_transform(df_t4[cluster_cols])

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_t4["cluster_id"] = kmeans.fit_predict(X4_sc)

    pca = PCA(n_components=2, random_state=42)
    pca_2d = pca.fit_transform(X4_sc)
    df_t4["pca_1"] = pca_2d[:, 0]
    df_t4["pca_2"] = pca_2d[:, 1]

    return {
        "reg_t2": reg_t2, "scaler2": scaler2, "t2_features": t2_features,
        "kmeans": kmeans, "pca": pca, "scaler4": scaler4, "cluster_cols": cluster_cols, "df_t4": df_t4
    }

df = load_and_preprocess_data()
models = train_dashboard_models(df)

# ==============================================================================
# 4. SIDEBAR FILTERS (with reset, date range, export)
# ==============================================================================
all_years = sorted(df["year"].unique().tolist())
min_d, max_d = df["report_date"].min().date(), df["report_date"].max().date()
YEAR_ALL = "All Years (2020–2026)"
ERA_NONE = "None / Use Year Filter"

def reset_filters():
    st.session_state.update(yr_mode=YEAR_ALL, custom_years=all_years, era=ERA_NONE,
                            months=MONTHS, quarter="All Quarters", dow="All Days",
                            drange=(min_d, max_d))

for k, v in dict(yr_mode=YEAR_ALL, custom_years=all_years, era=ERA_NONE, months=MONTHS,
                 quarter="All Quarters", dow="All Days", drange=(min_d, max_d)).items():
    st.session_state.setdefault(k, v)

with st.sidebar:
    # st.image("https://img.icons8.com/isometric/100/analytics.png", width=70)
    st.title("CBSL Analytics")
    st.caption("Macroeconomic & Power Grid Decision Support System")
    st.button("🔄 Reset all filters", on_click=reset_filters, use_container_width=True)
    st.markdown("---")

    st.subheader("📅 Primary Year Filter")
    selected_year_mode = st.selectbox("Select Filter Year:",
                                      [YEAR_ALL] + [str(y) for y in all_years] + ["Custom Multi-Year Selection"], key="yr_mode")
    if selected_year_mode == "Custom Multi-Year Selection":
        selected_years = st.multiselect("Select Specific Years:", all_years, key="custom_years")
    elif selected_year_mode != YEAR_ALL:
        selected_years = [int(selected_year_mode)]
    else:
        selected_years = all_years

    st.subheader("📌 Macro Era Presets")
    era_preset = st.radio("Select Historical Era:", [
        ERA_NONE, "Pre-Crisis Baseline (2020–2021)", "Economic Crisis Shock Phase (2022–2023)",
        "Post-Crisis Recovery (2024–2026)", "Last 12 Months"], key="era")

    st.subheader("🗓️ Granular Filters")
    drange = st.date_input("Exact Date Range:", min_value=min_d, max_value=max_d, key="drange")
    selected_months = st.multiselect("Filter by Months:", MONTHS, key="months")
    selected_quarter = st.selectbox("Filter by Quarter:", ["All Quarters", "Q1", "Q2", "Q3", "Q4"], key="quarter")
    dow_filter = st.radio("Day Filter:", ["All Days", "Weekdays Only", "Weekends Only"], key="dow", horizontal=True)

# ---- apply filters
df_filtered = df.copy()
active_chips = []
if era_preset == "Pre-Crisis Baseline (2020–2021)":
    df_filtered = df_filtered[df_filtered["report_date"] < "2022-01-01"]
elif era_preset == "Economic Crisis Shock Phase (2022–2023)":
    df_filtered = df_filtered[(df_filtered["report_date"] >= "2022-01-01") & (df_filtered["report_date"] < "2024-01-01")]
elif era_preset == "Post-Crisis Recovery (2024–2026)":
    df_filtered = df_filtered[df_filtered["report_date"] >= "2024-01-01"]
elif era_preset == "Last 12 Months":
    df_filtered = df_filtered[df_filtered["report_date"] >= df["report_date"].max() - pd.DateOffset(years=1)]
elif selected_years:
    df_filtered = df_filtered[df_filtered["year"].isin(selected_years)]
    if selected_year_mode != YEAR_ALL:
        active_chips.append(selected_year_mode if len(selected_years) == 1 else f"{len(selected_years)} years")
if era_preset != ERA_NONE:
    active_chips.append(era_preset.split(" (")[0])

if isinstance(drange, (tuple, list)) and len(drange) == 2:
    df_filtered = df_filtered[(df_filtered["report_date"].dt.date >= drange[0]) & (df_filtered["report_date"].dt.date <= drange[1])]
    if tuple(drange) != (min_d, max_d):
        active_chips.append(f"{drange[0]:%d %b %y} → {drange[1]:%d %b %y}")
if selected_months:
    df_filtered = df_filtered[df_filtered["month_name"].isin(selected_months)]
    if len(selected_months) < 12:
        active_chips.append(f"{len(selected_months)} months")
if selected_quarter != "All Quarters":
    df_filtered = df_filtered[df_filtered["quarter"].str.contains(selected_quarter)]
    active_chips.append(selected_quarter)
if dow_filter == "Weekdays Only":
    df_filtered = df_filtered[~df_filtered["is_weekend"]]; active_chips.append("Weekdays")
elif dow_filter == "Weekends Only":
    df_filtered = df_filtered[df_filtered["is_weekend"]]; active_chips.append("Weekends")

if len(df_filtered) == 0:
    st.error("⚠️ Current filter selection returned 0 rows! Showing full dataset instead. Use 'Reset all filters' in the sidebar.")
    df_filtered = df.copy()

with st.sidebar:
    st.markdown("---")
    st.metric("Records in window", f"{len(df_filtered):,}", f"of {len(df):,}", delta_color="off")
    st.download_button("⬇️ Download filtered CSV", df_filtered.to_csv(index=False).encode(),
                       "cbsl_filtered.csv", "text/csv", use_container_width=True)
    st.caption("Capstone Project II | Data Science Department\nSabaragamuwa University of Sri Lanka")

# ==============================================================================
# 5. HEADER
# ==============================================================================
chips = "".join(f'<span class="chip">{c}</span>' for c in active_chips) or '<span class="chip">No extra filters</span>'
st.markdown(f"""
<div class="header-banner">
    <div class="header-title">CBSL Macroeconomic & Energy Grid Forecasting</div>
    <div class="header-subtitle">Executive Decision-Support System | Active Window: <b>{len(df_filtered):,} Daily Records</b> ({df_filtered['report_date'].min():%d %b %Y} – {df_filtered['report_date'].max():%d %b %Y})</div>
    <div style="margin-top:8px">{chips}</div>
</div>
""", unsafe_allow_html=True)


def render_kpi(col, title, val_str, d1, d7, unit="", pp=False):
    s = "pp" if pp else "%"
    c1 = "kpi-delta-up" if d1 >= 0 else "kpi-delta-down"
    c7 = "kpi-delta-up" if d7 >= 0 else "kpi-delta-down"
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{val_str} <span style="font-size:.85rem;color:#475569;">{unit}</span></div>
        <div><span class="{c1}">1D: {d1:+.2f}{s}</span> | <span class="{c7}">7D: {d7:+.2f}{s}</span></div>
    </div>""", unsafe_allow_html=True)


def year_picker(key):
    """Per-tab year selector that defaults to the years in the filtered window."""
    yrs = st.multiselect("📅 Years to display on charts below:", all_years,
                         default=sorted(df_filtered["year"].unique().tolist()), key=key)
    out = df_filtered[df_filtered["year"].isin(yrs)]
    return (out if len(out) else df_filtered).copy()


tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Macro Telemetry & FX",
    "⚡ Power Grid & Fuel Mix Decompositions",
    "🎯 Day-Ahead Peak Demand Predictor",
    "🌐 Macro Regimes & Scenario Simulator"])

# ==============================================================================
# TAB 1
# ==============================================================================
with tab1:
    st.subheader("Executive Telemetry & Macroeconomic Trajectory")
    latest = df_filtered.iloc[-1]
    p1 = df_filtered.iloc[-2] if len(df_filtered) > 1 else latest
    p7 = df_filtered.iloc[-8] if len(df_filtered) > 7 else latest
    pc = lambda c, p: (latest[c] - p[c]) / p[c] * 100
    k1, k2, k3, k4 = st.columns(4)
    render_kpi(k1, "USD / LKR Exchange Rate", f"{latest['usd_tt_selling']:.2f}", pc('usd_tt_selling', p1), pc('usd_tt_selling', p7), "LKR")
    render_kpi(k2, "Peak Grid Demand", f"{latest['peak_demand']:,.1f}", pc('peak_demand', p1), pc('peak_demand', p7), "MW")
    render_kpi(k3, "Daily Energy Output", f"{latest['total_energy']:.1f}", pc('total_energy', p1), pc('total_energy', p7), "GWh")
    render_kpi(k4, "Hydropower Share", f"{latest['hydro_pct']:.1f}", latest['hydro_pct'] - p1['hydro_pct'], latest['hydro_pct'] - p7['hydro_pct'], "%", pp=True)

    st.markdown(f"""
    <div class="takeaway-box">
        💡 <b>Executive Takeaway for Selected Date Range</b>:<br>
        Between <b>{df_filtered['report_date'].min():%b %Y}</b> and <b>{df_filtered['report_date'].max():%b %Y}</b>,
        the USD/LKR exchange rate averaged <b>{df_filtered['usd_tt_selling'].mean():.2f} LKR</b> while national peak electricity demand averaged <b>{df_filtered['peak_demand'].mean():,.0f} MW</b>.
        The currency trajectory highlights structural shifts from the fixed peg regime (~200 LKR) through the 2022 currency float shock (>360 LKR) to post-crisis stabilization around 310 LKR.
    </div>""", unsafe_allow_html=True)

    df_t1 = year_picker("t1_year_filter")

    with st.expander("⚙️ Chart controls", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        fx_cols = [c for c in ["usd_tt_selling", "usd_tt_buying", "indicative_usd_spot"] if c in df_t1.columns]
        fx_sel = c1.multiselect("FX series", fx_cols, default=fx_cols[:1],
                                format_func=lambda c: c.replace("_", " ").upper())
        roll = c2.slider("Smoothing (days)", 1, 90, 1, help="Rolling mean window; 1 = raw data")
        fx_mode = c3.radio("FX view", ["Timeline", "Overlay years"], horizontal=True)
        log_y = c4.checkbox("Log scale")
        show_events = c4.checkbox("Mark 2022 float", value=True)

    col_fx, col_macro = st.columns([1.2, 1])
    with col_fx:
        fig_fx = go.Figure()
        palette = px.colors.qualitative.Bold
        if fx_mode == "Timeline" or not fx_sel:
            for i, c in enumerate(fx_sel or ["usd_tt_selling"]):
                fig_fx.add_trace(go.Scatter(x=df_t1["report_date"], y=df_t1[c].rolling(roll, min_periods=1).mean(),
                                            mode="lines", name=c.replace("_", " ").upper(),
                                            line=dict(color=["#2563eb", "#f59e0b", "#16a34a"][i % 3], width=2.3)))
            if show_events:
                ev = pd.Timestamp("2022-03-09")
                if df_t1["report_date"].min() <= ev <= df_t1["report_date"].max():
                    fig_fx.add_shape(type="line", x0=ev, x1=ev, y0=0, y1=1, yref="paper", line=dict(color="#dc2626", dash="dot"))
                    fig_fx.add_annotation(x=ev, y=1, yref="paper", text="CBSL float", showarrow=False, font=dict(color="#dc2626"))
            add_time_nav(fig_fx)
        else:
            c = fx_sel[0]
            for i, (y, g) in enumerate(df_t1.groupby("year")):
                fig_fx.add_trace(go.Scatter(x=g["report_date"].dt.dayofyear, y=g[c].rolling(roll, min_periods=1).mean(),
                                            mode="lines", name=str(y), line=dict(color=palette[i % len(palette)], width=2)))
        style(fig_fx, "USD/LKR Rate Trajectory", 440, "Date" if fx_mode == "Timeline" else "Day of year", "LKR Rate")
        if log_y:
            fig_fx.update_yaxes(type="log")
        st.plotly_chart(fig_fx, use_container_width=True)

    with col_macro:
        macro_opts = {"ncpi_yoy": ("NCPI Inflation (%)", "#ef4444"), "ccpi_yoy": ("CCPI Inflation (%)", "#f59e0b"),
                      "real_gdp_growth": ("Real GDP Growth (%)", "#16a34a")}
        macro_opts = {k: v for k, v in macro_opts.items() if k in df_t1.columns}
        m_sel = st.multiselect("Indicators", list(macro_opts), default=list(macro_opts),
                               format_func=lambda k: macro_opts[k][0])
        fig_macro = go.Figure()
        for k in m_sel:
            fig_macro.add_trace(go.Scatter(x=df_t1["report_date"], y=df_t1[k].rolling(roll, min_periods=1).mean(),
                                           mode="lines", name=macro_opts[k][0], line=dict(color=macro_opts[k][1], width=2)))
        style(fig_macro, "Macro Indicators (%)", 390, yt="Percentage (%)")
        st.plotly_chart(fig_macro, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 🗓️ Year-by-Year Historical Summary")
    ys = df.groupby("year")[["usd_tt_selling", "peak_demand", "total_energy", "hydro_pct", "thermal_coal_pct"]].mean().round(2)
    ys.columns = ["Avg USD/LKR Rate", "Avg Peak Demand (MW)", "Avg Daily Energy (GWh)", "Avg Hydro Share (%)", "Avg Coal Share (%)"]
    hl = st.toggle("Highlight heatmap", value=True)
    st.dataframe(ys.style.background_gradient(cmap="Blues", axis=0) if hl else ys, use_container_width=True)

# ==============================================================================
# TAB 2
# ==============================================================================
with tab2:
    st.subheader("National Power Grid Telemetry & Fuel Generation Mix Decompositions")
    st.markdown("""
    <div class="takeaway-box-green">
        ⚡ <b>Power Grid Generation Mix Takeaway</b>:<br>
        Hydropower generation follows seasonal monsoon rain cycles (peaking >60% during wet months and contracting <20% during dry spells).
        When hydro output contracts, the grid relies heavily on thermal coal and furnace oil peaker units, directly driving up daily generation costs.
    </div>""", unsafe_allow_html=True)

    df_t2c = year_picker("t2_year_filter")
    a, b, c_ = st.columns([2, 1, 1])
    src_sel = a.multiselect("Generation sources", list(SRC), default=list(SRC), format_func=lambda k: SRC[k][0]) or list(SRC)
    freq = b.selectbox("Time resolution", ["Daily", "Weekly", "Monthly"], index=2)
    mix_mode = c_.radio("Mix unit", ["Share %", "GWh"], horizontal=True)

    df_t2c["hydro_gwh"] = df_t2c["hydro_pct"] / 100 * df_t2c["total_energy"]
    df_t2c["coal_gwh"] = df_t2c["thermal_coal_pct"] / 100 * df_t2c["total_energy"]
    df_t2c["oil_gwh"] = df_t2c["thermal_oil_pct"] / 100 * df_t2c["total_energy"]
    df_t2c["wind_gwh"] = df_t2c["wind_pct"] / 100 * df_t2c["total_energy"]
    GWH = {"hydro_pct": "hydro_gwh", "thermal_coal_pct": "coal_gwh", "thermal_oil_pct": "oil_gwh", "wind_pct": "wind_gwh"}

    rule = {"Daily": None, "Weekly": "W", "Monthly": "MS"}[freq]
    base = df_t2c.set_index("report_date")
    mix_df = (base.resample(rule).mean(numeric_only=True) if rule else base).reset_index()

    col_mix, col_box = st.columns([1.3, 1])
    with col_mix:
        fig_mix = go.Figure()
        for k in src_sel:
            y = mix_df[k] if mix_mode == "Share %" else mix_df[GWH[k]]
            fig_mix.add_trace(go.Scatter(x=mix_df["report_date"], y=y, stackgroup="one", name=SRC[k][0],
                                         fillcolor=SRC[k][1], line=dict(width=0),
                                         groupnorm="percent" if mix_mode == "Share %" else None))
        style(fig_mix, f"Generation {mix_mode} ({freq})", 400, yt="Share (%)" if mix_mode == "Share %" else "Avg daily GWh")
        add_time_nav(fig_mix)
        st.plotly_chart(fig_mix, use_container_width=True)

    with col_box:
        r1, r2 = st.columns(2)
        metric = r1.selectbox("Metric", ["peak_demand", "total_energy"], format_func=lambda x: x.replace("_", " ").title())
        ctype = r2.selectbox("Chart", ["Box", "Violin", "Mean bars"])
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if ctype == "Box":
            fig_b = px.box(df_t2c, x="day_name", y=metric, category_orders={"day_name": day_order}, color="day_name",
                           color_discrete_sequence=px.colors.sequential.Blues_r)
        elif ctype == "Violin":
            fig_b = px.violin(df_t2c, x="day_name", y=metric, category_orders={"day_name": day_order}, color="day_name",
                              box=True, color_discrete_sequence=px.colors.sequential.Blues_r)
        else:
            g = df_t2c.groupby("day_name")[metric].mean().reindex(day_order).reset_index()
            fig_b = px.bar(g, x="day_name", y=metric, color_discrete_sequence=["#2563eb"])
        style(fig_b, f"{metric.replace('_', ' ').title()} by Day of Week", 400, "Day of Week", metric, legend_top=False)
        fig_b.update_layout(showlegend=False, hovermode="closest")
        st.plotly_chart(fig_b, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Aggregated Power Generation Volumes by Source (GWh)")
    v1, v2, v3 = st.columns(3)
    grp = v1.selectbox("Group by", ["Quarter", "Month", "Year"])
    agg = v2.radio("Aggregation", ["Total", "Daily average"], horizontal=True)
    bmode = v3.radio("Bar mode", ["stack", "group"], horizontal=True)
    gcol = {"Quarter": "quarter", "Month": "month_name", "Year": "year"}[grp]
    gcols = [GWH[k] for k in src_sel]
    grouped = df_t2c.groupby(gcol)[gcols].sum() if agg == "Total" else df_t2c.groupby(gcol)[gcols].mean()
    if grp == "Month":
        grouped = grouped.reindex(MONTHS).dropna()
    grouped = grouped.reset_index()
    fig_v = go.Figure()
    for k in src_sel:
        fig_v.add_trace(go.Bar(x=grouped[gcol].astype(str), y=grouped[GWH[k]], name=SRC[k][0], marker_color=SRC[k][1]))
    style(fig_v, f"{agg} generation by {grp.lower()} (GWh)", 380, grp, "GWh")
    fig_v.update_layout(barmode=bmode)
    st.plotly_chart(fig_v, use_container_width=True)

# ==============================================================================
# TAB 3
# ==============================================================================
with tab3:
    st.subheader("Day-Ahead National Peak Electricity Demand Predictor")
    st.caption(r"Engineered Delta-Lasso Architecture ($\pm 1 \text{ RMSE} = 116.74\text{ MW}$ base error)")

    defaults = dict(prev=2450.0, d7=2420.0, d1=15.0, en=48.5, hy=42.0, co=35.0)
    for k, v in defaults.items():
        st.session_state.setdefault(f"t3_{k}", v)

    def load_preset(p):
        st.session_state.update({f"t3_{k}": v for k, v in p.items()})

    def load_latest():
        d = df.dropna(subset=["peak_demand"]).reset_index(drop=True)
        st.session_state.update(t3_prev=float(d["peak_demand"].iloc[-1]), t3_d7=float(d["peak_demand"].iloc[-8]),
                                t3_d1=float(d["peak_demand"].iloc[-1] - d["peak_demand"].iloc[-2]),
                                t3_en=float(round(d["total_energy"].iloc[-1], 1)),
                                t3_hy=float(round(d["hydro_pct"].iloc[-1], 1)),
                                t3_co=float(round(d["thermal_coal_pct"].iloc[-1], 1)))

    pb = st.columns(4)
    pb[0].button("📡 Load latest actuals", on_click=load_latest, use_container_width=True)
    pb[1].button("🌧️ Wet season", on_click=load_preset, args=(dict(t3_hy=65.0, t3_co=22.0, t3_prev=2300.0, t3_d7=2300.0),), use_container_width=True)
    pb[2].button("☀️ Dry season", on_click=load_preset, args=(dict(t3_hy=18.0, t3_co=50.0, t3_prev=2700.0, t3_d7=2650.0),), use_container_width=True)
    pb[3].button("↩️ Defaults", on_click=load_preset, args=({f"t3_{k}": v for k, v in defaults.items()},), use_container_width=True)

    col_input, col_output = st.columns([1, 1.1])
    with col_input:
        st.markdown("##### 📥 Telemetry Feature Inputs")
        prev_demand = st.number_input("Yesterday's Peak Load (MW)", step=10.0, key="t3_prev")
        demand_7d_ago = st.number_input("Peak Load 7 Days Ago (MW)", step=10.0, key="t3_d7")
        diff1 = st.number_input("Yesterday vs day-before change (MW)", step=5.0, key="t3_d1")
        daily_energy = st.number_input("Total Daily Energy Output (GWh)", step=0.5, key="t3_en")
        hydro_share = st.slider("Hydropower Generation Share (%)", 0.0, 100.0, key="t3_hy")
        # coal_share = st.slider("Thermal Coal Generation Share (%)", 0.0, 100.0, key="t3_co")
        target_date = st.date_input("Target Prediction Date", value=datetime.now() + timedelta(days=1))
        conf = st.radio("Confidence band", ["±1 RMSE (~68%)", "±1.96 RMSE (~95%)", "±2.58 RMSE (~99%)"], horizontal=True)
        mult = {"±1 RMSE (~68%)": 1.0, "±1.96 RMSE (~95%)": 1.96, "±2.58 RMSE (~99%)": 2.58}[conf]

    dow = target_date.weekday()
    diff7 = prev_demand - demand_7d_ago

    def predict(prev, d7v, d1v, en, hy, dw):
        X = pd.DataFrame([{"demand_diff1": d1v, "demand_diff7": prev - d7v, "energy_lag1": en, "hydro_lag1": hy,
                           "sin_dow": np.sin(2 * np.pi * dw / 5.0), "cos_dow": np.cos(2 * np.pi * dw / 5.0)}])
        return prev + models["reg_t2"].predict(models["scaler2"].transform(X))[0]

    with col_output:
        pred_peak = predict(prev_demand, demand_7d_ago, diff1, daily_energy, hydro_share, dow)
        pred_delta = pred_peak - prev_demand
        band = 116.74 * mult
        st.markdown("##### ⚡ Forecast Output & Operational Alert")
        st.metric("Predicted Day-Ahead Peak Load", f"{pred_peak:,.1f} MW", f"{pred_delta:+.1f} MW Shift")
        st.info(f"📍 **{conf} range**: **{pred_peak - band:,.1f} MW** to **{pred_peak + band:,.1f} MW**")
        if pred_peak >= 3000:
            st.error("🔴 Peaker units likely required (≥ 3,000 MW).")
        elif pred_peak >= 2400:
            st.warning("🟠 Elevated load: prepare thermal reserves.")
        else:
            st.success("🟢 Normal operating range.")
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=pred_peak,
            title={'text': "Thermal Peaker Activation Gauge", 'font': {'size': 16, 'color': "#0f172a"}},
            delta={'reference': prev_demand, 'increasing': {'color': "#dc2626"}, 'decreasing': {'color': "#16a34a"}},
            gauge={'axis': {'range': [1500, 3500]}, 'bar': {'color': "#2563eb"}, 'bgcolor': "#fff",
                   'steps': [{'range': [1500, 2400], 'color': 'rgba(22,163,74,.2)'},
                             {'range': [2400, 3000], 'color': 'rgba(245,158,11,.2)'},
                             {'range': [3000, 3500], 'color': 'rgba(220,38,38,.3)'}],
                   'threshold': {'line': {'color': "#dc2626", 'width': 4}, 'thickness': .75, 'value': 3000}}))
        fig_g.update_layout(height=260, paper_bgcolor="#fff", font=PLOTLY_FONT, margin=dict(l=20, r=20, t=50, b=10))
        st.plotly_chart(fig_g, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 🔬 Sensitivity Analysis — how does the forecast respond?")
    s1, s2 = st.columns([1, 3])
    sweep = s1.selectbox("Vary", ["Hydro share (%)", "Yesterday's peak (MW)", "Daily energy (GWh)", "Day of week"])
    if sweep == "Day of week":
        xs = list(range(7)); labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        ys_ = [predict(prev_demand, demand_7d_ago, diff1, daily_energy, hydro_share, d) for d in xs]
        cur_x = labels[dow]
        fig_s = go.Figure(go.Bar(x=labels, y=ys_, marker_color=["#f59e0b" if l == cur_x else "#2563eb" for l in labels]))
    else:
        rng = {"Hydro share (%)": np.linspace(0, 100, 51), "Yesterday's peak (MW)": np.linspace(1800, 3200, 57),
               "Daily energy (GWh)": np.linspace(30, 60, 61)}[sweep]
        f = {"Hydro share (%)": lambda v: predict(prev_demand, demand_7d_ago, diff1, daily_energy, v, dow),
             "Yesterday's peak (MW)": lambda v: predict(v, demand_7d_ago, diff1, daily_energy, hydro_share, dow),
             "Daily energy (GWh)": lambda v: predict(prev_demand, demand_7d_ago, diff1, v, hydro_share, dow)}[sweep]
        ys_ = [f(v) for v in rng]
        cur = {"Hydro share (%)": hydro_share, "Yesterday's peak (MW)": prev_demand, "Daily energy (GWh)": daily_energy}[sweep]
        fig_s = go.Figure(go.Scatter(x=rng, y=ys_, mode="lines", line=dict(color="#2563eb", width=3), name="Forecast"))
        fig_s.add_trace(go.Scatter(x=[cur], y=[f(cur)], mode="markers", marker=dict(size=14, color="#f59e0b", symbol="star"), name="Current input"))
    style(fig_s, f"Predicted peak load vs {sweep}", 320, sweep, "Predicted peak (MW)")
    s2.plotly_chart(fig_s, use_container_width=True)

# ==============================================================================
# TAB 4
# ==============================================================================
with tab4:
    st.subheader("Unsupervised Macroeconomic Regime Discovery (K-Means k=3)")
    st.markdown("""
    <div class="takeaway-box">
        🌐 <b>Macro Regime Discovery Takeaway</b>:<br>
        Standardized K-Means clustering ($k=3$) and 2D PCA project six years of continuous indicators into 3 operational states:
        <b>Cluster 0 (Economic Crisis Shock Phase)</b>, <b>Cluster 1 (Post-Crisis Industrial Expansion)</b>, and <b>Cluster 2 (Pre-Crisis Baseline Period)</b>.
    </div>""", unsafe_allow_html=True)

    df_t4 = models["df_t4"].copy()
    df_t4["year"] = df_t4["report_date"].dt.year
    ccols = models["cluster_cols"]
    cent = df_t4.groupby("cluster_id")[ccols].mean().round(2)
    cnames = {0: "Cluster 0: Crisis Shock Phase", 1: "Cluster 1: Post-Crisis Expansion", 2: "Cluster 2: Pre-Crisis Baseline"}
    cluster_names = {0: "🔴 Cluster 0: Economic Shock & Crisis Phase", 1: "🔵 Cluster 1: Post-Crisis Industrial Expansion",
                     2: "🟢 Cluster 2: Pre-Crisis Baseline Period"}
    cent_display = cent.copy(); cent_display.index = [cnames[i] for i in cent.index]
    st.markdown("##### 📋 Regime Profiles (Centroid Feature Means)")
    st.dataframe(cent_display.style.background_gradient(cmap="Blues", axis=0), use_container_width=True)

    for k, c in zip(["usd", "dem", "en", "hy", "co"], ccols):
        pass
    sim_defaults = dict(sim_usd=310.0, sim_dem=2500.0, sim_en=48.0, sim_hy=40.0, sim_co=33.0)
    for k, v in sim_defaults.items():
        st.session_state.setdefault(k, v)
    keys = ["sim_usd", "sim_dem", "sim_en", "sim_hy", "sim_co"]

    def load_sim(vals):
        st.session_state.update({k: float(np.clip(v, lo, hi)) for k, v, (lo, hi) in zip(keys, vals, [(180, 400), (1500, 3200), (30, 60), (10, 75), (10, 60)])})

    col_sim, col_map = st.columns([1, 1.8])
    with col_sim:
        st.markdown("##### 🎛️ Scenario Simulator")
        pick = st.selectbox("Start from…", ["— custom —"] + [cnames[i] for i in cent.index] + ["Latest observation"])
        if st.button("Load into sliders", use_container_width=True):
            if pick == "Latest observation":
                load_sim(df_t4[ccols].iloc[-1].values)
            elif pick != "— custom —":
                load_sim(cent.iloc[[cnames[i] for i in cent.index].index(pick)][ccols].values)
            st.rerun()
        sim_usd = st.slider("Simulated USD / LKR Exchange Rate", 180.0, 400.0, key="sim_usd")
        sim_demand = st.slider("Simulated Peak Load (MW)", 1500.0, 3200.0, key="sim_dem")
        sim_energy = st.slider("Total Daily Energy (GWh)", 30.0, 60.0, key="sim_en")
        sim_hydro = st.slider("Hydro Generation Share (%)", 10.0, 75.0, key="sim_hy")
        sim_coal = st.slider("Thermal Coal Share (%)", 10.0, 60.0, key="sim_co")

        sim_df = pd.DataFrame([{"usd_tt_selling": sim_usd, "peak_demand": sim_demand, "total_energy": sim_energy,
                                "hydro_pct": sim_hydro, "thermal_coal_pct": sim_coal}])
        sim_sc = models["scaler4"].transform(sim_df)
        sim_cluster = models["kmeans"].predict(sim_sc)[0]
        sim_pca = models["pca"].transform(sim_sc)[0]
        st.success(f"**Assigned Macro Regime**:\n\n### {cluster_names[sim_cluster]}")
        dist = models["kmeans"].transform(sim_sc)[0]
        st.caption("Distance to each regime centroid (standardised units; smaller = closer)")
        st.bar_chart(pd.Series(dist, index=[f"C{i}" for i in range(3)]), height=140)

    with col_map:
        st.markdown("##### 📍 Interactive 2D PCA Cluster Scatter Map")
        o1, o2, o3 = st.columns([2, 1.3, 1])
        show_c = o1.multiselect("Show clusters", [0, 1, 2], default=[0, 1, 2], format_func=lambda i: cnames[i])
        color_by = o2.radio("Colour by", ["Cluster", "Year"], horizontal=True)
        opacity = o3.slider("Opacity", 0.1, 1.0, 0.6)
        d = df_t4[df_t4["cluster_id"].isin(show_c)] if show_c else df_t4
        hover = {"report_date": True, "usd_tt_selling": ":.1f", "peak_demand": ":.0f", "pca_1": False, "pca_2": False}
        if color_by == "Cluster":
            fig_pca = px.scatter(d, x="pca_1", y="pca_2", color=d["cluster_id"].map(cnames), opacity=opacity,
                                 color_discrete_map={cnames[0]: "#dc2626", cnames[1]: "#2563eb", cnames[2]: "#16a34a"},
                                 hover_data=hover, labels={"color": "Regime"})
        else:
            fig_pca = px.scatter(d, x="pca_1", y="pca_2", color=d["year"].astype(str), opacity=opacity,
                                 hover_data=hover, labels={"color": "Year"})
        fig_pca.add_trace(go.Scatter(x=[sim_pca[0]], y=[sim_pca[1]], mode="markers+text", name="User Scenario",
                                     text=["⭐ YOUR SCENARIO"], textposition="top center",
                                     marker=dict(size=18, color="#f59e0b", symbol="star", line=dict(width=1, color="#0f172a"))))
        style(fig_pca, "2D PCA Cluster Map", 430, "Principal Component 1", "Principal Component 2")
        fig_pca.update_layout(hovermode="closest")
        st.plotly_chart(fig_pca, use_container_width=True)

    st.markdown("##### ⏳ Regime timeline")
    fig_t = px.scatter(df_t4, x="report_date", y=df_t4["cluster_id"].map(cnames), color=df_t4["cluster_id"].map(cnames),
                       color_discrete_map={cnames[0]: "#dc2626", cnames[1]: "#2563eb", cnames[2]: "#16a34a"})
    style(fig_t, "Which regime was active when?", 260, yt="", legend_top=False)
    fig_t.update_layout(showlegend=False, hovermode="closest")
    add_time_nav(fig_t)
    st.plotly_chart(fig_t, use_container_width=True)