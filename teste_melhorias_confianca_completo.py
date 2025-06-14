#!/usr/bin/env python3
"""
🧪 TESTE COMPLETO DAS MELHORIAS DE CONFIANÇA
Validação das estratégias implementadas para aumentar a robustez dos sinais
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import logging
import warnings

# Suprimir warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_confidence_improvements():
    """Teste completo das melhorias de confiança"""
    
    print("🎯 TESTE COMPLETO DAS MELHORIAS DE CONFIANÇA")
    print("=" * 70)
    
    try:
        # Importar dependências
        from src.config import Config
        from src.market_data import MarketDataManager
        from ai_engine_enhanced import EnhancedAIEngine
        from melhorias_confianca_sinais import SignalConfidenceEnhancer
        
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = EnhancedAIEngine(config)
        enhancer = SignalConfidenceEnhancer(config)
        
        # Parâmetros do teste
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'SOLUSDT']
        test_timeframes = ['15m', '1h', '4h', '1d']
        
        results = []
        summary_stats = {
            'total_tests': 0,
            'successful_tests': 0,
            'improved_confidence': 0,
            'high_confidence_signals': 0,
            'hold_signals': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'avg_original_confidence': 0,
            'avg_enhanced_confidence': 0,
            'max_improvement': 0,
            'min_improvement': 0
        }
        
        print(f"\n🔍 Testando {len(test_symbols)} ativos × {len(test_timeframes)} timeframes = {len(test_symbols) * len(test_timeframes)} combinações\n")
        
        # Executar testes
        for symbol in test_symbols:
            print(f"📊 Testando {symbol}...")
            
            for timeframe in test_timeframes:
                try:
                    print(f"  ⏰ {timeframe} - ", end="")
                    summary_stats['total_tests'] += 1
                    
                    # Definir timeframe no engine
                    ai_engine.set_timeframe(timeframe)
                    
                    # Obter dados históricos
                    df = market_data.get_historical_data(symbol, timeframe, 200)
                    if df is None or len(df) < 100:
                        print("❌ Dados insuficientes")
                        continue
                    
                    # === TESTE 1: SINAL ORIGINAL ===
                    original_signal = ai_engine.enhanced_predict_signal(df, symbol)
                    
                    original_confidence = original_signal.get('confidence', 0)
                    original_signal_type = original_signal.get('signal_type', 'hold')
                    
                    # === TESTE 2: MELHORIAS MANUAIS ===
                    enhanced_signal = enhancer.enhance_signal_confidence(
                        original_signal, df, symbol, timeframe
                    )
                    
                    enhanced_confidence = enhanced_signal.get('confidence', 0)
                    enhanced_signal_type = enhanced_signal.get('signal_type', 'hold')
                    improvement = enhanced_confidence - original_confidence
                    
                    # === COLETA DE ESTATÍSTICAS ===
                    summary_stats['successful_tests'] += 1
                    summary_stats['avg_original_confidence'] += original_confidence
                    summary_stats['avg_enhanced_confidence'] += enhanced_confidence
                    
                    if improvement > 0:
                        summary_stats['improved_confidence'] += 1
                    
                    if enhanced_confidence >= 0.7:
                        summary_stats['high_confidence_signals'] += 1
                    
                    if enhanced_signal_type == 'hold':
                        summary_stats['hold_signals'] += 1
                    elif enhanced_signal_type == 'buy':
                        summary_stats['buy_signals'] += 1
                    elif enhanced_signal_type == 'sell':
                        summary_stats['sell_signals'] += 1
                    
                    summary_stats['max_improvement'] = max(summary_stats['max_improvement'], improvement)
                    summary_stats['min_improvement'] = min(summary_stats['min_improvement'], improvement)
                    
                    # === ANÁLISE DETALHADA ===
                    enhancement_scores = enhanced_signal.get('enhancement_scores', {})
                    
                    test_result = {
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'original_signal': original_signal_type,
                        'original_confidence': round(original_confidence, 3),
                        'enhanced_signal': enhanced_signal_type,
                        'enhanced_confidence': round(enhanced_confidence, 3),
                        'improvement': round(improvement, 3),
                        'signal_changed': original_signal_type != enhanced_signal_type,
                        'high_confidence': enhanced_confidence >= 0.7,
                        'enhancement_scores': {k: round(v, 3) for k, v in enhancement_scores.items()},
                        'enhancement_summary': enhanced_signal.get('enhancement_summary', ''),
                        'confidence_enhanced_flag': enhanced_signal.get('confidence_enhanced', False)
                    }
                    
                    results.append(test_result)
                    
                    # Output do resultado
                    status_emoji = "✅" if improvement > 0 else "🔄" if improvement == 0 else "⚠️"
                    confidence_emoji = "🎯" if enhanced_confidence >= 0.7 else "📊" if enhanced_confidence >= 0.5 else "⚡"
                    
                    print(f"{status_emoji} {enhanced_signal_type.upper()} {confidence_emoji} {enhanced_confidence:.3f} ({improvement:+.3f})")
                    
                except Exception as e:
                    print(f"❌ Erro: {str(e)[:50]}...")
                    logger.error(f"Erro em {symbol} {timeframe}: {e}")
        
        # === CÁLCULO DE ESTATÍSTICAS FINAIS ===
        if summary_stats['successful_tests'] > 0:
            summary_stats['avg_original_confidence'] /= summary_stats['successful_tests']
            summary_stats['avg_enhanced_confidence'] /= summary_stats['successful_tests']
        
        # === RELATÓRIO FINAL ===
        print(f"\n{'='*70}")
        print("📊 RELATÓRIO FINAL DAS MELHORIAS")
        print(f"{'='*70}")
        
        total = summary_stats['successful_tests']
        if total > 0:
            print(f"\n🧪 ESTATÍSTICAS GERAIS:")
            print(f"   Total de testes: {summary_stats['total_tests']}")
            print(f"   Testes bem-sucedidos: {total}")
            print(f"   Taxa de sucesso: {total/summary_stats['total_tests']*100:.1f}%")
            
            print(f"\n📈 MELHORIAS DE CONFIANÇA:")
            print(f"   Sinais melhorados: {summary_stats['improved_confidence']}/{total} ({summary_stats['improved_confidence']/total*100:.1f}%)")
            print(f"   Confiança média original: {summary_stats['avg_original_confidence']:.3f}")
            print(f"   Confiança média melhorada: {summary_stats['avg_enhanced_confidence']:.3f}")
            print(f"   Melhoria média: {summary_stats['avg_enhanced_confidence'] - summary_stats['avg_original_confidence']:+.3f}")
            print(f"   Maior melhoria: {summary_stats['max_improvement']:+.3f}")
            print(f"   Menor melhoria: {summary_stats['min_improvement']:+.3f}")
            
            print(f"\n🎯 QUALIDADE DOS SINAIS:")
            print(f"   Alta confiança (≥70%): {summary_stats['high_confidence_signals']}/{total} ({summary_stats['high_confidence_signals']/total*100:.1f}%)")
            
            print(f"\n📊 DISTRIBUIÇÃO DE SINAIS:")
            print(f"   BUY: {summary_stats['buy_signals']}/{total} ({summary_stats['buy_signals']/total*100:.1f}%)")
            print(f"   SELL: {summary_stats['sell_signals']}/{total} ({summary_stats['sell_signals']/total*100:.1f}%)")
            print(f"   HOLD: {summary_stats['hold_signals']}/{total} ({summary_stats['hold_signals']/total*100:.1f}%)")
            
            # === ANÁLISE POR TIMEFRAME ===
            print(f"\n⏰ ANÁLISE POR TIMEFRAME:")
            timeframe_stats = {}
            for result in results:
                tf = result['timeframe']
                if tf not in timeframe_stats:
                    timeframe_stats[tf] = {'count': 0, 'improvements': 0, 'high_conf': 0, 'avg_conf': 0}
                
                timeframe_stats[tf]['count'] += 1
                timeframe_stats[tf]['avg_conf'] += result['enhanced_confidence']
                
                if result['improvement'] > 0:
                    timeframe_stats[tf]['improvements'] += 1
                if result['enhanced_confidence'] >= 0.7:
                    timeframe_stats[tf]['high_conf'] += 1
            
            for tf, stats in timeframe_stats.items():
                if stats['count'] > 0:
                    avg_conf = stats['avg_conf'] / stats['count']
                    imp_rate = stats['improvements'] / stats['count'] * 100
                    high_conf_rate = stats['high_conf'] / stats['count'] * 100
                    print(f"   {tf:>3}: Conf média {avg_conf:.3f} | Melhorias {imp_rate:.1f}% | Alta conf {high_conf_rate:.1f}%")
            
            # === ANÁLISE POR ATIVO ===
            print(f"\n📈 ANÁLISE POR ATIVO:")
            symbol_stats = {}
            for result in results:
                sym = result['symbol']
                if sym not in symbol_stats:
                    symbol_stats[sym] = {'count': 0, 'improvements': 0, 'high_conf': 0, 'avg_conf': 0}
                
                symbol_stats[sym]['count'] += 1
                symbol_stats[sym]['avg_conf'] += result['enhanced_confidence']
                
                if result['improvement'] > 0:
                    symbol_stats[sym]['improvements'] += 1
                if result['enhanced_confidence'] >= 0.7:
                    symbol_stats[sym]['high_conf'] += 1
            
            for sym, stats in symbol_stats.items():
                if stats['count'] > 0:
                    avg_conf = stats['avg_conf'] / stats['count']
                    imp_rate = stats['improvements'] / stats['count'] * 100
                    high_conf_rate = stats['high_conf'] / stats['count'] * 100
                    print(f"   {sym:>8}: Conf média {avg_conf:.3f} | Melhorias {imp_rate:.1f}% | Alta conf {high_conf_rate:.1f}%")
            
        else:
            print("❌ Nenhum teste foi bem-sucedido")
        
        # === SALVAR RESULTADOS ===
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Resultados detalhados
        results_filename = f"teste_melhorias_confianca_completo_{timestamp}.json"
        with open(results_filename, 'w') as f:
            json.dump({
                'summary_stats': summary_stats,
                'detailed_results': results,
                'test_info': {
                    'symbols_tested': test_symbols,
                    'timeframes_tested': test_timeframes,
                    'timestamp': timestamp,
                    'total_combinations': len(test_symbols) * len(test_timeframes)
                }
            }, f, indent=2, default=str)
        
        print(f"\n💾 Resultados salvos em: {results_filename}")
        
        # === RECOMENDAÇÕES ===
        print(f"\n💡 RECOMENDAÇÕES:")
        
        if summary_stats['successful_tests'] > 0:
            improvement_rate = summary_stats['improved_confidence'] / summary_stats['successful_tests']
            high_conf_rate = summary_stats['high_confidence_signals'] / summary_stats['successful_tests']
            hold_rate = summary_stats['hold_signals'] / summary_stats['successful_tests']
            
            if improvement_rate > 0.7:
                print("   ✅ Sistema de melhorias funcionando bem")
            elif improvement_rate > 0.5:
                print("   🔄 Sistema de melhorias moderadamente eficaz")
            else:
                print("   ⚠️ Sistema de melhorias precisa de ajustes")
            
            if high_conf_rate > 0.5:
                print("   ✅ Boa taxa de sinais de alta confiança")
            else:
                print("   📊 Considerar ajustar thresholds de confiança")
            
            if hold_rate > 0.15:
                print("   ✅ Boa distribuição com sinais HOLD")
            elif hold_rate > 0.05:
                print("   🔄 Distribuição moderada de sinais HOLD")
            else:
                print("   ⚠️ Muito poucos sinais HOLD - sistema pode estar forçando decisões")
            
            avg_improvement = summary_stats['avg_enhanced_confidence'] - summary_stats['avg_original_confidence']
            if avg_improvement > 0.1:
                print("   🎯 Melhorias de confiança significativas")
            elif avg_improvement > 0.05:
                print("   📈 Melhorias de confiança moderadas")
            else:
                print("   📊 Melhorias de confiança mínimas")
        
        print(f"\n{'='*70}")
        print("🎯 TESTE COMPLETO FINALIZADO")
        print(f"{'='*70}")
        
    except Exception as e:
        print(f"❌ Erro geral no teste: {e}")
        logger.error(f"Erro geral: {e}")

if __name__ == "__main__":
    test_confidence_improvements()
