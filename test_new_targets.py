#!/usr/bin/env python3
"""
Teste dos novos alvos de stop loss e take profit ajustados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.signal_generator import SignalGenerator
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_new_targets():
    """Testar os novos alvos ajustados"""
    print("=== TESTE DOS NOVOS ALVOS AJUSTADOS ===")
    
    try:
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        # Limpar cooldown
        signal_generator.last_signal_time = {}
        
        # Timeframes para testar
        timeframes = ['1m', '5m', '15m', '30m', '1h', '2h', '4h']
        symbol = 'BTCUSDT'
        
        print(f"\n📊 Testando alvos para {symbol}")
        print("=" * 60)
        
        # Preço simulado do BTC
        btc_price = 100000  # $100k para facilitar cálculos
        
        for timeframe in timeframes:
            print(f"\n🕒 Timeframe: {timeframe}")
            print("-" * 30)
            
            try:
                # Testar método 1:1 (atual)
                levels_1to1 = signal_generator._calculate_trade_levels_1to1(
                    btc_price, 'buy', timeframe
                )
                
                sl_distance = btc_price - levels_1to1['stop_loss']
                tp_distance = levels_1to1['take_profit'] - btc_price
                
                print(f"💰 Método 1:1:")
                print(f"   Entry: ${btc_price:,.2f}")
                print(f"   Stop Loss: ${levels_1to1['stop_loss']:,.2f} (-${sl_distance:,.2f})")
                print(f"   Take Profit: ${levels_1to1['take_profit']:,.2f} (+${tp_distance:,.2f})")
                print(f"   Percentual SL: {(sl_distance/btc_price)*100:.2f}%")
                print(f"   Percentual TP: {(tp_distance/btc_price)*100:.2f}%")                # Verificar se é realista para o timeframe (critérios finais ajustados)
                if timeframe in ['1m', '5m', '15m']:
                    if sl_distance < 10 or tp_distance < 10:
                        print("   ⚠️  Alvos muito próximos - pode ser difícil de executar")
                    elif sl_distance > 200 or tp_distance > 200:
                        print("   ⚠️  Alvos muito distantes para timeframe curto")
                    else:
                        print("   ✅ Alvos apropriados para timeframe curto")
                elif timeframe in ['30m', '1h', '2h']:
                    if sl_distance < 50 or tp_distance < 50:
                        print("   ⚠️  Alvos muito próximos para timeframe médio")
                    elif sl_distance > 500 or tp_distance > 500:
                        print("   ⚠️  Alvos muito distantes para timeframe médio")
                    else:
                        print("   ✅ Alvos apropriados para timeframe médio")
                else:
                    if sl_distance < 200 or tp_distance < 200:
                        print("   ⚠️  Alvos muito próximos para timeframe longo")
                    else:
                        print("   ✅ Alvos apropriados para timeframe longo")
                
            except Exception as e:
                print(f"   ❌ Erro ao calcular alvos: {e}")
        
        print(f"\n" + "=" * 60)
        print("✅ Teste dos novos alvos concluído!")
        
        # Teste adicional: gerar um sinal real
        print(f"\n🚀 Teste de geração de sinal real com novos alvos:")
        signal = signal_generator.generate_signal(symbol, '1h')
        
        if signal:
            print(f"✅ Sinal gerado: {signal.signal_type}")
            print(f"   Símbolo: {signal.symbol}")
            print(f"   Confiança: {signal.confidence:.2%}")
            print(f"   Entry: ${signal.entry_price:,.2f}")
            print(f"   Stop Loss: ${signal.stop_loss:,.2f}")
            print(f"   Take Profit: ${signal.take_profit:,.2f}")
            
            # Calcular distâncias
            if signal.signal_type == 'buy':
                sl_dist = signal.entry_price - signal.stop_loss
                tp_dist = signal.take_profit - signal.entry_price
            else:
                sl_dist = signal.stop_loss - signal.entry_price
                tp_dist = signal.entry_price - signal.take_profit
            
            print(f"   Distância SL: ${sl_dist:,.2f} ({(sl_dist/signal.entry_price)*100:.2f}%)")
            print(f"   Distância TP: ${tp_dist:,.2f} ({(tp_dist/signal.entry_price)*100:.2f}%)")
            
        else:
            print("❌ Nenhum sinal gerado")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_targets()
