#!/usr/bin/env python3
"""
Demo script for Penny Stock Trading Application
This script demonstrates the key features of the trading application
"""

import time
import random
from datetime import datetime

from config import Config
from database import init_db
from trading_engine import TradingEngine
from market_data import MarketDataService
from risk_manager import RiskManager

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def print_portfolio_status(trading_engine):
    """Print current portfolio status"""
    portfolio = trading_engine.get_portfolio_summary()
    account = portfolio.get('account', {})
    
    print(f"\n📊 PORTFOLIO STATUS:")
    print(f"   Total Capital: ${account.get('total_capital', 0):,.2f}")
    print(f"   Available Capital: ${account.get('available_capital', 0):,.2f}")
    print(f"   Invested Capital: ${account.get('invested_capital', 0):,.2f}")
    print(f"   Total Profit: ${account.get('total_profit', 0):,.2f}")
    print(f"   Bank Deposits: ${account.get('bank_deposits', 0):,.2f}")
    print(f"   Daily P&L: ${account.get('daily_pnl', 0):,.2f}")
    
    positions = portfolio.get('positions', [])
    if positions:
        print(f"\n📈 ACTIVE POSITIONS:")
        for pos in positions:
            pnl_symbol = "🟢" if pos['unrealized_pnl'] >= 0 else "🔴"
            print(f"   {pnl_symbol} {pos['symbol']}: {pos['shares']} shares @ ${pos['entry_price']:.2f}")
            print(f"      Current: ${pos['current_price']:.2f}, P&L: ${pos['unrealized_pnl']:.2f} ({pos['pnl_percentage']:.1f}%)")

def demo_market_scanning():
    """Demo market scanning functionality"""
    print_header("MARKET SCANNING DEMO")
    
    market_data = MarketDataService()
    
    print("🔍 Scanning for penny stock opportunities...")
    opportunities = market_data.scan_for_opportunities()
    
    if opportunities:
        print(f"\n✅ Found {len(opportunities)} opportunities:")
        for i, opp in enumerate(opportunities, 1):
            print(f"   {i}. {opp['symbol']}: ${opp['price']:.2f} "
                  f"({opp['change_percent']:+.1f}%) - Confidence: {opp['confidence']:.2f}")
    else:
        print("❌ No opportunities found at this time")
    
    return opportunities

def demo_risk_management():
    """Demo risk management features"""
    print_header("RISK MANAGEMENT DEMO")
    
    risk_manager = RiskManager()
    
    print("🛡️ Risk Management Settings:")
    print(f"   Max Risk per Trade: {Config.MAX_PORTFOLIO_RISK*100}%")
    print(f"   Daily Loss Limit: {Config.MAX_DAILY_LOSS*100}%")
    print(f"   Stop Loss: {Config.STOP_LOSS_PERCENTAGE*100}%")
    print(f"   Take Profit: {Config.TAKE_PROFIT_PERCENTAGE*100}%")
    
    # Demo position sizing
    example_price = 2.50
    stop_loss = risk_manager.calculate_stop_loss(example_price)
    take_profit = risk_manager.calculate_take_profit(example_price)
    position_size = risk_manager.calculate_position_size("EXAMPLE", example_price, stop_loss)
    
    print(f"\n📏 Position Sizing Example (Stock @ ${example_price:.2f}):")
    print(f"   Stop Loss: ${stop_loss:.2f}")
    print(f"   Take Profit: ${take_profit:.2f}")
    print(f"   Calculated Position Size: {position_size} shares")
    
    # Portfolio risk metrics
    metrics = risk_manager.get_portfolio_risk_metrics()
    print(f"\n📊 Portfolio Risk Metrics:")
    print(f"   Capital Utilization: {metrics.get('capital_utilization', 0):.1f}%")
    print(f"   Active Positions: {metrics.get('active_positions', 0)}")
    print(f"   Original Capital Protected: {'✅' if metrics.get('original_capital_protection', False) else '❌'}")

