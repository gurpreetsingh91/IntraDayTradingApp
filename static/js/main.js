// Main JavaScript for Penny Stock Trading Application

// Global variables
let refreshInterval;
let chartInstances = {};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Penny Stock Trading App Initialized');
    
    // Initialize components
    initializeApp();
    setupEventListeners();
    startAutoRefresh();
    
    // Add loading states to buttons
    setupButtonLoading();
    
    // Initialize tooltips if available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// Application initialization
function initializeApp() {
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Initialize any existing charts
    initializeExistingCharts();
    
    // Show welcome message
    showWelcomeMessage();
}

// Setup event listeners
function setupEventListeners() {
    // Global refresh button
    const refreshBtn = document.getElementById('refreshData');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            refreshData();
            showNotification('Data refreshed', 'info');
        });
    }
    
    // Trading control buttons
    setupTradingControls();
    
    // Buy/Sell buttons
    setupTradeButtons();
    
    // Auto-refresh toggle
    setupAutoRefreshToggle();
    
    // Keyboard shortcuts
    setupKeyboardShortcuts();
}

// Setup trading control buttons
function setupTradingControls() {
    const controls = {
        'scanOpportunities': {
            action: scanOpportunities,
            loadingText: 'Scanning...'
        },
        'autoTrade': {
            action: autoTrade,
            loadingText: 'Trading...'
        },
        'updatePositions': {
            action: updatePositions,
            loadingText: 'Updating...'
        }
    };
    
    Object.keys(controls).forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener('click', function() {
                const control = controls[id];
                setButtonLoading(this, control.loadingText);
                control.action().finally(() => {
                    resetButtonLoading(this);
                });
            });
        }
    });
}

// Setup buy/sell buttons
function setupTradeButtons() {
    // Buy buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('buy-btn') || e.target.closest('.buy-btn')) {
            const btn = e.target.classList.contains('buy-btn') ? e.target : e.target.closest('.buy-btn');
            const symbol = btn.dataset.symbol;
            const price = parseFloat(btn.dataset.price);
            const shares = parseInt(btn.dataset.shares);
            
            if (confirm(`Buy ${shares} shares of ${symbol} at $${price.toFixed(2)}?`)) {
                setButtonLoading(btn, 'Buying...');
                executeBuy(symbol, shares, price).finally(() => {
                    resetButtonLoading(btn);
                });
            }
        }
        
        // Sell buttons
        if (e.target.classList.contains('sell-btn') || e.target.closest('.sell-btn')) {
            const btn = e.target.classList.contains('sell-btn') ? e.target : e.target.closest('.sell-btn');
            const symbol = btn.dataset.symbol;
            const price = parseFloat(btn.dataset.price);
            const shares = parseInt(btn.dataset.shares);
            
            if (confirm(`Sell ${shares} shares of ${symbol} at $${price.toFixed(2)}?`)) {
                setButtonLoading(btn, 'Selling...');
                executeSell(symbol, shares, price).finally(() => {
                    resetButtonLoading(btn);
                });
            }
        }
    });
}

