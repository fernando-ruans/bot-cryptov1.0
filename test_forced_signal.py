#!/usr/bin/env python3
"""
Teste forçado para simular um sinal AI positivo
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from signal_generator import SignalGenerator
from market_analyzer import MarketAnalyzer
from ai_engine import AIEngine
from config import TradingConfig
import warnings

# Suprimir warnings
warnings.filterwarnings('ignore')

class MockAIEngine(AIEngine):
    """AI Engine modificado para sempre retornar um sinal positivo"""
    
    def predict_signal(self, df, symbol):
        """Simular uma predição sempre positiva"""
        return {
            'signal': 1,  # Forçar BUY
            'confidence': 0.85,  # Alta confiança
            'individual_predictions': {
                'random_forest': 1,
                'gradient_boosting': 1,
                'lgbm': 1,
                'svm': 1
            },
            'timestamp': '2024-12-09T10:00:00'
        }

def test_with_forced_signal():
    """Testar com sinal AI forçado"""
    print("=== TESTE COM SINAL AI FORÇADO ===")
    
    try:
        config = TradingConfig()
        symbol = "BTCUSDT"
        
        # Usar AI Engine modificado
        ai_engine = MockAIEngine(config)
        market_analyzer = MarketAnalyzer(config)
        signal_generator = SignalGenerator(config, market_analyzer, ai_engine)
        
        print(f"1. Testando com sinal AI forçado (BUY, confidence=0.85)...")
        
        # Primeiro, testar o market_analyzer diretamente
        print(f"\n2. Testando market_analyzer...")
        recommendation = market_analyzer.get_trade_recommendation(symbol)
        
        print(f"   Recommendation: {recommendation.get('recommendation', 'N/A')}")
        print(f"   Confidence: {recommendation.get('confidence', 'N/A')}")
        print(f"   Market Score: {recommendation.get('market_score', 'N/A')}")
        
        # Agora testar o signal_generator
        print(f"\n3. Testando signal_generator...")
        signal = signal_generator.generate_signal(symbol)
        
        if signal:
            print(f"   ✅ SINAL GERADO!")
            print(f"   Tipo: {signal.signal_type}")
            print(f"   Confiança: {signal.confidence:.3f}")
            print(f"   Preço: ${signal.entry_price:.2f}")
            print(f"   Stop Loss: ${signal.stop_loss:.2f}")
            print(f"   Take Profit: ${signal.take_profit:.2f}")
        else:
            print(f"   ❌ Nenhum sinal gerado")
        
        return signal is not None
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_forced_signal()
    print(f"\n🎯 RESULTADO: {'✅ SUCESSO' if success else '❌ FALHA'}")
