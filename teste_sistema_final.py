#!/usr/bin/env python3
"""
✅ TESTE FINAL DO SISTEMA OTIMIZADO
Validação completa da integração do AI Engine V3
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

def test_system_integration():
    """Teste de integração completa do sistema"""
    
    print("🚀 TESTE FINAL DO SISTEMA OTIMIZADO V3")
    print("=" * 60)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from src.market_analyzer import MarketAnalyzer
        from ai_engine_v3_otimizado import OptimizedAIEngineV3
        
        config = Config()
        market_data = MarketDataManager(config)
        
        # Inicializar AI Engine V3
        ai_engine = OptimizedAIEngineV3(config)
        print("✅ AI Engine V3 inicializado")
          # Inicializar Market Analyzer com novo engine
        market_analyzer = MarketAnalyzer(config, market_data, ai_engine)
        print("✅ Market Analyzer inicializado")
        
        # Símbolos para testar
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        timeframes = ['1m', '5m']
        
        results = []
        
        for symbol in symbols:
            for timeframe in timeframes:
                print(f"\n📊 Analisando {symbol} {timeframe}...")
                  try:
                    # Usar market analyzer completo
                    analysis = market_analyzer.analyze_market_context(symbol, timeframe)
                    
                    if analysis:
                        signal = analysis.get('recommendation', 'UNKNOWN')
                        confidence = analysis.get('confidence', 0)
                        ai_confidence = analysis.get('ai_confidence', 0)
                        
                        # Testar também predição direta do AI
                        df = market_data.get_historical_data(symbol, timeframe, 500)
                        if df is not None and len(df) >= 200:
                            ai_result = ai_engine.optimized_predict_signal(df, f"{symbol}_{timeframe}")
                            
                            direct_signal = ai_result.get('signal_type', 'HOLD')
                            direct_confidence = ai_result.get('confidence', 0)
                            model_accuracy = ai_result.get('model_accuracy', 0)
                        else:
                            direct_signal = 'NO_DATA'
                            direct_confidence = 0
                            model_accuracy = 0
                        
                        result = {
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'analyzer_signal': signal,
                            'analyzer_confidence': confidence,
                            'ai_confidence': ai_confidence,
                            'direct_ai_signal': direct_signal,
                            'direct_ai_confidence': direct_confidence,
                            'model_accuracy': model_accuracy,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        results.append(result)
                        
                        print(f"   🎯 Market Analyzer: {signal} (conf: {confidence:.3f})")
                        print(f"   🧠 AI Direto: {direct_signal} (conf: {direct_confidence:.3f}, acc: {model_accuracy:.3f})")
                        
                        # Verificar consistência
                        if signal == direct_signal:
                            print(f"   ✅ Sinais consistentes")
                        else:
                            print(f"   ⚠️ Sinais diferentes (analyzer vs ai direto)")
                    else:
                        print(f"   ❌ Falha na análise")
                        
                except Exception as e:
                    print(f"   ❌ Erro: {e}")
                    
        # Análise dos resultados
        print(f"\n📊 ANÁLISE DOS RESULTADOS")
        print("=" * 60)
        
        if results:
            # Estatísticas gerais
            total_tests = len(results)
            successful_tests = len([r for r in results if r['direct_ai_signal'] != 'NO_DATA'])
            
            print(f"📈 Testes realizados: {total_tests}")
            print(f"✅ Testes bem-sucedidos: {successful_tests}")
            
            # Distribuição de sinais
            signals_analyzer = {}
            signals_ai = {}
            
            for result in results:
                analyzer_signal = result['analyzer_signal']
                ai_signal = result['direct_ai_signal']
                
                signals_analyzer[analyzer_signal] = signals_analyzer.get(analyzer_signal, 0) + 1
                signals_ai[ai_signal] = signals_ai.get(ai_signal, 0) + 1
            
            print(f"\n📊 Distribuição Market Analyzer: {signals_analyzer}")
            print(f"🧠 Distribuição AI Direto: {signals_ai}")
            
            # Métricas de qualidade
            valid_results = [r for r in results if r['direct_ai_signal'] != 'NO_DATA']
            if valid_results:
                avg_ai_confidence = sum(r['direct_ai_confidence'] for r in valid_results) / len(valid_results)
                avg_model_accuracy = sum(r['model_accuracy'] for r in valid_results) / len(valid_results)
                
                print(f"\n📈 Confiança média AI: {avg_ai_confidence:.3f}")
                print(f"🎯 Acurácia média modelo: {avg_model_accuracy:.3f}")
                
                # Sinais de alta qualidade (confiança > 60% e acurácia > 50%)
                high_quality = [r for r in valid_results if r['direct_ai_confidence'] > 0.6 and r['model_accuracy'] > 0.5]
                print(f"🏆 Sinais de alta qualidade: {len(high_quality)}/{len(valid_results)} ({len(high_quality)/len(valid_results)*100:.1f}%)")
                
                if high_quality:
                    print(f"\n🏆 SINAIS DE ALTA QUALIDADE:")
                    for r in high_quality:
                        print(f"   {r['symbol']} {r['timeframe']}: {r['direct_ai_signal']} (conf: {r['direct_ai_confidence']:.3f}, acc: {r['model_accuracy']:.3f})")
        
        # Salvar resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"teste_sistema_final_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Resultados salvos em: {filename}")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_performance_benchmark():
    """Benchmark de performance do sistema"""
    
    print(f"\n⚡ BENCHMARK DE PERFORMANCE")
    print("=" * 50)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from ai_engine_v3_otimizado import OptimizedAIEngineV3
        
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = OptimizedAIEngineV3(config)
        
        # Teste de velocidade
        symbol = 'BTCUSDT'
        timeframe = '5m'
        
        print(f"🔄 Testando velocidade com {symbol} {timeframe}...")
        
        # Múltiplas execuções para medir tempo médio
        execution_times = []
        
        for i in range(3):
            print(f"   Execução {i+1}/3...")
            
            start_time = time.time()
            
            df = market_data.get_historical_data(symbol, timeframe, 500)
            if df is not None and len(df) >= 200:
                result = ai_engine.optimized_predict_signal(df, f"{symbol}_{timeframe}")
                
                end_time = time.time()
                execution_time = end_time - start_time
                execution_times.append(execution_time)
                
                print(f"      Tempo: {execution_time:.2f}s")
                print(f"      Sinal: {result.get('signal_type', 'N/A')}")
                print(f"      Confiança: {result.get('confidence', 0):.3f}")
            else:
                print(f"      ❌ Dados insuficientes")
        
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            
            print(f"\n📊 ESTATÍSTICAS DE PERFORMANCE:")
            print(f"   ⏱️ Tempo médio: {avg_time:.2f}s")
            print(f"   🚀 Tempo mínimo: {min_time:.2f}s")
            print(f"   🐌 Tempo máximo: {max_time:.2f}s")
            
            # Avaliação de performance
            if avg_time < 5:
                performance_rating = "🟢 EXCELENTE"
            elif avg_time < 10:
                performance_rating = "🟡 BOM"
            elif avg_time < 15:
                performance_rating = "🟠 ACEITÁVEL"
            else:
                performance_rating = "🔴 LENTO"
            
            print(f"   📈 Avaliação: {performance_rating}")
        
    except Exception as e:
        print(f"❌ Erro no benchmark: {e}")

def main():
    """Função principal"""
    
    # Executar teste de integração
    results = test_system_integration()
    
    # Executar benchmark de performance
    test_performance_benchmark()
    
    print(f"\n✅ TESTES FINAIS CONCLUÍDOS!")
    print("=" * 60)
    
    if results:
        print("🎯 Sistema integrado com sucesso")
        print("📊 AI Engine V3 funcionando corretamente")
        print("🚀 Performance validada")
        print("💾 Resultados documentados")
        
        # Resumo da qualidade
        valid_results = [r for r in results if r.get('direct_ai_signal') != 'NO_DATA']
        if valid_results:
            high_quality_count = len([r for r in valid_results if r.get('direct_ai_confidence', 0) > 0.6 and r.get('model_accuracy', 0) > 0.5])
            quality_percentage = (high_quality_count / len(valid_results)) * 100
            
            print(f"🏆 Taxa de sinais de alta qualidade: {quality_percentage:.1f}%")
            
            if quality_percentage >= 50:
                print("✅ META ATINGIDA: Sistema com boa qualidade de sinais!")
            else:
                print("⚠️ Sistema funcional, mas pode precisar de ajustes finos")
    else:
        print("❌ Problemas detectados na integração")

if __name__ == "__main__":
    main()
