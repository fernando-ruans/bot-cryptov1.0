#!/usr/bin/env python3
"""
Debug específico para chamadas sequenciais ao SignalGenerator
Investigar por que a segunda chamada falha mesmo com cooldown = 0
"""

import logging
import sys
import time
from datetime import datetime

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from src.config import Config
from src.ai_engine import AITradingEngine
from src.market_data import MarketDataManager
from src.signal_generator import SignalGenerator

def debug_sequential_calls():
    """Debug detalhado de chamadas sequenciais"""
    print("=== DEBUG: CHAMADAS SEQUENCIAIS ===")
    
    try:
        # 1. Inicializar componentes
        print("1. Inicializando componentes...")
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        symbol = 'BTCUSDT'
        timeframe = '1h'
        
        print(f"   Cooldown configurado: {config.SIGNAL_CONFIG['signal_cooldown_minutes']} minutos")
        
        # 2. Estado inicial
        print("\n2. Estado inicial do SignalGenerator:")
        print(f"   Active signals: {len(signal_generator.active_signals)}")
        print(f"   Signal history: {len(signal_generator.signal_history)}")
        print(f"   Last signal time para {symbol}: {signal_generator.last_signal_time.get(symbol, 'N/A')}")
        
        # 3. Primeira chamada
        print(f"\n3. === PRIMEIRA CHAMADA ===")
        print(f"   Timestamp antes: {datetime.now()}")
        
        # Verificar cooldown antes
        is_cooldown_before = signal_generator._is_in_cooldown(symbol)
        print(f"   Em cooldown ANTES: {is_cooldown_before}")
        
        # Chamada 1
        signal1 = signal_generator.generate_signal(symbol, timeframe)
        
        print(f"   Timestamp após: {datetime.now()}")
        print(f"   Resultado: {signal1}")
        
        if signal1:
            print(f"   ✅ SUCESSO: {signal1.signal_type} com {signal1.confidence:.2f} confiança")
        else:
            print(f"   ❌ FALHOU: Nenhum sinal gerado")
        
        # Estado após primeira chamada
        print(f"\n   Estado após primeira chamada:")
        print(f"   Active signals: {len(signal_generator.active_signals)}")
        print(f"   Signal history: {len(signal_generator.signal_history)}")
        print(f"   Last signal time para {symbol}: {signal_generator.last_signal_time.get(symbol, 'N/A')}")
        
        # Verificar cooldown após
        is_cooldown_after = signal_generator._is_in_cooldown(symbol)
        print(f"   Em cooldown APÓS: {is_cooldown_after}")
        
        # 4. Pequena pausa (1 segundo)
        print(f"\n4. Aguardando 1 segundo...")
        time.sleep(1)
        
        # 5. Segunda chamada
        print(f"\n5. === SEGUNDA CHAMADA ===")
        print(f"   Timestamp antes: {datetime.now()}")
        
        # Verificar cooldown antes da segunda
        is_cooldown_before_2 = signal_generator._is_in_cooldown(symbol)
        print(f"   Em cooldown ANTES: {is_cooldown_before_2}")
        
        # Chamada 2
        signal2 = signal_generator.generate_signal(symbol, timeframe)
        
        print(f"   Timestamp após: {datetime.now()}")
        print(f"   Resultado: {signal2}")
        
        if signal2:
            print(f"   ✅ SUCESSO: {signal2.signal_type} com {signal2.confidence:.2f} confiança")
        else:
            print(f"   ❌ FALHOU: Nenhum sinal gerado")
        
        # Estado após segunda chamada
        print(f"\n   Estado após segunda chamada:")
        print(f"   Active signals: {len(signal_generator.active_signals)}")
        print(f"   Signal history: {len(signal_generator.signal_history)}")
        print(f"   Last signal time para {symbol}: {signal_generator.last_signal_time.get(symbol, 'N/A')}")
        
        # 6. Análise comparativa
        print(f"\n6. === ANÁLISE COMPARATIVA ===")
        print(f"   Primeira chamada: {'SUCESSO' if signal1 else 'FALHOU'}")
        print(f"   Segunda chamada: {'SUCESSO' if signal2 else 'FALHOU'}")
        
        if signal1 and not signal2:
            print(f"   🔍 PADRÃO DETECTADO: Primeira funciona, segunda falha!")
            print(f"   🔍 Possível causa: Estado interno do SignalGenerator sendo afetado")
            
            # Investigação mais profunda
            print(f"\n7. === INVESTIGAÇÃO PROFUNDA ===")
            
            # Verificar diferença de tempo
            if symbol in signal_generator.last_signal_time:
                time_diff = datetime.now() - signal_generator.last_signal_time[symbol]
                print(f"   Diferença de tempo desde último sinal: {time_diff.total_seconds():.2f} segundos")
                print(f"   Cooldown necessário: {config.SIGNAL_CONFIG['signal_cooldown_minutes'] * 60} segundos")
                
            # Verificar active_signals
            print(f"   Sinais ativos:")
            for signal_id, signal in signal_generator.active_signals.items():
                print(f"     - {signal_id}: {signal.symbol} {signal.signal_type}")
                
            # Tentar terceira chamada com reset de estado
            print(f"\n8. === TERCEIRA CHAMADA (RESET FORÇADO) ===")
            
            # Limpar last_signal_time para forçar reset
            if symbol in signal_generator.last_signal_time:
                del signal_generator.last_signal_time[symbol]
                print(f"   Last signal time removido")
            
            # Terceira chamada
            signal3 = signal_generator.generate_signal(symbol, timeframe)
            
            if signal3:
                print(f"   ✅ TERCEIRA SUCESSO: {signal3.signal_type} com {signal3.confidence:.2f} confiança")
                print(f"   🎯 CONFIRMADO: Problema é o estado interno (last_signal_time)")
            else:
                print(f"   ❌ TERCEIRA FALHOU: Mesmo com reset, ainda falha")
                print(f"   🔍 Problema pode ser mais profundo...")
        
        return {
            'primeira': signal1 is not None,
            'segunda': signal2 is not None,
            'terceira': signal3 is not None if 'signal3' in locals() else None
        }
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = debug_sequential_calls()
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Resultado do debug: {result}")
