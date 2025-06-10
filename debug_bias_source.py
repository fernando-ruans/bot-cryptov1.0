#!/usr/bin/env python3
"""
Debug específico para identificar a origem do viés nos sinais
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine
from src.signal_generator import SignalGenerator
import logging

# Configurar log para mostrar apenas info importante
logging.getLogger().setLevel(logging.ERROR)

def debug_bias_source():
    """Debug para identificar a fonte do viés"""
    print("=== DEBUG: ORIGEM DO VIÉS DE SINAIS ===")
    
    # Configurar componentes
    config = Config()
    config.SIGNAL_CONFIG['min_ai_confidence'] = 0.01
    config.SIGNAL_CONFIG['min_market_score'] = 0.01
    
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    symbol = 'BTCUSDT'
    timeframe = '1h'
    
    print(f"Analisando {symbol} {timeframe}...")
    
    # 1. Obter dados
    df = market_data.get_historical_data(symbol, timeframe, 500)
    df = signal_generator.technical_indicators.calculate_all_indicators(df)
    current_price = market_data.get_current_price(symbol)
    
    print(f"✓ Dados obtidos: {len(df)} registros")
    print(f"✓ Preço atual: ${current_price:.2f}")
    
    # 2. Testar análise técnica isolada
    print(f"\n=== 1. ANÁLISE TÉCNICA ISOLADA ===")
    tech_result = signal_generator._analyze_technical_indicators(df)
    print(f"Sinal técnico: {tech_result['signal']}")
    print(f"Confiança técnica: {tech_result['confidence']:.3f}")
    print(f"Razões: {tech_result['reasons'][:3]}")
    
    # 3. Testar análise de volume
    print(f"\n=== 2. ANÁLISE DE VOLUME ===")
    volume_result = signal_generator._analyze_volume(df)
    print(f"Sinal volume: {volume_result['signal']}")
    print(f"Confiança volume: {volume_result['confidence']:.3f}")
    print(f"Razões: {volume_result['reasons'][:2]}")
      # 4. Testar predição de IA
    print(f"\n=== 3. PREDIÇÃO DE IA ===")
    try:
        ai_result = ai_engine.predict_market_movement(df, symbol, timeframe)
        print(f"Sinal IA: {ai_result.get('signal', 'N/A')}")
        print(f"Confiança IA: {ai_result.get('confidence', 0):.3f}")
    except Exception as e:
        print(f"❌ Erro na IA: {e}")
        ai_result = {'signal': 0, 'confidence': 0}
    
    # 5. Testar análise de mercado
    print(f"\n=== 4. ANÁLISE DE MERCADO ===")
    market_recommendation = signal_generator.market_analyzer.get_trade_recommendation(symbol, timeframe)
    if market_recommendation:
        print(f"Recomendação: {market_recommendation.get('recommendation', 'N/A')}")
        print(f"Market score: {market_recommendation.get('market_score', 0):.3f}")
        print(f"AI confidence: {market_recommendation.get('ai_confidence', 0):.3f}")
    else:
        print("❌ Nenhuma recomendação de mercado")
    
    # 6. Testar combinação de análises
    print(f"\n=== 5. COMBINAÇÃO DE ANÁLISES ===")
    
    # Simular os dados de entrada para _combine_analyses
    volatility_result = {'signal': 'normal', 'confidence': 0.5, 'reasons': []}
    market_context = {
        'trend': 'sideways',
        'timeframe_context': {'timeframe': timeframe, 'noise_level': 'medium'},
        'macro_context': {'asset_class': 'crypto', 'risk_level': 'medium'}
    }
    
    combined_result = signal_generator._combine_analyses(
        tech_result, ai_result, volume_result, volatility_result, market_context
    )
    
    print(f"Sinal combinado: {combined_result['signal']}")
    print(f"Confiança combinada: {combined_result['confidence']:.3f}")
    
    # Analisar scores detalhados
    scores = combined_result.get('scores', {})
    print(f"\nSCORES DETALHADOS:")
    print(f"  Buy score:  {scores.get('buy', 0):.4f}")
    print(f"  Sell score: {scores.get('sell', 0):.4f}")
    print(f"  Technical:  {scores.get('technical', 0):.4f}")
    print(f"  AI:         {scores.get('ai', 0):.4f}")
    print(f"  Volume:     {scores.get('volume', 0):.4f}")
    
    # 7. Análise de thresholds
    print(f"\n=== 6. ANÁLISE DE THRESHOLDS ===")
    strong_threshold = 0.25
    medium_threshold = 0.15
    weak_threshold = 0.08
    
    buy_score = scores.get('buy', 0)
    sell_score = scores.get('sell', 0)
    
    print(f"Thresholds utilizados:")
    print(f"  Strong: {strong_threshold}")
    print(f"  Medium: {medium_threshold}")
    print(f"  Weak:   {weak_threshold}")
    
    print(f"\nComparação com scores:")
    print(f"  Buy > Strong?  {buy_score} > {strong_threshold} = {buy_score > strong_threshold}")
    print(f"  Buy > Medium?  {buy_score} > {medium_threshold} = {buy_score > medium_threshold}")
    print(f"  Buy > Weak?    {buy_score} > {weak_threshold} = {buy_score > weak_threshold}")
    print(f"  Sell > Strong? {sell_score} > {strong_threshold} = {sell_score > strong_threshold}")
    print(f"  Sell > Medium? {sell_score} > {medium_threshold} = {sell_score > medium_threshold}")
    print(f"  Sell > Weak?   {sell_score} > {weak_threshold} = {sell_score > weak_threshold}")
    
    # 8. Identificar problemas específicos
    print(f"\n=== 7. DIAGNÓSTICO ===")
    
    issues = []
    
    # Verificar se análise técnica está tendenciosa
    if tech_result['signal'] == 'buy' and tech_result['confidence'] > 0.3:
        issues.append("✗ Análise técnica favorece compras")
    elif tech_result['signal'] == 'sell' and tech_result['confidence'] > 0.3:
        print("✓ Análise técnica pode gerar vendas")
    else:
        issues.append("⚠ Análise técnica neutra/fraca")
    
    # Verificar IA
    ai_signal = ai_result.get('signal', 0)
    if ai_signal > 0:
        issues.append("✗ IA sempre favorece compras")
    elif ai_signal < 0:
        print("✓ IA pode gerar vendas")
    else:
        print("⚠ IA neutra")
    
    # Verificar volume
    if volume_result['signal'] in ['buy', 'confirm'] and volume_result['confidence'] > 0.2:
        issues.append("✗ Análise de volume favorece compras")
    elif volume_result['signal'] == 'sell' and volume_result['confidence'] > 0.2:
        print("✓ Análise de volume pode gerar vendas")
    
    # Verificar se sell_score está sendo penalizado
    if buy_score > 0.1 and sell_score < 0.05:
        issues.append("✗ CRÍTICO: sell_score muito baixo comparado ao buy_score")
    
    if issues:
        print("PROBLEMAS IDENTIFICADOS:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✓ Não foram identificados problemas óbvios")
    
    # 9. Sugestões de correção
    print(f"\n=== 8. SUGESTÕES DE CORREÇÃO ===")
    if sell_score < buy_score * 0.5:
        print("1. 🔧 URGENTE: Verificar cálculo de sell_score - pode estar sendo penalizado")
    
    if ai_signal >= 0:
        print("2. 🔧 Verificar treinamento da IA - pode estar tendenciosa para compras")
    
    if tech_result['signal'] == 'buy':
        print("3. 🔧 Revisar lógica de indicadores técnicos - podem estar favorecendo compras")
    
    print("4. 🔧 Implementar teste de mercado em baixa para validar sinais de venda")
    print("5. 🔧 Adicionar logs detalhados na função _combine_analyses")

if __name__ == "__main__":
    debug_bias_source()
