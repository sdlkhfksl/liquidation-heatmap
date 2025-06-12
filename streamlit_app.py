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
    
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    
    if st.button("🔄 Refresh Data"):
        st.rerun()

# Main content
try:
    with st.spinner(f"Fetching {symbol} data from {exchange}..."):
        fetcher = LiquidationDataFetcher(exchange)
        data = fetcher.get_liquidation_heatmap_data(symbol)
    
    if data:
        # Display current price prominently
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label=f"{symbol} Price",
                value=f"${data['current_price']:,.2f}",
                delta=None
            )
        with col2:
            long_5x = data['liquidation_levels']['long_liquidations'][0]
            st.metric(
                label="Long 5x Liquidation",
                value=f"${long_5x['price']:,.2f}",
                delta=f"-{long_5x['distance_percent']:.1f}%"
            )
        with col3:
            short_5x = data['liquidation_levels']['short_liquidations'][0]
            st.metric(
                label="Short 5x Liquidation", 
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
                long_df.append({
                    "Leverage": f"{liq['leverage']}x",
                    "Price": f"${liq['price']:,.2f}",
                    "Distance": f"{liq['distance_percent']:.2f}%"
                })
            st.dataframe(long_df, hide_index=True)
        
        with col2:
            st.subheader("🟢 Short Liquidations")
            short_df = []
            for liq in data['liquidation_levels']['short_liquidations']:
                short_df.append({
                    "Leverage": f"{liq['leverage']}x",
                    "Price": f"${liq['price']:,.2f}",
                    "Distance": f"{liq['distance_percent']:.2f}%"
                })
            st.dataframe(short_df, hide_index=True)
        
    else:
        st.error("❌ Failed to fetch data. Please try again.")
        
except Exception as e:
    st.error(f"❌ Error: {str(e)}")

# Auto-refresh
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()

# Footer
st.markdown("---")
st.caption("📊 Built with CCXT • Data from live exchanges • Updates every refresh")