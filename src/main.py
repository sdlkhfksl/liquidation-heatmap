import sys
import os
import argparse
from datetime import datetime
import plotly.io as pio
from data_fetcher import LiquidationDataFetcher
from visualizer import LiquidationHeatmapVisualizer


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate cryptocurrency liquidation heatmap')
    parser.add_argument('--symbol', type=str, default='BTC/USDT', 
                       help='Trading pair symbol (default: BTC/USDT)')
    parser.add_argument('--exchange', type=str, default='binance',
                       help='Exchange name (default: binance)')
    parser.add_argument('--output', type=str, default='interactive',
                       choices=['interactive', 'static', 'both'],
                       help='Output type (default: interactive)')
    parser.add_argument('--save-path', type=str, default=None,
                       help='Path to save the output (for static plots)')
    
    args = parser.parse_args()
    
    print(f"Generating liquidation heatmap for {args.symbol} on {args.exchange}...")
    
    # Initialize data fetcher
    fetcher = LiquidationDataFetcher(args.exchange)
    
    # Fetch data
    print("Fetching market data...")
    data = fetcher.get_liquidation_heatmap_data(args.symbol)
    
    if not data:
        print("Error: Unable to fetch data. Please check your connection and symbol.")
        return
    
    print(f"Current price: ${data['current_price']:,.2f}")
    print(f"Data points: {len(data['heatmap_data'])}")
    
    # Initialize visualizer
    visualizer = LiquidationHeatmapVisualizer()
    
    # Create visualizations
    if args.output in ['interactive', 'both']:
        print("Creating interactive heatmap...")
        fig_heatmap = visualizer.create_interactive_heatmap(data)
        fig_leverage = visualizer.create_leverage_distribution(data)
        
        # Save or show interactive plots
        if args.save_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            heatmap_path = f"{args.save_path}_heatmap_{timestamp}.html"
            leverage_path = f"{args.save_path}_leverage_{timestamp}.html"
            
            pio.write_html(fig_heatmap, heatmap_path)
            pio.write_html(fig_leverage, leverage_path)
            print(f"Interactive plots saved to:\n  - {heatmap_path}\n  - {leverage_path}")
        else:
            fig_heatmap.show()
            fig_leverage.show()
    
    if args.output in ['static', 'both']:
        print("Creating static heatmap...")
        save_path = args.save_path
        if save_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"{save_path}_static_{timestamp}.png"
        
        visualizer.create_static_heatmap(data, save_path)
        if save_path:
            print(f"Static plot saved to: {save_path}")
    
    print("\nLiquidation levels summary:")
    print("\nLong positions (price decrease):")
    for liq in data['liquidation_levels']['long_liquidations']:
        print(f"  {liq['leverage']}x leverage: ${liq['price']:,.2f} ({liq['distance_percent']:.2f}% down)")
    
    print("\nShort positions (price increase):")
    for liq in data['liquidation_levels']['short_liquidations']:
        print(f"  {liq['leverage']}x leverage: ${liq['price']:,.2f} ({liq['distance_percent']:.2f}% up)")


if __name__ == "__main__":
    main()