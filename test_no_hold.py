#!/usr/bin/env python3
"""
Teste para verificar se o sistema está gerando apenas BUY/SELL (sem HOLD)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from signal_generator import TradingSignalGenerator
import logging

# Configurar log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_no_hold_signals():
    """Testa se o sistema gera apenas BUY ou SELL, nunca HOLD"""
    print("🧪 Testando se sistema gera apenas BUY/SELL (sem HOLD)...")
    
    # Configuração para forçar sinais
    config = {
        'thresholds': {
            'min_confidence': 0.01,  # Mínimo muito baixo
            'strong_signal': 0.6,
            'medium_signal': 0.4,
            'weak_signal': 0.2
        },
        'indicators': {
            'rsi_period': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'bb_period': 20,
            'bb_std': 2
        },
        'ai_engine': {
            'enabled': True,
            'fallback_enabled': True
        },
        'risk_management': {
            'cooldown_minutes': 0  # Sem cooldown para teste
        }
    }
    
    generator = TradingSignalGenerator(config)
    
    # Dados fictícios para teste
    test_data = {
        'symbol': 'BTCUSDT',
        'close': [50000, 50100, 50200, 50150, 50300, 50250, 50400, 50350, 50500, 50450],
        'volume': [1000, 1100, 1050, 1200, 1150, 1300, 1250, 1400, 1350, 1500],
        'high': [50100, 50200, 50300, 50250, 50400, 50350, 50500, 50450, 50600, 50550],
        'low': [49900, 50000, 50100, 50050, 50200, 50150, 50300, 50250, 50400, 50350],
        'timestamp': list(range(10))
    }
    
    signals_generated = []
    
    # Gerar 20 sinais para teste
    for i in range(20):
        try:
            # Simular pequenas variações nos dados
            variation = (i % 3 - 1) * 100  # -100, 0, ou +100
            test_data['close'][-1] = 50450 + variation
            test_data['high'][-1] = 50550 + variation  
            test_data['low'][-1] = 50350 + variation
            
            signal = generator.generate_signal(test_data)
            
            if signal and 'signal' in signal:
                signal_type = signal['signal']
                confidence = signal.get('confidence', 0)
                signals_generated.append(signal_type)
                print(f"Teste {i+1:2d}: {signal_type.upper():4s} (confiança: {confidence:.3f})")
            else:
                print(f"Teste {i+1:2d}: ERRO - Sinal None ou inválido")
                signals_generated.append('ERROR')
                
        except Exception as e:
            print(f"Teste {i+1:2d}: ERRO - {e}")
            signals_generated.append('ERROR')
    
    # Análise dos resultados
    print("\n" + "="*50)
    print("📊 RESULTADOS:")
    
    buy_count = signals_generated.count('buy')
    sell_count = signals_generated.count('sell') 
    hold_count = signals_generated.count('hold')
    error_count = signals_generated.count('ERROR')
    
    print(f"BUY:   {buy_count:2d} ({buy_count/len(signals_generated)*100:.1f}%)")
    print(f"SELL:  {sell_count:2d} ({sell_count/len(signals_generated)*100:.1f}%)")
    print(f"HOLD:  {hold_count:2d} ({hold_count/len(signals_generated)*100:.1f}%)")
    print(f"ERRO:  {error_count:2d} ({error_count/len(signals_generated)*100:.1f}%)")
    
    # Verificar se objetivo foi alcançado
    success = hold_count == 0 and error_count == 0
    
    if success:
        print("\n✅ SUCESSO: Sistema gera apenas BUY/SELL!")
    else:
        print("\n❌ FALHA: Sistema ainda gera HOLD ou erros!")
        
    return success

if __name__ == "__main__":
    test_no_hold_signals()
