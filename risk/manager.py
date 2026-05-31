import ujson

class RiskManager:
    def __init__(self, max_pos_size=1000, max_drawdown=0.05, price_collar=0.10):
        self.max_pos_size = max_pos_size
        self.max_drawdown = max_drawdown
        self.price_collar = price_collar
        
        self.current_positions = {} # Symbol -> Quantity
        self.total_pnl = 0.0
        self.peak_pnl = 0.0
        self.is_trading_halted = False

    def check_order(self, symbol, side, price, qty, current_market_price):
        """
        Performs pre-trade risk validation.
        Returns (bool, str) -> (is_valid, reason)
        """
        if self.is_trading_halted:
            return False, "Risk Error: Trading halted due to risk limits."

        # 1. Position Size Check
        current_qty = self.current_positions.get(symbol, 0)
        potential_qty = current_qty + qty if side == 'BUY' else current_qty - qty
        
        if abs(potential_qty) > self.max_pos_size:
            return False, f"Risk Error: Order exceeds MAX_POS_SIZE ({self.max_pos_size})"

        # 2. Price Collar Check (Fat Finger Protection)
        if current_market_price:
            price_diff = abs(price - current_market_price) / current_market_price
            if price_diff > self.price_collar:
                return False, f"Risk Error: Order price outside COLLAR LIMIT ({self.price_collar * 100}%)"

        # 3. Drawdown Check
        if self.peak_pnl > 0:
            drawdown = (self.peak_pnl - self.total_pnl) / self.peak_pnl
            if drawdown > self.max_drawdown:
                self.is_trading_halted = True
                return False, f"Risk Error: MAX_DRAWDOWN EXCEEDED ({drawdown*100:.2f}%)"

        return True, "Risk Check Passed"

    def update_position(self, symbol, side, qty, exec_price=None):
        """Updates the internal position tracker after a successful execution."""
        change = qty if side == 'BUY' else -qty
        self.current_positions[symbol] = self.current_positions.get(symbol, 0) + change
        
    def update_pnl(self, realized_pnl):
        """Update total PnL and track peak for drawdown calculation."""
        self.total_pnl += realized_pnl
        if self.total_pnl > self.peak_pnl:
            self.peak_pnl = self.total_pnl
