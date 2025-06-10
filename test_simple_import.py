#!/usr/bin/env python3
"""
Teste SIMPLES para verificar se o sistema funciona sem HOLD
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from src.signal_generator import SignalGenerator
    from src.config import Config
    from src.market_data import MarketDataManager
    from src.ai_engine import AITradingEngine
    
    print("✅ Imports funcionando")
    
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    print("✅ Componentes inicializados")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
