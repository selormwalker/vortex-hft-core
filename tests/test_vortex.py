import pytest
from engine.main import VortexEngine

def test_matching_logic():
    engine = VortexEngine()
    
    # Phase 1: Adding Sell Orders
    engine.process_order("BTCUSD", "SELL", 60000, 1)
    engine.process_order("BTCUSD", "SELL", 60100, 2)
    
    book = engine.get_order_book("BTCUSD")
    assert 60000 in book.asks
    assert 60100 in book.asks
    
    # Phase 2: Matching Buy Order
    result = engine.process_order("BTCUSD", "BUY", 60200, 1.5)
    
    assert len(result["trades"]) == 2
    assert result["trades"][0]["price"] == 60000
    assert result["trades"][0]["qty"] == 1
    assert result["trades"][1]["price"] == 60100
    assert result["trades"][1]["qty"] == 0.5
    
    assert 60000 not in book.asks
    assert book.asks[60100] == 1.5
    
    # Phase 3: Risk Check (Fat Finger)
    result = engine.process_order("BTCUSD", "BUY", 70000, 1)
    assert result["status"] == "rejected"
