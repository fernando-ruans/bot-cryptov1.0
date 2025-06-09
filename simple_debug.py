#!/usr/bin/env python3
import sys
print("Iniciando debug simples...")

try:
    from src.config import Config
    print("✓ Config importado")
    
    config = Config()
    print("✓ Config criado")
    print(f"Min confidence: {config.SIGNAL_CONFIG['min_confidence']}")
    
    from src.market_data import MarketDataManager
    print("✓ MarketDataManager importado")
    
    market_data = MarketDataManager(config)
    print("✓ MarketDataManager criado")
    
    df = market_data.get_historical_data('BTCUSDT', '1h', 100)
    print(f"✓ Dados obtidos: {len(df)} registros")
    
    if len(df) > 0:
        print("✓ Dados válidos obtidos")
        print(f"Colunas: {list(df.columns)}")
        print(f"Último preço: {df['close'].iloc[-1]}")
    else:
        print("✗ Nenhum dado obtido")
        
except Exception as e:
    print(f"✗ Erro: {e}")
    import traceback
    traceback.print_exc()

print("Debug finalizado.")
