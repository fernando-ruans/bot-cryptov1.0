#!/usr/bin/env python3
"""
Teste final de verificação
"""

import logging
import sys

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from src.ai_engine import AITradingEngine
from src.market_data import MarketDataManager
from src.signal_generator import SignalGenerator
from src.config import Config

def test_signal_generation():
    """Teste final da geração de sinais"""
    print("=== TESTE FINAL DE GERAÇÃO DE SINAIS ===")
    
    # Inicializar componentes
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    # Testar com diferentes símbolos
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
    
    for symbol in symbols:
        print(f"\n--- Testando {symbol} ---")
        
        try:
            # Limpar cooldown (hack para teste)
            if symbol in signal_generator.last_signal_time:
                del signal_generator.last_signal_time[symbol]
            
            signal = signal_generator.generate_signal(symbol, '1h')
            
            if signal:
                print(f"SUCESSO: Sinal {signal.signal_type} gerado para {symbol}")
                print(f"  Confiança: {signal.confidence:.2f}")
                print(f"  Preço: ${signal.entry_price:.2f}")
                print(f"  Stop Loss: ${signal.stop_loss:.2f}")
                print(f"  Take Profit: ${signal.take_profit:.2f}")
                print(f"  Razões: {signal.reasons[:3]}...")  # Primeiras 3 razões
                return True  # Sucesso, parar aqui
            else:
                print(f"FALHA: Nenhum sinal gerado para {symbol}")
                
        except Exception as e:
            print(f"ERRO: {e}")
    
    print("\n=== NENHUM SINAL FOI GERADO ===")
    return False

if __name__ == "__main__":
    success = test_signal_generation()
    if success:
        print("\n✓ CORREÇÃO FUNCIONANDO - SINAIS SENDO GERADOS!")
    else:
        print("\n❌ PROBLEMA PERSISTE - INVESTIGAÇÃO ADICIONAL NECESSÁRIA")
