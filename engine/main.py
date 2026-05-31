from engine.order_book import OrderBook
from engine.gateway import MarketDataGateway
from risk.manager import RiskManager
import time

class VortexEngine:
    def __init__(self):
        self.books = {}
        self.risk_manager = RiskManager()
        self.gateway = MarketDataGateway(self)
        self.last_prices = {} # Symbol -> Last Market Price
        
        # Telemetry
        self.latency_history = []
        self.total_orders = 0
        self.total_trades = 0

    def process_order(self, symbol, side, price, qty, order_type='GTC'):
        """
        Processes an incoming order with pre-trade risk validation and nanosecond latency tracking.
        """
        start_time = time.perf_counter_ns()
        self.total_orders += 1

        if not symbol:
            return {"status": "error", "reason": "Invalid Symbol"}

        # 1. Run Pre-Trade Risk Checks
        current_market_price = self.last_prices.get(symbol)
        is_valid, reason = self.risk_manager.check_order(symbol, side, price, qty, current_market_price)
        
        if not is_valid:
            return {"status": "rejected", "reason": reason}

        # 2. Matching Logic
        if symbol not in self.books:
            self.books[symbol] = OrderBook(symbol)
        
        trades = self.books[symbol].add_order(side, price, qty, order_type)
        
        # 3. Handle Executions
        for trade in trades:
            self.total_trades += 1
            # Update last price to the latest execution price
            self.last_prices[symbol] = trade['price']
            # Update positions based on ACTUAL trades
            self.risk_manager.update_position(symbol, side, trade['qty'], trade['price'])

        # 4. Handle remaining GTC quantity (Risk manager needs to know about open exposure)
        # Note: In a production system, we'd distinguish between 'filled' and 'open' risk.
        
        end_time = time.perf_counter_ns()
        self.latency_history.append(end_time - start_time)
        
        status = "accepted" if (trades or order_type == 'GTC') else "cancelled"
        return {
            "status": status, 
            "symbol": symbol, 
            "trades": trades, 
            "latency_ns": end_time - start_time
        }

    def get_stats(self):
        avg_latency = sum(self.latency_history) / len(self.latency_history) if self.latency_history else 0
        return {
            "total_orders": self.total_orders,
            "total_trades": self.total_trades,
            "avg_latency_ns": avg_latency,
            "pnl": self.risk_manager.total_pnl,
            "halted": self.risk_manager.is_trading_halted
        }

    def ingest_raw_feed(self, raw_fix_stream):
        """Simulates ingestion from a high-speed FIX wire."""
        return self.gateway.on_tick_received(raw_fix_stream)

    def get_order_book(self, symbol):
        return self.books.get(symbol)
