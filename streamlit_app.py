import streamlit as st
import sys
import os
sys.path.append('src')

from data_fetcher import LiquidationDataFetcher
from visualizer import LiquidationHeatmapVisualizer
import plotly.graph_objects as go

st.set_page_config(
    page_title="Crypto Liquidation Heatmap",
    page_icon="📊",
    layout="wide"
)

st.title("🔥 Cryptocurrency Liquidation Heatmap")
st.caption("Real-time liquidation analysis similar to Coinglass")

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    symbol = st.selectbox(
        "Trading Pair",
        ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT"],
        index=0
    )
    
    exchange = st.selectbox(
        "Exchange",
        ["binance", "okx", "bybit"],
        index=0
    )
    
    st.subheader("📊 Analysis Period")
    duration_type = st.radio(
        "Duration Type",
        ["Real-time Snapshot", "Historical Analysis"],
        index=0
    )
    
    if duration_type == "Historical Analysis":
        time_period = st.selectbox(
            "Time Period",
            [
                ("12 Hours", "12h", 720),
                ("24 Hours", "1d", 1440),
                ("2 Days", "2d", 2880),
                ("3 Days", "3d", 4320)
            ],
            index=1,
            format_func=lambda x: x[0]
        )
        selected_timeframe = time_period[1]
        analysis_minutes = time_period[2]
        
        st.info(f"📈 Analyzing liquidations over {time_period[0]}")
    else:
        selected_timeframe = "current"
        analysis_minutes = 0
        st.info("⚡ Real-time liquidation snapshot")
    
    # Enhanced refresh options
    refresh_mode = st.radio("Refresh Mode", ["Manual", "Auto-refresh"], index=0)
    
    if refresh_mode == "Auto-refresh":
        refresh_interval = st.selectbox(
            "Update Interval",
            [5, 10, 30, 60, 300],
            index=2,
            format_func=lambda x: f"{x} seconds" if x < 60 else f"{x//60} minute{'s' if x//60 > 1 else ''}"
        )
        auto_refresh = True
    else:
        auto_refresh = False
        refresh_interval = 30
    
    if st.button("🔄 Refresh Data"):
        st.rerun()

# Main content
try:
    if duration_type == "Historical Analysis":
        spinner_text = f"Analyzing {symbol} liquidations over {time_period[0]} from {exchange}..."
    else:
        spinner_text = f"Fetching real-time {symbol} data from {exchange}..."
        
    with st.spinner(spinner_text):
        fetcher = LiquidationDataFetcher(exchange)
        if duration_type == "Historical Analysis":
            data = fetcher.get_historical_liquidation_data(symbol, selected_timeframe, analysis_minutes)
        else:
            data = fetcher.get_liquidation_heatmap_data(symbol)
    
    if data:
        # Show analysis type and additional info
        analysis_type = data.get('analysis_type', 'real-time')
        
        if analysis_type == 'historical':
            st.success(f"📊 Historical Analysis: {data['timeframe']} over {data.get('duration_minutes', 0)/60:.1f} hours")
            
            # Show historical price stats if available
            if 'price_stats' in data:
                stats = data['price_stats']
                col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
                with col_stats1:
                    st.metric("Price Range Low", f"${stats['min']:,.2f}")
                with col_stats2:
                    st.metric("Price Range High", f"${stats['max']:,.2f}")
                with col_stats3:
                    st.metric("Average Price", f"${stats['avg']:,.2f}")
                with col_stats4:
                    st.metric("Volatility", f"{stats['volatility']*100:.2f}%")
        else:
            st.info("⚡ Real-time liquidation snapshot")
        
        # Display current price prominently
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label=f"Current {symbol} Price",
                value=f"${data['current_price']:,.2f}",
                delta=None
            )
        with col2:
            long_5x = data['liquidation_levels']['long_liquidations'][0]
            risk_emoji = "🔴" if long_5x.get('risk_level') == 'high' else "🟡" if long_5x.get('risk_level') == 'medium' else "🟢"
            st.metric(
                label=f"{risk_emoji} Long 5x Liquidation",
                value=f"${long_5x['price']:,.2f}",
                delta=f"-{long_5x['distance_percent']:.1f}%"
            )
        with col3:
            short_5x = data['liquidation_levels']['short_liquidations'][0]
            risk_emoji = "🔴" if short_5x.get('risk_level') == 'high' else "🟡" if short_5x.get('risk_level') == 'medium' else "🟢"
            st.metric(
                label=f"{risk_emoji} Short 5x Liquidation", 
                value=f"${short_5x['price']:,.2f}",
                delta=f"+{short_5x['distance_percent']:.1f}%"
            )
        
        # Create visualizations
        visualizer = LiquidationHeatmapVisualizer()
        
        # Main heatmap
        st.subheader("📈 Liquidation Heatmap")
        fig_heatmap = visualizer.create_interactive_heatmap(data)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Leverage analysis
        st.subheader("⚖️ Leverage Distribution")
        fig_leverage = visualizer.create_leverage_distribution(data)
        st.plotly_chart(fig_leverage, use_container_width=True)
        
        # Liquidation tables
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔴 Long Liquidations")
            long_df = []
            for liq in data['liquidation_levels']['long_liquidations']:
                risk_level = liq.get('risk_level', 'unknown')
                risk_emoji = "🔴" if risk_level == 'high' else "🟡" if risk_level == 'medium' else "🟢"
                long_df.append({
                    "Leverage": f"{liq['leverage']}x",
                    "Price": f"${liq['price']:,.2f}",
                    "Distance": f"{liq['distance_percent']:.2f}%",
                    "Risk": f"{risk_emoji} {risk_level.title()}"
                })
            st.dataframe(long_df, hide_index=True)
        
        with col2:
            st.subheader("🟢 Short Liquidations")
            short_df = []
            for liq in data['liquidation_levels']['short_liquidations']:
                risk_level = liq.get('risk_level', 'unknown')
                risk_emoji = "🔴" if risk_level == 'high' else "🟡" if risk_level == 'medium' else "🟢"
                short_df.append({
                    "Leverage": f"{liq['leverage']}x",
                    "Price": f"${liq['price']:,.2f}",
                    "Distance": f"{liq['distance_percent']:.2f}%",
                    "Risk": f"{risk_emoji} {risk_level.title()}"
                })
            st.dataframe(short_df, hide_index=True)
        
    else:
        st.error("❌ Failed to fetch data. Please try again.")
        
except Exception as e:
    st.error(f"❌ Error: {str(e)}")

# Auto-refresh with custom interval
if auto_refresh:
    import time
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.caption("📊 Built with CCXT • Data from live exchanges • Updates every refresh")