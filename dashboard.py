import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
import logging

from config import Config
from database import init_db
from trading_engine import TradingEngine
from market_data import MarketDataService

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Initialize trading engine
trading_engine = TradingEngine()
market_data = MarketDataService()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Penny Stock Trading Dashboard"

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .main-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .metric-card {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                border-left: 4px solid #667eea;
            }
            .profit-positive {
                color: #28a745;
                font-weight: bold;
            }
            .profit-negative {
                color: #dc3545;
                font-weight: bold;
            }
            .trading-button {
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                border: none;
                color: white;
                padding: 12px 24px;
                border-radius: 25px;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            .trading-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# App layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("🚀 Penny Stock Trading Dashboard", className="text-center mb-0"),
                html.P("Intelligent Intraday Trading with Capital Protection", className="text-center mb-0 mt-2")
            ], className="main-header")
        ])
    ]),
    
    # Auto-refresh interval
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # Update every 30 seconds
        n_intervals=0
    ),
    
    # Portfolio Overview
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Portfolio Overview", className="card-title"),
                    html.Div(id="portfolio-metrics")
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Trading Controls
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Trading Controls", className="card-title"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("🔍 Scan Opportunities", id="scan-button", className="trading-button mb-2", style={"width": "100%"}),
                            dbc.Button("⚡ Auto Trade", id="auto-trade-button", className="trading-button mb-2", style={"width": "100%"}),
                            dbc.Button("📊 Update Positions", id="update-button", className="trading-button", style={"width": "100%"})
                        ], width=6),
                        dbc.Col([
                            html.Div(id="trading-status")
                        ], width=6)
                    ])
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Opportunities and Positions
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Trading Opportunities", className="card-title"),
                    html.Div(id="opportunities-table")
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Current Positions", className="card-title"),
                    html.Div(id="positions-table")
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    # Performance Charts
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Performance Chart", className="card-title"),
                    dcc.Graph(id="performance-chart")
                ])
            ])
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Profit Distribution", className="card-title"),
                    dcc.Graph(id="profit-chart")
                ])
            ])
        ], width=4)
    ], className="mb-4"),
    
    # Recent Trades
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Recent Trades", className="card-title"),
                    html.Div(id="recent-trades")
                ])
            ])
        ], width=12)
    ])
], fluid=True)

