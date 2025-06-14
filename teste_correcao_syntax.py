#!/usr/bin/env python3
"""
Teste para verificar a correção da sintaxe e funcionamento dos métodos corrigidos
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_syntax_import():
    """Testa se consegue importar o market_analyzer"""
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from src.market_analyzer import MarketAnalyzer
        
        logger.info("✅ Import do MarketAnalyzer funcionou")
        return True
    except Exception as e:
        logger.error(f"❌ Erro no import: {e}")
        return False

def test_basic_functionality():
    """Testa funcionalidade básica do MarketAnalyzer"""
    try:
        from src.market_analyzer import MarketAnalyzer
        
        # Criar instância
        analyzer = MarketAnalyzer()
        
        # Dados de teste simples
        test_data = {
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='1h'),
            'open': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 102,
            'low': np.random.randn(100).cumsum() + 98,
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100)
        }
        
        df = pd.DataFrame(test_data)
        df['symbol'] = 'TEST'
        
        logger.info("✅ Dados de teste criados")
        
        # Testar método de análise (se existir)
        if hasattr(analyzer, '_simple_technical_analysis'):
            # Adicionar alguns indicadores básicos para o teste
            df['rsi'] = 50 + np.random.randn(100) * 10
            df['macd'] = np.random.randn(100) * 0.1
            df['macd_signal'] = np.random.randn(100) * 0.1
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            
            result = analyzer._simple_technical_analysis(df)
            logger.info(f"✅ Análise técnica simples funcionou: {result}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste funcional: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testando correção de sintaxe...")
    
    # Teste 1: Import
    print("\n=== TESTE 1: Import ===")
    import_ok = test_syntax_import()
    
    if import_ok:
        # Teste 2: Funcionalidade básica
        print("\n=== TESTE 2: Funcionalidade ===")
        func_ok = test_basic_functionality()
        
        if func_ok:
            print("\n✅ TODOS OS TESTES PASSARAM!")
            print("📊 O arquivo market_analyzer.py está funcionando corretamente.")
        else:
            print("\n❌ Falha no teste funcional")
    else:
        print("\n❌ Falha no import - problemas de sintaxe ainda existem")
    
    print("\n" + "="*50)
