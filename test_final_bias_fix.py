#!/usr/bin/env python3
"""
Teste final: Verificar se o fix de 100% BUY foi corrigido
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.signal_generator import SignalGenerator
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.config import Config

def test_bias_fix():
    print("=== TESTE FINAL: VERIFICAÇÃO DO FIX DE BIAS ===")
    
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT"]
    timeframes = ["1h", "4h"]
    
    results = {
        'BUY': 0,
        'SELL': 0,
        'HOLD': 0
    }
    
    try:
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_gen = SignalGenerator(ai_engine, market_data)
        
        print(f"\n🔍 Testando {len(symbols)} símbolos × {len(timeframes)} timeframes = {len(symbols) * len(timeframes)} combinações\n")
        
        test_count = 0
        
        for symbol in symbols:
            for timeframe in timeframes:
                test_count += 1
                try:
                    print(f"[{test_count:2d}/{len(symbols) * len(timeframes)}] {symbol} {timeframe}... ", end="")
                    
                    # Gerar sinal
                    signal = signal_gen.generate_signal(symbol, timeframe)
                    
                    if signal and 'signal' in signal:
                        signal_type = signal['signal'].upper()
                        confidence = signal.get('confidence', 0)
                        
                        # Contar resultado
                        if signal_type in results:
                            results[signal_type] += 1
                        
                        print(f"{signal_type} ({confidence:.2f})")
                        
                    else:
                        results['HOLD'] += 1
                        print("HOLD (sem sinal)")
                        
                except Exception as e:
                    results['HOLD'] += 1
                    print(f"ERROR: {str(e)[:50]}")
        
        # Análise dos resultados
        total = sum(results.values())
        print(f"\n=== RESULTADOS FINAIS ===")
        print(f"Total de testes: {total}")
        print(f"Sinais BUY:  {results['BUY']:2d} ({results['BUY']/total*100:5.1f}%)")
        print(f"Sinais SELL: {results['SELL']:2d} ({results['SELL']/total*100:5.1f}%)")
        print(f"Sinais HOLD: {results['HOLD']:2d} ({results['HOLD']/total*100:5.1f}%)")
        
        # Verificar se o bias foi corrigido
        actionable_signals = results['BUY'] + results['SELL']
        if actionable_signals > 0:
            buy_percentage = results['BUY'] / actionable_signals * 100
            sell_percentage = results['SELL'] / actionable_signals * 100
            
            print(f"\n📊 ANÁLISE DOS SINAIS ACIONÁVEIS:")
            print(f"BUY:  {buy_percentage:5.1f}%")
            print(f"SELL: {sell_percentage:5.1f}%")
            
            if results['SELL'] > 0:
                print(f"\n✅ BIAS CORRIGIDO!")
                print(f"   ✓ Sistema agora gera sinais SELL: {results['SELL']} de {actionable_signals}")
                print(f"   ✓ Distribuição mais balanceada: {buy_percentage:.1f}% BUY vs {sell_percentage:.1f}% SELL")
            elif results['BUY'] == actionable_signals:
                print(f"\n❌ BIAS AINDA PRESENTE!")
                print(f"   ⚠️  {results['BUY']}/{actionable_signals} sinais são BUY (100%)")
                print(f"   🔧 Necessário investigar mais a fundo")
            else:
                print(f"\n⚠️  RESULTADO INCONCLUSIVO")
        else:
            print(f"\n⚠️  NENHUM SINAL ACIONÁVEL GERADO")
            print(f"   Todos os {total} testes resultaram em HOLD")
            
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bias_fix()
