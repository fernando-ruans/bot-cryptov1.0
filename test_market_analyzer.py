#!/usr/bin/env python3
"""
Teste direto do market analyzer
"""

import sys
import os
sys.path.append('src')

from config import Config
from market_data import MarketDataManager
from ai_engine import AITradingEngine
from market_analyzer import MarketAnalyzer

print("=== TESTE MARKET ANALYZER ===")

try:
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    market_analyzer = MarketAnalyzer(config, market_data, ai_engine)
    
    print("✓ Componentes inicializados")
    
    print("\n1. Testando get_trade_recommendation...")
    result = market_analyzer.get_trade_recommendation('BTCUSDT', '1h')
    
    print(f"Resultado completo: {result}")
    
    if result:
        print(f"  - Recommendation: {result.get('recommendation', 'N/A')}")
        print(f"  - Confidence: {result.get('confidence', 'N/A')}")
        print(f"  - Market Score: {result.get('market_score', 'N/A')}")
        print(f"  - Reasons: {result.get('reasons', [])[:3]}...")
    else:
        print("❌ Nenhuma recomendação retornada!")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIM DO TESTE ===")
