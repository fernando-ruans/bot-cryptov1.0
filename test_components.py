#!/usr/bin/env python3
"""
Script de teste para verificar se todos os componentes do Trading Bot estão funcionando
"""

import sys
import os
from datetime import datetime

def test_imports():
    """Testa se todas as importações estão funcionando"""
    print("🔍 Testando importações...")
    
    try:
        from src.config import Config
        print("✅ Config - OK")
    except Exception as e:
        print(f"❌ Config - ERRO: {e}")
        return False
    
    try:
        from src.database import DatabaseManager
        print("✅ Database - OK")
    except Exception as e:
        print(f"❌ Database - ERRO: {e}")
        return False
    
    try:
        from src.market_data import MarketDataManager
        print("✅ Market Data - OK")
    except Exception as e:
        print(f"❌ Market Data - ERRO: {e}")
        return False
    
    try:
        from src.technical_indicators import TechnicalIndicators
        print("✅ Technical Indicators - OK")
    except Exception as e:
        print(f"❌ Technical Indicators - ERRO: {e}")
        return False
    
    try:
        from src.ai_engine import AITradingEngine
        print("✅ AI Engine - OK")
    except Exception as e:
        print(f"❌ AI Engine - ERRO: {e}")
        return False
    
    try:
        from src.signal_generator import SignalGenerator
        print("✅ Signal Generator - OK")
    except Exception as e:
        print(f"❌ Signal Generator - ERRO: {e}")
        return False
    
    try:
        from src.risk_manager import RiskManager
        print("✅ Risk Manager - OK")
    except Exception as e:
        print(f"❌ Risk Manager - ERRO: {e}")
        return False
    
    try:
        from src.utils import generate_signal_id, format_currency
        print("✅ Utils - OK")
    except Exception as e:
        print(f"❌ Utils - ERRO: {e}")
        return False
    
    return True

def test_database():
    """Testa a conexão e inicialização do banco de dados"""
    print("\n🗄️ Testando banco de dados...")
    
    try:
        from src.database import DatabaseManager
        db = DatabaseManager()
        
        # Testa inicialização
        db.initialize()
        print("✅ Inicialização do banco - OK")
        
        # Testa estatísticas
        stats = db.get_database_stats()
        print(f"✅ Estatísticas do banco - OK: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ Banco de dados - ERRO: {e}")
        return False

def test_config():
    """Testa a configuração"""
    print("\n⚙️ Testando configuração...")
    
    try:
        from src.config import Config
        config = Config()
        
        print(f"✅ Pares crypto: {len(config.CRYPTO_PAIRS)} pares")
        print(f"✅ Pares forex: {len(config.FOREX_PAIRS)} pares")
        print(f"✅ Timeframes: {config.TIMEFRAMES}")
        print(f"✅ Modelo AI: {config.AI_MODEL_PATH}")
        
        return True
    except Exception as e:
        print(f"❌ Configuração - ERRO: {e}")
        return False

def test_technical_indicators():
    """Testa os indicadores técnicos com dados simulados"""
    print("\n📊 Testando indicadores técnicos...")
    
    try:
        import pandas as pd
        import numpy as np
        from src.technical_indicators import TechnicalIndicators
        
        # Criar dados simulados
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
        np.random.seed(42)
        
        # Simular dados OHLCV
        close_prices = 50000 + np.cumsum(np.random.randn(100) * 100)
        high_prices = close_prices + np.random.rand(100) * 200
        low_prices = close_prices - np.random.rand(100) * 200
        open_prices = np.roll(close_prices, 1)
        volume = np.random.randint(1000, 10000, 100)
        
        data = pd.DataFrame({
            'timestamp': dates,
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volume
        })
        
        from src.config import Config
        config = Config()
        ti = TechnicalIndicators(config)
        
        # Testar cálculo de todos os indicadores
        data_with_indicators = ti.calculate_all_indicators(data)
        print(f"✅ Indicadores calculados - colunas adicionadas: {len(data_with_indicators.columns) - len(data.columns)}")
        
        # Verificar se alguns indicadores específicos foram calculados
        if 'rsi' in data_with_indicators.columns:
            print(f"✅ RSI calculado - último valor: {data_with_indicators['rsi'].iloc[-1]:.2f}")
        
        if 'macd' in data_with_indicators.columns:
            print(f"✅ MACD calculado - último valor: {data_with_indicators['macd'].iloc[-1]:.2f}")
        
        if 'bb_upper' in data_with_indicators.columns:
            print(f"✅ Bollinger Bands calculadas - última banda superior: {data_with_indicators['bb_upper'].iloc[-1]:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Indicadores técnicos - ERRO: {e}")
        return False

def test_ai_engine():
    """Testa o motor de IA"""
    print("\n🧠 Testando motor de IA...")
    
    try:
        from src.config import Config
        from src.ai_engine import AITradingEngine
        import pandas as pd
        import numpy as np
        
        config = Config()
        ai_engine = AITradingEngine(config)
        
        # Criar dados simulados para teste
        np.random.seed(42)
        n_samples = 200
        
        data = pd.DataFrame({
            'close': 50000 + np.cumsum(np.random.randn(n_samples) * 100),
            'volume': np.random.randint(1000, 10000, n_samples),
            'rsi': np.random.rand(n_samples) * 100,
            'macd': np.random.randn(n_samples),
            'bb_position': np.random.rand(n_samples)
        })
        
        # Testar preparação de features
        features = ai_engine.prepare_features(data)
        print(f"✅ Features preparadas - shape: {features.shape}")
        
        # Testar criação de labels
        labels = ai_engine.create_labels(data['close'])
        print(f"✅ Labels criadas - distribuição: {pd.Series(labels).value_counts().to_dict()}")
        
        print("✅ Motor de IA - Componentes básicos funcionando")
        
        return True
    except Exception as e:
        print(f"❌ Motor de IA - ERRO: {e}")
        return False

def test_signal_generation():
    """Testa a geração de sinais"""
    print("\n🎯 Testando geração de sinais...")
    
    try:
        from src.config import Config
        from src.ai_engine import AITradingEngine
        from src.market_data import MarketDataManager
        from src.signal_generator import SignalGenerator, Signal
        
        config = Config()
        ai_engine = AITradingEngine(config)
        market_data = MarketDataManager(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        # Testar criação de sinal
        test_signal = Signal(
            symbol='BTCUSDT',
            signal_type='BUY',
            confidence=0.85,
            entry_price=50000.0,
            stop_loss=48000.0,
            take_profit=54000.0,
            timeframe='1h',
            timestamp=datetime.now(),
            reasons=['RSI oversold', 'MACD bullish crossover', 'Price above MA20']
        )
        
        print(f"✅ Sinal criado: {test_signal.symbol} - {test_signal.signal_type} - Confiança: {test_signal.confidence}")
        print(f"✅ Entry: ${test_signal.entry_price} | SL: ${test_signal.stop_loss} | TP: ${test_signal.take_profit}")
        
        return True
    except Exception as e:
        print(f"❌ Geração de sinais - ERRO: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 TESTE DE COMPONENTES DO TRADING BOT AI")
    print("=" * 50)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_database,
        test_technical_indicators,
        test_ai_engine,
        test_signal_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Erro inesperado no teste: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS COMPONENTES ESTÃO FUNCIONANDO!")
        print("✅ O Trading Bot está pronto para gerar sinais!")
    else:
        print("⚠️ Alguns componentes precisam de atenção.")
        print("🔧 Verifique os erros acima e instale dependências faltantes.")
    
    print("=" * 50)
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)