#!/usr/bin/env python3
"""
Teste de carregamento de modelos
"""

import sys
import os
sys.path.append('.')

from src.config import Config
from src.ai_engine import AITradingEngine

def test_model_loading():
    print("=== TESTE DE CARREGAMENTO DE MODELOS ===")
    
    config = Config()
    ai_engine = AITradingEngine(config)
    
    print("Antes do carregamento:")
    print(f"  is_trained: {ai_engine.is_trained}")
    print(f"  modelos: {list(ai_engine.models.keys())}")
    
    print("\nCarregando modelos...")
    ai_engine.load_models()
    
    print("Depois do carregamento:")
    print(f"  is_trained: {ai_engine.is_trained}")
    print(f"  modelos: {list(ai_engine.models.keys())}")
    
    if 'BTCUSDT' in ai_engine.models:
        print(f"\nModelos BTCUSDT: {list(ai_engine.models['BTCUSDT'].keys())}")
        for name, model_data in ai_engine.models['BTCUSDT'].items():
            has_model = model_data.get('model') is not None
            accuracy = model_data.get('accuracy', 'N/A')
            print(f"  {name}: model={has_model}, accuracy={accuracy}")
    
    # Testar predição
    print("\n=== TESTE DE PREDIÇÃO ===")
    from src.market_data import MarketDataManager
    from src.technical_indicators import TechnicalIndicators
    
    market_data = MarketDataManager(config)
    tech = TechnicalIndicators(config)
    
    # Obter dados
    df = market_data.get_historical_data('BTCUSDT', '1h', 100)
    if df is not None and not df.empty:
        print(f"Dados obtidos: {len(df)} registros")
        
        # Preparar features
        df_features = ai_engine.prepare_features(df)
        print(f"Features preparadas: {len(df_features.columns)} colunas")
        
        # Fazer predição
        prediction = ai_engine.predict_signal(df_features, 'BTCUSDT')
        print(f"Predição: {prediction}")
    else:
        print("Erro ao obter dados")

if __name__ == "__main__":
    test_model_loading()
