#!/usr/bin/env python3
"""
Script para analisar as features específicas que estão causando o viés BUY
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai_engine import AITradingEngine
from src.market_data import MarketDataManager
from src.config import Config
import pandas as pd
import logging

# Configurar logging para capturar debug
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_ai_bias():
    """Análise direta das features da IA"""
    
    print("🔍 ANÁLISE DIRETA DAS FEATURES DA IA")
    print("=" * 60)
      # Configuração usando Config() como nos outros testes
    config = Config()
    
    try:
        # Inicializar components
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        
        # Obter dados
        print(f"📊 Obtendo dados para BTCUSDT...")
        df = market_data.get_historical_data('BTCUSDT', '1h', limit=200)
        
        if df is None or len(df) < 50:
            print("❌ Erro ao obter dados")
            return
            
        print(f"✅ Dados obtidos: {len(df)} períodos")
        
        # Preparar features
        print(f"🔧 Preparando features...")
        df_with_features = ai_engine.prepare_features(df.copy())
        
        print(f"✅ Features preparadas: {len(df_with_features.columns)} colunas")
        
        # Analisar as últimas features
        latest = df_with_features.iloc[-1]
        
        print(f"\n🔍 ANÁLISE DAS FEATURES MAIS RECENTES:")
        
        # 1. Momentum
        print(f"\n📈 MOMENTUM FEATURES:")
        momentum_features = ['momentum_5', 'momentum_10', 'momentum_20', 'roc_5', 'roc_10', 'roc_20']
        for feature in momentum_features:
            if feature in latest.index:
                value = latest[feature]
                signal = "BUY" if value > 0 else "SELL" if value < 0 else "NEUTRAL"
                print(f"  {feature}: {value:.6f} -> {signal}")
        
        # 2. Padrões
        print(f"\n📊 PATTERN FEATURES:")
        pattern_features = ['bullish_patterns_score', 'bearish_patterns_score']
        for feature in pattern_features:
            if feature in latest.index:
                value = latest[feature]
                print(f"  {feature}: {value:.6f}")
        
        if 'bullish_patterns_score' in latest.index and 'bearish_patterns_score' in latest.index:
            balance = latest['bullish_patterns_score'] - latest['bearish_patterns_score']
            signal = "BUY" if balance > 0.3 else "SELL" if balance < -0.3 else "NEUTRAL"
            print(f"  Pattern Balance: {balance:.6f} -> {signal}")
        
        # 3. Regime
        print(f"\n🌊 REGIME FEATURES:")
        regime_features = ['ensemble_regime_score', 'regime_bull_bear', 'regime_volatility']
        for feature in regime_features:
            if feature in latest.index:
                value = latest[feature]
                if feature == 'ensemble_regime_score':
                    signal = "BUY" if value > 1 else "SELL" if value < -1 else "NEUTRAL"
                    print(f"  {feature}: {value:.6f} -> {signal}")
                else:
                    print(f"  {feature}: {value:.6f}")
        
        # 4. Volatilidade
        print(f"\n📉 VOLATILITY FEATURES:")
        vol_features = ['volatility_ratio', 'volatility_percentile', 'atr_normalized']
        for feature in vol_features:
            if feature in latest.index:
                value = latest[feature]
                print(f"  {feature}: {value:.6f}")
        
        # 5. Testar a função predict_signal diretamente
        print(f"\n🧠 TESTANDO PREDICT_SIGNAL DIRETAMENTE:")
        result = ai_engine.predict_signal(df_with_features, 'BTCUSDT')
        
        print(f"  Resultado: {result}")
        
        # 6. Análise de distribuição de features
        print(f"\n📊 DISTRIBUIÇÃO DAS FEATURES:")
        
        # Contar quantas features são positivas vs negativas
        numeric_features = df_with_features.select_dtypes(include=['float64', 'int64']).columns
        latest_numeric = latest[numeric_features]
        
        positive_count = (latest_numeric > 0).sum()
        negative_count = (latest_numeric < 0).sum()
        zero_count = (latest_numeric == 0).sum()
        
        print(f"  Features positivas: {positive_count}")
        print(f"  Features negativas: {negative_count}")
        print(f"  Features zero/nulas: {zero_count}")
        print(f"  Razão positivo/negativo: {positive_count/negative_count if negative_count > 0 else 'inf'}")
        
        # 7. Features mais extremas
        print(f"\n🔥 TOP FEATURES POSITIVAS:")
        top_positive = latest_numeric.nlargest(10)
        for feature, value in top_positive.items():
            if value > 0:
                print(f"  {feature}: {value:.6f}")
        
        print(f"\n❄️ TOP FEATURES NEGATIVAS:")
        top_negative = latest_numeric.nsmallest(10)
        for feature, value in top_negative.items():
            if value < 0:
                print(f"  {feature}: {value:.6f}")
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_ai_bias()
