#!/usr/bin/env python3

# Teste rápido de viés
import sys
sys.path.append('.')

try:
    from src.signal_generator import SignalGenerator
    from src.ai_engine import AITradingEngine
    from src.market_data import MarketDataManager
    from src.config import Config
    
    print("=== TESTE RÁPIDO DE VIÉS ===")
    
    config = Config()
    # Reduzir limites para forçar sinais
    config.SIGNAL_CONFIG['min_ai_confidence'] = 0.01
    config.SIGNAL_CONFIG['min_market_score'] = 0.01
    
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    # Teste com 3 símbolos
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
    timeframe = '1h'
    
    buy_count = 0
    sell_count = 0
    hold_count = 0
    
    for symbol in symbols:
        try:
            signal = signal_generator.generate_signal(symbol, timeframe)
            if signal:
                if signal.signal_type == 'buy':
                    buy_count += 1
                    print(f"{symbol}: BUY ({signal.confidence:.2f})")
                elif signal.signal_type == 'sell':
                    sell_count += 1
                    print(f"{symbol}: SELL ({signal.confidence:.2f})")
                else:
                    hold_count += 1
                    print(f"{symbol}: HOLD")
            else:
                hold_count += 1
                print(f"{symbol}: HOLD (None)")
        except Exception as e:
            print(f"{symbol}: ERRO - {e}")
    
    print(f"\nResultados:")
    print(f"BUY: {buy_count}, SELL: {sell_count}, HOLD: {hold_count}")
    
    if sell_count == 0 and buy_count > 0:
        print("🚨 VIÉS DETECTADO: Apenas sinais de compra!")
    elif buy_count == 0 and sell_count > 0:
        print("🚨 VIÉS DETECTADO: Apenas sinais de venda!")
    else:
        print("✅ Sinais balanceados")
        
except Exception as e:
    print(f"Erro no teste: {e}")
    import traceback
    traceback.print_exc()
