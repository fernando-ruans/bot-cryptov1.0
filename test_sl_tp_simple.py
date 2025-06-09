#!/usr/bin/env python3
"""
Teste simples para verificar valores de SL e TP
"""

import sys
sys.path.append('.')

from src.signal_generator import SignalGenerator
from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine

def test_sl_tp():
    print("🧪 Testando valores de Stop Loss e Take Profit...")
    
    try:
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_gen = SignalGenerator(ai_engine, market_data)
        
        # Gerar sinal
        signal = signal_gen.generate_signal('BTCUSDT', '1h')
        
        if signal:
            print(f"\n✅ Sinal gerado:")
            print(f"   Símbolo: {signal.symbol}")
            print(f"   Tipo: {signal.signal_type}")
            print(f"   Entry Price: ${signal.entry_price:.2f}")
            print(f"   Stop Loss: ${signal.stop_loss:.2f}")
            print(f"   Take Profit: ${signal.take_profit:.2f}")
            print(f"   Timeframe: {signal.timeframe}")
            
            # Calcular distâncias
            sl_distance = abs(signal.entry_price - signal.stop_loss)
            tp_distance = abs(signal.take_profit - signal.entry_price)
            
            sl_percent = (sl_distance / signal.entry_price) * 100
            tp_percent = (tp_distance / signal.entry_price) * 100
            
            print(f"\n📊 Análise das distâncias:")
            print(f"   SL Distance: ${sl_distance:.2f} ({sl_percent:.3f}%)")
            print(f"   TP Distance: ${tp_distance:.2f} ({tp_percent:.3f}%)")
            print(f"   Risk/Reward: 1:{tp_percent/sl_percent:.2f}")
            
            # Verificar se está dentro dos parâmetros esperados para 1h
            expected_sl = 1.20  # 1.20% para 1h
            expected_tp = 1.80  # 1.80% para 1h
            
            print(f"\n🎯 Comparação com valores esperados (1h):")
            print(f"   SL Esperado: {expected_sl}% | Atual: {sl_percent:.3f}%")
            print(f"   TP Esperado: {expected_tp}% | Atual: {tp_percent:.3f}%")
            
            if abs(sl_percent - expected_sl) < 0.05:  # Tolerância de 0.05%
                print("   ✅ Stop Loss dentro do esperado")
            else:
                print("   ❌ Stop Loss fora do esperado")
                
            if abs(tp_percent - expected_tp) < 0.05:  # Tolerância de 0.05%
                print("   ✅ Take Profit dentro do esperado")
            else:
                print("   ❌ Take Profit fora do esperado")
                
        else:
            print("❌ Nenhum sinal foi gerado")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sl_tp()