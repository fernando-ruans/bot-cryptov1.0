#!/usr/bin/env python3
"""
Script de debug para verificar geração de sinais
"""

import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from src.config import Config
from src.ai_engine import AITradingEngine
from src.market_data import MarketDataManager
from src.signal_generator import SignalGenerator

def debug_signal_generation():
    """Debug da geração de sinais"""
    print("=== DEBUG: Geração de Sinais ===")
    
    # Inicializar componentes
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    symbol = 'BTCUSDT'
    timeframe = '1h'
    
    print(f"1. Testando obtenção de dados para {symbol}")
    df = market_data.get_historical_data(symbol, timeframe, 500)
    print(f"   Dados obtidos: {len(df)} registros")
    if df.empty:
        print("   ERRO: Nenhum dado obtido!")
        return
    
    print("   Colunas dos dados:", df.columns.tolist())
    print("   Últimas 3 linhas:")
    print(df.tail(3))
    
    print(f"\n2. Testando preço atual para {symbol}")
    current_price = market_data.get_current_price(symbol)
    print(f"   Preço atual: ${current_price}")
    
    print(f"\n3. Testando cooldown para {symbol}")
    is_cooldown = signal_generator._is_in_cooldown(symbol)
    print(f"   Em cooldown: {is_cooldown}")
    
    print(f"\n4. Testando indicadores técnicos")
    df_with_indicators = signal_generator.technical_indicators.calculate_all_indicators(df.copy())
    print(f"   Colunas após indicadores: {len(df_with_indicators.columns)}")
    
    print(f"\n5. Testando análise técnica")
    technical_analysis = signal_generator._analyze_technical_indicators(df_with_indicators)
    print(f"   Resultado análise técnica: {technical_analysis}")
    
    print(f"\n6. Testando predição de IA")
    ai_prediction = ai_engine.predict_signal(df_with_indicators, symbol)
    print(f"   Resultado predição IA: {ai_prediction}")
    
    print(f"\n7. Testando análise de volume")
    volume_analysis = signal_generator._analyze_volume(df_with_indicators)
    print(f"   Resultado análise volume: {volume_analysis}")
    
    print(f"\n8. Testando análise de volatilidade")
    volatility_analysis = signal_generator._analyze_volatility(df_with_indicators)
    print(f"   Resultado análise volatilidade: {volatility_analysis}")
    
    print(f"\n9. Testando contexto de mercado")
    market_context = signal_generator._analyze_market_context(symbol, timeframe)
    print(f"   Resultado contexto mercado: {market_context}")
    
    print(f"\n10. Testando combinação de análises")
    combined_signal = signal_generator._combine_analyses(
        technical_analysis,
        ai_prediction,
        volume_analysis,
        volatility_analysis,
        market_context
    )
    print(f"   Resultado combinado: {combined_signal}")
    
    print(f"\n11. Verificando configurações")
    print(f"   Confiança mínima: {config.SIGNAL_CONFIG['min_confidence']}")
    print(f"   Confluência habilitada: {config.SIGNAL_CONFIG['enable_confluence']}")
    print(f"   Cooldown (min): {config.SIGNAL_CONFIG['signal_cooldown_minutes']}")
    
    print(f"\n12. Tentando gerar sinal final")
    signal = signal_generator.generate_signal(symbol, timeframe)
    if signal:
        print(f"   SUCESSO! Sinal gerado: {signal.to_dict()}")
    else:
        print(f"   FALHA: Nenhum sinal gerado")
    
    print("\n=== FIM DEBUG ===")

if __name__ == "__main__":
    debug_signal_generation()
