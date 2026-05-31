import bisect
import ujson

class OrderBook:
    def __init__(self, symbol):
        self.symbol = symbol
        self.bids = [] # List of [price, quantity] sorted by price ascending
        self.asks = [] # List of [price, quantity] sorted by price ascending
        self.bid_prices = []
        self.ask_prices = []

    def add_order(self, side, price, quantity, order_type='GTC'):
        """
        Adds an order and attempts to match it against the opposite side of the book.
        order_type: 'GTC' (Good 'Til Cancelled), 'IOC' (Immediate or Cancel), 'FOK' (Fill or Kill)
        Returns a list of trades executed.
        """
        trades = []
        original_qty = quantity
        
        if order_type == 'FOK':
            if not self._can_fill_fully(side, price, quantity):
                return []

        if side == 'BUY':
            # Match against asks
            while quantity > 0 and self.asks and self.asks[0][0] <= price:
                best_ask_price, ask_qty = self.asks[0]
                fill_qty = min(quantity, ask_qty)
                
                trades.append({"price": best_ask_price, "qty": fill_qty, "side": "BUY"})
                
                quantity -= fill_qty
                self.asks[0][1] -= fill_qty
                
                if self.asks[0][1] == 0:
                    self.asks.pop(0)
                    self.ask_prices.pop(0)
            
            # Post-match logic
            if quantity > 0 and order_type == 'GTC':
                idx = bisect.bisect_left(self.bid_prices, price)
                # For bids, we want descending for matching, but bisect works on ascending.
                # We store bids ascendingly for bisect, but match from the end (highest price).
                self.bids.insert(idx, [price, quantity])
                self.bid_prices.insert(idx, price)
                
        else: # SELL
            # Match against bids (match highest price first)
            while quantity > 0 and self.bids and self.bids[-1][0] >= price:
                best_bid_price, bid_qty = self.bids[-1]
                fill_qty = min(quantity, bid_qty)
                
                trades.append({"price": best_bid_price, "qty": fill_qty, "side": "SELL"})
                
                quantity -= fill_qty
                self.bids[-1][1] -= fill_qty
                
                if self.bids[-1][1] == 0:
                    self.bids.pop(-1)
                    self.bid_prices.pop(-1)

            if quantity > 0 and order_type == 'GTC':
                idx = bisect.bisect_left(self.ask_prices, price)
                self.asks.insert(idx, [price, quantity])
                self.ask_prices.insert(idx, price)

        return trades

    def _can_fill_fully(self, side, price, quantity):
        """Checks if an order can be fully filled immediately."""
        temp_qty = quantity
        if side == 'BUY':
            for ask_p, ask_q in self.asks:
                if ask_p > price: break
                temp_qty -= ask_q
                if temp_qty <= 0: return True
        else:
            for bid_p, bid_q in reversed(self.bids):
                if bid_p < price: break
                temp_qty -= bid_q
                if temp_qty <= 0: return True
        return False

    def get_l1(self):
        """Returns the best bid and ask."""
        return {
            "bid": self.bids[-1][0] if self.bids else None,
            "ask": self.asks[0][0] if self.asks else None
        }
