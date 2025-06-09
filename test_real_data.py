#!/usr/bin/env python3
"""
Teste específico para verificar se dados reais estão sendo usados
"""

import logging
import sys
import pandas as pd

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from src.config import Config
from src.market_data import MarketDataManager
from src.signal_generator import SignalGenerator
from src.ai_engine import AITradingEngine

def test_real_data():
    """Verificar se estamos usando dados reais"""
    print("=== VERIFICAÇÃO DE DADOS REAIS ===")
    
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    print(f"Modo demo: {market_data.demo_mode}")
    print(f"Usar APIs públicas: {market_data.use_public_apis}")
    print(f"Exchanges disponíveis: {list(market_data.exchanges.keys())}")
    
    # Buscar dados para BTC
    symbol = 'BTCUSDT'
    timeframe = '1h'
    
    print(f"\n--- Buscando dados para {symbol} {timeframe} ---")
    
    # Forçar atualização usando APIs públicas
    market_data._update_crypto_data(symbol, timeframe)
    
    # Verificar cache
    cache_key = f"{symbol}_{timeframe}"
    if cache_key in market_data.data_cache:
        df = market_data.data_cache[cache_key]
        print(f"✓ Dados no cache: {len(df)} registros")
        
        # Verificar últimos preços
        latest_prices = df['close'].tail(5)
        print(f"✓ Últimos 5 preços: {latest_prices.tolist()}")
        
        # Verificar variação
        price_std = df['close'].std()
        price_range = df['close'].max() - df['close'].min()
        
        print(f"✓ Desvio padrão: {price_std:.2f}")
        print(f"✓ Faixa de preços: {price_range:.2f}")
        
        # Determinar se são dados reais ou simulados
        if price_std > 1000:  # BTC tem alta variação
            print("🎯 DADOS REAIS DETECTADOS!")
        else:
            print("⚠ Possíveis dados simulados")
            
        # Mostrar informações detalhadas
        print(f"✓ Período: {df.index[0]} até {df.index[-1]}")
        print(f"✓ Preço atual: ${df['close'].iloc[-1]:.2f}")
        
        # Testar geração de sinal com dados reais
        print(f"\n--- Testando geração de sinal com dados reais ---")
        
        if symbol in signal_generator.last_signal_time:
            del signal_generator.last_signal_time[symbol]
            
        signal = signal_generator.generate_signal(symbol, timeframe)
        
        if signal:
            print(f"🎯 SINAL GERADO COM DADOS REAIS!")
            print(f"  Tipo: {signal.signal_type}")
            print(f"  Confiança: {signal.confidence:.2f}")
            print(f"  Preço real: ${signal.entry_price:.2f}")
            print(f"  Stop Loss: ${signal.stop_loss:.2f}")
            print(f"  Take Profit: ${signal.take_profit:.2f}")
        else:
            print("❌ Nenhum sinal gerado")
    else:
        print("❌ Nenhum dado no cache")

if __name__ == "__main__":
    test_real_data()
