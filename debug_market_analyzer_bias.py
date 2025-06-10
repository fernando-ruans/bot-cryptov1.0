#!/usr/bin/env python3
"""
DEBUG: Investigar Market Analyzer - Fonte do Bias BUY
Foca especificamente no Market Analyzer que pode estar causando o bias
"""

import asyncio
import sys
import os

# Adicionar src ao path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Importar com path absoluto
sys.path.insert(0, os.path.dirname(__file__))
from src.signal_generator import SignalGenerator
from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.market_analyzer import MarketAnalyzer

def debug_market_analyzer_bias():
    print("=== DEBUG: MARKET ANALYZER - FONTE DO BIAS BUY ===")
    
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    market_analyzer = MarketAnalyzer(config, market_data, ai_engine)
    
    symbol = "BTCUSDT"
    timeframe = "1h"
    
    print(f"📊 Analisando Market Analyzer para: {symbol} ({timeframe})")
    
    try:
        # 1. TESTAR get_trade_recommendation DIRETAMENTE
        print("\n1️⃣ TESTANDO get_trade_recommendation DIRETAMENTE:")
        print("=" * 60)
        
        recommendation = market_analyzer.get_trade_recommendation(symbol, timeframe)
        
        print(f"📊 RESULTADO COMPLETO:")
        if recommendation:
            for key, value in recommendation.items():
                print(f"   {key}: {value}")
        else:
            print("   ❌ Nenhuma recomendação retornada")
        
        # 2. VERIFICAR ANÁLISE DE MERCADO STEP BY STEP
        print("\n2️⃣ ANÁLISE STEP BY STEP:")
        print("=" * 60)
        
        # Analisar contexto de mercado
        print("🔍 Analisando contexto de mercado...")
        market_context = market_analyzer.analyze_market_context(symbol, timeframe)
        print(f"Contexto de mercado: {market_context}")
        
        # 3. VERIFICAR PREDICT_SIGNAL DA IA
        print("\n3️⃣ VERIFICAR PREDIÇÃO DA IA:")
        print("=" * 60)
        
        # Obter dados históricos
        df = market_data.get_historical_data(symbol, timeframe, 500)
        print(f"Dados obtidos: {len(df)} registros")
        
        if df is not None and not df.empty:
            # Preparar features para IA
            df_features = ai_engine.prepare_features(df)
            print(f"Features preparadas: {df_features.shape}")
            
            # Fazer predição
            ai_prediction = ai_engine.predict_signal(df_features, symbol)
            print(f"Predição IA: {ai_prediction}")
            
            # Verificar se a IA sempre retorna BUY
            if ai_prediction.get('signal') == 1:
                print("🚨 IA ESTÁ RETORNANDO SINAL BUY!")
                print("   Isso pode ser a fonte do bias!")
                
                # Verificar se é o modo de teste forçado
                if ai_prediction.get('test_mode'):
                    print("   ⚠️  IA EM MODO DE TESTE - FORÇANDO SINAL BUY!")
                    print("   ESTA É A FONTE DO BIAS!")
                
            elif ai_prediction.get('signal') == 0:
                print("ℹ️  IA retornando HOLD")
            elif ai_prediction.get('signal') == -1:
                print("ℹ️  IA retornando SELL")
        
        # 4. VERIFICAR COMBINAÇÃO FINAL NO MARKET ANALYZER
        print("\n4️⃣ VERIFICAR COMBINAÇÃO FINAL:")
        print("=" * 60)
        
        if recommendation:
            rec_signal = recommendation.get('recommendation', 'unknown')
            rec_confidence = recommendation.get('confidence', 0)
            market_score = recommendation.get('market_score', 0)
            
            print(f"Recomendação final: {rec_signal}")
            print(f"Confiança: {rec_confidence}")
            print(f"Market Score: {market_score}")
            
            if rec_signal == 'buy':
                print("🚨 MARKET ANALYZER ESTÁ RETORNANDO BUY!")
                print("   Investigando por quê...")
                
                # Verificar razões
                reasons = recommendation.get('reasons', [])
                print(f"   Razões ({len(reasons)}):")
                for i, reason in enumerate(reasons, 1):
                    print(f"     {i}. {reason}")
        
        # 5. TESTAR MÚLTIPLAS EXECUÇÕES
        print("\n5️⃣ TESTE DE CONSISTÊNCIA (5 execuções):")
        print("=" * 60)
        
        results = []
        for i in range(5):
            try:
                rec = market_analyzer.get_trade_recommendation(symbol, timeframe)
                signal = rec.get('recommendation', 'none') if rec else 'none'
                confidence = rec.get('confidence', 0) if rec else 0
                results.append((signal, confidence))
                print(f"   Execução {i+1}: {signal} ({confidence:.3f})")
            except Exception as e:
                print(f"   Execução {i+1}: ERRO - {e}")
                results.append(('error', 0))
        
        # Analisar resultados
        buy_count = sum(1 for r in results if r[0] == 'buy')
        sell_count = sum(1 for r in results if r[0] == 'sell')
        hold_count = sum(1 for r in results if r[0] == 'hold')
        error_count = sum(1 for r in results if r[0] == 'error')
        
        print(f"\n📊 RESUMO DE CONSISTÊNCIA:")
        print(f"   BUY: {buy_count}/5 ({buy_count*20}%)")
        print(f"   SELL: {sell_count}/5 ({sell_count*20}%)")
        print(f"   HOLD: {hold_count}/5 ({hold_count*20}%)")
        print(f"   ERRO: {error_count}/5 ({error_count*20}%)")
        
        if buy_count == 5:
            print("🚨 BIAS CONFIRMADO: 100% BUY nas 5 execuções!")
        elif buy_count >= 3:
            print("⚠️  BIAS PROVÁVEL: Maioria BUY")
        else:
            print("✅ Sem bias aparente")
        
        return recommendation
        
    except Exception as e:
        print(f"❌ ERRO na análise: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_market_analyzer_bias()
