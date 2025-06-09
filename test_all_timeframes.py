#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai_engine import AITradingEngine
from src.market_data import MarketDataManager
from src.config import Config
from src.signal_generator import SignalGenerator

def test_all_timeframes():
    """Testar stop loss e take profit para todos os timeframes"""
    
    # Valores esperados conforme nova tabela de parâmetros otimizados
    expected_values = {
        '1m': {'sl': 0.10, 'tp': 0.15},
        '5m': {'sl': 0.30, 'tp': 0.50},
        '15m': {'sl': 0.60, 'tp': 0.80},
        '30m': {'sl': 0.80, 'tp': 1.20},
        '1h': {'sl': 1.20, 'tp': 1.80},
        '2h': {'sl': 1.80, 'tp': 2.70},
        '4h': {'sl': 2.50, 'tp': 3.50}
    }
    
    try:
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        print("🔍 Testando Stop Loss e Take Profit para todos os timeframes...\n")
        
        all_correct = True
        
        for timeframe, expected in expected_values.items():
            try:
                # Gerar sinal para o timeframe
                signal = signal_generator.generate_signal('BTCUSDT', timeframe)
                
                if signal and signal.signal_type != 'hold':
                    entry_price = signal.entry_price
                    stop_loss = signal.stop_loss
                    take_profit = signal.take_profit
                    
                    # Calcular distâncias percentuais
                    if signal.signal_type == 'buy':
                        sl_distance_pct = ((entry_price - stop_loss) / entry_price) * 100
                        tp_distance_pct = ((take_profit - entry_price) / entry_price) * 100
                    else:  # sell
                        sl_distance_pct = ((stop_loss - entry_price) / entry_price) * 100
                        tp_distance_pct = ((entry_price - take_profit) / entry_price) * 100
                    
                    # Verificar se estão dentro da tolerância (±0.01%)
                    sl_correct = abs(sl_distance_pct - expected['sl']) <= 0.01
                    tp_correct = abs(tp_distance_pct - expected['tp']) <= 0.01
                    
                    status_sl = "✅" if sl_correct else "❌"
                    status_tp = "✅" if tp_correct else "❌"
                    
                    print(f"📊 {timeframe.upper()}:")
                    print(f"   Tipo: {signal.signal_type}")
                    print(f"   Entry: ${entry_price:.2f}")
                    print(f"   {status_sl} SL: {sl_distance_pct:.3f}% (esperado: {expected['sl']:.2f}%)")
                    print(f"   {status_tp} TP: {tp_distance_pct:.3f}% (esperado: {expected['tp']:.2f}%)")
                    print(f"   Risk/Reward: 1:{tp_distance_pct/sl_distance_pct:.2f}")
                    print()
                    
                    if not (sl_correct and tp_correct):
                        all_correct = False
                        
                else:
                    print(f"⚠️  {timeframe.upper()}: Sinal HOLD ou erro na geração")
                    print()
                    
            except Exception as e:
                print(f"❌ Erro ao testar {timeframe}: {e}")
                print()
                all_correct = False
        
        if all_correct:
            print("🎉 TODOS OS TIMEFRAMES ESTÃO CORRETOS!")
        else:
            print("⚠️  Alguns timeframes precisam de ajuste.")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    test_all_timeframes()