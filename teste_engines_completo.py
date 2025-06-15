#!/usr/bin/env python3
"""
🧪 TESTE COMPLETO DE AI ENGINES - COMPARAÇÃO FINAL
Testa todas as engines com dados realistas e métricas detalhadas
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
from typing import Dict, List, Tuple

# Configurar logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_realistic_data(periods=500):
    """Gerar dados mais realistas para teste"""
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='1h')
    
    # Simular movimento mais realista
    np.random.seed(42)
    base_price = 50000
    returns = []
    
    # Criar alguns padrões conhecidos
    for i in range(periods):
        if i < 100:  # Tendência de alta
            ret = np.random.normal(0.003, 0.015)
        elif i < 200:  # Consolidação
            ret = np.random.normal(0.0, 0.008)
        elif i < 300:  # Tendência de baixa
            ret = np.random.normal(-0.002, 0.020)
        else:  # Recuperação
            ret = np.random.normal(0.001, 0.012)
        returns.append(ret)
    
    # Calcular preços
    prices = [base_price]
    for ret in returns[1:]:
        price = prices[-1] * (1 + ret)
        prices.append(max(price, base_price * 0.3))  # Não ir abaixo de 30% do preço base
    
    # Criar OHLCV mais realista
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': np.random.lognormal(15, 1, len(dates))
    })
    
    # Garantir que high >= low e price está entre eles
    for i in range(len(df)):
        df.loc[i, 'high'] = max(df.loc[i, 'high'], df.loc[i, 'open'], df.loc[i, 'close'])
        df.loc[i, 'low'] = min(df.loc[i, 'low'], df.loc[i, 'open'], df.loc[i, 'close'])
    
    return df

def test_engine_comprehensive(engine_name, engine_class):
    """Teste abrangente de uma engine"""
    print(f"🧪 Testando {engine_name}...")
    
    result = {
        'engine_name': engine_name,
        'available': False,
        'init_success': False,
        'methods_tested': {},
        'performance_metrics': {},
        'signals_generated': [],
        'errors': []
    }
    
    try:
        # Importar config
        from src.config import Config
        config = Config()
        
        # Inicializar engine
        start_init = time.time()
        engine = engine_class(config)
        init_time = time.time() - start_init
        
        result['available'] = True
        result['init_success'] = True
        result['init_time'] = round(init_time, 4)
        
        # Gerar dados de teste
        test_data = generate_realistic_data()
        
        # Testar diferentes métodos disponíveis
        methods_to_test = [
            ('generate_signal', lambda e, d: e.generate_signal(d, 'BTCUSDT', '1h')),
            ('predict_signal', lambda e, d: e.predict_signal(d, 'BTCUSDT')),
            ('analyze_market', lambda e, d: e.analyze_market(d, 'BTCUSDT')),
            ('ultra_fast_predict', lambda e, d: e.ultra_fast_predict(d, 'BTCUSDT')),
            ('optimized_predict_signal', lambda e, d: e.optimized_predict_signal(d, 'BTCUSDT'))
        ]
        
        for method_name, method_call in methods_to_test:
            if hasattr(engine, method_name):
                try:
                    start_test = time.time()
                    signal_result = method_call(engine, test_data)
                    test_time = time.time() - start_test
                    
                    result['methods_tested'][method_name] = {
                        'success': True,
                        'time': round(test_time, 4),
                        'result': signal_result
                    }
                    
                    # Coletar dados do sinal
                    if signal_result:
                        signal_data = {
                            'method': method_name,
                            'signal': signal_result.get('signal_type', signal_result.get('signal', 'unknown')),
                            'confidence': signal_result.get('confidence', 0),
                            'time': test_time
                        }
                        result['signals_generated'].append(signal_data)
                        
                except Exception as e:
                    result['methods_tested'][method_name] = {
                        'success': False,
                        'error': str(e),
                        'time': 0
                    }
                    result['errors'].append(f"{method_name}: {str(e)}")
        
        # Calcular métricas de performance
        successful_methods = [m for m in result['methods_tested'].values() if m['success']]
        
        if successful_methods:
            times = [m['time'] for m in successful_methods]
            result['performance_metrics'] = {
                'avg_time': round(np.mean(times), 4),
                'min_time': round(min(times), 4),
                'max_time': round(max(times), 4),
                'methods_count': len(successful_methods),
                'speed_score': round(1 / max(np.mean(times), 0.0001), 2)
            }
            
            # Analisar sinais gerados
            if result['signals_generated']:
                signals = [s['signal'] for s in result['signals_generated']]
                confidences = [s['confidence'] for s in result['signals_generated']]
                
                result['signal_analysis'] = {
                    'signals_count': len(signals),
                    'unique_signals': list(set(signals)),
                    'avg_confidence': round(np.mean(confidences), 3),
                    'max_confidence': round(max(confidences), 3),
                    'min_confidence': round(min(confidences), 3),
                    'non_hold_signals': len([s for s in signals if s not in ['hold', 'HOLD', 2]])
                }
        
        print(f"✅ {engine_name}: {len(successful_methods)} métodos OK, {len(result['signals_generated'])} sinais")
        
    except Exception as e:
        result['error'] = str(e)
        print(f"❌ {engine_name}: {e}")
    
    return result

def calculate_final_score(result):
    """Calcular score final para ranking"""
    if not result.get('available') or not result.get('performance_metrics'):
        return 0
    
    metrics = result['performance_metrics']
    signal_analysis = result.get('signal_analysis', {})
    
    # Componentes do score
    speed_component = min(metrics.get('speed_score', 0), 1000) / 1000  # Normalizado 0-1
    methods_component = min(metrics.get('methods_count', 0), 5) / 5   # Normalizado 0-1
    confidence_component = signal_analysis.get('avg_confidence', 0)   # Já 0-1
    signal_diversity = min(len(signal_analysis.get('unique_signals', [])), 3) / 3  # Normalizado 0-1
    
    # Score ponderado (speed e confidence são mais importantes)
    final_score = (
        speed_component * 0.35 +
        confidence_component * 0.35 +
        methods_component * 0.20 +
        signal_diversity * 0.10
    )
    
    return round(final_score, 4)

def main():
    """Função principal do teste completo"""
    print("🚀 TESTE COMPLETO DE AI ENGINES")
    print("=" * 50)
    
    # Lista de engines para testar
    engines_to_test = [
        ('AITradingEngine', 'src.ai_engine', 'AITradingEngine'),
        ('UltraFastAIEngine', 'ai_engine_ultra_fast', 'UltraFastAIEngine'),
        ('OptimizedAIEngineV3', 'ai_engine_v3_otimizado', 'OptimizedAIEngineV3'),
        ('UltraEnhancedAIEngine', 'ai_engine_ultra_enhanced', 'UltraEnhancedAIEngine')
    ]
    
    results = []
    
    for engine_name, module_name, class_name in engines_to_test:
        try:
            # Importar dinamicamente
            module = __import__(module_name, fromlist=[class_name])
            engine_class = getattr(module, class_name)
            
            # Testar engine
            result = test_engine_comprehensive(engine_name, engine_class)
            results.append(result)
            
        except ImportError as e:
            print(f"⚠️ Não foi possível importar {engine_name}: {e}")
            results.append({
                'engine_name': engine_name,
                'available': False,
                'error': f"Import error: {e}"
            })
        except Exception as e:
            print(f"❌ Erro geral com {engine_name}: {e}")
            results.append({
                'engine_name': engine_name,
                'available': False,
                'error': f"General error: {e}"
            })
    
    # Calcular scores e ordenar
    available_engines = [r for r in results if r.get('available', False)]
    
    if available_engines:
        # Calcular scores finais
        for result in available_engines:
            result['final_score'] = calculate_final_score(result)
        
        # Ordenar por score final
        available_engines.sort(key=lambda x: x['final_score'], reverse=True)
        
        print("\n📊 RESULTADOS DETALHADOS:")
        print("-" * 50)
        
        for i, result in enumerate(available_engines, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
            print(f"\n{medal} {result['engine_name']} (Score: {result['final_score']})")
            
            if result.get('performance_metrics'):
                pm = result['performance_metrics']
                print(f"   ⚡ Velocidade: {pm.get('avg_time', 'N/A')}s (Score: {pm.get('speed_score', 'N/A')})")
                print(f"   🔧 Métodos: {pm.get('methods_count', 'N/A')}")
                
            if result.get('signal_analysis'):
                sa = result['signal_analysis']
                print(f"   📊 Sinais: {sa.get('signals_count', 'N/A')} total, {sa.get('non_hold_signals', 'N/A')} não-neutros")
                print(f"   💯 Confiança: {sa.get('avg_confidence', 'N/A')} (média)")
                print(f"   🎯 Tipos: {sa.get('unique_signals', 'N/A')}")
            
            if result.get('errors'):
                print(f"   ⚠️ Erros: {len(result['errors'])}")
        
        # Recomendação final
        best_engine = available_engines[0]
        print(f"\n🎯 RECOMENDAÇÃO FINAL:")
        print(f"✅ MELHOR ENGINE: {best_engine['engine_name']}")
        print(f"📈 Score Final: {best_engine['final_score']}")
        print(f"⚡ Para Mobile/Android: {'IDEAL' if best_engine['final_score'] > 0.7 else 'ACEITÁVEL' if best_engine['final_score'] > 0.5 else 'PROBLEMÁTICA'}")
        
        # Salvar resultado detalhado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"engine_comparison_complete_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Resultados completos salvos em: {filename}")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            
        # Criar recomendação específica
        recommendation = {
            'timestamp': timestamp,
            'best_engine': best_engine['engine_name'],
            'final_score': best_engine['final_score'],
            'mobile_ready': best_engine['final_score'] > 0.6,
            'reasoning': f"Score {best_engine['final_score']} baseado em velocidade, confiança e funcionalidade",
            'alternatives': [e['engine_name'] for e in available_engines[1:3]]
        }
        
        rec_filename = f"ai_engine_final_recommendation_{timestamp}.json"
        try:
            with open(rec_filename, 'w') as f:
                json.dump(recommendation, f, indent=2)
            print(f"📋 Recomendação salva em: {rec_filename}")
        except Exception as e:
            print(f"❌ Erro ao salvar recomendação: {e}")
    
    else:
        print("❌ Nenhuma engine disponível funcionou")
        
    print("\n✅ Teste completo concluído!")

if __name__ == "__main__":
    main()
