from engine.main import VortexEngine
import time

def run_simulation():
    engine = VortexEngine()
    print("--- Starting Vortex HFT Simulation ---")
    
    # 1. Setup liquidity
    print("Populating Order Book (Liquidity Provision)...")
    engine.process_order("AAPL", "SELL", 150.10, 100)
    engine.process_order("AAPL", "SELL", 150.20, 100)
    engine.process_order("AAPL", "BUY", 149.90, 100)
    engine.process_order("AAPL", "BUY", 149.80, 100)
    
    # 2. Test Aggressive Orders
    print("\nTesting Aggressive BUY (Fill-or-Kill)...")
    res = engine.process_order("AAPL", "BUY", 150.15, 50, order_type="FOK")
    print(f"FOK Result: {res['status']} | Latency: {res['latency_ns']}ns")
    
    print("\nTesting Aggressive SELL (Immediate-or-Cancel)...")
    res = engine.process_order("AAPL", "SELL", 149.85, 150, order_type="IOC")
    print(f"IOC Result: {res['status']} | Trades: {len(res['trades'])} | Latency: {res['latency_ns']}ns")

    # 3. Test Risk Limits (Position Size)
    print("\nTesting Risk Limits (Max Position Size)...")
    res = engine.process_order("AAPL", "BUY", 151.00, 2000) # Max is 1000
    print(f"Large Order Result: {res['status']} | Reason: {res.get('reason')}")

    # 4. Final Stats
    print("\n--- Simulation Complete ---")
    stats = engine.get_stats()
    for k, v in stats.items():
        print(f"{k.upper()}: {v}")

if __name__ == "__main__":
    run_simulation()
