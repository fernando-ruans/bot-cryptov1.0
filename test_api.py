#!/usr/bin/env python3
"""
Teste da API principal do gerador de sinais
"""

def test_signal_api():
    """Teste da API principal"""
    print("=== TESTE: API Principal de Sinais ===")
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from src.signal_generator import SignalGenerator
        
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        signal_gen = SignalGenerator(market_data, config)
        
        print(f"✓ Confiança mínima: {config.SIGNAL_CONFIG['min_confidence']}")
        
        # Testar geração via API principal
        print("\n--- Testando API Principal ---")
        signal = signal_gen.generate_signal('BTCUSDT', '1h')
        
        if signal:
            print(f"Resultado da API:")
            print(f"  - Sinal: {signal.get('signal', 'unknown')}")
            print(f"  - Confiança: {signal.get('confidence', 0):.2f}")
            print(f"  - Timestamp: {signal.get('timestamp', 'N/A')}")
            print(f"  - Razões: {signal.get('reasons', [])}")
            
            if signal.get('signal') == 'hold':
                print("✅ API corretamente rejeitou sinais abaixo do threshold")
            else:
                conf = signal.get('confidence', 0)
                if conf >= config.SIGNAL_CONFIG['min_confidence']:
                    print("✅ API aprovou sinal com confiança suficiente")
                else:
                    print("❌ API aprovou sinal abaixo do threshold!")
        else:
            print("• API retornou None (nenhum sinal)")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_signal_api()
