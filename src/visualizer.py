import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.subplots as sp


class LiquidationHeatmapVisualizer:
    def __init__(self):
        """Initialize the visualizer with default settings."""
        self.color_scheme = {
            'long': 'Reds',
            'short': 'Greens',
            'combined': 'RdYlGn'
        }
        
    def create_interactive_heatmap(self, data: dict) -> go.Figure:
        """Create an interactive liquidation heatmap using Plotly."""
        heatmap_df = data['heatmap_data']
        current_price = data['current_price']
        liquidation_levels = data['liquidation_levels']
        
        # Create figure with subplots
        fig = sp.make_subplots(
            rows=1, cols=2,
            column_widths=[0.8, 0.2],
            horizontal_spacing=0.02,
            subplot_titles=('Liquidation Heatmap', 'Volume Profile')
        )
        
        # Prepare data for heatmap
        price_range = heatmap_df['price'].values
        
        # Create time axis (mock for now, would be real-time in production)
        time_steps = 50
        time_range = pd.date_range(end=datetime.now(), periods=time_steps, freq='5min')
        
        # Create 2D heatmap data (price x time)
        heatmap_matrix = np.zeros((len(price_range), time_steps))
        
        # Fill heatmap with liquidation intensity
        for i, price in enumerate(price_range):
            # Base intensity from order book
            base_intensity = heatmap_df.iloc[i]['total_liquidation_volume']
            
            # Add time-based variation (simulate changing market conditions)
            for j in range(time_steps):
                variation = np.random.normal(1, 0.1)
                heatmap_matrix[i, j] = base_intensity * variation
        
        # Normalize for better visualization
        heatmap_matrix = np.log1p(heatmap_matrix)
        
        # Add main heatmap
        fig.add_trace(
            go.Heatmap(
                z=heatmap_matrix,
                x=time_range,
                y=price_range,
                colorscale='Hot',
                showscale=True,
                colorbar=dict(
                    title="Liquidation<br>Intensity",
                    x=1.1
                ),
                hovertemplate='Price: $%{y:,.2f}<br>' +
                             'Time: %{x}<br>' +
                             'Intensity: %{z:.2f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Add current price line
        fig.add_trace(
            go.Scatter(
                x=time_range,
                y=[current_price] * len(time_range),
                mode='lines',
                name='Current Price',
                line=dict(color='yellow', width=2, dash='dash'),
                showlegend=True
            ),
            row=1, col=1
        )
        
        # Add liquidation level lines
        for liq in liquidation_levels['long_liquidations']:
            fig.add_trace(
                go.Scatter(
                    x=time_range,
                    y=[liq['price']] * len(time_range),
                    mode='lines',
                    name=f"Long {liq['leverage']}x",
                    line=dict(color='red', width=1, dash='dot'),
                    visible='legendonly',
                    hovertemplate=f"Long {liq['leverage']}x: $%{{y:,.2f}}<extra></extra>"
                ),
                row=1, col=1
            )
        
        for liq in liquidation_levels['short_liquidations']:
            fig.add_trace(
                go.Scatter(
                    x=time_range,
                    y=[liq['price']] * len(time_range),
                    mode='lines',
                    name=f"Short {liq['leverage']}x",
                    line=dict(color='green', width=1, dash='dot'),
                    visible='legendonly',
                    hovertemplate=f"Short {liq['leverage']}x: $%{{y:,.2f}}<extra></extra>"
                ),
                row=1, col=1
            )
        
        # Add volume profile
        fig.add_trace(
            go.Bar(
                x=heatmap_df['total_liquidation_volume'],
                y=heatmap_df['price'],
                orientation='h',
                name='Volume Profile',
                marker_color='rgba(255, 255, 255, 0.6)',
                showlegend=False,
                hovertemplate='Price: $%{y:,.2f}<br>' +
                             'Volume: %{x:,.2f}<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=f"Liquidation Heatmap - {data['symbol']}",
            height=800,
            plot_bgcolor='black',
            paper_bgcolor='#0d1117',
            font=dict(color='white'),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(0,0,0,0.5)'
            ),
            hovermode='closest'
        )
        
        # Update axes
        fig.update_xaxes(title_text="Time", row=1, col=1, gridcolor='#333')
        fig.update_xaxes(title_text="Volume", row=1, col=2, gridcolor='#333')
        fig.update_yaxes(title_text="Price ($)", row=1, col=1, gridcolor='#333')
        fig.update_yaxes(showticklabels=False, row=1, col=2)
        
        return fig
    
    def create_static_heatmap(self, data: dict, save_path: str = None) -> None:
        """Create a static liquidation heatmap using matplotlib."""
        heatmap_df = data['heatmap_data']
        current_price = data['current_price']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8), 
                                       gridspec_kw={'width_ratios': [3, 1]})
        
        # Prepare data for heatmap
        price_range = heatmap_df['price'].values
        liquidation_intensity = heatmap_df['total_liquidation_volume'].values
        
        # Create 2D data for visualization
        intensity_matrix = np.tile(liquidation_intensity, (50, 1)).T
        
        # Apply logarithmic scale for better visualization
        intensity_matrix = np.log1p(intensity_matrix)
        
        # Create heatmap
        im = ax1.imshow(intensity_matrix, cmap='hot', aspect='auto',
                       extent=[0, 50, price_range.min(), price_range.max()])
        
        # Add current price line
        ax1.axhline(y=current_price, color='yellow', linestyle='--', 
                   linewidth=2, label='Current Price')
        
        # Add liquidation levels
        for liq in data['liquidation_levels']['long_liquidations'][:3]:  # Top 3 leverages
            ax1.axhline(y=liq['price'], color='red', linestyle=':', 
                       alpha=0.5, label=f"Long {liq['leverage']}x")
        
        for liq in data['liquidation_levels']['short_liquidations'][:3]:
            ax1.axhline(y=liq['price'], color='green', linestyle=':', 
                       alpha=0.5, label=f"Short {liq['leverage']}x")
        
        ax1.set_xlabel('Time Steps')
        ax1.set_ylabel('Price ($)')
        ax1.set_title(f'Liquidation Heatmap - {data["symbol"]}')
        ax1.legend(loc='upper left', fontsize='small')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax1)
        cbar.set_label('Liquidation Intensity (log scale)')
        
        # Volume profile
        ax2.barh(heatmap_df['price'], heatmap_df['total_liquidation_volume'], 
                alpha=0.7, color='white')
        ax2.set_xlabel('Volume')
        ax2.set_ylabel('')
        ax2.set_title('Volume Profile')
        ax2.yaxis.tick_right()
        
        # Style
        fig.patch.set_facecolor('#0d1117')
        for ax in [ax1, ax2]:
            ax.set_facecolor('#1c1c1c')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            for spine in ax.spines.values():
                spine.set_edgecolor('white')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def create_leverage_distribution(self, data: dict) -> go.Figure:
        """Create a visualization showing liquidation distribution by leverage."""
        liquidation_levels = data['liquidation_levels']
        
        # Prepare data
        leverages = []
        prices = []
        types = []
        distances = []
        
        for liq in liquidation_levels['long_liquidations']:
            leverages.append(f"{liq['leverage']}x")
            prices.append(liq['price'])
            types.append('Long')
            distances.append(liq['distance_percent'])
        
        for liq in liquidation_levels['short_liquidations']:
            leverages.append(f"{liq['leverage']}x")
            prices.append(liq['price'])
            types.append('Short')
            distances.append(liq['distance_percent'])
        
        df = pd.DataFrame({
            'Leverage': leverages,
            'Price': prices,
            'Type': types,
            'Distance %': distances
        })
        
        # Create subplot figure
        fig = sp.make_subplots(
            rows=1, cols=2,
            subplot_titles=('Liquidation Prices by Leverage', 
                          'Distance from Current Price')
        )
        
        # Add bar chart for prices
        for t in ['Long', 'Short']:
            df_filtered = df[df['Type'] == t]
            fig.add_trace(
                go.Bar(
                    x=df_filtered['Leverage'],
                    y=df_filtered['Price'],
                    name=t,
                    marker_color='red' if t == 'Long' else 'green'
                ),
                row=1, col=1
            )
        
        # Add scatter for distance
        fig.add_trace(
            go.Scatter(
                x=df[df['Type'] == 'Long']['Leverage'],
                y=df[df['Type'] == 'Long']['Distance %'],
                mode='lines+markers',
                name='Long Distance',
                line=dict(color='red')
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=df[df['Type'] == 'Short']['Leverage'],
                y=df[df['Type'] == 'Short']['Distance %'],
                mode='lines+markers',
                name='Short Distance',
                line=dict(color='green')
            ),
            row=1, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=f"Liquidation Analysis - {data['symbol']}",
            height=500,
            showlegend=True,
            plot_bgcolor='#1c1c1c',
            paper_bgcolor='#0d1117',
            font=dict(color='white')
        )
        
        fig.update_xaxes(title_text="Leverage", gridcolor='#333')
        fig.update_yaxes(title_text="Price ($)", row=1, col=1, gridcolor='#333')
        fig.update_yaxes(title_text="Distance (%)", row=1, col=2, gridcolor='#333')
        
        return fig