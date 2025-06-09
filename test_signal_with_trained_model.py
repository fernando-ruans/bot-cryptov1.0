#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a geração de sinais com o modelo de IA treinado
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.technical_indicators import TechnicalIndicators
from src.market_analyzer import MarketAnalyzer
from src.signal_generator import SignalGenerator
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
    """Função principal para testar a geração de sinais"""
    try:
        print("=== TESTE DE GERAÇÃO DE SINAIS COM MODELO TREINADO ===")
        
        # Inicializar componentes
        config = Config()
        
        # Configurar parâmetros ultra-agressivos para forçar sinais
        config.SIGNAL_CONFIG['min_confidence'] = 0.5  # Reduzir confiança mínima
        config.SIGNAL_CONFIG['min_market_score'] = 0.5  # Reduzir score mínimo
        config.RISK_MANAGEMENT['min_ai_confidence'] = 0.5  # Reduzir confiança mínima da IA
        
        market_data = MarketDataManager(config)
        tech_indicators = TechnicalIndicators(config)
        ai_engine = AITradingEngine(config)
        
        # Carregar modelos treinados
        print("Carregando modelos de IA...")
        ai_engine.load_models()
        
        market_analyzer = MarketAnalyzer(config, market_data, ai_engine)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        # Símbolo para teste
        symbol = 'BTCUSDT'
        timeframe = '1h'
        
        print(f"Obtendo dados históricos para {symbol}...")
        
        # Obter dados históricos
        df = market_data.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            limit=1000
        )
        
        if df is None or df.empty:
            print(f"[ERRO] Erro: Não foi possível obter dados históricos")
            return
        
        print(f"[OK] Dados obtidos: {len(df)} registros")
        print(f"Período: {df.index[0]} até {df.index[-1]}")
        
        # Calcular indicadores técnicos
        print("Calculando indicadores técnicos...")
        df = tech_indicators.calculate_all_indicators(df)
        
        print(f"[OK] Indicadores calculados. Total de colunas: {len(df.columns)}")
        
        # Verificar se o modelo está treinado
        print("Verificando modelo de IA...")
        prediction = ai_engine.predict_signal(df, symbol)
        
        if 'error' in prediction and prediction['error'] == 'Modelo não treinado':
            print(f"[ERRO] Modelo de IA não está treinado para {symbol}")
            return
        
        print(f"[OK] Modelo de IA está treinado para {symbol}")
        
        # Tentar gerar um sinal
        print("\nTentando gerar um sinal...")
        signal = signal_generator.generate_signal(symbol, timeframe)
        
        if signal:
            print(f"[OK] Sinal gerado com sucesso!")
            print(f"Detalhes do sinal:")
            print(f"  - Símbolo: {signal.symbol}")
            print(f"  - Timeframe: {signal.timeframe}")
            print(f"  - Tipo: {signal.signal_type}")
            print(f"  - Preço de entrada: {signal.entry_price}")
            print(f"  - Stop Loss: {signal.stop_loss}")
            print(f"  - Take Profit: {signal.take_profit}")
            print(f"  - Confiança: {signal.confidence}")
            print(f"  - Razões: {signal.reasons}")
            print(f"  - Timestamp: {signal.timestamp}")
        else:
            print(f"[AVISO] Não foi possível gerar um sinal")
            
            # Depurar o processo de análise de mercado
            print("\nDepurando análise de mercado...")
            market_recommendation = market_analyzer.get_trade_recommendation(symbol, timeframe)
            
            print(f"Recomendação de mercado:")
            print(f"  - Recomendação: {market_recommendation.get('recommendation', 'N/A')}")
            print(f"  - Confiança: {market_recommendation.get('confidence', 'N/A')}")
            print(f"  - Score de mercado: {market_recommendation.get('market_score', 'N/A')}")
            print(f"  - Razões: {market_recommendation.get('reasons', [])}")
            
            # Tentar forçar um sinal
            print("\nTentando forçar um sinal de compra...")
            forced_signal = {
                'symbol': symbol,
                'timeframe': timeframe,
                'signal_type': 'buy',
                'entry_price': df['close'].iloc[-1],
                'stop_loss': df['close'].iloc[-1] * 0.95,  # 5% abaixo
                'take_profit': df['close'].iloc[-1] * 1.05,  # 5% acima
                'confidence': 0.85,
                'reasons': ['Sinal forçado para teste'],
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"Sinal forçado:")
            for key, value in forced_signal.items():
                print(f"  - {key}: {value}")
            
    except Exception as e:
        print(f"[ERRO] Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()