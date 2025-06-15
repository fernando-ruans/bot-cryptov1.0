#!/usr/bin/env python3
"""
🧪 TESTE SIMPLES E ROBUSTO - AI ENGINES
Teste básico para comparar as engines disponíveis
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_sample_data():
    """Gerar dados de amostra para teste"""
    dates = pd.date_range(end=datetime.now(), periods=200, freq='1H')
    
    # Simular dados OHLCV para BTCUSDT
    np.random.seed(42)
    base_price = 50000
    returns = np.random.normal(0.001, 0.02, len(dates))
    prices = [base_price]
    
    for i in range(1, len(dates)):
        price = prices[-1] * (1 + returns[i])
        prices.append(max(price, base_price * 0.5))
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices], 
        'close': prices,
        'volume': np.random.lognormal(15, 1, len(dates))
    })
    
    return df

def test_engine_basic(engine_name, engine_class):
    """Teste básico de uma engine"""
    logger.info(f"🧪 Testando {engine_name}...")
    
    result = {
        'engine_name': engine_name,
        'available': False,
        'init_success': False,
        'speed_test': 0,
        'error': None
    }
    
    try:
        # Tentar importar config básico
        from src.config import Config
        config = Config()
        
        # Tentar inicializar engine
        start_init = time.time()
        engine = engine_class(config)
        init_time = time.time() - start_init
        
        result['available'] = True
        result['init_success'] = True
        result['init_time'] = round(init_time, 3)
        
        # Teste de velocidade básico
        test_data = generate_sample_data()
        
        start_test = time.time()
        
        # Tentar diferentes métodos de teste
        methods_tested = 0
        if hasattr(engine, 'generate_signal'):
            try:
                signal = engine.generate_signal(test_data, 'BTCUSDT', '1h')
                methods_tested += 1
            except Exception as e:
                logger.debug(f"generate_signal falhou: {e}")
        
        if hasattr(engine, 'predict_signal'):
            try:
                signal = engine.predict_signal(test_data)
                methods_tested += 1
            except Exception as e:
                logger.debug(f"predict_signal falhou: {e}")
                
        if hasattr(engine, 'analyze_market'):
            try:
                signal = engine.analyze_market(test_data, 'BTCUSDT')
                methods_tested += 1
            except Exception as e:
                logger.debug(f"analyze_market falhou: {e}")
        
        test_time = time.time() - start_test
        
        result['speed_test'] = round(test_time, 3)
        result['methods_available'] = methods_tested
        result['speed_score'] = round(1 / max(test_time, 0.001), 2)
        
        logger.info(f"✅ {engine_name}: Init {init_time:.3f}s, Test {test_time:.3f}s")
        
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"❌ {engine_name}: {e}")
    
    return result

def main():
    """Função principal do teste"""
    print("🚀 TESTE BÁSICO DE AI ENGINES")
    print("=" * 40)
    
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
            result = test_engine_basic(engine_name, engine_class)
            results.append(result)
            
        except ImportError as e:
            logger.warning(f"⚠️ Não foi possível importar {engine_name}: {e}")
            results.append({
                'engine_name': engine_name,
                'available': False,
                'error': f"Import error: {e}"
            })
        except Exception as e:
            logger.error(f"❌ Erro geral com {engine_name}: {e}")
            results.append({
                'engine_name': engine_name,
                'available': False,
                'error': f"General error: {e}"
            })
    
    # Analisar resultados
    print("\n📊 RESULTADOS:")
    print("-" * 40)
    
    available_engines = [r for r in results if r.get('available', False)]
    
    if available_engines:
        # Ordenar por speed_score
        available_engines.sort(key=lambda x: x.get('speed_score', 0), reverse=True)
        
        for i, result in enumerate(available_engines, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
            print(f"{medal} {result['engine_name']}")
            print(f"   Init Time: {result.get('init_time', 'N/A')}s")
            print(f"   Test Time: {result.get('speed_test', 'N/A')}s")
            print(f"   Speed Score: {result.get('speed_score', 'N/A')}")
            print(f"   Methods: {result.get('methods_available', 'N/A')}")
            print()
        
        # Recomendação
        best_engine = available_engines[0]
        print("🎯 RECOMENDAÇÃO:")
        print(f"✅ MELHOR ENGINE: {best_engine['engine_name']}")
        print(f"⚡ Speed Score: {best_engine.get('speed_score', 'N/A')}")
        
        # Salvar resultado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"engine_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"💾 Resultados salvos em: {filename}")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
    
    else:
        print("❌ Nenhuma engine disponível funcionou")
        
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    main()
