#!/usr/bin/env python3
"""
Teste em lote para verificar a distribuição dos sinais após correção do viés
"""

import sys
import os
import json
import time
from datetime import datetime
from collections import Counter

# Adicionar diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar classes necessárias
from src.signal_generator import SignalGenerator
from src.config import Config

def test_signal_distribution():
    """Testa a distribuição de sinais em lote"""
    print("🎯 TESTE DE DISTRIBUIÇÃO DE SINAIS EM LOTE")
    print("=" * 50)
    
    try:
        # Configuração
        config = Config()
        generator = SignalGenerator(config)
        
        # Lista de símbolos para testar
        symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT",
            "SOLUSDT", "DOTUSDT", "LINKUSDT", "LTCUSDT", "BCHUSDT",
            "AVAXUSDT", "MATICUSDT", "UNIUSDT", "XLMUSDT", "ATOMUSDT"
        ]
        
        # Timeframes para testar
        timeframes = ["1h", "4h", "1d"]
        
        all_signals = []
        signal_count = Counter()
        
        print(f"📊 Testando {len(symbols)} símbolos em {len(timeframes)} timeframes...")
        print()
        
        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    print(f"🔍 Testando {symbol} {timeframe}...", end=" ")
                    
                    # Gerar sinal
                    result = generator.generate_signal(symbol, timeframe)
                    signal = result.get('action', 'none').lower()
                    confidence = result.get('confidence', 0)
                    
                    all_signals.append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'signal': signal,
                        'confidence': confidence,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    signal_count[signal] += 1
                    
                    # Emoji para o sinal
                    emoji = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}.get(signal, "⚪")
                    print(f"{emoji} {signal.upper()} ({confidence:.2f})")
                    
                    # Pequena pausa para não sobrecarregar
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"❌ Erro: {str(e)[:50]}...")
                    continue
        
        # Estatísticas
        total_signals = len(all_signals)
        print()
        print("📈 RESULTADOS DA DISTRIBUIÇÃO")
        print("=" * 40)
        print(f"Total de sinais testados: {total_signals}")
        print()
        
        for signal_type, count in signal_count.most_common():
            percentage = (count / total_signals) * 100 if total_signals > 0 else 0
            emoji = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}.get(signal_type, "⚪")
            print(f"{emoji} {signal_type.upper()}: {count} ({percentage:.1f}%)")
        
        # Análise de balanceamento
        print()
        print("🎯 ANÁLISE DE BALANCEAMENTO")
        print("=" * 40)
        
        buy_pct = (signal_count.get('buy', 0) / total_signals) * 100 if total_signals > 0 else 0
        sell_pct = (signal_count.get('sell', 0) / total_signals) * 100 if total_signals > 0 else 0
        hold_pct = (signal_count.get('hold', 0) / total_signals) * 100 if total_signals > 0 else 0
        
        if buy_pct > 60:
            print("⚠️  VIÉS PARA BUY DETECTADO!")
        elif sell_pct > 60:
            print("⚠️  VIÉS PARA SELL DETECTADO!")
        elif hold_pct > 80:
            print("⚠️  MUITOS SINAIS HOLD - SISTEMA MUITO CONSERVADOR!")
        else:
            print("✅ DISTRIBUIÇÃO BALANCEADA!")
        
        # Verificar se há variação nos sinais
        unique_signals = len(signal_count)
        if unique_signals >= 2:
            print("✅ VARIEDADE DE SINAIS: Sistema gerando diferentes tipos de sinal")
        else:
            print("❌ FALTA DE VARIEDADE: Sistema gerando apenas um tipo de sinal")
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teste_distribuicao_sinais_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'total_signals': total_signals,
                'distribution': dict(signal_count),
                'percentages': {
                    'buy': buy_pct,
                    'sell': sell_pct,
                    'hold': hold_pct
                },
                'signals': all_signals
            }, f, indent=2)
        
        print(f"💾 Resultados salvos em: {filename}")
        
        # Status final
        print()
        print("🏁 STATUS FINAL")
        print("=" * 30)
        
        if unique_signals >= 2 and not (buy_pct > 70 or sell_pct > 70 or hold_pct > 85):
            print("🎉 CORREÇÃO DO VIÉS BEM-SUCEDIDA!")
            print("✅ Sistema gerando sinais balanceados")
            return True
        else:
            print("⚠️  AINDA HÁ PROBLEMAS DE VIÉS")
            print("❌ Sistema precisa de mais ajustes")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_signal_distribution()
    
    if success:
        print("\n🚀 SISTEMA PRONTO PARA PRODUÇÃO!")
    else:
        print("\n🔧 SISTEMA PRECISA DE MAIS CORREÇÕES")
