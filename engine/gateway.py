class FIXParser:
    """
    High-performance parser for FIX (Financial Information eXchange) messages.
    Focuses on minimal overhead for high-frequency market data ingestion.
    """
    SOH = "\x01" # Standard FIX delimiter

    @staticmethod
    def parse(message: str):
        """
        Decodes a tag=value string into a high-speed dictionary.
        Example: 8=FIX.4.2|35=D|55=BTCUSD|44=65000|
        """
        pairs = message.strip(FIXParser.SOH).split(FIXParser.SOH)
        msg_dict = {}
        for pair in pairs:
            if "=" in pair:
                tag, value = pair.split("=", 1)
                msg_dict[tag] = value
        return msg_dict

    @staticmethod
    def encode(msg_dict: dict):
        """
        Encodes a dictionary into a standard FIX message string.
        """
        return FIXParser.SOH.join([f"{k}={v}" for k, v in msg_dict.items()]) + FIXParser.SOH

class MarketDataGateway:
    """
    Simulates a low-latency gateway for receiving exchange tick data.
    """
    def __init__(self, engine):
        self.engine = engine
        self.msg_count = 0

    def on_tick_received(self, raw_fix_msg: str):
        """
        Entry point for raw market data strings.
        """
        parsed = FIXParser.parse(raw_fix_msg)
        symbol = parsed.get("55") # Tag 55: Symbol
        side = "BUY" if parsed.get("54") == "1" else "SELL" # Tag 54: Side
        price = float(parsed.get("44", 0)) # Tag 44: Price
        qty = float(parsed.get("38", 0)) # Tag 38: Quantity
        
        self.msg_count += 1
        return self.engine.process_order(symbol, side, price, qty)
