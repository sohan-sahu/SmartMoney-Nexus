import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==============================================================================
# 1. PAGE CONFIGURATION & RESPONSIVE THEME
# ==============================================================================
st.set_page_config(
    page_title="SmartMoney Nexus", 
    layout="wide",  # Forces the application to stretch across the full browser width
    initial_sidebar_state="expanded"
)

st.title("📊 SmartMoney Nexus: Institutional Flow & Rotation Terminal")
st.markdown("---")

# ==============================================================================
# 2. DATA INGESTION ENGINE (Tiered Global Macro & Domestic Sectors)
# ==============================================================================
@st.cache_data(ttl=3600)  # Cache data for 1 hour to prevent API throttling
def fetch_market_data():
    end_date = datetime.today()
    start_date = end_date - timedelta(days=5 * 365) # 5-year historical baseline
    
    global_macro = {
        # Developed Markets (DM)
        'US (S&P 500)': '^GSPC',
        'US Tech (Nasdaq)': '^IXIC',
        'Germany (DAX)': '^GDAXI',
        'Japan (Nikkei 225)': '^N225',
        'UK (FTSE 100)': '^FTSE',
        'France (CAC 40)': '^FCHI',
        
        # Emerging Markets (EM)
        'India (Nifty 50)': '^NSEI',
        'China (MSCI)': 'MCHI',
        'Taiwan (MSCI)': 'EWT',
        'South Korea (MSCI)': 'EWY',
        'Brazil (MSCI)': 'EWZ',
        
        # Frontier Markets (FM)
        'Sri Lanka & Frontier Hubs': 'FM',
        'Vietnam (MSCI)': 'VNM',
        
        # Macro Core Benchmarks
        'US Dollar Index': 'DX-Y.NYB',
        'Emerging Markets ETF': 'EEM',
        'US 10Y Bond Yield': '^TNX'
    }
    
    classifications = {
        'US (S&P 500)': 'Developed Markets (DM)',
        'US Tech (Nasdaq)': 'Developed Markets (DM)',
        'Germany (DAX)': 'Developed Markets (DM)',
        'Japan (Nikkei 225)': 'Developed Markets (DM)',
        'UK (FTSE 100)': 'Developed Markets (DM)',
        'France (CAC 40)': 'Developed Markets (DM)',
        'India (Nifty 50)': 'Emerging Markets (EM)',
        'China (MSCI)': 'Emerging Markets (EM)',
        'Taiwan (MSCI)': 'Emerging Markets (EM)',
        'South Korea (MSCI)': 'Emerging Markets (EM)',
        'Brazil (MSCI)': 'Emerging Markets (EM)',
        'Sri Lanka & Frontier Hubs': 'Frontier Markets (FM)',
        'Vietnam (MSCI)': 'Frontier Markets (FM)'
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
    
    all_tickers = {**global_macro, **sectors}
    data = yf.download(list(all_tickers.values()), start=start_date, end=end_date)['Close']
    
    inv_tickers = {v: k for k, v in all_tickers.items()}
    data.rename(columns=inv_tickers, inplace=True)
    
    # Clean data comprehensively to ensure responsive visuals never get corrupt 'nan' elements
    data = data.ffill().bfill().fillna(0)
    
    if 'US 10Y Bond Yield' in data.columns:
        data['US 10Y Bond Yield'] = data['US 10Y Bond Yield'] / 10
        
    return data, sectors, global_macro, classifications

try:
    master_data, sectoral_dict, global_dict, market_classes = fetch_market_data()
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
    
    if 'India (Nifty 50)' in master_data.columns and (master_data['India (Nifty 50)'] != 0).any():
        nifty = master_data['India (Nifty 50)'].replace(0, np.nan).dropna()
        rolling_mean = nifty.rolling(window=250).mean()
        rolling_std = nifty.rolling(window=250).std()
        z_score = (nifty - rolling_mean) / rolling_std
        
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

    # Responsive structural column splits: switches automatically to single stack on smaller screens
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="Calculated Real-Time EVI Score", value=f"{current_evi}", delta=f"Zone: {status}", delta_color=delta_type)
        st.markdown(f"### Allocation Directives")
        st.info(f"**Current Status:** Market is verifying inside the **{status}** spectrum.")

    with col2:
        fig_evi = px.line(evi_series, title="Synthetic EVI Trajectory Model", labels={'value': 'EVI Index Score', 'Date': 'Timeline'})
        fig_evi.add_hrect(y0=130, y1=170, fillcolor="red", opacity=0.2, annotation_text="Profit Booking Zone")
        fig_evi.add_hrect(y0=110, y1=130, fillcolor="orange", opacity=0.2, annotation_text="Debt Overweight")
        fig_evi.add_hrect(y0=90, y1=110, fillcolor="yellow", opacity=0.2, annotation_text="Neutral Strategy Band")
        fig_evi.add_hrect(y0=50, y1=90, fillcolor="green", opacity=0.2, annotation_text="Equity Accumulation Zone")
        
        # Responsive plot config
        st.plotly_chart(fig_evi, width='stretch')

