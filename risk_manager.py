import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from config import Config
from database import Account, Position, Trade, SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskManager:
    """Risk management system to protect capital and manage positions"""
    
    def __init__(self):
        self.session = SessionLocal()
        self.max_daily_loss_reached = False
        self.original_capital = Config.INITIAL_CAPITAL
        
    def get_account_info(self) -> Dict:
        """Get current account information"""
        try:
            account = self.session.query(Account).first()
            if not account:
                # Create default account
                account = Account()
                self.session.add(account)
                self.session.commit()
            
            return {
                'total_capital': account.total_capital,
                'available_capital': account.available_capital,
                'invested_capital': account.invested_capital,
                'total_profit': account.total_profit,
                'bank_deposits': account.bank_deposits,
                'original_capital': self.original_capital
            }
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return {}
    
    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss_price: float) -> int:
        """Calculate appropriate position size based on risk management rules"""
        try:
            account_info = self.get_account_info()
            available_capital = account_info.get('available_capital', 0)
            
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss_price)
            
            # Maximum risk amount (2% of available capital)
            max_risk_amount = available_capital * Config.MAX_PORTFOLIO_RISK
            
            # Calculate position size
            if risk_per_share > 0:
                position_size = int(max_risk_amount / risk_per_share)
            else:
                position_size = 0
            
            # Apply maximum position size limit
            position_size = min(position_size, Config.MAX_POSITION_SIZE)
            
            # Ensure we don't exceed available capital
            total_cost = position_size * entry_price
            if total_cost > available_capital * 0.9:  # Leave 10% buffer
                position_size = int((available_capital * 0.9) / entry_price)
            
            logger.info(f"Calculated position size for {symbol}: {position_size} shares")
            return max(0, position_size)
            
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            return 0
    
    def validate_trade(self, symbol: str, action: str, shares: int, price: float) -> Tuple[bool, str]:
        """Validate if a trade should be executed based on risk parameters"""
        try:
            account_info = self.get_account_info()
            
            # Check if we have sufficient capital
            if action == "BUY":
                total_cost = shares * price
                if total_cost > account_info.get('available_capital', 0):
                    return False, "Insufficient capital for trade"
            
            # Check maximum number of open positions
            active_positions = self.session.query(Position).filter_by(is_active=True).count()
            if action == "BUY" and active_positions >= Config.MAX_OPEN_POSITIONS:
                return False, "Maximum number of open positions reached"
            
            # Check daily loss limit
            if self.check_daily_loss_limit():
                return False, "Daily loss limit reached"
            
            # Check if original capital is protected
            if not self.is_original_capital_protected():
                return False, "Original capital protection violated"
            
            return True, "Trade validated"
            
        except Exception as e:
            logger.error(f"Error validating trade: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    def check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit has been reached"""
        try:
            today = datetime.now().date()
            daily_trades = self.session.query(Trade).filter(
                Trade.executed_at >= today,
                Trade.profit_loss < 0
            ).all()
            
            daily_loss = sum(trade.profit_loss for trade in daily_trades)
            max_daily_loss = self.original_capital * Config.MAX_DAILY_LOSS
            
            if abs(daily_loss) >= max_daily_loss:
                self.max_daily_loss_reached = True
                logger.warning(f"Daily loss limit reached: {daily_loss}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking daily loss limit: {str(e)}")
            return False
    
    def is_original_capital_protected(self) -> bool:
        """Check if original capital is protected"""
        try:
            account_info = self.get_account_info()
            total_capital = account_info.get('total_capital', 0)
            
            # Original capital should always be protected
            # We only risk profits, not the original investment
            return total_capital >= self.original_capital * 0.95  # 5% buffer
            
        except Exception as e:
            logger.error(f"Error checking capital protection: {str(e)}")
            return False
    
    def calculate_stop_loss(self, entry_price: float, position_type: str = "LONG") -> float:
        """Calculate stop loss price"""
        if position_type == "LONG":
            return entry_price * (1 - Config.STOP_LOSS_PERCENTAGE)
        else:
            return entry_price * (1 + Config.STOP_LOSS_PERCENTAGE)
    
    def calculate_take_profit(self, entry_price: float, position_type: str = "LONG") -> float:
        """Calculate take profit price"""
        if position_type == "LONG":
            return entry_price * (1 + Config.TAKE_PROFIT_PERCENTAGE)
        else:
            return entry_price * (1 - Config.TAKE_PROFIT_PERCENTAGE)
    
    def should_close_position(self, position: Position, current_price: float) -> Tuple[bool, str]:
        """Determine if a position should be closed"""
        try:
            # Check stop loss
            if current_price <= position.stop_loss:
                return True, "STOP_LOSS"
            
            # Check take profit
            if current_price >= position.take_profit:
                return True, "TAKE_PROFIT"
            
            # Check if profit threshold is met for partial profit taking
            unrealized_profit = (current_price - position.entry_price) * position.shares
            profit_percentage = (current_price - position.entry_price) / position.entry_price
            
            if profit_percentage >= Config.MIN_PROFIT_THRESHOLD:
                return True, "PROFIT_TARGET"
            
            return False, "HOLD"
            
        except Exception as e:
            logger.error(f"Error checking position closure: {str(e)}")
            return False, "ERROR"
    
    def get_portfolio_risk_metrics(self) -> Dict:
        """Calculate portfolio risk metrics"""
        try:
            account_info = self.get_account_info()
            active_positions = self.session.query(Position).filter_by(is_active=True).all()
            
            total_invested = sum(pos.shares * pos.entry_price for pos in active_positions)
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in active_positions)
            
            # Calculate daily P&L
            today = datetime.now().date()
            daily_trades = self.session.query(Trade).filter(
                Trade.executed_at >= today
            ).all()
            daily_pnl = sum(trade.profit_loss for trade in daily_trades)
            
            return {
                'total_capital': account_info.get('total_capital', 0),
                'available_capital': account_info.get('available_capital', 0),
                'invested_capital': total_invested,
                'unrealized_pnl': total_unrealized_pnl,
                'daily_pnl': daily_pnl,
                'active_positions': len(active_positions),
                'capital_utilization': (total_invested / account_info.get('total_capital', 1)) * 100,
                'original_capital_protection': self.is_original_capital_protected()
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {str(e)}")
            return {}
    
    def reset_daily_limits(self):
        """Reset daily trading limits (called at market open)"""
        self.max_daily_loss_reached = False
        logger.info("Daily trading limits reset")
    
    def __del__(self):
        """Clean up database session"""
        if hasattr(self, 'session'):
            self.session.close()