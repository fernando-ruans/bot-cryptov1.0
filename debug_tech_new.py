#!/usr/bin/env python3
"""
Debug específico da análise técnica para encontrar por que nunca gera SELL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.signal_generator import SignalGenerator
import logging
import pandas as pd

# Configurar log para mostrar apenas info importante
logging.getLogger().setLevel(logging.ERROR)

def debug_technical_analysis():
    """Debug específico da análise técnica"""
    print("=== DEBUG: ANÁLISE TÉCNICA DETALHADA ===")
    
    # Configurar componentes
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    symbol = 'BTCUSDT'
    timeframe = '1h'
    
    # Obter dados
    df = market_data.get_historical_data(symbol, timeframe, 500)
    df = signal_generator.technical_indicators.calculate_all_indicators(df)
    
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    print(f"Analisando {symbol} {timeframe}...")
    print(f"Dados: {len(df)} registros")
    print()
    
    # Analisar indicadores individualmente
    print("=== INDICADORES INDIVIDUAIS ===")
    
    # RSI
    if 'rsi' in latest and not pd.isna(latest['rsi']):
        rsi = latest['rsi']
        print(f"RSI: {rsi:.1f}")
        if rsi < 35:
            print(f"  → BUY (RSI oversold: {rsi:.1f})")
        elif rsi > 65:
            print(f"  → SELL (RSI overbought: {rsi:.1f})")
        elif 35 <= rsi <= 50:
            print(f"  → BUY zone (RSI: {rsi:.1f})")
        elif 50 <= rsi <= 65:
            print(f"  → SELL zone (RSI: {rsi:.1f})")
        else:
            print(f"  → Neutro")
    
    # MACD
    if ('macd' in latest and 'macd_signal' in latest and 
        not pd.isna(latest['macd']) and not pd.isna(latest['macd_signal'])):
        macd = latest['macd']
        macd_signal = latest['macd_signal']
        prev_macd = prev['macd'] if 'macd' in prev else macd
        prev_macd_signal = prev['macd_signal'] if 'macd_signal' in prev else macd_signal
        
        print(f"MACD: {macd:.3f} vs Signal: {macd_signal:.3f}")
        
        if macd > macd_signal:
            if prev_macd <= prev_macd_signal:
                print(f"  → BUY (MACD bullish crossover)")
            else:
                print(f"  → BUY (MACD above signal)")
        elif macd < macd_signal:
            if prev_macd >= prev_macd_signal:
                print(f"  → SELL (MACD bearish crossover)")
            else:
                print(f"  → SELL (MACD below signal)")
    
    # EMA
    if 'ema_12' in latest and 'ema_26' in latest:
        ema_12 = latest['ema_12']
        ema_26 = latest['ema_26']
        prev_ema_12 = prev['ema_12'] if 'ema_12' in prev else ema_12
        prev_ema_26 = prev['ema_26'] if 'ema_26' in prev else ema_26
        
        print(f"EMA 12: {ema_12:.2f} vs EMA 26: {ema_26:.2f}")
        
        if ema_12 > ema_26:
            if prev_ema_12 <= prev_ema_26:
                print(f"  → BUY (EMA 12/26 bullish crossover)")
            else:
                print(f"  → BUY (EMA 12 above EMA 26)")
        else:
            if prev_ema_12 >= prev_ema_26:
                print(f"  → SELL (EMA 12/26 bearish crossover)")
            else:
                print(f"  → SELL (EMA 12 below EMA 26)")
    
    # Bollinger Bands
    if ('bb_lower' in latest and 'bb_upper' in latest and 
        not pd.isna(latest['bb_lower']) and not pd.isna(latest['bb_upper'])):
        bb_lower = latest['bb_lower']
        bb_upper = latest['bb_upper']
        close = latest['close']
        
        bb_position = (close - bb_lower) / (bb_upper - bb_lower)
        print(f"Bollinger Position: {bb_position:.2f} (0=lower, 1=upper)")
        
        if bb_position <= 0.2:
            print(f"  → BUY (Price near lower BB)")
        elif bb_position >= 0.8:
            print(f"  → SELL (Price near upper BB)")
        elif bb_position <= 0.4:
            print(f"  → BUY zone (Lower BB zone)")
        elif bb_position >= 0.6:
            print(f"  → SELL zone (Upper BB zone)")
    
    # Stochastic
    if ('stoch_k' in latest and 'stoch_d' in latest and 
        not pd.isna(latest['stoch_k']) and not pd.isna(latest['stoch_d'])):
        stoch_k = latest['stoch_k']
        stoch_d = latest['stoch_d']
        
        print(f"Stochastic K: {stoch_k:.1f}, D: {stoch_d:.1f}")
        
        if stoch_k < 25:
            if stoch_k > stoch_d:
                print(f"  → BUY (Stochastic oversold with bullish signal)")
            else:
                print(f"  → BUY zone (Stochastic oversold)")
        elif stoch_k > 75:
            if stoch_k < stoch_d:
                print(f"  → SELL (Stochastic overbought with bearish signal)")
            else:
                print(f"  → SELL zone (Stochastic overbought)")
    
    print()
    
    # Executar análise técnica completa
    print("=== ANÁLISE TÉCNICA COMPLETA ===")
    tech_result = signal_generator._analyze_technical_indicators(df)
    
    print(f"Resultado final: {tech_result['signal']}")
    print(f"Confiança: {tech_result['confidence']:.3f}")
    print(f"Buy strength: {tech_result.get('buy_strength', 'N/A')}")
    print(f"Sell strength: {tech_result.get('sell_strength', 'N/A')}")
    
    print(f"\nRazões ({len(tech_result['reasons'])}):")
    for i, reason in enumerate(tech_result['reasons'][:10]):
        print(f"  {i+1}. {reason}")
    
    # Análise de forças
    print()
    print("=== ANÁLISE DE FORÇAS ===")
    
    # Contar sinais de buy vs sell manualmente
    buy_signals = [reason for reason in tech_result['reasons'] if any(word in reason.lower() for word in ['buy', 'bullish', 'above', 'oversold'])]
    sell_signals = [reason for reason in tech_result['reasons'] if any(word in reason.lower() for word in ['sell', 'bearish', 'below', 'overbought'])]
    
    print(f"Razões de BUY ({len(buy_signals)}):")
    for reason in buy_signals:
        print(f"  • {reason}")
    
    print(f"\nRazões de SELL ({len(sell_signals)}):")
    for reason in sell_signals:
        print(f"  • {reason}")
    
    # Diagnóstico
    print()
    print("=== DIAGNÓSTICO ===")
    
    if len(sell_signals) == 0:
        print("🚨 PROBLEMA: Nenhuma razão de SELL encontrada!")
        print("   Isso explica por que sell_score sempre é 0")
    elif len(buy_signals) > len(sell_signals) * 3:
        print("⚠️  DESEQUILÍBRIO: Muito mais sinais de BUY que SELL")
    else:
        print("✓ Sinais técnicos parecem balanceados")
    
    print()
    print("=== SUGESTÕES ===")
    print("1. Verificar se os indicadores estão configurados corretamente")
    print("2. Testar em diferentes condições de mercado (alta/baixa)")
    print("3. Ajustar thresholds dos indicadores técnicos")

if __name__ == "__main__":
    debug_technical_analysis()
