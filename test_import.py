print("=== TESTE SIMPLES ===")

try:
    from src.config import Config
    print("✓ Config importado")
    
    from src.market_data import MarketDataManager
    print("✓ MarketDataManager importado")
    
    config = Config()
    market_data = MarketDataManager(config)
    print("✓ MarketDataManager inicializado")
    
    print(f"Demo mode: {market_data.demo_mode}")
    print(f"Public APIs: {market_data.use_public_apis}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
