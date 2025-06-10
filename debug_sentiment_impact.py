#!/usr/bin/env python3
"""
DEBUG: Impacto da Análise de Sentimento no Bias de BUY
Verifica se a análise de sentimento está causando o bias
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

async def debug_sentiment_impact():
    print("=== DEBUG: IMPACTO DA ANÁLISE DE SENTIMENTO ===")
    
    config = Config()
    market_data = MarketDataManager(config)
    ai_engine = AITradingEngine(config)
    generator = SignalGenerator(ai_engine, market_data)
    
    symbol = "BTCUSDT"
    timeframe = "1h"
    
    print(f"📊 Testando: {symbol} ({timeframe})")
    
    try:
        # Obter dados
        df = market_data.get_historical_data(symbol, timeframe, 500)
        if df is None or df.empty:
            print("❌ Erro ao obter dados")
            return
            
        # Calcular indicadores
        df = generator.technical_indicators.calculate_all_indicators(df)
        print(f"✅ Dados obtidos: {len(df)} registros")
          # 1. ANÁLISE TÉCNICA ISOLADA
        print("\n1️⃣ ANÁLISE TÉCNICA ISOLADA:")
        print("=" * 50)
        tech_signals = generator._analyze_technical_indicators(df)
        print(f"Resultado Técnico: {tech_signals}")
        print(f"Razões Técnicas: {tech_signals.get('reasons', [])}")
          # 2. ANÁLISE DE SENTIMENTO ISOLADA
        print("\n2️⃣ ANÁLISE DE SENTIMENTO ISOLADA:")
        print("=" * 50)
        try:
            # Como não temos análise de sentimento real, simular
            sentiment_signals = {'signal': 'HOLD', 'confidence': 0}
            sentiment_reasons = ['Análise de sentimento não disponível']
            print(f"Resultado Sentimento: {sentiment_signals}")
            print(f"Razões Sentimento: {sentiment_reasons}")
        except Exception as e:
            print(f"⚠️  Erro no sentimento: {e}")
            sentiment_signals = {'signal': 'HOLD', 'confidence': 0}
            sentiment_reasons = []
        
        # 3. ANÁLISE ON-CHAIN ISOLADA
        print("\n3️⃣ ANÁLISE ON-CHAIN ISOLADA:")
        print("=" * 50)
        try:
            # Como não temos análise on-chain real, simular
            onchain_signals = {'signal': 'HOLD', 'confidence': 0}
            onchain_reasons = ['Análise on-chain não disponível']
            print(f"Resultado On-Chain: {onchain_signals}")
            print(f"Razões On-Chain: {onchain_reasons}")
        except Exception as e:
            print(f"⚠️  Erro no on-chain: {e}")
            onchain_signals = {'signal': 'HOLD', 'confidence': 0}
            onchain_reasons = []
        
        # 4. COMBINAÇÃO FINAL
        print("\n4️⃣ COMBINAÇÃO FINAL:")
        print("=" * 50)
        
        # Simular a combinação
        weights = {
            'technical': 0.5,
            'sentiment': 0.3,
            'onchain': 0.2
        }
        
        print(f"Pesos: {weights}")
        
        # Calcular scores
        tech_score = tech_signals.get('confidence', 0)
        sent_score = sentiment_signals.get('confidence', 0)
        chain_score = onchain_signals.get('confidence', 0)
        
        tech_signal = tech_signals.get('signal', 'HOLD')
        sent_signal = sentiment_signals.get('signal', 'HOLD')
        chain_signal = onchain_signals.get('signal', 'HOLD')
        
        print(f"\nScores individuais:")
        print(f"  Técnico: {tech_signal} ({tech_score:.3f})")
        print(f"  Sentimento: {sent_signal} ({sent_score:.3f})")
        print(f"  On-Chain: {chain_signal} ({chain_score:.3f})")
        
        # Calcular scores ponderados
        buy_score = 0
        sell_score = 0
        
        # Técnico
        if tech_signal == 'BUY':
            buy_score += tech_score * weights['technical']
        elif tech_signal == 'SELL':
            sell_score += tech_score * weights['technical']
            
        # Sentimento
        if sent_signal == 'BUY':
            buy_score += sent_score * weights['sentiment']
        elif sent_signal == 'SELL':
            sell_score += sent_score * weights['sentiment']
            
        # On-Chain
        if chain_signal == 'BUY':
            buy_score += chain_score * weights['onchain']
        elif chain_signal == 'SELL':
            sell_score += chain_score * weights['onchain']
        
        print(f"\nScores finais ponderados:")
        print(f"  Buy Score: {buy_score:.3f}")
        print(f"  Sell Score: {sell_score:.3f}")
        
        # Determinar sinal final
        min_confidence = 0.3
        if buy_score > sell_score and buy_score >= min_confidence:
            final_signal = 'BUY'
            final_confidence = buy_score
        elif sell_score > buy_score and sell_score >= min_confidence:
            final_signal = 'SELL'
            final_confidence = sell_score
        else:
            final_signal = 'HOLD'
            final_confidence = max(buy_score, sell_score)
        
        print(f"\n🎯 RESULTADO MANUAL:")
        print(f"   Sinal: {final_signal}")
        print(f"   Confiança: {final_confidence:.3f}")
          # 5. COMPARAR COM SISTEMA REAL
        print("\n5️⃣ COMPARAÇÃO COM SISTEMA REAL:")
        print("=" * 50)
        real_result = generator.generate_signal(symbol, timeframe)        
        print(f"Sistema Real: {real_result.signal_type if real_result else 'None'} ({real_result.confidence if real_result else 0:.3f})")
        print(f"Cálculo Manual: {final_signal} ({final_confidence:.3f})")
        
        if real_result and real_result.signal_type != final_signal:
            print("⚠️  DISCREPÂNCIA DETECTADA!")
            print("   O sistema real difere do cálculo manual!")
        else:
            print("✅ Sistema consistente")
            
        # 6. ANÁLISE DE CADA COMPONENTE
        print("\n6️⃣ ANÁLISE DE IMPACTO:")
        print("=" * 50)
        
        tech_impact = tech_score * weights['technical']
        sent_impact = sent_score * weights['sentiment'] 
        chain_impact = chain_score * weights['onchain']
        
        print(f"Impacto Técnico: {tech_impact:.3f} ({tech_signal})")
        print(f"Impacto Sentimento: {sent_impact:.3f} ({sent_signal})")
        print(f"Impacto On-Chain: {chain_impact:.3f} ({chain_signal})")
        
        total_impact = tech_impact + sent_impact + chain_impact
        
        if total_impact > 0:
            print(f"\nContribuição percentual:")
            if tech_impact > 0:
                print(f"  Técnico: {(tech_impact/total_impact)*100:.1f}%")
            if sent_impact > 0:
                print(f"  Sentimento: {(sent_impact/total_impact)*100:.1f}%")
            if chain_impact > 0:
                print(f"  On-Chain: {(chain_impact/total_impact)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_sentiment_impact())
