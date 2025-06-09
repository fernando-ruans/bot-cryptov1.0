#!/usr/bin/env python3
"""
Teste das APIs públicas para dados de mercado
"""

import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from src.config import Config
from src.market_data import MarketDataManager

def test_public_apis():
    """Testar todas as APIs públicas disponíveis"""
    print("=== TESTE DE APIS PÚBLICAS ===")
    
    config = Config()
    market_data = MarketDataManager(config)
    
    print(f"Modo demo: {market_data.demo_mode}")
    print(f"Usar APIs públicas: {market_data.use_public_apis}")
    print(f"Exchanges disponíveis: {list(market_data.exchanges.keys())}")
    
    # Testar diferentes símbolos
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
    
    for symbol in test_symbols:
        print(f"\n--- Testando {symbol} ---")
        
        try:
            # Forçar atualização
            market_data._update_crypto_data(symbol, '1h')
            
            # Verificar se dados foram obtidos
            cache_key = f"{symbol}_1h"
            if cache_key in market_data.data_cache:
                df = market_data.data_cache[cache_key]
                print(f"✓ Dados obtidos: {len(df)} registros")
                print(f"  Últimos preços: {df['close'].tail(3).tolist()}")
                print(f"  Período: {df.index[0]} até {df.index[-1]}")
                
                # Verificar se são dados reais (não todos iguais)
                price_variation = df['close'].std()
                if price_variation > 0:
                    print(f"✓ Dados reais detectados (variação: {price_variation:.2f})")
                else:
                    print("⚠ Possíveis dados simulados (sem variação)")
            else:
                print("❌ Nenhum dado no cache")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    print("\n=== TESTE DE API ESPECÍFICAS ===")
    
    # Testar CoinGecko diretamente
    try:
        print("\n--- Testando CoinGecko ---")
        df_cg = market_data._fetch_from_coingecko('BTCUSDT', '1h')
        print(f"✓ CoinGecko: {len(df_cg)} registros")
        print(f"  Preço atual: ${df_cg['close'].iloc[-1]:.2f}")
    except Exception as e:
        print(f"❌ CoinGecko falhou: {e}")
    
    # Testar Binance público
    try:
        print("\n--- Testando Binance Público ---")
        if 'binance_public' in market_data.exchanges:
            exchange = market_data.exchanges['binance_public']
            ohlcv = exchange.fetch_ohlcv('BTCUSDT', '1h', limit=10)
            print(f"✓ Binance público: {len(ohlcv)} registros")
            print(f"  Último preço: ${ohlcv[-1][4]:.2f}")
        else:
            print("❌ Binance público não inicializado")
    except Exception as e:
        print(f"❌ Binance público falhou: {e}")

if __name__ == "__main__":
    test_public_apis()
