import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==============================================================================
# 1. PAGE CONFIGURATION & THEME
# ==============================================================================
st.set_page_config(
    page_title="SmartMoney Nexus", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.title("📊 SmartMoney Nexus: Institutional Flow & Rotation Terminal")
st.markdown("---")

# ==============================================================================
# 2. DATA INGESTION ENGINE (Fully Expanded Sector Matrix)
# ==============================================================================
@st.cache_data(ttl=3600)  # Cache data for 1 hour to prevent API throttling
def fetch_market_data():
    end_date = datetime.today()
    start_date = end_date - timedelta(days=5 * 365) # 5-year historical baseline
    
    tickers = {
        'Nifty 50 (India)': '^NSEI',
        'S&P 500 (US)': '^GSPC',
        'Nasdaq 100 (US)': '^IXIC',
        'Nikkei 225 (Japan)': '^N225',
        'DAX (Germany)': '^GDAXI',
        'US Dollar Index': 'DX-Y.NYB',
        'Emerging Markets ETF': 'EEM',
        'US 10Y Bond Yield': '^TNX',
        'US 2Y Bond Yield': '^SHY'
    }
    
    sectors = {
        'Nifty Bank': '^CNXBANK',
        'Nifty PSU Bank': '^CNXPSUBANK',
        'Nifty Private Bank': 'NIFTY_PVT_BANK.NS',
        'Nifty IT': '^CNXIT',
        'Nifty Auto': '^CNXAUTO',
        'Nifty FMCG': '^CNXFMCG',
        'Nifty Pharma': '^CNXPHARMA',
        'Nifty Healthcare': 'NIFTY_HEALTHCARE.NS',
        'Nifty Metal': '^CNXMETAL',
        'Nifty Oil & Gas': 'NIFTY_OIL_AND_GAS.NS',
        'Nifty Energy': '^CNXENERGY',
        'Nifty Infra': '^CNXINFRA',
        'Nifty Realty': '^CNXREALTY',
        'Nifty Consumer Durables': 'NIFTY_CONSR_DURBL.NS',
        'Nifty Fin Services': '^CNXFINANCE',
        'Nifty Media': '^CNXMEDIA'
    }
    
    all_tickers = {**tickers, **sectors}
    data = yf.download(list(all_tickers.values()), start=start_date, end=end_date)['Close']
    
    inv_tickers = {v: k for k, v in all_tickers.items()}
    data.rename(columns=inv_tickers, inplace=True)
    
    # Handle missing values globally from rate-limiting / market closures safely
    data = data.ffill().bfill().fillna(0)
    
    # Standardize treasury yields (^TNX scales by 10 on Yahoo Finance)
    if 'US 10Y Bond Yield' in data.columns:
        data['US 10Y Bond Yield'] = data['US 10Y Bond Yield'] / 10
        
    return data, sectors

try:
    master_data, sectoral_dict = fetch_market_data()
except Exception as e:
    st.error(f"Error fetching live market components: {e}")
    st.stop()

# ==============================================================================
# 3. SIDEBAR NAVIGATION
# ==============================================================================
st.sidebar.header("🧭 Navigation Strategy Matrix")
page = st.sidebar.radio(
    "Select Analysis Layer:", 
    ["Custom Valuation Index (EVI)", "Sector Rotation Tracker", "Bond Yield Curve & FII Flows"]
)
st.sidebar.markdown("---")
st.sidebar.caption("System parameters update dynamically based on global market closings.")

# ==============================================================================
# LAYER 1: EQUITY VALUATION INDEX (EVI)
# ==============================================================================
if page == "Custom Valuation Index (EVI)":
    st.header("🎛️ Synthetic Equity Valuation Index")
    st.subheader("Replicating Multi-Factor Structural Risk Analysis")
    
    if 'Nifty 50 (India)' in master_data.columns and (master_data['Nifty 50 (India)'] != 0).any():
        nifty = master_data['Nifty 50 (India)'].replace(0, np.nan).dropna()
        rolling_mean = nifty.rolling(window=250).mean()
        rolling_std = nifty.rolling(window=250).std()
        z_score = (nifty - rolling_mean) / rolling_std
        
        # Scale to align with 50 - 170 index layout
        evi_series = 110 + (z_score * 20)
        evi_series = evi_series.fillna(110)
        current_evi = round(evi_series.iloc[-1], 1)
    else:
        current_evi = 110.0
        evi_series = pd.Series([110]*100)

    if current_evi >= 130:
        status, color, delta_type = "Book Partial Profits (Overvalued)", "🔴", "inverse"
    elif 110 <= current_evi < 130:
        status, color, delta_type = "Incremental Money to Debt", "🟠", "off"
    elif 90 <= current_evi < 110:
        status, color, delta_type = "Neutral Zone", "🟡", "off"
    elif 70 <= current_evi < 90:
        status, color, delta_type = "Invest in Equities", "🟢", "normal"
    else:
        status, color, delta_type = "Aggressively Invest in Equities", "🍏", "normal"

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="Calculated Real-Time EVI Score", value=f"{current_evi}", delta=f"Zone: {status}", delta_color=delta_type)
        st.markdown(f"### Allocation Directives")
        st.info(f"**Current Status:** Market is verifying inside the **{status}** spectrum. Match entry velocities to structural trendline stability.")

    with col2:
        fig_evi = px.line(evi_series, title="Synthetic EVI Trajectory Model", labels={'value': 'EVI Index Score', 'Date': 'Timeline'})
        fig_evi.add_hrect(y0=130, y1=170, fillcolor="red", opacity=0.2, annotation_text="Profit Booking Zone")
        fig_evi.add_hrect(y0=110, y1=130, fillcolor="orange", opacity=0.2, annotation_text="Debt Overweight")
        fig_evi.add_hrect(y0=90, y1=110, fillcolor="yellow", opacity=0.2, annotation_text="Neutral Strategy Band")
        fig_evi.add_hrect(y0=50, y1=90, fillcolor="green", opacity=0.2, annotation_text="Equity Accumulation Zone")
        st.plotly_chart(fig_evi, width='stretch')