# Callbacks
@app.callback(
    Output('portfolio-metrics', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_portfolio_metrics(n):
    try:
        portfolio = trading_engine.get_portfolio_summary()
        account = portfolio.get('account', {})
        
        return dbc.Row([
            dbc.Col([
                html.H5(f"${account.get('total_capital', 0):.2f}", className="text-primary"),
                html.P("Total Capital", className="mb-0")
            ], width=2),
            dbc.Col([
                html.H5(f"${account.get('available_capital', 0):.2f}", className="text-success"),
                html.P("Available Capital", className="mb-0")
            ], width=2),
            dbc.Col([
                html.H5(f"${account.get('invested_capital', 0):.2f}", className="text-info"),
                html.P("Invested Capital", className="mb-0")
            ], width=2),
            dbc.Col([
                html.H5(f"${account.get('total_profit', 0):.2f}", 
                       className="profit-positive" if account.get('total_profit', 0) >= 0 else "profit-negative"),
                html.P("Total Profit", className="mb-0")
            ], width=2),
            dbc.Col([
                html.H5(f"${account.get('bank_deposits', 0):.2f}", className="text-warning"),
                html.P("Bank Deposits", className="mb-0")
            ], width=2),
            dbc.Col([
                html.H5(f"${account.get('daily_pnl', 0):.2f}", 
                       className="profit-positive" if account.get('daily_pnl', 0) >= 0 else "profit-negative"),
                html.P("Daily P&L", className="mb-0")
            ], width=2)
        ])
    except Exception as e:
        logger.error(f"Error updating portfolio metrics: {str(e)}")
        return html.Div("Error loading portfolio metrics")

@app.callback(
    Output('opportunities-table', 'children'),
    Input('scan-button', 'n_clicks'),
    Input('interval-component', 'n_intervals')
)
def update_opportunities(n_clicks, n_intervals):
    try:
        opportunities = trading_engine.get_trading_opportunities()
        
        if not opportunities:
            return html.P("No opportunities found")
        
        table_data = []
        for opp in opportunities:
            table_data.append(
                dbc.Row([
                    dbc.Col(html.Strong(opp['symbol']), width=2),
                    dbc.Col(f"${opp['price']:.2f}", width=2),
                    dbc.Col(f"{opp['change_percent']:.1f}%", width=2),
                    dbc.Col(f"{opp['suggested_position_size']}", width=2),
                    dbc.Col(f"{opp['confidence']:.2f}", width=2),
                    dbc.Col(
                        dbc.Button("Buy", size="sm", color="success", 
                                 id=f"buy-{opp['symbol']}", className="btn-sm"),
                        width=2
                    )
                ], className="mb-2 p-2 border-bottom")
            )
        
        return html.Div(table_data)
    except Exception as e:
        logger.error(f"Error updating opportunities: {str(e)}")
        return html.Div("Error loading opportunities")

@app.callback(
    Output('positions-table', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_positions(n):
    try:
        portfolio = trading_engine.get_portfolio_summary()
        positions = portfolio.get('positions', [])
        
        if not positions:
            return html.P("No active positions")
        
        table_data = []
        for pos in positions:
            pnl_class = "profit-positive" if pos['unrealized_pnl'] >= 0 else "profit-negative"
            table_data.append(
                dbc.Row([
                    dbc.Col(html.Strong(pos['symbol']), width=2),
                    dbc.Col(f"{pos['shares']}", width=2),
                    dbc.Col(f"${pos['entry_price']:.2f}", width=2),
                    dbc.Col(f"${pos['current_price']:.2f}", width=2),
                    dbc.Col(f"${pos['unrealized_pnl']:.2f}", width=2, className=pnl_class),
                    dbc.Col(f"{pos['pnl_percentage']:.1f}%", width=2, className=pnl_class)
                ], className="mb-2 p-2 border-bottom")
            )
        
        return html.Div(table_data)
    except Exception as e:
        logger.error(f"Error updating positions: {str(e)}")
        return html.Div("Error loading positions")

@app.callback(
    Output('performance-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_performance_chart(n):
    try:
        # Mock data for demo - in production, this would come from historical data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        portfolio = trading_engine.get_portfolio_summary()
        current_capital = portfolio.get('account', {}).get('total_capital', Config.INITIAL_CAPITAL)
        
        # Simulate portfolio growth
        values = []
        base_value = Config.INITIAL_CAPITAL
        for i, date in enumerate(dates):
            # Simple simulation of portfolio growth
            growth = (current_capital - base_value) * (i / len(dates))
            values.append(base_value + growth)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Portfolio Performance (30 Days)",
            xaxis_title="Date",
            yaxis_title="Portfolio Value ($)",
            hovermode='x unified',
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error updating performance chart: {str(e)}")
        return go.Figure()

@app.callback(
    Output('profit-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_profit_chart(n):
    try:
        portfolio = trading_engine.get_portfolio_summary()
        account = portfolio.get('account', {})
        
        # Create profit distribution chart
        reinvested = account.get('available_capital', 0) - Config.INITIAL_CAPITAL
        bank_deposits = account.get('bank_deposits', 0)
        
        if reinvested <= 0 and bank_deposits <= 0:
            return go.Figure()
        
        fig = go.Figure(data=[
            go.Pie(
                labels=['Reinvested', 'Bank Deposits'],
                values=[max(0, reinvested), bank_deposits],
                hole=.3,
                marker_colors=['#28a745', '#17a2b8']
            )
        ])
        
        fig.update_layout(
            title="Profit Distribution",
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error updating profit chart: {str(e)}")
        return go.Figure()

@app.callback(
    Output('recent-trades', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_recent_trades(n):
    try:
        portfolio = trading_engine.get_portfolio_summary()
        trades = portfolio.get('recent_trades', [])
        
        if not trades:
            return html.P("No recent trades")
        
        table_data = []
        for trade in trades:
            pnl_class = "profit-positive" if trade['profit_loss'] >= 0 else "profit-negative"
            table_data.append(
                dbc.Row([
                    dbc.Col(trade['symbol'], width=2),
                    dbc.Col(trade['action'], width=1),
                    dbc.Col(f"{trade['shares']}", width=1),
                    dbc.Col(f"${trade['price']:.2f}", width=2),
                    dbc.Col(f"${trade['profit_loss']:.2f}", width=2, className=pnl_class),
                    dbc.Col(trade['executed_at'].strftime('%H:%M:%S'), width=2)
                ], className="mb-1 p-1 border-bottom")
            )
        
        return html.Div(table_data)
    except Exception as e:
        logger.error(f"Error updating recent trades: {str(e)}")
        return html.Div("Error loading recent trades")

@app.callback(
    Output('trading-status', 'children'),
    Input('auto-trade-button', 'n_clicks'),
    Input('update-button', 'n_clicks')
)
def handle_trading_actions(auto_clicks, update_clicks):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    
    if 'auto-trade-button' in changed_id:
        try:
            executed_trades = trading_engine.auto_trade()
            if executed_trades:
                return dbc.Alert([
                    html.H6("Auto-trades executed:", className="alert-heading"),
                    html.Ul([
                        html.Li(f"{trade['symbol']}: {trade['message']}")
                        for trade in executed_trades
                    ])
                ], color="success")
            else:
                return dbc.Alert("No suitable opportunities found", color="info")
        except Exception as e:
            return dbc.Alert(f"Error executing auto-trade: {str(e)}", color="danger")
    
    elif 'update-button' in changed_id:
        try:
            trading_engine.update_positions()
            return dbc.Alert("Positions updated successfully", color="success")
        except Exception as e:
            return dbc.Alert(f"Error updating positions: {str(e)}", color="danger")
    
    return html.Div()

# Background task to update positions periodically
def background_update():
    """Background task to update positions every minute"""
    while True:
        try:
            trading_engine.update_positions()
            time.sleep(60)  # Update every minute
        except Exception as e:
            logger.error(f"Error in background update: {str(e)}")
            time.sleep(60)

# Start background thread
background_thread = threading.Thread(target=background_update, daemon=True)
background_thread.start()

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)