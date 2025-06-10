#!/usr/bin/env python3
"""
Debug pós-correção: Investigar por que ainda temos 100% BUY
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.signal_generator import SignalGenerator
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.config import Config
import traceback

def debug_signal_generation():
    print("=== DEBUG PÓS-CORREÇÃO: INVESTIGANDO 100% BUY ===")
    
    # Testar apenas um símbolo para análise detalhada
    symbol = "BTCUSDT"
    timeframe = "1h"
    
    try:
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        signal_gen = SignalGenerator(ai_engine, market_data)
        
        print(f"\n🔍 ANALISANDO {symbol} {timeframe}...")        # Obter dados de mercado
        data = market_data.get_historical_data(symbol, timeframe, limit=100)
        if data is None or data.empty:
            print("❌ Dados insuficientes")
            return
            
        print(f"✅ Dados obtidos: {len(data)} candles")
          # Análise técnica detalhada
        print("\n📊 ANÁLISE TÉCNICA DETALHADA:")
        tech_result = signal_gen._analyze_technical_indicators(data)
        print(f"Tech Signal: {tech_result['signal']}")
        print(f"Tech Confidence: {tech_result['confidence']}")
        print(f"Tech Reasons: {tech_result['reasons']}")
        
        # Análise de IA
        print("\n🤖 ANÁLISE DE IA:")
        try:
            ai_result = signal_gen._analyze_with_ai(data, symbol)
            print(f"AI Signal: {ai_result['signal']}")
            print(f"AI Confidence: {ai_result['confidence']}")
            print(f"AI Reasons: {ai_result['reasons']}")
        except Exception as e:
            print(f"AI Error: {e}")
            ai_result = {'signal': 'HOLD', 'confidence': 0.0, 'reasons': ['AI não disponível']}
        
        # Análise de risco
        print("\n⚠️ ANÁLISE DE RISCO:")
        risk_result = signal_gen._analyze_risk(data, symbol)
        print(f"Risk Multiplier: {risk_result['risk_multiplier']}")
        print(f"Risk Level: {risk_result['risk_level']}")
        print(f"Risk Factors: {risk_result['risk_factors']}")
        
        # Combinação final
        print("\n🎯 COMBINAÇÃO FINAL:")
        final_signal = signal_gen._combine_signals(tech_result, ai_result, risk_result, symbol)
        print(f"Final Signal: {final_signal['signal']}")
        print(f"Final Confidence: {final_signal['confidence']}")
        print(f"Final Reasons: {final_signal['reasons']}")
        
        # Análise detalhada dos scores
        print("\n📈 ANÁLISE DOS SCORES:")
        
        # Recriar lógica de _combine_signals para debug
        tech_signal = tech_result['signal']
        tech_conf = tech_result['confidence']
        ai_signal = ai_result['signal']
        ai_conf = ai_result['confidence']
        risk_mult = risk_result['risk_multiplier']
        
        print(f"Tech: {tech_signal} (conf: {tech_conf})")
        print(f"AI: {ai_signal} (conf: {ai_conf})")
        print(f"Risk Multiplier: {risk_mult}")
        
        # Calcular scores
        buy_score = 0.0
        sell_score = 0.0
        
        if tech_signal == 'BUY':
            buy_score += tech_conf * 0.6
        elif tech_signal == 'SELL':
            sell_score += tech_conf * 0.6
            
        if ai_signal == 'BUY':
            buy_score += ai_conf * 0.4
        elif ai_signal == 'SELL':
            sell_score += ai_conf * 0.4
            
        # Aplicar multiplicador de risco
        buy_score *= risk_mult
        sell_score *= risk_mult
        
        print(f"Buy Score (antes do risco): {buy_score/risk_mult:.4f}")
        print(f"Sell Score (antes do risco): {sell_score/risk_mult:.4f}")
        print(f"Buy Score (após risco): {buy_score:.4f}")
        print(f"Sell Score (após risco): {sell_score:.4f}")
        
        # Decisão final
        if buy_score > sell_score:
            decision = "BUY"
        elif sell_score > buy_score:
            decision = "SELL"
        else:
            decision = "EMPATE (vai para HOLD ou BUY dependendo da lógica)"
            
        print(f"Decisão baseada em scores: {decision}")
        
    except Exception as e:
        print(f"❌ Erro durante debug: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_signal_generation()
