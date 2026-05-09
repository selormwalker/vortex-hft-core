from .order_book import OrderBook
from .gateway import MarketDataGateway
from ..risk.manager import RiskManager
import time

class VortexEngine:
    def __init__(self):
        self.books = {}
        self.risk_manager = RiskManager()
        self.gateway = MarketDataGateway(self)
        self.last_prices = {} # Symbol -> Last Market Price

    def process_order(self, symbol, side, price, qty):
        """
        Processes an incoming order with pre-trade risk validation.
        """
        if not symbol:
            return {"status": "error", "reason": "Invalid Symbol"}

        # 1. Run Pre-Trade Risk Checks
        current_market_price = self.last_prices.get(symbol)
        is_valid, reason = self.risk_manager.check_order(symbol, side, price, qty, current_market_price)
        
        if not is_valid:
            print(f"[REJECTED] {symbol} | {reason}")
            return {"status": "rejected", "reason": reason}

        # 2. Matching Logic
        if symbol not in self.books:
            self.books[symbol] = OrderBook(symbol)
        
        self.books[symbol].add_order(side, price, qty)
        self.last_prices[symbol] = price 
        
        # 3. Post-Trade Position Update
        self.risk_manager.update_position(symbol, side, qty)
        
        print(f"[ACCEPTED] {symbol} | {side} {qty} @ {price}")
        return {"status": "accepted", "symbol": symbol}

    def ingest_raw_feed(self, raw_fix_stream):
        """Simulates ingestion from a high-speed FIX wire."""
        return self.gateway.on_tick_received(raw_fix_stream)

    def get_order_book(self, symbol):
        return self.books.get(symbol)
