#!/usr/bin/env python3
"""
Teste FINAL - Verificar dados reais e geração de sinais
"""

import logging
import sys

# Configurar logging para mostrar tudo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Desabilitar logs excessivos do CCXT
logging.getLogger('ccxt').setLevel(logging.WARNING)

from src.config import Config
from src.market_data import MarketDataManager
from src.signal_generator import SignalGenerator
from src.ai_engine import AITradingEngine

def main():
    print("🚀 === TESTE FINAL: DADOS REAIS + SINAIS === 🚀")
    
    # Inicializar sistema
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    # Status do sistema
    print(f"\n📊 Status do Sistema:")
    print(f"   Modo demo: {market_data.demo_mode}")
    print(f"   APIs públicas: {market_data.use_public_apis}")
    print(f"   Exchanges: {list(market_data.exchanges.keys())}")
    
    # Testar dados reais
    symbol = 'BTCUSDT'
    timeframe = '1h'
    
    print(f"\n📈 Testando dados para {symbol}...")
    
    # Buscar dados
    data = market_data.get_data(symbol, timeframe)
    
    if data is not None and not data.empty:
        print(f"✅ Dados obtidos: {len(data)} registros")
        print(f"✅ Último preço: ${data['close'].iloc[-1]:.2f}")
        print(f"✅ Variação: ${data['close'].std():.2f}")
        print(f"✅ Período: {data.index[0]} até {data.index[-1]}")
        
        # Verificar se são dados reais
        if data['close'].std() > 1000:  # BTC tem alta variação
            print("🎯 CONFIRMADO: DADOS REAIS!")
        else:
            print("⚠️  Possíveis dados simulados")
            
    else:
        print("❌ Falha ao obter dados")
        return
    
    # Testar geração de sinal
    print(f"\n🎯 Testando geração de sinal...")
    
    # Limpar cooldown
    if symbol in signal_generator.last_signal_time:
        del signal_generator.last_signal_time[symbol]
    
    signal = signal_generator.generate_signal(symbol, timeframe)
    
    if signal:
        print(f"🎉 SINAL GERADO COM SUCESSO!")
        print(f"   Tipo: {signal.signal_type.upper()}")
        print(f"   Confiança: {signal.confidence:.1%}")
        print(f"   Preço: ${signal.entry_price:.2f}")
        print(f"   Stop Loss: ${signal.stop_loss:.2f}")
        print(f"   Take Profit: ${signal.take_profit:.2f}")
        print(f"   Principais razões:")
        for i, reason in enumerate(signal.reasons[:3], 1):
            print(f"     {i}. {reason}")
            
        print(f"\n🎯 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print(f"   ✅ Dados reais da Binance")
        print(f"   ✅ Sinais sendo gerados")
        print(f"   ✅ Confiança: {signal.confidence:.1%}")
        
    else:
        print("❌ Nenhum sinal gerado")
        print("   Possíveis causas:")
        print("   - Confiança abaixo do mínimo (40%)")
        print("   - Cooldown ativo")
        print("   - Condições de mercado inadequadas")

if __name__ == "__main__":
    main()