// API Functions
async function scanOpportunities() {
    try {
        showStatus('Scanning for opportunities...', 'info');
        
        const response = await fetch('/api/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatus(data.message, 'success');
            showNotification(`Found ${data.opportunities?.length || 0} opportunities`, 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showStatus('Error: ' + data.error, 'danger');
            showNotification('Scan failed', 'error');
        }
    } catch (error) {
        console.error('Scan error:', error);
        showStatus('Error scanning opportunities', 'danger');
        showNotification('Network error during scan', 'error');
    }
}

async function autoTrade() {
    try {
        showStatus('Executing automated trades...', 'info');
        
        const response = await fetch('/api/auto_trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatus(data.message, 'success');
            showNotification(`Executed ${data.trades?.length || 0} trades`, 'success');
            setTimeout(() => location.reload(), 2000);
        } else {
            showStatus('Error: ' + data.error, 'danger');
            showNotification('Auto-trade failed', 'error');
        }
    } catch (error) {
        console.error('Auto-trade error:', error);
        showStatus('Error executing auto trade', 'danger');
        showNotification('Network error during auto-trade', 'error');
    }
}

async function updatePositions() {
    try {
        showStatus('Updating positions...', 'info');
        
        const response = await fetch('/api/update_positions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatus(data.message, 'success');
            showNotification('Positions updated', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showStatus('Error: ' + data.error, 'danger');
            showNotification('Update failed', 'error');
        }
    } catch (error) {
        console.error('Update error:', error);
        showStatus('Error updating positions', 'danger');
        showNotification('Network error during update', 'error');
    }
}

async function executeBuy(symbol, shares, price) {
    try {
        showStatus(`Buying ${shares} shares of ${symbol}...`, 'info');
        
        const response = await fetch('/api/buy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                symbol: symbol,
                shares: shares,
                price: price
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatus(data.message, 'success');
            showNotification(`Bought ${shares} shares of ${symbol}`, 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showStatus('Error: ' + data.message, 'danger');
            showNotification('Buy order failed', 'error');
        }
    } catch (error) {
        console.error('Buy error:', error);
        showStatus('Error executing buy order', 'danger');
        showNotification('Network error during buy', 'error');
    }
}

async function executeSell(symbol, shares, price) {
    try {
        showStatus(`Selling ${shares} shares of ${symbol}...`, 'info');
        
        const response = await fetch('/api/sell', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                symbol: symbol,
                shares: shares,
                price: price
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatus(data.message, 'success');
            showNotification(`Sold ${shares} shares of ${symbol}`, 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showStatus('Error: ' + data.message, 'danger');
            showNotification('Sell order failed', 'error');
        }
    } catch (error) {
        console.error('Sell error:', error);
        showStatus('Error executing sell order', 'danger');
        showNotification('Network error during sell', 'error');
    }
}

// Data refresh functions
async function refreshData() {
    try {
        const response = await fetch('/api/portfolio');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        updatePortfolioMetrics(data);
        updatePositionsData();
        updateOpportunitiesData();
        
    } catch (error) {
        console.error('Error refreshing data:', error);
        showNotification('Failed to refresh data', 'error');
    }
}

async function updatePositionsData() {
    try {
        const response = await fetch('/api/positions');
        const positions = await response.json();
        
        updatePositionsTable(positions);
    } catch (error) {
        console.error('Error updating positions:', error);
    }
}

async function updateOpportunitiesData() {
    try {
        const response = await fetch('/api/opportunities');
        const opportunities = await response.json();
        
        updateOpportunitiesTable(opportunities);
    } catch (error) {
        console.error('Error updating opportunities:', error);
    }
}

// UI Update functions
function updatePortfolioMetrics(data) {
    const metricUpdates = [
        { selector: '.metric-value', property: 'total_capital' },
        { selector: '.metric-value', property: 'available_capital' },
        { selector: '.metric-value', property: 'invested_capital' },
        { selector: '.metric-value', property: 'total_profit' },
        { selector: '.metric-value', property: 'bank_deposits' },
        { selector: '.metric-value', property: 'daily_pnl' }
    ];
    
    const elements = document.querySelectorAll('.metric-value');
    const values = [
        data.account?.total_capital,
        data.account?.available_capital,
        data.account?.invested_capital,
        data.account?.total_profit,
        data.account?.bank_deposits,
        data.account?.daily_pnl
    ];
    
    elements.forEach((element, index) => {
        if (values[index] !== undefined) {
            element.textContent = '$' + values[index].toFixed(2);
            
            // Add color coding for profit/loss
            if (index === 3 || index === 5) { // profit and daily P&L
                element.className = element.className.replace(/text-(success|danger)/, '');
                element.classList.add(values[index] >= 0 ? 'text-success' : 'text-danger');
            }
        }
    });
}

function updatePositionsTable(positions) {
    // This would update the positions table if it exists on the current page
    // Implementation depends on the specific page structure
}

function updateOpportunitiesTable(opportunities) {
    // This would update the opportunities table if it exists on the current page
    // Implementation depends on the specific page structure
}

// Status and notification functions
function showStatus(message, type) {
    const statusDiv = document.getElementById('tradingStatus');
    if (statusDiv) {
        statusDiv.className = `alert alert-${type}`;
        statusDiv.innerHTML = `<i class="fas fa-info-circle me-2"></i>${message}`;
        
        // Auto-hide success/info messages after 5 seconds
        if (type === 'success' || type === 'info') {
            setTimeout(() => {
                statusDiv.className = 'alert alert-info';
                statusDiv.innerHTML = '<i class="fas fa-info-circle me-2"></i>Ready to trade. Click a button above to get started.';
            }, 5000);
        }
    }
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} notification-toast fade-in`;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 4000);
}

function showWelcomeMessage() {
    // Show welcome message on first visit
    if (!localStorage.getItem('welcomeShown')) {
        setTimeout(() => {
            showNotification('Welcome to Penny Stock Trader! 🚀', 'info');
            localStorage.setItem('welcomeShown', 'true');
        }, 1000);
    }
}

// Button loading states
function setButtonLoading(button, text) {
    if (!button) return;
    
    button.disabled = true;
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${text}`;
    button.classList.add('loading');
}

function resetButtonLoading(button) {
    if (!button) return;
    
    button.disabled = false;
    if (button.dataset.originalText) {
        button.innerHTML = button.dataset.originalText;
        delete button.dataset.originalText;
    }
    button.classList.remove('loading');
}

function setupButtonLoading() {
    // Add loading states to all buttons by default
    document.querySelectorAll('button[type="submit"], .btn').forEach(btn => {
        if (!btn.hasAttribute('data-no-loading')) {
            btn.addEventListener('click', function() {
                if (!this.disabled) {
                    setButtonLoading(this, 'Loading...');
                    
                    // Reset after 10 seconds if not manually reset
                    setTimeout(() => {
                        resetButtonLoading(this);
                    }, 10000);
                }
            });
        }
    });
}

// Auto-refresh functionality
function startAutoRefresh() {
    // Start auto-refresh every 30 seconds
    refreshInterval = setInterval(refreshData, 30000);
    
    // Add visual indicator
    addRefreshIndicator();
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

function setupAutoRefreshToggle() {
    // Create auto-refresh toggle if it doesn't exist
    const navbar = document.querySelector('.navbar-nav:last-child');
    if (navbar && !document.getElementById('autoRefreshToggle')) {
        const toggleHtml = `
            <li class="nav-item">
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" id="autoRefreshToggle" checked>
                    <label class="form-check-label text-light" for="autoRefreshToggle">Auto-refresh</label>
                </div>
            </li>
        `;
        navbar.insertAdjacentHTML('beforeend', toggleHtml);
        
        document.getElementById('autoRefreshToggle').addEventListener('change', function() {
            if (this.checked) {
                startAutoRefresh();
                showNotification('Auto-refresh enabled', 'info');
            } else {
                stopAutoRefresh();
                showNotification('Auto-refresh disabled', 'info');
            }
        });
    }
}

function addRefreshIndicator() {
    // Add a subtle refresh indicator
    const indicator = document.createElement('div');
    indicator.id = 'refreshIndicator';
    indicator.className = 'status-indicator online';
    indicator.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9998;
    `;
    indicator.title = 'Auto-refresh active';
    
    document.body.appendChild(indicator);
}

// Chart helper functions
function initializeExistingCharts() {
    // Initialize any charts that might exist on the page
    if (typeof Chart !== 'undefined') {
        // Portfolio chart
        const portfolioCanvas = document.getElementById('portfolioChart');
        if (portfolioCanvas && !chartInstances.portfolio) {
            // Chart initialization would go here
        }
        
        // Profit chart
        const profitCanvas = document.getElementById('profitChart');
        if (profitCanvas && !chartInstances.profit) {
            // Chart initialization would go here
        }
    }
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + R: Refresh data
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            refreshData();
            showNotification('Data refreshed via keyboard shortcut', 'info');
        }
        
        // Ctrl/Cmd + S: Scan opportunities
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const scanBtn = document.getElementById('scanOpportunities');
            if (scanBtn) {
                scanBtn.click();
            }
        }
        
        // Ctrl/Cmd + T: Auto trade
        if ((e.ctrlKey || e.metaKey) && e.key === 't') {
            e.preventDefault();
            const tradeBtn = document.getElementById('autoTrade');
            if (tradeBtn) {
                tradeBtn.click();
            }
        }
    });
}

// Utility functions
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

function formatPercentage(value) {
    return (value * 100).toFixed(2) + '%';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    showNotification('An error occurred. Please refresh the page.', 'error');
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showNotification('Network error. Please check your connection.', 'error');
});

// Export functions for global access
window.TradingApp = {
    refreshData,
    scanOpportunities,
    autoTrade,
    updatePositions,
    executeBuy,
    executeSell,
    showNotification,
    formatCurrency,
    formatPercentage
};