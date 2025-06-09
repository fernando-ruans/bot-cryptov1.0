#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para treinar o modelo de IA do bot de trading
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.technical_indicators import TechnicalIndicators
import pandas as pd
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Função principal para treinar o modelo de IA"""
    try:
        print("=== TREINAMENTO DO MODELO DE IA ===")
        
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        tech_indicators = TechnicalIndicators(config)
        
        # Símbolo para treinamento
        symbol = 'BTCUSDT'
        timeframe = '1h'
        
        print(f"Obtendo dados históricos para {symbol}...")
        
        # Obter dados históricos (máximo disponível)
        df = market_data.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            limit=1000  # Obter mais dados para melhor treinamento
        )
        
        if df is None or df.empty:
            print("[ERRO] Erro: Não foi possível obter dados históricos")
            return
        
        print(f"[OK] Dados obtidos: {len(df)} registros")
        print(f"Período: {df.index[0]} até {df.index[-1]}")
        
        # Calcular indicadores técnicos
        print("Calculando indicadores técnicos...")
        df = tech_indicators.calculate_all_indicators(df)
        
        print(f"[OK] Indicadores calculados. Total de colunas: {len(df.columns)}")
        
        # Verificar se há dados suficientes
        min_samples = config.MIN_TRAINING_SAMPLES
        if len(df) < min_samples:
            print(f"[AVISO] Poucos dados para treinamento ({len(df)} < {min_samples})")
            print("Continuando mesmo assim...")
        
        # Treinar modelo
        print(f"Iniciando treinamento do modelo para {symbol}...")
        print("Isso pode levar alguns minutos...")
        
        training_result = ai_engine.train_models(df, symbol)
        
        if training_result.get('success', True):
            print("[OK] Treinamento concluído com sucesso!")
            
            # Testar predição
            print("\nTestando predição...")
            prediction = ai_engine.predict_signal(df, symbol)
            
            print(f"Resultado da predição:")
            print(f"  - Sinal: {prediction.get('signal', 'N/A')}")
            print(f"  - Confiança: {prediction.get('confidence', 'N/A'):.4f}")
            
            if 'individual_predictions' in prediction:
                print(f"  - Predições individuais: {prediction['individual_predictions']}")
            
            if prediction.get('signal', 0) != 0:
                print("[OK] Modelo treinado e funcionando corretamente!")
            else:
                print("[AVISO] Modelo treinado, mas predição neutra")
                
        else:
            print(f"[ERRO] Erro no treinamento: {training_result.get('error', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"[ERRO] Erro durante o treinamento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()