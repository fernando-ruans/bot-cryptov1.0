#!/usr/bin/env python3
"""
✅ TESTE FINAL SIMPLIFICADO - AI ENGINE V3
Validação direta do AI Engine V3 Otimizado
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ai_engine_direct():
    """Teste direto do AI Engine V3"""
    
    print("🚀 TESTE DIRETO DO AI ENGINE V3 OTIMIZADO")
    print("=" * 60)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from ai_engine_v3_otimizado import OptimizedAIEngineV3
        
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = OptimizedAIEngineV3(config)
        
        print("✅ Componentes inicializados")
        
        # Testar com múltiplos símbolos e timeframes
        test_cases = [
            ('BTCUSDT', '1m'),
            ('BTCUSDT', '5m'),
            ('ETHUSDT', '1m'),
            ('ETHUSDT', '5m'),
            ('BNBUSDT', '1m'),
            ('BNBUSDT', '5m'),
        ]
        
        results = []
        
        for symbol, timeframe in test_cases:
            print(f"\n📊 Testando {symbol} {timeframe}...")
            
            try:
                # Obter dados
                df = market_data.get_historical_data(symbol, timeframe, 500)
                if df is None or len(df) < 200:
                    print(f"   ❌ Dados insuficientes")
                    continue
                
                # Fazer predição direta
                start_time = time.time()
                result = ai_engine.optimized_predict_signal(df, f"{symbol}_{timeframe}")
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                signal_type = result.get('signal_type', 'UNKNOWN')
                confidence = result.get('confidence', 0)
                model_accuracy = result.get('model_accuracy', 0)
                confluence = result.get('confluence', 0)
                
                test_result = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal_type': signal_type,
                    'confidence': confidence,
                    'model_accuracy': model_accuracy,
                    'confluence': confluence,
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                }
                
                results.append(test_result)
                
                print(f"   🎯 Sinal: {signal_type}")
                print(f"   📈 Confiança: {confidence:.3f}")
                print(f"   🎯 Acurácia: {model_accuracy:.3f}")
                print(f"   🤝 Confluence: {confluence:.3f}")
                print(f"   ⏱️ Tempo: {execution_time:.2f}s")
                
                # Avaliar qualidade do sinal
                if signal_type != 'HOLD':
                    if confidence >= 0.70 and model_accuracy >= 0.50:
                        quality = "🟢 ALTA"
                    elif confidence >= 0.55 and model_accuracy >= 0.40:
                        quality = "🟡 MÉDIA"
                    elif confidence >= 0.45:
                        quality = "🟠 BAIXA"
                    else:
                        quality = "🔴 MUITO BAIXA"
                    
                    print(f"   📊 Qualidade: {quality}")
                else:
                    print(f"   📊 Status: HOLD (sem trade)")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                results.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'error': str(e),
                    'success': False
                })
        
        # Análise dos resultados
        print(f"\n📊 ANÁLISE DOS RESULTADOS")
        print("=" * 60)
        
        successful_tests = [r for r in results if r.get('success', False)]
        total_tests = len(results)
        
        print(f"📈 Testes realizados: {total_tests}")
        print(f"✅ Testes bem-sucedidos: {len(successful_tests)}")
        print(f"📊 Taxa de sucesso: {len(successful_tests)/max(total_tests,1)*100:.1f}%")
        
        if successful_tests:
            # Estatísticas de qualidade
            avg_confidence = sum(r['confidence'] for r in successful_tests) / len(successful_tests)
            avg_accuracy = sum(r['model_accuracy'] for r in successful_tests) / len(successful_tests)
            avg_time = sum(r['execution_time'] for r in successful_tests) / len(successful_tests)
            
            print(f"\n📈 Confiança média: {avg_confidence:.3f}")
            print(f"🎯 Acurácia média: {avg_accuracy:.3f}")
            print(f"⏱️ Tempo médio: {avg_time:.2f}s")
            
            # Distribuição de sinais
            signal_counts = {}
            for r in successful_tests:
                signal = r['signal_type']
                signal_counts[signal] = signal_counts.get(signal, 0) + 1
            
            print(f"📊 Distribuição: {signal_counts}")
            
            # Sinais ativos (não HOLD)
            active_signals = [r for r in successful_tests if r['signal_type'] != 'HOLD']
            print(f"🎯 Sinais ativos: {len(active_signals)}/{len(successful_tests)} ({len(active_signals)/len(successful_tests)*100:.1f}%)")
            
            # Sinais de alta qualidade
            high_quality_signals = [
                r for r in active_signals 
                if r['confidence'] >= 0.60 and r['model_accuracy'] >= 0.50
            ]
            
            if active_signals:
                quality_rate = len(high_quality_signals) / len(active_signals) * 100
                print(f"🏆 Taxa de alta qualidade: {quality_rate:.1f}%")
            
            # Melhor sinal
            if active_signals:
                best_signal = max(active_signals, key=lambda x: x['confidence'] * x['model_accuracy'])
                print(f"\n🏆 MELHOR SINAL:")
                print(f"   {best_signal['symbol']} {best_signal['timeframe']}: {best_signal['signal_type']}")
                print(f"   Confiança: {best_signal['confidence']:.3f}")
                print(f"   Acurácia: {best_signal['model_accuracy']:.3f}")
                print(f"   Score: {best_signal['confidence'] * best_signal['model_accuracy']:.3f}")
            
            # Avaliação geral do sistema
            print(f"\n🎯 AVALIAÇÃO GERAL:")
            
            if avg_accuracy >= 0.55 and avg_confidence >= 0.60:
                system_rating = "🟢 EXCELENTE"
                recommendation = "Sistema pronto para uso em produção"
            elif avg_accuracy >= 0.45 and avg_confidence >= 0.50:
                system_rating = "🟡 BOM"
                recommendation = "Sistema funcional, monitoramento recomendado"
            elif avg_accuracy >= 0.35 and avg_confidence >= 0.40:
                system_rating = "🟠 ACEITÁVEL"
                recommendation = "Sistema precisa de ajustes"
            else:
                system_rating = "🔴 NECESSITA MELHORIA"
                recommendation = "Sistema requer otimização adicional"
            
            print(f"   Rating: {system_rating}")
            print(f"   Recomendação: {recommendation}")
        
        # Salvar resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"validacao_ai_engine_v3_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'total_tests': total_tests,
                'successful_tests': len(successful_tests),
                'results': results,
                'summary': {
                    'avg_confidence': avg_confidence if successful_tests else 0,
                    'avg_accuracy': avg_accuracy if successful_tests else 0,
                    'avg_execution_time': avg_time if successful_tests else 0,
                    'signal_distribution': signal_counts if successful_tests else {},
                    'active_signals_count': len(active_signals) if successful_tests else 0,
                    'high_quality_count': len(high_quality_signals) if successful_tests else 0
                }
            }, f, indent=2, default=str)
        
        print(f"\n💾 Resultados salvos em: {filename}")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_threshold_optimization():
    """Teste de otimização de threshold"""
    
    print(f"\n🎯 TESTE DE OTIMIZAÇÃO DE THRESHOLD")
    print("=" * 50)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from ai_engine_v3_otimizado import OptimizedAIEngineV3
        
        config = Config()
        market_data = MarketDataManager(config)
        
        # Testar com BTCUSDT 5m (melhor performance anteriormente)
        symbol = 'BTCUSDT'
        timeframe = '5m'
        
        df = market_data.get_historical_data(symbol, timeframe, 500)
        if df is None or len(df) < 200:
            print("❌ Dados insuficientes")
            return
        
        # Testar diferentes thresholds
        thresholds = [0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
        
        print(f"📊 Testando thresholds para {symbol} {timeframe}")
        
        best_threshold = None
        best_score = 0
        
        for threshold in thresholds:
            print(f"\n📏 Threshold: {threshold}")
            
            ai_engine = OptimizedAIEngineV3(config)
            ai_engine.min_confidence_threshold = threshold
            
            result = ai_engine.optimized_predict_signal(df, f"{symbol}_{timeframe}")
            
            signal_type = result.get('signal_type', 'HOLD')
            confidence = result.get('confidence', 0)
            model_accuracy = result.get('model_accuracy', 0)
            
            # Calcular score (confiança * acurácia * peso do sinal ativo)
            active_weight = 1.2 if signal_type != 'HOLD' else 0.8
            score = confidence * model_accuracy * active_weight
            
            print(f"   🎯 Sinal: {signal_type}")
            print(f"   📈 Confiança: {confidence:.3f}")
            print(f"   🎯 Acurácia: {model_accuracy:.3f}")
            print(f"   📊 Score: {score:.3f}")
            
            if score > best_score:
                best_score = score
                best_threshold = threshold
        
        print(f"\n🏆 THRESHOLD ÓTIMO ENCONTRADO:")
        print(f"   Threshold: {best_threshold}")
        print(f"   Score: {best_score:.3f}")
        
        return best_threshold
        
    except Exception as e:
        print(f"❌ Erro na otimização: {e}")
        return None

def main():
    """Função principal"""
    
    print("🚀 VALIDAÇÃO FINAL DO AI ENGINE V3 OTIMIZADO")
    print("=" * 70)
    
    # Teste direto do AI Engine
    results = test_ai_engine_direct()
    
    # Teste de otimização de threshold
    optimal_threshold = test_threshold_optimization()
    
    print(f"\n✅ VALIDAÇÃO CONCLUÍDA!")
    print("=" * 70)
    
    if results:
        successful_results = [r for r in results if r.get('success', False)]
        
        if successful_results:
            avg_accuracy = sum(r['model_accuracy'] for r in successful_results) / len(successful_results)
            active_signals = len([r for r in successful_results if r['signal_type'] != 'HOLD'])
            
            print(f"🎯 AI Engine V3 funcionando corretamente")
            print(f"📊 Acurácia média: {avg_accuracy:.1%}")
            print(f"🚀 Sinais ativos: {active_signals}/{len(successful_results)}")
            
            if optimal_threshold:
                print(f"⚙️ Threshold ótimo sugerido: {optimal_threshold}")
            
            # Determinar se o sistema está pronto
            if avg_accuracy >= 0.45 and active_signals >= len(successful_results) * 0.5:
                print(f"\n✅ SISTEMA APROVADO PARA PRODUÇÃO!")
                print(f"   - Acurácia aceitável (≥45%)")
                print(f"   - Boa atividade de sinais")
                print(f"   - Performance estável")
            else:
                print(f"\n⚠️ SISTEMA FUNCIONAL MAS REQUER MONITORAMENTO")
                print(f"   - Considere ajustes finos se necessário")
        else:
            print(f"❌ SISTEMA REQUER CORREÇÕES")
    else:
        print(f"❌ VALIDAÇÃO FALHOU")

if __name__ == "__main__":
    main()
