#!/usr/bin/env python3
"""
Teste individualizado de cada método do market_analyzer para identificar onde está travando
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import signal
import threading
from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.market_analyzer import MarketAnalyzer

def test_with_timeout(func, args=(), kwargs={}, timeout=10, method_name="método"):
    """Executa função com timeout"""
    result = {'value': None, 'error': None, 'completed': False}
    
    def run_function():
        try:
            result['value'] = func(*args, **kwargs)
            result['completed'] = True
        except Exception as e:
            result['error'] = str(e)
            result['completed'] = True
    
    thread = threading.Thread(target=run_function)
    thread.daemon = True
    start_time = time.time()
    thread.start()
    thread.join(timeout=timeout)
    
    elapsed = time.time() - start_time
    
    if thread.is_alive():
        print(f"   ❌ {method_name} TRAVOU! (tempo limite: {timeout}s)")
        return False, None, elapsed
    elif result['error']:
        print(f"   ❌ {method_name} erro: {result['error']}")
        return False, result['error'], elapsed
    else:
        print(f"   ✅ {method_name} OK em {elapsed:.2f}s")
        return True, result['value'], elapsed

def test_market_analyzer_methods():
    """Testa cada método do market_analyzer individualmente"""
    print("=== TESTE INDIVIDUALIZADO MARKET ANALYZER ===")
    
    try:
        print("1. Inicializando componentes...")
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        analyzer = MarketAnalyzer(config, market_data, ai_engine)
        
        symbol = 'BTCUSDT'
        timeframe = '1h'
        
        print("✅ Componentes inicializados")
        
        print(f"\n2. Obtendo dados históricos para {symbol}...")
        success, df, elapsed = test_with_timeout(
            market_data.get_historical_data, 
            args=(symbol, timeframe, 100),
            timeout=15,
            method_name="get_historical_data"
        )
        
        if not success:
            print("❌ Falha ao obter dados históricos - parando teste")
            return
        
        print(f"   Dataset: {len(df)} registros")
        
        print("\n3. Testando métodos individuais do market_analyzer...")
        
        # Calcular indicadores técnicos primeiro
        print("   3.1. Calculando indicadores técnicos...")
        success, df_with_indicators, elapsed = test_with_timeout(
            analyzer.technical_indicators.calculate_all_indicators,
            args=(df,),
            timeout=20,
            method_name="calculate_all_indicators"
        )
        
        if not success:
            print("❌ Falha nos indicadores técnicos - usando dados originais")
            df_with_indicators = df
        else:
            print(f"      Indicadores: {len(df_with_indicators.columns)} colunas")
        
        # Testar cada método de análise individualmente
        methods_to_test = [
            ("_detect_market_regime", [df_with_indicators]),
            ("_analyze_volatility", [df_with_indicators]),
            ("_analyze_volume", [df_with_indicators]),
            ("_analyze_momentum", [df_with_indicators]),
            ("_get_correlation_data", [symbol]),
            ("_analyze_liquidity", [symbol]),
            ("_detect_patterns", [df_with_indicators])
        ]
        
        results = {}
        
        for method_name, args in methods_to_test:
            print(f"   3.{len(results)+2}. Testando {method_name}...")
            
            method = getattr(analyzer, method_name)
            success, result, elapsed = test_with_timeout(
                method,
                args=args,
                timeout=15,
                method_name=method_name
            )
            
            results[method_name] = {
                'success': success,
                'result': result,
                'elapsed': elapsed
            }
            
            if not success:
                print(f"      ⚠️ Problema identificado em {method_name}")
        
        print("\n4. Testando analyze_market_context completo...")
        success, market_context, elapsed = test_with_timeout(
            analyzer.analyze_market_context,
            args=(symbol, timeframe),
            timeout=30,
            method_name="analyze_market_context"
        )
        
        if success and market_context:
            print(f"   Market Score: {market_context.get('market_score', 'N/A')}")
        
        print("\n5. Testando get_trade_recommendation...")
        success, recommendation, elapsed = test_with_timeout(
            analyzer.get_trade_recommendation,
            args=(symbol, timeframe),
            timeout=45,
            method_name="get_trade_recommendation"
        )
        
        if success and recommendation:
            print(f"   Recommendation: {recommendation.get('recommendation', 'N/A')}")
            print(f"   Confidence: {recommendation.get('confidence', 'N/A')}")
        
        print("\n=== RESUMO DOS RESULTADOS ===")
        failed_methods = [name for name, result in results.items() if not result['success']]
        if failed_methods:
            print(f"❌ Métodos que falharam: {', '.join(failed_methods)}")
        else:
            print("✅ Todos os métodos individuais funcionaram")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_market_analyzer_methods()
