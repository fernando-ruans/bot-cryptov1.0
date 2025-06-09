#!/usr/bin/env python3
"""
Teste simples da correção
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from src.ai_engine import AITradingEngine
from src.market_data import MarketDataManager
from src.signal_generator import SignalGenerator
from src.config import Config

def test_fix():
    print("Testando correcao...")
    
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    symbol = 'BTCUSDT'
    timeframe = '1h'
    
    signal = signal_generator.generate_signal(symbol, timeframe)
    
    if signal is None:
        print("Nenhum sinal gerado ainda")
        
        # Teste direto da análise técnica
        df = market_data.get_historical_data(symbol, timeframe, 100)
        if df is not None:
            df = signal_generator.technical_indicators.calculate_all_indicators(df)
            result = signal_generator._analyze_technical_indicators(df)
            print(f"Análise técnica: {result['signal']} (conf: {result['confidence']:.2f})")
            print(f"Buy strength: {result.get('buy_strength', 0):.2f}")
            print(f"Sell strength: {result.get('sell_strength', 0):.2f}")
    else:
        print(f"Sinal gerado: {signal.signal_type} (conf: {signal.confidence:.2f})")

if __name__ == "__main__":
    test_fix()
