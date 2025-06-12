import ccxt
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import time
from datetime import datetime, timedelta


class LiquidationDataFetcher:
    def __init__(self, exchange_name: str = 'binance'):
        """Initialize the data fetcher with specified exchange."""
        self.exchange = getattr(ccxt, exchange_name)({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'  # Use futures market for liquidation data
            }
        })
        
    def fetch_order_book(self, symbol: str, limit: int = 1000) -> Dict:
        """Fetch order book data for a given symbol."""
        try:
            order_book = self.exchange.fetch_order_book(symbol, limit)
            return order_book
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return None
    
    def fetch_ticker(self, symbol: str) -> Dict:
        """Fetch current ticker data including price."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            print(f"Error fetching ticker: {e}")
            return None
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 500) -> pd.DataFrame:
        """Fetch OHLCV data for volatility calculation."""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching OHLCV: {e}")
            return None
    
    def calculate_liquidation_levels(self, current_price: float, leverage_levels: List[int] = None) -> Dict[str, List[float]]:
        """
        Calculate potential liquidation price levels based on leverage.
        
        For longs: Liquidation Price = Entry Price * (1 - 1/Leverage)
        For shorts: Liquidation Price = Entry Price * (1 + 1/Leverage)
        """
        if leverage_levels is None:
            leverage_levels = [5, 10, 25, 50, 100, 125]
        
        liquidation_levels = {
            'long_liquidations': [],
            'short_liquidations': []
        }
        
        for leverage in leverage_levels:
            # Long liquidation (price goes down)
            long_liq_price = current_price * (1 - 1/leverage)
            liquidation_levels['long_liquidations'].append({
                'leverage': leverage,
                'price': long_liq_price,
                'distance_percent': ((current_price - long_liq_price) / current_price) * 100
            })
            
            # Short liquidation (price goes up)
            short_liq_price = current_price * (1 + 1/leverage)
            liquidation_levels['short_liquidations'].append({
                'leverage': leverage,
                'price': short_liq_price,
                'distance_percent': ((short_liq_price - current_price) / current_price) * 100
            })
        
        return liquidation_levels
    
    def estimate_liquidation_volume(self, order_book: Dict, liquidation_levels: Dict) -> pd.DataFrame:
        """
        Estimate potential liquidation volumes at different price levels
        based on order book depth.
        """
        bids = pd.DataFrame(order_book['bids'], columns=['price', 'volume'])
        asks = pd.DataFrame(order_book['asks'], columns=['price', 'volume'])
        
        # Create price ranges for heatmap
        all_prices = []
        
        # Add liquidation level prices
        for long_liq in liquidation_levels['long_liquidations']:
            all_prices.append(long_liq['price'])
        for short_liq in liquidation_levels['short_liquidations']:
            all_prices.append(short_liq['price'])
        
        # Add order book prices
        all_prices.extend(bids['price'].tolist())
        all_prices.extend(asks['price'].tolist())
        
        # Create price grid
        min_price = min(all_prices) * 0.95
        max_price = max(all_prices) * 1.05
        price_grid = np.linspace(min_price, max_price, 100)
        
        # Calculate cumulative volume at each price level
        heatmap_data = []
        
        for price in price_grid:
            # Volume that would be liquidated if price reaches this level
            long_volume = bids[bids['price'] >= price]['volume'].sum()
            short_volume = asks[asks['price'] <= price]['volume'].sum()
            
            # Add leverage-based multiplier (higher leverage = more liquidations)
            for liq_level in liquidation_levels['long_liquidations']:
                if abs(price - liq_level['price']) < (price * 0.001):  # Within 0.1% of liquidation level
                    long_volume *= (1 + liq_level['leverage'] / 100)
            
            for liq_level in liquidation_levels['short_liquidations']:
                if abs(price - liq_level['price']) < (price * 0.001):
                    short_volume *= (1 + liq_level['leverage'] / 100)
            
            heatmap_data.append({
                'price': price,
                'long_liquidation_volume': long_volume,
                'short_liquidation_volume': short_volume,
                'total_liquidation_volume': long_volume + short_volume
            })
        
        return pd.DataFrame(heatmap_data)
    
    def get_liquidation_heatmap_data(self, symbol: str) -> Dict:
        """
        Get all necessary data for creating a liquidation heatmap.
        """
        # Fetch current data
        ticker = self.fetch_ticker(symbol)
        if not ticker:
            return None
        
        current_price = ticker['last']
        
        # Fetch order book
        order_book = self.fetch_order_book(symbol)
        if not order_book:
            return None
        
        # Calculate liquidation levels
        liquidation_levels = self.calculate_liquidation_levels(current_price)
        
        # Estimate liquidation volumes
        heatmap_df = self.estimate_liquidation_volume(order_book, liquidation_levels)
        
        # Fetch historical data for volatility
        ohlcv = self.fetch_ohlcv(symbol)
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'liquidation_levels': liquidation_levels,
            'heatmap_data': heatmap_df,
            'ohlcv': ohlcv,
            'timestamp': datetime.now()
        }