#!/usr/bin/env python3
"""
Debug específico da análise técnica
"""

import logging
import sys
import pandas as pd

# Configurar logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])

from src.ai_engine import AITradingEngine
from src.market_data import MarketDataManager
from src.signal_generator import SignalGenerator
from src.config import Config

def debug_technical_analysis():
    """Debug detalhado da análise técnica"""
    print("=== DEBUG ANÁLISE TÉCNICA ===")
    
    # Inicializar componentes
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    # Obter dados
    symbol = 'BTCUSDT'
    timeframe = '1h'
    df = market_data.get_historical_data(symbol, timeframe, 100)
    
    if df is None or df.empty:
        print("❌ Dados não disponíveis")
        return
    
    print(f"✓ Dados obtidos: {len(df)} registros")
    
    # Calcular indicadores
    df = signal_generator.technical_indicators.calculate_all_indicators(df)
    print("✓ Indicadores calculados")
    
    # Análise técnica COM DEBUG
    print("\n=== ANÁLISE TÉCNICA DETALHADA ===")
    
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    signals = []
    reasons = []
    
    print(f"Último registro:")
    print(f"  Close: {latest['close']:.2f}")
    print(f"  RSI: {latest.get('rsi', 'N/A')}")
    print(f"  MACD: {latest.get('macd', 'N/A')}")
    print(f"  MACD Signal: {latest.get('macd_signal', 'N/A')}")
    print(f"  EMA 12: {latest.get('ema_12', 'N/A')}")
    print(f"  EMA 26: {latest.get('ema_26', 'N/A')}")
    print(f"  ADX: {latest.get('adx', 'N/A')}")
    
    print(f"\n=== AVALIAÇÃO DE SINAIS ===")
    
    # RSI Analysis
    if 'rsi' in latest and not pd.isna(latest['rsi']):
        rsi = latest['rsi']
        print(f"RSI: {rsi:.1f}")
        if rsi < 35:
            signals.append(('buy', 0.7))
            reasons.append(f"RSI oversold: {rsi:.1f}")
            print(f"  → BUY (0.7): RSI oversold")
        elif rsi > 65:
            signals.append(('sell', 0.7))
            reasons.append(f"RSI overbought: {rsi:.1f}")
            print(f"  → SELL (0.7): RSI overbought")
        elif 35 <= rsi <= 50:
            signals.append(('buy', 0.4))
            reasons.append(f"RSI in buy zone: {rsi:.1f}")
            print(f"  → BUY (0.4): RSI in buy zone")
        elif 50 <= rsi <= 65:
            signals.append(('sell', 0.4))
            reasons.append(f"RSI in sell zone: {rsi:.1f}")
            print(f"  → SELL (0.4): RSI in sell zone")
        else:
            print(f"  → HOLD: RSI neutro")
    
    # MACD Analysis
    if ('macd' in latest and 'macd_signal' in latest and
        not pd.isna(latest['macd']) and not pd.isna(latest['macd_signal'])):
        
        macd = latest['macd']
        macd_signal = latest['macd_signal']
        print(f"MACD: {macd:.4f}, Signal: {macd_signal:.4f}")
        
        if macd > macd_signal:
            if len(df) > 1 and prev['macd'] <= prev['macd_signal']:
                signals.append(('buy', 0.8))
                reasons.append("MACD bullish crossover")
                print(f"  → BUY (0.8): MACD bullish crossover")
            else:
                signals.append(('buy', 0.5))
                reasons.append("MACD above signal line")
                print(f"  → BUY (0.5): MACD above signal line")
        elif macd < macd_signal:
            if len(df) > 1 and prev['macd'] >= prev['macd_signal']:
                signals.append(('sell', 0.8))
                reasons.append("MACD bearish crossover")
                print(f"  → SELL (0.8): MACD bearish crossover")
            else:
                signals.append(('sell', 0.5))
                reasons.append("MACD below signal line")
                print(f"  → SELL (0.5): MACD below signal line")
    
    # EMA Analysis
    if 'ema_12' in latest and 'ema_26' in latest:
        if not pd.isna(latest['ema_12']) and not pd.isna(latest['ema_26']):
            ema12 = latest['ema_12']
            ema26 = latest['ema_26']
            print(f"EMA 12: {ema12:.2f}, EMA 26: {ema26:.2f}")
            
            if ema12 > ema26:
                if len(df) > 1 and prev['ema_12'] <= prev['ema_26']:
                    signals.append(('buy', 0.7))
                    reasons.append("EMA 12/26 bullish crossover")
                    print(f"  → BUY (0.7): EMA bullish crossover")
                else:
                    signals.append(('buy', 0.4))
                    reasons.append("EMA 12 above EMA 26")
                    print(f"  → BUY (0.4): EMA 12 above EMA 26")
            else:
                if len(df) > 1 and prev['ema_12'] >= prev['ema_26']:
                    signals.append(('sell', 0.7))
                    reasons.append("EMA 12/26 bearish crossover")
                    print(f"  → SELL (0.7): EMA bearish crossover")
                else:
                    signals.append(('sell', 0.4))
                    reasons.append("EMA 12 below EMA 26")
                    print(f"  → SELL (0.4): EMA 12 below EMA 26")
    
    # ADX Analysis
    if 'adx' in latest and not pd.isna(latest['adx']):
        adx = latest['adx']
        print(f"ADX: {adx:.1f}")
        if adx > 20:
            if 'adx_pos' in latest and 'adx_neg' in latest:
                if not pd.isna(latest['adx_pos']) and not pd.isna(latest['adx_neg']):
                    adx_pos = latest['adx_pos']
                    adx_neg = latest['adx_neg']
                    print(f"  ADX+: {adx_pos:.2f}, ADX-: {adx_neg:.2f}")
                    if adx_pos > adx_neg:
                        signals.append(('buy', 0.5))
                        reasons.append(f"Uptrend detected (ADX: {adx:.1f})")
                        print(f"  → BUY (0.5): Uptrend detected")
                    else:
                        signals.append(('sell', 0.5))
                        reasons.append(f"Downtrend detected (ADX: {adx:.1f})")
                        print(f"  → SELL (0.5): Downtrend detected")
    
    print(f"\n=== RESUMO DOS SINAIS ===")
    print(f"Total de sinais encontrados: {len(signals)}")
    for i, (signal_type, strength) in enumerate(signals):
        print(f"  {i+1}. {signal_type.upper()} ({strength}): {reasons[i] if i < len(reasons) else 'N/A'}")
    
    # Calcular forças
    buy_signals = [s[1] for s in signals if s[0] == 'buy']
    sell_signals = [s[1] for s in signals if s[0] == 'sell']
    
    buy_strength = sum(buy_signals)
    sell_strength = sum(sell_signals)
    
    print(f"\n=== CÁLCULO FINAL ===")
    print(f"Buy signals: {buy_signals} → Soma: {buy_strength:.2f}")
    print(f"Sell signals: {sell_signals} → Soma: {sell_strength:.2f}")
    print(f"Limiar necessário: 0.6")
    
    # Determinar sinal final
    if buy_strength > sell_strength and buy_strength > 0.6:
        signal_type = 'buy'
        confidence = min(buy_strength / 2.5, 1.0)
        print(f"✓ RESULTADO: BUY (confiança: {confidence:.2f})")
    elif sell_strength > buy_strength and sell_strength > 0.6:
        signal_type = 'sell'
        confidence = min(sell_strength / 2.5, 1.0)
        print(f"✓ RESULTADO: SELL (confiança: {confidence:.2f})")
    else:
        signal_type = 'hold'
        confidence = 0.0
        print(f"❌ RESULTADO: HOLD (confiança: {confidence:.2f})")
        print(f"   Motivo: Nenhuma força atinge o limiar de 0.6")

if __name__ == "__main__":
    debug_technical_analysis()
