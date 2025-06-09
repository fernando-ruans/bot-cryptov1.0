#!/usr/bin/env python3

import ccxt
import pandas as pd

print("=== TESTE DIRETO BINANCE PÚBLICO ===")

try:
    # Criar exchange
    exchange = ccxt.binance({'enableRateLimit': True})
    print("✓ Exchange criado")
    
    # Buscar dados
    ohlcv = exchange.fetch_ohlcv('BTCUSDT', '1h', limit=5)
    print(f"✓ {len(ohlcv)} registros obtidos")
    
    # Mostrar dados
    for i, candle in enumerate(ohlcv):
        timestamp = pd.to_datetime(candle[0], unit='ms')
        print(f"  {i}: {timestamp} - Close: ${candle[4]:.2f}")
        
    print(f"\n🎯 DADOS REAIS FUNCIONANDO!")
    print(f"Último preço BTC: ${ohlcv[-1][4]:.2f}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
