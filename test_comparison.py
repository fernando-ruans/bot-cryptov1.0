#!/usr/bin/env python3
"""
Comparação entre signal_generator direto vs servidor
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=== COMPARAÇÃO SIGNAL GENERATOR ===")

try:
    from src.config import Config
    from src.market_data import MarketDataManager
    from src.ai_engine import AITradingEngine
    from src.signal_generator import SignalGenerator
    
    # Criar exatamente como no main.py
    print("1. Criando componentes como no main.py...")
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    print("✅ Componentes criados")
    
    # Verificar configurações
    print(f"\n2. Verificando configurações:")
    print(f"   Min AI confidence: {config.SIGNAL_CONFIG.get('min_ai_confidence', 'NOT SET')}")
    print(f"   Min market score: {config.SIGNAL_CONFIG.get('min_market_score', 'NOT SET')}")
    
    # Testar com os mesmos parâmetros do endpoint
    print(f"\n3. Testando com parâmetros do endpoint:")
    symbol = 'BTCUSDT'
    timeframe = '1h'
    
    print(f"   Chamando generate_signal('{symbol}', '{timeframe}')...")
    signal = signal_generator.generate_signal(symbol, timeframe)
    
    print(f"\n📊 Resultado:")
    if signal:
        print(f"   ✅ Signal: {signal.signal_type}")
        print(f"   ✅ Confidence: {signal.confidence}")
        print(f"   ✅ Entry Price: {signal.entry_price}")
    else:
        print(f"   ❌ Nenhum sinal gerado")
        
    # Verificar se há diferenças no market_analyzer
    print(f"\n4. Verificando market_analyzer interno:")
    market_analyzer = signal_generator.market_analyzer
    recommendation = market_analyzer.get_trade_recommendation(symbol, timeframe)
    
    print(f"   Market recommendation:")
    if recommendation:
        print(f"      Type: {recommendation.get('recommendation', 'N/A')}")
        print(f"      Confidence: {recommendation.get('confidence', 'N/A')}")
        print(f"      Market Score: {recommendation.get('market_score', 'N/A')}")
    else:
        print(f"      ❌ Nenhuma recomendação")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
