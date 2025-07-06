import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
from config import Config
from database import StockData, SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataService:
    """Service to fetch and manage stock market data"""
    
    def __init__(self):
        self.session = SessionLocal()
        
    def get_penny_stocks(self) -> List[str]:
        """Get list of penny stocks based on price criteria"""
        # For demo purposes, using a predefined list of penny stocks
        # In production, this would scan the market for stocks meeting criteria
        penny_stocks = [
            "SNDL", "FORD", "NOK", "NAKD", "SENS", "TNXP", "EXPR", 
            "GNUS", "CTRM", "SHIP", "CCIV", "PLTR", "WISH", "SOFI",
            "RIOT", "MARA", "WKHS", "TLRY", "HYMC", "MULN"
        ]
        return penny_stocks
    
    def get_stock_data(self, symbol: str, period: str = "1d") -> Optional[Dict]:
        """Get stock data for a specific symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period=period)
            
            if hist.empty:
                logger.warning(f"No data found for {symbol}")
                return None
            
            current_price = hist['Close'].iloc[-1]
            volume = hist['Volume'].iloc[-1]
            
            # Calculate price change
            if len(hist) > 1:
                prev_close = hist['Close'].iloc[-2]
                change_percent = ((current_price - prev_close) / prev_close) * 100
            else:
                change_percent = 0.0
            
            # Check if it's a penny stock
            is_penny = Config.MIN_PRICE <= current_price <= Config.MAX_PRICE
            
            stock_data = {
                'symbol': symbol,
                'price': float(current_price),
                'volume': int(volume),
                'change_percent': float(change_percent),
                'market_cap': info.get('marketCap', 0),
                'is_penny_stock': is_penny,
                'last_updated': datetime.now()
            }
            
            # Cache the data
            self.cache_stock_data(stock_data)
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def cache_stock_data(self, stock_data: Dict):
        """Cache stock data in database"""
        try:
            # Check if data already exists
            existing = self.session.query(StockData).filter_by(symbol=stock_data['symbol']).first()
            
            if existing:
                # Update existing record
                for key, value in stock_data.items():
                    setattr(existing, key, value)
            else:
                # Create new record
                new_stock = StockData(**stock_data)
                self.session.add(new_stock)
            
            self.session.commit()
            
        except Exception as e:
            logger.error(f"Error caching stock data: {str(e)}")
            self.session.rollback()
    
    def get_cached_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get cached stock data"""
        try:
            stock = self.session.query(StockData).filter_by(symbol=symbol).first()
            if stock:
                return {
                    'symbol': stock.symbol,
                    'price': stock.price,
                    'volume': stock.volume,
                    'change_percent': stock.change_percent,
                    'market_cap': stock.market_cap,
                    'is_penny_stock': stock.is_penny_stock,
                    'last_updated': stock.last_updated
                }
            return None
        except Exception as e:
            logger.error(f"Error getting cached data: {str(e)}")
            return None
    
    def scan_for_opportunities(self) -> List[Dict]:
        """Scan penny stocks for trading opportunities"""
        opportunities = []
        penny_stocks = self.get_penny_stocks()
        
        for symbol in penny_stocks:
            try:
                stock_data = self.get_stock_data(symbol)
                if stock_data and stock_data['is_penny_stock']:
                    # Simple momentum strategy - look for stocks with positive change
                    if stock_data['change_percent'] > 5 and stock_data['volume'] > Config.MIN_VOLUME:
                        opportunities.append({
                            'symbol': symbol,
                            'price': stock_data['price'],
                            'change_percent': stock_data['change_percent'],
                            'volume': stock_data['volume'],
                            'signal': 'BUY',
                            'confidence': min(stock_data['change_percent'] / 10, 1.0)
                        })
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {str(e)}")
                continue
        
        # Sort by confidence score
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)
        return opportunities[:5]  # Return top 5 opportunities
    
    def get_intraday_data(self, symbol: str, interval: str = "1m") -> pd.DataFrame:
        """Get intraday data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval=interval)
            return data
        except Exception as e:
            logger.error(f"Error getting intraday data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate basic technical indicators"""
        if data.empty:
            return {}
        
        try:
            # Simple Moving Averages
            data['SMA_5'] = data['Close'].rolling(window=5).mean()
            data['SMA_10'] = data['Close'].rolling(window=10).mean()
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD
            ema_12 = data['Close'].ewm(span=12).mean()
            ema_26 = data['Close'].ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            
            current_price = data['Close'].iloc[-1]
            
            return {
                'current_price': float(current_price),
                'sma_5': float(data['SMA_5'].iloc[-1]) if not pd.isna(data['SMA_5'].iloc[-1]) else None,
                'sma_10': float(data['SMA_10'].iloc[-1]) if not pd.isna(data['SMA_10'].iloc[-1]) else None,
                'sma_20': float(data['SMA_20'].iloc[-1]) if not pd.isna(data['SMA_20'].iloc[-1]) else None,
                'rsi': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
                'macd': float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
                'signal': float(signal.iloc[-1]) if not pd.isna(signal.iloc[-1]) else None,
            }
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return {}
    
    def __del__(self):
        """Clean up database session"""
        if hasattr(self, 'session'):
            self.session.close()