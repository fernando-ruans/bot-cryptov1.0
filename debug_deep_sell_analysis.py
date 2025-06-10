#!/usr/bin/env python3
"""
Debug MUITO PROFUNDO: Investigar por que não há sinais SELL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.signal_generator import SignalGenerator
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.config import Config
import traceback

def debug_deep_signal_generation():
    print("=== DEBUG PROFUNDO: POR QUE NÃO HÁ SINAIS SELL? ===")
    
    symbol = "BTCUSDT"
    timeframe = "1h"
    
    try:
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_gen = SignalGenerator(ai_engine, market_data)
        
        # Obter dados
        data = market_data.get_historical_data(symbol, timeframe, 100)
        if data is None or data.empty:
            print("❌ Nenhum dado obtido")
            return
            
        print(f"✅ Dados obtidos: {len(data)} registros")
        
        # Calcular indicadores
        data_with_indicators = signal_gen.technical_indicators.calculate_all_indicators(data.copy())
        print(f"✅ Indicadores calculados: {len(data_with_indicators.columns)} colunas")
        
        # Debug da análise técnica PASSO A PASSO
        print(f"\n🔍 ANÁLISE TÉCNICA DETALHADA PASSO A PASSO:")
        print(f"=" * 60)
        
        latest = data_with_indicators.iloc[-1]
        prev = data_with_indicators.iloc[-2] if len(data_with_indicators) > 1 else latest
        signals = []
        reasons = []
        
        print(f"📊 DADOS ATUAIS:")
        print(f"   Close: {latest['close']:.2f}")
        print(f"   RSI: {latest.get('rsi', 'N/A')}")
        print(f"   MACD: {latest.get('macd', 'N/A')}")
        print(f"   MACD Signal: {latest.get('macd_signal', 'N/A')}")
        print(f"   EMA 12: {latest.get('ema_12', 'N/A')}")
        print(f"   EMA 26: {latest.get('ema_26', 'N/A')}")
        print(f"   BB Lower: {latest.get('bb_lower', 'N/A')}")
        print(f"   BB Upper: {latest.get('bb_upper', 'N/A')}")
        
        # 1. RSI Analysis
        print(f"\n1️⃣ ANÁLISE RSI:")
        if 'rsi' in latest and not pd.isna(latest['rsi']):
            rsi = latest['rsi']
            print(f"   RSI = {rsi:.1f}")
            
            if rsi < 35:
                signals.append(('buy', 0.7))
                reasons.append(f"RSI oversold: {rsi:.1f}")
                print(f"   ✅ BUY: RSI oversold ({rsi:.1f} < 35)")
            elif rsi > 65:
                signals.append(('sell', 0.7))
                reasons.append(f"RSI overbought: {rsi:.1f}")
                print(f"   ✅ SELL: RSI overbought ({rsi:.1f} > 65)")
            elif 35 <= rsi <= 50:
                signals.append(('buy', 0.4))
                reasons.append(f"RSI in buy zone: {rsi:.1f}")
                print(f"   ⚠️  BUY: RSI in buy zone ({rsi:.1f})")
            elif 50 <= rsi <= 65:
                signals.append(('sell', 0.4))
                reasons.append(f"RSI in sell zone: {rsi:.1f}")
                print(f"   ⚠️  SELL: RSI in sell zone ({rsi:.1f})")
            else:
                print(f"   ❌ HOLD: RSI neutro ({rsi:.1f})")
        else:
            print(f"   ❌ RSI não disponível")
        
        # 2. MACD Analysis
        print(f"\n2️⃣ ANÁLISE MACD:")
        if ('macd' in latest and 'macd_signal' in latest and 
            not pd.isna(latest['macd']) and not pd.isna(latest['macd_signal'])):
            
            macd = latest['macd']
            macd_signal = latest['macd_signal']
            print(f"   MACD = {macd:.4f}, Signal = {macd_signal:.4f}")
            
            if macd > macd_signal:
                if len(data_with_indicators) > 1 and prev['macd'] <= prev['macd_signal']:
                    signals.append(('buy', 0.8))
                    reasons.append("MACD bullish crossover")
                    print(f"   ✅ BUY: MACD bullish crossover")
                else:
                    signals.append(('buy', 0.5))
                    reasons.append("MACD above signal line")
                    print(f"   ⚠️  BUY: MACD above signal line")
            elif macd < macd_signal:
                if len(data_with_indicators) > 1 and prev['macd'] >= prev['macd_signal']:
                    signals.append(('sell', 0.8))
                    reasons.append("MACD bearish crossover")
                    print(f"   ✅ SELL: MACD bearish crossover")
                else:
                    signals.append(('sell', 0.5))
                    reasons.append("MACD below signal line")
                    print(f"   ⚠️  SELL: MACD below signal line")
            else:
                print(f"   ❌ HOLD: MACD neutro")
        else:
            print(f"   ❌ MACD não disponível")
        
        # 3. EMA Analysis
        print(f"\n3️⃣ ANÁLISE EMA:")
        if 'ema_12' in latest and 'ema_26' in latest:
            if not pd.isna(latest['ema_12']) and not pd.isna(latest['ema_26']):
                ema12 = latest['ema_12']
                ema26 = latest['ema_26']
                print(f"   EMA 12 = {ema12:.2f}, EMA 26 = {ema26:.2f}")
                
                if ema12 > ema26:
                    if len(data_with_indicators) > 1 and prev['ema_12'] <= prev['ema_26']:
                        signals.append(('buy', 0.7))
                        reasons.append("EMA 12/26 bullish crossover")
                        print(f"   ✅ BUY: EMA bullish crossover")
                    else:
                        signals.append(('buy', 0.4))
                        reasons.append("EMA 12 above EMA 26")
                        print(f"   ⚠️  BUY: EMA 12 above EMA 26")
                else:
                    if len(data_with_indicators) > 1 and prev['ema_12'] >= prev['ema_26']:
                        signals.append(('sell', 0.7))
                        reasons.append("EMA 12/26 bearish crossover")
                        print(f"   ✅ SELL: EMA bearish crossover")
                    else:
                        signals.append(('sell', 0.4))
                        reasons.append("EMA 12 below EMA 26")
                        print(f"   ⚠️  SELL: EMA 12 below EMA 26")
            else:
                print(f"   ❌ EMA dados inválidos")
        else:
            print(f"   ❌ EMA não disponível")
        
        # 4. Bollinger Bands Analysis
        print(f"\n4️⃣ ANÁLISE BOLLINGER BANDS:")
        if ('bb_lower' in latest and 'bb_upper' in latest and 
            not pd.isna(latest['bb_lower']) and not pd.isna(latest['bb_upper'])):
            
            bb_position = (latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower'])
            print(f"   BB Position = {bb_position:.2f} (0=lower, 1=upper)")
            
            if bb_position <= 0.2:
                signals.append(('buy', 0.6))
                reasons.append("Price near lower Bollinger Band")
                print(f"   ✅ BUY: Price near lower BB ({bb_position:.2f})")
            elif bb_position >= 0.8:
                signals.append(('sell', 0.6))
                reasons.append("Price near upper Bollinger Band")
                print(f"   ✅ SELL: Price near upper BB ({bb_position:.2f})")
            elif bb_position <= 0.4:
                signals.append(('buy', 0.3))
                reasons.append("Price in lower BB zone")
                print(f"   ⚠️  BUY: Price in lower BB zone ({bb_position:.2f})")
            elif bb_position >= 0.6:
                signals.append(('sell', 0.3))
                reasons.append("Price in upper BB zone")
                print(f"   ⚠️  SELL: Price in upper BB zone ({bb_position:.2f})")
            else:
                print(f"   ❌ HOLD: Price in middle BB zone ({bb_position:.2f})")
        else:
            print(f"   ❌ Bollinger Bands não disponível")
        
        # RESUMO DOS SINAIS
        print(f"\n📊 RESUMO DOS SINAIS ENCONTRADOS:")
        print(f"=" * 60)
        
        buy_signals = [s[1] for s in signals if s[0] == 'buy']
        sell_signals = [s[1] for s in signals if s[0] == 'sell']
        
        print(f"Total de sinais: {len(signals)}")
        print(f"Sinais BUY: {len(buy_signals)} → {buy_signals}")
        print(f"Sinais SELL: {len(sell_signals)} → {sell_signals}")
        
        buy_strength = sum(buy_signals)
        sell_strength = sum(sell_signals)
        
        print(f"Buy Strength: {buy_strength:.2f}")
        print(f"Sell Strength: {sell_strength:.2f}")
        
        print(f"\n🎯 DETALHES DE CADA SINAL:")
        for i, (signal_type, strength) in enumerate(signals):
            reason = reasons[i] if i < len(reasons) else "N/A"
            print(f"   {i+1:2d}. {signal_type.upper():4s} ({strength:.1f}): {reason}")
        
        # CÁLCULO FINAL
        print(f"\n🏁 CÁLCULO FINAL:")
        min_strength = 0.4
        min_diff = 0.2
        
        print(f"Limiar mínimo: {min_strength}")
        print(f"Diferença mínima: {min_diff}")
        
        if buy_strength >= min_strength and buy_strength > sell_strength + min_diff:
            result = "BUY (forte)"
            confidence = min(buy_strength / 2.0, 1.0)
        elif sell_strength >= min_strength and sell_strength > buy_strength + min_diff:
            result = "SELL (forte)"
            confidence = min(sell_strength / 2.0, 1.0)
        elif buy_strength >= min_strength and buy_strength > sell_strength:
            result = "BUY (fraco)"
            confidence = min(buy_strength / 3.0, 0.6)
        elif sell_strength >= min_strength and sell_strength > buy_strength:
            result = "SELL (fraco)"
            confidence = min(sell_strength / 3.0, 0.6)
        else:
            result = "HOLD"
            confidence = 0.0
        
        print(f"✅ RESULTADO FINAL: {result} (confiança: {confidence:.2f})")
        
        # Comparar com resultado real do sistema
        print(f"\n🔄 COMPARANDO COM O SISTEMA:")
        tech_result = signal_gen._analyze_technical_indicators(data_with_indicators)
        print(f"Sistema retorna: {tech_result['signal'].upper()} ({tech_result['confidence']:.2f})")
        
        if tech_result['signal'].upper() != result.split()[0]:
            print(f"⚠️  DISCREPÂNCIA DETECTADA!")
            print(f"   Esperado: {result}")
            print(f"   Sistema:  {tech_result['signal'].upper()}")
        else:
            print(f"✅ Resultado consistente!")
        
    except Exception as e:
        print(f"❌ Erro durante debug: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    import pandas as pd
    debug_deep_signal_generation()
