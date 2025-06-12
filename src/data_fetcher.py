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
                'distance_percent': ((current_price - long_liq_price) / current_price) * 100,
                'risk_level': 'high' if leverage >= 50 else 'medium' if leverage >= 25 else 'low'
            })
            
            # Short liquidation (price goes up)
            short_liq_price = current_price * (1 + 1/leverage)
            liquidation_levels['short_liquidations'].append({
                'leverage': leverage,
                'price': short_liq_price,
                'distance_percent': ((short_liq_price - current_price) / current_price) * 100,
                'risk_level': 'high' if leverage >= 50 else 'medium' if leverage >= 25 else 'low'
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
            'timestamp': datetime.now(),
            'analysis_type': 'real-time'
        }
    
    def get_historical_liquidation_data(self, symbol: str, timeframe: str, duration_minutes: int) -> Dict:
        """
        Get historical liquidation analysis over a specific timeframe.
        """
        print(f"📊 Fetching historical data for {symbol} over {timeframe}...")
        
        # Get current price first
        ticker = self.fetch_ticker(symbol)
        if not ticker:
            return None
        
        current_price = ticker['last']
        
        # Map timeframes to valid exchange intervals
        timeframe_mapping = {
            "12h": "1h",  # Use 1h candles for 12h period
            "1d": "1h",   # Use 1h candles for 1d period  
            "2d": "4h",   # Use 4h candles for 2d period
            "3d": "4h"    # Use 4h candles for 3d period
        }
        
        valid_timeframe = timeframe_mapping.get(timeframe, "1h")
        candles_needed = max(12, duration_minutes // (60 if valid_timeframe == "1h" else 240))
        
        # Fetch historical OHLCV data
        ohlcv = self.fetch_ohlcv(symbol, valid_timeframe, limit=min(candles_needed, 1000))
        
        if ohlcv is None or ohlcv.empty:
            print("⚠️ No historical data available, using current snapshot")
            return self.get_liquidation_heatmap_data(symbol)
        
        # Calculate price volatility and ranges
        price_min = ohlcv['low'].min()
        price_max = ohlcv['high'].max()
        price_avg = ohlcv['close'].mean()
        volatility = ((ohlcv['high'] - ohlcv['low']) / ohlcv['close']).mean()
        
        # Create enhanced liquidation levels based on historical data
        liquidation_levels = self.calculate_enhanced_liquidation_levels(
            current_price, price_min, price_max, volatility
        )
        
        # Generate historical heatmap with time series
        heatmap_df = self.generate_historical_heatmap(
            ohlcv, liquidation_levels, duration_minutes
        )
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'liquidation_levels': liquidation_levels,
            'heatmap_data': heatmap_df,
            'ohlcv': ohlcv,
            'timestamp': datetime.now(),
            'analysis_type': 'historical',
            'timeframe': timeframe,
            'duration_minutes': duration_minutes,
            'price_stats': {
                'min': price_min,
                'max': price_max,
                'avg': price_avg,
                'volatility': volatility
            }
        }
    
    def calculate_enhanced_liquidation_levels(self, current_price: float, price_min: float, 
                                            price_max: float, volatility: float) -> Dict[str, List[float]]:
        """
        Calculate enhanced liquidation levels based on historical price movements.
        """
        leverage_levels = [5, 10, 25, 50, 100, 125]
        
        liquidation_levels = {
            'long_liquidations': [],
            'short_liquidations': []
        }
        
        # Factor in historical volatility for more realistic liquidation zones
        volatility_multiplier = max(1.0, min(2.0, 1 + volatility))
        
        for leverage in leverage_levels:
            # Base liquidation calculation
            base_long_liq = current_price * (1 - 1/leverage)
            base_short_liq = current_price * (1 + 1/leverage)
            
            # Adjust based on historical ranges
            range_factor = (price_max - price_min) / current_price
            adjusted_range = range_factor * volatility_multiplier
            
            # Enhanced liquidation zones
            long_liq_price = max(base_long_liq, price_min * 1.01)  # Don't go below historical low
            short_liq_price = min(base_short_liq, price_max * 0.99)  # Don't go above historical high
            
            liquidation_levels['long_liquidations'].append({
                'leverage': leverage,
                'price': long_liq_price,
                'distance_percent': ((current_price - long_liq_price) / current_price) * 100,
                'risk_level': 'high' if leverage >= 50 else 'medium' if leverage >= 25 else 'low'
            })
            
            liquidation_levels['short_liquidations'].append({
                'leverage': leverage,
                'price': short_liq_price,
                'distance_percent': ((short_liq_price - current_price) / current_price) * 100,
                'risk_level': 'high' if leverage >= 50 else 'medium' if leverage >= 25 else 'low'
            })
        
        return liquidation_levels
    
    def generate_historical_heatmap(self, ohlcv: pd.DataFrame, liquidation_levels: Dict,
                                  duration_minutes: int) -> pd.DataFrame:
        """
        Generate a time-based liquidation heatmap from historical data.
        """
        if ohlcv.empty:
            return pd.DataFrame()
        
        # Create time-based price grid
        time_points = min(len(ohlcv), 50)  # Max 50 time points for visualization
        price_points = 100
        
        # Get price range from historical data
        price_min = ohlcv['low'].min() * 0.95
        price_max = ohlcv['high'].max() * 1.05
        
        price_grid = np.linspace(price_min, price_max, price_points)
        time_grid = ohlcv['timestamp'].iloc[-time_points:] if len(ohlcv) >= time_points else ohlcv['timestamp']
        
        heatmap_data = []
        
        for i, timestamp in enumerate(time_grid):
            # Get the price at this time point
            if i < len(ohlcv):
                historical_price = ohlcv.iloc[i]['close']
                volume = ohlcv.iloc[i]['volume']
            else:
                historical_price = ohlcv.iloc[-1]['close']
                volume = ohlcv.iloc[-1]['volume']
            
            for price in price_grid:
                # Calculate liquidation intensity based on distance from historical price
                distance_factor = abs(price - historical_price) / historical_price
                
                # Volume-weighted liquidation probability
                long_intensity = volume * np.exp(-distance_factor * 10) if price < historical_price else 0
                short_intensity = volume * np.exp(-distance_factor * 10) if price > historical_price else 0
                
                # Add leverage-based multipliers
                for liq_level in liquidation_levels['long_liquidations']:
                    if abs(price - liq_level['price']) < (price * 0.01):  # Within 1%
                        long_intensity *= (1 + liq_level['leverage'] / 100)
                
                for liq_level in liquidation_levels['short_liquidations']:
                    if abs(price - liq_level['price']) < (price * 0.01):
                        short_intensity *= (1 + liq_level['leverage'] / 100)
                
                heatmap_data.append({
                    'timestamp': timestamp,
                    'price': price,
                    'long_liquidation_volume': long_intensity,
                    'short_liquidation_volume': short_intensity,
                    'total_liquidation_volume': long_intensity + short_intensity,
                    'historical_price': historical_price
                })
        
        return pd.DataFrame(heatmap_data)