#!/usr/bin/env python3
"""
Teste específico do signal_generator
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("=== TESTE SIGNAL GENERATOR ===")
    
    from src.config import Config
    from src.market_data import MarketDataManager
    from src.ai_engine import AITradingEngine
    from src.market_analyzer import MarketAnalyzer
    from src.signal_generator import SignalGenerator
    
    # Configurar componentes
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    market_analyzer = MarketAnalyzer(config, market_data, ai_engine)
    
    print("✅ Componentes inicializados")
      # Criar signal generator (ele cria o market_analyzer internamente)
    signal_generator = SignalGenerator(ai_engine, market_data)
    print("✅ SignalGenerator criado")
    
    # Testar geração de sinal
    symbol = 'BTCUSDT'
    print(f"\n🔍 Testando signal_generator.generate_signal('{symbol}')...")
    
    signal = signal_generator.generate_signal(symbol)
    
    print(f"\n📊 Resultado:")
    print(f"   Type: {type(signal)}")
    
    if signal:
        print(f"   Signal: {signal.signal_type}")
        print(f"   Confidence: {signal.confidence}")
        print(f"   Entry Price: {signal.entry_price}")
        print(f"   Stop Loss: {signal.stop_loss}")
        print(f"   Take Profit: {signal.take_profit}")
    else:
        print(f"   ❌ Nenhum sinal gerado")
    
    print("\n✅ TESTE CONCLUÍDO!")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
