#!/usr/bin/env python3
"""
Teste simples e rápido do market_analyzer para identificar onde está travando
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from src.market_analyzer import MarketAnalyzer

def test_market_analyzer_steps():
    """Testa cada passo do market_analyzer separadamente"""
    print("=== TESTE MARKET ANALYZER SIMPLES ===")
    
    try:
        print("1. Criando instância do MarketAnalyzer...")
        start_time = time.time()
        analyzer = MarketAnalyzer()
        print(f"   ✅ Criado em {time.time() - start_time:.2f}s")
        
        # Teste 1: Método direto sem dependências
        print("\n2. Testando método get_volatility_score...")
        start_time = time.time()
        try:
            # Dados de teste simples
            test_data = {
                'high': [100, 102, 101, 103, 105],
                'low': [98, 99, 100, 101, 102],
                'close': [99, 101, 100.5, 102, 104]
            }
            volatility = analyzer.get_volatility_score(test_data)
            print(f"   ✅ Volatility score: {volatility} em {time.time() - start_time:.2f}s")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            
        # Teste 2: Método com dados reais
        print("\n3. Testando get_trade_recommendation com timeout...")
        start_time = time.time()
        
        # Usar timeout para evitar travamento
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Timeout após 10 segundos")
        
        # Windows não suporta signal, vamos usar threading
        import threading
        result = {'recommendation': None, 'error': None}
        
        def run_recommendation():
            try:
                recommendation = analyzer.get_trade_recommendation('BTCUSDT')
                result['recommendation'] = recommendation
            except Exception as e:
                result['error'] = str(e)
        
        thread = threading.Thread(target=run_recommendation)
        thread.daemon = True
        thread.start()
        thread.join(timeout=15)  # 15 segundos de timeout
        
        if thread.is_alive():
            print(f"   ❌ TRAVOU! Método não respondeu em 15 segundos")
            return
        elif result['error']:
            print(f"   ❌ Erro: {result['error']}")
        else:
            print(f"   ✅ Recommendation: {result['recommendation']} em {time.time() - start_time:.2f}s")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_market_analyzer_steps()
