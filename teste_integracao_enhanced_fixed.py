#!/usr/bin/env python3
"""
Teste de integração do Enhanced AI Engine com SignalGenerator
"""

def test_integration():
    try:
        print("🧪 Testando integração Enhanced AI Engine + SignalGenerator...")
        
        # Imports
        from ai_engine_enhanced import EnhancedAIEngine
        from src.config import Config
        from src.market_data import MarketDataManager
        from src.signal_generator import SignalGenerator
        
        print("✅ Imports bem-sucedidos")
        
        # Inicialização
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = EnhancedAIEngine(config)
        
        print("✅ Componentes inicializados")
        
        # Criar SignalGenerator
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        print("✅ SignalGenerator criado com Enhanced AI Engine")
        
        # Teste de geração de sinal
        print("🔍 Testando geração de sinal com BTCUSDT...")
        result = signal_generator.generate_signal('BTCUSDT', '1h')
        
        print(f"✅ Sinal gerado: {result.signal_type}")
        print(f"✅ Confiança: {result.confidence:.3f}")
        print(f"✅ Symbol: {result.symbol}")
        print(f"✅ Timeframe: {result.timeframe}")
        
        print("\n🎉 INTEGRAÇÃO BEM-SUCEDIDA!")
        print("✅ Enhanced AI Engine está funcionando no sistema!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_integration()
