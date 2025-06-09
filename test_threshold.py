#!/usr/bin/env python3
"""
Teste threshold de confiança 50%
"""

def test_confidence_threshold():
    """Teste do threshold de confiança"""
    print("=== TESTE: Threshold de Confiança 50% ===")
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from src.signal_generator import SignalGenerator
        
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        signal_gen = SignalGenerator(market_data, config)
        
        print(f"✓ Confiança mínima configurada: {config.SIGNAL_CONFIG['min_confidence']}")
        
        valid_signals = 0
        total_tests = 5
        
        for i in range(total_tests):
            print(f"\n--- Teste {i+1}/{total_tests} para BTCUSDT 1h ---")
            
            # Gerar sinal completo através da API principal
            signal = signal_gen.generate_signal('BTCUSDT', '1h')
            
            if signal and signal.get('signal') != 'hold':
                confidence = signal.get('confidence', 0)
                signal_type = signal.get('signal', 'unknown')
                
                print(f"  Sinal: {signal_type}")
                print(f"  Confiança: {confidence:.2f}")
                
                if confidence >= config.SIGNAL_CONFIG['min_confidence']:
                    valid_signals += 1
                    print(f"  ✅ VÁLIDO (>= {config.SIGNAL_CONFIG['min_confidence']})")
                else:
                    print(f"  ❌ REJEITADO (< {config.SIGNAL_CONFIG['min_confidence']})")
            else:
                print("  • Hold/Nenhum sinal")
                
            # Pequeno delay para variação
            import time
            time.sleep(0.1)
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Sinais válidos: {valid_signals}/{total_tests}")
        print(f"Taxa de sucesso: {(valid_signals/total_tests)*100:.1f}%")
        
        if valid_signals >= 2:  # Pelo menos 40% de sucesso
            print("✅ Threshold de 50% é viável!")
            return True
        else:
            print("⚠️ Threshold de 50% pode ser muito alto")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_confidence_threshold()
