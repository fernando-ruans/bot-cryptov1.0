#!/usr/bin/env python3
"""
🎯 TESTE DEFINITIVO - AI ENGINES
Teste final simplificado para escolher a melhor engine
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import json

# Configurar logging simples
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def create_test_data():
    """Criar dados de teste simples e válidos"""
    dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='1h')
    
    # Dados simples mas válidos
    base_price = 50000
    data = {
        'timestamp': dates,
        'open': [base_price + i for i in range(len(dates))],
        'high': [base_price + i + 100 for i in range(len(dates))],
        'low': [base_price + i - 100 for i in range(len(dates))],
        'close': [base_price + i + 50 for i in range(len(dates))],
        'volume': [1000000 + i * 1000 for i in range(len(dates))]
    }
    
    return pd.DataFrame(data)

def test_engine_performance(engine_name, engine_class):
    """Testar performance real de uma engine"""
    print(f"\n🧪 Testando {engine_name}...")
    
    try:
        # Inicializar
        from src.config import Config
        config = Config()
        engine = engine_class(config)
        
        # Preparar dados
        test_data = create_test_data()
        
        # Teste de velocidade
        times = []
        successful_calls = 0
        total_calls = 5
        
        for i in range(total_calls):
            start = time.time()
            
            try:
                # Tentar diferentes métodos
                result = None
                
                if hasattr(engine, 'generate_signal'):
                    result = engine.generate_signal(test_data, 'BTCUSDT', '1h')
                elif hasattr(engine, 'predict_signal'):
                    result = engine.predict_signal(test_data)
                elif hasattr(engine, 'ultra_fast_predict'):
                    result = engine.ultra_fast_predict(test_data, 'BTCUSDT')
                
                if result:
                    successful_calls += 1
                    
            except Exception as e:
                print(f"   ⚠️ Erro na chamada {i+1}: {str(e)[:50]}...")
            
            times.append(time.time() - start)
        
        # Calcular métricas
        avg_time = sum(times) / len(times)
        success_rate = (successful_calls / total_calls) * 100
        speed_score = 1 / max(avg_time, 0.001)
        
        result = {
            'engine': engine_name,
            'avg_time': round(avg_time, 4),
            'success_rate': success_rate,
            'speed_score': round(speed_score, 2),
            'successful_calls': successful_calls,
            'total_calls': total_calls
        }
        
        print(f"   ✅ Tempo médio: {avg_time:.4f}s")
        print(f"   ✅ Taxa de sucesso: {success_rate:.0f}%")
        print(f"   ✅ Score de velocidade: {speed_score:.1f}")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return {
            'engine': engine_name,
            'error': str(e),
            'avg_time': float('inf'),
            'success_rate': 0,
            'speed_score': 0
        }

def main():
    """Função principal"""
    print("🎯 TESTE DEFINITIVO DE AI ENGINES")
    print("=" * 40)
    
    # Engines para testar
    engines = [
        ('UltraFastAIEngine', 'ai_engine_ultra_fast'),
        ('OptimizedAIEngineV3', 'ai_engine_v3_otimizado'),
        ('UltraEnhancedAIEngine', 'ai_engine_ultra_enhanced'),
        ('AITradingEngine', 'src.ai_engine')
    ]
    
    results = []
    
    # Testar cada engine
    for engine_name, module_name in engines:
        try:
            if module_name.startswith('src.'):
                module = __import__(module_name, fromlist=[engine_name])
            else:
                module = __import__(module_name, fromlist=[engine_name])
            
            engine_class = getattr(module, engine_name)
            result = test_engine_performance(engine_name, engine_class)
            results.append(result)
            
        except Exception as e:
            print(f"\n❌ Erro ao importar {engine_name}: {e}")
            results.append({
                'engine': engine_name,
                'error': f'Import failed: {e}',
                'avg_time': float('inf'),
                'success_rate': 0,
                'speed_score': 0
            })
    
    # Analisar resultados
    print(f"\n{'='*40}")
    print("📊 RESULTADOS FINAIS")
    print(f"{'='*40}")
    
    # Filtrar engines funcionais
    working_engines = [r for r in results if r.get('success_rate', 0) > 0]
    
    if working_engines:
        # Ordenar por critério composto (velocidade + confiabilidade)
        for result in working_engines:
            # Score composto: 70% velocidade + 30% confiabilidade
            composite = (result['speed_score'] * 0.7) + (result['success_rate'] * 0.3)
            result['composite_score'] = round(composite, 2)
        
        working_engines.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Exibir ranking
        for i, result in enumerate(working_engines, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
            print(f"\n{medal} {result['engine']}")
            print(f"   Score Composto: {result['composite_score']}")
            print(f"   Velocidade: {result['speed_score']:.1f} ops/s")
            print(f"   Confiabilidade: {result['success_rate']:.0f}%")
            print(f"   Tempo médio: {result['avg_time']:.4f}s")
        
        # Recomendação final
        best = working_engines[0]
        print(f"\n🎯 RECOMENDAÇÃO FINAL:")
        print(f"✅ MELHOR ENGINE: {best['engine']}")
        print(f"📊 Score Composto: {best['composite_score']}")
        print(f"⚡ Velocidade: {best['speed_score']:.1f} ops/s")
        print(f"🔒 Confiabilidade: {best['success_rate']:.0f}%")
        
        # Orientação de uso
        print(f"\n💡 COMO USAR:")
        if best['engine'] == 'UltraFastAIEngine':
            print("from ai_engine_ultra_fast import UltraFastAIEngine")
            print("ai_engine = UltraFastAIEngine(config)")
        elif best['engine'] == 'OptimizedAIEngineV3':
            print("from ai_engine_v3_otimizado import OptimizedAIEngineV3")
            print("ai_engine = OptimizedAIEngineV3(config)")
        elif best['engine'] == 'UltraEnhancedAIEngine':
            print("from ai_engine_ultra_enhanced import UltraEnhancedAIEngine")
            print("ai_engine = UltraEnhancedAIEngine(config)")
        else:
            print("from src.ai_engine import AITradingEngine")
            print("ai_engine = AITradingEngine(config)")
        
        # Salvar resultado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recommendation = {
            'timestamp': timestamp,
            'winner': best,
            'all_results': results,
            'recommendation': f"Use {best['engine']} for best performance"
        }
        
        filename = f"final_engine_recommendation_{timestamp}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(recommendation, f, indent=2, default=str)
            print(f"\n💾 Recomendação salva em: {filename}")
        except:
            pass
        
    else:
        print("❌ Nenhuma engine funcionou corretamente")
    
    print(f"\n✅ Teste concluído!")

if __name__ == "__main__":
    main()
