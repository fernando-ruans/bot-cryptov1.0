#!/usr/bin/env python3
"""
Teste múltiplos sinais para verificar distribuição de confiança
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.signal_generator import SignalGenerator
from src.market_data import MarketDataManager
from src.config import Config
import time

def test_multiple_signals():
    """Testa geração de múltiplos sinais"""
    print("=== TESTE: Múltiplos Sinais ===")
    
    try:
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        signal_gen = SignalGenerator(market_data, config)
        
        print(f"✓ Confiança mínima configurada: {config.SIGNAL_CONFIG['min_confidence']}")
        
        symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        timeframes = ['1h', '4h']
        
        valid_signals = 0
        total_tests = 0
        
        for symbol in symbols:
            for timeframe in timeframes:
                print(f"\n--- Testando {symbol} {timeframe} ---")
                
                # Gerar sinal
                signal = signal_gen.generate_signal(symbol, timeframe)
                total_tests += 1
                
                if signal and signal.get('signal') != 'hold':
                    confidence = signal.get('confidence', 0)
                    signal_type = signal.get('signal', 'unknown')
                    print(f"✓ Sinal gerado: {signal_type} com {confidence:.2f} confiança")
                    
                    if confidence >= config.SIGNAL_CONFIG['min_confidence']:
                        valid_signals += 1
                        print(f"  ✅ VÁLIDO: Confiança {confidence:.2f} >= {config.SIGNAL_CONFIG['min_confidence']}")
                    else:
                        print(f"  ❌ REJEITADO: Confiança {confidence:.2f} < {config.SIGNAL_CONFIG['min_confidence']}")
                else:
                    print("• Nenhum sinal forte detectado (hold)")
                
                # Pequeno delay para variação nos dados
                time.sleep(0.1)
        
        print(f"\n=== RESUMO ===")
        print(f"Total de testes: {total_tests}")
        print(f"Sinais válidos: {valid_signals}")
        print(f"Taxa de sucesso: {(valid_signals/total_tests)*100:.1f}%")
        
        if valid_signals > 0:
            print("✅ Sistema está gerando sinais válidos!")
        else:
            print("⚠️ Nenhum sinal atingiu o threshold mínimo")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multiple_signals()
