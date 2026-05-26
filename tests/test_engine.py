import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.main import VortexEngine

def test_matching_logic():
    engine = VortexEngine()
    
    print("--- Phase 1: Adding Sell Orders ---")
    # Add some sell orders
    engine.process_order("BTCUSD", "SELL", 60000, 1)
    engine.process_order("BTCUSD", "SELL", 60100, 2)
    
    book = engine.get_order_book("BTCUSD")
    assert 60000 in book.asks
    assert 60100 in book.asks
    
    print("\n--- Phase 2: Matching Buy Order ---")
    # Add a buy order that matches
    # This should match 1 BTC @ 60000 and 0.5 BTC @ 60100
    result = engine.process_order("BTCUSD", "BUY", 60200, 1.5)
    
    assert len(result["trades"]) == 2
    assert result["trades"][0]["price"] == 60000
    assert result["trades"][0]["qty"] == 1
    assert result["trades"][1]["price"] == 60100
    assert result["trades"][1]["qty"] == 0.5
    
    assert 60000 not in book.asks
    assert book.asks[60100] == 1.5
    
    print("\n--- Phase 3: Risk Check (Fat Finger) ---")
    # Last price was 60200 (from the accepted buy order)
    # Price collar is 10% by default in RiskManager
    # 70000 is > 10% away from 60200
    result = engine.process_order("BTCUSD", "BUY", 70000, 1)
    assert result["status"] == "rejected"
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_matching_logic()
