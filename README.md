# 🚀 Penny Stock Trading Application

A sophisticated intraday trading application designed specifically for penny stocks with intelligent profit splitting and capital protection features.

## ✨ Key Features

### 🎯 Core Trading Features
- **Automated Penny Stock Scanning** - Identifies trading opportunities in real-time
- **Intelligent Position Sizing** - Calculates optimal position sizes based on risk management
- **Automated Stop Loss & Take Profit** - Protects capital with automatic exit strategies
- **Profit Splitting System** - Automatically splits profits 50/50 (reinvestment vs bank deposit)
- **Original Capital Protection** - Ensures your initial investment is never at risk

### 💰 Profit Management
- **50% Profit Reinvestment** - Automatically reinvests half of all profits for compound growth
- **50% Bank Deposits** - Secures half of profits in simulated bank account
- **Original Investment Protection** - Only risks profits, never the original capital

### 🛡️ Risk Management
- **Maximum 2% Risk Per Trade** - Limits risk exposure per position
- **Daily Loss Limits** - Stops trading if daily loss threshold is reached
- **Position Size Optimization** - Calculates optimal position sizes automatically
- **Real-time Risk Monitoring** - Continuously monitors portfolio risk metrics

### 📊 Modern Web Interface
- **Dual Web Interfaces** - Choose between Dash or Flask-based web applications
- **Real-time Dashboard** - Beautiful, responsive web interface with live updates
- **Portfolio Analytics** - Comprehensive portfolio performance tracking
- **Trading Opportunities** - Live scanning and display of trading opportunities
- **Performance Charts** - Visual representation of portfolio growth and profit distribution
- **Interactive Controls** - One-click trading, scanning, and position management

## 🏗️ Technical Architecture

### Core Components
1. **Trading Engine** (`trading_engine.py`) - Core trading logic and execution
2. **Market Data Service** (`market_data.py`) - Real-time stock data and scanning
3. **Risk Manager** (`risk_manager.py`) - Advanced risk management and capital protection
4. **Database Layer** (`database.py`) - SQLite database for trade and position tracking
5. **Web Dashboard** (`dashboard.py`) - Modern Dash-based web interface

### Technology Stack
- **Backend**: Python 3.8+
- **Database**: SQLite with SQLAlchemy ORM
- **Web Framework**: Dash with Bootstrap components
- **Data Processing**: Pandas, NumPy
- **Market Data**: yfinance API
- **Charting**: Plotly
- **Styling**: Bootstrap 5 with custom CSS

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection for market data
- Modern web browser

### Installation

1. **Clone or Download** the application files
2. **Create Virtual Environment** (Recommended):
   ```bash
   python3 -m venv trading_env
   source trading_env/bin/activate  # On Windows: trading_env\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python main.py
   ```

5. **Access the Dashboard**:
   Open your browser to `http://localhost:8050`

### Alternative CLI Mode
For command-line testing:
```bash
python main.py --mode cli
```

## 🎮 Using the Application

### Web Interface Options

**Option 1: Dash Dashboard (Default)**
```bash
python main.py
```
Access at: `http://localhost:8050`

**Option 2: Flask Web Application**
```bash
python web_app.py
```
Access at: `http://localhost:5000`

### Dashboard Overview
Both web interfaces provide:
- **Portfolio Metrics** - Real-time portfolio status
- **Trading Controls** - Scan opportunities, execute trades, update positions
- **Opportunities Table** - Live trading opportunities with buy buttons
- **Positions Table** - Current active positions with P&L
- **Performance Charts** - Portfolio growth and profit distribution
- **Recent Trades** - History of executed trades

### Trading Workflow
1. **Scan Opportunities** - Click "Scan Opportunities" to find trading candidates
2. **Review Suggestions** - Examine the opportunities table for potential trades
3. **Auto Trade** - Use "Auto Trade" for automated execution of top opportunities
4. **Monitor Positions** - Watch your positions in the positions table
5. **Automatic Exits** - Positions automatically close at stop loss or take profit levels

### Profit Splitting in Action
When a profitable trade is closed:
- **50% of profit** → Reinvested into available capital for future trades
- **50% of profit** → Deposited into bank account (simulated)
- **Original investment** → Returned to available capital

## ⚙️ Configuration

