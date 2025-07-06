#!/usr/bin/env python3
"""
Penny Stock Trading Application
Main entry point for the intraday trading application with profit splitting
"""

import os
import sys
import logging
from datetime import datetime
import argparse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database import init_db
from trading_engine import TradingEngine
from market_data import MarketDataService
from risk_manager import RiskManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def initialize_application():
    """Initialize the trading application"""
    try:
        logger.info("Initializing Penny Stock Trading Application...")
        
        # Initialize database
        logger.info("Setting up database...")
        init_db()
        
        # Initialize components
        logger.info("Initializing trading engine...")
        trading_engine = TradingEngine()
        
        logger.info("Initializing market data service...")
        market_data = MarketDataService()
        
        logger.info("Initializing risk manager...")
        risk_manager = RiskManager()
        
        # Display initial portfolio status
        portfolio = trading_engine.get_portfolio_summary()
        logger.info(f"Initial capital: ${Config.INITIAL_CAPITAL:,.2f}")
        logger.info(f"Available capital: ${portfolio.get('account', {}).get('available_capital', 0):,.2f}")
        
        logger.info("Application initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        return False

def run_dashboard():
    """Run the web dashboard"""
    try:
        logger.info("Starting web dashboard...")
        from dashboard import app
        
        # Print access information
        print("\n" + "="*60)
        print("🚀 PENNY STOCK TRADING DASHBOARD")
        print("="*60)
        print(f"Dashboard URL: http://localhost:8050")
        print(f"Initial Capital: ${Config.INITIAL_CAPITAL:,}")
        print(f"Risk Management: {Config.MAX_PORTFOLIO_RISK*100}% max risk per trade")
        print(f"Profit Splitting: {Config.REINVESTMENT_PERCENTAGE*100}% reinvest, {Config.BANK_DEPOSIT_PERCENTAGE*100}% to bank")
        print(f"Stop Loss: {Config.STOP_LOSS_PERCENTAGE*100}%")
        print(f"Take Profit: {Config.TAKE_PROFIT_PERCENTAGE*100}%")
        print("="*60)
        print("Press Ctrl+C to stop the application")
        print("="*60 + "\n")
        
        # Start the dashboard
        app.run_server(debug=False, host='0.0.0.0', port=8050)
        
    except KeyboardInterrupt:
        logger.info("Dashboard stopped by user")
    except Exception as e:
        logger.error(f"Error running dashboard: {str(e)}")

def run_cli_mode():
    """Run in command line mode for testing"""
    try:
        trading_engine = TradingEngine()
        
        while True:
            print("\n" + "="*50)
            print("PENNY STOCK TRADING CLI")
            print("="*50)
            print("1. Portfolio Summary")
            print("2. Scan Opportunities")
            print("3. Execute Auto Trade")
            print("4. Update Positions")
            print("5. Risk Metrics")
            print("6. Exit")
            print("="*50)
            
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == '1':
                portfolio = trading_engine.get_portfolio_summary()
                account = portfolio.get('account', {})
                print(f"\nPORTFOLIO SUMMARY:")
                print(f"Total Capital: ${account.get('total_capital', 0):,.2f}")
                print(f"Available Capital: ${account.get('available_capital', 0):,.2f}")
                print(f"Invested Capital: ${account.get('invested_capital', 0):,.2f}")
                print(f"Total Profit: ${account.get('total_profit', 0):,.2f}")
                print(f"Bank Deposits: ${account.get('bank_deposits', 0):,.2f}")
                print(f"Daily P&L: ${account.get('daily_pnl', 0):,.2f}")
                
                positions = portfolio.get('positions', [])
                if positions:
                    print(f"\nACTIVE POSITIONS:")
                    for pos in positions:
                        print(f"  {pos['symbol']}: {pos['shares']} shares @ ${pos['entry_price']:.2f} "
                              f"(Current: ${pos['current_price']:.2f}, P&L: ${pos['unrealized_pnl']:.2f})")
            
            elif choice == '2':
                print("\nScanning for opportunities...")
                opportunities = trading_engine.get_trading_opportunities()
                if opportunities:
                    print("TRADING OPPORTUNITIES:")
                    for opp in opportunities:
                        print(f"  {opp['symbol']}: ${opp['price']:.2f} "
                              f"({opp['change_percent']:+.1f}%) - "
                              f"Confidence: {opp['confidence']:.2f}")
                else:
                    print("No opportunities found")
            
            elif choice == '3':
                print("\nExecuting auto trade...")
                executed_trades = trading_engine.auto_trade()
                if executed_trades:
                    print("EXECUTED TRADES:")
                    for trade in executed_trades:
                        print(f"  {trade['symbol']}: {trade['message']}")
                else:
                    print("No trades executed")
            
            elif choice == '4':
                print("\nUpdating positions...")
                trading_engine.update_positions()
                print("Positions updated successfully")
            
            elif choice == '5':
                risk_manager = RiskManager()
                metrics = risk_manager.get_portfolio_risk_metrics()
                print(f"\nRISK METRICS:")
                print(f"Capital Utilization: {metrics.get('capital_utilization', 0):.1f}%")
                print(f"Active Positions: {metrics.get('active_positions', 0)}")
                print(f"Daily P&L: ${metrics.get('daily_pnl', 0):,.2f}")
                print(f"Original Capital Protected: {metrics.get('original_capital_protection', False)}")
            
            elif choice == '6':
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please try again.")
                
    except KeyboardInterrupt:
        logger.info("CLI mode stopped by user")
    except Exception as e:
        logger.error(f"Error in CLI mode: {str(e)}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Penny Stock Trading Application')
    parser.add_argument('--mode', choices=['dashboard', 'cli'], default='dashboard',
                       help='Run mode: dashboard (web UI) or cli (command line)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize application
    if not initialize_application():
        sys.exit(1)
    
    # Run in selected mode
    if args.mode == 'dashboard':
        run_dashboard()
    elif args.mode == 'cli':
        run_cli_mode()

if __name__ == '__main__':
    main()