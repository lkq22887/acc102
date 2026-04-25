import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Commodity Price Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.stApp { background-color: #0a0a0f; color: #e8e8e8; }
[data-testid="stSidebar"] { background-color: #111118; border-right: 1px solid #2a2a3a; }

.metric-card {
    background: linear-gradient(135deg, #13131f 0%, #1a1a2e 100%);
    border: 1px solid #2a2a3a; border-radius: 12px;
    padding: 20px 24px; margin-bottom: 12px;
}
.metric-label { font-family: 'Space Mono', monospace; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: #888; margin-bottom: 6px; }
.metric-value { font-size: 28px; font-weight: 800; color: #f0c040; letter-spacing: -1px; }
.metric-delta { font-family: 'Space Mono', monospace; font-size: 12px; margin-top: 4px; }
.delta-pos { color: #4ecca3; }
.delta-neg { color: #ff6b6b; }

.section-header {
    font-size: 13px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase;
    color: #f0c040; border-bottom: 1px solid #2a2a3a; padding-bottom: 8px;
    margin: 24px 0 16px 0; font-family: 'Space Mono', monospace;
}

.hero { text-align: center; padding: 32px 0 20px 0; }
.hero h1 { font-size: 48px; font-weight: 800; letter-spacing: -2px; color: #ffffff; margin: 0; }
.hero h1 span { color: #f0c040; }
.hero p { font-family: 'Space Mono', monospace; font-size: 12px; letter-spacing: 2px; color: #666; margin-top: 8px; }

.insight-box {
    background: linear-gradient(135deg, #13131f, #1a1a2e);
    border-left: 3px solid #f0c040; border-radius: 0 8px 8px 0;
    padding: 14px 18px; margin: 10px 0; font-size: 14px; line-height: 1.6; color: #ccc;
}

.detail-card {
    background: linear-gradient(135deg, #0f1a2e, #1a2a1a);
    border: 1px solid #f0c040; border-radius: 12px; padding: 20px 24px; margin: 12px 0;
}
.detail-card h3 { color: #f0c040; font-family: 'Space Mono', monospace; font-size: 13px; letter-spacing: 2px; margin: 0 0 12px 0; }
.detail-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #1e1e30; }
.detail-key { color: #888; font-size: 13px; }
.detail-val { color: #e8e8e8; font-weight: 700; font-family: 'Space Mono', monospace; font-size: 13px; }

.calc-result {
    background: linear-gradient(135deg, #0f2a1a, #1a2e0f);
    border: 1px solid #4ecca3; border-radius: 12px;
    padding: 20px 24px; margin: 12px 0; text-align: center;
}
.calc-result .big { font-size: 36px; font-weight: 800; letter-spacing: -1px; }
.calc-result .sub { font-family: 'Space Mono', monospace; font-size: 11px; color: #888; letter-spacing: 2px; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("commodity_data.csv", parse_dates=["Date"], index_col="Date")
    df = df.dropna(how="all").ffill()
    return df

df = load_data()

COLORS = {"Gold": "#f0c040", "Oil": "#4ecca3", "DXY": "#a78bfa", "US10Y": "#ff6b6b"}
LABELS = {
    "Gold":  "Gold (USD/oz)",
    "Oil":   "WTI Crude Oil (USD/bbl)",
    "DXY":   "US Dollar Index",
    "US10Y": "10Y Treasury Yield (%)",
}

EVENTS = {
    "2022-02-24": ("🔴", "Russia invades Ukraine"),
    "2022-03-16": ("📈", "Fed first rate hike"),
    "2022-06-15": ("📈", "Fed +75bps hike"),
    "2023-03-10": ("🏦", "SVB bank collapse"),
    "2023-07-26": ("📈", "Fed final hike (5.5%)"),
    "2024-09-18": ("📉", "Fed first rate cut"),
    "2025-01-20": ("🇺🇸", "Trump inauguration"),
}

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-header">⚙ Controls</div>', unsafe_allow_html=True)
    min_date = df.index.min().date()
    max_date = df.index.max().date()
    date_range = st.date_input("Date Range", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)

    st.markdown('<div class="section-header">📈 Assets</div>', unsafe_allow_html=True)
    show_gold = st.checkbox("Gold", value=True)
    show_oil  = st.checkbox("Crude Oil (WTI)", value=True)

    st.markdown('<div class="section-header">🌐 Macro Drivers</div>', unsafe_allow_html=True)
    show_dxy   = st.checkbox("US Dollar Index (DXY)", value=True)
    show_us10y = st.checkbox("10Y Treasury Yield", value=True)

    st.markdown('<div class="section-header">🔧 Options</div>', unsafe_allow_html=True)
    norm_mode   = st.selectbox("Price Display", ["Normalised (Base=100)", "Raw Prices"])
    roll_window = st.slider("Rolling Correlation Window (days)", 20, 120, 60, step=10)
    vol_window  = st.slider("Volatility Window (days)", 10, 60, 21, step=5)
    show_events = st.checkbox("Show Macro Events on Chart", value=True)

    st.markdown("---")
    st.markdown(
        '<p style="font-family:Space Mono;font-size:10px;color:#444;letter-spacing:1px;">'
        'DATA: Yahoo Finance<br>ACCESSED: Apr 2026<br>ACC102 · Track 4</p>',
        unsafe_allow_html=True
    )

# ─── Filter ───────────────────────────────────────────────────────────────────
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = df.index.min(), df.index.max()

dff = df.loc[start:end].copy()
active_assets  = [a for a, s in [("Gold", show_gold), ("Oil", show_oil)] if s]
active_drivers = [d for d, s in [("DXY", show_dxy), ("US10Y", show_us10y)] if s]
active_all     = active_assets + active_drivers

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>Commodity Price <span>Explorer</span></h1>
    <p>WHAT DRIVES GOLD &amp; OIL? · MACRO FACTOR ANALYSIS · 2022–2026</p>
</div>
""", unsafe_allow_html=True)

# ─── KPI Row ──────────────────────────────────────────────────────────────────
if len(dff) > 1:
    kpi_cols = st.columns(4)
    kpi_items = [("Gold","🥇","USD/oz"),("Oil","🛢️","USD/bbl"),("DXY","💵","Index"),("US10Y","📉","%")]
    for col, (key, icon, unit) in zip(kpi_cols, kpi_items):
        latest = dff[key].dropna().iloc[-1]
        first  = dff[key].dropna().iloc[0]
        chg    = (latest - first) / first * 100
        sign   = "+" if chg >= 0 else ""
        cls    = "delta-pos" if chg >= 0 else "delta-neg"
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{icon} {key} · {unit}</div>
                <div class="metric-value">{latest:,.2f}</div>
                <div class="metric-delta {cls}">{sign}{chg:.1f}% over period</div>
            </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈  Price Trends",
    "🔗  Correlations",
    "📊  Volatility",
    "🔍  Scatter Analysis",
    "💰  Return Calculator",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Price Trends + Click-to-Detail + Event Annotations
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Price Trend — Click Any Point for Details</div>', unsafe_allow_html=True)

    if not active_all:
        st.warning("Select at least one asset or driver from the sidebar.")
    else:
        fig = go.Figure()

        for col in active_all:
            series = dff[col].dropna()
            y = series / series.iloc[0] * 100 if norm_mode == "Normalised (Base=100)" else series
            fig.add_trace(go.Scatter(
                x=series.index, y=y.values,
                name=LABELS[col],
                line=dict(color=COLORS[col], width=2),
                hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m-%d}}<br>Value: %{{y:.2f}}<extra></extra>"
            ))

        # Event annotations
        if show_events:
            ref_col = active_all[0]
            ref_series = dff[ref_col].dropna()
            ref_y = ref_series / ref_series.iloc[0] * 100 if norm_mode == "Normalised (Base=100)" else ref_series
            for ev_date_str, (icon, label) in EVENTS.items():
                ev_ts = pd.Timestamp(ev_date_str)
                if start <= ev_ts <= end:
                    fig.add_shape(type="line", xref="x", yref="paper",
                                  x0=ev_date_str, x1=ev_date_str, y0=0, y1=1,
                                  line=dict(color="#333", dash="dot", width=1))
                    # Find nearest y value
                    nearest_idx = ref_y.index.get_indexer([ev_ts], method="nearest")[0]
                    y_val = ref_y.iloc[nearest_idx]
                    fig.add_annotation(
                        x=ev_date_str, y=y_val,
                        text=icon, showarrow=False,
                        font=dict(size=16), yshift=20,
                        hovertext=label
                    )

        y_title = "Normalised Value (Base=100)" if norm_mode == "Normalised (Base=100)" else "Price / Value"
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0d0d18",
            font=dict(color="#aaa", family="Space Mono"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(gridcolor="#1e1e30"),
            yaxis=dict(gridcolor="#1e1e30", title=y_title),
            hovermode="x unified",
            height=460,
            margin=dict(l=10, r=10, t=10, b=10),
        )

        # ── Click to detail ──────────────────────────────────────────────────
        selected = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="trend_chart")

        if selected and selected.get("selection") and selected["selection"].get("points"):
            pt = selected["selection"]["points"][0]
            clicked_date = pd.Timestamp(pt["x"])
            nearest_idx  = dff.index.get_indexer([clicked_date], method="nearest")[0]
            nearest_date = dff.index[nearest_idx]
            row = dff.iloc[nearest_idx]

            st.markdown(f"""
            <div class="detail-card">
                <h3>📅 DATA SNAPSHOT · {nearest_date.strftime('%d %B %Y')}</h3>
                <div class="detail-row"><span class="detail-key">🥇 Gold</span><span class="detail-val">${row['Gold']:,.2f} / oz</span></div>
                <div class="detail-row"><span class="detail-key">🛢️ WTI Oil</span><span class="detail-val">${row['Oil']:,.2f} / bbl</span></div>
                <div class="detail-row"><span class="detail-key">💵 DXY</span><span class="detail-val">{row['DXY']:.2f}</span></div>
                <div class="detail-row"><span class="detail-key">📉 10Y Yield</span><span class="detail-val">{row['US10Y']:.3f}%</span></div>
            </div>""", unsafe_allow_html=True)

            # Check proximity to events
            for ev_str, (icon, label) in EVENTS.items():
                ev_ts = pd.Timestamp(ev_str)
                if abs((nearest_date - ev_ts).days) <= 5:
                    st.markdown(f"""
                    <div class="insight-box">
                    {icon} <b>Near macro event:</b> {label} ({ev_str})<br>
                    This event likely drove significant commodity price movements around this date.
                    </div>""", unsafe_allow_html=True)

            # Store for calculator
            st.session_state["calc_buy_date"] = nearest_date.date()
            st.info(f"💰 Date saved! Switch to the **Return Calculator** tab to use **{nearest_date.strftime('%d %b %Y')}** as your buy-in date.", icon="👆")

        # Event legend
        if show_events:
            st.markdown('<div class="section-header">Macro Event Legend</div>', unsafe_allow_html=True)
            ev_cols = st.columns(3)
            for i, (ev_date_str, (icon, label)) in enumerate(EVENTS.items()):
                with ev_cols[i % 3]:
                    st.markdown(f"**{icon} {ev_date_str}** — {label}")

        if show_gold and show_dxy and len(dff) > 1:
            gold_chg = (dff["Gold"].dropna().iloc[-1] / dff["Gold"].dropna().iloc[0] - 1) * 100
            dxy_chg  = (dff["DXY"].dropna().iloc[-1]  / dff["DXY"].dropna().iloc[0]  - 1) * 100
            direction = "while the Dollar " + ("strengthened" if dxy_chg > 0 else "weakened")
            st.markdown(f"""
            <div class="insight-box">
            💡 <b>Key observation:</b> Over this period, Gold moved <b>{gold_chg:+.1f}%</b> {direction} by <b>{dxy_chg:+.1f}%</b>.
            This inverse relationship is a classic macro signal — a weaker dollar typically supports commodity prices.
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Correlations
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Rolling Correlation Analysis</div>', unsafe_allow_html=True)

    if len(active_all) < 2:
        st.info("Select at least two assets/drivers to compute correlations.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            pair_x = st.selectbox("Asset A", active_all, index=0, key="px")
        with col_b:
            remaining = [c for c in active_all if c != pair_x]
            pair_y = st.selectbox("Asset B", remaining if remaining else active_all, index=0, key="py")

        if pair_x != pair_y:
            roll_corr = dff[pair_x].rolling(roll_window).corr(dff[pair_y])
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=roll_corr.index, y=roll_corr.values,
                fill="tozeroy", line=dict(color="#f0c040", width=2),
                fillcolor="rgba(240,192,64,0.12)",
                hovertemplate="Date: %{x|%Y-%m-%d}<br>Correlation: %{y:.3f}<extra></extra>"
            ))
            fig2.add_hline(y=0,    line_dash="dash", line_color="#666")
            fig2.add_hline(y=0.5,  line_dash="dot",  line_color="#4ecca3", opacity=0.5)
            fig2.add_hline(y=-0.5, line_dash="dot",  line_color="#ff6b6b", opacity=0.5)
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0d0d18",
                font=dict(color="#aaa", family="Space Mono"),
                xaxis=dict(gridcolor="#1e1e30"),
                yaxis=dict(gridcolor="#1e1e30", title="Pearson Correlation", range=[-1.1, 1.1]),
                height=380, margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig2, use_container_width=True)

            avg_corr = roll_corr.mean()
            interp = "strong positive" if avg_corr > 0.5 else "strong negative" if avg_corr < -0.5 else "weak / unstable"
            st.markdown(f"""
            <div class="insight-box">
            📐 Average {roll_window}-day correlation between <b>{pair_x}</b> and <b>{pair_y}</b>: <b>{avg_corr:.3f}</b>
            — a <b>{interp}</b> relationship over the selected period.
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-header">Full Correlation Matrix</div>', unsafe_allow_html=True)
        corr_matrix = dff[active_all].corr()
        fig3 = px.imshow(corr_matrix, text_auto=".2f",
                         color_continuous_scale=[[0,"#ff6b6b"],[0.5,"#1a1a2e"],[1,"#f0c040"]],
                         zmin=-1, zmax=1)
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#aaa", family="Space Mono", size=12),
            height=380, margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Volatility
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Rolling Annualised Volatility</div>', unsafe_allow_html=True)

    if not active_assets:
        st.info("Select Gold and/or Oil from the sidebar.")
    else:
        returns = dff[active_assets].pct_change().dropna()
        vol = returns.rolling(vol_window).std() * np.sqrt(252) * 100

        fig4 = go.Figure()
        for col in active_assets:
            fig4.add_trace(go.Scatter(
                x=vol.index, y=vol[col], name=col,
                line=dict(color=COLORS[col], width=2),
                hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m-%d}}<br>Vol: %{{y:.1f}}%<extra></extra>"
            ))
        fig4.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0d0d18",
            font=dict(color="#aaa", family="Space Mono"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(gridcolor="#1e1e30"),
            yaxis=dict(gridcolor="#1e1e30", title="Annualised Volatility (%)"),
            height=380, margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig4, use_container_width=True)

        vol_summary = pd.DataFrame({
            "Asset": active_assets,
            "Avg Vol (%)": [vol[c].mean() for c in active_assets],
            "Max Vol (%)": [vol[c].max()  for c in active_assets],
            "Min Vol (%)": [vol[c].min()  for c in active_assets],
        }).set_index("Asset").round(2)
        st.dataframe(vol_summary, use_container_width=True)

        if show_gold and show_oil and len(active_assets) == 2:
            g_avg = vol["Gold"].mean()
            o_avg = vol["Oil"].mean()
            more_vol = "Oil" if o_avg > g_avg else "Gold"
            st.markdown(f"""
            <div class="insight-box">
            ⚡ <b>{more_vol}</b> exhibited higher average annualised volatility ({o_avg:.1f}% vs {g_avg:.1f}%).
            Oil is more sensitive to geopolitical supply shocks, while gold functions as a stable store of value.
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Scatter
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Scatter: Asset vs Macro Driver</div>', unsafe_allow_html=True)

    if not active_assets or not active_drivers:
        st.info("Select at least one asset and one macro driver from the sidebar.")
    else:
        s_col_a, s_col_b = st.columns(2)
        with s_col_a:
            sc_asset  = st.selectbox("Asset (Y axis)",  active_assets,  key="sca")
        with s_col_b:
            sc_driver = st.selectbox("Driver (X axis)", active_drivers, key="scd")

        scatter_df = dff[[sc_asset, sc_driver]].dropna().copy()
        scatter_df["Year"] = scatter_df.index.year.astype(str)

        slope, intercept, r_value, p_value, _ = stats.linregress(
            scatter_df[sc_driver], scatter_df[sc_asset]
        )
        x_range = np.linspace(scatter_df[sc_driver].min(), scatter_df[sc_driver].max(), 200)
        y_fit   = slope * x_range + intercept

        year_colors = {"2022":"#a78bfa","2023":"#4ecca3","2024":"#f0c040","2025":"#ff6b6b","2026":"#60a5fa"}
        fig5 = go.Figure()
        for yr, grp in scatter_df.groupby("Year"):
            fig5.add_trace(go.Scatter(
                x=grp[sc_driver], y=grp[sc_asset],
                mode="markers", name=str(yr),
                marker=dict(color=year_colors.get(str(yr),"#aaa"), size=5, opacity=0.7),
                hovertemplate=f"<b>{yr}</b><br>{sc_driver}: %{{x:.2f}}<br>{sc_asset}: %{{y:.2f}}<extra></extra>"
            ))
        fig5.add_trace(go.Scatter(
            x=x_range, y=y_fit, mode="lines",
            name=f"OLS (R²={r_value**2:.3f})",
            line=dict(color="#ffffff", width=2, dash="dash")
        ))
        fig5.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0d0d18",
            font=dict(color="#aaa", family="Space Mono"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(gridcolor="#1e1e30", title=LABELS[sc_driver]),
            yaxis=dict(gridcolor="#1e1e30", title=LABELS[sc_asset]),
            height=420, margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig5, use_container_width=True)

        direction = "positive" if slope > 0 else "negative"
        strength  = "strong" if abs(r_value) > 0.6 else "moderate" if abs(r_value) > 0.35 else "weak"
        sig_text  = "statistically significant (p < 0.05)" if p_value < 0.05 else "not statistically significant"
        st.markdown(f"""
        <div class="insight-box">
        📊 <b>OLS Regression:</b> {sc_asset} ~ {sc_driver}<br>
        Slope = <b>{slope:.4f}</b> | R² = <b>{r_value**2:.3f}</b> | p-value = <b>{p_value:.4f}</b><br>
        → <b>{strength.capitalize()} {direction}</b> linear relationship, {sig_text}.
        A 1-unit increase in <b>{sc_driver}</b> is associated with a <b>{slope:.2f}</b> unit change in <b>{sc_asset}</b>.
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Return Calculator
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">💰 Hypothetical Return Calculator</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
    💡 <b>Tip:</b> Click any data point on the <b>Price Trends</b> chart to auto-fill the buy-in date here.
    </div>""", unsafe_allow_html=True)

    default_buy = st.session_state.get("calc_buy_date", df.index.min().date())

    calc_col1, calc_col2, calc_col3 = st.columns(3)
    with calc_col1:
        calc_asset = st.selectbox("Asset", ["Gold", "Oil"], key="calc_asset")
    with calc_col2:
        buy_date = st.date_input("Buy-in Date", value=default_buy,
                                 min_value=df.index.min().date(),
                                 max_value=df.index.max().date(), key="buy_date")
    with calc_col3:
        sell_date = st.date_input("Sell Date", value=df.index.max().date(),
                                  min_value=df.index.min().date(),
                                  max_value=df.index.max().date(), key="sell_date")

    investment = st.number_input("Investment Amount (USD)", min_value=100,
                                 max_value=10_000_000, value=10_000, step=500)

    if st.button("Calculate Return", type="primary"):
        buy_ts  = pd.Timestamp(buy_date)
        sell_ts = pd.Timestamp(sell_date)

        if buy_ts >= sell_ts:
            st.error("Sell date must be after buy-in date.")
        else:
            buy_idx  = df.index.get_indexer([buy_ts],  method="nearest")[0]
            sell_idx = df.index.get_indexer([sell_ts], method="nearest")[0]
            buy_price        = df[calc_asset].iloc[buy_idx]
            sell_price       = df[calc_asset].iloc[sell_idx]
            actual_buy_date  = df.index[buy_idx]
            actual_sell_date = df.index[sell_idx]

            pct_return   = (sell_price - buy_price) / buy_price * 100
            abs_return   = investment * pct_return / 100
            final_value  = investment + abs_return
            holding_days = (actual_sell_date - actual_buy_date).days
            ann_return   = ((sell_price / buy_price) ** (365 / max(holding_days, 1)) - 1) * 100

            color = "#4ecca3" if pct_return >= 0 else "#ff6b6b"
            sign  = "+" if pct_return >= 0 else ""

            st.markdown(f"""
            <div class="calc-result" style="border-color:{color};">
                <div class="big" style="color:{color};">{sign}{pct_return:.2f}%</div>
                <div class="sub">TOTAL RETURN · {holding_days} DAYS HELD</div>
            </div>""", unsafe_allow_html=True)

            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Buy Price",   f"${buy_price:,.2f}",  f"{actual_buy_date.strftime('%d %b %Y')}")
            r2.metric("Sell Price",  f"${sell_price:,.2f}", f"{actual_sell_date.strftime('%d %b %Y')}")
            r3.metric("P&L (USD)",   f"${abs_return:+,.2f}")
            r4.metric("Final Value", f"${final_value:,.2f}", f"Ann. {ann_return:+.1f}%")

            # Mini chart for holding period
            sub_df = df[calc_asset].loc[actual_buy_date:actual_sell_date]

            # Parse hex color to rgb for fillcolor
            hex_col = color.lstrip("#")
            r_int, g_int, b_int = int(hex_col[0:2],16), int(hex_col[2:4],16), int(hex_col[4:6],16)

            x_dates = sub_df.index.strftime("%Y-%m-%d").tolist()
            buy_str  = actual_buy_date.strftime("%Y-%m-%d")
            sell_str = actual_sell_date.strftime("%Y-%m-%d")

            fig6 = go.Figure()
            fig6.add_trace(go.Scatter(
                x=x_dates, y=sub_df.values,
                fill="tozeroy", line=dict(color=color, width=2),
                fillcolor=f"rgba({r_int},{g_int},{b_int},0.12)"
            ))
            # Use add_shape instead of add_vline to avoid Timestamp issues
            for vx, vcol, vlabel in [(buy_str, "#4ecca3", "BUY"), (sell_str, "#ff6b6b", "SELL")]:
                fig6.add_shape(type="line", xref="x", yref="paper",
                               x0=vx, x1=vx, y0=0, y1=1,
                               line=dict(color=vcol, dash="dash", width=2))
                fig6.add_annotation(x=vx, y=1, yref="paper", text=vlabel,
                                    showarrow=False, font=dict(color=vcol, size=12), yshift=8)
            fig6.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0d0d18",
                font=dict(color="#aaa", family="Space Mono"),
                xaxis=dict(gridcolor="#1e1e30"),
                yaxis=dict(gridcolor="#1e1e30", title=LABELS[calc_asset]),
                height=280, showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig6, use_container_width=True)

            # Events during holding period
            for ev_str, (icon, label) in EVENTS.items():
                ev_ts = pd.Timestamp(ev_str)
                if actual_buy_date <= ev_ts <= actual_sell_date:
                    st.markdown(f"""
                    <div class="insight-box">
                    {icon} <b>Macro event during holding period:</b> {label} ({ev_str})<br>
                    This event likely influenced {calc_asset} price movements during your holding window.
                    </div>""", unsafe_allow_html=True)
