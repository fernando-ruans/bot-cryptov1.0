#!/usr/bin/env python3
"""
🧪 TESTE RÁPIDO DE VIÉS - CORREÇÕES IMPLEMENTADAS
Verificação das correções de viés por timeframe
"""

import pandas as pd
import json
from datetime import datetime

def teste_rapido_vies():
    """Teste rápido para validar correções"""
    
    print("🧪 TESTE RÁPIDO - CORREÇÕES DE VIÉS")
    print("=" * 50)
    
    try:
        from src.config import Config
        from src.market_data import MarketDataManager
        from ai_engine_enhanced import EnhancedAIEngine
        from melhorias_confianca_sinais import SignalConfidenceEnhancer
        
        # Inicializar
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = EnhancedAIEngine(config)
        enhancer = SignalConfidenceEnhancer(config)
        
        print(f"✅ Threshold ajustado: {enhancer.min_confidence_threshold}")
        print(f"🔧 Correções disponíveis: {list(enhancer.timeframe_bias_correction.keys())}")
        
        # Testar com alguns casos
        test_cases = [
            ('BTCUSDT', '5m'),    # Viés BUY extremo
            ('BTCUSDT', '1d'),    # Viés SELL extremo  
            ('ETHUSDT', '1h'),    # Balanceado
        ]
        
        results = []
        
        for symbol, timeframe in test_cases:
            print(f"\n🔍 Testando {symbol} {timeframe}...")
            
            # Definir timeframe
            ai_engine.set_timeframe(timeframe)
            
            # Obter dados
            df = market_data.get_historical_data(symbol, timeframe, 100)
            if df is None:
                print(f"❌ Dados indisponíveis")
                continue
            
            # Gerar sinal original
            original_signal = ai_engine.enhanced_predict_signal(df, symbol)
            
            # Extrair dados
            signal_type = original_signal.get('signal_type', 'hold')
            confidence = original_signal.get('confidence', 0)
            enhanced = original_signal.get('confidence_enhanced', False)
            
            print(f"📊 Resultado: {signal_type.upper()} (conf: {confidence:.3f})")
            print(f"🎯 Melhorado: {enhanced}")
            
            # Verificar correção de viés
            if 'enhancement_scores' in original_signal:
                scores = original_signal['enhancement_scores']
                print(f"📈 Scores: {scores}")
            
            results.append({
                'symbol': symbol,
                'timeframe': timeframe,
                'signal': signal_type,
                'confidence': confidence,
                'enhanced': enhanced
            })
        
        # Resumo
        print(f"\n{'='*50}")
        print("📊 RESUMO RÁPIDO:")
        
        buy_count = sum(1 for r in results if r['signal'] == 'buy')
        sell_count = sum(1 for r in results if r['signal'] == 'sell')
        hold_count = sum(1 for r in results if r['signal'] == 'hold')
        avg_conf = sum(r['confidence'] for r in results) / len(results) if results else 0
        
        print(f"   BUY: {buy_count}/{len(results)}")
        print(f"   SELL: {sell_count}/{len(results)}")
        print(f"   HOLD: {hold_count}/{len(results)}")
        print(f"   Confiança média: {avg_conf:.3f}")
        
        # Salvar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"teste_rapido_vies_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Salvo em: {filename}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste_rapido_vies()
