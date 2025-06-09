#!/usr/bin/env python3
"""
Método de teste para forçar geração de sinais
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.signal_generator import SignalGenerator
from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from datetime import datetime

def create_test_signal():
    """Criar um sinal de teste forçado"""
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    # Obter preço atual
    current_price = market_data.get_current_price('BTCUSDT')
    if current_price is None:
        current_price = 45000  # Fallback
    
    # Importar classe Signal
    from src.signal_generator import Signal
    
    # Criar sinal forçado
    test_signal = Signal(
        symbol='BTCUSDT',
        signal_type='buy',
        confidence=0.85,
        entry_price=current_price,
        stop_loss=current_price * 0.98,
        take_profit=current_price * 1.04,
        timeframe='1h',
        timestamp=datetime.now(),
        reasons=['Sinal de teste forçado', 'RSI oversold simulado', 'Volume alto simulado']
    )
    
    # Registrar o sinal
    signal_generator._register_signal(test_signal)
    
    print(f"Sinal de teste criado: {test_signal.to_dict()}")
    
    # Verificar se foi registrado
    active_signals = signal_generator.get_active_signals()
    print(f"Sinais ativos após criação: {len(active_signals)}")
    
    return test_signal

if __name__ == "__main__":
    create_test_signal()
