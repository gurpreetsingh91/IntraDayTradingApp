import os
from datetime import datetime, time

class Config:
    """Configuration class for the trading application"""
    
    # Trading Parameters
    MAX_PORTFOLIO_RISK = 0.02  # Maximum 2% of portfolio at risk per trade
    MAX_DAILY_LOSS = 0.05      # Maximum 5% daily loss threshold
    MIN_PROFIT_THRESHOLD = 0.10  # Minimum 10% profit to trigger profit-taking
    STOP_LOSS_PERCENTAGE = 0.05  # 5% stop loss
    TAKE_PROFIT_PERCENTAGE = 0.50  # 50% take profit target
    
    # Profit Splitting
    REINVESTMENT_PERCENTAGE = 0.50  # 50% of profit reinvested
    BANK_DEPOSIT_PERCENTAGE = 0.50  # 50% of profit to bank
    
    # Trading Hours (Market Hours: 9:30 AM - 4:00 PM ET)
    MARKET_OPEN = time(9, 30)
    MARKET_CLOSE = time(16, 0)
    
    # Penny Stock Criteria
    MIN_PRICE = 0.01
    MAX_PRICE = 5.00
    MIN_VOLUME = 100000  # Minimum daily volume
    
    # Database
    DATABASE_URL = "sqlite:///trading_app.db"
    
    # API Keys (would be loaded from environment variables)
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
    
    # Risk Management
    MAX_POSITION_SIZE = 1000  # Maximum position size per stock
    MAX_OPEN_POSITIONS = 5    # Maximum concurrent positions
    
    # Simulation Mode (for demo purposes)
    SIMULATION_MODE = True
    INITIAL_CAPITAL = 10000.0  # Starting capital
    
    # Bank Account Simulation
    BANK_ACCOUNT_NUMBER = "XXXX-XXXX-1234"
    BANK_ROUTING_NUMBER = "123456789"