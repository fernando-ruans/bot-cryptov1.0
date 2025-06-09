#!/usr/bin/env python3
"""
Script para debugar especificamente o market_analyzer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.market_analyzer import MarketAnalyzer
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def debug_market_analyzer():
    """Debug específico do market analyzer"""
    print("=== DEBUG MARKET ANALYZER ===")
    
    try:
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        market_analyzer = MarketAnalyzer(config, market_data, ai_engine)
        
        # Configurações ultra-agressivas
        config.SIGNAL_CONFIG['min_confidence'] = 0.01
        config.SIGNAL_CONFIG['min_market_score'] = 0.01
        config.RISK_MANAGEMENT['min_ai_confidence'] = 0.01
        
        print("✓ Componentes inicializados")
        
        symbol = 'BTCUSDT'
        timeframe = '1h'
        
        print(f"\n=== TESTANDO get_trade_recommendation para {symbol} ===")
        
        # Chamar diretamente o método
        recommendation = market_analyzer.get_trade_recommendation(symbol, timeframe)
        
        print(f"\nResultado completo:")
        print(f"Type: {type(recommendation)}")
        print(f"Keys: {list(recommendation.keys()) if isinstance(recommendation, dict) else 'N/A'}")
        
        if recommendation:
            print(f"\nDetalhes da recomendação:")
            for key, value in recommendation.items():
                print(f"  {key}: {value}")
        else:
            print("❌ Recomendação vazia!")
            
        # Testar especificamente o predict_signal
        print(f"\n=== TESTANDO ai_engine.predict_signal ===")
        
        df = market_data.get_historical_data(symbol, timeframe, 100)
        if df is not None and not df.empty:
            print(f"✓ Dados obtidos: {len(df)} registros")
            
            # Preparar features
            df_features = ai_engine.prepare_features(df)
            print(f"✓ Features preparadas: {len(df_features.columns)} colunas")
            
            # Testar predict_signal
            ai_prediction = ai_engine.predict_signal(df_features, symbol)
            print(f"\nResultado do AI predict_signal:")
            print(f"Type: {type(ai_prediction)}")
            if isinstance(ai_prediction, dict):
                for key, value in ai_prediction.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  Valor: {ai_prediction}")
        else:
            print("❌ Não conseguiu obter dados históricos")
            
        return recommendation
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = debug_market_analyzer()
    if result:
        print("\n✅ DEBUG CONCLUÍDO!")
    else:
        print("\n❌ DEBUG FALHOU!")