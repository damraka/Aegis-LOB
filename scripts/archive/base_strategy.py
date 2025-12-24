import aegis_lob as lob
import time

def run_test():
    # Start the engine
    ob = lob.OrderBook()
    
    print("--- Aegis-LOB Python Kontrolü Başladı ---")
    
    # 1. Send buy and sell orders (Create Spread)
    ob.add_order(lob.Order(1, 100.0, 10, lob.Side.BUY, int(time.time())))
    ob.add_order(lob.Order(2, 105.0, 10, lob.Side.SELL, int(time.time())))
    
    print(f"En Iyi Alis: {ob.get_best_bid()}")
    print(f"En Iyi Satis: {ob.get_best_ask()}")
    print(f"Orta Fiyat: {ob.get_mid_price()}")
    
    # 2. Pairing Test (Buy Order Matching)
    print("\nEslestirme Testi Basliyor...")
    print("\nAgresif Alis Gonderiliyor (105.0 fiyattan)...")
    ob.add_order(lob.Order(3, 105.0, 5, lob.Side.BUY, int(time.time())))
    
if __name__ == "__main__":
    run_test()