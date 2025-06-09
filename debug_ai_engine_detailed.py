#!/usr/bin/env python3
"""
Debug específico do AI Engine para identificar por que sempre retorna signal=0
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai_engine import AIEngine
from config import TradingConfig
from market_data import MarketData
import warnings

# Suprimir warnings
warnings.filterwarnings('ignore')

def debug_ai_engine():
    """Debug específico do AI Engine"""
    print("=== DEBUG AI ENGINE - INVESTIGANDO SIGNAL=0 ===")
    
    try:
        config = TradingConfig()
        ai_engine = AIEngine(config)
        market_data = MarketData(config)
        symbol = "BTCUSDT"
        
        print(f"1. Carregando modelos para {symbol}...")
        ai_engine.load_models(symbol)
        print(f"   ✅ Modelos carregados: {ai_engine.is_trained}")
        
        print(f"\n2. Obtendo dados históricos...")
        df = market_data.get_historical_data(symbol, '1h', 500)
        print(f"   ✅ {len(df)} registros obtidos")
        
        print(f"\n3. Preparando features...")
        df_prepared = ai_engine.prepare_features(df)
        print(f"   ✅ Features preparadas: {df_prepared.shape}")
        
        print(f"\n4. Fazendo predição...")
        prediction = ai_engine.predict_signal(df_prepared, symbol)
        
        print(f"\n📊 Resultado da predição:")
        for key, value in prediction.items():
            if key == 'individual_predictions':
                print(f"  {key}:")
                for model_name, pred in value.items():
                    print(f"    {model_name}: {pred}")
            else:
                print(f"  {key}: {value}")
        
        print(f"\n🔍 Análise detalhada:")
        signal = prediction.get('signal', 0)
        confidence = prediction.get('confidence', 0)
        individual_preds = prediction.get('individual_predictions', {})
        
        print(f"  - Signal final: {signal}")
        print(f"  - Confidence final: {confidence:.4f}")
        print(f"  - Número de modelos: {len(individual_preds)}")
        
        if individual_preds:
            buy_votes = sum(1 for pred in individual_preds.values() if pred == 1)
            sell_votes = sum(1 for pred in individual_preds.values() if pred == -1)
            hold_votes = sum(1 for pred in individual_preds.values() if pred == 0)
            
            print(f"  - Votos BUY (1): {buy_votes}")
            print(f"  - Votos SELL (-1): {sell_votes}")
            print(f"  - Votos HOLD (0): {hold_votes}")
            
            if signal == 0:
                print(f"\n❌ PROBLEMA: Signal=0 significa HOLD")
                print(f"   Possíveis causas:")
                print(f"   - Maioria dos modelos votou HOLD")
                print(f"   - Threshold de consenso muito alto")
                print(f"   - Modelos mal treinados")
        
        # Testar com dados mais recentes (últimos registros)
        print(f"\n5. Testando só com dados mais recentes...")
        recent_df = df_prepared.tail(100)  # Últimos 100 registros
        recent_prediction = ai_engine.predict_signal(recent_df, symbol)
        print(f"   Signal recente: {recent_prediction.get('signal', 0)}")
        print(f"   Confidence recente: {recent_prediction.get('confidence', 0):.4f}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ai_engine()