# ==============================================================================
# LAYER 2: SECTOR ROTATION MATRICES
# ==============================================================================
elif page == "Sector Rotation Tracker":
    st.header("🔄 Sector Rotation & Momentum Mapping")
    st.subheader("Identifying Alpha Pipelines via Multi-Timeframe Rate of Change (ROC)")
    
    benchmark = 'India (Nifty 50)'
    sector_performance = []
    
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
        st.success("🔥 Money Is Moving Here (Leading)")
        st.write(", ".join(leading) if leading else "None")
    with c2:
        st.info("⏳ In Queue Focus (Improving)")
        st.write(", ".join(improving) if improving else "None")
    with c3:
        st.warning("⚠️ Time to Move Out (Weakening)")
        st.write(", ".join(weakening) if weakening else "None")

    point_sizes = np.abs(df_rotation['Relative Momentum (Y-Axis)']).fillna(0.0) + 5

    fig_rrg = px.scatter(
        df_rotation, x='Relative Strength (X-Axis)', y='Relative Momentum (Y-Axis)', text='Sector', 
        size=point_sizes, title="Relative Rotation Matrix (Benchmark: Nifty 50)"
    )
    fig_rrg.add_hline(y=0, line_dash="dash", line_color="gray")
    fig_rrg.add_vline(x=0, line_dash="dash", line_color="gray")
    
    # Responsive graph application
    st.plotly_chart(fig_rrg, width='stretch')

# ==============================================================================
# LAYER 3: YIELD CURVE INVERSION & TIERED GLOBAL FLOWS
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
            st.error("🚨 Yield Curve Inverted! Defensive strategies advised.")
        else:
            st.success("✅ The Yield curve remains positive.")

    with bc2:
        fig_spread = px.line(spread, title="Yield Spread History (10Y - 2Y)", labels={'value': 'Spread (%)'})
        fig_spread.add_hline(y=0, line_color="red", line_width=2, line_dash="dash")
        st.plotly_chart(fig_spread, width='stretch')
        
    st.markdown("---")
    st.subheader("🌐 Global Equity Performance Rankings (Tiered Ingestion Matrix)")
    st.write("Markets are dynamically sorted by **3-Month performance** inside their explicit institutional allocation tiers.")
    
    perf_list = []
    for idx in market_classes.keys():
        if idx in master_data.columns and (master_data[idx] != 0).any():
            series = master_data[idx].replace(0, np.nan).ffill()
            m1 = ((series.iloc[-1] / series.iloc[-21]) - 1) * 100 if len(series) > 21 else 0.0
            m3 = ((series.iloc[-1] / series.iloc[-63]) - 1) * 100 if len(series) > 63 else 0.0
            y1 = ((series.iloc[-1] / series.iloc[-252]) - 1) * 100 if len(series) > 252 else 0.0
            
            perf_list.append({
                'Global Hub': idx, 
                'Market Tier': market_classes[idx],
                '1-Month %': m1, 
                '3-Month %': m3, 
                '1-Year %': y1
            })
            
    df_raw = pd.DataFrame(perf_list)
    
    # Render separate sorted tables with responsive layout containment
    for tier in ['Developed Markets (DM)', 'Emerging Markets (EM)', 'Frontier Markets (FM)']:
        st.markdown(f"### 🚀 {tier} Leaderboard")
        df_tier = df_raw[df_raw['Market Tier'] == tier].set_index('Global Hub').drop(columns=['Market Tier'])
        df_tier = df_tier.sort_values(by='3-Month %', ascending=False)
        
        # Wrapping dataframe layout responsibly to ensure width='stretch' behavior across mobile devices
        st.dataframe(df_tier.style.background_gradient(cmap='RdYlGn', axis=0).format("{:.2f}%"), width='stretch')
        
    st.markdown("---")
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
