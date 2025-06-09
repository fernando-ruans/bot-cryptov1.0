#!/usr/bin/env python3
"""
Teste simples das APIs públicas
"""

try:
    import ccxt
    print("✓ CCXT importado com sucesso")
    
    # Testar Binance público
    exchange = ccxt.binance({'enableRateLimit': True})
    print("✓ Binance público inicializado")
    
    # Buscar dados de teste
    ticker = exchange.fetch_ticker('BTC/USDT')
    print(f"✓ Preço atual BTC: ${ticker['last']:.2f}")
    
    # Buscar histórico
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=5)
    print(f"✓ Dados históricos: {len(ohlcv)} registros")
    print(f"  Último preço: ${ohlcv[-1][4]:.2f}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Testando CoinGecko ---")
try:
    import requests
    
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {'ids': 'bitcoin', 'vs_currencies': 'usd'}
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    btc_price = data['bitcoin']['usd']
    print(f"✓ CoinGecko BTC: ${btc_price:.2f}")
    
except Exception as e:
    print(f"❌ CoinGecko erro: {e}")

print("\n=== APIs PÚBLICAS TESTADAS ===")