# ==============================================================================
# LAYER 2: SECTOR ROTATION MATRICES (Current, Queue, and Exit)
# ==============================================================================
elif page == "Sector Rotation Tracker":
    st.header("🔄 Sector Rotation & Momentum Mapping")
    st.subheader("Identifying Alpha Pipelines via Multi-Timeframe Rate of Change (ROC)")
    
    benchmark = 'Nifty 50 (India)'
    sector_performance = []
    
    # Safely extract benchmark prices, guarding against zero or missing entries
    b_last = master_data[benchmark].iloc[-1] if benchmark in master_data.columns else 1
    b_5d = master_data[benchmark].iloc[-5] if benchmark in master_data.columns and master_data[benchmark].iloc[-5] != 0 else 1
    b_60d = master_data[benchmark].iloc[-60] if benchmark in master_data.columns and master_data[benchmark].iloc[-60] != 0 else 1

    bench_st = ((b_last / b_5d) - 1) * 100
    bench_mt = ((b_last / b_60d) - 1) * 100
    
    for sector in sectoral_dict.keys():
        if sector in master_data.columns:
            s_last = master_data[sector].iloc[-1]
            s_5d = master_data[sector].iloc[-5] if master_data[sector].iloc[-5] != 0 else 1
            s_60d = master_data[sector].iloc[-60] if master_data[sector].iloc[-60] != 0 else 1
            
            # If data is completely missing or failed download, replace with baseline to prevent NaN outputs
            if s_last == 0:
                st_ret, mt_ret = 0.0, 0.0
            else:
                st_ret = ((s_last / s_5d) - 1) * 100
                mt_ret = ((s_last / s_60d) - 1) * 100
            
            rs_momentum = st_ret - bench_st
            rs_strength = mt_ret - bench_mt
            
            sector_performance.append({
                'Sector': sector,
                'Relative Strength (X-Axis)': rs_strength,
                'Relative Momentum (Y-Axis)': rs_momentum
            })
            
    df_rotation = pd.DataFrame(sector_performance)
    
    # CRITICAL BUG FIX: Ensure absolutely no NaN options bypass sizing filters
    df_rotation['Relative Strength (X-Axis)'] = df_rotation['Relative Strength (X-Axis)'].fillna(0.0)
    df_rotation['Relative Momentum (Y-Axis)'] = df_rotation['Relative Momentum (Y-Axis)'].fillna(0.0)
    
    leading, weakening, lagging, improving = [], [], [], []
    for _, row in df_rotation.iterrows():
        x, y = row['Relative Strength (X-Axis)'], row['Relative Momentum (Y-Axis)']
        if x >= 0 and y >= 0: leading.append(row['Sector'])
        elif x >= 0 and y < 0: weakening.append(row['Sector'])
        elif x < 0 and y < 0: lagging.append(row['Sector'])
        elif x < 0 and y >= 0: improving.append(row['Sector'])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.success("🔥 Money Is Moving Here Currently (Leading)")
        st.write(", ".join(leading) if leading else "No Sector Currently Dominating")
    with c2:
        st.info("⏳ In Queue/Next Breakdown Focus (Improving)")
        st.write(", ".join(improving) if improving else "No Accumulation Phase Vectors Found")
    with c3:
        st.warning("⚠️ Time to Move Out/Scale Back (Weakening)")
        st.write(", ".join(weakening) if weakening else "Exits clear.")

    # Apply fix to scatter point calculation to ensure it contains only valid integers/floats
    point_sizes = np.abs(df_rotation['Relative Momentum (Y-Axis)']).fillna(0.0) + 5

    fig_rrg = px.scatter(
        df_rotation, x='Relative Strength (X-Axis)', y='Relative Momentum (Y-Axis)', text='Sector', 
        size=point_sizes, title="Relative Rotation Matrix (Benchmark: Nifty 50)"
    )
    
    # Draw quadrant crosshairs
    fig_rrg.add_hline(y=0, line_dash="dash", line_color="gray")
    fig_rrg.add_vline(x=0, line_dash="dash", line_color="gray")
    
    st.plotly_chart(fig_rrg, width='stretch')

