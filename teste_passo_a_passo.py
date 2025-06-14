#!/usr/bin/env python3
"""
TESTE FOCAL DO VIÉS
Teste super específico para identificar onde o problema acontece
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_step_by_step():
    """Teste passo a passo de cada componente"""
    print("🔬 TESTE FOCAL DO VIÉS")
    print("=" * 40)
    
    try:
        # Importar classes necessárias
        from src.config import Config
        from src.market_data import MarketDataManager
        from src.ai_engine import AITradingEngine
        from src.signal_generator import SignalGenerator
        from src.market_analyzer import MarketAnalyzer
        
        # Inicializar componentes
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        market_analyzer = MarketAnalyzer(config, market_data, ai_engine)
        signal_generator = SignalGenerator(ai_engine, market_data)
        
        symbol = 'BTCUSDT'
        timeframe = '1h'
        
        print(f"\n🎯 Testando {symbol} {timeframe} - PASSO A PASSO")
        
        # Passo 1: Obter dados
        print(f"\n📊 PASSO 1: Obtendo dados...")
        df = market_data.get_historical_data(symbol, timeframe, 500)
        print(f"✅ Dados obtidos: {len(df)} registros")
        
        # Passo 2: Calcular indicadores técnicos
        print(f"\n📈 PASSO 2: Calculando indicadores técnicos...")
        df_with_indicators = signal_generator.technical_indicators.calculate_all_indicators(df)
        print(f"✅ Indicadores calculados: {len(df_with_indicators.columns)} colunas")
        
        # Passo 3: Análise técnica isolada
        print(f"\n⚙️ PASSO 3: Análise técnica isolada...")
        tech_result = signal_generator._analyze_technical_indicators(df_with_indicators)
        print(f"📊 Resultado técnico:")
        print(f"   Signal: {tech_result.get('signal', 'N/A')}")
        print(f"   Confidence: {tech_result.get('confidence', 0):.3f}")
        print(f"   Reasons: {tech_result.get('reasons', [])}")
        
        # Passo 4: IA isolada
        print(f"\n🤖 PASSO 4: Análise de IA isolada...")
        df_features = ai_engine.prepare_features(df_with_indicators)
        ai_result = ai_engine.predict_signal(df_features, symbol)
        print(f"🧠 Resultado IA:")
        print(f"   Signal: {ai_result.get('signal', 'N/A')}")
        print(f"   Confidence: {ai_result.get('confidence', 0):.3f}")
        print(f"   Reason: {ai_result.get('reason', 'N/A')}")
        
        # Passo 5: Market Analyzer
        print(f"\n📊 PASSO 5: Market Analyzer...")
        market_rec = market_analyzer.get_trade_recommendation(symbol, timeframe)
        print(f"📈 Market Recommendation:")
        print(f"   Recommendation: {market_rec.get('recommendation', 'N/A')}")
        print(f"   Confidence: {market_rec.get('confidence', 0):.3f}")
        print(f"   Market Score: {market_rec.get('market_score', 0):.3f}")
        print(f"   AI Score: {market_rec.get('ai_score', 0):.3f}")
        
        # Passo 6: Verificar thresholds
        print(f"\n🎯 PASSO 6: Verificando thresholds...")
        min_ai_confidence = config.SIGNAL_CONFIG.get('min_ai_confidence', 0.30)
        min_market_score = config.SIGNAL_CONFIG.get('min_market_score', 0.30)
        min_confidence = config.SIGNAL_CONFIG.get('min_confidence', 0.01)
        
        print(f"🔧 Configurações:")
        print(f"   min_ai_confidence: {min_ai_confidence}")
        print(f"   min_market_score: {min_market_score}")
        print(f"   min_confidence: {min_confidence}")
        
        # Verificar se passa nos thresholds
        ai_confidence = market_rec.get('confidence', 0)
        market_score = market_rec.get('market_score', 0)
        
        print(f"\n✅ Verificação de thresholds:")
        print(f"   AI Confidence: {ai_confidence:.3f} >= {min_ai_confidence}: {'✅' if ai_confidence >= min_ai_confidence else '❌'}")
        print(f"   Market Score: {market_score:.3f} >= {min_market_score}: {'✅' if market_score >= min_market_score else '❌'}")
        
        # Passo 7: Signal Generator completo
        print(f"\n🎯 PASSO 7: Signal Generator completo...")
        try:
            final_signal = signal_generator.generate_signal(symbol, timeframe)
            if final_signal:
                print(f"🎉 Sinal Final Gerado:")
                print(f"   Type: {final_signal.signal_type}")
                print(f"   Confidence: {final_signal.confidence:.3f}")
                print(f"   Entry Price: ${final_signal.entry_price:.2f}")
                print(f"   Stop Loss: ${final_signal.stop_loss:.2f}")
                print(f"   Take Profit: ${final_signal.take_profit:.2f}")
            else:
                print(f"❌ Nenhum sinal gerado")
        except Exception as e:
            print(f"❌ Erro no Signal Generator: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_step_by_step()
