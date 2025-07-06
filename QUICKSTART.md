# 🚀 Quick Start Guide

Get your Penny Stock Trading Application running in minutes!

## ⚡ Installation (30 seconds)

1. **Create Virtual Environment** (Recommended):
   ```bash
   python3 -m venv trading_env
   source trading_env/bin/activate  # On Windows: trading_env\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Setup** (Optional):
   ```bash
   python setup.py
   ```

## 🎯 Launch Application

### Option 1: Web Dashboard (Recommended)
```bash
python main.py
```
Then open: `http://localhost:8050`

### Option 2: Command Line
```bash
python main.py --mode cli
```

### Option 3: Demo Mode
```bash
python demo.py
```

## 🎮 First Steps

### Using the Web Dashboard
1. **Portfolio Overview** - See your starting capital ($10,000)
2. **Scan Opportunities** - Click "🔍 Scan Opportunities" 
3. **Auto Trade** - Click "⚡ Auto Trade" for automated trading
4. **Monitor Positions** - Watch your trades in real-time

### Using CLI Mode
1. Choose option `1` for portfolio summary
2. Choose option `2` to scan for opportunities
3. Choose option `3` to execute auto trades
4. Choose option `4` to update positions

## 💡 Key Features

### 🎯 Core Trading
- **Automatic penny stock scanning**
- **Risk-managed position sizing**
- **Stop loss & take profit orders**
- **50/50 profit splitting**

### 🛡️ Risk Protection
- **Original capital protection**
- **2% max risk per trade**
- **5% daily loss limit**
- **Position size optimization**

### 📊 Monitoring
- **Real-time portfolio tracking**
- **Performance charts**
- **Trade history**
- **Risk metrics**

## 🔧 Configuration

Edit `config.py` to customize:
- Initial capital amount
- Risk percentages
- Profit splitting ratios
- Stop loss/take profit levels

## 🆘 Troubleshooting

### Common Issues
1. **Dependencies**: Run `pip install -r requirements.txt`
2. **Database**: Run `python setup.py` to initialize
3. **Port 8050**: Close other applications using this port
4. **Internet**: Ensure connection for market data

### Error Messages
- **"No opportunities found"**: Market conditions or low volatility
- **"Insufficient capital"**: Reduce position sizes or add capital
- **"Validation failed"**: Check risk management settings

## 📈 What to Expect

### Initial State
- Starting capital: $10,000
- Available for trading: $10,000
- Active positions: 0
- Bank deposits: $0

### After Trading
- Profits automatically split 50/50
- 50% reinvested for compound growth
- 50% "deposited" to bank account
- Original $10,000 protected

## 🎯 Trading Strategy

The application uses a momentum-based strategy:
1. **Scans penny stocks** ($0.01 - $5.00)
2. **Filters by volume** (>100K shares)
3. **Looks for positive momentum** (>5% daily gain)
4. **Calculates position sizes** based on risk
5. **Sets stop loss** at -5%
6. **Sets take profit** at +50%

## 📊 Understanding the Dashboard

### Portfolio Metrics
- **Total Capital**: Your entire portfolio value
- **Available Capital**: Cash available for trading
- **Invested Capital**: Currently invested in positions
- **Total Profit**: Cumulative profits generated
- **Bank Deposits**: 50% of profits "withdrawn"
- **Daily P&L**: Today's profit/loss

### Opportunities Table
- **Symbol**: Stock ticker
- **Price**: Current stock price
- **Change %**: Daily price change
- **Position Size**: Recommended shares to buy
- **Confidence**: Algorithm confidence score

### Positions Table
- **Symbol**: Stock ticker
- **Shares**: Number of shares owned
- **Entry Price**: Purchase price
- **Current Price**: Current market price
- **P&L**: Unrealized profit/loss
- **P&L %**: Percentage gain/loss

## 🎪 Demo Mode

Run `python demo.py` to see:
- Market scanning in action
- Risk management calculations
- Trade execution with profit splitting
- Automated trading demonstration
- Performance tracking

## 🚀 Ready to Trade!

You're all set! The application will:
- ✅ Protect your original investment
- ✅ Find trading opportunities automatically
- ✅ Execute trades with proper risk management
- ✅ Split profits 50/50 (reinvest/bank)
- ✅ Track performance in real-time

**Remember**: This is a simulation for educational purposes. Always practice with virtual money before considering real trading!

---

Need help? Check the full `README.md` for detailed documentation.