### Key Settings (`config.py`)
```python
# Risk Management
MAX_PORTFOLIO_RISK = 0.02      # 2% max risk per trade
MAX_DAILY_LOSS = 0.05          # 5% daily loss limit
STOP_LOSS_PERCENTAGE = 0.05    # 5% stop loss
TAKE_PROFIT_PERCENTAGE = 0.50  # 50% take profit

# Profit Splitting
REINVESTMENT_PERCENTAGE = 0.50  # 50% reinvest
BANK_DEPOSIT_PERCENTAGE = 0.50  # 50% to bank

# Trading Parameters
INITIAL_CAPITAL = 10000.0       # Starting capital
MAX_POSITION_SIZE = 1000        # Max shares per position
MAX_OPEN_POSITIONS = 5          # Max concurrent positions
```

### Penny Stock Criteria
- **Price Range**: $0.01 - $5.00
- **Minimum Volume**: 100,000 shares daily
- **Momentum Filter**: Looking for stocks with positive momentum

## 🔒 Risk Management Features

### Capital Protection
- **Original Investment Shield** - Your initial capital is never at risk
- **Only Risk Profits** - Trading uses only profits generated from previous trades
- **Daily Loss Limits** - Automatic trading halt if daily loss threshold is reached
- **Position Size Limits** - Maximum position size and number of concurrent positions

### Automated Risk Controls
- **Stop Loss Orders** - Automatic exit at 5% loss
- **Take Profit Orders** - Automatic exit at 50% gain
- **Real-time Monitoring** - Continuous position monitoring and updates
- **Risk Metric Tracking** - Portfolio risk metrics calculated in real-time

## 📈 Performance Tracking

### Portfolio Metrics
- Total Capital
- Available Capital
- Invested Capital
- Total Profit
- Bank Deposits
- Daily P&L
- Unrealized P&L

### Risk Metrics
- Capital Utilization
- Active Positions Count
- Daily P&L
- Original Capital Protection Status
- Maximum Drawdown

## 🗄️ Database Schema

### Core Tables
- **accounts** - Portfolio and account information
- **positions** - Active stock positions
- **trades** - Trade execution history
- **bank_transactions** - Bank deposit records
- **stock_data** - Cached market data
- **trading_sessions** - Daily performance tracking

## 🔧 Advanced Features

### Automated Trading
- **Opportunity Scanning** - Automatically scans penny stocks for trading opportunities
- **Smart Position Sizing** - Calculates optimal position sizes based on risk
- **Automated Execution** - Can execute trades automatically based on confidence scores
- **Background Monitoring** - Continuously monitors positions for exit signals

### Market Data Integration
- **Real-time Quotes** - Uses yfinance for real-time stock data
- **Technical Indicators** - RSI, MACD, Moving Averages
- **Volume Analysis** - Ensures adequate liquidity before trading
- **Penny Stock Filtering** - Automatically identifies qualifying penny stocks

## 🚨 Important Disclaimers

### Trading Risks
- **This is for educational purposes only**
- **Past performance does not guarantee future results**
- **Trading involves substantial risk of loss**
- **Never trade with money you cannot afford to lose**

### Simulation Mode
- The application runs in simulation mode by default
- No real money is at risk during testing
- All trades are simulated for learning purposes
- Real trading requires integration with a broker API

## 🛠️ Development & Customization

### Extending the Application
- **Add New Strategies** - Implement custom trading strategies
- **Integrate Broker APIs** - Connect to real trading accounts
- **Custom Risk Rules** - Modify risk management parameters
- **Additional Indicators** - Add more technical analysis tools

### File Structure
```
├── main.py              # Main application entry point
├── config.py            # Configuration settings
├── database.py          # Database models and setup
├── trading_engine.py    # Core trading logic
├── market_data.py       # Market data service
├── risk_manager.py      # Risk management system
├── dashboard.py         # Web dashboard interface
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 📞 Support & Contributing

### Getting Help
- Review the code comments for detailed explanations
- Check the log files for troubleshooting (`trading_app.log`)
- Ensure all dependencies are properly installed

### Contributing
- Fork the repository
- Make your improvements
- Test thoroughly
- Submit pull requests

## 📝 License

This project is provided as-is for educational purposes. Use at your own risk.

---

**Remember**: This application is designed for educational purposes and simulation only. Always consult with financial professionals before making real trading decisions.