#!/usr/bin/env python3
"""
DEBUG: Por que só retorna HOLD?
Investigar thresholds e configurações que estão impedindo sinais BUY/SELL
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.signal_generator import SignalGenerator
from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine

def debug_hold_problem():
    print("=== DEBUG: POR QUE SÓ RETORNA HOLD? ===")
    
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    symbol = "BTCUSDT"
    timeframe = "1h"
    
    print(f"📊 Analisando {symbol} ({timeframe})")
    
    # 1. VERIFICAR CONFIGURAÇÕES ATUAIS
    print("\n1️⃣ CONFIGURAÇÕES ATUAIS:")
    print("=" * 50)
    
    print(f"🔧 SIGNAL_CONFIG:")
    for key, value in config.SIGNAL_CONFIG.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔧 RISK_MANAGEMENT:")
    for key, value in config.RISK_MANAGEMENT.items():
        print(f"   {key}: {value}")
    
    # 2. OBTER DADOS
    print(f"\n2️⃣ OBTENDO DADOS:")
    print("=" * 50)
    
    df = market_data.get_historical_data(symbol, timeframe, 500)
    print(f"📊 Dados históricos: {len(df)} registros")
    print(f"📊 Preço atual: ${df['close'].iloc[-1]:.2f}")
    
    # 3. ANÁLISE TÉCNICA DETALHADA
    print(f"\n3️⃣ ANÁLISE TÉCNICA DETALHADA:")
    print("=" * 50)
    
    # Calcular indicadores
    df_with_indicators = signal_generator.technical_indicators.calculate_all_indicators(df.copy())
    
    # Análise técnica direta
    technical_result = signal_generator._analyze_technical_indicators(df_with_indicators)
    
    print(f"📊 Resultado técnico:")
    print(f"   Signal: {technical_result['signal']}")
    print(f"   Confidence: {technical_result['confidence']:.4f}")
    print(f"   Buy strength: {technical_result.get('buy_strength', 0):.4f}")
    print(f"   Sell strength: {technical_result.get('sell_strength', 0):.4f}")
    print(f"   Reasons: {technical_result['reasons'][:3]}")
    
    # 4. PREDIÇÃO AI
    print(f"\n4️⃣ PREDIÇÃO AI:")
    print("=" * 50)
    
    ai_prediction = ai_engine.predict_signal(df_with_indicators, symbol)
    print(f"📊 Predição AI:")
    for key, value in ai_prediction.items():
        if key != 'individual_predictions':
            print(f"   {key}: {value}")
    
    # 5. ANÁLISES AUXILIARES
    print(f"\n5️⃣ ANÁLISES AUXILIARES:")
    print("=" * 50)
    
    volume_analysis = signal_generator._analyze_volume(df_with_indicators)
    print(f"📊 Volume: {volume_analysis}")
    
    volatility_analysis = signal_generator._analyze_volatility(df_with_indicators)
    print(f"📊 Volatilidade: {volatility_analysis}")
    
    market_context = signal_generator._analyze_market_context(symbol, timeframe)
    print(f"📊 Contexto: {market_context}")
    
    # 6. COMBINAÇÃO FINAL
    print(f"\n6️⃣ COMBINAÇÃO FINAL:")
    print("=" * 50)
    
    combined = signal_generator._combine_analyses(
        technical_result, ai_prediction, volume_analysis,
        volatility_analysis, market_context
    )
    
    print(f"📊 Resultado final:")
    for key, value in combined.items():
        print(f"   {key}: {value}")
    
    # 7. TESTAR COM THRESHOLDS REDUZIDOS
    print(f"\n7️⃣ TESTE COM THRESHOLDS REDUZIDOS:")
    print("=" * 50)
    
    # Salvar configurações originais
    original_min_confidence = config.SIGNAL_CONFIG['min_confidence']
    original_min_market_score = config.SIGNAL_CONFIG.get('min_market_score', 0.5)
    original_ai_confidence = config.RISK_MANAGEMENT.get('min_ai_confidence', 0.6)
    
    # Aplicar configurações ultra-agressivas
    config.SIGNAL_CONFIG['min_confidence'] = 0.05  # 5%
    config.SIGNAL_CONFIG['min_market_score'] = 0.1  # 10%
    config.RISK_MANAGEMENT['min_ai_confidence'] = 0.1  # 10%
    config.SIGNAL_CONFIG['enable_confluence'] = False
    
    print(f"📊 Configurações ultra-agressivas aplicadas:")
    print(f"   min_confidence: {config.SIGNAL_CONFIG['min_confidence']}")
    print(f"   min_market_score: {config.SIGNAL_CONFIG['min_market_score']}")
    print(f"   min_ai_confidence: {config.RISK_MANAGEMENT['min_ai_confidence']}")
    print(f"   enable_confluence: {config.SIGNAL_CONFIG['enable_confluence']}")
    
    # Atualizar o signal_generator com a nova config
    signal_generator.config = config
    
    # Testar novamente
    print(f"\n📊 Testando com configurações agressivas:")
    signal = signal_generator.generate_signal(symbol, timeframe)
    
    if signal:
        print(f"✅ SINAL GERADO:")
        print(f"   Tipo: {signal.signal_type}")
        print(f"   Confiança: {signal.confidence:.4f}")
        print(f"   Preço: ${signal.entry_price:.2f}")
        print(f"   Razões: {signal.reasons[:3]}")
    else:
        print(f"❌ AINDA SEM SINAL - Problema mais profundo")
    
    # 8. RESTAURAR CONFIGURAÇÕES
    config.SIGNAL_CONFIG['min_confidence'] = original_min_confidence
    config.SIGNAL_CONFIG['min_market_score'] = original_min_market_score
    config.RISK_MANAGEMENT['min_ai_confidence'] = original_ai_confidence
    config.SIGNAL_CONFIG['enable_confluence'] = True
    
    print(f"\n8️⃣ DIAGNÓSTICO:")
    print("=" * 50)
    
    if technical_result['confidence'] < 0.1:
        print("❌ PROBLEMA: Análise técnica muito fraca")
        print("   🔧 Solução: Ajustar cálculo de indicadores técnicos")
    
    if ai_prediction.get('confidence', 0) < 0.1:
        print("❌ PROBLEMA: AI com confiança muito baixa")
        print("   🔧 Solução: Treinar modelos ou usar fallback")
    
    if combined.get('confidence', 0) < original_min_confidence:
        print(f"❌ PROBLEMA: Confiança combinada {combined.get('confidence', 0):.4f} < threshold {original_min_confidence}")
        print("   🔧 Solução: Reduzir thresholds ou melhorar análises")

if __name__ == "__main__":
    try:
        debug_hold_problem()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
