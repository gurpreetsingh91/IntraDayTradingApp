import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from config import Config
from database import Account, Position, Trade, BankTransaction, SessionLocal
from risk_manager import RiskManager
from market_data import MarketDataService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingEngine:
    """Core trading engine with profit splitting functionality"""
    
    def __init__(self):
        self.session = SessionLocal()
        self.risk_manager = RiskManager()
        self.market_data = MarketDataService()
        
    def execute_buy_order(self, symbol: str, shares: int, price: float) -> Tuple[bool, str]:
        """Execute a buy order"""
        try:
            # Validate the trade
            is_valid, message = self.risk_manager.validate_trade(symbol, "BUY", shares, price)
            if not is_valid:
                logger.warning(f"Buy order validation failed: {message}")
                return False, message
            
            total_cost = shares * price
            
            # Update account balance
            account = self.session.query(Account).first()
            if account.available_capital < total_cost:
                return False, "Insufficient funds"
            
            # Create position
            stop_loss = self.risk_manager.calculate_stop_loss(price)
            take_profit = self.risk_manager.calculate_take_profit(price)
            
            position = Position(
                symbol=symbol,
                shares=shares,
                entry_price=price,
                current_price=price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                unrealized_pnl=0.0
            )
            
            # Create trade record
            trade = Trade(
                symbol=symbol,
                action="BUY",
                shares=shares,
                price=price,
                total_amount=total_cost,
                trade_type="MANUAL"
            )
            
            # Update account
            account.available_capital -= total_cost
            account.invested_capital += total_cost
            
            # Save to database
            self.session.add(position)
            self.session.add(trade)
            self.session.commit()
            
            logger.info(f"Buy order executed: {shares} shares of {symbol} at ${price:.2f}")
            return True, f"Successfully bought {shares} shares of {symbol}"
            
        except Exception as e:
            logger.error(f"Error executing buy order: {str(e)}")
            self.session.rollback()
            return False, f"Error executing buy order: {str(e)}"
    
    def execute_sell_order(self, symbol: str, shares: int, price: float, trade_type: str = "MANUAL") -> Tuple[bool, str]:
        """Execute a sell order with profit splitting"""
        try:
            # Find the position
            position = self.session.query(Position).filter_by(
                symbol=symbol, 
                is_active=True
            ).first()
            
            if not position:
                return False, f"No active position found for {symbol}"
            
            if shares > position.shares:
                return False, f"Cannot sell {shares} shares, only {position.shares} available"
            
            # Calculate profit/loss
            total_proceeds = shares * price
            cost_basis = shares * position.entry_price
            profit_loss = total_proceeds - cost_basis
            
            # Create trade record
            trade = Trade(
                symbol=symbol,
                action="SELL",
                shares=shares,
                price=price,
                total_amount=total_proceeds,
                profit_loss=profit_loss,
                trade_type=trade_type
            )
            
            # Handle profit splitting if there's a profit
            if profit_loss > 0:
                self.handle_profit_splitting(profit_loss, trade)
            
            # Update position
            if shares == position.shares:
                # Close entire position
                position.is_active = False
            else:
                # Reduce position size
                position.shares -= shares
            
            # Update account
            account = self.session.query(Account).first()
            account.available_capital += cost_basis  # Return original investment
            account.invested_capital -= cost_basis
            
            if profit_loss > 0:
                # Add 50% of profit to available capital for reinvestment
                reinvestment_amount = profit_loss * Config.REINVESTMENT_PERCENTAGE
                account.available_capital += reinvestment_amount
                account.total_profit += profit_loss
            else:
                # Loss - adjust available capital
                account.available_capital += profit_loss
            
            # Update total capital
            account.total_capital = account.available_capital + account.invested_capital
            
            # Save to database
            self.session.add(trade)
            self.session.commit()
            
            logger.info(f"Sell order executed: {shares} shares of {symbol} at ${price:.2f}, P&L: ${profit_loss:.2f}")
            return True, f"Successfully sold {shares} shares of {symbol}"
            
        except Exception as e:
            logger.error(f"Error executing sell order: {str(e)}")
            self.session.rollback()
            return False, f"Error executing sell order: {str(e)}"
    
    def handle_profit_splitting(self, profit: float, trade: Trade):
        """Handle the 50/50 profit splitting logic"""
        try:
            # Calculate split amounts
            reinvestment_amount = profit * Config.REINVESTMENT_PERCENTAGE
            bank_deposit_amount = profit * Config.BANK_DEPOSIT_PERCENTAGE
            
            # Update trade record
            trade.profit_reinvested = reinvestment_amount
            trade.profit_to_bank = bank_deposit_amount
            
            # Create bank transaction
            bank_transaction = BankTransaction(
                amount=bank_deposit_amount,
                transaction_type="DEPOSIT",
                reference_trade_id=trade.id,
                status="COMPLETED"
            )
            
            # Update account bank deposits
            account = self.session.query(Account).first()
            account.bank_deposits += bank_deposit_amount
            
            self.session.add(bank_transaction)
            
            logger.info(f"Profit split - Reinvestment: ${reinvestment_amount:.2f}, Bank Deposit: ${bank_deposit_amount:.2f}")
            
        except Exception as e:
            logger.error(f"Error handling profit splitting: {str(e)}")
    
    def update_positions(self):
        """Update all active positions with current market prices"""
        try:
            active_positions = self.session.query(Position).filter_by(is_active=True).all()
            
            for position in active_positions:
                # Get current price
                stock_data = self.market_data.get_stock_data(position.symbol)
                if stock_data:
                    current_price = stock_data['price']
                    position.current_price = current_price
                    
                    # Calculate unrealized P&L
                    position.unrealized_pnl = (current_price - position.entry_price) * position.shares
                    
                    # Check if position should be closed
                    should_close, reason = self.risk_manager.should_close_position(position, current_price)
                    
                    if should_close:
                        logger.info(f"Auto-closing position {position.symbol} due to {reason}")
                        self.execute_sell_order(position.symbol, position.shares, current_price, reason)
            
            self.session.commit()
            
        except Exception as e:
            logger.error(f"Error updating positions: {str(e)}")
            self.session.rollback()
    
    def get_trading_opportunities(self) -> List[Dict]:
        """Get trading opportunities based on market scan"""
        try:
            opportunities = self.market_data.scan_for_opportunities()
            
            # Filter opportunities based on risk management
            valid_opportunities = []
            for opp in opportunities:
                entry_price = opp['price']
                stop_loss = self.risk_manager.calculate_stop_loss(entry_price)
                position_size = self.risk_manager.calculate_position_size(
                    opp['symbol'], entry_price, stop_loss
                )
                
                if position_size > 0:
                    opp['suggested_position_size'] = position_size
                    opp['stop_loss'] = stop_loss
                    opp['take_profit'] = self.risk_manager.calculate_take_profit(entry_price)
                    valid_opportunities.append(opp)
            
            return valid_opportunities
            
        except Exception as e:
            logger.error(f"Error getting trading opportunities: {str(e)}")
            return []
    
    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""
        try:
            account = self.session.query(Account).first()
            active_positions = self.session.query(Position).filter_by(is_active=True).all()
            
            # Calculate portfolio metrics
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in active_positions)
            total_invested = sum(pos.shares * pos.entry_price for pos in active_positions)
            
            # Get recent trades
            recent_trades = self.session.query(Trade).order_by(
                Trade.executed_at.desc()
            ).limit(10).all()
            
            # Calculate today's P&L
            today = datetime.now().date()
            daily_trades = self.session.query(Trade).filter(
                Trade.executed_at >= today
            ).all()
            daily_pnl = sum(trade.profit_loss for trade in daily_trades)
            
            return {
                'account': {
                    'total_capital': account.total_capital,
                    'available_capital': account.available_capital,
                    'invested_capital': account.invested_capital,
                    'total_profit': account.total_profit,
                    'bank_deposits': account.bank_deposits,
                    'unrealized_pnl': total_unrealized_pnl,
                    'daily_pnl': daily_pnl
                },
                'positions': [
                    {
                        'symbol': pos.symbol,
                        'shares': pos.shares,
                        'entry_price': pos.entry_price,
                        'current_price': pos.current_price,
                        'unrealized_pnl': pos.unrealized_pnl,
                        'pnl_percentage': ((pos.current_price - pos.entry_price) / pos.entry_price) * 100
                    }
                    for pos in active_positions
                ],
                'recent_trades': [
                    {
                        'symbol': trade.symbol,
                        'action': trade.action,
                        'shares': trade.shares,
                        'price': trade.price,
                        'profit_loss': trade.profit_loss,
                        'executed_at': trade.executed_at
                    }
                    for trade in recent_trades
                ],
                'risk_metrics': self.risk_manager.get_portfolio_risk_metrics()
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {str(e)}")
            return {}
    
    def auto_trade(self) -> List[Dict]:
        """Execute automated trading based on opportunities"""
        try:
            opportunities = self.get_trading_opportunities()
            executed_trades = []
            
            for opp in opportunities[:3]:  # Execute top 3 opportunities
                if opp['confidence'] > 0.7:  # High confidence threshold
                    success, message = self.execute_buy_order(
                        opp['symbol'],
                        opp['suggested_position_size'],
                        opp['price']
                    )
                    
                    executed_trades.append({
                        'symbol': opp['symbol'],
                        'action': 'BUY',
                        'success': success,
                        'message': message,
                        'confidence': opp['confidence']
                    })
            
            return executed_trades
            
        except Exception as e:
            logger.error(f"Error in auto trading: {str(e)}")
            return []
    
    def __del__(self):
        """Clean up database session"""
        if hasattr(self, 'session'):
            self.session.close()