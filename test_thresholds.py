#!/usr/bin/env python3
"""
Teste de diferentes thresholds de confiança
"""

def test_thresholds():
    """Testar diferentes thresholds"""
    print("=== TESTE: Diferentes Thresholds ===")
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from src.ai_engine import AITradingEngine
        from src.signal_generator import SignalGenerator
        
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_gen = SignalGenerator(ai_engine, market_data)
        
        # Obter dados
        df = market_data.get_historical_data('BTCUSDT', '1h', 500)
        df = signal_gen.technical_indicators.calculate_all_indicators(df)
        
        # Testar análise técnica direta
        print("\n--- Análise Técnica Direta ---")
        tech_result = signal_gen._analyze_technical_indicators(df)
        print(f"Sinal técnico: {tech_result['signal']}")
        print(f"Confiança técnica: {tech_result['confidence']:.3f}")
        
        # Testar diferentes thresholds
        thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]
        
        for threshold in thresholds:
            print(f"\n--- Threshold: {threshold:.1f} ---")
            config.SIGNAL_CONFIG['min_confidence'] = threshold
            
            signal = signal_gen.generate_signal('BTCUSDT', '1h')
            
            if signal:
                print(f"✅ PASSOU: {signal.signal_type} com {signal.confidence:.3f}")
            else:
                print(f"❌ REJEITADO: Abaixo de {threshold:.1f}")
        
        # Restaurar threshold original
        config.SIGNAL_CONFIG['min_confidence'] = 0.5
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_thresholds()
