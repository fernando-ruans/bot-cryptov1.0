#!/usr/bin/env python3
"""
DEBUG: Por que está retornando None em vez de sinais BUY/SELL?
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.signal_generator import SignalGenerator
from src.config import Config
from src.market_data import MarketDataManager
from src.ai_engine import AITradingEngine

def debug_none_signals():
    print("=== DEBUG: POR QUE SINAIS SÃO NONE? ===")
    
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    signal_generator = SignalGenerator(ai_engine, market_data)
    
    symbols = ["ETHUSDT", "LINKUSDT", "BTCUSDT"]
    
    for symbol in symbols:
        print(f"\n{'='*50}")
        print(f"🔍 DEBUGANDO {symbol}")
        print(f"{'='*50}")
        
        try:
            # 1. Verificar dados básicos
            df = market_data.get_historical_data(symbol, "1h", 500)
            print(f"📊 Dados: {len(df)} registros")
            print(f"💰 Preço atual: ${df['close'].iloc[-1]:.2f}")
            
            # 2. Verificar cooldown
            is_cooldown = signal_generator._is_in_cooldown(symbol)
            print(f"⏰ Em cooldown: {is_cooldown}")
            
            # 3. Calcular indicadores
            df_with_indicators = signal_generator.technical_indicators.calculate_all_indicators(df.copy())
            print(f"📈 Indicadores calculados: {len(df_with_indicators.columns)} colunas")
            
            # 4. Análise técnica
            technical_result = signal_generator._analyze_technical_indicators(df_with_indicators)
            print(f"🔧 TÉCNICA:")
            print(f"   Signal: {technical_result['signal']}")
            print(f"   Confidence: {technical_result['confidence']:.4f}")
            print(f"   Buy strength: {technical_result.get('buy_strength', 0):.4f}")
            print(f"   Sell strength: {technical_result.get('sell_strength', 0):.4f}")
            
            # 5. AI Prediction
            ai_prediction = ai_engine.predict_signal(df_with_indicators, symbol)
            print(f"🤖 AI:")
            print(f"   Signal: {ai_prediction.get('signal', 'N/A')}")
            print(f"   Confidence: {ai_prediction.get('confidence', 0):.4f}")
            print(f"   Fallback: {ai_prediction.get('fallback', False)}")
            
            # 6. Análises auxiliares
            volume_analysis = signal_generator._analyze_volume(df_with_indicators)
            volatility_analysis = signal_generator._analyze_volatility(df_with_indicators)
            market_context = signal_generator._analyze_market_context(symbol, "1h")
            
            print(f"📊 VOLUME: {volume_analysis.get('signal')} (conf: {volume_analysis.get('confidence', 0):.3f})")
            print(f"📊 VOLATILIDADE: {volatility_analysis.get('signal')} (conf: {volatility_analysis.get('confidence', 0):.3f})")
            
            # 7. Combinação final
            combined = signal_generator._combine_analyses(
                technical_result, ai_prediction, volume_analysis,
                volatility_analysis, market_context
            )
            
            print(f"🎯 COMBINADO:")
            print(f"   Signal: {combined.get('signal')}")
            print(f"   Confidence: {combined.get('confidence', 0):.4f}")
            print(f"   Scores: {combined.get('scores', {})}")
            
            # 8. Verificar thresholds
            min_confidence = config.SIGNAL_CONFIG['min_confidence']
            print(f"⚙️ THRESHOLDS:")
            print(f"   Min confidence: {min_confidence}")
            print(f"   Atende threshold: {combined.get('confidence', 0) >= min_confidence}")
            
            # 9. Tentar gerar sinal completo
            print(f"\n🚀 TENTANDO GERAR SINAL COMPLETO:")
            signal = signal_generator.generate_signal(symbol, "1h")
            
            if signal:
                print(f"✅ SINAL GERADO:")
                print(f"   Tipo: {signal.signal_type}")
                print(f"   Confiança: {signal.confidence:.4f}")
                print(f"   Entry: ${signal.entry_price:.2f}")
            else:
                print(f"❌ NENHUM SINAL GERADO")
                
                # Debug específico
                print(f"\n🔍 INVESTIGAÇÃO DETALHADA:")
                
                # Verificar se é problema de confiança
                if combined.get('confidence', 0) < min_confidence:
                    print(f"   ❌ Confiança muito baixa: {combined.get('confidence', 0):.4f} < {min_confidence}")
                
                # Verificar se é problema de signal type
                if combined.get('signal') == 'hold':
                    print(f"   ❌ Sistema retornando HOLD em vez de BUY/SELL")
                
                # Verificar se é problema de scores
                scores = combined.get('scores', {})
                if scores.get('buy', 0) == 0 and scores.get('sell', 0) == 0:
                    print(f"   ❌ Scores zerados - problema na análise")
                
        except Exception as e:
            print(f"❌ ERRO: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_none_signals()
