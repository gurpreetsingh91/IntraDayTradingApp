#!/usr/bin/env python3
"""
Flask Web Application for Penny Stock Trading
Alternative web interface using traditional HTML templates
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
from datetime import datetime
import threading
import time
import logging

from config import Config
from database import init_db
from trading_engine import TradingEngine
from market_data import MarketDataService
from risk_manager import RiskManager

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize trading components
init_db()
trading_engine = TradingEngine()
market_data = MarketDataService()
risk_manager = RiskManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for real-time updates
latest_portfolio_data = {}
latest_opportunities = []
latest_positions = []

def update_data_background():
    """Background thread to update data periodically"""
    global latest_portfolio_data, latest_opportunities, latest_positions
    
    while True:
        try:
            # Update portfolio data
            latest_portfolio_data = trading_engine.get_portfolio_summary()
            
            # Update opportunities
            latest_opportunities = trading_engine.get_trading_opportunities()
            
            # Update positions
            trading_engine.update_positions()
            latest_positions = latest_portfolio_data.get('positions', [])
            
            time.sleep(30)  # Update every 30 seconds
        except Exception as e:
            logger.error(f"Error in background update: {str(e)}")
            time.sleep(30)

# Start background thread
background_thread = threading.Thread(target=update_data_background, daemon=True)
background_thread.start()

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        portfolio = trading_engine.get_portfolio_summary()
        opportunities = trading_engine.get_trading_opportunities()
        risk_metrics = risk_manager.get_portfolio_risk_metrics()
        
        return render_template('index.html', 
                             portfolio=portfolio,
                             opportunities=opportunities,
                             risk_metrics=risk_metrics,
                             config=Config)
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/portfolio')
def portfolio():
    """Portfolio details page"""
    try:
        portfolio = trading_engine.get_portfolio_summary()
        risk_metrics = risk_manager.get_portfolio_risk_metrics()
        
        return render_template('portfolio.html',
                             portfolio=portfolio,
                             risk_metrics=risk_metrics,
                             config=Config)
    except Exception as e:
        logger.error(f"Error loading portfolio: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/opportunities')
def opportunities():
    """Trading opportunities page"""
    try:
        opportunities = trading_engine.get_trading_opportunities()
        return render_template('opportunities.html', opportunities=opportunities)
    except Exception as e:
        logger.error(f"Error loading opportunities: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/positions')
def positions():
    """Current positions page"""
    try:
        portfolio = trading_engine.get_portfolio_summary()
        positions = portfolio.get('positions', [])
        return render_template('positions.html', positions=positions)
    except Exception as e:
        logger.error(f"Error loading positions: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/trades')
def trades():
    """Trade history page"""
    try:
        portfolio = trading_engine.get_portfolio_summary()
        trades = portfolio.get('recent_trades', [])
        return render_template('trades.html', trades=trades)
    except Exception as e:
        logger.error(f"Error loading trades: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/settings')
def settings():
    """Settings and configuration page"""
    try:
        return render_template('settings.html', config=Config)
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        return render_template('error.html', error=str(e))

# API Routes for AJAX calls
@app.route('/api/portfolio')
def api_portfolio():
    """API endpoint for portfolio data"""
    try:
        portfolio = trading_engine.get_portfolio_summary()
        return jsonify(portfolio)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/opportunities')
def api_opportunities():
    """API endpoint for trading opportunities"""
    try:
        opportunities = trading_engine.get_trading_opportunities()
        return jsonify(opportunities)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/positions')
def api_positions():
    """API endpoint for current positions"""
    try:
        portfolio = trading_engine.get_portfolio_summary()
        positions = portfolio.get('positions', [])
        return jsonify(positions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """API endpoint to scan for opportunities"""
    try:
        opportunities = trading_engine.get_trading_opportunities()
        return jsonify({
            'success': True,
            'opportunities': opportunities,
            'message': f'Found {len(opportunities)} opportunities'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auto_trade', methods=['POST'])
def api_auto_trade():
    """API endpoint for automated trading"""
    try:
        executed_trades = trading_engine.auto_trade()
        return jsonify({
            'success': True,
            'trades': executed_trades,
            'message': f'Executed {len(executed_trades)} trades'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/buy', methods=['POST'])
def api_buy():
    """API endpoint to execute buy order"""
    try:
        data = request.json
        symbol = data.get('symbol')
        shares = int(data.get('shares', 0))
        price = float(data.get('price', 0))
        
        success, message = trading_engine.execute_buy_order(symbol, shares, price)
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sell', methods=['POST'])
def api_sell():
    """API endpoint to execute sell order"""
    try:
        data = request.json
        symbol = data.get('symbol')
        shares = int(data.get('shares', 0))
        price = float(data.get('price', 0))
        
        success, message = trading_engine.execute_sell_order(symbol, shares, price)
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/update_positions', methods=['POST'])
def api_update_positions():
    """API endpoint to update positions"""
    try:
        trading_engine.update_positions()
        return jsonify({
            'success': True,
            'message': 'Positions updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/risk_metrics')
def api_risk_metrics():
    """API endpoint for risk metrics"""
    try:
        metrics = risk_manager.get_portfolio_risk_metrics()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 PENNY STOCK TRADING WEB APPLICATION")
    print("="*60)
    print(f"🌐 Web Interface: http://localhost:5000")
    print(f"💰 Initial Capital: ${Config.INITIAL_CAPITAL:,}")
    print(f"🛡️ Risk Management: {Config.MAX_PORTFOLIO_RISK*100}% max risk per trade")
    print(f"💫 Profit Splitting: {Config.REINVESTMENT_PERCENTAGE*100}% reinvest, {Config.BANK_DEPOSIT_PERCENTAGE*100}% to bank")
    print("="*60)
    print("Press Ctrl+C to stop the application")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)