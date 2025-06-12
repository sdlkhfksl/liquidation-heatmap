# 🔥 Cryptocurrency Liquidation Heatmap

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

A professional cryptocurrency liquidation heatmap visualization tool similar to **Coinglass**, built with Python, CCXT, and Streamlit.

![Liquidation Heatmap Preview](https://via.placeholder.com/800x400/0d1117/ffffff?text=Liquidation+Heatmap+Preview)

## 🚀 Features

- **📊 Real-time Data**: Live order book and price data from major exchanges
- **📈 Interactive Heatmap**: Plotly-based visualizations with hover details  
- **⚖️ Leverage Analysis**: Support for 5x, 10x, 25x, 50x, 100x, 125x leverage
- **🔄 Multi-Exchange**: Binance, OKX, Bybit support via CCXT
- **💰 Multiple Pairs**: BTC/USDT, ETH/USDT, SOL/USDT, and more
- **🌐 Web Interface**: Professional Streamlit dashboard
- **📱 Mobile Responsive**: Works on desktop and mobile

## 🎯 What It Shows

The liquidation heatmap visualizes potential liquidation levels based on:

1. **Current order book depth** from live exchanges
2. **Leverage calculations** for different position sizes
3. **Volume concentration** at critical price levels
4. **Support/Resistance zones** where liquidations cluster

**Red zones** = Long liquidations (price goes down)  
**Green zones** = Short liquidations (price goes up)  
**Hot spots** = High liquidation density

## 🛠️ Installation

### Option 1: Quick Start (Streamlit Cloud)
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy your forked repo
4. Done! ✨

### Option 2: Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/liquidation-heatmap.git
cd liquidation-heatmap

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run streamlit_app.py

# Or run CLI version
python src/main.py --symbol BTC/USDT
```

## 🖥️ Usage

### Web Interface (Recommended)
```bash
streamlit run streamlit_app.py
```
Then open `http://localhost:8501` in your browser.

### Command Line Interface
```bash
# Basic usage
python src/main.py

# Custom symbol and exchange
python src/main.py --symbol ETH/USDT --exchange binance

# Generate static charts
python src/main.py --output static --save-path ./charts/heatmap

# Both interactive and static
python src/main.py --output both --save-path ./output/analysis
```

## 📊 Example Output

### Live BTC/USDT Analysis
```
Current BTC price: $107,836.90
Heatmap data points: 100

Long liquidation levels:
  5x: $86,269.52 (20.00% down)
  10x: $97,053.21 (10.00% down)
  25x: $103,523.42 (4.00% down)

Short liquidation levels:
  5x: $129,404.28 (20.00% up)
  10x: $118,620.59 (10.00% up)
  25x: $112,150.38 (4.00% up)
```

## 🏗️ Architecture

```
liquidation_heatmap/
├── streamlit_app.py          # Web interface (main entry point)
├── src/
│   ├── main.py              # CLI interface
│   ├── data_fetcher.py      # CCXT data fetching
│   └── visualizer.py        # Plotly/matplotlib charts
├── data/                    # Cached data
├── output/                  # Generated charts
└── requirements.txt         # Dependencies
```

## 🔧 Configuration

### Supported Exchanges
- **Binance** (default)
- **OKX** 
- **Bybit**

### Supported Trading Pairs
- BTC/USDT, ETH/USDT, BNB/USDT
- SOL/USDT, ADA/USDT, DOT/USDT
- Any pair supported by the exchange

### Leverage Levels
- 5x, 10x, 25x, 50x, 100x, 125x (customizable)

## 🚀 Deployment Options

### 1. Render (Free + Private Repos) ⭐
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Steps:**
1. Go to [render.com](https://render.com) and sign up
2. Click "New" → "Web Service"  
3. Connect your GitHub repo (works with private repos!)
4. Render will auto-detect the `render.yaml` config
5. Click "Deploy" - your app will be live in ~3 minutes!

### 2. Streamlit Cloud (Free, Public Repos Only)
[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/new?repo=vsching/liquidation-heatmap&branch=main&mainModule=streamlit_app.py)

### 3. Railway
```bash
railway up
```

### 4. Heroku
```bash
git push heroku main
```

### 5. Docker
```bash
docker build -t liquidation-heatmap .
docker run -p 8501:8501 liquidation-heatmap
```

## 📈 Liquidation Formula

**Long Liquidation Price** = Entry Price × (1 - 1/Leverage)  
**Short Liquidation Price** = Entry Price × (1 + 1/Leverage)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Not financial advice. Always do your own research before making trading decisions.

## 🙏 Acknowledgments

- [CCXT](https://github.com/ccxt/ccxt) - Cryptocurrency trading API
- [Streamlit](https://streamlit.io/) - Web framework
- [Plotly](https://plotly.com/) - Interactive visualizations
- [Coinglass](https://coinglass.com/) - Inspiration for the heatmap design

---

⭐ **Star this repo if you found it helpful!**