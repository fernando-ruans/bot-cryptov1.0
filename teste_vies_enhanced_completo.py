#!/usr/bin/env python3
"""
Teste completo de viés do Enhanced AI Engine
Testa todos os ativos e timeframes para verificar distribuição balanceada de sinais
"""

import os
import sys
import json
from datetime import datetime
from collections import defaultdict, Counter

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.dirname(__file__))

from ai_engine_enhanced import EnhancedAIEngine
from src.config import Config
from src.market_data import MarketDataManager
from src.signal_generator import SignalGenerator

def test_enhanced_ai_bias():
    """Testa viés do Enhanced AI Engine em todos os ativos e timeframes"""
    
    print("🤖 TESTE DE VIÉS - ENHANCED AI ENGINE")
    print("=" * 60)
    
    # Lista de ativos para testar
    assets = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT',
        'SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'LTCUSDT', 'MATICUSDT'
    ]
    
    # Lista de timeframes para testar
    timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']    # Inicializar clientes
    print("📊 Inicializando Enhanced AI Engine...")
    try:
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = EnhancedAIEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        print("✅ Enhanced AI Engine e SignalGenerator inicializados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        return
    
    # Estruturas para armazenar resultados
    results = {
        'timestamp': datetime.now().isoformat(),
        'engine': 'EnhancedAIEngine',
        'total_tests': 0,
        'results_by_asset': {},
        'results_by_timeframe': {},
        'overall_distribution': {'BUY': 0, 'SELL': 0, 'HOLD': 0},
        'bias_analysis': {}
    }
    
    signal_counts = defaultdict(lambda: defaultdict(int))
    timeframe_counts = defaultdict(lambda: defaultdict(int))
    
    total_tests = len(assets) * len(timeframes)
    current_test = 0
    
    print(f"\n🔍 Executando {total_tests} testes ({len(assets)} ativos × {len(timeframes)} timeframes)")
    print("-" * 60)
    
    # Testar cada combinação de ativo e timeframe
    for asset in assets:
        print(f"\n📈 Testando {asset}...")
        results['results_by_asset'][asset] = {}
        
        for timeframe in timeframes:
            current_test += 1
            progress = (current_test / total_tests) * 100
            
            try:
                print(f"  [{current_test:2d}/{total_tests}] {timeframe} ({progress:5.1f}%)", end=" ")
                  # Gerar sinal usando o SignalGenerator com Enhanced AI Engine
                signal = signal_generator.generate_signal(asset, timeframe)
                
                if signal and hasattr(signal, 'signal_type'):
                    signal_type = signal.signal_type.upper()
                    confidence = signal.confidence
                    
                    # Contar sinais
                    signal_counts[asset][signal_type] += 1
                    timeframe_counts[timeframe][signal_type] += 1
                    results['overall_distribution'][signal_type] += 1
                    
                    # Armazenar resultado detalhado
                    results['results_by_asset'][asset][timeframe] = {
                        'signal': signal_type,
                        'confidence': confidence,
                        'entry_price': signal.entry_price,
                        'stop_loss': signal.stop_loss,
                        'take_profit': signal.take_profit
                    }
                    
                    print(f"→ {signal_type} (conf: {confidence:.2f})")
                    
                else:
                    print("→ ❌ Erro no sinal")
                    results['results_by_asset'][asset][timeframe] = {
                        'signal': 'ERROR',
                        'confidence': 0,
                        'error': 'Signal generation failed'
                    }
                    
            except Exception as e:
                print(f"→ ❌ Erro: {str(e)[:50]}...")
                results['results_by_asset'][asset][timeframe] = {
                    'signal': 'ERROR',
                    'confidence': 0,
                    'error': str(e)
                }
    
    # Processar resultados por timeframe
    for timeframe in timeframes:
        total_tf = sum(timeframe_counts[timeframe].values())
        if total_tf > 0:
            results['results_by_timeframe'][timeframe] = {
                'total': total_tf,
                'BUY': timeframe_counts[timeframe]['BUY'],
                'SELL': timeframe_counts[timeframe]['SELL'],
                'HOLD': timeframe_counts[timeframe]['HOLD'],
                'BUY_pct': (timeframe_counts[timeframe]['BUY'] / total_tf) * 100,
                'SELL_pct': (timeframe_counts[timeframe]['SELL'] / total_tf) * 100,
                'HOLD_pct': (timeframe_counts[timeframe]['HOLD'] / total_tf) * 100
            }
    
    results['total_tests'] = current_test
    
    # Análise de viés
    total_signals = sum(results['overall_distribution'].values())
    if total_signals > 0:
        buy_pct = (results['overall_distribution']['BUY'] / total_signals) * 100
        sell_pct = (results['overall_distribution']['SELL'] / total_signals) * 100
        hold_pct = (results['overall_distribution']['HOLD'] / total_signals) * 100
        
        results['bias_analysis'] = {
            'total_signals': total_signals,
            'buy_percentage': buy_pct,
            'sell_percentage': sell_pct,
            'hold_percentage': hold_pct,
            'is_balanced': abs(buy_pct - sell_pct) < 10 and hold_pct > 5,
            'bias_detected': abs(buy_pct - sell_pct) > 20 or hold_pct < 2,
            'recommendations': []
        }
        
        # Gerar recomendações
        if buy_pct > 60:
            results['bias_analysis']['recommendations'].append("Reduzir viés para BUY - muitos sinais de compra")
        if sell_pct > 60:
            results['bias_analysis']['recommendations'].append("Reduzir viés para SELL - muitos sinais de venda")
        if hold_pct < 5:
            results['bias_analysis']['recommendations'].append("Aumentar sinais HOLD - poucos sinais neutros")
        if abs(buy_pct - sell_pct) > 20:
            results['bias_analysis']['recommendations'].append("Balancear melhor BUY vs SELL")
    
    # Salvar resultados em arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"teste_vies_enhanced_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Exibir resultados
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DO TESTE DE VIÉS - ENHANCED AI ENGINE")
    print("=" * 60)
    
    print(f"\n🔢 ESTATÍSTICAS GERAIS:")
    print(f"   • Testes executados: {results['total_tests']}")
    print(f"   • Sinais válidos: {total_signals}")
    print(f"   • Engine utilizado: {results['engine']}")
    
    if total_signals > 0:
        print(f"\n📈 DISTRIBUIÇÃO GERAL:")
        print(f"   • BUY:  {results['overall_distribution']['BUY']:2d} ({buy_pct:5.1f}%)")
        print(f"   • SELL: {results['overall_distribution']['SELL']:2d} ({sell_pct:5.1f}%)")
        print(f"   • HOLD: {results['overall_distribution']['HOLD']:2d} ({hold_pct:5.1f}%)")
        
        print(f"\n⚖️ ANÁLISE DE VIÉS:")
        if results['bias_analysis']['is_balanced']:
            print("   ✅ Sistema BALANCEADO - distribuição adequada")
        elif results['bias_analysis']['bias_detected']:
            print("   ⚠️ VIÉS DETECTADO - distribuição desbalanceada")
        else:
            print("   🔄 Sistema ACEITÁVEL - pequeno desbalanceamento")
        
        if results['bias_analysis']['recommendations']:
            print(f"\n💡 RECOMENDAÇÕES:")
            for i, rec in enumerate(results['bias_analysis']['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n📊 DISTRIBUIÇÃO POR TIMEFRAME:")
        for tf in timeframes:
            if tf in results['results_by_timeframe']:
                tf_data = results['results_by_timeframe'][tf]
                print(f"   {tf:>3}: BUY {tf_data['BUY']:2d} ({tf_data['BUY_pct']:4.0f}%) | "
                      f"SELL {tf_data['SELL']:2d} ({tf_data['SELL_pct']:4.0f}%) | "
                      f"HOLD {tf_data['HOLD']:2d} ({tf_data['HOLD_pct']:4.0f}%)")
    
    print(f"\n💾 Resultados salvos em: {filename}")
    print("\n" + "=" * 60)
    
    return results

if __name__ == "__main__":
    test_enhanced_ai_bias()