def demo_trading_execution():
    """Demo trading execution and profit splitting"""
    print_header("TRADING EXECUTION DEMO")
    
    trading_engine = TradingEngine()
    
    # Get some opportunities
    opportunities = trading_engine.get_trading_opportunities()
    
    if opportunities:
        # Execute a demo trade
        opp = opportunities[0]
        symbol = opp['symbol']
        price = opp['price']
        shares = opp['suggested_position_size']
        
        print(f"🎯 Executing demo trade:")
        print(f"   Symbol: {symbol}")
        print(f"   Price: ${price:.2f}")
        print(f"   Shares: {shares}")
        
        # Execute buy order
        success, message = trading_engine.execute_buy_order(symbol, shares, price)
        
        if success:
            print(f"✅ {message}")
            print_portfolio_status(trading_engine)
            
            # Simulate price movement and profit
            print(f"\n⏱️ Simulating price movement...")
            time.sleep(2)
            
            # Simulate a profitable sale
            new_price = price * (1 + random.uniform(0.10, 0.30))  # 10-30% profit
            print(f"🚀 Stock moved to ${new_price:.2f} (+{((new_price-price)/price)*100:.1f}%)")
            
            # Execute sell order
            success, message = trading_engine.execute_sell_order(symbol, shares, new_price)
            
            if success:
                print(f"✅ {message}")
                
                # Show profit splitting
                profit = (new_price - price) * shares
                reinvested = profit * Config.REINVESTMENT_PERCENTAGE
                bank_deposit = profit * Config.BANK_DEPOSIT_PERCENTAGE
                
                print(f"\n💰 PROFIT SPLITTING:")
                print(f"   Total Profit: ${profit:.2f}")
                print(f"   Reinvested (50%): ${reinvested:.2f}")
                print(f"   Bank Deposit (50%): ${bank_deposit:.2f}")
                
                print_portfolio_status(trading_engine)
        else:
            print(f"❌ {message}")
    else:
        print("❌ No opportunities available for demo trade")

def demo_automated_trading():
    """Demo automated trading features"""
    print_header("AUTOMATED TRADING DEMO")
    
    trading_engine = TradingEngine()
    
    print("🤖 Executing automated trading...")
    executed_trades = trading_engine.auto_trade()
    
    if executed_trades:
        print(f"✅ Auto-trading executed {len(executed_trades)} trades:")
        for trade in executed_trades:
            status = "✅" if trade['success'] else "❌"
            print(f"   {status} {trade['symbol']}: {trade['message']}")
            print(f"      Confidence: {trade['confidence']:.2f}")
        
        print_portfolio_status(trading_engine)
    else:
        print("❌ No suitable opportunities found for auto-trading")

def demo_performance_tracking():
    """Demo performance tracking features"""
    print_header("PERFORMANCE TRACKING DEMO")
    
    trading_engine = TradingEngine()
    portfolio = trading_engine.get_portfolio_summary()
    
    print("📈 Performance Metrics:")
    
    # Recent trades
    recent_trades = portfolio.get('recent_trades', [])
    if recent_trades:
        print(f"\n📋 Recent Trades ({len(recent_trades)} total):")
        for trade in recent_trades[:5]:  # Show last 5
            action_symbol = "🟢" if trade['action'] == 'BUY' else "🔴"
            pnl_symbol = "📈" if trade['profit_loss'] >= 0 else "📉"
            print(f"   {action_symbol} {trade['symbol']}: {trade['action']} {trade['shares']} @ ${trade['price']:.2f}")
            if trade['profit_loss'] != 0:
                print(f"      {pnl_symbol} P&L: ${trade['profit_loss']:.2f}")
    
    # Portfolio summary
    account = portfolio.get('account', {})
    initial_capital = Config.INITIAL_CAPITAL
    total_return = account.get('total_capital', initial_capital) - initial_capital
    return_pct = (total_return / initial_capital) * 100
    
    print(f"\n🎯 Performance Summary:")
    print(f"   Initial Capital: ${initial_capital:,.2f}")
    print(f"   Current Capital: ${account.get('total_capital', 0):,.2f}")
    print(f"   Total Return: ${total_return:.2f} ({return_pct:+.2f}%)")
    print(f"   Profit Withdrawn: ${account.get('bank_deposits', 0):,.2f}")

def run_comprehensive_demo():
    """Run a comprehensive demo of all features"""
    print("🚀 PENNY STOCK TRADING APPLICATION DEMO")
    print("="*60)
    print("This demo showcases the key features of the trading application")
    print("All trades are simulated - no real money is involved")
    
    # Initialize
    init_db()
    
    # Demo each component
    demo_market_scanning()
    time.sleep(2)
    
    demo_risk_management()
    time.sleep(2)
    
    demo_trading_execution()
    time.sleep(2)
    
    demo_automated_trading()
    time.sleep(2)
    
    demo_performance_tracking()
    
    print_header("DEMO COMPLETED")
    print("🎉 Demo completed successfully!")
    print("💡 Key Features Demonstrated:")
    print("   ✅ Market scanning and opportunity identification")
    print("   ✅ Risk management and position sizing")
    print("   ✅ Trade execution with profit splitting")
    print("   ✅ Automated trading capabilities")
    print("   ✅ Performance tracking and analysis")
    print("\n🚀 Ready to run the full application:")
    print("   python main.py")

if __name__ == "__main__":
    run_comprehensive_demo()