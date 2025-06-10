#!/usr/bin/env python3
"""
Teste simples para verificar se a correção do bias funcionou
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_import():
    """Testar se conseguimos importar após as correções"""
    try:
        print("Testando importação dos módulos...")
        
        from src.config import Config
        print("✅ Config importado")
        
        from src.market_data import MarketDataManager
        print("✅ MarketDataManager importado")
        
        from src.ai_engine import AITradingEngine
        print("✅ AITradingEngine importado")
        
        from src.signal_generator import SignalGenerator
        print("✅ SignalGenerator importado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Teste básico de funcionalidade"""
    try:
        from src.config import Config
        from src.market_data import MarketDataManager  
        from src.ai_engine import AITradingEngine
        
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = AITradingEngine(config)
        
        print("✅ Componentes inicializados")
        
        # Testar se a IA não está mais em modo de teste
        symbol = "BTCUSDT"
        df = market_data.get_historical_data(symbol, "1h", 100)
        
        if df is not None and not df.empty:
            print(f"✅ Dados obtidos: {len(df)} registros")
            
            # Preparar features
            df_features = ai_engine.prepare_features(df)
            print(f"✅ Features preparadas: {df_features.shape}")
            
            # Testar predição
            prediction = ai_engine.predict_signal(df_features, symbol)
            print(f"📊 Predição da IA: {prediction}")
            
            # Verificar se não está mais em modo de teste
            if prediction.get('test_mode'):
                print("❌ AINDA EM MODO DE TESTE!")
                return False
            else:
                print("✅ Modo de teste desativado!")
                return True
        else:
            print("❌ Não conseguiu obter dados")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== TESTE SIMPLES PÓS-CORREÇÃO ===")
    
    if test_import():
        print("\n=== TESTE DE FUNCIONALIDADE ===")
        if test_basic_functionality():
            print("\n🎯 CORREÇÃO BEM-SUCEDIDA!")
        else:
            print("\n❌ AINDA HÁ PROBLEMAS")
    else:
        print("\n❌ FALHA NA IMPORTAÇÃO")
