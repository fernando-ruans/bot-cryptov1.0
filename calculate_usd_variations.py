#!/usr/bin/env python3
"""
Calcular variações em dólares para cada timeframe
"""

import sys
sys.path.append('.')

from src.signal_generator import SignalGenerator
from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine

def calculate_usd_variations():
    """Calcular variações em USD para todos os timeframes"""
    
    try:
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_gen = SignalGenerator(ai_engine, market_data)
        
        # Obter preço atual do BTC
        signal = signal_gen.generate_signal('BTCUSDT', '1h')
        current_price = signal.entry_price if signal else 110000
        
        print(f"💰 Preço atual BTC: ${current_price:.2f}")
        print("\n📊 Variação em Dólares por Timeframe:")
        print("=" * 60)
        print(f"{'TF':>4} | {'SL %':>6} | {'SL $':>8} | {'TP %':>6} | {'TP $':>8} | {'Total $':>8}")
        print("-" * 60)
        
        # Parâmetros por timeframe
        timeframes = {
            '1m': {'sl': 0.10, 'tp': 0.15},
            '5m': {'sl': 0.30, 'tp': 0.50},
            '15m': {'sl': 0.60, 'tp': 0.80},
            '30m': {'sl': 0.80, 'tp': 1.20},
            '1h': {'sl': 1.20, 'tp': 1.80},
            '2h': {'sl': 1.80, 'tp': 2.70},
            '4h': {'sl': 2.50, 'tp': 3.50},
            '1d': {'sl': 4.00, 'tp': 5.00}
        }
        
        for tf, values in timeframes.items():
            sl_usd = current_price * (values['sl'] / 100)
            tp_usd = current_price * (values['tp'] / 100)
            total_usd = sl_usd + tp_usd
            
            print(f"{tf:>4} | {values['sl']:>5.2f}% | ${sl_usd:>7.2f} | {values['tp']:>5.2f}% | ${tp_usd:>7.2f} | ${total_usd:>7.2f}")
        
        print("\n💡 Interpretação:")
        print("   - SL $: Valor em dólares que você pode perder")
        print("   - TP $: Valor em dólares que você pode ganhar")
        print("   - Total $: Variação total possível (SL + TP)")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        # Usar preço fixo se houver erro
        current_price = 110000
        print(f"\n💰 Usando preço fixo BTC: ${current_price:.2f}")
        
        timeframes = {
            '1m': {'sl': 0.10, 'tp': 0.15},
            '5m': {'sl': 0.30, 'tp': 0.50},
            '15m': {'sl': 0.60, 'tp': 0.80},
            '30m': {'sl': 0.80, 'tp': 1.20},
            '1h': {'sl': 1.20, 'tp': 1.80},
            '2h': {'sl': 1.80, 'tp': 2.70},
            '4h': {'sl': 2.50, 'tp': 3.50},
            '1d': {'sl': 4.00, 'tp': 5.00}
        }
        
        print("\n📊 Variação em Dólares por Timeframe:")
        print("=" * 60)
        print(f"{'TF':>4} | {'SL %':>6} | {'SL $':>8} | {'TP %':>6} | {'TP $':>8} | {'Total $':>8}")
        print("-" * 60)
        
        for tf, values in timeframes.items():
            sl_usd = current_price * (values['sl'] / 100)
            tp_usd = current_price * (values['tp'] / 100)
            total_usd = sl_usd + tp_usd
            
            print(f"{tf:>4} | {values['sl']:>5.2f}% | ${sl_usd:>7.2f} | {values['tp']:>5.2f}% | ${tp_usd:>7.2f} | ${total_usd:>7.2f}")

if __name__ == "__main__":
    calculate_usd_variations()