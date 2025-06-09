#!/usr/bin/env python3
"""
Debug específico do market analyzer
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from market_analyzer import MarketAnalyzer
from config import TradingConfig
import warnings
import logging

# Suprimir warnings
warnings.filterwarnings('ignore')

def debug_market_analyzer():
    """Debug específico do market analyzer"""
    print("=== DEBUG MARKET ANALYZER ===")
    
    try:
        config = TradingConfig()
        market_analyzer = MarketAnalyzer(config)
        symbol = "BTCUSDT"
        
        print(f"Analisando {symbol}...")
        result = market_analyzer.get_trade_recommendation(symbol)
        
        print(f"\n📊 Resultado completo:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        # Verificar se atende aos thresholds
        market_score = result.get('market_score', 0)
        confidence = result.get('confidence', 0)
        recommendation = result.get('recommendation', 'hold')
        
        min_market_score = config.SIGNAL_CONFIG.get('min_market_score', 0.30)
        min_ai_confidence = config.SIGNAL_CONFIG.get('min_ai_confidence', 0.30)
        
        print(f"\n✅ Verificação de critérios:")
        print(f"  Market score: {market_score:.3f} >= {min_market_score} ? {market_score >= min_market_score}")
        print(f"  Confidence: {confidence:.3f} >= {min_ai_confidence} ? {confidence >= min_ai_confidence}")
        print(f"  Recommendation: {recommendation} != 'hold' ? {recommendation != 'hold'}")
        
        meets_all = (
            market_score >= min_market_score and
            confidence >= min_ai_confidence and
            recommendation != 'hold'
        )
        
        print(f"  ✅ Todos os critérios atendidos? {meets_all}")
        
        if not meets_all:
            print(f"\n❌ PROBLEMAS IDENTIFICADOS:")
            if market_score < min_market_score:
                print(f"  - Market score baixo: {market_score:.3f} < {min_market_score}")
            if confidence < min_ai_confidence:
                print(f"  - Confidence baixo: {confidence:.3f} < {min_ai_confidence}")
            if recommendation == 'hold':
                print(f"  - Recomendação é HOLD (sem ação)")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_market_analyzer()
