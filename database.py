from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import Config

Base = declarative_base()

class Account(Base):
    """Account model to track portfolio balance and bank deposits"""
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    total_capital = Column(Float, default=Config.INITIAL_CAPITAL)
    available_capital = Column(Float, default=Config.INITIAL_CAPITAL)
    invested_capital = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    bank_deposits = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Position(Base):
    """Position model to track current stock positions"""
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    shares = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Trade(Base):
    """Trade model to track executed trades"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    action = Column(String(10), nullable=False)  # BUY or SELL
    shares = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    profit_loss = Column(Float, default=0.0)
    profit_reinvested = Column(Float, default=0.0)
    profit_to_bank = Column(Float, default=0.0)
    trade_type = Column(String(20), default="MANUAL")  # MANUAL, STOP_LOSS, TAKE_PROFIT
    executed_at = Column(DateTime, default=datetime.now)

class BankTransaction(Base):
    """Bank transaction model to track deposits to bank account"""
    __tablename__ = 'bank_transactions'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), default="DEPOSIT")
    reference_trade_id = Column(Integer, ForeignKey('trades.id'))
    account_number = Column(String(20), default=Config.BANK_ACCOUNT_NUMBER)
    status = Column(String(20), default="PENDING")
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationship
    trade = relationship("Trade", backref="bank_transactions")

class StockData(Base):
    """Stock data model to cache stock information"""
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    change_percent = Column(Float, nullable=False)
    market_cap = Column(Float, nullable=True)
    is_penny_stock = Column(Boolean, default=False)
    last_updated = Column(DateTime, default=datetime.now)

class TradingSession(Base):
    """Trading session model to track daily performance"""
    __tablename__ = 'trading_sessions'
    
    id = Column(Integer, primary_key=True)
    session_date = Column(DateTime, nullable=False)
    starting_capital = Column(Float, nullable=False)
    ending_capital = Column(Float, nullable=False)
    total_trades = Column(Integer, default=0)
    profitable_trades = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)
    total_loss = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)

# Database initialization
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database and create tables"""
    Base.metadata.create_all(bind=engine)
    
    # Create default account if it doesn't exist
    session = SessionLocal()
    try:
        account = session.query(Account).first()
        if not account:
            account = Account()
            session.add(account)
            session.commit()
    finally:
        session.close()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()