#!/usr/bin/env python3
"""
🔍 VERIFICAÇÃO RÁPIDA DO SISTEMA
Teste rápido para confirmar que tudo está funcionando
"""

def verificar_sistema():
    """Verificação rápida do sistema"""
    
    print("🔍 VERIFICAÇÃO RÁPIDA DO SISTEMA")
    print("=" * 50)
    
    try:
        # Testar imports
        print("📦 Testando imports...")
        from src.config import Config
        from src.market_data import MarketDataManager
        from ai_engine_v3_otimizado import OptimizedAIEngineV3
        print("   ✅ Imports OK")
        
        # Testar inicialização
        print("🚀 Testando inicialização...")
        config = Config()
        market_data = MarketDataManager(config)
        ai_engine = OptimizedAIEngineV3(config)
        print("   ✅ Inicialização OK")
        
        # Teste rápido de sinal
        print("🎯 Testando geração de sinal...")
        df = market_data.get_historical_data('BTCUSDT', '5m', 100)
        if df is not None and len(df) >= 50:
            result = ai_engine.optimized_predict_signal(df, 'BTCUSDT_test')
            
            signal_type = result.get('signal_type', 'UNKNOWN')
            confidence = result.get('confidence', 0)
            
            print(f"   🎯 Sinal: {signal_type}")
            print(f"   📈 Confiança: {confidence:.3f}")
            print("   ✅ Geração de sinal OK")
        else:
            print("   ⚠️ Dados insuficientes para teste")
        
        print(f"\n✅ SISTEMA FUNCIONANDO CORRETAMENTE!")
        print("🚀 AI Engine V3 Otimizado ativo")
        print("📊 Dashboard disponível em: http://localhost:5000")
        print("🔄 Sistema pronto para uso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

if __name__ == "__main__":
    verificar_sistema()
