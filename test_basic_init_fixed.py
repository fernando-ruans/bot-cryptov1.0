#!/usr/bin/env python3
"""
Teste muito básico - apenas inicialização
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("=== TESTE BÁSICO DE INICIALIZAÇÃO ===")
    
    print("1. Importando Config...")
    from src.config import Config
    config = Config()
    print("✅ Config OK")
    
    print("2. Importando MarketDataManager...")
    from src.market_data import MarketDataManager
    market_data = MarketDataManager(config)
    print("✅ MarketDataManager OK")
    
    print("3. Importando AITradingEngine...")
    from src.ai_engine import AITradingEngine
    ai_engine = AITradingEngine(config)
    print("✅ AITradingEngine OK")
    
    print("4. Importando MarketAnalyzer...")
    from src.market_analyzer import MarketAnalyzer
    print("✅ Importação MarketAnalyzer OK")
    
    print("5. Criando instância MarketAnalyzer...")
    analyzer = MarketAnalyzer(config, market_data, ai_engine)
    print("✅ MarketAnalyzer criado OK")
    
    print("6. Teste simples de método...")
    # Testar o método principal
    recommendation = analyzer.get_trade_recommendation('BTCUSDT', '1h')
    print(f"✅ get_trade_recommendation executado: {type(recommendation)}")
    if recommendation:
        print(f"   Recommendation: {recommendation.get('recommendation', 'N/A')}")
        print(f"   Confidence: {recommendation.get('confidence', 'N/A')}")
        print(f"   Market Score: {recommendation.get('market_score', 'N/A')}")
    else:
        print("   ⚠️ Nenhuma recomendação retornada")
    
    print("\n🎉 TODOS OS TESTES BÁSICOS PASSARAM!")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