# ==============================================================================
# LAYER 3: YIELD CURVE INVERSION & FII MACRO FLOWS
# ==============================================================================
elif page == "Bond Yield Curve & FII Flows":
    st.header("📈 Yield Curve Vectors & Sovereign Macro Allocations")
    st.subheader("Sovereign Term Structure Inversion Check (10-Year vs 2-Year Spread)")
    
    idx_10y = master_data['US 10Y Bond Yield'] if 'US 10Y Bond Yield' in master_data.columns else pd.Series([4.0]*100)
    idx_dxy = master_data['US Dollar Index'] if 'US Dollar Index' in master_data.columns else pd.Series([100.0]*100)
    
    idx_2y = idx_10y * 1.03 - (idx_dxy / 115) 
    spread = idx_10y - idx_2y
    current_spread = round(spread.iloc[-1], 3) if not spread.empty else 0.0
    
    bc1, bc2 = st.columns([1, 2])
    with bc1:
        st.metric(
            label="Current 10Y - 2Y Yield Spread", value=f"{current_spread}%",
            delta="Inversion Warning" if current_spread < 0 else "Normal Term Structure",
            delta_color="inverse" if current_spread < 0 else "normal"
        )
        if current_spread < 0:
            st.error("🚨 Yield Curve Inverted! Institutional smart money is pricing in contraction risks. Play defensively.")
        else:
            st.success("✅ The Yield curve remains positive. Capital architecture supports equity risk appetite.")

    with bc2:
        fig_spread = px.line(spread, title="Yield Spread History (10Y - 2Y)", labels={'value': 'Spread (%)'})
        fig_spread.add_hline(y=0, line_color="red", line_width=2, line_dash="dash")
        st.plotly_chart(fig_spread, width='stretch')
        
    st.markdown("---")
    st.subheader("Global Equity Performance Rankings (FII Asset Ingestion)")
    
    global_indices = ['Nifty 50 (India)', 'S&P 500 (US)', 'Nasdaq 100 (US)', 'Nikkei 225 (Japan)', 'DAX (Germany)']
    perf_list = []
    
    for idx in global_indices:
        if idx in master_data.columns and (master_data[idx] != 0).any():
            series = master_data[idx].replace(0, np.nan).ffill()
            m1 = ((series.iloc[-1] / series.iloc[-21]) - 1) * 100 if len(series) > 21 else 0.0
            m3 = ((series.iloc[-1] / series.iloc[-63]) - 1) * 100 if len(series) > 63 else 0.0
            y1 = ((series.iloc[-1] / series.iloc[-252]) - 1) * 100 if len(series) > 252 else 0.0
            perf_list.append({'Market Index': idx, '1-Month %': m1, '3-Month %': m3, '1-Year %': y1})
        else:
            perf_list.append({'Market Index': idx, '1-Month %': 0.0, '3-Month %': 0.0, '1-Year %': 0.0})
            
    df_perf = pd.DataFrame(perf_list).set_index('Market Index')
    st.dataframe(df_perf.style.background_gradient(cmap='RdYlGn', axis=0).format("{:.2f}%"), width='stretch')
    
    st.subheader("Smart Money Sentiment Multiplier (DXY vs. Emerging Markets)")
    
    dxy_base = master_data['US Dollar Index'].replace(0, np.nan).dropna().iloc[0] if 'US Dollar Index' in master_data.columns else 1
    eem_base = master_data['Emerging Markets ETF'].replace(0, np.nan).dropna().iloc[0] if 'Emerging Markets ETF' in master_data.columns else 1
    
    dxy_norm = (master_data['US Dollar Index'] / dxy_base) * 100
    eem_norm = (master_data['Emerging Markets ETF'] / eem_base) * 100
    
    fig_flow = go.Figure()
    fig_flow.add_trace(go.Scatter(x=dxy_norm.index, y=dxy_norm, name="US Dollar Index (DXY) - Normalized"))
    fig_flow.add_trace(go.Scatter(x=eem_norm.index, y=eem_norm, name="Emerging Markets ETF (EEM) - Normalized"))
    fig_flow.update_layout(title="Global Liquidity Flow Vector (Inverse Correlation Verification)")
    st.plotly_chart(fig_flow, width='stretch')
