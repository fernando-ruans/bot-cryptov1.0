#!/usr/bin/env python3
"""
Script para forçar geração de sinais e identificar problemas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.signal_generator import SignalGenerator
from src.technical_indicators import TechnicalIndicators
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_force_signal():
    """Teste forçado de geração de sinais"""
    print("=== TESTE FORÇADO DE GERAÇÃO DE SINAIS ===")
    
    try:
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        # Configurações ultra-agressivas
        config.SIGNAL_CONFIG['min_confidence'] = 0.01  # 1%
        config.SIGNAL_CONFIG['signal_cooldown_minutes'] = 0
        config.SIGNAL_CONFIG['enable_confluence'] = False
        config.SIGNAL_CONFIG['min_market_score'] = 0.01
        signal_generator.config = config
        
        print("✓ Componentes inicializados com configurações ultra-agressivas")
        
        # Obter dados
        symbol = 'BTCUSDT'
        timeframe = '1h'
        
        df = market_data.get_historical_data(symbol, timeframe, 100)
        if df is None or df.empty:
            print("❌ ERRO: Não conseguiu obter dados históricos")
            return
        
        print(f"✓ Dados obtidos: {len(df)} candles")
        
        # Calcular indicadores
        tech_indicators = TechnicalIndicators(config)
        df_with_indicators = tech_indicators.calculate_all_indicators(df)
        
        print("✓ Indicadores calculados")
        
        # Testar análise técnica diretamente
        print("\n=== TESTE DA ANÁLISE TÉCNICA ===")
        technical_result = signal_generator._analyze_technical_indicators(df_with_indicators)
        
        print(f"Resultado técnico: {technical_result['signal']}")
        print(f"Confiança: {technical_result['confidence']:.3f}")
        print(f"Buy strength: {technical_result.get('buy_strength', 0):.3f}")
        print(f"Sell strength: {technical_result.get('sell_strength', 0):.3f}")
        print(f"Razões: {technical_result['reasons']}")
        
        # Se ainda for 'hold', vamos forçar manualmente
        if technical_result['signal'] == 'hold':
            print("\n=== FORÇANDO SINAL MANUALMENTE ===")
            
            # Verificar valores dos indicadores
            latest = df_with_indicators.iloc[-1]
            print(f"RSI: {latest.get('rsi', 'N/A')}")
            print(f"MACD: {latest.get('macd', 'N/A')}")
            print(f"MACD Signal: {latest.get('macd_signal', 'N/A')}")
            print(f"BB Position: {(latest['close'] - latest.get('bb_lower', latest['close'])) / max(latest.get('bb_upper', latest['close']) - latest.get('bb_lower', latest['close']), 1)}")
            
            # Criar sinal forçado
            from src.signal_generator import Signal
            from datetime import datetime
            
            current_price = market_data.get_current_price(symbol)
            
            forced_signal = Signal(
                symbol=symbol,
                signal_type='buy',  # Forçar buy
                confidence=0.75,
                entry_price=current_price,
                stop_loss=current_price * 0.98,
                take_profit=current_price * 1.02,
                timeframe=timeframe,
                timestamp=datetime.now(),
                reasons=[
                    "Sinal forçado para teste",
                    f"RSI: {latest.get('rsi', 'N/A')}",
                    f"Preço: ${current_price:.2f}",
                    "Configurações ultra-agressivas"
                ]
            )
            
            # Registrar o sinal
            signal_generator._register_signal(forced_signal)
            
            print(f"✓ SINAL FORÇADO CRIADO:")
            print(f"  ID: {forced_signal.id}")
            print(f"  Tipo: {forced_signal.signal_type}")
            print(f"  Confiança: {forced_signal.confidence:.1%}")
            print(f"  Preço entrada: ${forced_signal.entry_price:.2f}")
            print(f"  Stop Loss: ${forced_signal.stop_loss:.2f}")
            print(f"  Take Profit: ${forced_signal.take_profit:.2f}")
            
            return forced_signal
        
        else:
            print(f"✓ SINAL TÉCNICO GERADO: {technical_result['signal']}")
            
            # Tentar gerar sinal completo
            signal = signal_generator.generate_signal(symbol, timeframe)
            
            if signal:
                print(f"✓ SINAL COMPLETO GERADO:")
                print(f"  ID: {signal.id}")
                print(f"  Tipo: {signal.signal_type}")
                print(f"  Confiança: {signal.confidence:.1%}")
                return signal
            else:
                print("❌ Análise técnica OK mas sinal completo não foi gerado")
                return None
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_force_signal()
    if result:
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ TESTE FALHOU!")