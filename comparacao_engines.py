#!/usr/bin/env python3
"""
🔬 COMPARAÇÃO DE PERFORMANCE - AI ENGINES
Teste comparativo entre diferentes versões do AI Engine
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

def compare_ai_engines():
    """Comparar performance dos diferentes engines"""
    
    print("🔬 COMPARAÇÃO DE PERFORMANCE - AI ENGINES")
    print("=" * 70)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from ai_engine_ultra_enhanced import UltraEnhancedAIEngine
        from ai_engine_v3_otimizado import OptimizedAIEngineV3
        
        config = Config()
        market_data = MarketDataManager(config)
        
        # Engines para testar
        engines = {
            'Ultra Enhanced': UltraEnhancedAIEngine(config),
            'Optimized V3': OptimizedAIEngineV3(config)
        }
        
        # Símbolos e timeframes para testar
        test_cases = [
            ('BTCUSDT', '1m'),
            ('BTCUSDT', '5m'),
            ('ETHUSDT', '1m'),
            ('ETHUSDT', '5m'),
            ('BNBUSDT', '1m'),
            ('BNBUSDT', '5m'),
        ]
        
        results = {}
        
        for symbol, timeframe in test_cases:
            print(f"\n📊 Testando {symbol} {timeframe}")
            print("-" * 50)
            
            # Obter dados
            df = market_data.get_historical_data(symbol, timeframe, 500)
            if df is None or len(df) < 200:
                print(f"❌ Dados insuficientes para {symbol} {timeframe}")
                continue
            
            test_key = f"{symbol}_{timeframe}"
            results[test_key] = {}
            
            for engine_name, engine in engines.items():
                print(f"\n🧠 Testando {engine_name}...")
                
                start_time = time.time()
                
                try:
                    # Fazer predição
                    if engine_name == 'Ultra Enhanced':
                        result = engine.ultra_predict_signal(df, f"{symbol}_{timeframe}")
                    else:  # Optimized V3
                        result = engine.optimized_predict_signal(df, f"{symbol}_{timeframe}")
                    
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    # Extrair métricas
                    signal_type = result.get('signal_type', 'HOLD')
                    confidence = result.get('confidence', 0)
                    model_accuracy = result.get('model_accuracy', 0)
                    confluence = result.get('confluence', 0)
                    
                    results[test_key][engine_name] = {
                        'signal_type': signal_type,
                        'confidence': confidence,
                        'model_accuracy': model_accuracy,
                        'confluence': confluence,
                        'execution_time': execution_time,
                        'success': True
                    }
                    
                    print(f"   ✅ Sinal: {signal_type}")
                    print(f"   📈 Confiança: {confidence:.3f}")
                    print(f"   🎯 Acurácia: {model_accuracy:.3f}")
                    print(f"   ⏱️ Tempo: {execution_time:.2f}s")
                    
                except Exception as e:
                    results[test_key][engine_name] = {
                        'success': False,
                        'error': str(e),
                        'execution_time': time.time() - start_time
                    }
                    print(f"   ❌ Erro: {e}")
        
        # Análise comparativa
        print(f"\n📊 ANÁLISE COMPARATIVA")
        print("=" * 70)
        
        engine_stats = {}
        for engine_name in engines.keys():
            engine_stats[engine_name] = {
                'total_tests': 0,
                'successful_tests': 0,
                'active_signals': 0,
                'avg_confidence': 0,
                'avg_accuracy': 0,
                'avg_execution_time': 0,
                'signals_by_type': {'BUY': 0, 'SELL': 0, 'HOLD': 0}
            }
        
        # Calcular estatísticas
        for test_key, test_results in results.items():
            for engine_name, result in test_results.items():
                stats = engine_stats[engine_name]
                stats['total_tests'] += 1
                stats['avg_execution_time'] += result.get('execution_time', 0)
                
                if result.get('success', False):
                    stats['successful_tests'] += 1
                    confidence = result.get('confidence', 0)
                    accuracy = result.get('model_accuracy', 0)
                    signal_type = result.get('signal_type', 'HOLD')
                    
                    stats['avg_confidence'] += confidence
                    stats['avg_accuracy'] += accuracy
                    stats['signals_by_type'][signal_type] += 1
                    
                    if signal_type != 'HOLD':
                        stats['active_signals'] += 1
        
        # Normalizar médias
        for engine_name, stats in engine_stats.items():
            if stats['successful_tests'] > 0:
                stats['avg_confidence'] /= stats['successful_tests']
                stats['avg_accuracy'] /= stats['successful_tests']
            if stats['total_tests'] > 0:
                stats['avg_execution_time'] /= stats['total_tests']
        
        # Exibir resultados
        for engine_name, stats in engine_stats.items():
            print(f"\n🧠 {engine_name.upper()}")
            print(f"   ✅ Testes bem-sucedidos: {stats['successful_tests']}/{stats['total_tests']}")
            print(f"   🎯 Sinais ativos: {stats['active_signals']}")
            print(f"   📈 Confiança média: {stats['avg_confidence']:.3f}")
            print(f"   🎯 Acurácia média: {stats['avg_accuracy']:.3f}")
            print(f"   ⏱️ Tempo médio: {stats['avg_execution_time']:.2f}s")
            print(f"   📊 Distribuição: BUY:{stats['signals_by_type']['BUY']} SELL:{stats['signals_by_type']['SELL']} HOLD:{stats['signals_by_type']['HOLD']}")
            
            # Calcular score geral
            success_rate = stats['successful_tests'] / max(stats['total_tests'], 1)
            signal_activity = stats['active_signals'] / max(stats['successful_tests'], 1)
            overall_score = (stats['avg_confidence'] * 0.4 + 
                           stats['avg_accuracy'] * 0.4 + 
                           success_rate * 0.1 + 
                           signal_activity * 0.1)
            
            print(f"   🏆 Score geral: {overall_score:.3f}")
        
        # Recomendação
        best_engine = max(engine_stats.keys(), 
                         key=lambda x: engine_stats[x]['avg_accuracy'] * engine_stats[x]['avg_confidence'])
        
        print(f"\n🏆 RECOMENDAÇÃO:")
        print(f"   Engine recomendado: {best_engine}")
        print(f"   Razão: Melhor combinação de acurácia e confiança")
        
        # Salvar resultados detalhados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"comparacao_engines_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'results': results,
                'statistics': engine_stats,
                'recommendation': best_engine
            }, f, indent=2, default=str)
        
        print(f"\n💾 Resultados salvos em: {filename}")
        
        return results, engine_stats
        
    except Exception as e:
        print(f"❌ Erro na comparação: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def analyze_signal_quality():
    """Análise de qualidade dos sinais gerados"""
    
    print(f"\n🔍 ANÁLISE DE QUALIDADE DOS SINAIS")
    print("=" * 50)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from ai_engine_v3_otimizado import OptimizedAIEngineV3
        
        config = Config()
        market_data = MarketDataManager(config)
        optimized_ai = OptimizedAIEngineV3(config)
        
        # Teste com diferentes thresholds
        thresholds = [0.30, 0.35, 0.40, 0.45, 0.50]
        symbol = 'BTCUSDT'
        timeframe = '5m'
        
        print(f"📊 Analisando {symbol} {timeframe} com diferentes thresholds")
        
        df = market_data.get_historical_data(symbol, timeframe, 500)
        if df is None or len(df) < 200:
            print("❌ Dados insuficientes")
            return
        
        threshold_results = []
        
        for threshold in thresholds:
            print(f"\n📏 Threshold: {threshold}")
            
            # Configurar threshold
            optimized_ai.min_confidence_threshold = threshold
            
            # Fazer predição
            result = optimized_ai.optimized_predict_signal(df, f"{symbol}_{timeframe}")
            
            signal_type = result.get('signal_type', 'HOLD')
            confidence = result.get('confidence', 0)
            model_accuracy = result.get('model_accuracy', 0)
            
            threshold_results.append({
                'threshold': threshold,
                'signal_type': signal_type,
                'confidence': confidence,
                'model_accuracy': model_accuracy,
                'is_active': signal_type != 'HOLD'
            })
            
            print(f"   🎯 Sinal: {signal_type}")
            print(f"   📈 Confiança: {confidence:.3f}")
            print(f"   🎯 Acurácia: {model_accuracy:.3f}")
        
        # Encontrar threshold ótimo
        active_signals = [r for r in threshold_results if r['is_active']]
        
        if active_signals:
            # Ordenar por confiança * acurácia
            active_signals.sort(key=lambda x: x['confidence'] * x['model_accuracy'], reverse=True)
            best_signal = active_signals[0]
            
            print(f"\n🏆 MELHOR CONFIGURAÇÃO:")
            print(f"   Threshold: {best_signal['threshold']}")
            print(f"   Sinal: {best_signal['signal_type']}")
            print(f"   Confiança: {best_signal['confidence']:.3f}")
            print(f"   Acurácia: {best_signal['model_accuracy']:.3f}")
            print(f"   Score: {best_signal['confidence'] * best_signal['model_accuracy']:.3f}")
        else:
            print(f"\n⚠️ Nenhum sinal ativo encontrado")
            print(f"   Recomendação: Usar threshold mais baixo (<{min(thresholds)})")
        
        return threshold_results
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Executar comparação
    results, stats = compare_ai_engines()
    
    # Executar análise de qualidade
    quality_results = analyze_signal_quality()
    
    print(f"\n✅ TESTES CONCLUÍDOS!")
    print("=" * 50)
    print("📊 Engines comparados")
    print("🔍 Qualidade dos sinais analisada")
    print("💾 Resultados salvos em arquivos JSON")
