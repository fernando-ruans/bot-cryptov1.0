#!/usr/bin/env python3
"""
Debug profundo da geração de sinais
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from signal_generator import SignalGenerator
from market_analyzer import MarketAnalyzer  
from ai_engine import AIEngine
from config import TradingConfig
import logging
import warnings

# Suprimir warnings desnecessários
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_signal_generation():
    """Debug completo da geração de sinais"""
    print("=== DEBUG PROFUNDO DA GERAÇÃO DE SINAIS ===")
    
    try:
        config = TradingConfig()
        symbol = "BTCUSDT"
        
        print(f"\n📊 Configurações atuais:")
        print(f"  - Min AI confidence: {config.SIGNAL_CONFIG['min_ai_confidence']}")
        print(f"  - Min market score: {config.SIGNAL_CONFIG['min_market_score']}")
        print(f"  - Min confidence: {config.SIGNAL_CONFIG['min_confidence']}")
        
        # 1. Testar Market Analyzer
        print(f"\n🎯 1. Testando Market Analyzer...")
        market_analyzer = MarketAnalyzer(config)
        recommendation = market_analyzer.get_trade_recommendation(symbol)
        print(f"Market recommendation: {recommendation}")
        
        # 2. Testar AI Engine
        print(f"\n🤖 2. Testando AI Engine...")
        ai_engine = AIEngine(config)
        ai_engine.load_models(symbol)
        ai_prediction = ai_engine.predict_signal(symbol)
        print(f"AI prediction: {ai_prediction}")
        
        # 3. Testar Signal Generator com logs detalhados
        print(f"\n📡 3. Testando Signal Generator...")
        signal_generator = SignalGenerator(config, market_analyzer, ai_engine)
        
        # Ativar debug no signal generator
        signal_generator.logger.setLevel(logging.DEBUG)
        
        # Gerar sinal com debug
        signal = signal_generator.generate_signal(symbol)
        print(f"Signal generated: {signal}")
        
        # 4. Diagnóstico detalhado
        print(f"\n🔍 4. Diagnóstico detalhado:")
        print(f"  Market score: {recommendation.get('market_score', 'N/A')}")
        print(f"  AI confidence: {ai_prediction.get('confidence', 'N/A')}")
        print(f"  AI signal: {ai_prediction.get('signal', 'N/A')}")
        
        # Verificar thresholds
        market_score = recommendation.get('market_score', 0)
        ai_confidence = ai_prediction.get('confidence', 0)
        ai_signal = ai_prediction.get('signal', 0)
        
        min_market = config.SIGNAL_CONFIG['min_market_score']
        min_ai_conf = config.SIGNAL_CONFIG['min_ai_confidence']
        
        print(f"\n✅ Verificação de critérios:")
        print(f"  Market score {market_score:.3f} >= {min_market} ? {market_score >= min_market}")
        print(f"  AI confidence {ai_confidence:.3f} >= {min_ai_conf} ? {ai_confidence >= min_ai_conf}")
        print(f"  AI signal {ai_signal} != 0 ? {ai_signal != 0}")
        
        meets_criteria = (
            market_score >= min_market and 
            ai_confidence >= min_ai_conf and 
            ai_signal != 0
        )
        print(f"  Todos os critérios atendidos? {meets_criteria}")
        
        if not meets_criteria:
            print(f"\n❌ PROBLEMA IDENTIFICADO:")
            if market_score < min_market:
                print(f"  - Market score muito baixo: {market_score:.3f} < {min_market}")
            if ai_confidence < min_ai_conf:
                print(f"  - AI confidence muito baixo: {ai_confidence:.3f} < {min_ai_conf}")
            if ai_signal == 0:
                print(f"  - AI sinal é neutro (0) - sem recomendação")
        
    except Exception as e:
        print(f"❌ Erro durante debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_signal_generation()
